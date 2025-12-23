"""
CMAT interface for communicating with the CMAT Python API.
Version 8.0 - Direct Python API integration (no subprocess calls).
"""

import sys
import json
import threading
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from ..models import Task, AgentStatus, QueueState
from .path_utils import PathUtils


class CMATInterface:
    """Direct Python interface to CMAT v8.2+ system."""

    def __init__(self, project_root: str):
        """Initialize the CMAT interface.

        Args:
            project_root: Path to project root directory (contains .claude/)
        """
        self.project_root = Path(project_root)

        # Validate project structure
        claude_dir = self.project_root / ".claude"
        if not claude_dir.exists():
            raise FileNotFoundError(f"No .claude directory found in {self.project_root}")

        cmat_package = claude_dir / "cmat" / "__init__.py"
        if not cmat_package.exists():
            raise FileNotFoundError(
                f"CMAT Python package not found at {cmat_package}\n"
                "Please install CMAT v8.2+ using File > Install..."
            )

        # Add .claude to Python path for importing cmat
        claude_path_str = str(claude_dir)
        if claude_path_str not in sys.path:
            sys.path.insert(0, claude_path_str)

        # Import and initialize CMAT
        try:
            from cmat import CMAT
            self.cmat = CMAT(base_path=str(self.project_root))
        except ImportError as e:
            raise ImportError(
                f"Failed to import CMAT: {e}\n"
                "Required dependencies may be missing. Install with:\n"
                "  pip install pyyaml"
            )

        # Update file paths to new locations (v8.2+)
        self.queue_file = self.project_root / ".claude/data/task_queue.json"
        self.templates_file = self.project_root / ".claude/data/workflow_templates.json"
        self.learnings_file = self.project_root / ".claude/data/learnings.json"
        self.models_file = self.project_root / ".claude/data/models.json"
        self.logs_dir = self.project_root / ".claude/logs"
        self.agents_file = self.project_root / ".claude/agents/agents.json"
        self.tools_file = self.project_root / ".claude/tools/tools.json"
        self.skills_file = self.project_root / ".claude/skills/skills.json"

        # Ensure directories exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # QUEUE COMMANDS
    # =========================================================================

    def add_task(self, title: str, agent: str, priority: str,
                 task_type: str, source_file: str, description: str,
                 auto_complete: bool = False, auto_chain: bool = False) -> str:
        """Add a new task to the queue."""
        task = self.cmat.queue.add(
            title=title,
            assigned_agent=agent,
            priority=priority,
            task_type=task_type,
            source_file=source_file,
            description=description,
            auto_complete=auto_complete,
            auto_chain=auto_chain,
        )
        return task.id

    def start_task(self, task_id: str):
        """Start a task asynchronously."""
        def execute():
            try:
                self.cmat.workflow.run_task(task_id)
            except Exception as e:
                print(f"Error executing task {task_id}: {e}")

        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        return None  # UI doesn't actually use the process handle

    def complete_task(self, task_id: str, result: str = "", auto_chain: bool = False):
        """Complete a task."""
        self.cmat.queue.complete(task_id, result=result)
        if auto_chain:
            # Trigger workflow auto-chain if applicable
            task = self.cmat.queue.get(task_id)
            if task and task.metadata and task.metadata.workflow_name:
                self.cmat.workflow.handle_completion(task)

    def cancel_task(self, task_id: str, reason: str = ""):
        """Cancel a task."""
        self.cmat.queue.cancel(task_id, reason=reason)

    def rerun_task(self, task_id: str):
        """Re-run a completed or failed task."""
        self.cmat.queue.rerun(task_id)

    def cancel_all_tasks(self, reason: str = ""):
        """Cancel all pending and active tasks."""
        tasks = self.cmat.queue.list_tasks()  # Get all tasks
        for task in tasks:
            if task.status.value in ['pending', 'active']:
                self.cmat.queue.cancel(task.id, reason=reason)

    def clear_finished_tasks(self):
        """Clear all completed and failed tasks from history."""
        queue_data = self._read_queue_file()
        queue_data['tasks'] = [
            t for t in queue_data.get('tasks', [])
            if t.get('status') not in ['completed', 'failed']
        ]
        self._write_queue_file(queue_data)

    def reset_queue(self):
        """Reset the entire queue system to empty state."""
        empty_queue = {
            "queue_metadata": {
                "created": datetime.utcnow().isoformat() + "Z",
                "version": "3.0.0",
                "description": "Task queue for multi-agent development system"
            },
            "tasks": [],
            "agent_status": {}
        }
        self._write_queue_file(empty_queue)

    def fail_task(self, task_id: str, error: str = ""):
        """Fail a task."""
        self.cmat.queue.fail(task_id, error=error)

    def update_metadata(self, task_id: str, key: str, value: str):
        """Update task metadata."""
        task = self.cmat.queue.get(task_id)
        if task and task.metadata:
            # Update metadata directly in queue file
            queue_data = self._read_queue_file()
            for task_data in queue_data.get('tasks', []):
                if task_data['id'] == task_id:
                    if 'metadata' not in task_data:
                        task_data['metadata'] = {}
                    task_data['metadata'][key] = value
                    break
            self._write_queue_file(queue_data)

    def get_queue_state(self) -> QueueState:
        """Get current queue state."""
        all_tasks = self.cmat.queue.list_tasks()  # Get all tasks regardless of status

        def convert_task(cmat_task) -> Task:
            """Convert CMAT Task model to UI Task model."""
            start_datetime = None
            end_datetime = None
            runtime_seconds = None

            # CMAT v8.2+ uses datetime objects, not strings
            if cmat_task.started:
                try:
                    if isinstance(cmat_task.started, datetime):
                        start_datetime = int(cmat_task.started.timestamp())
                    else:
                        # Fallback for string format
                        start_dt = datetime.fromisoformat(str(cmat_task.started).replace('Z', '+00:00'))
                        start_datetime = int(start_dt.timestamp())
                except (ValueError, AttributeError, TypeError):
                    pass

            if cmat_task.completed:
                try:
                    if isinstance(cmat_task.completed, datetime):
                        end_datetime = int(cmat_task.completed.timestamp())
                    else:
                        # Fallback for string format
                        end_dt = datetime.fromisoformat(str(cmat_task.completed).replace('Z', '+00:00'))
                        end_datetime = int(end_dt.timestamp())
                except (ValueError, AttributeError, TypeError):
                    pass

            # CMAT v8.2+ uses get_duration_seconds() method
            try:
                runtime_seconds = cmat_task.get_duration_seconds()
            except (AttributeError, TypeError):
                # Fallback to direct attribute if method doesn't exist
                runtime_seconds = getattr(cmat_task, 'runtime_seconds', None)

            # Convert metadata
            metadata_dict = None
            if cmat_task.metadata:
                metadata_dict = cmat_task.metadata.to_dict()

            # Convert datetime objects to ISO strings for UI
            created_str = cmat_task.created.isoformat() if isinstance(cmat_task.created, datetime) else cmat_task.created
            started_str = cmat_task.started.isoformat() if isinstance(cmat_task.started, datetime) else cmat_task.started
            completed_str = cmat_task.completed.isoformat() if isinstance(cmat_task.completed, datetime) else cmat_task.completed

            return Task(
                id=cmat_task.id,
                title=cmat_task.title,
                assigned_agent=cmat_task.assigned_agent,
                priority=cmat_task.priority.value if hasattr(cmat_task.priority, 'value') else cmat_task.priority,
                task_type=cmat_task.task_type,
                description=cmat_task.description,
                source_file=cmat_task.source_file,
                created=created_str,
                status=cmat_task.status.value if hasattr(cmat_task.status, 'value') else cmat_task.status,
                started=started_str,
                completed=completed_str,
                result=cmat_task.result,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                runtime_seconds=runtime_seconds,
                auto_complete=cmat_task.auto_complete,
                auto_chain=cmat_task.auto_chain,
                metadata=metadata_dict
            )

        ui_tasks = [convert_task(t) for t in all_tasks]

        return QueueState(
            pending_tasks=[t for t in ui_tasks if t.status == 'pending'],
            active_workflows=[t for t in ui_tasks if t.status == 'active'],
            completed_tasks=[t for t in ui_tasks if t.status == 'completed'],
            failed_tasks=[t for t in ui_tasks if t.status == 'failed'],
            agent_status={}
        )

    # =========================================================================
    # WORKFLOW COMMANDS
    # =========================================================================

    def start_workflow(self, workflow_name: str, enhancement_name: str):
        """Start a workflow."""
        # Create task but don't execute yet (execute=False)
        # UI handles async execution in its own thread
        task_id = self.cmat.workflow.start_workflow(
            workflow_name, enhancement_name, execute=False
        )

        # Execute first task asynchronously
        def execute():
            try:
                self.cmat.workflow.run_task(task_id)
            except Exception as e:
                print(f"Error starting workflow {workflow_name}: {e}")

        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        return task_id

    def get_workflow_templates(self) -> List:
        """Get all workflow templates."""
        from ..models import WorkflowTemplate

        templates = self.cmat.workflow.list_all()

        # Convert CMAT workflow models to UI models
        ui_templates = []
        for cmat_template in templates:
            ui_template = WorkflowTemplate.from_dict(
                cmat_template.id,
                {
                    'name': cmat_template.name,
                    'description': cmat_template.description,
                    'steps': [
                        {
                            'agent': step.agent,
                            'input': step.input,
                            'required_output': step.required_output,
                            'on_status': {
                                status: {
                                    'next_step': trans.next_step,
                                    'auto_chain': trans.auto_chain
                                }
                                for status, trans in (step.on_status or {}).items()
                            }
                        }
                        for step in cmat_template.steps
                    ]
                }
            )
            ui_templates.append(ui_template)

        return ui_templates

    def get_workflow_template(self, slug: str):
        """Get a specific workflow template by slug."""
        from ..models import WorkflowTemplate

        cmat_template = self.cmat.workflow.get(slug)
        if not cmat_template:
            return None

        return WorkflowTemplate.from_dict(
            cmat_template.id,
            {
                'name': cmat_template.name,
                'description': cmat_template.description,
                'steps': [
                    {
                        'agent': step.agent,
                        'input': step.input,
                        'required_output': step.required_output,
                        'on_status': {
                            status: {
                                'next_step': trans.next_step,
                                'auto_chain': trans.auto_chain
                            }
                            for status, trans in (step.on_status or {}).items()
                        }
                    }
                    for step in cmat_template.steps
                ]
            }
        )

    def get_workflow_step_details(self, workflow_name: str, step_index: int) -> Optional[Dict]:
        """Get details for a specific workflow step."""
        template = self.cmat.workflow.get(workflow_name)
        if not template or step_index >= len(template.steps):
            return None

        step = template.steps[step_index]
        return {
            'agent': step.agent,
            'input': step.input,
            'required_output': step.required_output,
            'on_status': {
                status: {
                    'next_step': trans.next_step,
                    'auto_chain': trans.auto_chain
                }
                for status, trans in (step.on_status or {}).items()
            }
        }

    def get_step_expected_statuses(self, workflow_name: str, step_index: int) -> List[str]:
        """Get expected status codes for a workflow step."""
        step_details = self.get_workflow_step_details(workflow_name, step_index)
        if not step_details:
            return []
        return list(step_details.get('on_status', {}).keys())

    def get_step_input_path(self, workflow_name: str, step_index: int,
                            enhancement_name: str) -> Optional[str]:
        """Get resolved input path for a workflow step."""
        step_details = self.get_workflow_step_details(workflow_name, step_index)
        if not step_details:
            return None

        input_pattern = step_details['input']
        resolved = input_pattern.replace('{enhancement_name}', enhancement_name)

        if step_index > 0 and '{previous_step}' in resolved:
            prev_step = self.get_workflow_step_details(workflow_name, step_index - 1)
            if prev_step:
                prev_agent = prev_step['agent']
                resolved = resolved.replace('{previous_step}',
                                          f"enhancements/{enhancement_name}/{prev_agent}")

        return resolved

    def get_step_output_path(self, workflow_name: str, step_index: int,
                             enhancement_name: str, agent: str) -> Optional[str]:
        """Get expected output path for a workflow step."""
        step_details = self.get_workflow_step_details(workflow_name, step_index)
        if not step_details:
            return None

        required_output = step_details['required_output']
        return f"enhancements/{enhancement_name}/{agent}/required_output/{required_output}"

    def validate_step_output(self, workflow_name: str, step_index: int,
                             agent: str, enhancement_dir: str) -> Tuple[bool, str]:
        """Validate agent outputs for a workflow step."""
        step_details = self.get_workflow_step_details(workflow_name, step_index)
        if not step_details:
            return False, "Workflow step not found"

        required_output = step_details['required_output']
        output_path = Path(enhancement_dir) / agent / "required_output" / required_output

        if output_path.exists():
            return True, f"Output file found: {output_path}"
        else:
            return False, f"Required output not found: {output_path}"

    def add_workflow_step(self, workflow_name: str, agent: str,
                          input_pattern: str, output_filename: str,
                          position: Optional[int] = None):
        """Add a step to a workflow template."""
        # This would require implementing in CMAT Python API
        # For now, direct JSON manipulation
        templates_data = self._read_templates_file()
        workflow = templates_data.get('workflows', {}).get(workflow_name)
        if not workflow:
            raise ValueError(f"Workflow {workflow_name} not found")

        new_step = {
            'agent': agent,
            'input': input_pattern,
            'required_output': output_filename,
            'description': '',
            'on_status': {}
        }

        if position is None:
            workflow['steps'].append(new_step)
        else:
            workflow['steps'].insert(position, new_step)

        self._write_templates_file(templates_data)

    def edit_workflow_step(self, workflow_name: str, step_number: int,
                           input_pattern: Optional[str] = None,
                           output_filename: Optional[str] = None):
        """Edit an existing workflow step."""
        templates_data = self._read_templates_file()
        workflow = templates_data.get('workflows', {}).get(workflow_name)
        if not workflow:
            raise ValueError(f"Workflow {workflow_name} not found")

        step_index = step_number - 1
        if step_index >= len(workflow['steps']):
            raise ValueError(f"Step {step_number} not found")

        step = workflow['steps'][step_index]
        if input_pattern:
            step['input'] = input_pattern
        if output_filename:
            step['required_output'] = output_filename

        self._write_templates_file(templates_data)

    def remove_workflow_step(self, workflow_name: str, step_number: int):
        """Remove a step from workflow template."""
        templates_data = self._read_templates_file()
        workflow = templates_data.get('workflows', {}).get(workflow_name)
        if not workflow:
            raise ValueError(f"Workflow {workflow_name} not found")

        step_index = step_number - 1
        if step_index >= len(workflow['steps']):
            raise ValueError(f"Step {step_number} not found")

        workflow['steps'].pop(step_index)
        self._write_templates_file(templates_data)

    def add_workflow_transition(self, workflow_name: str, step_number: int,
                                status: str, next_step: str, auto_chain: bool = True):
        """Add status transition to workflow step."""
        templates_data = self._read_templates_file()
        workflow = templates_data.get('workflows', {}).get(workflow_name)
        if not workflow:
            raise ValueError(f"Workflow {workflow_name} not found")

        step_index = step_number
        if step_index >= len(workflow['steps']):
            raise ValueError(f"Step {step_number} not found")

        step = workflow['steps'][step_index]
        if 'on_status' not in step:
            step['on_status'] = {}

        step['on_status'][status] = {
            'next_step': next_step,
            'auto_chain': auto_chain
        }

        self._write_templates_file(templates_data)

    def remove_workflow_transition(self, workflow_name: str, step_number: int, status: str):
        """Remove status transition from workflow step."""
        templates_data = self._read_templates_file()
        workflow = templates_data.get('workflows', {}).get(workflow_name)
        if not workflow:
            raise ValueError(f"Workflow {workflow_name} not found")

        step_index = step_number
        if step_index >= len(workflow['steps']):
            raise ValueError(f"Step {step_number} not found")

        step = workflow['steps'][step_index]
        if 'on_status' in step and status in step['on_status']:
            del step['on_status'][status]

        self._write_templates_file(templates_data)

    def list_workflow_transitions(self, workflow_name: str, step_number: int) -> List[Dict]:
        """List transitions for a workflow step."""
        step_details = self.get_workflow_step_details(workflow_name, step_number)
        if not step_details:
            return []

        transitions = []
        for status, trans in step_details.get('on_status', {}).items():
            transitions.append({
                'status': status,
                'next_step': trans['next_step'],
                'auto_chain': trans['auto_chain']
            })

        return transitions

    def validate_workflow(self, workflow_name: str) -> Tuple[bool, List[str]]:
        """Validate a workflow template."""
        template = self.cmat.workflow.get(workflow_name)
        if not template:
            return False, [f"Workflow {workflow_name} not found"]

        messages = []
        is_valid = True

        # Check each step
        for i, step in enumerate(template.steps):
            # Check agent exists
            agent = self.cmat.agents.get(step.agent)
            if not agent:
                messages.append(f"Step {i+1}: Agent '{step.agent}' not found")
                is_valid = False

            # Check required fields
            if not step.input:
                messages.append(f"Step {i+1}: Missing input pattern")
                is_valid = False
            if not step.required_output:
                messages.append(f"Step {i+1}: Missing required output")
                is_valid = False

            # Check transitions reference valid steps
            if step.on_status:
                for status, trans in step.on_status.items():
                    if trans.next_step and trans.next_step != 'null':
                        # Check if next_step agent exists
                        next_agent = self.cmat.agents.get(trans.next_step)
                        if not next_agent:
                            messages.append(
                                f"Step {i+1}: Transition '{status}' references "
                                f"unknown agent '{trans.next_step}'"
                            )
                            is_valid = False

        if is_valid:
            messages.append("✓ Workflow validation passed")

        return is_valid, messages

    # =========================================================================
    # SKILLS COMMANDS
    # =========================================================================

    def get_skills_list(self) -> Optional[Dict]:
        """Get all available skills."""
        skills = self.cmat.skills.list_all()

        # Convert to dict format expected by UI
        return {
            "skills": [
                {
                    "name": skill.name,
                    "directory": skill.skill_directory,
                    "category": skill.category,
                    "description": skill.description or ""
                }
                for skill in skills
            ]
        }

    def get_agent_skills(self, agent: str) -> List[str]:
        """Get skills assigned to an agent."""
        agent_obj = self.cmat.agents.get(agent)
        if not agent_obj:
            return []
        return agent_obj.skills

    def load_skill_content(self, skill_directory: str) -> Optional[str]:
        """Load skill content from directory."""
        skill = self.cmat.skills.get(skill_directory)
        if not skill:
            return None

        skill_path = self.project_root / ".claude/skills" / skill_directory / "SKILL.md"
        if skill_path.exists():
            return skill_path.read_text()
        return None

    def get_skills_prompt(self, agent: str) -> Optional[str]:
        """Build complete skills section for agent prompt."""
        return self.cmat.skills.build_prompt(agent)

    # =========================================================================
    # INTEGRATION COMMANDS (Placeholder - not in CMAT v8 yet)
    # =========================================================================

    def add_integration_task(self, workflow_status: str, source_file: str,
                             previous_agent: str, parent_task_id: str = "") -> str:
        """Add integration task (not yet implemented in CMAT v8)."""
        # TODO: Implement when integration service is added to CMAT Python
        return ""

    def sync_task_external(self, task_id: str):
        """Sync task to external systems (not yet implemented)."""
        pass

    def sync_all_external(self):
        """Sync all unsynced tasks (not yet implemented)."""
        pass

    # =========================================================================
    # AGENT COMMANDS
    # =========================================================================

    def run_agent_direct(
            self,
            agent_name: str,
            input_file: Path,
            output_dir: Path,
            task_description: str = "UI-invoked task",
            task_type: str = "analysis"
    ) -> Path:
        """Run an agent directly (synchronous)."""
        result = self.cmat.tasks.execute_direct(
            agent=agent_name,
            input_file=str(input_file),
            output_dir=str(output_dir),
            task_description=task_description,
            task_type=task_type
        )

        if not result.success:
            raise RuntimeError(f"Agent execution failed: {result.error}")

        return Path(output_dir)

    def run_agent_async(
            self,
            agent_name: str,
            input_file: Path,
            output_dir: Path,
            task_description: str = "UI-invoked task",
            task_type: str = "analysis",
            on_success=None,
            on_error=None
    ):
        """Run an agent asynchronously."""
        def run_in_thread():
            try:
                result = self.cmat.tasks.execute_direct(
                    agent=agent_name,
                    input_file=str(input_file),
                    output_dir=str(output_dir),
                    task_description=task_description,
                    task_type=task_type
                )

                if result.success and on_success:
                    import tkinter as tk
                    root = tk._default_root
                    if root:
                        root.after(0, lambda: on_success(Path(output_dir)))
                    else:
                        on_success(Path(output_dir))
                elif not result.success and on_error:
                    import tkinter as tk
                    root = tk._default_root
                    if root:
                        root.after(0, lambda: on_error(Exception(result.error)))
                    else:
                        on_error(Exception(result.error))

            except Exception as ex:
                if on_error:
                    import tkinter as tk
                    root = tk._default_root
                    if root:
                        root.after(0, lambda: on_error(ex))
                    else:
                        on_error(ex)

        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()

    def get_agents_data(self) -> Optional[Dict]:
        """Get agents data."""
        agents = self.cmat.agents.list_all()

        return {
            'agents': [
                {
                    'name': agent.name,
                    'agent-file': agent.agent_file,
                    'role': agent.role,
                    'description': agent.description or '',
                    'tools': agent.tools,
                    'skills': agent.skills
                }
                for agent in agents
            ]
        }

    def regenerate_agents_json(self):
        """Regenerate agents.json from markdown files."""
        # CMAT Python auto-generates agents.json on demand
        # Just invalidate cache to force reload
        self.cmat.invalidate_caches()

    def get_agent_list(self) -> Dict[str, str]:
        """Get dictionary of available agents."""
        agents = self.cmat.agents.list_all()
        return {agent.agent_file: agent.name for agent in agents}

    def get_agent_role(self, agent: str) -> Optional[str]:
        """Get role for specific agent."""
        agent_obj = self.cmat.agents.get(agent)
        if not agent_obj:
            return None
        return agent_obj.role

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def get_version(self) -> str:
        """Get CMAT version."""
        from cmat import __version__
        return __version__

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
        """Get tools configuration."""
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
        import re

        skills_used = []
        agent_output = log_content

        if "END OF PROMPT" in log_content:
            agent_output = log_content.split("END OF PROMPT", 1)[1]

        # Try new format: SKILLS_USED: skill1, skill2
        if "SKILLS_USED:" in agent_output:
            match = re.search(r'SKILLS_USED:\s*([^\n]+)', agent_output)
            if match:
                skills_line = match.group(1).strip()
                skills_used = [s.strip() for s in skills_line.split(',') if s.strip()]
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

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _read_queue_file(self) -> dict:
        """Read queue file directly."""
        with open(self.queue_file, 'r') as f:
            return json.load(f)

    def _write_queue_file(self, data: dict):
        """Write queue file directly."""
        with open(self.queue_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _read_templates_file(self) -> dict:
        """Read templates file directly."""
        with open(self.templates_file, 'r') as f:
            return json.load(f)

    def _write_templates_file(self, data: dict):
        """Write templates file directly."""
        with open(self.templates_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _extract_enhancement_name(self, source_file: str) -> Optional[str]:
        """Extract enhancement name from source file path."""
        import re
        match = re.match(r'^enhancements/([^/]+)/', source_file)
        return match.group(1) if match else None

    # =========================================================================
    # SERVICE ACCESSORS (v8.2+ Python API)
    # =========================================================================

    @property
    def learnings(self):
        """Access the learnings service (RAG system)."""
        return self.cmat.learnings

    @property
    def models(self):
        """Access the models service (Claude model management)."""
        return self.cmat.models