"""
Workflow Template Editor Dialog - Create and edit workflow templates with validation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import json

from .base_dialog import BaseDialog
from ..utils import to_slug, validate_slug


class WorkflowTemplateEditorDialog(BaseDialog):
    """Dialog for creating/editing workflow templates."""

    def __init__(self, parent, queue_interface, mode='create', template_slug=None):
        self.queue = queue_interface
        self.mode = mode
        self.template_slug = template_slug
        self.steps = []

        title = "Create Workflow Template" if mode == 'create' else f"Edit Template: {template_slug}"
        super().__init__(parent, title, 850, 750)

        self.build_ui()

        if mode == 'edit' and template_slug:
            self.load_template_data()

        self.show()

    def build_ui(self):
        """Build the template editor UI."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Template name
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(name_frame, text="Template Name: *", font=('Arial', 10, 'bold')).pack(anchor="w")
        self.name_var = tk.StringVar()
        self.name_var.trace_add('write', self.on_name_changed)
        self.name_entry = ttk.Entry(name_frame, textvariable=self.name_var, width=50)
        self.name_entry.pack(fill="x", pady=(0, 5))

        # Slug (auto-generated)
        slug_header = ttk.Frame(name_frame)
        slug_header.pack(fill="x")

        ttk.Label(slug_header, text="Slug (auto-generated): *", font=('Arial', 10, 'bold')).pack(side="left")

        if self.mode == 'create':
            self.auto_slug_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                slug_header,
                text="Auto",
                variable=self.auto_slug_var,
                command=self.toggle_slug_auto
            ).pack(side="right")

        self.slug_var = tk.StringVar()
        self.slug_entry = ttk.Entry(name_frame, textvariable=self.slug_var, width=50)
        self.slug_entry.pack(fill="x")

        if self.mode == 'create':
            self.slug_entry.config(state='readonly')
        else:
            self.slug_entry.config(state='readonly')

        ttk.Label(
            name_frame,
            text="(lowercase, hyphens only: my-custom-workflow)",
            font=('Arial', 8),
            foreground='gray'
        ).pack(anchor="w", pady=(0, 10))

        # Description
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(desc_frame, text="Description: *", font=('Arial', 10, 'bold')).pack(anchor="w")
        self.description_var = tk.StringVar()
        ttk.Entry(desc_frame, textvariable=self.description_var, width=50).pack(fill="x")

        # Steps section
        steps_label_frame = ttk.Frame(main_frame)
        steps_label_frame.pack(fill="x", pady=(10, 5))

        ttk.Label(
            steps_label_frame,
            text="Workflow Steps:",
            font=('Arial', 10, 'bold')
        ).pack(side="left")

        ttk.Label(
            steps_label_frame,
            text="(Steps execute in order from top to bottom)",
            font=('Arial', 9),
            foreground='gray'
        ).pack(side="left", padx=(10, 0))

        # Steps list
        steps_frame = ttk.Frame(main_frame)
        steps_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Left: Steps list
        list_frame = ttk.Frame(steps_frame)
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        columns = ('step', 'agent', 'status')
        self.steps_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )

        self.steps_tree.heading('step', text='#')
        self.steps_tree.heading('agent', text='Agent')
        self.steps_tree.heading('status', text='Chain Status')

        self.steps_tree.column('step', width=40)
        self.steps_tree.column('agent', width=200)
        self.steps_tree.column('status', width=350)

        # Configure tags for status colors
        self.steps_tree.tag_configure('valid', background='#E8F5E9')  # Light green
        self.steps_tree.tag_configure('warning', background='#FFF9E6')  # Light yellow
        self.steps_tree.tag_configure('first', background='#E3F2FD')  # Light blue

        steps_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.steps_tree.yview)
        self.steps_tree.configure(yscrollcommand=steps_scroll.set)

        self.steps_tree.pack(side="left", fill="both", expand=True)
        steps_scroll.pack(side="right", fill="y")

        # Right: Step controls
        controls_frame = ttk.Frame(steps_frame)
        controls_frame.pack(side="right", fill="y", padx=(5, 0))

        ttk.Button(
            controls_frame,
            text="Add Step",
            command=self.add_step,
            width=15
        ).pack(pady=2)

        ttk.Button(
            controls_frame,
            text="Move Up",
            command=self.move_step_up,
            width=15
        ).pack(pady=2)

        ttk.Button(
            controls_frame,
            text="Move Down",
            command=self.move_step_down,
            width=15
        ).pack(pady=2)

        ttk.Button(
            controls_frame,
            text="Remove Step",
            command=self.remove_step,
            width=15
        ).pack(pady=2)

        ttk.Separator(controls_frame, orient="horizontal").pack(fill="x", pady=10)

        ttk.Button(
            controls_frame,
            text="View Step Details",
            command=self.view_step_details,
            width=15
        ).pack(pady=2)

        # Bottom buttons
        self.create_button_frame(main_frame, [
            ("Save Template", self.save_template),
            ("Cancel", self.cancel)
        ])

        ttk.Label(main_frame, text="* Required fields", font=('Arial', 9), foreground='gray').pack()

    def on_name_changed(self, *args):
        """Auto-generate slug from name if enabled."""
        if self.mode == 'create' and self.auto_slug_var.get():
            name = self.name_var.get().strip()
            slug = to_slug(name)
            self.slug_var.set(slug)

    def toggle_slug_auto(self):
        """Toggle auto-generation of slug."""
        if self.auto_slug_var.get():
            self.slug_entry.config(state='readonly')
            self.on_name_changed()
        else:
            self.slug_entry.config(state='normal')

    def load_template_data(self):
        """Load existing template data using model."""
        try:
            template = self.queue.get_workflow_template(self.template_slug)

            if not template:
                messagebox.showerror("Error", "Template not found")
                self.cancel()
                return

            # Load basic fields
            self.name_var.set(template.name)
            self.slug_var.set(template.slug)
            self.description_var.set(template.description)

            # Load steps
            self.steps = []
            for step in template.steps:
                self.steps.append({
                    'agent': step.agent,
                    'task': step.task,
                    'description': step.description
                })

            self.refresh_steps_list()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load template: {e}")
            self.cancel()

    def validate_chain(self, prev_agent, current_agent):
        """
        Validate that current agent can receive output from previous agent.

        Returns:
            (is_valid, message) tuple
        """
        if not prev_agent:
            return True, "First step in workflow"

        # Get contracts
        prev_contract = self.queue.get_agent_contract(prev_agent)
        curr_contract = self.queue.get_agent_contract(current_agent)

        if not prev_contract or not curr_contract:
            return False, "⚠ Cannot validate - contract not found"

        # Get previous agent's output directory and root document
        prev_outputs = prev_contract.get('outputs', {})
        prev_output_dir = prev_outputs.get('output_directory', '')
        prev_root_doc = prev_outputs.get('root_document', '')

        # Get current agent's expected input pattern
        curr_inputs = curr_contract.get('inputs', {}).get('required', [])
        if not curr_inputs:
            return True, "✓ No specific input requirements"

        expected_pattern = curr_inputs[0].get('pattern', '')

        # Check if previous agent's output matches current agent's expected input pattern
        # Pattern format: "enhancements/{enhancement_name}/prev_output_dir/prev_root_doc.md"
        if prev_output_dir and prev_root_doc:
            # Simple validation: check if the pattern is flexible enough
            if '{enhancement_name}' in expected_pattern and '*' not in expected_pattern:
                # Strict pattern - check if output directory matches
                if prev_output_dir not in expected_pattern:
                    return False, f"⚠ Warning: Expects input from different directory than '{prev_output_dir}'"

            # Get next agents from previous contract
            prev_success = prev_contract.get('statuses', {}).get('success', [])
            if prev_success:
                next_agents = prev_success[0].get('next_agents', [])
                if current_agent in next_agents:
                    return True, "✓ Valid auto-chain configured"
                elif next_agents:
                    agents_map = self.queue.get_agent_list()
                    expected_names = [agents_map.get(a, a) for a in next_agents]
                    return False, f"⚠ Warning: Previous step expects next: {', '.join(expected_names)}"

        return False, "⚠ Warning: Auto-chain may require manual configuration"

    def add_step(self):
        """Add a step to the workflow."""
        # Create dialog to select agent
        add_dialog = tk.Toplevel(self.dialog)
        add_dialog.title("Add Workflow Step")
        add_dialog.geometry("500x300")
        add_dialog.transient(self.dialog)
        add_dialog.grab_set()

        # Center on parent
        add_dialog.update_idletasks()
        x = self.dialog.winfo_x() + (self.dialog.winfo_width() // 2) - (add_dialog.winfo_width() // 2)
        y = self.dialog.winfo_y() + (self.dialog.winfo_height() // 2) - (add_dialog.winfo_height() // 2)
        add_dialog.geometry(f"+{x}+{y}")

        main_frame = ttk.Frame(add_dialog, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Select Agent:", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))

        # Agent listbox
        listbox_frame = ttk.Frame(main_frame)
        listbox_frame.pack(fill="both", expand=True, pady=(0, 10))

        agents_listbox = tk.Listbox(listbox_frame, font=('Arial', 10))
        agents_scroll = ttk.Scrollbar(listbox_frame, orient="vertical", command=agents_listbox.yview)
        agents_listbox.configure(yscrollcommand=agents_scroll.set)

        agents_listbox.pack(side="left", fill="both", expand=True)
        agents_scroll.pack(side="right", fill="y")

        # Populate agents
        agents_map = self.queue.get_agent_list()
        agent_keys = []
        for agent_key, agent_name in sorted(agents_map.items(), key=lambda x: x[1]):
            agents_listbox.insert(tk.END, agent_name)
            agent_keys.append(agent_key)

        # Buttons
        def add_selected():
            selection = agents_listbox.curselection()
            if selection:
                idx = selection[0]
                agent_key = agent_keys[idx]
                agent_name = agents_map[agent_key]

                self.steps.append({
                    'agent': agent_key,
                    'task': f"Execute {agent_name}",
                    'description': f"Process with {agent_name}"
                })

                self.refresh_steps_list()
                add_dialog.destroy()

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Add", command=add_selected, width=10).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=add_dialog.destroy, width=10).pack(side="left", padx=5)

        # Bind double-click
        agents_listbox.bind('<Double-Button-1>', lambda e: add_selected())

    def remove_step(self):
        """Remove selected step."""
        selection = self.steps_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a step to remove.")
            return

        item = selection[0]
        values = self.steps_tree.item(item, 'values')
        step_num = int(values[0]) - 1  # Convert to 0-indexed

        if messagebox.askyesno("Confirm", f"Remove step {values[0]} ({values[1]})?"):
            self.steps.pop(step_num)
            self.refresh_steps_list()

    def move_step_up(self):
        """Move selected step up in order."""
        selection = self.steps_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a step to move.")
            return

        item = selection[0]
        values = self.steps_tree.item(item, 'values')
        step_num = int(values[0]) - 1  # Convert to 0-indexed

        if step_num == 0:
            messagebox.showinfo("Info", "Step is already at the top.")
            return

        # Swap with previous
        self.steps[step_num], self.steps[step_num - 1] = self.steps[step_num - 1], self.steps[step_num]
        self.refresh_steps_list()

        # Re-select moved item
        new_item = self.steps_tree.get_children()[step_num - 1]
        self.steps_tree.selection_set(new_item)

    def move_step_down(self):
        """Move selected step down in order."""
        selection = self.steps_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a step to move.")
            return

        item = selection[0]
        values = self.steps_tree.item(item, 'values')
        step_num = int(values[0]) - 1  # Convert to 0-indexed

        if step_num >= len(self.steps) - 1:
            messagebox.showinfo("Info", "Step is already at the bottom.")
            return

        # Swap with next
        self.steps[step_num], self.steps[step_num + 1] = self.steps[step_num + 1], self.steps[step_num]
        self.refresh_steps_list()

        # Re-select moved item
        new_item = self.steps_tree.get_children()[step_num + 1]
        self.steps_tree.selection_set(new_item)

    def view_step_details(self):
        """View details of selected step in a nicely formatted dialog."""
        selection = self.steps_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a step to view.")
            return

        item = selection[0]
        values = self.steps_tree.item(item, 'values')
        step_num = int(values[0])
        agent_key = self.steps[step_num - 1]['agent']

        try:
            # Get agent contract details
            contract = self.queue.get_agent_contract(agent_key)
            if not contract:
                messagebox.showerror("Error", "Agent contract not found")
                return

            agents_map = self.queue.get_agent_list()
            agent_name = agents_map.get(agent_key, agent_key)

            # Create view window
            view_window = tk.Toplevel(self.dialog)
            view_window.title(f"Step {step_num}: {agent_name}")
            view_window.geometry("650x550")
            view_window.transient(self.dialog)
            view_window.grab_set()

            main_frame = ttk.Frame(view_window, padding=20)
            main_frame.pack(fill="both", expand=True)

            # Header
            ttk.Label(
                main_frame,
                text=agent_name,
                font=('Arial', 14, 'bold')
            ).pack(anchor="w", pady=(0, 5))

            ttk.Label(
                main_frame,
                text=f"Agent Key: {agent_key}",
                font=('Arial', 9),
                foreground='gray'
            ).pack(anchor="w", pady=(0, 20))

            # Role Section
            role_frame = ttk.LabelFrame(main_frame, text="Role", padding=10)
            role_frame.pack(fill="x", pady=(0, 10))

            ttk.Label(
                role_frame,
                text=contract.get('role', 'N/A'),
                font=('Arial', 10, 'bold')
            ).pack(anchor="w")

            ttk.Label(
                role_frame,
                text=contract.get('description', ''),
                wraplength=580
            ).pack(anchor="w", pady=(5, 0))

            # Outputs Section
            outputs_frame = ttk.LabelFrame(main_frame, text="Outputs", padding=10)
            outputs_frame.pack(fill="x", pady=(0, 10))

            outputs = contract.get('outputs', {})

            output_info = [
                ("Output Directory:", outputs.get('output_directory', 'N/A')),
                ("Root Document:", outputs.get('root_document', 'N/A'))
            ]

            for label, value in output_info:
                row = ttk.Frame(outputs_frame)
                row.pack(fill="x", pady=2)

                ttk.Label(
                    row,
                    text=label,
                    font=('Arial', 9, 'bold'),
                    width=18
                ).pack(side="left")

                ttk.Label(
                    row,
                    text=value,
                    font=('Arial', 9)
                ).pack(side="left")

            # Success Statuses Section
            status_frame = ttk.LabelFrame(main_frame, text="Success Statuses", padding=10)
            status_frame.pack(fill="x", pady=(0, 10))

            for status in contract.get('statuses', {}).get('success', []):
                status_row = ttk.Frame(status_frame)
                status_row.pack(fill="x", pady=2)

                ttk.Label(
                    status_row,
                    text="●",
                    foreground='green',
                    font=('Arial', 10)
                ).pack(side="left", padx=(0, 5))

                ttk.Label(
                    status_row,
                    text=status.get('code', 'N/A'),
                    font=('Arial', 9, 'bold')
                ).pack(side="left", padx=(0, 10))

                next_agents = status.get('next_agents', [])
                if next_agents:
                    next_names = [agents_map.get(a, a) for a in next_agents]
                    ttk.Label(
                        status_row,
                        text=f"→ Next: {', '.join(next_names)}",
                        font=('Arial', 9),
                        foreground='blue'
                    ).pack(side="left")

            # Inputs Section
            inputs_frame = ttk.LabelFrame(main_frame, text="Expected Inputs", padding=10)
            inputs_frame.pack(fill="x", pady=(0, 10))

            required_inputs = contract.get('inputs', {}).get('required', [])
            if required_inputs:
                for inp in required_inputs:
                    ttk.Label(
                        inputs_frame,
                        text=f"Pattern: {inp.get('pattern', 'N/A')}",
                        font=('Arial', 9)
                    ).pack(anchor="w", pady=2)

                    ttk.Label(
                        inputs_frame,
                        text=inp.get('description', ''),
                        font=('Arial', 8),
                        foreground='gray',
                        wraplength=580
                    ).pack(anchor="w", pady=(0, 5))
            else:
                ttk.Label(
                    inputs_frame,
                    text="No specific input requirements",
                    font=('Arial', 9),
                    foreground='gray'
                ).pack(anchor="w")

            ttk.Button(main_frame, text="Close", command=view_window.destroy).pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load agent details: {e}")

    def refresh_steps_list(self):
        """Refresh the steps list display with chain validation."""
        for item in self.steps_tree.get_children():
            self.steps_tree.delete(item)

        agents_map = self.queue.get_agent_list()

        for idx, step in enumerate(self.steps):
            agent_key = step['agent']
            agent_name = agents_map.get(agent_key, agent_key)

            # Validate chain
            prev_agent = self.steps[idx - 1]['agent'] if idx > 0 else None
            is_valid, status_msg = self.validate_chain(prev_agent, agent_key)

            # Determine tag
            if idx == 0:
                tag = 'first'
            elif is_valid:
                tag = 'valid'
            else:
                tag = 'warning'

            self.steps_tree.insert(
                '',
                tk.END,
                values=(
                    str(idx + 1),
                    agent_name,
                    status_msg
                ),
                tags=(tag,)
            )

    def validate(self) -> bool:
        """Validate template before saving."""
        name = self.name_var.get().strip()
        slug = self.slug_var.get().strip()
        description = self.description_var.get().strip()

        if not name:
            messagebox.showwarning("Validation", "Template name is required.")
            return False

        if not slug:
            messagebox.showwarning("Validation", "Slug is required.")
            return False

        if not validate_slug(slug):
            messagebox.showwarning("Validation", "Slug must be lowercase with hyphens only (e.g., my-workflow).")
            return False

        if not description:
            messagebox.showwarning("Validation", "Description is required.")
            return False

        if not self.steps:
            messagebox.showwarning("Validation", "At least one step is required.")
            return False

        # Check for chain warnings
        has_warnings = False
        for idx, step in enumerate(self.steps):
            if idx > 0:
                prev_agent = self.steps[idx - 1]['agent']
                is_valid, _ = self.validate_chain(prev_agent, step['agent'])
                if not is_valid:
                    has_warnings = True
                    break

        if has_warnings:
            if not messagebox.askyesno(
                    "Chain Warnings",
                    "Some steps have chain warnings indicating they may not auto-chain correctly.\n\n"
                    "You can still save this template, but you may need to manually configure task chaining.\n\n"
                    "Continue with save?"
            ):
                return False

        return True

    def save_template(self):
        """Save the template."""
        if not self.validate():
            return

        name = self.name_var.get().strip()
        slug = self.slug_var.get().strip()
        description = self.description_var.get().strip()

        try:
            if self.mode == 'create':
                # Create new template
                subprocess.run(
                    [str(self.queue.script_path), "workflow", "create", slug, description],
                    cwd=str(self.queue.project_root),
                    capture_output=True,
                    text=True,
                    check=True
                )

            # Update name in JSON (workflow commands don't handle 'name' field)
            if self.templates_file.exists():
                with open(self.templates_file, 'r') as f:
                    data = json.load(f)

                if 'templates' not in data:
                    data['templates'] = {}

                if slug not in data['templates']:
                    data['templates'][slug] = {}

                data['templates'][slug]['name'] = name

                with open(self.templates_file, 'w') as f:
                    json.dump(data, f, indent=2)

            # Add all steps
            for step in self.steps:
                subprocess.run(
                    [str(self.queue.script_path), "workflow", "add-step", slug, step['agent']],
                    cwd=str(self.queue.project_root),
                    capture_output=True,
                    text=True,
                    check=True
                )

            self.close(result=slug)

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to save template: {e.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save template: {e}")