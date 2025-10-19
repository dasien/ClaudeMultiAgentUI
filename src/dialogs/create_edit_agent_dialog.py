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

        # Load tools data
        self.tools_data = self.queue.get_tools_data()
        self.tool_checkboxes = {}  # Will store tool name -> BooleanVar mapping

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Agent" if mode == 'create' else "Edit Agent")
        self.dialog.geometry("700x850")
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
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Name
        ttk.Label(main_frame, text="Agent Name: *").pack(anchor=tk.W)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=50).pack(fill=tk.X, pady=(0, 10))

        # File name (slug)
        ttk.Label(main_frame, text="File Name (slug): *").pack(anchor=tk.W)
        self.file_var = tk.StringVar()
        file_entry = ttk.Entry(main_frame, textvariable=self.file_var, width=50)
        file_entry.pack(fill=tk.X, pady=(0, 5))
        if self.mode == 'edit':
            file_entry.config(state='readonly')
        ttk.Label(main_frame, text="(lowercase, hyphens, no spaces or extension)", font=('Arial', 8), foreground='gray').pack(anchor=tk.W, pady=(0, 10))

        # Description
        ttk.Label(main_frame, text="Description: *").pack(anchor=tk.W)
        self.description_text = tk.Text(main_frame, height=3, wrap=tk.WORD)
        self.description_text.pack(fill=tk.X, pady=(0, 10))

        # Agent Persona (optional preset)
        if self.tools_data and 'agent_personas' in self.tools_data:
            persona_frame = ttk.Frame(main_frame)
            persona_frame.pack(fill=tk.X, pady=(0, 10))

            ttk.Label(persona_frame, text="Agent Persona (optional): ").pack(side=tk.LEFT)
            self.persona_var = tk.StringVar(value="")

            # Create dropdown with persona options
            personas = list(self.tools_data['agent_personas'].keys())
            persona_names = [""] + [self.tools_data['agent_personas'][p]['display_name'] for p in personas]
            persona_combo = ttk.Combobox(persona_frame, textvariable=self.persona_var, values=persona_names, state='readonly', width=25)
            persona_combo.pack(side=tk.LEFT, padx=5)
            persona_combo.bind('<<ComboboxSelected>>', self.on_persona_selected)

            ttk.Label(persona_frame, text="(select to auto-fill tools)", font=('Arial', 8), foreground='gray').pack(side=tk.LEFT, padx=5)

        # Tools (checkboxes)
        tools_label_frame = ttk.LabelFrame(main_frame, text="Tools *", padding=10)
        tools_label_frame.pack(fill=tk.BOTH, pady=(0, 10))

        if self.tools_data and 'claude_code_tools' in self.tools_data:
            # Create checkbox grid (2 columns)
            tools_list = self.tools_data['claude_code_tools']
            num_cols = 2

            for idx, tool in enumerate(tools_list):
                tool_name = tool['name']
                tool_display = tool.get('display_name', tool_name)
                tool_desc = tool.get('description', '')

                row = idx // num_cols
                col = idx % num_cols

                # Create checkbox with tooltip
                var = tk.BooleanVar(value=False)
                self.tool_checkboxes[tool_name] = var

                cb = ttk.Checkbutton(tools_label_frame, text=f"{tool_display} ({tool_name})", variable=var)
                cb.grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)
        else:
            # Fallback to text entry if tools.json not available
            ttk.Label(tools_label_frame, text="Tools data not available. Using text entry:", foreground='red').pack(anchor=tk.W)
            self.tools_var = tk.StringVar()
            ttk.Entry(tools_label_frame, textvariable=self.tools_var, width=50).pack(fill=tk.X, pady=(5, 0))
            ttk.Label(tools_label_frame, text="Example: Read, Write, Edit, Bash, Glob, Grep", font=('Arial', 8), foreground='gray').pack(anchor=tk.W)

        # Agent Details with Generate button
        details_label_frame = ttk.Frame(main_frame)
        details_label_frame.pack(fill=tk.X, anchor=tk.W)
        ttk.Label(details_label_frame, text="Agent Details: *").pack(side=tk.LEFT)

        # Check if API key is available
        api_key = self.settings.get_claude_api_key() if self.settings else None
        generate_btn = ttk.Button(details_label_frame, text="Generate", command=self.generate_details)
        generate_btn.pack(side=tk.RIGHT)
        if not api_key:
            generate_btn.config(state=tk.DISABLED)

        self.details_text = tk.Text(main_frame, height=15, wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Required fields note
        ttk.Label(main_frame, text="* Required fields", font=('Arial', 9), foreground='gray').pack(anchor=tk.W)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        save_text = "Create Agent" if self.mode == 'create' else "Save Changes"
        ttk.Button(button_frame, text=save_text, command=self.save_agent).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)

    def on_persona_selected(self, event=None):
        """Handle agent persona selection and auto-fill tools."""
        if not self.tools_data or 'agent_personas' not in self.tools_data:
            return

        selected_display_name = self.persona_var.get()
        if not selected_display_name:
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

    def load_agent_data(self):
        """Load existing agent data for editing."""
        try:
            # Load from agents.json
            with open(self.agents_json_file, 'r') as f:
                data = json.load(f)

            agents = data.get('agents', [])
            agent_data = next((a for a in agents if a.get('agent-file') == self.agent_file), None)

            if not agent_data:
                messagebox.showerror("Error", f"Agent '{self.agent_file}' not found in agents.json")
                self.dialog.destroy()
                return

            # Set form fields
            self.name_var.set(agent_data.get('name', ''))
            self.file_var.set(self.agent_file)
            self.description_text.insert('1.0', agent_data.get('description', ''))

            # Set tool checkboxes from agent data
            tools = agent_data.get('tools', [])
            if self.tool_checkboxes:
                # Using checkboxes
                for tool_name, var in self.tool_checkboxes.items():
                    var.set(tool_name in tools)
            else:
                # Fallback to text entry
                if hasattr(self, 'tools_var'):
                    self.tools_var.set(', '.join(tools))

            # Load markdown file
            md_file = self.agents_dir / f"{self.agent_file}.md"
            if md_file.exists():
                with open(md_file, 'r') as f:
                    content = f.read()
                    # Extract content after frontmatter
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
            # Call Claude API
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

            # Set the generated details
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
        # Validate
        name = self.name_var.get().strip()
        file_slug = self.file_var.get().strip()
        description = self.description_text.get('1.0', tk.END).strip()
        details = self.details_text.get('1.0', tk.END).strip()

        # Collect selected tools from checkboxes or text entry
        tools = []
        if self.tool_checkboxes:
            # Using checkboxes
            tools = [tool_name for tool_name, var in self.tool_checkboxes.items() if var.get()]
        else:
            # Fallback to text entry
            tools_str = self.tools_var.get().strip() if hasattr(self, 'tools_var') else ""
            tools = [t.strip() for t in tools_str.split(',') if t.strip()]

        if not all([name, file_slug, description, details]):
            messagebox.showwarning("Validation Error", "All fields are required.")
            return

        if not tools:
            messagebox.showwarning("Validation Error", "At least one tool must be selected.")
            return

        # Validate file slug format
        if not re.match(r'^[a-z0-9-]+$', file_slug):
            messagebox.showerror("Invalid File Name", "File name must be lowercase with hyphens only (e.g., 'my-agent-name')")
            return

        try:
            # Create/update agents.json
            with open(self.agents_json_file, 'r') as f:
                data = json.load(f)

            agents = data.get('agents', [])

            if self.mode == 'create':
                # Check if agent file already exists
                if any(a.get('agent-file') == file_slug for a in agents):
                    messagebox.showerror("Duplicate Agent", f"An agent with file name '{file_slug}' already exists.")
                    return

                # Add new agent
                agents.append({
                    "name": name,
                    "agent-file": file_slug,
                    "tools": tools,
                    "description": description
                })
            else:
                # Update existing agent
                for agent in agents:
                    if agent.get('agent-file') == file_slug:
                        agent['name'] = name
                        agent['tools'] = tools
                        agent['description'] = description
                        break

            # Save agents.json
            data['agents'] = agents
            with open(self.agents_json_file, 'w') as f:
                json.dump(data, f, indent=2)

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
            messagebox.showinfo("Success", f"Agent '{name}' saved successfully.")
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save agent: {e}")

    def cancel(self):
        self.result = None
        self.dialog.destroy()