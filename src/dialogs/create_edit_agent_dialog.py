"""
Create/Edit Agent dialog for creating and editing agent definitions.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import json
import re
import urllib.request
import urllib.error


class CreateEditAgentDialog:
    """Dialog for creating or editing an agent."""

    def __init__(self, parent, queue_interface, settings=None, mode='create', agent_file=None):
        self.queue = queue_interface
        self.settings = settings
        self.mode = mode  # 'create' or 'edit'
        self.agent_file = agent_file
        self.result = None

        self.agents_dir = self.queue.agents_file.parent
        self.agents_json_file = self.queue.agents_file
        self.contracts_file = self.queue.project_root / ".claude/AGENT_CONTRACTS.json"

        # Load tools data
        self.tools_data = self.queue.get_tools_data()
        self.tool_checkboxes = {}  # Will store tool name -> BooleanVar mapping

        # Load existing agents for next agent dropdown
        self.agents_map = self.queue.get_agent_list()

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Agent" if mode == 'create' else "Edit Agent")
        self.dialog.geometry("750x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.build_ui()

        if mode == 'edit' and agent_file:
            self.load_agent_data()

        # Wait for dialog to close
        self.dialog.wait_window()

    def build_ui(self):
        # Main container
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create notebook (tabbed interface)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create tabs
        basic_tab = ttk.Frame(notebook, padding=20)
        workflow_tab = ttk.Frame(notebook, padding=20)
        tools_tab = ttk.Frame(notebook, padding=20)

        notebook.add(basic_tab, text="Basic Information")
        notebook.add(workflow_tab, text="Workflow Contract")
        notebook.add(tools_tab, text="Tools & Skills")

        # Build each tab
        self.build_basic_tab(basic_tab)
        self.build_workflow_tab(workflow_tab)
        self.build_tools_tab(tools_tab)

        # Bottom buttons (outside tabs)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        save_text = "Save"
        ttk.Button(button_frame, text=save_text, command=self.save_agent, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel, width=15).pack(side=tk.LEFT, padx=5)

        # Required fields note
        ttk.Label(main_frame, text="* Required fields", font=('Arial', 9), foreground='gray').pack()

    def build_basic_tab(self, parent):
        """Build the Basic Information tab."""
        # Name
        ttk.Label(parent, text="Agent Name: *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.name_var, width=60).pack(fill=tk.X, pady=(0, 15))

        # File name (slug)
        ttk.Label(parent, text="File Name (slug): *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.file_var = tk.StringVar()
        file_entry = ttk.Entry(parent, textvariable=self.file_var, width=60)
        file_entry.pack(fill=tk.X, pady=(0, 5))
        if self.mode == 'edit':
            file_entry.config(state='readonly')
        ttk.Label(parent, text="(lowercase, hyphens, no spaces or extension)",
                  font=('Arial', 8), foreground='gray').pack(anchor=tk.W, pady=(0, 15))

        # Description
        ttk.Label(parent, text="Description: *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(parent, text="Brief one-line description of the agent's purpose",
                  font=('Arial', 8), foreground='gray').pack(anchor=tk.W, pady=(0, 5))

        desc_frame = ttk.Frame(parent)
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        self.description_text = tk.Text(desc_frame, height=1, wrap=tk.WORD, font=('Arial', 10))
        desc_scrollbar = ttk.Scrollbar(desc_frame, orient=tk.VERTICAL, command=self.description_text.yview)
        self.description_text.configure(yscrollcommand=desc_scrollbar.set)

        self.description_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Agent Details
        details_header = ttk.Frame(parent)
        details_header.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(details_header, text="Agent Details: *", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

        # Check if API key is available
        api_key = self.settings.get_claude_api_key() if self.settings else None
        generate_btn = ttk.Button(details_header, text="Generate with AI", command=self.generate_details)
        generate_btn.pack(side=tk.RIGHT)
        if not api_key:
            generate_btn.config(state=tk.DISABLED)

        ttk.Label(parent, text="Comprehensive role definition, responsibilities, and guidelines",
                  font=('Arial', 8), foreground='gray').pack(anchor=tk.W, pady=(0, 5))

        details_frame = ttk.Frame(parent)
        details_frame.pack(fill=tk.BOTH, expand=True)

        self.details_text = tk.Text(details_frame, wrap=tk.WORD, font=('Courier', 9), height=12)
        details_scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)

        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def build_workflow_tab(self, parent):
        """Build the Workflow Contract tab."""
        # Role
        ttk.Label(parent, text="Role in Workflow: *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.role_var = tk.StringVar()
        role_combo = ttk.Combobox(parent, textvariable=self.role_var, state='readonly', width=40)
        role_combo['values'] = ['analysis', 'technical_design', 'implementation', 'testing', 'documentation',
                                'integration']
        role_combo.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(parent, text="Determines task type and workflow position",
                  font=('Arial', 8), foreground='gray').pack(anchor=tk.W, pady=(0, 15))
        role_combo.bind('<<ComboboxSelected>>', self.on_role_selected)

        # Output Directory
        ttk.Label(parent, text="Output Directory Name: *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.output_dir_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.output_dir_var, width=50).pack(fill=tk.X, pady=(0, 5))
        ttk.Label(parent, text="Subdirectory under enhancement (e.g., 'requirements-analyst')",
                  font=('Arial', 8), foreground='gray').pack(anchor=tk.W, pady=(0, 15))

        # Root Document
        ttk.Label(parent, text="Root Output Document: *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.root_doc_var = tk.StringVar(value="summary.md")
        ttk.Entry(parent, textvariable=self.root_doc_var, width=50).pack(fill=tk.X, pady=(0, 5))
        ttk.Label(parent, text="Primary handoff document (e.g., 'analysis_summary.md')",
                  font=('Arial', 8), foreground='gray').pack(anchor=tk.W, pady=(0, 15))

        # Success Status Code
        ttk.Label(parent, text="Success Status Code: *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.success_status_var = tk.StringVar()
        success_combo = ttk.Combobox(parent, textvariable=self.success_status_var,
                                     state='readonly', width=40)
        success_combo['values'] = [
            'READY_FOR_DEVELOPMENT',
            'READY_FOR_IMPLEMENTATION',
            'READY_FOR_TESTING',
            'TESTING_COMPLETE',
            'DOCUMENTATION_COMPLETE',
            'INTEGRATION_COMPLETE'
        ]
        success_combo.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(parent, text="Status code output when agent completes successfully",
                  font=('Arial', 8), foreground='gray').pack(anchor=tk.W, pady=(0, 15))

        # Next Agent(s)
        ttk.Label(parent, text="Next Agent (after success): *", font=('Arial', 10, 'bold')).pack(anchor=tk.W,
                                                                                                 pady=(0, 5))
        self.next_agent_var = tk.StringVar()
        self.next_agent_combo = ttk.Combobox(parent, textvariable=self.next_agent_var,
                                             state='readonly', width=40)
        # Populate with available agents
        next_agent_values = ['(none - workflow ends)'] + list(self.agents_map.values())
        self.next_agent_combo['values'] = next_agent_values
        self.next_agent_combo.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(parent, text="Which agent runs next in the workflow",
                  font=('Arial', 8), foreground='gray').pack(anchor=tk.W, pady=(0, 15))

        # Metadata Required
        self.metadata_required_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Require metadata header in outputs",
                        variable=self.metadata_required_var).pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(parent, text="YAML frontmatter with enhancement, agent, task_id, timestamp, status",
                  font=('Arial', 8), foreground='gray').pack(anchor=tk.W, padx=(20, 0))

    def build_tools_tab(self, parent):
        """Build the Tools & Skills tab."""
        # Agent Persona (optional preset)
        if self.tools_data and 'agent_personas' in self.tools_data:
            ttk.Label(parent, text="Quick Start: Agent Persona", font=('Arial', 10, 'bold')).pack(anchor=tk.W,
                                                                                                  pady=(0, 5))

            persona_frame = ttk.Frame(parent)
            persona_frame.pack(fill=tk.X, pady=(0, 5))

            ttk.Label(persona_frame, text="Select a preset:").pack(side=tk.LEFT, padx=(0, 10))
            self.persona_var = tk.StringVar(value="")

            # Create dropdown with persona options
            personas = list(self.tools_data['agent_personas'].keys())
            persona_names = ["(none)"] + [self.tools_data['agent_personas'][p]['display_name'] for p in personas]
            persona_combo = ttk.Combobox(persona_frame, textvariable=self.persona_var,
                                         values=persona_names, state='readonly', width=25)
            persona_combo.pack(side=tk.LEFT)
            persona_combo.bind('<<ComboboxSelected>>', self.on_persona_selected)

            ttk.Label(parent, text="Automatically selects appropriate tools for common agent types",
                      font=('Arial', 8), foreground='gray').pack(anchor=tk.W, pady=(0, 15))

        # Tools Selection
        ttk.Label(parent, text="Available Tools: *", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(parent, text="Select the Claude Code tools this agent can use",
                  font=('Arial', 8), foreground='gray').pack(anchor=tk.W, pady=(0, 10))

        # Simple frame for tools (no scrolling)
        tools_frame = ttk.Frame(parent)
        tools_frame.pack(fill=tk.BOTH, expand=True)

        if self.tools_data and 'claude_code_tools' in self.tools_data:
            # Create checkbox grid (3 columns)
            tools_list = self.tools_data['claude_code_tools']
            num_cols = 3  # Changed from 2 to 3

            for idx, tool in enumerate(tools_list):
                tool_name = tool['name']
                tool_display = tool.get('display_name', tool_name)

                row = idx // num_cols
                col = idx % num_cols

                # Create checkbox
                var = tk.BooleanVar(value=False)
                self.tool_checkboxes[tool_name] = var

                cb = ttk.Checkbutton(tools_frame, text=f"{tool_display}", variable=var)
                cb.grid(row=row, column=col, sticky=tk.W, padx=15, pady=3)
        else:
            # Fallback to text entry if tools.json not available
            ttk.Label(tools_frame, text="Tools data not available. Using text entry:",
                      foreground='red').pack(anchor=tk.W)
            self.tools_var = tk.StringVar()
            ttk.Entry(tools_frame, textvariable=self.tools_var, width=50).pack(fill=tk.X, pady=(5, 0))
            ttk.Label(tools_frame, text="Example: Read, Write, Edit, Bash, Glob, Grep",
                      font=('Arial', 8), foreground='gray').pack(anchor=tk.W)

    def on_role_selected(self, event=None):
        """Auto-populate contract fields based on role selection."""
        role = self.role_var.get()

        role_defaults = {
            'analysis': {
                'output_dir': 'requirements-analyst',
                'root_doc': 'analysis_summary.md',
                'success_status': 'READY_FOR_DEVELOPMENT',
                'next_agent': 'Architect'
            },
            'technical_design': {
                'output_dir': 'architect',
                'root_doc': 'implementation_plan.md',
                'success_status': 'READY_FOR_IMPLEMENTATION',
                'next_agent': 'Implementer'
            },
            'implementation': {
                'output_dir': 'implementer',
                'root_doc': 'test_plan.md',
                'success_status': 'READY_FOR_TESTING',
                'next_agent': 'Tester'
            },
            'testing': {
                'output_dir': 'tester',
                'root_doc': 'test_summary.md',
                'success_status': 'TESTING_COMPLETE',
                'next_agent': 'Documenter'
            },
            'documentation': {
                'output_dir': 'documenter',
                'root_doc': 'documentation_summary.md',
                'success_status': 'DOCUMENTATION_COMPLETE',
                'next_agent': '(none - workflow ends)'
            },
            'integration': {
                'output_dir': 'integration-coordinator',
                'root_doc': 'integration_summary.md',
                'success_status': 'INTEGRATION_COMPLETE',
                'next_agent': '(none - workflow ends)'
            }
        }

        if role in role_defaults:
            defaults = role_defaults[role]
            self.output_dir_var.set(defaults['output_dir'])
            self.root_doc_var.set(defaults['root_doc'])
            self.success_status_var.set(defaults['success_status'])
            self.next_agent_var.set(defaults['next_agent'])

    def on_persona_selected(self, event=None):
        """Handle agent persona selection and auto-fill tools."""
        if not self.tools_data or 'agent_personas' not in self.tools_data:
            return

        selected_display_name = self.persona_var.get()
        if not selected_display_name or selected_display_name == "(none)":
            # Clear all checkboxes if empty selection
            for var in self.tool_checkboxes.values():
                var.set(False)
            return

        # Find the persona key by display name
        persona_key = None
        for key, persona in self.tools_data['agent_personas'].items():
            if persona['display_name'] == selected_display_name:
                persona_key = key
                break

        if not persona_key:
            return

        # Get the tools for this persona
        persona_tools = self.tools_data['agent_personas'][persona_key].get('tools', [])

        # Clear all checkboxes first
        for var in self.tool_checkboxes.values():
            var.set(False)

        # Set checkboxes for persona tools
        for tool_name in persona_tools:
            if tool_name in self.tool_checkboxes:
                self.tool_checkboxes[tool_name].set(True)

    def get_agent_key(self, display_name: str) -> str:
        """Convert agent display name to agent-file key."""
        for key, value in self.agents_map.items():
            if value == display_name:
                return key
        return display_name

    def load_agent_data(self):
        """Load existing agent data for editing."""
        try:
            # Load from agents.json
            with open(self.agents_json_file, 'r') as f:
                data = json.load(f)

            # Handle both {"agents": [...]} and [...] formats
            if isinstance(data, list):
                agents = data
            elif isinstance(data, dict) and 'agents' in data:
                agents = data['agents']
            else:
                agents = []

            agent_data = next((a for a in agents if a.get('agent-file') == self.agent_file), None)

            if not agent_data:
                messagebox.showerror("Error", f"Agent '{self.agent_file}' not found in agents.json")
                self.dialog.destroy()
                return

            # Set basic fields
            self.name_var.set(agent_data.get('name', ''))
            self.file_var.set(self.agent_file)
            self.description_text.insert('1.0', agent_data.get('description', ''))

            # Set tool checkboxes from agent data
            tools = agent_data.get('tools', [])
            if self.tool_checkboxes:
                for tool_name, var in self.tool_checkboxes.items():
                    var.set(tool_name in tools)
            else:
                if hasattr(self, 'tools_var'):
                    self.tools_var.set(', '.join(tools))

            # Load contract data
            if self.contracts_file.exists():
                with open(self.contracts_file, 'r') as f:
                    contracts_data = json.load(f)

                contract = contracts_data.get("agents", {}).get(self.agent_file, {})

                if contract:
                    self.role_var.set(contract.get('role', ''))
                    self.output_dir_var.set(contract.get('outputs', {}).get('output_directory', ''))
                    self.root_doc_var.set(contract.get('outputs', {}).get('root_document', ''))

                    # Get success status
                    success_statuses = contract.get('statuses', {}).get('success', [])
                    if success_statuses:
                        self.success_status_var.set(success_statuses[0].get('code', ''))

                        # Get next agent
                        next_agents = success_statuses[0].get('next_agents', [])
                        if next_agents:
                            next_agent_file = next_agents[0]
                            next_agent_name = self.agents_map.get(next_agent_file, next_agent_file)
                            self.next_agent_var.set(next_agent_name)
                        else:
                            self.next_agent_var.set('(none - workflow ends)')

                    self.metadata_required_var.set(contract.get('metadata_required', True))

            # Load markdown file
            md_file = self.agents_dir / f"{self.agent_file}.md"
            if md_file.exists():
                with open(md_file, 'r') as f:
                    content = f.read()
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        details = parts[2].strip()
                        self.details_text.insert('1.0', details)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load agent data: {e}")
            self.dialog.destroy()

    def generate_details(self):
        """Generate agent details using Claude API."""
        name = self.name_var.get().strip()
        description = self.description_text.get('1.0', tk.END).strip()

        if not name or not description:
            messagebox.showwarning("Missing Information", "Please enter Agent Name and Description first.")
            return

        api_key = self.settings.get_claude_api_key() if self.settings else None
        if not api_key:
            messagebox.showwarning("No API Key", "Claude API key not configured.")
            return

        # Show loading indicator
        progress = tk.Toplevel(self.dialog)
        progress.title("Generating Agent Details")
        progress.geometry("350x100")
        progress.transient(self.dialog)
        progress.grab_set()

        progress_frame = ttk.Frame(progress, padding=20)
        progress_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(progress_frame, text="Calling Claude API...", font=('Arial', 10)).pack(pady=(0, 10))
        progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate', length=250)
        progress_bar.pack(pady=(0, 10))
        progress_bar.start()
        progress.update()

        try:
            context_prompt = f"""Agent Name: {name}

