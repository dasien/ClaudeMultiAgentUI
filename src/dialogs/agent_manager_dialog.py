"""
Agent Manager dialog for viewing and managing agents.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import json


class AgentManagerDialog:
    """Dialog for managing agents (create, edit, delete)."""

    def __init__(self, parent, queue_interface, settings=None):
        self.queue = queue_interface
        self.settings = settings
        self.agents_file = self.queue.agents_file
        self.agents_dir = self.queue.agents_file.parent

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Agent Manager")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.build_ui()
        self.load_agents()

    def build_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="Manage Agents", font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Agent list frame
        list_frame = ttk.LabelFrame(main_frame, text="Agents", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Treeview for agents
        columns = ('name', 'file', 'description')
        self.agent_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )

        self.agent_tree.heading('name', text='Name')
        self.agent_tree.heading('file', text='File')
        self.agent_tree.heading('description', text='Description')

        self.agent_tree.column('name', width=150)
        self.agent_tree.column('file', width=150)
        self.agent_tree.column('description', width=400)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.agent_tree.yview)
        self.agent_tree.configure(yscrollcommand=scrollbar.set)

        self.agent_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Create New Agent", command=self.create_agent).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit Selected", command=self.edit_agent).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_agent).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.load_agents).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def load_agents(self):
        """Load agents from agents.json."""
        # Clear current items
        for item in self.agent_tree.get_children():
            self.agent_tree.delete(item)

        try:
            with open(self.agents_file, 'r') as f:
                data = json.load(f)

            agents = data.get('agents', [])
            for agent in agents:
                name = agent.get('name', '')
                agent_file = agent.get('agent-file', '')
                description = agent.get('description', '')

                self.agent_tree.insert('', tk.END, values=(name, agent_file, description))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load agents: {e}")

    def create_agent(self):
        """Open dialog to create a new agent."""
        from .create_edit_agent_dialog import CreateEditAgentDialog
        dialog = CreateEditAgentDialog(self.dialog, self.queue, self.settings, mode='create')
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

        from .create_edit_agent_dialog import CreateEditAgentDialog
        dialog = CreateEditAgentDialog(self.dialog, self.queue, self.settings, mode='edit', agent_file=agent_file)
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

        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Delete agent '{agent_name}'?\n\nThis will:\n- Remove the agent from agents.json\n- Delete the agent markdown file\n\nThis action cannot be undone."):
            return

        try:
            # Remove from agents.json
            with open(self.agents_file, 'r') as f:
                data = json.load(f)

            agents = data.get('agents', [])
            agents = [a for a in agents if a.get('agent-file') != agent_file]
            data['agents'] = agents

            with open(self.agents_file, 'w') as f:
                json.dump(data, f, indent=2)

            # Delete markdown file
            md_file = self.agents_dir / f"{agent_file}.md"
            if md_file.exists():
                md_file.unlink()

            messagebox.showinfo("Success", f"Agent '{agent_name}' deleted successfully.")
            self.load_agents()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete agent: {e}")