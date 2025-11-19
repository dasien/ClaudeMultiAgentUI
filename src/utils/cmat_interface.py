"""
CMAT interface for communicating with the cmat.sh script system.
Version 5.0 - Updated for workflow-based orchestration.
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re

from ..models import Task, AgentStatus, QueueState


class CMATInterface:
    """Interface to the cmat.sh command system (v5.0+)."""

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
        self.skills_file = self.project_root / ".claude/skills/skills.json"
        self.templates_file = self.project_root / ".claude/queues/workflow_templates.json"

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
        """Clear all completed and failed tasks from history."""
        self._run_command("queue", "clear-finished", "--force")

    def reset_queue(self):
        """Reset the entire queue system to empty state."""
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
    # WORKFLOW COMMANDS (v5.0)
    # =========================================================================

    def start_workflow(self, workflow_name: str, enhancement_name: str) -> subprocess.Popen:
        """
        Start a workflow using 'cmat workflow start'.

        Args:
            workflow_name: Name of workflow template
            enhancement_name: Name of enhancement

        Returns:
            Process handle for async execution
        """
        return self._run_command_async("workflow", "start", workflow_name, enhancement_name)

    def get_workflow_templates(self) -> List:
        """Get all workflow templates using WorkflowTemplate model."""
        from ..models import WorkflowTemplate

        if not self.templates_file.exists():
            return []

        try:
            with open(self.templates_file, 'r') as f:
                data = json.load(f)

            templates = []
            workflows_dict = data.get('workflows', {})

            for slug, template_data in workflows_dict.items():
                template = WorkflowTemplate.from_dict(slug, template_data)
                templates.append(template)

            return templates
        except (json.JSONDecodeError, IOError):
            return []

    def get_workflow_template(self, slug: str):
        """Get a specific workflow template by slug."""
        from ..models import WorkflowTemplate

        if not self.templates_file.exists():
            return None

        try:
            with open(self.templates_file, 'r') as f:
                data = json.load(f)

            template_data = data.get('workflows', {}).get(slug)
            if not template_data:
                return None

            return WorkflowTemplate.from_dict(slug, template_data)
        except (json.JSONDecodeError, IOError):
            return None

    def get_workflow_step_details(self, workflow_name: str, step_index: int) -> Optional[Dict]:
        """
        Get details for a specific workflow step.

        Args:
            workflow_name: Name of workflow template
            step_index: Step index (0-based)

        Returns:
            Step details dict or None if not found
        """
        template = self.get_workflow_template(workflow_name)
        if not template or step_index >= len(template.steps):
            return None

        step = template.steps[step_index]
        return {
            'agent': step.agent,
            'input': step.input,
            'required_output': step.required_output,
            'on_status': step.on_status,
            'description': step.description
        }

    def get_step_expected_statuses(self, workflow_name: str, step_index: int) -> List[str]:
        """
        Get expected status codes for a workflow step.

        Args:
            workflow_name: Name of workflow template
            step_index: Step index (0-based)

        Returns:
            List of expected status codes
        """
        step_details = self.get_workflow_step_details(workflow_name, step_index)
        if not step_details:
            return []

        return list(step_details.get('on_status', {}).keys())

    def get_step_input_path(self, workflow_name: str, step_index: int,
                            enhancement_name: str) -> Optional[str]:
        """
        Get resolved input path for a workflow step.

        Args:
            workflow_name: Name of workflow template
            step_index: Step index (0-based)
            enhancement_name: Enhancement name for placeholder substitution

        Returns:
            Resolved input path or None
        """
        step_details = self.get_workflow_step_details(workflow_name, step_index)
        if not step_details:
            return None

        input_pattern = step_details['input']

        # Substitute {enhancement_name}
        resolved = input_pattern.replace('{enhancement_name}', enhancement_name)

        # Handle {previous_step} - need previous agent info
        if step_index > 0 and '{previous_step}' in resolved:
            prev_step = self.get_workflow_step_details(workflow_name, step_index - 1)
            if prev_step:
                prev_agent = prev_step['agent']
                resolved = resolved.replace('{previous_step}',
                                            f"enhancements/{enhancement_name}/{prev_agent}")

        return resolved

    def get_step_output_path(self, workflow_name: str, step_index: int,
                             enhancement_name: str, agent: str) -> Optional[str]:
        """
        Get expected output path for a workflow step.

        Args:
            workflow_name: Name of workflow template
            step_index: Step index (0-based)
            enhancement_name: Enhancement name
            agent: Agent name

        Returns:
            Expected output path or None
        """
        step_details = self.get_workflow_step_details(workflow_name, step_index)
        if not step_details:
            return None

        required_output = step_details['required_output']
        return f"enhancements/{enhancement_name}/{agent}/required_output/{required_output}"

    def validate_step_output(self, workflow_name: str, step_index: int,
                             agent: str, enhancement_dir: str) -> Tuple[bool, str]:
        """
        Validate agent outputs for a workflow step.

        Args:
            workflow_name: Name of workflow template
            step_index: Step index (0-based)
            agent: Agent name
            enhancement_dir: Enhancement directory path

        Returns:
            (is_valid, message) tuple
        """
        step_details = self.get_workflow_step_details(workflow_name, step_index)
        if not step_details:
            return False, "Workflow step not found"

        required_output = step_details['required_output']

        try:
            output = self._run_command("workflow", "validate-output",
                                       agent, enhancement_dir, required_output)
            return True, output.strip()
        except RuntimeError as e:
            return False, str(e)

    def add_workflow_step(self, workflow_name: str, agent: str,
                          input_pattern: str, output_filename: str,
                          position: Optional[int] = None):
        """
        Add a step to a workflow template.

        Args:
            workflow_name: Name of workflow template
            agent: Agent to execute
            input_pattern: Input file/directory pattern
            output_filename: Required output filename
            position: Optional position to insert (default: append)
        """
        args = ["workflow", "add-step", workflow_name, agent, input_pattern, output_filename]
        if position is not None:
            args.append(str(position))
        self._run_command(*args)

    def edit_workflow_step(self, workflow_name: str, step_number: int,
                           input_pattern: Optional[str] = None,
                           output_filename: Optional[str] = None):
        """
        Edit an existing workflow step.

        Args:
            workflow_name: Name of workflow template
            step_number: Step number (1-based as shown to user)
            input_pattern: New input pattern (optional)
            output_filename: New output filename (optional)
        """
        args = ["workflow", "edit-step", workflow_name, str(step_number)]
        if input_pattern:
            args.append(input_pattern)
        if output_filename:
            args.append(output_filename)
        self._run_command(*args)

    def remove_workflow_step(self, workflow_name: str, step_number: int):
        """
        Remove a step from workflow template.

        Args:
            workflow_name: Name of workflow template
            step_number: Step number (1-based as shown to user)
        """
        self._run_command("workflow", "remove-step", workflow_name, str(step_number))

    def add_workflow_transition(self, workflow_name: str, step_number: int,
                                status: str, next_step: str, auto_chain: bool = True):
        """
        Add status transition to workflow step.

        Args:
            workflow_name: Name of workflow template
            step_number: Step number (0-based)
            status: Status code
            next_step: Next agent name or 'null' for end
            auto_chain: Whether to auto-chain
        """
        self._run_command("workflow", "add-transition",
                          workflow_name, str(step_number), status, next_step,
                          "true" if auto_chain else "false")

    def remove_workflow_transition(self, workflow_name: str, step_number: int, status: str):
        """
        Remove status transition from workflow step.

        Args:
            workflow_name: Name of workflow template
            step_number: Step number (0-based)
            status: Status code to remove
        """
        self._run_command("workflow", "remove-transition",
                          workflow_name, str(step_number), status)

    def list_workflow_transitions(self, workflow_name: str, step_number: int) -> List[Dict]:
        """
        List transitions for a workflow step.

        Args:
            workflow_name: Name of workflow template
            step_number: Step number (0-based)

        Returns:
            List of transition dicts with 'status', 'next_step', 'auto_chain'
        """
        try:
            output = self._run_command("workflow", "list-transitions",
                                       workflow_name, str(step_number))
            # Parse output format: "STATUS → NEXT (auto_chain: true)"
            transitions = []
            for line in output.strip().split('\n'):
                if '→' in line:
                    match = re.match(r'\s*(\S+)\s*→\s*(\S+)\s*\(auto_chain:\s*(\w+)\)', line)
                    if match:
                        transitions.append({
                            'status': match.group(1),
                            'next_step': match.group(2),
                            'auto_chain': match.group(3) == 'true'
                        })
            return transitions
        except RuntimeError:
            return []

    def validate_workflow(self, workflow_name: str) -> Tuple[bool, List[str]]:
        """
        Validate a workflow template.

        Args:
            workflow_name: Name of workflow template

        Returns:
            (is_valid, messages) tuple
        """
        try:
            output = self._run_command("workflow", "validate", workflow_name)
            lines = [line.strip() for line in output.split('\n') if line.strip()]
            is_valid = any('validation passed' in line.lower() for line in lines)
            return is_valid, lines
        except RuntimeError as e:
            return False, [str(e)]

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

    def get_agent_role(self, agent: str) -> Optional[str]:
        """
        Get role for specific agent.

        Args:
            agent: Agent key (agent-file)

        Returns:
            Role string or None
        """
        agents_data = self.get_agents_data()
        if not agents_data:
            return None

        agents_list = agents_data.get('agents', [])
        for agent_data in agents_list:
            if agent_data.get('agent-file') == agent:
                return agent_data.get('role')

        return None

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
            return "5.0.0"
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

        agent_output = log_content
        if "END OF PROMPT" in log_content:
            agent_output = log_content.split("END OF PROMPT", 1)[1]

        # Try new format first: SKILLS_USED: skill1, skill2, skill3
        if "SKILLS_USED:" in agent_output:
            match = re.search(r'SKILLS_USED:\s*([^\n]+)', agent_output)
            if match:
                skills_line = match.group(1).strip()
                skills_used = [skill.strip() for skill in skills_line.split(',') if skill.strip()]
                return skills_used

        # Fall back to old format: ## Skills Applied
        if "Skills Applied" not in log_content:
            return skills_used

        lines = log_content.split('\n')
        in_skills = False

        for line in lines:
            if "## Skills Applied" in line or "Skills Applied:" in line:
                in_skills = True
                continue
            elif in_skills:
                if line.startswith('- ✅'):
                    match = re.search(r'\*\*([^*]+)\*\*', line)
                    if match:
                        skills_used.append(match.group(1))
                elif not line.strip() or line.startswith('#'):
                    break

        return skills_used

    def _extract_enhancement_name(self, source_file: str) -> Optional[str]:
        """Extract enhancement name from source file path."""
        match = re.match(r'^enhancements/([^/]+)/', source_file)
        return match.group(1) if match else None