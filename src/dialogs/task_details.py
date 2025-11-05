"""
Enhanced Task Details Dialog with skills usage display.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import subprocess
import sys

from .base_dialog import BaseDialog
from ..utils import TimeUtils


class TaskDetailsDialog(BaseDialog):
    """Enhanced dialog for viewing task details with skills usage."""

    def __init__(self, parent, task, queue_interface):
        super().__init__(parent, "Task Details", 750, 650)
        self.task = task
        self.queue = queue_interface

        self.build_ui()
        # Don't call show() - details dialogs don't return results

    def build_ui(self):
        """Build the task details UI."""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 10))

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
            ttk.Button(button_frame, text="📄 View Full Log", command=self.view_log).pack(side="left", padx=5)

        expected = self.queue.get_expected_output_path(self.task.assigned_agent, self.task.source_file)
        if expected:
            output_path = self.queue.project_root / Path(expected).parent
            if output_path.exists():
                ttk.Button(
                    button_frame,
                    text="📁 Open Output Folder",
                    command=lambda: self.open_folder(output_path)
                ).pack(side="left", padx=5)

        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side="left", padx=5)

    def build_general_tab(self, parent):
        """Build General Info tab."""
        scrollable_frame = ttk.Frame(parent, padding=20)
        scrollable_frame.pack(fill="both", expand=True)

        # Task ID with copy button
        id_frame = ttk.Frame(scrollable_frame)
        id_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(id_frame, text="Task ID:", font=('Arial', 10, 'bold')).pack(side="left")
        ttk.Label(id_frame, text=self.task.id, font=('Courier', 9)).pack(side="left", padx=(10, 0))
        ttk.Button(id_frame, text="Copy", command=self.copy_id).pack(side="right")

        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", pady=10)

        # Basic info grid
        info_grid = ttk.Frame(scrollable_frame)
        info_grid.pack(fill="x", pady=(0, 10))

        # Using TimeUtils for runtime formatting!
        fields = [
            ("Title", self.task.title),
            ("Agent", self.task.assigned_agent),
            ("Status", f"● {self.task.status}"),
            ("Priority", self.task.priority.upper()),
            ("Type", self.task.task_type),
            ("Created", self.task.created),
            ("Started", self.task.started or "(not started)"),
            ("Completed", self.task.completed or "(not completed)"),
            ("Runtime", TimeUtils.format_runtime(self.task.runtime_seconds) or "(not available)"),
        ]

        for i, (label, value) in enumerate(fields):
            row_frame = ttk.Frame(info_grid)
            row_frame.pack(fill="x", pady=2)

            ttk.Label(row_frame, text=f"{label}:", font=('Arial', 9, 'bold'), width=12).pack(side="left")
            ttk.Label(row_frame, text=str(value), font=('Arial', 9)).pack(side="left")

        # Source file with open button
        source_frame = ttk.Frame(scrollable_frame)
        source_frame.pack(fill="x", pady=5)

        ttk.Label(source_frame, text="Source File:", font=('Arial', 9, 'bold'), width=12).pack(side="left")
        ttk.Label(source_frame, text=self.task.source_file, wraplength=500).pack(side="left")
        ttk.Button(source_frame, text="Open", command=self.open_file).pack(side="right")

        # Automation flags
        auto_frame = ttk.Frame(scrollable_frame)
        auto_frame.pack(fill="x", pady=5)

        ttk.Label(auto_frame, text="Automation:", font=('Arial', 9, 'bold'), width=12).pack(side="left")

        auto_text = []
        if self.task.auto_complete:
            auto_text.append("Auto-Complete")
        if self.task.auto_chain:
            auto_text.append("Auto-Chain")

        ttk.Label(
            auto_frame,
            text=" | ".join(auto_text) if auto_text else "Manual",
            font=('Arial', 9)
        ).pack(side="left")

        # Result
        if self.task.result:
            ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", pady=15)
            ttk.Label(scrollable_frame, text="Result:", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))
            ttk.Label(scrollable_frame, text=self.task.result, wraplength=650).pack(anchor="w")

        return scrollable_frame

    def build_details_tab(self, parent):
        """Build Details tab."""
        scrollable_frame = ttk.Frame(parent, padding=20)
        scrollable_frame.pack(fill="both", expand=True)

        # SKILLS SECTION
        skills_frame = ttk.LabelFrame(scrollable_frame, text="🎯 Skills", padding=10)
        skills_frame.pack(fill="x", pady=(0, 15))

        # Available skills
        agent_skills = self.queue.get_agent_skills(self.task.assigned_agent)

        if agent_skills:
            ttk.Label(
                skills_frame,
                text=f"Available Skills ({len(agent_skills)}):",
                font=('Arial', 9, 'bold')
            ).pack(anchor="w", pady=(0, 5))

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
                        ).pack(anchor="w")

            # Skills actually used (from log)
            if self.task.status in ['completed', 'failed']:
                log_content = self.queue.get_task_log(self.task.id, self.task.source_file)
                if log_content:
                    skills_used = self.queue.extract_skills_used(log_content)

                    if skills_used:
                        ttk.Separator(skills_frame, orient="horizontal").pack(fill="x", pady=(10, 10))

                        ttk.Label(
                            skills_frame,
                            text=f"Skills Applied ({len(skills_used)}):",
                            font=('Arial', 9, 'bold'),
                            foreground='green'
                        ).pack(anchor="w", pady=(0, 5))

                        for skill in skills_used:
                            ttk.Label(
                                skills_frame,
                                text=f"  ✓ {skill}",
                                font=('Arial', 9),
                                foreground='green'
                            ).pack(anchor="w")
        else:
            ttk.Label(
                skills_frame,
                text="This agent has no skills assigned",
                font=('Arial', 9),
                foreground='gray'
            ).pack(anchor="w")

        # Contract validation
        if self.task.status in ['completed', 'active']:
            ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", pady=10)
            contract_frame = ttk.LabelFrame(scrollable_frame, text="Contract Validation", padding=10)
            contract_frame.pack(fill="x", pady=(0, 15))

            all_valid, messages = self.queue.validate_agent_outputs(
                self.task.assigned_agent,
                self.task.source_file
            )

            for msg in messages:
                color = 'green' if '✓' in msg else 'red'
                ttk.Label(contract_frame, text=msg, foreground=color, font=('Arial', 9)).pack(anchor="w", pady=1)

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
                    ).pack(anchor="w", pady=(5, 0))

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
                ).pack(anchor="w", pady=(5, 0))

        # Description
        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(scrollable_frame, text="Description:", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))

        desc_frame = ttk.Frame(scrollable_frame)
        desc_frame.pack(fill="x", pady=(0, 15))

        desc_text = tk.Text(desc_frame, height=5, wrap="word", state=tk.NORMAL, width=80)
        desc_scroll = ttk.Scrollbar(desc_frame, command=desc_text.yview)
        desc_text.configure(yscrollcommand=desc_scroll.set)

        desc_text.pack(side="left", fill="x", expand=True)
        desc_scroll.pack(side="right", fill="y")

        desc_text.insert('1.0', self.task.description)
        desc_text.config(state=tk.DISABLED)

        # External Integration
        if self.task.metadata:
            ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", pady=10)
            ttk.Label(scrollable_frame, text="External Integration:", font=('Arial', 10, 'bold')).pack(anchor="w",
                                                                                                       pady=(0, 5))

            meta_frame = ttk.Frame(scrollable_frame)
            meta_frame.pack(fill="x")

            for key, value in self.task.metadata.items():
                if value and value != 'null':
                    row = ttk.Frame(meta_frame)
                    row.pack(fill="x", pady=1)

                    ttk.Label(row, text=f"{key}:", font=('Arial', 9), width=20).pack(side="left")
                    ttk.Label(row, text=str(value), font=('Arial', 9), foreground='blue').pack(side="left")

        return scrollable_frame

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
        header.pack(fill="x")

        ttk.Label(header, text="Search:", font=('Arial', 9)).pack(side="left", padx=(0, 5))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(header, textvariable=search_var, width=30)
        search_entry.pack(side="left")

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

        ttk.Button(header, text="Find", command=search_log).pack(side="left", padx=5)

        # Text area
        text_frame = ttk.Frame(log_window, padding=10)
        text_frame.pack(fill="both", expand=True)

        text_widget = tk.Text(text_frame, wrap="none", font=('Courier', 9))
        scroll_y = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        scroll_x = ttk.Scrollbar(text_frame, orient="horizontal", command=text_widget.xview)
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
        button_frame.pack(fill="x")

        ttk.Button(button_frame, text="Close", command=log_window.destroy).pack(side="right")