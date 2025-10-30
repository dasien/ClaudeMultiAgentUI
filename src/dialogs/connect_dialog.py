"""
Connect dialog for selecting a v3.0 CMAT project.
Validates v3.0 structure including cmat.sh, skills, and contracts.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path


class ConnectDialog:
    """Dialog for connecting to a v3.0 CMAT project."""

    def __init__(self, parent):
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Connect to Project")
        self.dialog.geometry("700x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.build_ui()
        self.dialog.wait_window()

    def build_ui(self):
        """Build UI."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Instructions
        ttk.Label(
            main_frame,
            text="Select the project root directory containing .claude/ folder:",
            wraplength=650
        ).pack(anchor=tk.W, pady=(0, 10))

        # Path selection
        path_frame = ttk.LabelFrame(main_frame, text="Project Directory", padding=10)
        path_frame.pack(fill=tk.X, pady=(0, 20))

        entry_frame = ttk.Frame(path_frame)
        entry_frame.pack(fill=tk.X)

        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(entry_frame, textvariable=self.path_var)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(entry_frame, text="Browse...", command=self.browse).pack(side=tk.LEFT, padx=(5, 0))

        # Validation frame
        self.validation_frame = ttk.LabelFrame(main_frame, text="System Validation", padding=10)
        self.validation_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Validation items
        self.validation_items = {
            'project_root': ttk.Label(self.validation_frame, text="○ Project root directory", foreground='gray'),
            'cmat_script': ttk.Label(self.validation_frame, text="○ CMAT script (.claude/scripts/cmat.sh)",
                                     foreground='gray'),
            'queue_file': ttk.Label(self.validation_frame, text="○ Task queue (.claude/queues/task_queue.json)",
                                    foreground='gray'),
            'contracts': ttk.Label(self.validation_frame, text="○ Agent contracts (.claude/AGENT_CONTRACTS.json)",
                                   foreground='gray'),
            'skills': ttk.Label(self.validation_frame, text="○ Skills system (.claude/skills/skills.json)",
                                foreground='gray'),
            'agents': ttk.Label(self.validation_frame, text="○ Agents (.claude/agents/agents.json)", foreground='gray'),
        }

        for label in self.validation_items.values():
            label.pack(anchor=tk.W, pady=3)

        # Version info
        self.version_label = ttk.Label(
            self.validation_frame,
            text="",
            font=('Arial', 9, 'bold'),
            foreground='blue'
        )
        self.version_label.pack(anchor=tk.W, pady=(10, 0))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        self.connect_btn = ttk.Button(
            button_frame,
            text="Connect",
            command=self.connect,
            state=tk.DISABLED
        )
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)

        # Trace path changes
        self.path_var.trace_add('write', lambda *args: self.validate_path())

    def browse(self):
        """Browse for project directory."""
        directory = filedialog.askdirectory(
            parent=self.dialog,
            title="Select Project Root Directory",
            mustexist=True
        )

        if directory:
            self.path_var.set(directory)

    def validate_path(self):
        """Validate selected path for v3.0 compatibility."""
        path_str = self.path_var.get()

        if not path_str:
            self.connect_btn.config(state=tk.DISABLED)
            return

        project_root = Path(path_str)

        # Validation checks
        checks = {
            'project_root': project_root.exists() and project_root.is_dir(),
            'cmat_script': (project_root / ".claude/scripts/cmat.sh").exists(),
            'queue_file': (project_root / ".claude/queues/task_queue.json").exists(),
            'contracts': (project_root / ".claude/AGENT_CONTRACTS.json").exists(),
            'skills': (project_root / ".claude/skills/skills.json").exists(),
            'agents': (project_root / ".claude/agents/agents.json").exists(),
        }

        # Update validation labels
        for key, is_valid in checks.items():
            label = self.validation_items[key]
            if is_valid:
                label.config(text=f"✓ {label.cget('text')[2:]}", foreground='green')
            else:
                label.config(text=f"✗ {label.cget('text')[2:]}", foreground='red')

        # Determine if this is a valid v3.0 project
        required_v3 = ['project_root', 'cmat_script', 'contracts', 'skills']
        is_v3_valid = all(checks[k] for k in required_v3)

        # Optional but recommended
        optional = ['queue_file', 'agents']
        has_optional = all(checks[k] for k in optional)

        # Update version label
        if is_v3_valid:
            if has_optional:
                self.version_label.config(text="✓ Valid CMAT v3.0 Project", foreground='green')
                self.connect_btn.config(state=tk.NORMAL)
            else:
                self.version_label.config(
                    text="⚠ Valid v3.0 structure (queue/agents will be created)",
                    foreground='orange'
                )
                self.connect_btn.config(state=tk.NORMAL)
        else:
            # Check if it's an older version
            if (project_root / ".claude/queues/queue_manager.sh").exists():
                self.version_label.config(
                    text="✗ This appears to be v2.0 or earlier - please upgrade template first",
                    foreground='red'
                )
            else:
                self.version_label.config(
                    text="✗ Not a valid CMAT v3.0 project",
                    foreground='red'
                )
            self.connect_btn.config(state=tk.DISABLED)

    def connect(self):
        """Connect to project."""
        project_root = Path(self.path_var.get())
        cmat_script = project_root / ".claude/scripts/cmat.sh"

        # Return path to cmat.sh
        self.result = str(cmat_script)
        self.dialog.destroy()

    def cancel(self):
        """Cancel dialog."""
        self.result = None
        self.dialog.destroy()