"""
Create task dialog for adding new tasks to the queue.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json
import urllib.request
import urllib.error


class CreateTaskDialog:
    """Dialog for creating a new task."""

    def __init__(self, parent, queue_interface, settings=None):
        self.queue = queue_interface
        self.settings = settings
        self.result = None
        self.should_start = False  # Track if "Create & Start" was clicked

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Task")
        self.dialog.geometry("600x650")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.build_ui()

        # Wait for dialog to close
        self.dialog.wait_window()

    def build_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="Title: *").pack(anchor=tk.W)
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(main_frame, textvariable=self.title_var)
        self.title_entry.pack(fill=tk.X, pady=(0, 10))

        # Agent
        ttk.Label(main_frame, text="Agent: *").pack(anchor=tk.W)
        self.agent_var = tk.StringVar()
        agent_combo = ttk.Combobox(main_frame, textvariable=self.agent_var, state='readonly')

        # Get agent dictionary (agent-file -> name)
        try:
            self.agents_map = self.queue.get_agent_list()
            # print(f"DEBUG: Agents map: {self.agents_map}")  # DEBUG: Commented out
            agent_combo['values'] = list(self.agents_map.values())
            if agent_combo['values']:
                agent_combo.current(0)
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

        agent_combo.pack(fill=tk.X, pady=(0, 10))

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

        # Get task types dictionary (key: internal value, value: display name)
        self.task_types_map = self.queue.get_task_types()
        task_type_combo['values'] = list(self.task_types_map.values())
        task_type_combo.current(0)  # Default to first item
        task_type_combo.pack(fill=tk.X, pady=(0, 10))

        # Source File
        ttk.Label(main_frame, text="Source File: *").pack(anchor=tk.W)

        source_frame = ttk.Frame(main_frame)
        source_frame.pack(fill=tk.X, pady=(0, 10))

        self.source_var = tk.StringVar()
        ttk.Entry(source_frame, textvariable=self.source_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(source_frame, text="Browse...", command=self.browse_source).pack(side=tk.LEFT, padx=(5, 0))

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
        self.dialog.after(0, self.set_initial_focus)

    def set_initial_focus(self):
        """Set focus to the title entry field."""
        self.title_entry.focus_set()

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
Do not include phrases like "Here's a description" or "I'll create" - output only the task description itself.

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
        agent = self.agent_var.get()
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
        task_type = self.get_task_type_key(task_type_display)

        # Build context for generation
        context_parts = []
        context_parts.append(f"Task Title: {title}")

        if task_type:
            task_type_descriptions = {
                "analysis": "Analysis task focused on understanding and documenting code or requirements",
                "technical_analysis": "Technical analysis requiring deep investigation and design decisions",
                "implementation": "Implementation task requiring code changes and development work",
                "testing": "Testing task requiring test creation, execution, and validation"
            }
            if task_type in task_type_descriptions:
                context_parts.append(f"Task Type: {task_type_descriptions[task_type]}")

        if agent:
            context_parts.append(f"Assigned Agent: {agent}")

        if priority:
            context_parts.append(f"Priority: {priority}")

        context_parts.append(f"Source File: {source_file}")

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
                # print(f"Claude API call failed: {e}")  # DEBUG: Commented out
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
                "testing": "This is a testing task requiring test creation, execution, and validation."
            }
            if task_type in task_type_descriptions:
                prompt_parts.append(f"{task_type_descriptions[task_type]}\n")

        if agent:
            prompt_parts.append(f"Assigned Agent: {agent}\n")

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

            # Debug output
            # import sys  # DEBUG: Commented out
            # print(f"DEBUG create_task: auto_complete={auto_complete}, auto_chain={auto_chain}", file=sys.stderr)  # DEBUG: Commented out
            # print(f"DEBUG create_task: auto_complete={auto_complete}, auto_chain={auto_chain}")  # DEBUG: Commented out

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