"""
Enhanced Agent Manager with skills editing support.
v3.0 - Includes visual skills assignment and prompt preview.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import json
import re
import urllib.request
import threading
from .claude_working_dialog import ClaudeWorkingDialog


class EnhancedCreateEditAgentDialog:
    """Enhanced dialog for creating/editing agents with skills support."""

    def __init__(self, parent, queue_interface, settings=None, mode='create', agent_file=None):
        self.queue = queue_interface
        self.settings = settings
        self.mode = mode
        self.agent_file = agent_file
        self.result = None

        self.agents_dir = self.queue.agents_file.parent
        self.agents_json_file = self.queue.agents_file
        self.contracts_file = self.queue.contracts_file

        # Load data
        self.tools_data = self.queue.get_tools_data()
        self.skills_data = self.queue.get_skills_list()
        self.agents_map = self.queue.get_agent_list()

        # UI state
        self.tool_checkboxes = {}
        self.skill_checkboxes = {}

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Agent" if mode == 'create' else "Edit Agent")
        self.dialog.geometry("900x800")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.build_ui()

        if mode == 'edit' and agent_file:
            self.load_agent_data()

        self.dialog.wait_window()

    def build_ui(self):
        """Build the UI with tabbed interface."""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 10))

        # Tabs
        basic_tab = ttk.Frame(notebook, padding=20)
        workflow_tab = ttk.Frame(notebook, padding=20)
        tools_tab = ttk.Frame(notebook, padding=20)
        skills_tab = ttk.Frame(notebook, padding=20)

        notebook.add(basic_tab, text="Basic Info")
        notebook.add(workflow_tab, text="Workflow")
        notebook.add(tools_tab, text="Tools")
        notebook.add(skills_tab, text="Skills")

        self.build_basic_tab(basic_tab)
        self.build_workflow_tab(workflow_tab)
        self.build_tools_tab(tools_tab)
        self.build_skills_tab(skills_tab)

        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Save Agent", command=self.save_agent, width=15).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel, width=15).pack(side="left", padx=5)

        ttk.Label(main_frame, text="* Required fields", font=('Arial', 9), foreground='gray').pack()

    def build_basic_tab(self, parent):
        """Build basic information tab."""
        # Store reference to file entry for later access
        self.file_entry = None

        # Name and File on same line
        name_file_frame = ttk.Frame(parent)
        name_file_frame.pack(fill="x", pady=(0, 15))

        # Name column
        name_col = ttk.Frame(name_file_frame)
        name_col.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Label(name_col, text="Agent Name: *", font=('Arial', 10, 'bold')).pack(anchor="w")
        self.name_var = tk.StringVar()
        self.name_var.trace_add('write', self.on_name_changed)
        ttk.Entry(name_col, textvariable=self.name_var, width=30).pack(fill="x")

        # File column
        file_col = ttk.Frame(name_file_frame)
        file_col.pack(side="left", fill="x", expand=True, padx=(5, 0))

        file_header = ttk.Frame(file_col)
        file_header.pack(fill="x")

        ttk.Label(file_header, text="File Name (slug): *", font=('Arial', 10, 'bold')).pack(side="left")

        if self.mode == 'create':
            self.auto_filename_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                file_header,
                text="Auto",
                variable=self.auto_filename_var,
                command=self.toggle_filename_auto
            ).pack(side="right")

        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_col, textvariable=self.file_var, width=30)
        self.file_entry.pack(fill="x")
        if self.mode == 'edit':
            self.file_entry.config(state='readonly')
        elif self.mode == 'create':
            self.file_entry.config(state='readonly')  # Start as readonly when auto is on

        ttk.Label(parent, text="(lowercase, hyphens only)", font=('Arial', 8), foreground='gray').pack(anchor="w",
                                                                                                       pady=(0, 15))

        # Description - single line
        ttk.Label(parent, text="Description: *", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))
        self.description_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.description_var, width=70).pack(fill="x", pady=(0, 15))

        # Agent Details
        details_header = ttk.Frame(parent)
        details_header.pack(fill="x", pady=(0, 5))

        ttk.Label(details_header, text="Role Definition: *", font=('Arial', 10, 'bold')).pack(side="left")

        api_key = self.settings.get_claude_api_key() if self.settings else None
        if api_key:
            ttk.Button(details_header, text="Generate with Claude", command=self.generate_details).pack(side="right")

        details_frame = ttk.Frame(parent)
        details_frame.pack(fill="both", expand=True)

        self.details_text = tk.Text(details_frame, wrap="word", font=('Courier', 9))
        details_scroll = ttk.Scrollbar(details_frame, orient="vertical", command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scroll.set)

        self.details_text.pack(side="left", fill="both", expand=True)
        details_scroll.pack(side="right", fill="y")

    def build_workflow_tab(self, parent):
        """Build workflow contract tab."""
        # Role
        ttk.Label(parent, text="Workflow Role: *", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))
        self.role_var = tk.StringVar()
        role_combo = ttk.Combobox(parent, textvariable=self.role_var, state='readonly', width=40)
        role_combo['values'] = ['analysis', 'technical_design', 'implementation', 'testing', 'documentation',
                                'integration']
        role_combo.pack(fill="x", pady=(0, 15))
        role_combo.bind('<<ComboboxSelected>>', self.on_role_selected)

        # Output Directory
        ttk.Label(parent, text="Output Directory: *", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))
        self.output_dir_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.output_dir_var, width=50).pack(fill="x", pady=(0, 15))

        # Root Document
        ttk.Label(parent, text="Root Document: *", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))
        self.root_doc_var = tk.StringVar(value="summary.md")
        ttk.Entry(parent, textvariable=self.root_doc_var, width=50).pack(fill="x", pady=(0, 15))

        # Success Status
        ttk.Label(parent, text="Success Status Code: *", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))
        self.success_status_var = tk.StringVar()
        status_combo = ttk.Combobox(parent, textvariable=self.success_status_var, state='readonly', width=40)
        status_combo['values'] = [
            'READY_FOR_DEVELOPMENT',
            'READY_FOR_IMPLEMENTATION',
            'READY_FOR_TESTING',
            'TESTING_COMPLETE',
            'DOCUMENTATION_COMPLETE',
            'INTEGRATION_COMPLETE'
        ]
        status_combo.pack(fill="x", pady=(0, 15))

        # Next Agent
        ttk.Label(parent, text="Next Agent: *", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))
        self.next_agent_var = tk.StringVar()
        self.next_agent_combo = ttk.Combobox(parent, textvariable=self.next_agent_var, state='readonly', width=40)
        next_values = ['(none - workflow ends)'] + list(self.agents_map.values())
        self.next_agent_combo['values'] = next_values
        self.next_agent_combo.pack(fill="x", pady=(0, 15))

        # Metadata Required
        self.metadata_required_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Require metadata header in outputs", variable=self.metadata_required_var).pack(
            anchor="w")

    def build_tools_tab(self, parent):
        """Build tools selection tab."""
        ttk.Label(parent, text="Available Tools: *", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))

        # Agent persona quick selection
        if self.tools_data and 'agent_personas' in self.tools_data:
            persona_frame = ttk.LabelFrame(parent, text="Quick Select from Persona", padding=10)
            persona_frame.pack(fill="x", pady=(0, 15))

            self.persona_var = tk.StringVar(value="")
            persona_combo = ttk.Combobox(persona_frame, textvariable=self.persona_var, state='readonly', width=30)

            personas = self.tools_data['agent_personas']
            persona_names = ["(none)"] + [personas[p]['display_name'] for p in personas.keys()]
            persona_combo['values'] = persona_names
            persona_combo.pack(fill="x")
            persona_combo.bind('<<ComboboxSelected>>', self.on_persona_selected)

        # Tools grid
        tools_frame = ttk.Frame(parent)
        tools_frame.pack(fill="both", expand=True)

        if self.tools_data and 'claude_code_tools' in self.tools_data:
            tools_list = self.tools_data['claude_code_tools']

            for idx, tool in enumerate(tools_list):
                row = idx // 3
                col = idx % 3

                var = tk.BooleanVar(value=False)
                self.tool_checkboxes[tool['name']] = var

                cb = ttk.Checkbutton(
                    tools_frame,
                    text=tool.get('display_name', tool['name']),
                    variable=var
                )
                cb.grid(row=row, column=col, sticky=tk.W, padx=15, pady=3)

    def build_skills_tab(self, parent):
        """Build skills selection tab."""
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(
            header_frame,
            text="Assign Skills to Agent",
            font=('Arial', 11, 'bold')
        ).pack(side="left")

        ttk.Button(
            header_frame,
            text="Preview Skills Prompt",
            command=self.preview_agent_skills
        ).pack(side="right")

        # Category filter
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(filter_frame, text="Filter by category:").pack(side="left", padx=(0, 5))
        self.skills_category_var = tk.StringVar(value="All")
        self.skills_category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.skills_category_var,
            state='readonly',
            width=20
        )
        self.skills_category_combo.pack(side="left")
        self.skills_category_combo.bind('<<ComboboxSelected>>', self.filter_skills_list)

        # Populate categories
        if self.skills_data:
            categories = set(['All'])
            for skill in self.skills_data.get('skills', []):
                cat = skill.get('category', 'uncategorized')
                categories.add(cat.replace('-', ' ').title())
            self.skills_category_combo['values'] = sorted(list(categories))

        # Skills checkboxes frame
        self.skills_checkboxes_frame = ttk.Frame(parent)
        self.skills_checkboxes_frame.pack(fill="both", expand=True)

        self.populate_skills_checkboxes()

        # Summary
        self.skills_summary_label = ttk.Label(
            parent,
            text="0 skills selected",
            font=('Arial', 9),
            foreground='gray'
        )
        self.skills_summary_label.pack(anchor="w", pady=(10, 0))

    def populate_skills_checkboxes(self):
        """Populate skills checkboxes with filtering."""
        # Clear existing
        for widget in self.skills_checkboxes_frame.winfo_children():
            widget.destroy()

        if not self.skills_data:
            ttk.Label(
                self.skills_checkboxes_frame,
                text="Skills system not available",
                foreground='red'
            ).pack(anchor="w")
            return

        category_filter = self.skills_category_var.get()
        skills_list = self.skills_data.get('skills', [])

        # Create scrollable frame (resized to fit content better)
        canvas = tk.Canvas(self.skills_checkboxes_frame, height=400, width=600)
        scrollbar = ttk.Scrollbar(self.skills_checkboxes_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add checkboxes
        row = 0
        for skill in skills_list:
            category = skill.get('category', 'uncategorized')

            # Apply filter
            if category_filter != 'All':
                if category.replace('-', ' ').title() != category_filter:
                    continue

            skill_dir = skill.get('skill-directory', '')
            name = skill.get('name', skill_dir)
            description = skill.get('description', '')
            cat_display = category.replace('-', ' ').title()

            # Create checkbox
            if skill_dir not in self.skill_checkboxes:
                var = tk.BooleanVar(value=False)
                self.skill_checkboxes[skill_dir] = var
                var.trace_add('write', lambda *args: self.update_skills_summary())
            else:
                var = self.skill_checkboxes[skill_dir]

            cb_frame = ttk.Frame(scrollable_frame)
            cb_frame.grid(row=row, column=0, sticky=tk.W, pady=3, padx=5)

            cb = ttk.Checkbutton(cb_frame, text=f"{name} ({cat_display})", variable=var)
            cb.pack(anchor="w")

            # Description tooltip (as label)
            if description:
                ttk.Label(
                    cb_frame,
                    text=description,
                    font=('Arial', 8),
                    foreground='gray',
                    wraplength=700
                ).pack(anchor="w", padx=(20, 0))

            row += 1

    def filter_skills_list(self, event=None):
        """Re-populate skills checkboxes with filter applied."""
        self.populate_skills_checkboxes()

    def update_skills_summary(self):
        """Update skills selection summary."""
        selected = sum(1 for var in self.skill_checkboxes.values() if var.get())
        self.skills_summary_label.config(text=f"{selected} skill(s) selected")

    def preview_agent_skills(self):
        """Preview what the skills prompt will look like for this agent."""
        # Get currently selected skills
        selected_skills = [skill_dir for skill_dir, var in self.skill_checkboxes.items() if var.get()]

        if not selected_skills:
            messagebox.showinfo("No Skills", "No skills selected. Select skills first to preview.")
            return

        # Build preview manually by loading each skill
        try:
            preview_content = []
            preview_content.append("=" * 80)
            preview_content.append("## SPECIALIZED SKILLS AVAILABLE")
            preview_content.append("=" * 80)
            preview_content.append("")
            preview_content.append("You have access to the following specialized skills:")
            preview_content.append("")

            for skill_dir in selected_skills:
                skill_content = self.queue.load_skill_content(skill_dir)
                if skill_content:
                    preview_content.append("---")
                    preview_content.append("")
                    preview_content.append(skill_content)
                    preview_content.append("")

            preview_content.append("---")
            preview_content.append("")
            preview_content.append("**Using Skills**: Apply the above skills as appropriate.")

            # Show preview window
            preview = tk.Toplevel(self.dialog)
            preview.title("Skills Prompt Preview")
            preview.geometry("800x600")
            preview.transient(self.dialog)

            text_frame = ttk.Frame(preview, padding=10)
            text_frame.pack(fill="both", expand=True)

            text_widget = tk.Text(text_frame, wrap="word", font=('Courier', 9))
            scroll = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scroll.set)

            text_widget.pack(side="left", fill="both", expand=True)
            scroll.pack(side="right", fill="y")

            text_widget.insert('1.0', '\n'.join(preview_content))
            text_widget.config(state=tk.DISABLED)

            ttk.Button(preview, text="Close", command=preview.destroy).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to build preview: {e}")

    def build_tools_tab(self, parent):
        """Build tools selection tab."""
        ttk.Label(parent, text="Available Tools: *", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))

        # Agent persona quick selection
        if self.tools_data and 'agent_personas' in self.tools_data:
            persona_frame = ttk.LabelFrame(parent, text="Quick Select from Persona", padding=10)
            persona_frame.pack(fill="x", pady=(0, 15))

            self.persona_var = tk.StringVar(value="")
            persona_combo = ttk.Combobox(persona_frame, textvariable=self.persona_var, state='readonly', width=30)

            personas = self.tools_data['agent_personas']
            persona_names = ["(none)"] + [personas[p]['display_name'] for p in personas.keys()]
            persona_combo['values'] = persona_names
            persona_combo.pack(fill="x")
            persona_combo.bind('<<ComboboxSelected>>', self.on_persona_selected)

        # Tools grid
        tools_frame = ttk.Frame(parent)
        tools_frame.pack(fill="both", expand=True)

        if self.tools_data and 'claude_code_tools' in self.tools_data:
            tools_list = self.tools_data['claude_code_tools']

            for idx, tool in enumerate(tools_list):
                row = idx // 3
                col = idx % 3

                var = tk.BooleanVar(value=False)
                self.tool_checkboxes[tool['name']] = var

                cb = ttk.Checkbutton(
                    tools_frame,
                    text=tool.get('display_name', tool['name']),
                    variable=var
                )
                cb.grid(row=row, column=col, sticky=tk.W, padx=15, pady=3)

    def on_role_selected(self, event=None):
        """Auto-populate fields based on role."""
        role = self.role_var.get()

        defaults = {
            'analysis': {
                'output_dir': 'requirements-analyst',
                'root_doc': 'analysis_summary.md',
                'status': 'READY_FOR_DEVELOPMENT',
                'next': 'Architect'
            },
            'technical_design': {
                'output_dir': 'architect',
                'root_doc': 'implementation_plan.md',
                'status': 'READY_FOR_IMPLEMENTATION',
                'next': 'Implementer'
            },
            'implementation': {
                'output_dir': 'implementer',
                'root_doc': 'test_plan.md',
                'status': 'READY_FOR_TESTING',
                'next': 'Tester'
            },
            'testing': {
                'output_dir': 'tester',
                'root_doc': 'test_summary.md',
                'status': 'TESTING_COMPLETE',
                'next': 'Documenter'
            },
            'documentation': {
                'output_dir': 'documenter',
                'root_doc': 'documentation_summary.md',
                'status': 'DOCUMENTATION_COMPLETE',
                'next': '(none - workflow ends)'
            },
            'integration': {
                'output_dir': 'integration-coordinator',
                'root_doc': 'integration_summary.md',
                'status': 'INTEGRATION_COMPLETE',
                'next': '(none - workflow ends)'
            }
        }

        if role in defaults:
            d = defaults[role]
            self.output_dir_var.set(d['output_dir'])
            self.root_doc_var.set(d['root_doc'])
            self.success_status_var.set(d['status'])
            self.next_agent_var.set(d['next'])

    def on_persona_selected(self, event=None):
        """Apply persona tool selection."""
        if not self.tools_data or 'agent_personas' not in self.tools_data:
            return

        selected = self.persona_var.get()
        if not selected or selected == "(none)":
            for var in self.tool_checkboxes.values():
                var.set(False)
            return

        # Find persona
        personas = self.tools_data['agent_personas']
        persona_key = None
        for key, persona in personas.items():
            if persona['display_name'] == selected:
                persona_key = key
                break

        if not persona_key:
            return

        # Apply tools
        persona_tools = personas[persona_key].get('tools', [])
        for tool_name in self.tool_checkboxes.keys():
            self.tool_checkboxes[tool_name].set(tool_name in persona_tools)

    def on_name_changed(self, *args):
        """Auto-generate filename from name if enabled."""
        if self.mode == 'create' and self.auto_filename_var.get():
            name = self.name_var.get().strip()
            slug = self.name_to_slug(name)
            self.file_var.set(slug)

    def name_to_slug(self, name: str) -> str:
        """Convert name to slug format."""
        # Convert to lowercase
        slug = name.lower()
        # Replace spaces and underscores with hyphens
        slug = re.sub(r'[\s_]+', '-', slug)
        # Remove non-alphanumeric characters except hyphens
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        # Strip leading/trailing hyphens
        slug = slug.strip('-')
        return slug

    def toggle_filename_auto(self):
        """Toggle auto-generation of filename."""
        if self.auto_filename_var.get():
            self.file_entry.config(state='readonly')
            self.on_name_changed()
        else:
            self.file_entry.config(state='normal')

    def generate_details(self):
        """Generate agent details with AI."""
        name = self.name_var.get().strip()
        description = self.description_var.get().strip()

        if not name or not description:
            messagebox.showwarning("Missing Info", "Enter name and description first.")
            return

        context = f"""Agent: {name}
