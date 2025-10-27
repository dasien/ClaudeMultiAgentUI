"""
Task details dialog for viewing task information.
Enhanced for v2.0 with contract validation status.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import subprocess
import sys


class TaskDetailsDialog:
    """Dialog for viewing task details with v2.0 contract validation."""

    def __init__(self, parent, task, queue_interface):
        self.task = task
        self.queue = queue_interface

        # Check if v2.0 compatible
        self.is_v2 = self.queue.is_v2_compatible()

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Task Details")
        self.dialog.geometry("700x800")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.build_ui()

    def build_ui(self):
        # Main frame with scrollbar
        main_canvas = tk.Canvas(self.dialog)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.dialog, orient=tk.VERTICAL, command=main_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        main_canvas.configure(yscrollcommand=scrollbar.set)
        main_canvas.bind('<Configure>', lambda e: main_canvas.configure(scrollregion=main_canvas.bbox('all')))

        main_frame = ttk.Frame(main_canvas, padding=20)
        main_canvas.create_window((0, 0), window=main_frame, anchor='nw')

        # Task ID with copy button
        id_frame = ttk.Frame(main_frame)
        id_frame.pack(fill=tk.X, pady=5)
        ttk.Label(id_frame, text=f"Task ID:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        ttk.Label(id_frame, text=f"{self.task.id}").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(id_frame, text="Copy ID", command=self.copy_id).pack(side=tk.RIGHT)

        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Format runtime for display
        runtime_display = "(not available)"
        if self.task.runtime_seconds:
            seconds = int(self.task.runtime_seconds)
            if seconds < 60:
                runtime_display = f"{seconds}s"
            elif seconds < 3600:
                minutes = seconds // 60
                secs = seconds % 60
                runtime_display = f"{minutes}m {secs}s"
            else:
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                runtime_display = f"{hours}h {minutes}m"

        # Other fields
        fields = [
            ("Title", self.task.title),
            ("Agent", self.task.assigned_agent),
            ("Status", f"● {self.task.status}"),
            ("Priority", self.task.priority),
            ("Type", self.task.task_type),
            ("Auto Complete", "Yes" if self.task.auto_complete else "No"),
            ("Auto Chain", "Yes" if self.task.auto_chain else "No"),
            ("Created", self.task.created),
            ("Started", self.task.started or "(not started)"),
            ("Completed", self.task.completed or "(not completed)"),
            ("Runtime", runtime_display),
        ]

        for label, value in fields:
            frame = ttk.Frame(main_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=f"{label}:", font=('Arial', 9, 'bold'), width=15).pack(side=tk.LEFT)
            ttk.Label(frame, text=str(value)).pack(side=tk.LEFT)

        # Source file with open button
        source_frame = ttk.Frame(main_frame)
        source_frame.pack(fill=tk.X, pady=2)
        ttk.Label(source_frame, text="Source File:", font=('Arial', 9, 'bold'), width=15).pack(side=tk.LEFT)
        ttk.Label(source_frame, text=self.task.source_file, wraplength=400).pack(side=tk.LEFT)
        ttk.Button(source_frame, text="Open File", command=self.open_file).pack(side=tk.RIGHT)

        # Contract Validation (v2.0 only, for completed tasks)
        if self.is_v2 and self.task.status in ['completed', 'active']:
            ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

            contract_frame = ttk.LabelFrame(main_frame, text="Contract Validation", padding=10)
            contract_frame.pack(fill=tk.X, pady=(0, 10))

            # Get validation status
            all_valid, messages = self.queue.validate_agent_outputs(
                self.task.assigned_agent,
                self.task.source_file
            )

            # Show validation messages
            for msg in messages:
                color = 'green' if '✓' in msg else 'red'
                ttk.Label(contract_frame, text=msg, foreground=color, font=('Arial', 9)).pack(anchor=tk.W, pady=1)

            # Show next agent if task completed successfully
            if self.task.result and self.task.status == 'completed':
                # Extract status from result
                status_code = self.task.result.split(' -')[0].strip()  # Get first part before " -"
                next_agents = self.queue.get_next_agents(self.task.assigned_agent, status_code)

                if next_agents:
                    next_agent_text = f"Next Agent: {', '.join(next_agents)}"
                    ttk.Label(contract_frame, text=next_agent_text, foreground='blue', font=('Arial', 9, 'bold')).pack(
                        anchor=tk.W, pady=(5, 1))
                elif status_code == 'DOCUMENTATION_COMPLETE':
                    ttk.Label(contract_frame, text="Next Agent: None (workflow complete)", foreground='gray',
                              font=('Arial', 9)).pack(anchor=tk.W, pady=(5, 1))

            # Show expected output path
            expected_output = self.queue.get_expected_output_path(
                self.task.assigned_agent,
                self.task.source_file
            )
            if expected_output:
                ttk.Label(contract_frame, text=f"Expected Output: {expected_output}", foreground='blue',
                          font=('Arial', 9)).pack(anchor=tk.W, pady=(5, 1))

        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Description
        ttk.Label(main_frame, text="Description:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        desc_text = tk.Text(desc_frame, height=10, wrap=tk.WORD, state=tk.NORMAL)
        desc_scrollbar = ttk.Scrollbar(desc_frame, command=desc_text.yview)
        desc_text.configure(yscrollcommand=desc_scrollbar.set)

        desc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        desc_text.insert('1.0', self.task.description)
        desc_text.config(state=tk.DISABLED)

        # Result (if completed/failed)
        if self.task.result:
            ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
            ttk.Label(main_frame, text="Result:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
            result_label = ttk.Label(main_frame, text=self.task.result, wraplength=620)
            result_label.pack(anchor=tk.W, pady=5)

        # Metadata (if available)
        if self.task.metadata:
            ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
            ttk.Label(main_frame, text="Metadata:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)

            metadata_frame = ttk.Frame(main_frame)
            metadata_frame.pack(fill=tk.X, pady=5)

            for key, value in self.task.metadata.items():
                if value:  # Only show non-null values
                    meta_line = ttk.Frame(metadata_frame)
                    meta_line.pack(fill=tk.X, pady=1)
                    ttk.Label(meta_line, text=f"{key}:", font=('Arial', 8), width=20).pack(side=tk.LEFT)
                    ttk.Label(meta_line, text=str(value), font=('Arial', 8), foreground='blue').pack(side=tk.LEFT)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        if self.queue.task_log_exists(self.task.id, self.task.source_file):
            ttk.Button(button_frame, text="View Log", command=self.view_log).pack(side=tk.LEFT, padx=5)

        # Open output folder button (v2.0 only)
        if self.is_v2:
            expected_output = self.queue.get_expected_output_path(
                self.task.assigned_agent,
                self.task.source_file
            )
            if expected_output:
                output_path = self.queue.project_root / Path(expected_output).parent
                if output_path.exists():
                    ttk.Button(button_frame, text="Open Output Folder",
                               command=lambda: self.open_folder(output_path)).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Close", command=self.close).pack(side=tk.LEFT, padx=5)

    def copy_id(self):
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append(self.task.id)
        messagebox.showinfo("Copied", "Task ID copied to clipboard")

    def open_file(self):
        source_path = Path(self.task.source_file)
        if not source_path.is_absolute():
            source_path = self.queue.project_root / source_path

        if not source_path.exists():
            messagebox.showerror("Error", f"File not found: {source_path}")
            return

        # Open file with default application
        if sys.platform == 'darwin':
            subprocess.run(['open', str(source_path)])
        elif sys.platform == 'win32':
            subprocess.run(['start', str(source_path)], shell=True)
        else:
            subprocess.run(['xdg-open', str(source_path)])

    def open_folder(self, folder_path: Path):
        """Open a folder in the system file browser."""
        if not folder_path.exists():
            messagebox.showerror("Error", f"Folder not found: {folder_path}")
            return

        # Open folder with system file browser
        if sys.platform == 'darwin':
            subprocess.run(['open', str(folder_path)])
        elif sys.platform == 'win32':
            subprocess.run(['explorer', str(folder_path)])
        else:
            subprocess.run(['xdg-open', str(folder_path)])

    def view_log(self):
        log_content = self.queue.get_task_log(self.task.id, self.task.source_file)
        if log_content:
            # Create log viewer
            log_window = tk.Toplevel(self.dialog)
            log_window.title(f"Task Log: {self.task.id}")
            log_window.geometry("900x700")

            text_frame = ttk.Frame(log_window, padding=10)
            text_frame.pack(fill=tk.BOTH, expand=True)

            text_widget = tk.Text(text_frame, wrap=tk.NONE, font=('Courier', 10))
            scrollbar_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            scrollbar_x = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
            text_widget.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

            text_widget.grid(row=0, column=0, sticky='nsew')
            scrollbar_y.grid(row=0, column=1, sticky='ns')
            scrollbar_x.grid(row=1, column=0, sticky='ew')

            text_frame.columnconfigure(0, weight=1)
            text_frame.rowconfigure(0, weight=1)

            text_widget.insert('1.0', log_content)
            text_widget.config(state=tk.DISABLED)

            ttk.Button(log_window, text="Close", command=log_window.destroy).pack(pady=10)

    def close(self):
        self.dialog.destroy()