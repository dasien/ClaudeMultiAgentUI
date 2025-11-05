"""
Workflow State Viewer - Visualize active workflows and their progress.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional
from collections import defaultdict

from .base_dialog import BaseDialog
from ..utils import TimeUtils


class WorkflowStateViewer(BaseDialog):
    """Dialog for visualizing workflow states and progress."""

    def __init__(self, parent, queue_interface):
        super().__init__(parent, "Active Workflows", 750, 600)
        self.queue = queue_interface
        self.workflows = {}

        self.build_ui()
        self.load_workflows()
        # Don't call show() - workflow viewer doesn't return a result

    def build_ui(self):
        """Build the workflow viewer UI."""
        # Main canvas for scrolling
        canvas = tk.Canvas(self.dialog)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        self.workflows_frame = ttk.Frame(canvas, padding=20)
        canvas.create_window((0, 0), window=self.workflows_frame, anchor='nw')

        # Bottom buttons - Using BaseDialog helper
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill="x", pady=10)

        ttk.Button(button_frame, text="Refresh", command=self.load_workflows).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side="left", padx=5)

    def load_workflows(self):
        """Load and display all active workflows."""
        for widget in self.workflows_frame.winfo_children():
            widget.destroy()

        try:
            queue_state = self.queue.get_queue_state()

            # Group tasks by enhancement
            enhancement_tasks = defaultdict(list)

            for task in (queue_state.pending_tasks +
                         queue_state.active_workflows +
                         queue_state.completed_tasks[-20:]):

                source = task.source_file
                if source.startswith('enhancements/'):
                    parts = source.split('/')
                    if len(parts) >= 2:
                        enhancement = parts[1]
                        enhancement_tasks[enhancement].append(task)

            if not enhancement_tasks:
                ttk.Label(
                    self.workflows_frame,
                    text="No active workflows found",
                    font=('Arial', 11),
                    foreground='gray'
                ).pack(pady=20)
                return

            # Display each workflow
            for enhancement, tasks in sorted(enhancement_tasks.items()):
                self.render_workflow(enhancement, tasks)

        except Exception as e:
            ttk.Label(
                self.workflows_frame,
                text=f"Error loading workflows: {e}",
                foreground='red'
            ).pack(pady=20)

    def render_workflow(self, enhancement: str, tasks: List):
        """Render a single workflow visualization."""
        workflow_state = self.analyze_workflow_state(tasks)

        # Create workflow frame
        workflow_frame = ttk.LabelFrame(
            self.workflows_frame,
            text=f"Enhancement: {enhancement}",
            padding=15
        )
        workflow_frame.pack(fill="x", pady=(0, 15))

        # Progress bar
        progress_frame = ttk.Frame(workflow_frame)
        progress_frame.pack(fill="x", pady=(0, 10))

        progress_pct = workflow_state['progress_percent']
        ttk.Label(
            progress_frame,
            text=f"{progress_pct}% complete",
            font=('Arial', 10, 'bold')
        ).pack(side="left")

        progress_bar = ttk.Progressbar(
            progress_frame,
            length=400,
            mode='determinate',
            value=progress_pct
        )
        progress_bar.pack(side="right", fill="x", expand=True, padx=(10, 0))

        # Workflow steps
        steps_frame = ttk.Frame(workflow_frame)
        steps_frame.pack(fill="x", pady=(10, 0))

        standard_agents = [
            'requirements-analyst',
            'architect',
            'implementer',
            'tester',
            'documenter'
        ]

        for i, agent in enumerate(standard_agents):
            step_state = workflow_state['agents'].get(agent, 'not_started')

            step_frame = ttk.Frame(steps_frame)
            step_frame.pack(anchor="w", pady=2)

            # Status icon
            if step_state == 'completed':
                icon, color = "✓", 'green'
            elif step_state == 'active':
                icon, color = "→", 'orange'
            elif step_state == 'failed':
                icon, color = "✗", 'red'
            elif step_state == 'pending':
                icon, color = "○", 'blue'
            else:
                icon, color = " ", 'gray'

            ttk.Label(
                step_frame,
                text=icon,
                font=('Arial', 12, 'bold'),
                foreground=color,
                width=2
            ).pack(side="left")

            agent_name = self.queue.get_agent_list().get(agent, agent)
            ttk.Label(
                step_frame,
                text=agent_name,
                font=('Arial', 10)
            ).pack(side="left", padx=(5, 0))

            # Show task info if exists - Using TimeUtils!
            agent_tasks = [t for t in tasks if t.assigned_agent == agent]
            if agent_tasks:
                latest = agent_tasks[-1]
                runtime_str = TimeUtils.format_runtime(latest.runtime_seconds)
                info = f"({latest.status}"
                if runtime_str:
                    info += f", {runtime_str}"
                info += ")"

                ttk.Label(
                    step_frame,
                    text=info,
                    font=('Arial', 9),
                    foreground='gray'
                ).pack(side="left", padx=(5, 0))

        # Current status
        status_frame = ttk.Frame(workflow_frame)
        status_frame.pack(fill="x", pady=(10, 0))

        ttk.Label(
            status_frame,
            text="Status:",
            font=('Arial', 9, 'bold')
        ).pack(side="left")

        ttk.Label(
            status_frame,
            text=workflow_state['status_text'],
            font=('Arial', 9),
            foreground=workflow_state['status_color']
        ).pack(side="left", padx=(5, 0))

        # Show next agent if applicable
        if workflow_state['next_agent']:
            next_name = self.queue.get_agent_list().get(
                workflow_state['next_agent'],
                workflow_state['next_agent']
            )
            ttk.Label(
                status_frame,
                text=f"→ Next: {next_name}",
                font=('Arial', 9),
                foreground='blue'
            ).pack(side="left", padx=(20, 0))

    def analyze_workflow_state(self, tasks: List) -> Dict:
        """Analyze workflow state from tasks."""
        agent_states = {}

        standard_agents = [
            'requirements-analyst',
            'architect',
            'implementer',
            'tester',
            'documenter'
        ]

        for agent in standard_agents:
            agent_tasks = [t for t in tasks if t.assigned_agent == agent]

            if not agent_tasks:
                agent_states[agent] = 'not_started'
            else:
                latest = agent_tasks[-1]
                if latest.status == 'completed':
                    agent_states[agent] = 'completed'
                elif latest.status == 'active':
                    agent_states[agent] = 'active'
                elif latest.status == 'failed':
                    agent_states[agent] = 'failed'
                else:
                    agent_states[agent] = 'pending'

        # Calculate progress
        completed = sum(1 for s in agent_states.values() if s == 'completed')
        progress_pct = int((completed / len(standard_agents)) * 100)

        # Determine current status
        if any(s == 'failed' for s in agent_states.values()):
            status_text = "BLOCKED - Failed task"
            status_color = 'red'
            next_agent = None
        elif any(s == 'active' for s in agent_states.values()):
            active_agent = next((a for a, s in agent_states.items() if s == 'active'), None)
            status_text = f"IN PROGRESS - {self.queue.get_agent_list().get(active_agent, active_agent)}"
            status_color = 'orange'
            next_agent = None
        elif all(s == 'completed' for s in agent_states.values() if s != 'not_started'):
            status_text = "COMPLETE"
            status_color = 'green'
            next_agent = None
        else:
            next_agent = None
            for agent in standard_agents:
                if agent_states[agent] == 'not_started':
                    next_agent = agent
                    break

            if next_agent:
                status_text = "WAITING"
                status_color = 'blue'
            else:
                status_text = "READY"
                status_color = 'blue'

        return {
            'agents': agent_states,
            'progress_percent': progress_pct,
            'status_text': status_text,
            'status_color': status_color,
            'next_agent': next_agent
        }