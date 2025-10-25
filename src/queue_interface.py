"""
Queue interface for communicating with the queue_manager.sh script.
Enhanced for v2.0 with contract and state awareness.
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import re

from .models import Task, AgentStatus, QueueState


class QueueInterface:
    """Interface to the queue_manager.sh bash script with v2.0 contract support."""

    def __init__(self, queue_script_path: str):
        """Initialize the queue interface.

        Args:
            queue_script_path: Path to queue_manager.sh
        """
        self.script_path = Path(queue_script_path)

        if not self.script_path.exists():
            raise FileNotFoundError(f"Queue manager script not found: {self.script_path}")

        # Derive other paths
        self.project_root = self.script_path.parent.parent.parent
        self.queue_file = self.project_root / ".claude/queues/task_queue.json"
        self.logs_dir = self.project_root / ".claude/logs"
        self.agents_file = self.project_root / ".claude/agents/agents.json"
        self.tools_file = self.project_root / ".claude/tools/tools.json"
        self.contracts_file = self.project_root / ".claude/AGENT_CONTRACTS.json"
        self.states_file = self.project_root / ".claude/WORKFLOW_STATES.json"

        # Validate paths
        if not self.queue_file.exists():
            raise FileNotFoundError(f"Queue file not found: {self.queue_file}")

        if not self.logs_dir.exists():
            raise FileNotFoundError(f"Logs directory not found: {self.logs_dir}")

    def _run_command(self, *args) -> str:
        """Run queue manager command.

        Args:
            *args: Arguments to pass to queue_manager.sh

        Returns:
            Command output
        """
        cmd = [str(self.script_path)] + list(args)
        result = subprocess.run(
            cmd,
            cwd=str(self.project_root),
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "No error message"
            stdout_msg = result.stdout.strip() if result.stdout else ""
            full_error = f"Command failed with exit code {result.returncode}\n"
            full_error += f"Command: {' '.join(args)}\n"
            if error_msg:
                full_error += f"Error: {error_msg}\n"
            if stdout_msg:
                full_error += f"Output: {stdout_msg}"
            raise RuntimeError(full_error)

        return result.stdout

    def _run_command_async(self, *args) -> subprocess.Popen:
        """Run queue manager command asynchronously (non-blocking).

        Args:
            *args: Arguments to pass to queue_manager.sh

        Returns:
            Popen object for the running process
        """
        cmd = [str(self.script_path)] + list(args)
        process = subprocess.Popen(
            cmd,
            cwd=str(self.project_root),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            start_new_session=True,
            close_fds=True
        )

        return process

    def add_task(self, title: str, agent: str, priority: str,
                 task_type: str, source_file: str, description: str,
                 auto_complete: bool = False, auto_chain: bool = False) -> str:
        """Add a new task to the queue.

        UPDATED: Now accepts auto_complete and auto_chain parameters
        """
        args = [
            "add",
            title,
            agent,
            priority,
            task_type,
            source_file,
            description,
            "true" if auto_complete else "false",
            "true" if auto_chain else "false"
        ]

        output = self._run_command(*args)
        return output.strip().split('\n')[-1]

    def start_task(self, task_id: str, auto_complete: bool = False, auto_chain: bool = False) -> subprocess.Popen:
        """Start a task asynchronously (non-blocking).

        Args:
            task_id: Task ID to start
            auto_complete: Whether to enable auto-completion
            auto_chain: Whether to enable auto-chaining

        Returns:
            Popen object for the running process
        """
        args = ["start", task_id]
        if auto_complete:
            args.append("--auto-complete")
        if auto_chain:
            args.append("--auto-chain")

        return self._run_command_async(*args)

    def cancel_task(self, task_id: str, reason: str = ""):
        """Cancel a task.

        Args:
            task_id: Task ID to cancel
            reason: Cancellation reason
        """
        if reason:
            self._run_command("cancel", task_id, reason)
        else:
            self._run_command("cancel", task_id)

    def cancel_all_tasks(self, reason: str = ""):
        """Cancel all pending and active tasks.

        Args:
            reason: Cancellation reason
        """
        if reason:
            self._run_command("cancel-all", reason)
        else:
            self._run_command("cancel-all")

    def complete_task(self, task_id: str, result: str = "", auto_chain: bool = False):
        """Complete a task.

        Args:
            task_id: Task ID to complete
            result: Completion result message
            auto_chain: Whether to enable auto-chaining
        """
        args = ["complete", task_id]
        if result:
            args.append(result)
        if auto_chain:
            args.append("--auto-chain")

        self._run_command(*args)

    def fail_task(self, task_id: str, error: str = ""):
        """Fail a task.

        Args:
            task_id: Task ID to fail
            error: Error message
        """
        if error:
            self._run_command("fail", task_id, error)
        else:
            self._run_command("fail", task_id)

    def add_integration_task(self, workflow_status: str, source_file: str,
                             previous_agent: str, parent_task_id: str = "") -> str:
        """Add an integration task for external system sync."""
        args = ["add-integration", workflow_status, source_file, previous_agent]
        if parent_task_id:
            args.append(parent_task_id)

        output = self._run_command(*args)
        return output.strip()

    def validate_agent_outputs(self, agent: str, enhancement_dir: str) -> bool:
        """Validate agent outputs against contract."""
        try:
            self._run_command("validate_agent_outputs", agent, enhancement_dir)
            return True
        except RuntimeError:
            return False

    def sync_external(self, task_id: str):
        """Create integration task for specific completed task."""
        self._run_command("sync-external", task_id)

    def sync_all(self):
        """Create integration tasks for all unsynced completed tasks."""
        self._run_command("sync-all")

    def update_metadata(self, task_id: str, key: str, value: str):
        """Update task metadata."""
        self._run_command("update-metadata", task_id, key, value)

    def get_queue_state(self) -> QueueState:
        """Get current queue state using list_tasks command.

        Returns:
            QueueState object
        """
        # Call list_tasks command
        output = self._run_command("list_tasks", "all", "compact")
        data = json.loads(output)

        # Helper to parse tasks with defaults for missing fields
        def parse_task(task_data: dict) -> Task:
            # Convert runtime_seconds to Unix timestamps for display compatibility
            # Note: start_datetime and end_datetime are derived from ISO strings if needed
            from datetime import datetime

            start_datetime = None
            end_datetime = None

            if task_data.get('started'):
                try:
                    start_dt = datetime.fromisoformat(task_data['started'].replace('Z', '+00:00'))
                    start_datetime = int(start_dt.timestamp())
                except (ValueError, AttributeError):
                    pass

            if task_data.get('completed'):
                try:
                    end_dt = datetime.fromisoformat(task_data['completed'].replace('Z', '+00:00'))
                    end_datetime = int(end_dt.timestamp())
                except (ValueError, AttributeError):
                    pass

            return Task(
                id=task_data['id'],
                title=task_data['title'],
                assigned_agent=task_data['assigned_agent'],
                priority=task_data['priority'],
                task_type=task_data.get('task_type', 'unknown'),
                description=task_data.get('description', ''),
                source_file=task_data.get('source_file', ''),
                created=task_data['created'],
                status=task_data['status'],
                started=task_data.get('started'),
                completed=task_data.get('completed'),
                result=task_data.get('result'),
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                runtime_seconds=task_data.get('runtime_seconds'),
                auto_complete=task_data.get('auto_complete', False),
                auto_chain=task_data.get('auto_chain', False),
                metadata=task_data.get('metadata')
            )

        # Parse tasks from list_tasks output format
        pending_tasks = [parse_task(task) for task in data.get('pending', [])]
        active_workflows = [parse_task(task) for task in data.get('active', [])]
        completed_tasks = [parse_task(task) for task in data.get('completed', [])]
        failed_tasks = [parse_task(task) for task in data.get('failed', [])]

        # Note: list_tasks doesn't provide agent_status, so we keep it empty
        agent_status = {}

        return QueueState(
            pending_tasks=pending_tasks,
            active_workflows=active_workflows,
            completed_tasks=completed_tasks,
            failed_tasks=failed_tasks,
            agent_status=agent_status
        )

    def get_agent_list(self) -> Dict[str, str]:
        """Get dictionary of available agents.

        Returns:
            Dictionary mapping agent-file to agent name (display name)

        Raises:
            FileNotFoundError: If agents.json is not found
        """
        if not self.agents_file.exists():
            raise FileNotFoundError(f"Agents file not found: {self.agents_file}")

        with open(self.agents_file, 'r') as f:
            data = json.load(f)

        print(f"DEBUG: agents.json data type: {type(data)}")
        print(f"DEBUG: agents.json keys: {data.keys() if isinstance(data, dict) else 'not a dict'}")

        result = {}

        # Determine the agents list based on structure
        agents_list = []

        if isinstance(data, dict):
            # Structure: {"agents": [...]}
            agents_list = data.get('agents', [])
        elif isinstance(data, list):
            # Structure: [...]
            agents_list = data
        else:
            print(f"ERROR: Unexpected agents.json format: {type(data)}")
            return result

        # Parse each agent
        for agent in agents_list:
            if not isinstance(agent, dict):
                # Skip non-dict items
                continue

            agent_file = agent.get('agent-file')
            name = agent.get('name')

            if agent_file and name:
                result[agent_file] = name

        print(f"DEBUG: Parsed agents map: {result}")

        if not result:
            print("WARNING: No agents found in agents.json")

        return result

    def get_task_types(self) -> Dict[str, str]:
        """Get dictionary of available task types.

        Returns:
            Dictionary mapping internal values to display names
        """
        return {
            "analysis": "Analysis",
            "technical_analysis": "Technical Analysis",
            "implementation": "Implementation",
            "testing": "Testing",
            "documentation": "Documentation",
            "integration": "Integration"
        }

    def get_priorities(self) -> List[str]:
        """Get list of available priorities.

        Returns:
            List of priority names
        """
        return [
            "critical",
            "high",
            "normal",
            "low"
        ]

    def get_task_log(self, task_id: str, source_file: str) -> Optional[str]:
        """Get log content for a task.

        Args:
            task_id: Task ID
            source_file: Source file path to help locate log

        Returns:
            Log content or None if not found
        """
        # Extract enhancement name from source file
        enhancement_name = self._extract_enhancement_name(source_file)
        if not enhancement_name:
            return None

        # Look in enhancement logs directory
        log_dir = self.project_root / "enhancements" / enhancement_name / "logs"

        if not log_dir.exists():
            return None

        # Find log file matching task ID
        log_files = list(log_dir.glob(f"*{task_id}*.log"))

        if not log_files:
            return None

        # Read most recent log
        log_file = max(log_files, key=lambda p: p.stat().st_mtime)

        with open(log_file, 'r') as f:
            return f.read()

    def task_log_exists(self, task_id: str, source_file: str) -> bool:
        """Check if log exists for a task.

        Args:
            task_id: Task ID
            source_file: Source file path to help locate log

        Returns:
            True if log exists
        """
        return self.get_task_log(task_id, source_file) is not None

    def get_operations_log(self, max_lines: int = 1000) -> str:
        """Get operations log content.

        Args:
            max_lines: Maximum number of lines to return

        Returns:
            Log content
        """
        log_file = self.logs_dir / "queue_operations.log"

        if not log_file.exists():
            return "No operations log found."

        with open(log_file, 'r') as f:
            lines = f.readlines()

        # Return last N lines
        return ''.join(lines[-max_lines:])

    def get_tools_data(self) -> Optional[Dict]:
        """Get tools configuration data from tools.json.

        Returns:
            Dictionary containing claude_code_tools and agent_personas, or None if not found
        """
        if not self.tools_file.exists():
            return None

        with open(self.tools_file, 'r') as f:
            return json.load(f)

    # =========================================================================
    # V2.0 CONTRACT AND STATE METHODS
    # =========================================================================

    def get_agent_contracts(self) -> Optional[dict]:
        """Load AGENT_CONTRACTS.json.

        Returns:
            Dictionary containing agent contracts, or None if not found
        """
        if not self.contracts_file.exists():
            return None

        try:
            with open(self.contracts_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def get_workflow_states(self) -> Optional[dict]:
        """Load WORKFLOW_STATES.json.

        Returns:
            Dictionary containing workflow states, or None if not found
        """
        if not self.states_file.exists():
            return None

        try:
            with open(self.states_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def get_agent_contract(self, agent: str) -> Optional[dict]:
        """Get contract for specific agent.

        Args:
            agent: Agent name (agent-file key)

        Returns:
            Agent contract dictionary or None if not found
        """
        contracts = self.get_agent_contracts()
        if not contracts:
            return None

        return contracts.get('agents', {}).get(agent)

    def validate_source_file_pattern(self, agent: str, source_file: str) -> tuple[bool, str]:
        """Validate that source file matches agent's expected input pattern.

        Args:
            agent: Agent name
            source_file: Source file path

        Returns:
            Tuple of (is_valid, message)
        """
        contract = self.get_agent_contract(agent)
        if not contract:
            return True, "No contract found (validation skipped)"

        required_inputs = contract.get('inputs', {}).get('required', [])
        if not required_inputs:
            return True, "No input pattern specified in contract"

        # Get first required input pattern
        pattern = required_inputs[0].get('pattern', '')
        if not pattern:
            return True, "No pattern specified"

        # Convert pattern to regex
        # Replace {enhancement_name} with regex pattern
        regex_pattern = pattern.replace('{enhancement_name}', r'([^/]+)')
        regex_pattern = f"^{regex_pattern}$"

        # Test if source file matches
        if re.match(regex_pattern, source_file):
            return True, f"✓ Matches pattern: {pattern}"
        else:
            return False, f"✗ Expected pattern: {pattern}"

    def get_agent_expected_outputs(self, agent: str) -> Optional[dict]:
        """Get expected outputs for an agent from contract.

        Args:
            agent: Agent name

        Returns:
            Dictionary with root_document, output_directory, additional_required
        """
        contract = self.get_agent_contract(agent)
        if not contract:
            return None

        return contract.get('outputs', {})

    def get_agent_success_statuses(self, agent: str) -> List[dict]:
        """Get success statuses for an agent.

        Args:
            agent: Agent name

        Returns:
            List of success status dictionaries
        """
        contract = self.get_agent_contract(agent)
        if not contract:
            return []

        return contract.get('statuses', {}).get('success', [])

    def get_next_agents(self, agent: str, status: str) -> List[str]:
        """Get next agents based on current agent and status.

        Args:
            agent: Current agent name
            status: Completion status

        Returns:
            List of next agent names
        """
        contract = self.get_agent_contract(agent)
        if not contract:
            return []

        success_statuses = contract.get('statuses', {}).get('success', [])
        for status_def in success_statuses:
            if status_def.get('code') == status:
                return status_def.get('next_agents', [])

        return []

    def validate_agent_outputs(self, agent: str, source_file: str) -> tuple[bool, List[str]]:
        """Validate that agent created required outputs.

        Args:
            agent: Agent name
            source_file: Source file (to determine enhancement directory)

        Returns:
            Tuple of (all_valid, list of validation messages)
        """
        contract = self.get_agent_contract(agent)
        if not contract:
            return True, ["No contract found (validation skipped)"]

        # Extract enhancement name and build paths
        enhancement_name = self._extract_enhancement_name(source_file)
        if not enhancement_name:
            return False, ["Cannot determine enhancement name from source file"]

        enhancement_dir = self.project_root / "enhancements" / enhancement_name

        outputs = contract.get('outputs', {})
        output_directory = outputs.get('output_directory', '')
        root_document = outputs.get('root_document', '')
        additional_required = outputs.get('additional_required', [])

        messages = []
        all_valid = True

        # Check root document
        root_path = enhancement_dir / output_directory / root_document
        if root_path.exists():
            messages.append(f"✓ Root document exists: {output_directory}/{root_document}")
        else:
            messages.append(f"✗ Root document missing: {output_directory}/{root_document}")
            all_valid = False

        # Check additional required files
        for req_file in additional_required:
            file_path = enhancement_dir / output_directory / req_file
            if file_path.exists():
                messages.append(f"✓ Required file exists: {req_file}")
            else:
                messages.append(f"✗ Required file missing: {req_file}")
                all_valid = False

        # Check metadata header if required
        if contract.get('metadata_required', False) and root_path.exists():
            has_header, header_msg = self._check_metadata_header(root_path)
            messages.append(header_msg)
            if not has_header:
                all_valid = False

        return all_valid, messages

    def _check_metadata_header(self, file_path: Path) -> tuple[bool, str]:
        """Check if file has required metadata header.

        Args:
            file_path: Path to file

        Returns:
            Tuple of (has_header, message)
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read(500)  # Read first 500 chars

            # Check for YAML frontmatter
            if not content.startswith('---'):
                return False, "✗ Missing YAML frontmatter (---)"

            # Check for required fields
            required_fields = ['enhancement:', 'agent:', 'task_id:', 'timestamp:', 'status:']
            missing_fields = []

            for field in required_fields:
                if field not in content:
                    missing_fields.append(field.rstrip(':'))

            if missing_fields:
                return False, f"✗ Metadata missing fields: {', '.join(missing_fields)}"

            return True, "✓ Metadata header valid (5 required fields)"

        except IOError:
            return False, "✗ Could not read file"

    def _extract_enhancement_name(self, source_file: str) -> Optional[str]:
        """Extract enhancement name from source file path.

        Args:
            source_file: Source file path

        Returns:
            Enhancement name or None
        """
        # Pattern: enhancements/{enhancement_name}/...
        match = re.match(r'^enhancements/([^/]+)/', source_file)
        if match:
            return match.group(1)
        return None

    def get_expected_output_path(self, agent: str, source_file: str) -> Optional[str]:
        """Get the expected output path for an agent based on source file.

        Args:
            agent: Agent name
            source_file: Source file path

        Returns:
            Expected output path or None
        """
        contract = self.get_agent_contract(agent)
        if not contract:
            return None

        enhancement_name = self._extract_enhancement_name(source_file)
        if not enhancement_name:
            return None

        outputs = contract.get('outputs', {})
        output_dir = outputs.get('output_directory', '')
        root_doc = outputs.get('root_document', '')

        return f"enhancements/{enhancement_name}/{output_dir}/{root_doc}"

    def get_metadata_requirements(self) -> List[str]:
        """Get list of required metadata header fields.

        Returns:
            List of required field names
        """
        contracts = self.get_agent_contracts()
        if not contracts:
            return ['enhancement', 'agent', 'task_id', 'timestamp', 'status']

        # Return from contracts if available
        metadata_fields = contracts.get('metadata_fields', {})
        return [field for field, spec in metadata_fields.items() if spec.get('required', False)]

    def is_v2_compatible(self) -> bool:
        """Check if the connected project is v2.0 compatible.

        Returns:
            True if AGENT_CONTRACTS.json exists
        """
        return self.contracts_file.exists()

    def get_system_version(self) -> str:
        """Get the multi-agent system version.

        Returns:
            Version string (e.g., "2.0.0" or "1.0")
        """
        if self.contracts_file.exists():
            try:
                contracts = self.get_agent_contracts()
                return contracts.get('version', '2.0.0')
            except:
                return "2.0.0"
        return "1.0"