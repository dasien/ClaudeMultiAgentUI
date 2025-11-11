"""
Agent Manager dialog for viewing and managing agents.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import json

from .base_dialog import BaseDialog


class AgentListDialog(BaseDialog):
    """Dialog for managing agents (create, edit, delete)."""

    def __init__(self, parent, queue_interface, settings=None):
        super().__init__(parent, "Agent Manager", 900, 600)
        self.queue = queue_interface
        self.settings = settings
        self.agents_file = self.queue.agents_file
        self.agents_dir = self.queue.agents_file.parent

        self.build_ui()
        self.load_agents()
        # Don't call show() - this dialog doesn't return a result

    def build_ui(self):
        """Build the agent manager UI."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Manage Agents", font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Agent list
        list_frame = ttk.LabelFrame(main_frame, text="Agents", padding=10)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Treeview - Enhanced with skills column
        columns = ('name', 'file', 'skills_count', 'description')
        self.agent_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )

        self.agent_tree.heading('name', text='Name')
        self.agent_tree.heading('file', text='File')
        self.agent_tree.heading('skills_count', text='Skills')
        self.agent_tree.heading('description', text='Description')

        self.agent_tree.column('name', width=180)
        self.agent_tree.column('file', width=150)
        self.agent_tree.column('skills_count', width=60)
        self.agent_tree.column('description', width=400)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.agent_tree.yview)
        self.agent_tree.configure(yscrollcommand=scrollbar.set)

        self.agent_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind double-click
        self.agent_tree.bind('<Double-Button-1>', lambda e: self.edit_agent())

        # Buttons - Using BaseDialog helper
        self.create_button_frame(main_frame, [
            ("Create New Agent", self.create_agent),
            ("Edit Selected", self.edit_agent),
            ("Delete Selected", self.delete_agent),
            ("Refresh", self.load_agents),
            ("Close", self.dialog.destroy)
        ])

    def load_agents(self):
        """Load agents from agents.json."""
        for item in self.agent_tree.get_children():
            self.agent_tree.delete(item)

        try:
            with open(self.agents_file, 'r') as f:
                data = json.load(f)

            # Handle both formats
            agents = data.get('agents', []) if isinstance(data, dict) else data

            for agent in agents:
                if not isinstance(agent, dict):
                    continue

                name = agent.get('name', '')
                agent_file = agent.get('agent-file', '')
                description = agent.get('description', '')

                # Show skills count
                skills = agent.get('skills', [])
                skills_count = len(skills) if skills else 0

                self.agent_tree.insert(
                    '',
                    tk.END,
                    values=(name, agent_file, skills_count, description)
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load agents: {e}")

    def create_agent(self):
        """Open dialog to create a new agent."""
        from .agent_details import AgentDetailsDialog
        dialog = AgentDetailsDialog(
            self.dialog,
            self.queue,
            self.settings,
            mode='create'
        )
        if dialog.result:
            self.load_agents()

    def edit_agent(self):
        """Open dialog to edit the selected agent."""
        selection = self.agent_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an agent to edit.")
            return

        item = selection[0]
        values = self.agent_tree.item(item, 'values')
        agent_file = values[1]

        from .agent_details import AgentDetailsDialog
        dialog = AgentDetailsDialog(
            self.dialog,
            self.queue,
            self.settings,
            mode='edit',
            agent_file=agent_file
        )
        if dialog.result:
            self.load_agents()

    def delete_agent(self):
        """Delete the selected agent."""
        selection = self.agent_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an agent to delete.")
            return

        item = selection[0]
        values = self.agent_tree.item(item, 'values')
        agent_name = values[0]
        agent_file = values[1]

        if not messagebox.askyesno(
                "Confirm Delete",
                f"Delete agent '{agent_name}'?\n\n"
                f"This will:\n"
                f"- Remove from agents.json\n"
                f"- Remove from AGENT_CONTRACTS.json\n"
                f"- Delete markdown file\n\n"
                f"Cannot be undone."
        ):
            return

        try:
            # Remove from agents.json
            with open(self.agents_file, 'r') as f:
                data = json.load(f)

            agents = data.get('agents', []) if isinstance(data, dict) else data
            agents = [a for a in agents if a.get('agent-file') != agent_file]

            if isinstance(data, dict):
                data['agents'] = agents
                with open(self.agents_file, 'w') as f:
                    json.dump(data, f, indent=2)
            else:
                with open(self.agents_file, 'w') as f:
                    json.dump(agents, f, indent=2)

            # Remove from contracts
            contracts_file = self.queue.project_root / ".claude/AGENT_CONTRACTS.json"
            if contracts_file.exists():
                with open(contracts_file, 'r') as f:
                    contracts = json.load(f)

                if "agents" in contracts and agent_file in contracts["agents"]:
                    del contracts["agents"][agent_file]

                    with open(contracts_file, 'w') as f:
                        json.dump(contracts, f, indent=2)

            # Delete markdown file
            md_file = self.agents_dir / f"{agent_file}.md"
            if md_file.exists():
                md_file.unlink()

            self.load_agents()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}")