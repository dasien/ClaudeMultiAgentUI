"""
Connect dialog for selecting a queue manager.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path


class ConnectDialog:
    """Dialog for connecting to a queue manager."""

    def __init__(self, parent):
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Connect to Queue Manager")
        self.dialog.geometry("600x300")
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
        # Instructions
        ttk.Label(
            self.dialog,
            text="Select the project root directory (containing .claude folder):",
            wraplength=550
        ).pack(pady=10, padx=20)

        # Script path
        path_frame = ttk.Frame(self.dialog)
        path_frame.pack(fill=tk.X, padx=20, pady=5)

        ttk.Label(path_frame, text="Project Root Directory:").pack(anchor=tk.W)

        entry_frame = ttk.Frame(path_frame)
        entry_frame.pack(fill=tk.X, pady=5)

        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(entry_frame, textvariable=self.path_var)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(entry_frame, text="Browse...", command=self.browse).pack(side=tk.LEFT, padx=(5, 0))

        # Validation frame
        self.validation_frame = ttk.LabelFrame(self.dialog, text="Validation", padding=10)
        self.validation_frame.pack(fill=tk.X, padx=20, pady=10)

        self.project_root_label = ttk.Label(self.validation_frame, text="Project Root: ")
        self.project_root_label.pack(anchor=tk.W)

        self.queue_file_label = ttk.Label(self.validation_frame, text="Queue File: ")
        self.queue_file_label.pack(anchor=tk.W)

        self.logs_dir_label = ttk.Label(self.validation_frame, text="Logs Dir: ")
        self.logs_dir_label.pack(anchor=tk.W)

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)

        self.connect_btn = ttk.Button(button_frame, text="Connect", command=self.connect, state=tk.DISABLED)
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)

        # Trace path changes (use trace_add for Python 3.6+ compatibility)
        self.path_var.trace_add('write', lambda *args: self.validate_path())

    def browse(self):
        directory = filedialog.askdirectory(
            parent=self.dialog,
            title="Select Project Root Directory",
            mustexist=True
        )

        if directory:
            self.path_var.set(directory)

    def validate_path(self):
        path_str = self.path_var.get()

        if not path_str:
            self.connect_btn.config(state=tk.DISABLED)
            return

        project_root = Path(path_str)

        if not project_root.exists():
            self.project_root_label.config(text="Project Root: ✗ Directory not found", foreground='red')
            self.queue_file_label.config(text="Queue File: ", foreground='black')
            self.logs_dir_label.config(text="Logs Dir: ", foreground='black')
            self.connect_btn.config(state=tk.DISABLED)
            return

        if not project_root.is_dir():
            self.project_root_label.config(text="Project Root: ✗ Not a directory", foreground='red')
            self.queue_file_label.config(text="Queue File: ", foreground='black')
            self.logs_dir_label.config(text="Logs Dir: ", foreground='black')
            self.connect_btn.config(state=tk.DISABLED)
            return

        # Look for required files/folders
        queue_manager_script = project_root / ".claude/queues/queue_manager.sh"
        queue_file = project_root / ".claude/queues/task_queue.json"
        logs_dir = project_root / ".claude/logs"

        # Validate
        script_valid = queue_manager_script.exists()
        queue_valid = queue_file.exists()
        logs_valid = logs_dir.exists()

        # Update labels
        self.project_root_label.config(
            text=f"Project Root: {project_root} {'✓' if project_root.exists() else '✗'}",
            foreground='green' if project_root.exists() else 'red'
        )

        self.queue_file_label.config(
            text=f"Queue Manager: .claude/queues/queue_manager.sh {'✓ Found' if script_valid else '✗ Not Found'}",
            foreground='green' if script_valid else 'red'
        )

        # Show optional status for queue file and logs
        queue_status = '✓ Found' if queue_valid else '(will be created)'
        logs_status = '✓ Found' if logs_valid else '(will be created)'

        self.logs_dir_label.config(
            text=f"Task Queue & Logs: {queue_status}, {logs_status}",
            foreground='green' if (queue_valid and logs_valid) else 'gray'
        )

        # Enable connect if only the script is valid (queue file and logs can be created)
        if script_valid:
            self.connect_btn.config(state=tk.NORMAL)
        else:
            self.connect_btn.config(state=tk.DISABLED)

    def connect(self):
        # Return the path to queue_manager.sh, not just the project root
        project_root = Path(self.path_var.get())
        queue_manager_script = project_root / ".claude/queues/queue_manager.sh"
        self.result = str(queue_manager_script)
        self.dialog.destroy()

    def cancel(self):
        self.result = None
        self.dialog.destroy()