Description: {description}

Generate comprehensive agent details following this structure:

# [Agent Name] Agent

## Role and Purpose
[Clear description of the agent's role and primary purpose]

## Core Responsibilities
[Numbered list of 3-5 key responsibilities]

## Workflow
[Step-by-step workflow description]

## Output Standards
[Description of expected output format and quality standards]

## Success Criteria
[Bulleted list of success metrics]

## Scope Boundaries
### ✅ DO:
[List of things the agent should do]

### ❌ DO NOT:
[List of things the agent should avoid]

## Status Reporting
[Expected status reporting format and keywords]

## Communication
[Communication guidelines and best practices]

Focus on clarity, actionable guidance, and role boundaries."""

            generated_details = self.call_claude_api(context_prompt)
            progress.destroy()

            self.details_text.delete('1.0', tk.END)
            self.details_text.insert('1.0', generated_details)

        except Exception as e:
            progress.destroy()
            messagebox.showerror("API Error", f"Failed to generate agent details: {str(e)}")

    def call_claude_api(self, context_prompt: str) -> str:
        """Call Claude API to generate agent details."""
        api_key = self.settings.get_claude_api_key() if self.settings else None
        if not api_key:
            raise Exception("No API key configured")

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        system_prompt = """You are an expert at creating detailed agent role definitions for multi-agent AI systems.
Generate ONLY the agent details content without any conversational framing, preamble, or meta-commentary.
Do not include phrases like "Here's the agent details" - output only the content itself.

Follow the provided structure exactly and create comprehensive, actionable guidance for the agent."""

        data = {
            "model": "claude-sonnet-4-5-20250929",
            "max_tokens": 8192,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": context_prompt
                }
            ]
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['content'][0]['text']

    def save_agent(self):
        """Save the agent (create or update)."""
        # Validate basic fields
        name = self.name_var.get().strip()
        file_slug = self.file_var.get().strip()
        description = self.description_text.get('1.0', tk.END).strip()
        details = self.details_text.get('1.0', tk.END).strip()

        # Collect selected tools
        tools = []
        if self.tool_checkboxes:
            tools = [tool_name for tool_name, var in self.tool_checkboxes.items() if var.get()]
        else:
            if hasattr(self, 'tools_var'):
                tools_str = self.tools_var.get().strip()
                tools = [t.strip() for t in tools_str.split(',') if t.strip()]

        # Validate contract fields
        role = self.role_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        root_doc = self.root_doc_var.get().strip()
        success_status = self.success_status_var.get().strip()
        next_agent = self.next_agent_var.get().strip()
        metadata_required = self.metadata_required_var.get()

        if not all([name, file_slug, description, details]):
            messagebox.showwarning("Validation Error", "All basic fields are required.")
            return

        if not tools:
            messagebox.showwarning("Validation Error", "At least one tool must be selected.")
            return

        if not all([role, output_dir, root_doc, success_status, next_agent]):
            messagebox.showwarning("Validation Error", "All workflow contract fields are required.")
            return

        if not re.match(r'^[a-z0-9-]+$', file_slug):
            messagebox.showerror("Invalid File Name",
                                 "File name must be lowercase with hyphens only (e.g., 'my-agent-name')")
            return

        # Convert next agent display name to agent-file key
        next_agent_file = None
        if next_agent != '(none - workflow ends)':
            next_agent_file = self.get_agent_key(next_agent)

        try:
            # Update agents.json
            with open(self.agents_json_file, 'r') as f:
                data = json.load(f)

            if isinstance(data, list):
                agents = data
            elif isinstance(data, dict) and 'agents' in data:
                agents = data['agents']
            else:
                agents = []

            if self.mode == 'create':
                if any(a.get('agent-file') == file_slug for a in agents):
                    messagebox.showerror("Duplicate Agent", f"An agent with file name '{file_slug}' already exists.")
                    return

                agents.append({
                    "name": name,
                    "agent-file": file_slug,
                    "tools": tools,
                    "description": description
                })
            else:
                for agent in agents:
                    if agent.get('agent-file') == file_slug:
                        agent['name'] = name
                        agent['tools'] = tools
                        agent['description'] = description
                        break

            # Save agents.json
            if isinstance(data, list):
                with open(self.agents_json_file, 'w') as f:
                    json.dump(agents, f, indent=2)
            else:
                data['agents'] = agents
                with open(self.agents_json_file, 'w') as f:
                    json.dump(data, f, indent=2)

            # Update AGENT_CONTRACTS.json
            if self.contracts_file.exists():
                with open(self.contracts_file, 'r') as f:
                    contracts_data = json.load(f)
            else:
                contracts_data = {
                    "version": "1.0.0",
                    "description": "Agent contracts defining inputs, outputs, and workflow transitions",
                    "agents": {},
                    "metadata_fields": {
                        "enhancement": {"type": "string", "description": "Enhancement name", "required": True},
                        "agent": {"type": "string", "description": "Agent that created the document", "required": True},
                        "task_id": {"type": "string", "description": "Task queue ID", "required": True},
                        "timestamp": {"type": "string", "format": "ISO-8601", "description": "Creation time",
                                      "required": True},
                        "status": {"type": "string", "description": "Completion status", "required": True}
                    }
                }

            # Create contract entry
            contract = {
                "role": role,
                "description": description,
                "inputs": {
                    "required": [{
                        "name": "source_document",
                        "pattern": "enhancements/{enhancement_name}/*/{document}.md",
                        "description": "Input document from previous workflow phase"
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
                        "description": f"{name} phase complete",
                        "next_agents": [next_agent_file] if next_agent_file else []
                    }],
                    "failure": [{
                        "code": "BLOCKED",
                        "pattern": "BLOCKED: {reason}",
                        "description": "Cannot proceed due to blocking issue"
                    }]
                },
                "metadata_required": metadata_required
            }

            contracts_data["agents"][file_slug] = contract

            with open(self.contracts_file, 'w') as f:
                json.dump(contracts_data, f, indent=2)

            # Create/update markdown file
            md_content = f"""---
name: "{name}"
description: "{description}"
tools: {json.dumps(tools)}
---

{details}
"""

            md_file = self.agents_dir / f"{file_slug}.md"
            with open(md_file, 'w') as f:
                f.write(md_content)

            self.result = file_slug
            messagebox.showinfo("Success",
                                f"Agent '{name}' saved successfully.\n\n"
                                f"✓ agents.json updated\n"
                                f"✓ {file_slug}.md created\n"
                                f"✓ AGENT_CONTRACTS.json updated")
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save agent: {e}")

    def cancel(self):
        self.result = None
        self.dialog.destroy()