Description: {description}

Generate comprehensive agent role definition with:
- Role and Purpose
- Core Responsibilities
- Workflow steps
- Output Standards
- Success Criteria
- Scope Boundaries (DO/DON'T)"""

        # Show working dialog
        self.working_dialog = ClaudeWorkingDialog(
            self.dialog,
            "Generating agent role definition",
            "30-60 seconds"
        )
        self.working_dialog.show()

        # Run API call in separate thread
        def api_thread():
            try:
                details = self.call_claude_api(context)
                # Schedule UI update on main thread
                self.dialog.after(0, lambda: self.on_generation_complete(details))
            except Exception as error:
                # Schedule error handling on main thread
                self.dialog.after(0, lambda err=error: self.on_generation_error(err))

        thread = threading.Thread(target=api_thread, daemon=True)
        thread.start()

    def on_generation_complete(self, content):
        """Handle successful generation (runs on UI thread)."""
        self.working_dialog.close()
        self.details_text.delete('1.0', tk.END)
        self.details_text.insert('1.0', content)

    def on_generation_error(self, error):
        """Handle generation error (runs on UI thread)."""
        self.working_dialog.close()
        messagebox.showerror("Error", f"AI generation failed: {error}")

    def call_claude_api(self, context: str) -> str:
        """Call Claude API."""
        # Get Claude configuration from settings
        config = self.settings.get_claude_config() if self.settings else None
        if not config or not config.get('api_key'):
            raise Exception("No API key configured")

        api_key = config['api_key']
        model = config['model']
        max_tokens = config['max_tokens']

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        data = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": context}]
        }

        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=90) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['content'][0]['text']

    def load_agent_data(self):
        """Load existing agent for editing."""
        try:
            # Load agents.json
            with open(self.agents_json_file, 'r') as f:
                data = json.load(f)

            agents = data.get('agents', []) if isinstance(data, dict) else data
            agent_data = next((a for a in agents if a.get('agent-file') == self.agent_file), None)

            if not agent_data:
                messagebox.showerror("Error", f"Agent '{self.agent_file}' not found")
                self.dialog.destroy()
                return

            # Set basic fields
            self.name_var.set(agent_data.get('name', ''))
            self.file_var.set(self.agent_file)
            self.description_var.set(agent_data.get('description', ''))

            # Set tools
            tools = agent_data.get('tools', [])
            for tool_name, var in self.tool_checkboxes.items():
                var.set(tool_name in tools)

            # Set skills
            skills = agent_data.get('skills', [])
            for skill_dir, var in self.skill_checkboxes.items():
                var.set(skill_dir in skills)
            self.update_skills_summary()

            # Load contract
            if self.contracts_file.exists():
                with open(self.contracts_file, 'r') as f:
                    contracts = json.load(f)

                contract = contracts.get('agents', {}).get(self.agent_file, {})
                if contract:
                    self.role_var.set(contract.get('role', ''))
                    self.output_dir_var.set(contract.get('outputs', {}).get('output_directory', ''))
                    self.root_doc_var.set(contract.get('outputs', {}).get('root_document', ''))

                    success = contract.get('statuses', {}).get('success', [])
                    if success:
                        self.success_status_var.set(success[0].get('code', ''))
                        next_agents = success[0].get('next_agents', [])
                        if next_agents:
                            next_name = self.agents_map.get(next_agents[0], next_agents[0])
                            self.next_agent_var.set(next_name)
                        else:
                            self.next_agent_var.set('(none - workflow ends)')

                    self.metadata_required_var.set(contract.get('metadata_required', True))

            # Load markdown
            md_file = self.agents_dir / f"{self.agent_file}.md"
            if md_file.exists():
                with open(md_file, 'r') as f:
                    content = f.read()
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        self.details_text.insert('1.0', parts[2].strip())

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")
            self.dialog.destroy()

    def save_agent(self):
        """Save the agent."""
        # Validate
        name = self.name_var.get().strip()
        file_slug = self.file_var.get().strip()
        description = self.description_var.get().strip()
        details = self.details_text.get('1.0', tk.END).strip()

        tools = [name for name, var in self.tool_checkboxes.items() if var.get()]
        skills = [skill_dir for skill_dir, var in self.skill_checkboxes.items() if var.get()]

        role = self.role_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        root_doc = self.root_doc_var.get().strip()
        success_status = self.success_status_var.get().strip()
        next_agent = self.next_agent_var.get().strip()

        if not all([name, file_slug, description, details, role, output_dir, root_doc, success_status, next_agent]):
            messagebox.showwarning("Validation", "All required fields must be filled.")
            return

        if not tools:
            messagebox.showwarning("Validation", "Select at least one tool.")
            return

        if not re.match(r'^[a-z0-9-]+$', file_slug):
            messagebox.showerror("Invalid File Name", "File name must be lowercase with hyphens only.")
            return

        # Get next agent key
        next_agent_file = None
        if next_agent != '(none - workflow ends)':
            for key, val in self.agents_map.items():
                if val == next_agent:
                    next_agent_file = key
                    break

        try:
            # Update agents.json
            with open(self.agents_json_file, 'r') as f:
                data = json.load(f)

            agents = data.get('agents', []) if isinstance(data, dict) else data

            if self.mode == 'create':
                if any(a.get('agent-file') == file_slug for a in agents):
                    messagebox.showerror("Duplicate", f"Agent '{file_slug}' already exists.")
                    return

                agents.append({
                    "name": name,
                    "agent-file": file_slug,
                    "tools": tools,
                    "skills": skills,
                    "description": description
                })
            else:
                for agent in agents:
                    if agent.get('agent-file') == file_slug:
                        agent['name'] = name
                        agent['tools'] = tools
                        agent['skills'] = skills
                        agent['description'] = description
                        break

            # Save agents.json
            if isinstance(data, dict):
                data['agents'] = agents
                with open(self.agents_json_file, 'w') as f:
                    json.dump(data, f, indent=2)
            else:
                with open(self.agents_json_file, 'w') as f:
                    json.dump(agents, f, indent=2)

            # Update contracts
            with open(self.contracts_file, 'r') as f:
                contracts = json.load(f)

            contracts['agents'][file_slug] = {
                "role": role,
                "description": description,
                "inputs": {
                    "required": [{
                        "name": "source_document",
                        "pattern": "enhancements/{enhancement_name}/*/{document}.md",
                        "description": "Input from previous phase"
                    }]
                },
                "outputs": {
                    "root_document": root_doc,
                    "output_directory": output_dir,
                    "additional_required": []
                },
                "statuses": {
                    "success": [{
                        "code": success_status,
                        "description": f"{name} complete",
                        "next_agents": [next_agent_file] if next_agent_file else []
                    }],
                    "failure": [{
                        "code": "BLOCKED",
                        "pattern": "BLOCKED: {reason}",
                        "description": "Cannot proceed"
                    }]
                },
                "metadata_required": self.metadata_required_var.get()
            }

            with open(self.contracts_file, 'w') as f:
                json.dump(contracts, f, indent=2)

            # Create markdown file
            md_content = f"""---
name: "{name}"
description: "{description}"
tools: {json.dumps(tools)}
skills: {json.dumps(skills)}
---

{details}
"""

            md_file = self.agents_dir / f"{file_slug}.md"
            with open(md_file, 'w') as f:
                f.write(md_content)

            self.result = file_slug
            messagebox.showinfo(
                "Success",
                f"Agent '{name}' saved successfully!\n\n"
                f"✓ agents.json updated\n"
                f"✓ {file_slug}.md created\n"
                f"✓ AGENT_CONTRACTS.json updated\n"
                f"✓ {len(skills)} skill(s) assigned"
            )
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def cancel(self):
        """Cancel dialog."""
        self.result = None
        self.dialog.destroy()