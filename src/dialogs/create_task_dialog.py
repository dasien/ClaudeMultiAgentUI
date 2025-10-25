"""
Create task dialog for adding new tasks to the queue.
Enhanced for v2.0 with contract information and validation.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json
import urllib.request
import urllib.error


class CreateTaskDialog:
    """Dialog for creating a new task with v2.0 contract support."""

    def __init__(self, parent, queue_interface, settings=None):
        self.queue = queue_interface
        self.settings = settings
        self.result = None
        self.should_start = False  # Track if "Create & Start" was clicked

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Task")
        self.dialog.geometry("700x800")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # Check if v2.0 compatible
        self.is_v2 = self.queue.is_v2_compatible()

        self.build_ui()

        # Wait for dialog to close
        self.dialog.wait_window()

    def build_ui(self):
        # Main frame with scrollbar support
        main_canvas = tk.Canvas(self.dialog)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.dialog, orient=tk.VERTICAL, command=main_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        main_canvas.configure(yscrollcommand=scrollbar.set)
        main_canvas.bind('<Configure>', lambda e: main_canvas.configure(scrollregion=main_canvas.bbox('all')))

        main_frame = ttk.Frame(main_canvas, padding=20)
        main_canvas.create_window((0, 0), window=main_frame, anchor='nw')

        # Title
        ttk.Label(main_frame, text="Title: *").pack(anchor=tk.W)
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(main_frame, textvariable=self.title_var)
        self.title_entry.pack(fill=tk.X, pady=(0, 10))

        # Agent
        ttk.Label(main_frame, text="Agent: *").pack(anchor=tk.W)
        self.agent_var = tk.StringVar()
        self.agent_combo = ttk.Combobox(main_frame, textvariable=self.agent_var, state='readonly')

        # Get agent dictionary (agent-file -> name)
        try:
            self.agents_map = self.queue.get_agent_list()
            self.agent_combo['values'] = list(self.agents_map.values())
            if self.agent_combo['values']:
                self.agent_combo.current(0)
        except FileNotFoundError as e:
            messagebox.showerror(
                "Agents File Not Found",
                f"Could not find agents.json file:\n\n{e}\n\n"
                f"Expected location: {self.queue.project_root}/.claude/agents/agents.json"
            )
            self.dialog.destroy()
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load agents: {e}")
            self.dialog.destroy()
            return

        self.agent_combo.pack(fill=tk.X, pady=(0, 10))

        # Bind agent selection to update contract info
        self.agent_combo.bind('<<ComboboxSelected>>', self.on_agent_selected)

        # Contract Info Frame (v2.0 only)
        if self.is_v2:
            self.contract_frame = ttk.LabelFrame(main_frame, text="Agent Contract Info", padding=10)
            self.contract_frame.pack(fill=tk.X, pady=(0, 10))

            self.contract_input_label = ttk.Label(self.contract_frame, text="Expected Input: (not selected)", foreground='gray')
            self.contract_input_label.pack(anchor=tk.W, pady=2)

            self.contract_output_label = ttk.Label(self.contract_frame, text="Output: (not selected)", foreground='gray')
            self.contract_output_label.pack(anchor=tk.W, pady=2)

            self.contract_status_label = ttk.Label(self.contract_frame, text="Success Status: (not selected)", foreground='gray')
            self.contract_status_label.pack(anchor=tk.W, pady=2)

            self.contract_next_label = ttk.Label(self.contract_frame, text="Next Agent: (not selected)", foreground='gray')
            self.contract_next_label.pack(anchor=tk.W, pady=2)

        # Priority
        ttk.Label(main_frame, text="Priority: *").pack(anchor=tk.W)
        self.priority_var = tk.StringVar()
        priority_combo = ttk.Combobox(main_frame, textvariable=self.priority_var, state='readonly')
        priority_combo['values'] = self.queue.get_priorities()
        priority_combo.current(1)  # Default to 'high'
        priority_combo.pack(fill=tk.X, pady=(0, 10))

        # Task Type
        ttk.Label(main_frame, text="Task Type: *").pack(anchor=tk.W)
        self.task_type_var = tk.StringVar()
        task_type_combo = ttk.Combobox(main_frame, textvariable=self.task_type_var, state='readonly')

        # Get task types dictionary
        self.task_types_map = self.queue.get_task_types()
        task_type_combo['values'] = list(self.task_types_map.values())
        task_type_combo.current(0)  # Default to first item
        task_type_combo.pack(fill=tk.X, pady=(0, 10))

        # Source File
        ttk.Label(main_frame, text="Source File: *").pack(anchor=tk.W)

        source_frame = ttk.Frame(main_frame)
        source_frame.pack(fill=tk.X, pady=(0, 5))

        self.source_var = tk.StringVar()
        self.source_entry = ttk.Entry(source_frame, textvariable=self.source_var)
        self.source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(source_frame, text="Browse...", command=self.browse_source).pack(side=tk.LEFT, padx=(5, 0))

        # Bind source file changes to validation
        self.source_var.trace_add('write', lambda *args: self.validate_source_file())

        # Source file validation label (v2.0 only)
        if self.is_v2:
            self.source_validation_label = ttk.Label(main_frame, text="", font=('Arial', 9))
            self.source_validation_label.pack(anchor=tk.W, pady=(0, 10))
        else:
            # Add spacing
            ttk.Label(main_frame, text="").pack(pady=(0, 10))

        # Prompt
        prompt_label_frame = ttk.Frame(main_frame)
        prompt_label_frame.pack(fill=tk.X, anchor=tk.W)
        ttk.Label(prompt_label_frame, text="Prompt: *").pack(side=tk.LEFT)
        ttk.Button(prompt_label_frame, text="Generate", command=self.generate_prompt).pack(side=tk.RIGHT)

        self.description_text = tk.Text(main_frame, height=8, wrap=tk.WORD)
        self.description_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Options frame for checkboxes
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        self.auto_complete_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Auto Complete", variable=self.auto_complete_var).pack(side=tk.LEFT, padx=(0, 10))

        self.auto_chain_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Auto Chain", variable=self.auto_chain_var).pack(side=tk.LEFT)

        # Required fields note
        ttk.Label(main_frame, text="* Required fields", font=('Arial', 9), foreground='gray').pack(anchor=tk.W)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Create Task", command=self.create_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Create & Start", command=self.create_and_start).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)

        # Set focus to title field after window is initialized
        self.dialog.after(100, self.set_initial_focus)

    def set_initial_focus(self):
        """Set focus to the title entry field."""
        self.title_entry.focus_set()

    def on_agent_selected(self, event=None):
        """Handle agent selection and update contract info."""
        if not self.is_v2:
            return

        agent_display = self.agent_var.get()
        agent_key = self.get_agent_key(agent_display)

        if not agent_key:
            return

        contract = self.queue.get_agent_contract(agent_key)
        if not contract:
            self.contract_input_label.config(text="Expected Input: No contract found", foreground='gray')
            self.contract_output_label.config(text="Output: No contract found", foreground='gray')
            self.contract_status_label.config(text="Success Status: No contract found", foreground='gray')
            self.contract_next_label.config(text="Next Agent: No contract found", foreground='gray')
            return

        # Update contract info labels
        required_inputs = contract.get('inputs', {}).get('required', [])
        if required_inputs:
            input_pattern = required_inputs[0].get('pattern', 'Not specified')
            self.contract_input_label.config(text=f"Expected Input: {input_pattern}", foreground='blue')
        else:
            self.contract_input_label.config(text="Expected Input: Not specified", foreground='gray')

        outputs = contract.get('outputs', {})
        output_dir = outputs.get('output_directory', 'unknown')
        root_doc = outputs.get('root_document', 'unknown')
        self.contract_output_label.config(
            text=f"Output: {output_dir}/{root_doc}",
            foreground='blue'
        )

        success_statuses = contract.get('statuses', {}).get('success', [])
        if success_statuses:
            status_codes = [s.get('code') for s in success_statuses]
            self.contract_status_label.config(
                text=f"Success Status: {', '.join(status_codes)}",
                foreground='blue'
            )

            # Get next agents from first success status
            next_agents = success_statuses[0].get('next_agents', [])
            if next_agents:
                self.contract_next_label.config(
                    text=f"Next Agent: {', '.join(next_agents)}",
                    foreground='blue'
                )
            else:
                self.contract_next_label.config(text="Next Agent: None (workflow complete)", foreground='gray')
        else:
            self.contract_status_label.config(text="Success Status: Not specified", foreground='gray')
            self.contract_next_label.config(text="Next Agent: Not specified", foreground='gray')

        # Trigger source validation in case agent changed
        self.validate_source_file()

    def validate_source_file(self):
        """Validate source file against agent's expected pattern."""
        if not self.is_v2:
            return

        agent_display = self.agent_var.get()
        source_file = self.source_var.get().strip()

        if not agent_display or not source_file:
            self.source_validation_label.config(text="", foreground='black')
            return

        agent_key = self.get_agent_key(agent_display)
        if not agent_key:
            return

        is_valid, message = self.queue.validate_source_file_pattern(agent_key, source_file)

        if is_valid:
            self.source_validation_label.config(text=message, foreground='green')
        else:
            self.source_validation_label.config(text=message, foreground='orange')

    def call_claude_api(self, context_prompt: str) -> str:
        """Call Claude API to generate a task description.

        Args:
            context_prompt: The context to send to Claude

        Returns:
            Generated task description

        Raises:
            Exception: If API call fails
        """
        api_key = self.settings.get_claude_api_key() if self.settings else None
        if not api_key:
            raise Exception("No API key configured")

        # Prepare API request
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        # Create the prompt for Claude
        system_prompt = """You are an expert at creating detailed, actionable task descriptions for software development work.
Generate ONLY the task description content without any conversational framing, preamble, or meta-commentary.
Do not include phrases like "Here's a description" or "I'll create" - output only the content itself.

The task description should include:
- Clear goals and objectives
- Expected deliverables
- Technical requirements and constraints
- Acceptance criteria

Be specific, actionable, and focus on what needs to be done."""

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

        # Make request
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
        """Convert agent display name to agent-file key.

        Args:
            display_name: The display name from the combobox

        Returns:
            The agent-file key value
        """
        for key, value in self.agents_map.items():
            if value == display_name:
                return key
        return display_name  # Fallback to display name if not found

    def get_task_type_key(self, display_name: str) -> str:
        """Convert task type display name to internal key.

        Args:
            display_name: The display name from the combobox

        Returns:
            The internal key value
        """
        for key, value in self.task_types_map.items():
            if value == display_name:
                return key
        return display_name  # Fallback to display name if not found

    def generate_prompt(self):
        """Generate a task description prompt based on current form values."""
        title = self.title_var.get().strip()
        agent_display = self.agent_var.get()
        priority = self.priority_var.get()
        task_type_display = self.task_type_var.get()
        source_file = self.source_var.get().strip()

        # Check if required fields are filled
        if not title:
            messagebox.showwarning("Missing Title", "Please enter a task title first.")
            return

        if not source_file:
            messagebox.showwarning("Missing Source File", "Please select a source file first.")
            return

        # Convert display name to internal key
        agent_key = self.get_agent_key(agent_display)
        task_type = self.get_task_type_key(task_type_display)

        # Build context for generation
        context_parts = []
        context_parts.append(f"Task Title: {title}")

        if task_type:
            task_type_descriptions = {
                "analysis": "Analysis task focused on understanding and documenting code or requirements",
                "technical_analysis": "Technical analysis requiring deep investigation and design decisions",
                "implementation": "Implementation task requiring code changes and development work",
                "testing": "Testing task requiring test creation, execution, and validation",
                "documentation": "Documentation task for creating or updating project documentation"
            }
            if task_type in task_type_descriptions:
                context_parts.append(f"Task Type: {task_type_descriptions[task_type]}")

        if agent_display:
            context_parts.append(f"Assigned Agent: {agent_display}")

        if priority:
            context_parts.append(f"Priority: {priority}")

        context_parts.append(f"Source File: {source_file}")

        # Add contract info if v2.0
        if self.is_v2 and agent_key:
            contract = self.queue.get_agent_contract(agent_key)
            if contract:
                expected_output = self.queue.get_expected_output_path(agent_key, source_file)
                if expected_output:
                    context_parts.append(f"Expected Output: {expected_output}")

        # Try to read source file for context
        source_content = None
        try:
            source_path = Path(source_file)
            if not source_path.is_absolute():
                source_path = self.queue.project_root / source_path

            if source_path.exists():
                with open(source_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Limit context size
                    if len(content) > 2000:
                        source_content = content[:2000] + "\n...[truncated]"
                    else:
                        source_content = content
        except Exception as e:
            print(f"Could not read source file: {e}")

        if source_content:
            context_parts.append(f"\nSource File Content:\n{source_content}")

        context_prompt = "\n".join(context_parts)

        # Try Claude API if available
        api_key = self.settings.get_claude_api_key() if self.settings else None

        if api_key:
            # Show loading indicator
            progress = tk.Toplevel(self.dialog)
            progress.title("Generating Description")
            progress.geometry("350x100")
            progress.transient(self.dialog)
            progress.grab_set()

            # Add frame with proper background
            progress_frame = ttk.Frame(progress, padding=20)
            progress_frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(progress_frame, text="Calling Claude API...", font=('Arial', 10)).pack(pady=(0, 10))
            progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate', length=250)
            progress_bar.pack(pady=(0, 10))
            progress_bar.start()
            progress.update()

            try:
                # Call Claude API
                generated_description = self.call_claude_api(context_prompt)
                progress.destroy()

                # Set the generated description
                self.description_text.delete('1.0', tk.END)
                self.description_text.insert('1.0', generated_description)
                return

            except Exception as e:
                progress.destroy()
                # Fall through to template-based generation
                messagebox.showinfo(
                    "API Error",
                    f"Could not reach Claude API: {str(e)}\n\nUsing template-based generation instead."
                )

        # Fallback: Generate template-based prompt
        prompt_parts = []
        prompt_parts.append(f"Task: {title}\n")

        if task_type:
            task_type_descriptions = {
                "analysis": "This is an analysis task focused on understanding and documenting code or requirements.",
                "technical_analysis": "This is a technical analysis task requiring deep technical investigation and design decisions.",
                "implementation": "This is an implementation task requiring code changes and development work.",
                "testing": "This is a testing task requiring test creation, execution, and validation.",
                "documentation": "This is a documentation task for creating or updating project documentation."
            }
            if task_type in task_type_descriptions:
                prompt_parts.append(f"{task_type_descriptions[task_type]}\n")

        if agent_display:
            prompt_parts.append(f"Assigned Agent: {agent_display}\n")

        prompt_parts.append(f"Source File: {source_file}\n")

        if source_content:
            if len(source_content) > 500:
                prompt_parts.append(f"\nSource File Preview:\n{source_content[:500]}...\n")
            else:
                prompt_parts.append(f"\nSource File Content:\n{source_content}\n")

        if priority:
            prompt_parts.append(f"\nPriority: {priority}")

        prompt_parts.append("\n\nPlease provide a detailed description of what needs to be accomplished in this task, including:")
        prompt_parts.append("- Specific goals and objectives")
        prompt_parts.append("- Expected deliverables")
        prompt_parts.append("- Any constraints or requirements")
        prompt_parts.append("- Acceptance criteria")

        generated_prompt = "\n".join(prompt_parts)
        self.description_text.delete('1.0', tk.END)
        self.description_text.insert('1.0', generated_prompt)

    def browse_source(self):
        filename = filedialog.askopenfilename(
            parent=self.dialog,
            title="Select Source File",
            initialdir=str(self.queue.project_root),
            filetypes=[
                ("Markdown", "*.md"),
                ("All Files", "*.*")
            ]
        )

        if filename:
            # Make relative to project root if possible
            try:
                rel_path = Path(filename).relative_to(self.queue.project_root)
                self.source_var.set(str(rel_path))
            except ValueError:
                self.source_var.set(filename)

    def create_task(self):
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

        # Convert display names to internal keys
        agent = self.get_agent_key(agent_display)
        task_type = self.get_task_type_key(task_type_display)

        # Validate source file exists
        source_path = Path(source_file)
        if not source_path.is_absolute():
            source_path = self.queue.project_root / source_path

        if not source_path.exists():
            messagebox.showerror("File Not Found", f"Source file does not exist: {source_file}")
            return

        # Create task
        try:
            # Get checkbox values
            auto_complete = self.auto_complete_var.get()
            auto_chain = self.auto_chain_var.get()

            task_id = self.queue.add_task(
                title=title,
                agent=agent,
                priority=priority,
                task_type=task_type,
                source_file=source_file,
                description=description,
                auto_complete=auto_complete,
                auto_chain=auto_chain
            )
            self.result = task_id
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create task: {e}")

    def create_and_start(self):
        """Create task and mark it to be started immediately."""
        self.should_start = True
        self.create_task()

    def cancel(self):
        self.result = None
        self.dialog.destroy()