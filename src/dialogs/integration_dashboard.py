"""
Integration Dashboard - View and manage GitHub/Jira/Confluence sync status.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional  # FIXED: Added Optional


class IntegrationDashboard:
    """Dashboard for viewing integration status with external systems."""

    def __init__(self, parent, queue_interface):
        self.queue = queue_interface

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Integration Dashboard")
        self.dialog.geometry("1100x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.build_ui()
        self.load_integration_status()

    def build_ui(self):
        """Build the UI."""
        # Header
        header_frame = ttk.Frame(self.dialog, padding=10)
        header_frame.pack(fill=tk.X)

        # Stats frame
        stats_frame = ttk.Frame(self.dialog, padding=10)
        stats_frame.pack(fill=tk.X)

        self.stats_labels = {}
        for key in ['total', 'synced', 'unsynced', 'failed']:
            frame = ttk.Frame(stats_frame)
            frame.pack(side=tk.LEFT, padx=20)

            label = ttk.Label(frame, text="0", font=('Arial', 16, 'bold'))
            label.pack()

            ttk.Label(frame, text=key.title(), font=('Arial', 9), foreground='gray').pack()
            self.stats_labels[key] = label

        # Main table
        table_frame = ttk.Frame(self.dialog, padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('enhancement', 'task_id', 'agent', 'status', 'github', 'jira', 'confluence', 'sync_status')
        self.integration_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )

        self.integration_tree.heading('enhancement', text='Enhancement')
        self.integration_tree.heading('task_id', text='Task ID')
        self.integration_tree.heading('agent', text='Agent')
        self.integration_tree.heading('status', text='Status')
        self.integration_tree.heading('github', text='GitHub')
        self.integration_tree.heading('jira', text='Jira')
        self.integration_tree.heading('confluence', text='Confluence')
        self.integration_tree.heading('sync_status', text='Sync Status')

        self.integration_tree.column('enhancement', width=150)
        self.integration_tree.column('task_id', width=150)
        self.integration_tree.column('agent', width=120)
        self.integration_tree.column('status', width=100)
        self.integration_tree.column('github', width=100)
        self.integration_tree.column('jira', width=100)
        self.integration_tree.column('confluence', width=100)
        self.integration_tree.column('sync_status', width=120)

        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.integration_tree.yview)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.integration_tree.xview)
        self.integration_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.integration_tree.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Context menu
        self.integration_tree.bind('<Button-3>', self.show_context_menu)
        self.integration_tree.bind('<Double-Button-1>', self.open_external_link)

        # Configure tags for sync status
        self.integration_tree.tag_configure('synced', background='#E8F5E9')
        self.integration_tree.tag_configure('unsynced', background='#FFF9E6')
        self.integration_tree.tag_configure('failed', background='#FFEBEE')

        # Bottom buttons
        button_frame = ttk.Frame(self.dialog, padding=10)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Sync All Unsynced", command=self.sync_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.load_integration_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def load_integration_status(self):
        """Load and display integration status for all tasks."""
        # Clear current
        for item in self.integration_tree.get_children():
            self.integration_tree.delete(item)

        try:
            queue_state = self.queue.get_queue_state()

            # Get all completed tasks (these are the ones that should be synced)
            completed_tasks = queue_state.completed_tasks

            total = 0
            synced = 0
            unsynced = 0
            failed = 0

            for task in completed_tasks:
                # Extract enhancement name
                enhancement = self._extract_enhancement(task.source_file)

                # Get metadata
                metadata = task.metadata or {}
                github_issue = metadata.get('github_issue')
                jira_ticket = metadata.get('jira_ticket')
                confluence_page = metadata.get('confluence_page')

                # Determine sync status
                has_github = bool(github_issue and github_issue != 'null')
                has_jira = bool(jira_ticket and jira_ticket != 'null')
                has_confluence = bool(confluence_page and confluence_page != 'null')

                # Check if integration was attempted
                github_display = f"#{github_issue}" if has_github else "—"
                jira_display = jira_ticket if has_jira else "—"
                confluence_display = "✓" if has_confluence else "—"

                # Determine overall sync status
                if task.result and 'INTEGRATION_COMPLETE' in task.result:
                    sync_status = "Complete"
                    tag = 'synced'
                    synced += 1
                elif task.result and 'INTEGRATION_FAILED' in task.result:
                    sync_status = "Failed"
                    tag = 'failed'
                    failed += 1
                elif has_github or has_jira or has_confluence:
                    sync_status = "Partial"
                    tag = 'synced'
                    synced += 1
                elif self._needs_integration(task.result):
                    sync_status = "Not Synced"
                    tag = 'unsynced'
                    unsynced += 1
                else:
                    sync_status = "N/A"
                    tag = ''

                total += 1

                # Insert row
                self.integration_tree.insert(
                    '',
                    tk.END,
                    values=(
                        enhancement,
                        task.id,
                        task.assigned_agent,
                        task.result or task.status,
                        github_display,
                        jira_display,
                        confluence_display,
                        sync_status
                    ),
                    tags=(tag,)
                )

            # Update stats
            self.stats_labels['total'].config(text=str(total))
            self.stats_labels['synced'].config(text=str(synced), foreground='green')
            self.stats_labels['unsynced'].config(text=str(unsynced), foreground='orange')
            self.stats_labels['failed'].config(text=str(failed), foreground='red')

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load integration status: {e}")

    def show_context_menu(self, event):
        """Show context menu for integration actions."""
        item = self.integration_tree.identify_row(event.y)
        if not item:
            return

        self.integration_tree.selection_set(item)
        values = self.integration_tree.item(item, 'values')

        menu = tk.Menu(self.dialog, tearoff=0)

        task_id = values[1]
        github = values[4]
        jira = values[5]
        sync_status = values[7]

        # Sync option
        if sync_status == "Not Synced":
            menu.add_command(
                label="Sync to External Systems",
                command=lambda: self.sync_task(task_id)
            )
            menu.add_separator()

        # Open external links
        if github != "—":
            menu.add_command(
                label=f"Open GitHub Issue {github}",
                command=lambda: self.open_github_issue(github)
            )

        if jira != "—":
            menu.add_command(
                label=f"Open Jira Ticket {jira}",
                command=lambda: self.open_jira_ticket(jira)
            )

        if github == "—" and jira == "—":
            menu.add_command(label="No external links", state=tk.DISABLED)

        menu.post(event.x_root, event.y_root)

    def open_external_link(self, event):
        """Double-click to open external link."""
        item = self.integration_tree.identify_row(event.y)
        if not item:
            return

        values = self.integration_tree.item(item, 'values')
        github = values[4]

        if github != "—":
            self.open_github_issue(github)

    def sync_task(self, task_id: str):
        """Sync specific task to external systems."""
        try:
            self.queue.sync_task_external(task_id)
            messagebox.showinfo("Success", f"Integration task created for {task_id}")
            self.load_integration_status()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to sync: {e}")

    def sync_all(self):
        """Sync all unsynced tasks."""
        if messagebox.askyesno(
                "Confirm",
                "Create integration tasks for all unsynced completed tasks?"
        ):
            try:
                self.queue.sync_all_external()
                messagebox.showinfo("Success", "Integration tasks created")
                self.load_integration_status()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to sync: {e}")

    def open_github_issue(self, issue_num: str):
        """Open GitHub issue in browser."""
        # Would need GitHub config to build URL
        messagebox.showinfo("GitHub", f"Would open issue {issue_num}\n(URL building requires GitHub config)")

    def open_jira_ticket(self, ticket: str):
        """Open Jira ticket in browser."""
        # Would need Jira config to build URL
        messagebox.showinfo("Jira", f"Would open ticket {ticket}\n(URL building requires Jira config)")

    def _extract_enhancement(self, source_file: str) -> str:
        """Extract enhancement name from source file."""
        if source_file.startswith('enhancements/'):
            parts = source_file.split('/')
            if len(parts) >= 2:
                return parts[1]
        return "(unknown)"

    def _needs_integration(self, result: Optional[str]) -> bool:
        """Check if result indicates integration is needed."""
        if not result:
            return False

        integration_statuses = [
            'READY_FOR_DEVELOPMENT',
            'READY_FOR_IMPLEMENTATION',
            'READY_FOR_TESTING',
            'TESTING_COMPLETE',
            'DOCUMENTATION_COMPLETE'
        ]

        return any(status in result for status in integration_statuses)