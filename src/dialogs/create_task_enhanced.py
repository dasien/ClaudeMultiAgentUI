"""
Enhanced Create Task Dialog with skills preview and quick workflows.
v3.0 - Includes skills display and workflow templates.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json
import urllib.request


class CreateTaskDialog:
    """Enhanced dialog for creating tasks with skills preview and quick workflows."""

    def __init__(self, parent, queue_interface, settings=None):
        self.queue = queue_interface
        self.settings = settings
        self.result = None
        self.should_start = False

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Task")
        self.dialog.geometry("700x850")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # Get agents map
        self.agents_map = self.queue.get_agent_list()
        self.task_types_map = self.queue.get_task_types()

        self.build_ui()

        # Wait for dialog
        self.dialog.wait_window()

    def build_ui(self):
        """Build the UI."""
        # Simple frame without scrolling
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(main_frame, text="Title: *").pack(anchor="w")
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=70)
        self.title_entry.pack(fill="x", pady=(0, 5))

        # Workflow and Agent on same line (like Priority and Task Type)
        workflow_agent_frame = ttk.Frame(main_frame)
        workflow_agent_frame.pack(fill="x", pady=(0, 10))

        # Workflow
        workflow_col = ttk.Frame(workflow_agent_frame)
        workflow_col.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Label(workflow_col, text="Quick Start Workflow (optional):").pack(anchor="w")
        self.workflow_var = tk.StringVar()
        workflow_combo = ttk.Combobox(workflow_col, textvariable=self.workflow_var, state='readonly', width=25)
        workflows = [
            "(none)",
            "📋 Full Feature",
            "🐛 Bug Fix",
            "🔥 Hotfix",
            "🔧 Refactoring"
        ]
        workflow_combo['values'] = workflows
        workflow_combo.current(0)
        workflow_combo.pack(fill="x")
        workflow_combo.bind('<<ComboboxSelected>>', self.on_workflow_selected)

        # Agent
        agent_col = ttk.Frame(workflow_agent_frame)
        agent_col.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ttk.Label(agent_col, text="Agent: *").pack(anchor="w")
        self.agent_var = tk.StringVar()
        self.agent_combo = ttk.Combobox(agent_col, textvariable=self.agent_var, state='readonly', width=25)
        self.agent_combo['values'] = list(self.agents_map.values())
        if self.agent_combo['values']:
            self.agent_combo.current(0)
        self.agent_combo.pack(fill="x")
        self.agent_combo.bind('<<ComboboxSelected>>', self.on_agent_selected)

        # Skills Preview Frame
        self.skills_frame = ttk.LabelFrame(main_frame, text="🎯 Agent Skills", padding=10)
        self.skills_frame.pack(fill="x", pady=(0, 10))

        self.skills_list_label = ttk.Label(
            self.skills_frame,
            text="Select an agent to see available skills",
            font=('Arial', 9),
            foreground='gray'
        )
        self.skills_list_label.pack(anchor="w")

        ttk.Button(
            self.skills_frame,
            text="Preview Full Skills Prompt",
            command=self.preview_skills_prompt,
            state=tk.DISABLED
        ).pack(anchor="w", pady=(5, 0))

        self.preview_btn = None  # Store reference for state management

        # Priority and Task Type on same line
        priority_type_frame = ttk.Frame(main_frame)
        priority_type_frame.pack(fill="x", pady=(0, 10))

        # Priority
        priority_col = ttk.Frame(priority_type_frame)
        priority_col.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Label(priority_col, text="Priority: *").pack(anchor="w")
        self.priority_var = tk.StringVar()
        priority_combo = ttk.Combobox(priority_col, textvariable=self.priority_var, state='readonly', width=25)
        priority_combo['values'] = self.queue.get_priorities()
        priority_combo.current(1)  # Default to 'high'
        priority_combo.pack(fill="x")

        # Task Type
        type_col = ttk.Frame(priority_type_frame)
        type_col.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ttk.Label(type_col, text="Task Type: *").pack(anchor="w")
        self.task_type_var = tk.StringVar()
        task_type_combo = ttk.Combobox(type_col, textvariable=self.task_type_var, state='readonly', width=25)
        task_type_combo['values'] = list(self.task_types_map.values())
        task_type_combo.current(0)
        task_type_combo.pack(fill="x")

        # Source File
        ttk.Label(main_frame, text="Source File: *").pack(anchor="w")
        source_frame = ttk.Frame(main_frame)
        source_frame.pack(fill="x", pady=(0, 5))

        self.source_var = tk.StringVar()
        self.source_entry = ttk.Entry(source_frame, textvariable=self.source_var)
        self.source_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(source_frame, text="Browse...", command=self.browse_source).pack(side="left", padx=(5, 0))

        self.source_var.trace_add('write', lambda *args: self.validate_source_file())

        self.source_validation_label = ttk.Label(main_frame, text="", font=('Arial', 9))
        self.source_validation_label.pack(anchor="w", pady=(0, 10))

        # Prompt
        prompt_label_frame = ttk.Frame(main_frame)
        prompt_label_frame.pack(fill="x", anchor="w")
        ttk.Label(prompt_label_frame, text="Task Description: *").pack(side="left")
        ttk.Button(prompt_label_frame, text="Generate with AI", command=self.generate_prompt).pack(side="right")

        self.description_text = tk.Text(main_frame, height=8, wrap="word")
        self.description_text.pack(fill="both", expand=True, pady=(0, 10))

        # Automation options
        options_frame = ttk.LabelFrame(main_frame, text="Automation Options", padding=10)
        options_frame.pack(fill="x", pady=(0, 10))

        self.auto_complete_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Auto Complete (complete without prompting)",
            variable=self.auto_complete_var
        ).pack(anchor="w")

        self.auto_chain_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Auto Chain (automatically progress to next agent)",
            variable=self.auto_chain_var
        ).pack(anchor="w")

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Create Task", command=self.create_task).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Create & Start", command=self.create_and_start).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side="left", padx=5)

        # Set initial focus
        self.dialog.after(100, self.title_entry.focus_set)

        # Trigger initial agent selection
        if self.agent_combo['values']:
            self.on_agent_selected()

    def on_agent_selected(self, event=None):
        """Handle agent selection - show skills."""
        agent_display = self.agent_var.get()
        agent_key = self.get_agent_key(agent_display)

        if not agent_key:
            return

        # Get agent's skills
        skills = self.queue.get_agent_skills(agent_key)

        # Update skills display
        for widget in self.skills_frame.winfo_children():
            widget.destroy()

        if skills:
            ttk.Label(
                self.skills_frame,
                text=f"This agent has {len(skills)} skill(s) available:",
                font=('Arial', 9, 'bold')
            ).pack(anchor="w", pady=(0, 5))

            # Get skill names from skills.json
            skills_data = self.queue.get_skills_list()
            if skills_data:
                for skill_dir in skills:
                    skill_info = next(
                        (s for s in skills_data.get('skills', []) 
                         if s.get('skill-directory') == skill_dir),
                        None
                    )
                    if skill_info:
                        name = skill_info.get('name', skill_dir)
                        category = skill_info.get('category', 'unknown')
                        ttk.Label(
                            self.skills_frame,
                            text=f"  • {name} ({category})",
                            font=('Arial', 9)
                        ).pack(anchor="w", pady=1)

            # Preview button
            self.preview_btn = ttk.Button(
                self.skills_frame,
                text="📄 Preview Full Skills Prompt",
                command=self.preview_skills_prompt
            )
            self.preview_btn.pack(anchor="w", pady=(10, 0))

        else:
            ttk.Label(
                self.skills_frame,
                text="This agent has no skills assigned",
                font=('Arial', 9),
                foreground='gray'
            ).pack(anchor="w")

        # Update contract info
        contract = self.queue.get_agent_contract(agent_key)
        if contract:
            # Could show expected outputs, etc.
            pass

        # Trigger source validation
        self.validate_source_file()

    def preview_skills_prompt(self):
        """Show preview of skills that will be injected into agent prompt."""
        agent_display = self.agent_var.get()
        agent_key = self.get_agent_key(agent_display)

        if not agent_key:
            return

        try:
            skills_prompt = self.queue.get_skills_prompt(agent_key)

            if not skills_prompt:
                messagebox.showinfo("No Skills", "This agent has no skills assigned.")
                return

            # Create preview window
            preview = tk.Toplevel(self.dialog)
            preview.title(f"Skills Prompt Preview: {agent_display}")
            preview.geometry("800x600")
            preview.transient(self.dialog)

            # Text widget with scrollbar
            text_frame = ttk.Frame(preview, padding=10)
            text_frame.pack(fill="both", expand=True)

            text_widget = tk.Text(text_frame, wrap="word", font=('Courier', 9))
            scroll = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scroll.set)

            text_widget.pack(side="left", fill="both", expand=True)
            scroll.pack(side="right", fill="y")

            text_widget.insert('1.0', skills_prompt)
            text_widget.config(state=tk.DISABLED)

            ttk.Button(preview, text="Close", command=preview.destroy).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load skills prompt: {e}")

    def on_workflow_selected(self, event=None):
        """Handle workflow selection from dropdown."""
        workflow = self.workflow_var.get()

        if workflow == "(none)":
            return

        # Map workflow names to agent and settings
        workflow_map = {
            "📋 Full Feature": ("requirements-analyst", "Complete development workflow", "high"),
            "🐛 Bug Fix": ("requirements-analyst", "Bug fix (skip documentation)", "high"),
            "🔥 Hotfix": ("implementer", "Emergency fix (skip analysis)", "critical"),
            "🔧 Refactoring": ("architect", "Code improvement (skip requirements)", "normal")
        }

        if workflow in workflow_map:
            agent, description, priority = workflow_map[workflow]
            self.quick_start_workflow(agent, description, priority)

    def quick_start_workflow(self, agent: str, description: str, priority: str):
        """Quick start a workflow with pre-filled values."""
        # Set form values
        agent_name = self.agents_map.get(agent, agent)
        self.agent_var.set(agent_name)
        self.on_agent_selected()  # Update skills display

        self.priority_var.set(priority)

        # Set appropriate task type based on agent
        task_type_map = {
            'requirements-analyst': 'analysis',
            'architect': 'technical_analysis',
            'implementer': 'implementation',
            'tester': 'testing',
            'documenter': 'documentation'
        }
        task_type = task_type_map.get(agent, 'analysis')
        self.task_type_var.set(self.task_types_map.get(task_type, 'Analysis'))

        # Enable automation
        self.auto_complete_var.set(True)
        self.auto_chain_var.set(True)

        # Set description
        self.description_text.delete('1.0', tk.END)
        self.description_text.insert('1.0', f"Quick workflow: {description}\n\nThis workflow will automatically progress through all phases.")

        # Focus on title for user to fill in
        self.title_entry.focus_set()

    def validate_source_file(self):
        """Validate source file against agent's expected pattern."""
        agent_display = self.agent_var.get()
        source_file = self.source_var.get().strip()

        if not agent_display or not source_file:
            self.source_validation_label.config(text="", foreground='black')
            return

        agent_key = self.get_agent_key(agent_display)
        is_valid, message = self.queue.validate_source_file_pattern(agent_key, source_file)

        if is_valid:
            self.source_validation_label.config(text=message, foreground='green')
        else:
            self.source_validation_label.config(text=message, foreground='orange')

    def browse_source(self):
        """Browse for source file."""
        filename = filedialog.askopenfilename(
            parent=self.dialog,
            title="Select Source File",
            initialdir=str(self.queue.project_root),
            filetypes=[("Markdown", "*.md"), ("All Files", "*.*")]
        )

        if filename:
            try:
                rel_path = Path(filename).relative_to(self.queue.project_root)
                self.source_var.set(str(rel_path))
            except ValueError:
                self.source_var.set(filename)

    def generate_prompt(self):
        """Generate task description using Claude API."""
        title = self.title_var.get().strip()
        source_file = self.source_var.get().strip()

        if not title:
            messagebox.showwarning("Missing Title", "Please enter a task title first.")
            return

        if not source_file:
            messagebox.showwarning("Missing Source", "Please select a source file first.")
            return

        api_key = self.settings.get_claude_api_key() if self.settings else None
        if not api_key:
            messagebox.showwarning("No API Key", "Claude API key not configured in Settings menu.")
            return

        # Build context
        agent_display = self.agent_var.get()
        agent_key = self.get_agent_key(agent_display)
        task_type_display = self.task_type_var.get()
        task_type = self.get_task_type_key(task_type_display)

        context_parts = [f"Task Title: {title}"]
        
        if task_type:
            context_parts.append(f"Task Type: {task_type}")
        
        if agent_display:
            context_parts.append(f"Agent: {agent_display}")
            
            # Include agent skills in context
            skills = self.queue.get_agent_skills(agent_key)
            if skills:
                context_parts.append(f"Agent has these skills available: {', '.join(skills)}")

        context_parts.append(f"Source File: {source_file}")

        # Try to read source file
        try:
            source_path = Path(source_file)
            if not source_path.is_absolute():
                source_path = self.queue.project_root / source_path

            if source_path.exists():
                with open(source_path, 'r') as f:
                    content = f.read()
                    if len(content) > 2000:
                        content = content[:2000] + "\n...[truncated]"
                    context_parts.append(f"\nSource File Content:\n{content}")
        except Exception as e:
            print(f"Could not read source: {e}")

        # Show progress
        progress = tk.Toplevel(self.dialog)
        progress.title("Generating Description")
        progress.geometry("350x100")
        progress.transient(self.dialog)
        progress.grab_set()

        progress_frame = ttk.Frame(progress, padding=20)
        progress_frame.pack(fill="both", expand=True)

        ttk.Label(progress_frame, text="Calling Claude API...", font=('Arial', 10)).pack(pady=(0, 10))
        progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate', length=250)
        progress_bar.pack()
        progress_bar.start()
        progress.update()

        try:
            generated = self.call_claude_api("\n".join(context_parts))
            progress.destroy()
            
            self.description_text.delete('1.0', tk.END)
            self.description_text.insert('1.0', generated)

        except Exception as e:
            progress.destroy()
            messagebox.showerror("API Error", f"Failed to generate: {e}")

    def call_claude_api(self, context_prompt: str) -> str:
        """Call Claude API to generate task description."""
        api_key = self.settings.get_claude_api_key()

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        system_prompt = """You are an expert at creating detailed, actionable task descriptions for software development.
Generate ONLY the task description content without conversational framing.

Include:
- Clear goals and objectives
- Expected deliverables
- Technical requirements
- Acceptance criteria"""

        data = {
            "model": "claude-sonnet-4-5-20250929",
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [{"role": "user", "content": context_prompt}]
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

    def get_agent_key(self, display_name: str) -> str:
        """Convert agent display name to agent-file key."""
        for key, value in self.agents_map.items():
            if value == display_name:
                return key
        return display_name

    def get_task_type_key(self, display_name: str) -> str:
        """Convert task type display name to internal key."""
        for key, value in self.task_types_map.items():
            if value == display_name:
                return key
        return display_name

    def create_task(self):
        """Create the task."""
        # Validate
        title = self.title_var.get().strip()
        agent_display = self.agent_var.get()
        priority = self.priority_var.get()
        task_type_display = self.task_type_var.get()
        source_file = self.source_var.get().strip()
        description = self.description_text.get('1.0', tk.END).strip()

        if not all([title, agent_display, priority, task_type_display, source_file, description]):
            messagebox.showwarning("Validation Error", "All fields are required.")
            return

        # Convert to keys
        agent = self.get_agent_key(agent_display)
        task_type = self.get_task_type_key(task_type_display)

        # Validate source exists
        source_path = Path(source_file)
        if not source_path.is_absolute():
            source_path = self.queue.project_root / source_path

        if not source_path.exists():
            messagebox.showerror("File Not Found", f"Source file does not exist: {source_file}")
            return

        try:
            task_id = self.queue.add_task(
                title=title,
                agent=agent,
                priority=priority,
                task_type=task_type,
                source_file=source_file,
                description=description,
                auto_complete=self.auto_complete_var.get(),
                auto_chain=self.auto_chain_var.get()
            )
            self.result = task_id
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create task: {e}")

    def create_and_start(self):
        """Create task and mark to start immediately."""
        self.should_start = True
        self.create_task()

    def cancel(self):
        """Cancel dialog."""
        self.result = None
        self.dialog.destroy()
