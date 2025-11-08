"""
CMAT interface for communicating with the cmat.sh script system.
Version 3.0 - Simplified for cmat.sh only (no backward compatibility).
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re

from ..models import Task, AgentStatus, QueueState


class CMATInterface:
    """Interface to the cmat.sh command system (v3.0+)."""

    def __init__(self, cmat_script_path: str):
        """Initialize the queue interface.

        Args:
            cmat_script_path: Path to cmat.sh
        """
        self.script_path = Path(cmat_script_path)

        if not self.script_path.exists():
            raise FileNotFoundError(f"CMAT script not found: {self.script_path}")

        # Derive paths
        self.project_root = self._find_project_root()
        self.queue_file = self.project_root / ".claude/queues/task_queue.json"
        self.logs_dir = self.project_root / ".claude/logs"
        self.agents_file = self.project_root / ".claude/agents/agents.json"
        self.tools_file = self.project_root / ".claude/tools/tools.json"
        self.contracts_file = self.project_root / ".claude/AGENT_CONTRACTS.json"
        self.states_file = self.project_root / ".claude/WORKFLOW_STATES.json"
        self.skills_file = self.project_root / ".claude/skills/skills.json"

        # Validate essential paths
        if not self.queue_file.exists():
            raise FileNotFoundError(f"Queue file not found: {self.queue_file}")

        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _find_project_root(self) -> Path:
        """Find project root by walking up from script path."""
        current = self.script_path.parent
        while current != current.parent:
            if (current / ".claude").exists():
                return current
            current = current.parent
        raise FileNotFoundError("Could not find project root (.claude directory)")

    def _run_command(self, *args) -> str:
        """Run cmat command synchronously."""
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
            raise RuntimeError(
                f"Command failed: {' '.join(args)}\n"
                f"Exit code: {result.returncode}\n"
                f"Error: {error_msg}\n"
                f"Output: {stdout_msg}"
            )

        return result.stdout

    def _run_command_async(self, *args) -> subprocess.Popen:
        """Run cmat command asynchronously."""
        cmd = [str(self.script_path)] + list(args)
        return subprocess.Popen(
            cmd,
            cwd=str(self.project_root),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            start_new_session=True,
            close_fds=True
        )

    # =========================================================================
    # QUEUE COMMANDS
    # =========================================================================

    def add_task(self, title: str, agent: str, priority: str,
                 task_type: str, source_file: str, description: str,
                 auto_complete: bool = False, auto_chain: bool = False) -> str:
        """Add a new task to the queue."""
        output = self._run_command(
            "queue", "add",
            title, agent, priority, task_type, source_file, description,
            "true" if auto_complete else "false",
            "true" if auto_chain else "false"
        )
        return output.strip().split('\n')[-1]

    def start_task(self, task_id: str) -> subprocess.Popen:
        """Start a task asynchronously."""
        return self._run_command_async("queue", "start", task_id)

    def complete_task(self, task_id: str, result: str = "", auto_chain: bool = False):
        """Complete a task."""
        args = ["queue", "complete", task_id]
        if result:
            args.append(result)
        if auto_chain:
            args.append("--auto-chain")
        self._run_command(*args)

    def cancel_task(self, task_id: str, reason: str = ""):
        """Cancel a task."""
        args = ["queue", "cancel", task_id]
        if reason:
            args.append(reason)
        self._run_command(*args)

    def cancel_all_tasks(self, reason: str = ""):
        """Cancel all pending and active tasks."""
        args = ["queue", "cancel-all"]
        if reason:
            args.append(reason)
        self._run_command(*args)

    def clear_finished_tasks(self):
        """Clear all completed and failed tasks from history.

        This removes completed and failed tasks but leaves pending and active tasks intact.
        Uses --force to bypass confirmation prompts.
        """
        self._run_command("queue", "clear-finished", "--force")

    def reset_queue(self):
        """Reset the entire queue system to empty state.

        This clears all tasks (pending, active, completed, failed) and resets logs.
        Uses --force to bypass confirmation prompts.
        """
        self._run_command("queue", "init", "--force")

    def fail_task(self, task_id: str, error: str = ""):
        """Fail a task."""
        args = ["queue", "fail", task_id]
        if error:
            args.append(error)
        self._run_command(*args)

    def update_metadata(self, task_id: str, key: str, value: str):
        """Update task metadata."""
        self._run_command("queue", "metadata", task_id, key, value)

    def get_queue_state(self) -> QueueState:
        """Get current queue state."""
        output = self._run_command("queue", "list", "all", "json")
        data = json.loads(output)

        def parse_task(task_data: dict) -> Task:
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

        return QueueState(
            pending_tasks=[parse_task(t) for t in data.get('pending', [])],
            active_workflows=[parse_task(t) for t in data.get('active', [])],
            completed_tasks=[parse_task(t) for t in data.get('completed', [])],
            failed_tasks=[parse_task(t) for t in data.get('failed', [])],
            agent_status={}
        )

    # =========================================================================
    # WORKFLOW COMMANDS
    # =========================================================================

    def validate_agent_outputs(self, agent: str, source_file: str) -> Tuple[bool, List[str]]:
        """Validate agent outputs against contract."""
        enhancement_name = self._extract_enhancement_name(source_file)
        if not enhancement_name:
            return False, ["Cannot determine enhancement from source file"]

        enhancement_dir = f"enhancements/{enhancement_name}"

        try:
            output = self._run_command("workflow", "validate", agent, enhancement_dir)
            lines = [line.strip() for line in output.split('\n') if line.strip()]
            all_valid = all('✓' in msg or 'passed' in msg.lower() for msg in lines)
            return all_valid, lines
        except RuntimeError as e:
            return False, [str(e)]

    def get_next_agent(self, agent: str, status: str) -> Optional[str]:
        """Determine next agent based on current agent and status."""
        try:
            output = self._run_command("workflow", "next-agent", agent, status)
            next_agent = output.strip()
            return next_agent if next_agent != "UNKNOWN" else None
        except RuntimeError:
            return None

    def get_next_source_path(self, enhancement: str, next_agent: str, current_agent: str) -> Optional[str]:
        """Build source file path for next agent."""
        try:
            output = self._run_command("workflow", "next-source", enhancement, next_agent, current_agent)
            return output.strip()
        except RuntimeError:
            return None

    def auto_chain_workflow(self, task_id: str, status: str):
        """Automatically chain to next agent with validation."""
        self._run_command("workflow", "auto-chain", task_id, status)

    # =========================================================================
    # SKILLS COMMANDS
    # =========================================================================

    def get_skills_list(self) -> Optional[Dict]:
        """Get all available skills from skills.json."""
        if not self.skills_file.exists():
            return None

        try:
            with open(self.skills_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def get_agent_skills(self, agent: str) -> List[str]:
        """Get skills assigned to an agent."""
        try:
            output = self._run_command("skills", "get", agent)
            skills_data = json.loads(output)
            return skills_data if isinstance(skills_data, list) else []
        except (RuntimeError, json.JSONDecodeError):
            return []

    def load_skill_content(self, skill_directory: str) -> Optional[str]:
        """Load skill content from SKILL.md file."""
        try:
            return self._run_command("skills", "load", skill_directory)
        except RuntimeError:
            return None

    def get_skills_prompt(self, agent: str) -> Optional[str]:
        """Build complete skills section for agent prompt."""
        try:
            return self._run_command("skills", "prompt", agent)
        except RuntimeError:
            return None

    # =========================================================================
    # INTEGRATION COMMANDS
    # =========================================================================

    def add_integration_task(self, workflow_status: str, source_file: str,
                             previous_agent: str, parent_task_id: str = "") -> str:
        """Add integration task for external system sync."""
        args = ["integration", "add", workflow_status, source_file, previous_agent]
        if parent_task_id:
            args.append(parent_task_id)
        output = self._run_command(*args)
        return output.strip()

    def sync_task_external(self, task_id: str):
        """Sync specific task to external systems."""
        self._run_command("integration", "sync", task_id)

    def sync_all_external(self):
        """Sync all unsynced completed tasks."""
        self._run_command("integration", "sync-all")

    # =========================================================================
    # AGENT COMMANDS
    # =========================================================================

    def get_agents_data(self) -> Optional[Dict]:
        """Get agents data from agents.json."""
        if not self.agents_file.exists():
            return None

        try:
            with open(self.agents_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'agents' in data:
                    return data
                elif isinstance(data, list):
                    return {'agents': data}
                return data
        except (json.JSONDecodeError, IOError):
            return None

    def regenerate_agents_json(self):
        """Regenerate agents.json from agent markdown frontmatter."""
        self._run_command("agents", "generate-json")

    def get_agent_list(self) -> Dict[str, str]:
        """Get dictionary of available agents."""
        if not self.agents_file.exists():
            raise FileNotFoundError(f"Agents file not found: {self.agents_file}")

        with open(self.agents_file, 'r') as f:
            data = json.load(f)

        result = {}
        agents_list = data.get('agents', []) if isinstance(data, dict) else data

        for agent in agents_list:
            if isinstance(agent, dict):
                agent_file = agent.get('agent-file')
                name = agent.get('name')
                if agent_file and name:
                    result[agent_file] = name

        return result

    # =========================================================================
    # CONTRACT AND STATE METHODS
    # =========================================================================

    def get_agent_contracts(self) -> Optional[dict]:
        """Load AGENT_CONTRACTS.json."""
        if not self.contracts_file.exists():
            return None

        with open(self.contracts_file, 'r') as f:
            return json.load(f)

    def get_workflow_states(self) -> Optional[dict]:
        """Load WORKFLOW_STATES.json."""
        if not self.states_file.exists():
            return None

        with open(self.states_file, 'r') as f:
            return json.load(f)

    def get_agent_contract(self, agent: str) -> Optional[dict]:
        """Get contract for specific agent."""
        contracts = self.get_agent_contracts()
        return contracts.get('agents', {}).get(agent) if contracts else None

    def validate_source_file_pattern(self, agent: str, source_file: str) -> Tuple[bool, str]:
        """Validate source file against agent's expected pattern."""
        contract = self.get_agent_contract(agent)
        if not contract:
            return True, "No contract found"

        required_inputs = contract.get('inputs', {}).get('required', [])
        if not required_inputs:
            return True, "No input pattern specified"

        pattern = required_inputs[0].get('pattern', '')
        if not pattern:
            return True, "No pattern specified"

        regex_pattern = pattern.replace('{enhancement_name}', r'([^/]+)')
        regex_pattern = f"^{regex_pattern}$"

        if re.match(regex_pattern, source_file):
            return True, f"✓ Matches pattern: {pattern}"
        else:
            return False, f"✗ Expected pattern: {pattern}"

    def get_expected_output_path(self, agent: str, source_file: str) -> Optional[str]:
        """Get expected output path for an agent."""
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

    def get_next_agents(self, agent: str, status: str) -> List[str]:
        """Get next agents based on current agent and status."""
        contract = self.get_agent_contract(agent)
        if not contract:
            return []

        success_statuses = contract.get('statuses', {}).get('success', [])
        for status_def in success_statuses:
            if status_def.get('code') == status:
                return status_def.get('next_agents', [])

        return []

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def get_version(self) -> str:
        """Get CMAT version."""
        try:
            output = self._run_command("version")
            for line in output.split('\n'):
                if line.startswith('cmat v'):
                    return line.split('v')[1].strip()
            return "3.0.0"
        except RuntimeError:
            return "unknown"

    def get_task_types(self) -> Dict[str, str]:
        """Get available task types."""
        return {
            "analysis": "Analysis",
            "technical_analysis": "Technical Analysis",
            "implementation": "Implementation",
            "testing": "Testing",
            "documentation": "Documentation",
            "integration": "Integration"
        }

    def get_priorities(self) -> List[str]:
        """Get available priorities."""
        return ["critical", "high", "normal", "low"]

    def get_tools_data(self) -> Optional[Dict]:
        """Get tools configuration from tools.json."""
        if not self.tools_file.exists():
            return None

        with open(self.tools_file, 'r') as f:
            return json.load(f)

    def get_task_log(self, task_id: str, source_file: str) -> Optional[str]:
        """Get log content for a task."""
        enhancement_name = self._extract_enhancement_name(source_file)
        if not enhancement_name:
            return None

        log_dir = self.project_root / "enhancements" / enhancement_name / "logs"
        if not log_dir.exists():
            return None

        log_files = list(log_dir.glob(f"*{task_id}*.log"))
        if not log_files:
            return None

        log_file = max(log_files, key=lambda p: p.stat().st_mtime)
        with open(log_file, 'r') as f:
            return f.read()

    def task_log_exists(self, task_id: str, source_file: str) -> bool:
        """Check if log exists for a task."""
        return self.get_task_log(task_id, source_file) is not None

    def get_operations_log(self, max_lines: int = 1000) -> str:
        """Get operations log content."""
        log_file = self.logs_dir / "queue_operations.log"
        if not log_file.exists():
            return "No operations log found."

        with open(log_file, 'r') as f:
            lines = f.readlines()
        return ''.join(lines[-max_lines:])

    def extract_skills_used(self, log_content: str) -> List[str]:
        """Extract skills that were applied from task log."""
        skills_used = []

        if "Skills Applied" not in log_content:
            return skills_used

        lines = log_content.split('\n')
        in_skills = False

        for line in lines:
            if "## Skills Applied" in line or "Skills Applied:" in line:
                in_skills = True
                continue
            elif in_skills:
                # Look for checkbox pattern: - ✅ **skill-name**: description
                if line.startswith('- ✅'):
                    match = re.search(r'\*\*([^*]+)\*\*', line)
                    if match:
                        skills_used.append(match.group(1))
                elif not line.strip() or line.startswith('#'):
                    # End of skills section
                    break

        return skills_used

    def _extract_enhancement_name(self, source_file: str) -> Optional[str]:
        """Extract enhancement name from source file path."""
        match = re.match(r'^enhancements/([^/]+)/', source_file)
        return match.group(1) if match else None