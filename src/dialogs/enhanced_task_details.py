"""
Enhanced Task Details Dialog with skills usage display.
v3.0 - Shows which skills were applied during task execution.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import subprocess
import sys


class EnhancedTaskDetailsDialog:
    """Enhanced dialog for viewing task details with skills usage."""

    def __init__(self, parent, task, queue_interface):
        self.task = task
        self.queue = queue_interface

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Task Details")
        self.dialog.geometry("750x650")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.build_ui()

    def build_ui(self):
        """Build the UI with tabs."""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Tab 1: General Info
        general_tab = self.build_general_tab(notebook)
        notebook.add(general_tab, text="General Info")

        # Tab 2: Details
        details_tab = self.build_details_tab(notebook)
        notebook.add(details_tab, text="Details")

        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        if self.queue.task_log_exists(self.task.id, self.task.source_file):
            ttk.Button(button_frame, text="📄 View Full Log", command=self.view_log).pack(side=tk.LEFT, padx=5)

        expected = self.queue.get_expected_output_path(self.task.assigned_agent, self.task.source_file)
        if expected:
            output_path = self.queue.project_root / Path(expected).parent
            if output_path.exists():
                ttk.Button(
                    button_frame,
                    text="📁 Open Output Folder",
                    command=lambda: self.open_folder(output_path)
                ).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def build_general_tab(self, parent):
        """Build General Info tab."""
        # Frame with padding
        scrollable_frame = ttk.Frame(parent, padding=20)
        scrollable_frame.pack(fill=tk.BOTH, expand=True)

        # Task ID with copy button
        id_frame = ttk.Frame(scrollable_frame)
        id_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(id_frame, text="Task ID:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Label(id_frame, text=self.task.id, font=('Courier', 9)).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(id_frame, text="Copy", command=self.copy_id).pack(side=tk.RIGHT)

        ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Basic info grid
        info_grid = ttk.Frame(scrollable_frame)
        info_grid.pack(fill=tk.X, pady=(0, 10))

        fields = [
            ("Title", self.task.title),
            ("Agent", self.task.assigned_agent),
            ("Status", f"● {self.task.status}"),
            ("Priority", self.task.priority.upper()),
            ("Type", self.task.task_type),
            ("Created", self.task.created),
            ("Started", self.task.started or "(not started)"),
            ("Completed", self.task.completed or "(not completed)"),
            ("Runtime", self.format_runtime(self.task.runtime_seconds)),
        ]

        for i, (label, value) in enumerate(fields):
            row_frame = ttk.Frame(info_grid)
            row_frame.pack(fill=tk.X, pady=2)

            ttk.Label(row_frame, text=f"{label}:", font=('Arial', 9, 'bold'), width=12).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=str(value), font=('Arial', 9)).pack(side=tk.LEFT)

        # Source file with open button
        source_frame = ttk.Frame(scrollable_frame)
        source_frame.pack(fill=tk.X, pady=5)

        ttk.Label(source_frame, text="Source File:", font=('Arial', 9, 'bold'), width=12).pack(side=tk.LEFT)
        ttk.Label(source_frame, text=self.task.source_file, wraplength=500).pack(side=tk.LEFT)
        ttk.Button(source_frame, text="Open", command=self.open_file).pack(side=tk.RIGHT)

        # Automation flags
        auto_frame = ttk.Frame(scrollable_frame)
        auto_frame.pack(fill=tk.X, pady=5)

        ttk.Label(auto_frame, text="Automation:", font=('Arial', 9, 'bold'), width=12).pack(side=tk.LEFT)

        auto_text = []
        if self.task.auto_complete:
            auto_text.append("Auto-Complete")
        if self.task.auto_chain:
            auto_text.append("Auto-Chain")

        ttk.Label(
            auto_frame,
            text=" | ".join(auto_text) if auto_text else "Manual",
            font=('Arial', 9)
        ).pack(side=tk.LEFT)

        # Result
        if self.task.result:
            ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
            ttk.Label(scrollable_frame, text="Result:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
            ttk.Label(scrollable_frame, text=self.task.result, wraplength=650).pack(anchor=tk.W)

        return scrollable_frame

    def build_details_tab(self, parent):
        """Build Details tab."""
        # Simple frame with padding - no need for scrolling
        scrollable_frame = ttk.Frame(parent, padding=20)
        scrollable_frame.pack(fill=tk.BOTH, expand=True)

        # SKILLS SECTION
        skills_frame = ttk.LabelFrame(scrollable_frame, text="🎯 Skills", padding=10)
        skills_frame.pack(fill=tk.X, pady=(0, 15))

        # Available skills
        agent_skills = self.queue.get_agent_skills(self.task.assigned_agent)

        if agent_skills:
            ttk.Label(
                skills_frame,
                text=f"Available Skills ({len(agent_skills)}):",
                font=('Arial', 9, 'bold')
            ).pack(anchor=tk.W, pady=(0, 5))

            skills_data = self.queue.get_skills_list()
            for skill_dir in agent_skills:
                if skills_data:
                    skill_info = next(
                        (s for s in skills_data.get('skills', [])
                         if s.get('skill-directory') == skill_dir),
                        None
                    )
                    if skill_info:
                        ttk.Label(
                            skills_frame,
                            text=f"  • {skill_info.get('name', skill_dir)}",
                            font=('Arial', 9)
                        ).pack(anchor=tk.W)

            # Skills actually used (from log)
            if self.task.status in ['completed', 'failed']:
                log_content = self.queue.get_task_log(self.task.id, self.task.source_file)
                if log_content:
                    skills_used = self.queue.extract_skills_used(log_content)

                    if skills_used:
                        ttk.Separator(skills_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(10, 10))

                        ttk.Label(
                            skills_frame,
                            text=f"Skills Applied ({len(skills_used)}):",
                            font=('Arial', 9, 'bold'),
                            foreground='green'
                        ).pack(anchor=tk.W, pady=(0, 5))

                        for skill in skills_used:
                            ttk.Label(
                                skills_frame,
                                text=f"  ✓ {skill}",
                                font=('Arial', 9),
                                foreground='green'
                            ).pack(anchor=tk.W)
        else:
            ttk.Label(
                skills_frame,
                text="This agent has no skills assigned",
                font=('Arial', 9),
                foreground='gray'
            ).pack(anchor=tk.W)

        # Contract validation (for completed/active)
        if self.task.status in ['completed', 'active']:
            ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
            contract_frame = ttk.LabelFrame(scrollable_frame, text="Contract Validation", padding=10)
            contract_frame.pack(fill=tk.X, pady=(0, 15))

            all_valid, messages = self.queue.validate_agent_outputs(
                self.task.assigned_agent,
                self.task.source_file
            )

            for msg in messages:
                color = 'green' if '✓' in msg else 'red'
                ttk.Label(contract_frame, text=msg, foreground=color, font=('Arial', 9)).pack(anchor=tk.W, pady=1)

            # Next agent info
            if self.task.result and self.task.status == 'completed':
                status_code = self.task.result.split(' -')[0].strip()
                next_agents = self.queue.get_next_agents(self.task.assigned_agent, status_code)

                if next_agents:
                    next_names = [self.queue.get_agent_list().get(a, a) for a in next_agents]
                    ttk.Label(
                        contract_frame,
                        text=f"Next Agent: {', '.join(next_names)}",
                        foreground='blue',
                        font=('Arial', 9, 'bold')
                    ).pack(anchor=tk.W, pady=(5, 0))

            # Expected output
            expected = self.queue.get_expected_output_path(self.task.assigned_agent, self.task.source_file)
            if expected:
                expected_path = self.queue.project_root / expected
                exists = expected_path.exists()

                ttk.Label(
                    contract_frame,
                    text=f"Expected Output: {expected} {'✓' if exists else '✗'}",
                    foreground='green' if exists else 'orange',
                    font=('Arial', 9)
                ).pack(anchor=tk.W, pady=(5, 0))

        # Description
        ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(scrollable_frame, text="Description:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))

        desc_frame = ttk.Frame(scrollable_frame)
        desc_frame.pack(fill=tk.X, pady=(0, 15))

        desc_text = tk.Text(desc_frame, height=5, wrap=tk.WORD, state=tk.NORMAL, width=80)
        desc_scroll = ttk.Scrollbar(desc_frame, command=desc_text.yview)
        desc_text.configure(yscrollcommand=desc_scroll.set)

        desc_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        desc_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        desc_text.insert('1.0', self.task.description)
        desc_text.config(state=tk.DISABLED)

        # External Integration
        if self.task.metadata:
            ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
            ttk.Label(scrollable_frame, text="External Integration:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))

            meta_frame = ttk.Frame(scrollable_frame)
            meta_frame.pack(fill=tk.X)

            for key, value in self.task.metadata.items():
                if value and value != 'null':
                    row = ttk.Frame(meta_frame)
                    row.pack(fill=tk.X, pady=1)

                    ttk.Label(row, text=f"{key}:", font=('Arial', 9), width=20).pack(side=tk.LEFT)
                    ttk.Label(row, text=str(value), font=('Arial', 9), foreground='blue').pack(side=tk.LEFT)

        return scrollable_frame

    def format_runtime(self, seconds):
        """Format runtime."""
        if not seconds:
            return "(not available)"

        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        else:
            return f"{seconds // 3600}h {(seconds % 3600) // 60}m"

    def copy_id(self):
        """Copy task ID to clipboard."""
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append(self.task.id)
        messagebox.showinfo("Copied", "Task ID copied to clipboard")

    def open_file(self):
        """Open source file."""
        source_path = Path(self.task.source_file)
        if not source_path.is_absolute():
            source_path = self.queue.project_root / source_path

        if not source_path.exists():
            messagebox.showerror("Error", f"File not found: {source_path}")
            return

        if sys.platform == 'darwin':
            subprocess.run(['open', str(source_path)])
        elif sys.platform == 'win32':
            subprocess.run(['start', str(source_path)], shell=True)
        else:
            subprocess.run(['xdg-open', str(source_path)])

    def open_folder(self, folder_path: Path):
        """Open folder in file browser."""
        if not folder_path.exists():
            messagebox.showerror("Error", f"Folder not found: {folder_path}")
            return

        if sys.platform == 'darwin':
            subprocess.run(['open', str(folder_path)])
        elif sys.platform == 'win32':
            subprocess.run(['explorer', str(folder_path)])
        else:
            subprocess.run(['xdg-open', str(folder_path)])

    def view_log(self):
        """View full task log."""
        log_content = self.queue.get_task_log(self.task.id, self.task.source_file)
        if not log_content:
            messagebox.showinfo("No Log", "Log file not found")
            return

        # Create log viewer
        log_window = tk.Toplevel(self.dialog)
        log_window.title(f"Task Log: {self.task.id}")
        log_window.geometry("1000x700")

        # Header with search
        header = ttk.Frame(log_window, padding=10)
        header.pack(fill=tk.X)

        ttk.Label(header, text="Search:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(header, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT)
        
        def search_log():
            query = search_var.get()
            if query:
                text_widget.tag_remove('search', '1.0', tk.END)
                idx = '1.0'
                while True:
                    idx = text_widget.search(query, idx, tk.END, nocase=True)
                    if not idx:
                        break
                    end_idx = f"{idx}+{len(query)}c"
                    text_widget.tag_add('search', idx, end_idx)
                    idx = end_idx
                text_widget.tag_config('search', background='yellow')

        ttk.Button(header, text="Find", command=search_log).pack(side=tk.LEFT, padx=5)

        # Text area
        text_frame = ttk.Frame(log_window, padding=10)
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(text_frame, wrap=tk.NONE, font=('Courier', 9))
        scroll_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        scroll_x = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
        text_widget.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        text_widget.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')

        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        text_widget.insert('1.0', log_content)
        text_widget.config(state=tk.DISABLED)

        # Bottom buttons
        button_frame = ttk.Frame(log_window, padding=10)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Close", command=log_window.destroy).pack(side=tk.RIGHT)
