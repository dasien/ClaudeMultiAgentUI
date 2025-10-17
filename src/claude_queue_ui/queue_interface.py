"""
Queue interface for communicating with the queue_manager.sh script.
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

from .queue_models import Task, AgentStatus, QueueState


class QueueInterface:
    """Interface to the queue_manager.sh bash script."""

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

        Args:
            title: Task title
            agent: Agent name
            priority: Task priority (critical, high, normal, low)
            task_type: Task type (analysis, technical_analysis, implementation, testing)
            source_file: Source file path
            description: Task description
            auto_complete: Whether to enable auto-completion
            auto_chain: Whether to enable auto-chaining

        Returns:
            Task ID
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

        # Debug output
        import sys
        debug_msg = f"DEBUG: add_task called with auto_complete={auto_complete}, auto_chain={auto_chain}"
        print(debug_msg, file=sys.stderr)
        print(debug_msg)
        cmd_msg = f"DEBUG: Command: {self.script_path} {' '.join(repr(arg) for arg in args)}"
        print(cmd_msg, file=sys.stderr)
        print(cmd_msg)

        output = self._run_command(*args)

        # Extract task ID from output (last line should be task ID)
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

    def get_queue_state(self) -> QueueState:
        """Get current queue state by reading JSON directly.

        Returns:
            QueueState object
        """
        with open(self.queue_file, 'r') as f:
            data = json.load(f)

        # Helper to parse tasks with defaults for missing fields
        def parse_task(task_data: dict) -> Task:
            # Provide defaults for fields that may be missing in older tasks
            return Task(
                id=task_data['id'],
                title=task_data['title'],
                assigned_agent=task_data['assigned_agent'],
                priority=task_data['priority'],
                task_type=task_data.get('task_type', 'unknown'),
                description=task_data['description'],
                source_file=task_data.get('source_file', ''),
                created=task_data['created'],
                status=task_data['status'],
                started=task_data.get('started'),
                completed=task_data.get('completed'),
                result=task_data.get('result')
            )

        # Parse tasks
        pending_tasks = [parse_task(task) for task in data.get('pending_tasks', [])]
        active_workflows = [parse_task(task) for task in data.get('active_workflows', [])]
        completed_tasks = [parse_task(task) for task in data.get('completed_tasks', [])]
        failed_tasks = [parse_task(task) for task in data.get('failed_tasks', [])]

        # Parse agent status
        agent_status = {}
        for agent_name, status_data in data.get('agent_status', {}).items():
            agent_status[agent_name] = AgentStatus(
                name=agent_name,
                status=status_data.get('status', 'unknown'),
                current_task=status_data.get('current_task'),
                last_activity=status_data.get('last_activity')
            )

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
        print(f"DEBUG: agents.json data: {data}")

        result = {}

        # agents.json format may vary - adjust as needed
        if isinstance(data, list):
            # Handle list of dicts with agent-file and name
            for agent in data:
                if isinstance(agent, dict):
                    agent_file = agent.get('agent-file')
                    name = agent.get('name')
                    if agent_file and name:
                        result[agent_file] = name
                    else:
                        # Fallback for older format
                        name = agent.get('Name') or agent.get('name') or str(agent)
                        result[name] = name
                else:
                    # Simple string format
                    result[str(agent)] = str(agent)
        elif isinstance(data, dict):
            # Iterate over dictionary values to get agent names
            for agent in data.get('agents', []):
                if isinstance(agent, dict):
                    agent_file = agent.get('agent-file')
                    name = agent.get('name')
                    if agent_file and name:
                        result[agent_file] = name
                    elif name:
                        result[name] = name

        print(f"DEBUG: Parsed agents map: {result}")
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
            "testing": "Testing"
        }

    def get_priorities(self) -> List[str]:
        """Get list of available priorities.

        Returns:
            List of priority names
        """
        return [
            "Critical",
            "High",
            "Normal",
            "Low"
        ]

    def get_task_log(self, task_id: str, source_file: str) -> Optional[str]:
        """Get log content for a task.

        Args:
            task_id: Task ID
            source_file: Source file path to help locate log

        Returns:
            Log content or None if not found
        """
        # Determine log directory from source file
        source_path = Path(source_file)
        if not source_path.is_absolute():
            source_path = self.project_root / source_path

        log_dir = source_path.parent / "logs"

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