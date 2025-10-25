#!/usr/bin/env python3
"""
Multi-Agent Task Queue Manager
A graphical interface for managing multi-agent development workflows using Claude Code.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path
from enum import Enum
from typing import Optional

from .queue_interface import QueueInterface
from .models import ConnectionState, QueueUIState
from .dialogs import (
    ConnectDialog,
    CreateTaskDialog,
    TaskDetailsDialog,
    OperationsLogDialog,
    AboutDialog,
    AgentManagerDialog
)
from .config import Config
from .settings import Settings


class TaskQueueUI:
    """Main application window for the Task Queue Manager."""

    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Agent Task Queue Manager")
        self.root.geometry("1000x700")
        self.root.minsize(800, 500)

        # Settings manager
        self.settings = Settings()

        # State
        self.state = QueueUIState()
        self.state.connection_state = ConnectionState.DISCONNECTED
        self.state.auto_refresh_enabled = False  # Off by default, user can enable
        self.state.auto_refresh_interval = Config.AUTO_REFRESH_INTERVAL
        self.auto_refresh_timer = None  # Store timer ID for cancellation

        # Queue interface (will be initialized on connect)
        self.queue = None

        # Build UI
        self.build_menu_bar()
        self.build_connection_header()
        self.build_task_table()
        self.build_status_bar()

        # Configure styles
        self.configure_styles()

        # Initial state
        self.update_ui_state()

        # Setup window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        # Try to auto-connect to last used queue manager
        self.try_auto_connect()

    def build_menu_bar(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(
            label="Connect...",
            command=self.show_connect_dialog,
            accelerator="Ctrl+O"
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Quit",
            command=self.quit_app,
            accelerator="Ctrl+Q"
        )

        # Tasks menu
        tasks_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tasks", menu=tasks_menu)
        tasks_menu.add_command(
            label="Create Task...",
            command=self.create_task,
            accelerator="Ctrl+N"
        )
        tasks_menu.add_separator()
        tasks_menu.add_command(
            label="Cancel All Tasks",
            command=self.cancel_all_tasks
        )
        tasks_menu.add_separator()
        tasks_menu.add_command(
            label="Refresh List",
            command=self.refresh,
            accelerator="F5"
        )

        # Logs menu
        logs_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Logs", menu=logs_menu)
        logs_menu.add_command(
            label="View Operations Log",
            command=self.show_operations_log,
            accelerator="Ctrl+L"
        )

        # Agents menu
        agents_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Agents", menu=agents_menu)
        agents_menu.add_command(
            label="Manage Agents...",
            command=self.show_agent_manager
        )

        # Settings menu
        self.settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=self.settings_menu)

        # Auto-refresh checkbutton
        self.auto_refresh_var = tk.BooleanVar(value=self.state.auto_refresh_enabled)
        self.settings_menu.add_checkbutton(
            label="Auto Refresh",
            variable=self.auto_refresh_var,
            command=self.toggle_auto_refresh
        )
        self.settings_menu.add_separator()
        self.settings_menu.add_command(
            label="Configure Claude API Key...",
            command=self.configure_api_key
        )

        # About menu
        about_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="About", menu=about_menu)
        about_menu.add_command(
            label="About Task Queue UI",
            command=self.show_about_dialog
        )

        # Keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.show_connect_dialog())
        self.root.bind('<Control-q>', lambda e: self.quit_app())
        self.root.bind('<Control-l>', lambda e: self.show_operations_log())
        self.root.bind('<F5>', lambda e: self.refresh())
        self.root.bind('<Control-r>', lambda e: self.refresh())
        self.root.bind('<Control-n>', lambda e: self.create_task())
        self.root.bind('<Delete>', lambda e: self.cancel_task())
        self.root.bind('<Return>', lambda e: self.start_task())
        self.root.bind('<Control-c>', lambda e: self.copy_task_id())

    def build_connection_header(self):
        """Create the connection status header."""
        self.connection_frame = ttk.Frame(self.root, style='Connection.TFrame', padding=5)
        self.connection_frame.pack(fill=tk.X)

        self.connection_label = ttk.Label(
            self.connection_frame,
            text="Not connected - File > Connect to select queue manager",
            font=('Arial', 9),
            style='Connection.TLabel'
        )
        self.connection_label.pack(anchor=tk.W)

    def build_task_table(self):
        """Create the main task table."""
        # Main frame
        table_frame = ttk.Frame(self.root, padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Label frame
        label_frame = ttk.LabelFrame(table_frame, text="TASK QUEUE", padding=5)
        label_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar frame
        tree_frame = ttk.Frame(label_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Columns: Task ID, Title, Agent, Status, Start Date, End Date, Runtime
        columns = ('task_id', 'title', 'agent', 'status', 'start_date', 'end_date', 'runtime')
        self.task_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )

        # Column configuration
        self.task_tree.heading('task_id', text='Task ID', command=lambda: self.sort_by('task_id'))
        self.task_tree.heading('title', text='Title', command=lambda: self.sort_by('title'))
        self.task_tree.heading('agent', text='Agent', command=lambda: self.sort_by('agent'))
        self.task_tree.heading('status', text='Status', command=lambda: self.sort_by('status'))
        self.task_tree.heading('start_date', text='Start Date', command=lambda: self.sort_by('start_date'))
        self.task_tree.heading('end_date', text='End Date', command=lambda: self.sort_by('end_date'))
        self.task_tree.heading('runtime', text='Runtime', command=lambda: self.sort_by('runtime'))

        self.task_tree.column('task_id', width=180, minwidth=120)
        self.task_tree.column('title', width=300, minwidth=200)
        self.task_tree.column('agent', width=150, minwidth=120)
        self.task_tree.column('status', width=100, minwidth=80)
        self.task_tree.column('start_date', width=150, minwidth=120)
        self.task_tree.column('end_date', width=150, minwidth=120)
        self.task_tree.column('runtime', width=100, minwidth=80)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.task_tree.xview)
        self.task_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        self.task_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Hint label at bottom
        hint_label = ttk.Label(
            label_frame,
            text="[Right-click for actions | Double-click to view details]",
            font=('Arial', 9),
            foreground='gray'
        )
        hint_label.pack(pady=(5, 0))

        # Event bindings
        self.task_tree.bind('<Double-Button-1>', self.on_double_click)
        self.task_tree.bind('<Button-3>', self.show_context_menu)  # Windows/Linux
        self.task_tree.bind('<Button-2>', self.show_context_menu)  # macOS right-click
        self.task_tree.bind('<Control-Button-1>', self.show_context_menu)  # macOS Ctrl+click

        # Store sort state
        self.sort_column = None
        self.sort_reverse = False

    def build_status_bar(self):
        """Create the status bar."""
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN, padding=2)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Left side - task counts
        self.status_label = ttk.Label(
            status_frame,
            text="Not connected",
            font=('Arial', 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Right side - auto-refresh status
        self.refresh_label = ttk.Label(
            status_frame,
            text="Auto-refresh: OFF",
            font=('Arial', 9)
        )
        self.refresh_label.pack(side=tk.RIGHT, padx=5)

    def configure_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()

        # Connection header style
        style.configure('Connection.TFrame', background='#F0F0F0')
        style.configure('Connection.TLabel', background='#F0F0F0')

        # Define tags for row colors
        self.task_tree.tag_configure('pending', background='white')
        self.task_tree.tag_configure('active', background='#FFF9E6')
        self.task_tree.tag_configure('completed', background='#E8F5E9')
        self.task_tree.tag_configure('failed', background='#FFEBEE')

    def update_ui_state(self):
        """Update UI based on connection state."""
        if self.state.connection_state == ConnectionState.DISCONNECTED:
            self.connection_label.config(
                text="Not connected - File > Connect to select queue manager",
                foreground='black'
            )
            self.status_label.config(text="Not connected")
            self.refresh_label.config(text="Auto-refresh: OFF")

            # Clear table and show message
            for item in self.task_tree.get_children():
                self.task_tree.delete(item)

        elif self.state.connection_state == ConnectionState.CONNECTED:
            self.connection_label.config(
                text=f"Connected: {self.state.queue_manager_path}",
                foreground='black'
            )
            # Only start auto-refresh if enabled
            if self.state.auto_refresh_enabled:
                self.start_auto_refresh()
            else:
                self.refresh_label.config(text="Auto-refresh: OFF")

        elif self.state.connection_state == ConnectionState.ERROR:
            self.connection_label.config(
                text=f"Connection Error: {self.state.error_message}",
                foreground='red'
            )
            self.status_label.config(text="Connection error")

    def show_connect_dialog(self):
        """Show the connect to queue manager dialog."""
        dialog = ConnectDialog(self.root)
        if dialog.result:
            self.connect_to_queue(dialog.result)

    def try_auto_connect(self):
        """Try to auto-connect to the last used queue manager."""
        last_path = self.settings.get_last_queue_manager()
        if last_path:
            # Verify path still exists
            path = Path(last_path)
            if path.exists():
                try:
                    print(f"Auto-connecting to: {last_path}")
                    self.connect_to_queue(last_path, silent=True)
                except Exception as e:
                    print(f"Auto-connect failed: {e}")
                    # Don't show error dialog on auto-connect failure
            else:
                print(f"Last queue manager path no longer exists: {last_path}")
                # Clear invalid path
                self.settings.clear_last_queue_manager()

    def connect_to_queue(self, queue_manager_path, silent=False):
        """Connect to a queue manager.

        Args:
            queue_manager_path: Path to queue_manager.sh
            silent: If True, don't show error dialogs (for auto-connect)
        """
        try:
            path = Path(queue_manager_path)
            if not path.exists():
                raise FileNotFoundError(f"Queue manager not found: {path}")

            # Initialize queue interface
            self.queue = QueueInterface(str(path))

            # Update state
            self.state.connection_state = ConnectionState.CONNECTED
            self.state.queue_manager_path = path
            self.state.project_root = path.parent.parent.parent  # ../../../
            self.state.queue_file = self.state.project_root / ".claude/queues/task_queue.json"
            self.state.logs_dir = self.state.project_root / ".claude/logs"

            # Save to settings
            self.settings.set_last_queue_manager(str(path))
            print(f"Saved queue manager path to settings: {path}")

            # Update UI
            self.update_ui_state()
            self.refresh()

        except Exception as e:
            self.state.connection_state = ConnectionState.ERROR
            self.state.error_message = str(e)
            self.update_ui_state()
            if not silent:
                messagebox.showerror("Connection Error", f"Failed to connect: {e}")

    def refresh(self):
        """Refresh the task list."""
        if self.state.connection_state != ConnectionState.CONNECTED:
            return

        try:
            # Get queue state
            print("DEBUG: Fetching queue state...")
            queue_state = self.queue.get_queue_state()
            print(f"DEBUG: Got {len(queue_state.pending_tasks)} pending, {len(queue_state.active_workflows)} active, {len(queue_state.completed_tasks)} completed, {len(queue_state.failed_tasks)} failed")

            # Clear current items
            for item in self.task_tree.get_children():
                self.task_tree.delete(item)

            # Combine all tasks
            all_tasks = (
                queue_state.pending_tasks +
                queue_state.active_workflows +
                queue_state.completed_tasks[-50:] +  # Last 50 completed
                queue_state.failed_tasks
            )

            # Populate table
            for task in all_tasks:
                status_display = self.get_status_display(task.status)
                tag = task.status.lower()
                runtime_display = self.format_runtime(task.runtime_seconds)

                self.task_tree.insert(
                    '',
                    tk.END,
                    values=(
                        task.id,
                        task.title,
                        task.assigned_agent,
                        status_display,
                        task.started or '',
                        task.completed or '',
                        runtime_display
                    ),
                    tags=(tag,)
                )

            # Update status bar
            self.status_label.config(
                text=f"Status: {len(queue_state.pending_tasks)} Pending | "
                     f"{len(queue_state.active_workflows)} Active | "
                     f"{len(queue_state.completed_tasks)} Completed | "
                     f"{len(queue_state.failed_tasks)} Failed"
            )

            # Update refresh label
            import time
            self.state.last_refresh = time.time()

        except Exception as e:
            messagebox.showerror("Refresh Error", f"Failed to refresh: {e}")

    def get_status_display(self, status):
        """Get display string for status."""
        status_map = {
            'pending': 'Pending',
            'active': 'Active',
            'completed': 'Completed',
            'failed': 'Failed'
        }
        return status_map.get(status.lower(), status.capitalize())

    def format_runtime(self, runtime_seconds):
        """Format runtime seconds into human-readable string."""
        if runtime_seconds is None:
            return ''

        # Convert to integer if it's not already
        seconds = int(runtime_seconds)

        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"

    def toggle_auto_refresh(self):
        """Toggle auto-refresh on/off."""
        # Update state
        self.state.auto_refresh_enabled = self.auto_refresh_var.get()

        if self.state.auto_refresh_enabled:
            # Start auto-refresh
            if self.state.connection_state == ConnectionState.CONNECTED:
                self.start_auto_refresh()
            self.refresh_label.config(
                text=f"Auto-refresh: ✓ ON (every {self.state.auto_refresh_interval}s)"
            )
        else:
            # Stop auto-refresh
            if self.auto_refresh_timer:
                self.root.after_cancel(self.auto_refresh_timer)
                self.auto_refresh_timer = None
            self.refresh_label.config(text="Auto-refresh: OFF")

    def start_auto_refresh(self):
        """Start auto-refresh timer."""
        # Cancel existing timer if any
        if self.auto_refresh_timer:
            self.root.after_cancel(self.auto_refresh_timer)
            self.auto_refresh_timer = None

        if self.state.auto_refresh_enabled and self.state.connection_state == ConnectionState.CONNECTED:
            self.refresh()
            interval_ms = self.state.auto_refresh_interval * 1000
            self.auto_refresh_timer = self.root.after(interval_ms, self.start_auto_refresh)

            # Update refresh label
            self.refresh_label.config(
                text=f"Auto-refresh: ✓ ON (every {self.state.auto_refresh_interval}s)"
            )

    def on_double_click(self, event):
        """Handle double-click on task."""
        task = self.get_selected_task()
        if task:
            TaskDetailsDialog(self.root, task, self.queue)

    def show_context_menu(self, event):
        """Show context menu on right-click."""
        # Determine if task is selected
        item = self.task_tree.identify_row(event.y)

        menu = tk.Menu(self.root, tearoff=0)

        if item:
            # Task is selected
            self.task_tree.selection_set(item)
            task = self.get_selected_task()

            if task:
                can_start = task.status == 'pending'
                can_cancel = task.status in ['pending', 'active']
                has_log = self.queue.task_log_exists(task.id, task.source_file)

                menu.add_command(
                    label="Start Task",
                    command=self.start_task,
                    state=tk.NORMAL if can_start else tk.DISABLED
                )
                menu.add_command(
                    label="Cancel Task",
                    command=self.cancel_task,
                    state=tk.NORMAL if can_cancel else tk.DISABLED
                )
                menu.add_separator()
                menu.add_command(label="View Details...", command=self.show_task_details)
                menu.add_command(
                    label="View Task Log...",
                    command=self.show_task_log,
                    state=tk.NORMAL if has_log else tk.DISABLED
                )
                menu.add_separator()
                menu.add_command(label="Copy Task ID", command=self.copy_task_id)
                menu.add_separator()
                menu.add_command(label="Refresh", command=self.refresh, accelerator="F5")
        else:
            # No task selected (clicked empty space)
            menu.add_command(label="Create Task...", command=self.create_task)
            menu.add_separator()
            menu.add_command(label="Cancel All Tasks", command=self.cancel_all_tasks)
            menu.add_separator()
            menu.add_command(label="Refresh", command=self.refresh, accelerator="F5")

        menu.post(event.x_root, event.y_root)

    def get_selected_task(self):
        """Get the currently selected task."""
        selection = self.task_tree.selection()
        if not selection:
            return None

        item = selection[0]
        values = self.task_tree.item(item, 'values')

        if not values:
            return None

        # Get full task details from queue
        task_id = values[0]
        queue_state = self.queue.get_queue_state()

        # Search in all task lists
        for task in (queue_state.pending_tasks +
                    queue_state.active_workflows +
                    queue_state.completed_tasks +
                    queue_state.failed_tasks):
            if task.id == task_id:
                return task

        return None

    def create_task(self):
        """Show create task dialog."""
        if self.state.connection_state != ConnectionState.CONNECTED:
            messagebox.showwarning("Not Connected", "Please connect to a queue manager first.")
            return

        dialog = CreateTaskDialog(self.root, self.queue, self.settings)
        if dialog.result:
            # Task was created
            task_id = dialog.result

            # Check if we should start it immediately
            if dialog.should_start:
                try:
                    # Start the task (flags were already set during add_task)
                    process = self.queue.start_task(task_id)
                except Exception as e:
                    messagebox.showerror("Error", f"Task created but failed to start: {e}")

            self.refresh()

    def start_task(self):
        """Start the selected task."""
        task = self.get_selected_task()
        if not task:
            messagebox.showwarning("No Selection", "Please select a task to start.")
            return

        if task.status != 'pending':
            messagebox.showwarning("Invalid Status", "Only pending tasks can be started.")
            return

        # Confirm
        if messagebox.askyesno("Confirm", f"Start task {task.id}?\n\nThe agent will run in the background."):
            try:
                # Start task asynchronously (non-blocking)
                process = self.queue.start_task(task.id)

                # Immediately refresh to show the task as active
                self.refresh()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to start task: {e}")

    def cancel_task(self):
        """Cancel the selected task."""
        task = self.get_selected_task()
        if not task:
            messagebox.showwarning("No Selection", "Please select a task to cancel.")
            return

        if task.status not in ['pending', 'active']:
            messagebox.showwarning("Invalid Status", "Only pending or active tasks can be cancelled.")
            return

        # Confirm
        if messagebox.askyesno("Confirm", f"Cancel task {task.id}?"):
            try:
                self.queue.cancel_task(task.id, "Cancelled by user")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to cancel task: {e}")

    def cancel_all_tasks(self):
        """Cancel all pending and active tasks."""
        if self.state.connection_state != ConnectionState.CONNECTED:
            return

        # Confirm
        if messagebox.askyesno("Confirm", "Cancel ALL pending and active tasks?"):
            try:
                self.queue.cancel_all_tasks("Bulk cancellation by user")
                self.refresh()
                messagebox.showinfo("Success", "All tasks cancelled.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to cancel tasks: {e}")

    def show_task_details(self):
        """Show task details dialog."""
        task = self.get_selected_task()
        if task:
            TaskDetailsDialog(self.root, task, self.queue)

    def show_task_log(self):
        """Show task log."""
        task = self.get_selected_task()
        if task:
            log_content = self.queue.get_task_log(task.id, task.source_file)
            if log_content:
                # TODO: Show log viewer dialog
                messagebox.showinfo("Task Log", f"Log for {task.id}:\n\n{log_content[:500]}...")
            else:
                messagebox.showinfo("No Log", f"No log found for task {task.id}")

    def copy_task_id(self):
        """Copy selected task ID to clipboard."""
        task = self.get_selected_task()
        if task:
            self.root.clipboard_clear()
            self.root.clipboard_append(task.id)
            messagebox.showinfo("Copied", f"Task ID copied to clipboard: {task.id}")

    def show_operations_log(self):
        """Show operations log dialog."""
        if self.state.connection_state != ConnectionState.CONNECTED:
            messagebox.showwarning("Not Connected", "Please connect to a queue manager first.")
            return

        OperationsLogDialog(self.root, self.queue)

    def configure_api_key(self):
        """Show dialog to configure Claude API key."""
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Configure Claude API Key")
        dialog.geometry("500x250")
        dialog.transient(self.root)
        dialog.grab_set()

        # Center on parent
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Info label
        info_text = ("Enter your Claude API key to enable AI-powered task description generation.\n"
                    "Your API key will be stored securely in your local settings.")
        ttk.Label(main_frame, text=info_text, wraplength=450).pack(pady=(0, 10))

        # API Key entry
        ttk.Label(main_frame, text="Claude API Key:").pack(anchor=tk.W)
        api_key_var = tk.StringVar()

        # Get existing key if available
        existing_key = self.settings.get_claude_api_key()
        if existing_key:
            # Show masked version
            api_key_var.set(existing_key)

        api_key_entry = ttk.Entry(main_frame, textvariable=api_key_var, width=60, show="*")
        api_key_entry.pack(fill=tk.X, pady=(0, 10))

        # Show/Hide checkbox
        show_var = tk.BooleanVar(value=False)
        def toggle_show():
            api_key_entry.config(show="" if show_var.get() else "*")

        ttk.Checkbutton(main_frame, text="Show API Key", variable=show_var, command=toggle_show).pack(anchor=tk.W)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)

        def save_key():
            api_key = api_key_var.get().strip()
            if api_key:
                self.settings.set_claude_api_key(api_key)
                dialog.destroy()
            else:
                messagebox.showwarning("Empty Key", "Please enter an API key or click Clear to remove it.")

        def clear_key():
            if messagebox.askyesno("Confirm", "Remove the stored Claude API key?"):
                self.settings.clear_claude_api_key()
                dialog.destroy()

        ttk.Button(button_frame, text="Save", command=save_key).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=clear_key).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def show_about_dialog(self):
        """Show about dialog."""
        AboutDialog(self.root)

    def show_agent_manager(self):
        """Show agent manager dialog."""
        if self.state.connection_state != ConnectionState.CONNECTED:
            messagebox.showwarning("Not Connected", "Please connect to a queue manager first.")
            return

        AgentManagerDialog(self.root, self.queue, self.settings)

    def sort_by(self, column):
        """Sort table by column."""
        # Toggle sort direction
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        # Get all items
        items = [(self.task_tree.set(item, column), item)
                for item in self.task_tree.get_children('')]

        # Sort
        items.sort(reverse=self.sort_reverse)

        # Rearrange items
        for index, (val, item) in enumerate(items):
            self.task_tree.move(item, '', index)

    def quit_app(self):
        """Quit the application."""
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.root.quit()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = TaskQueueUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()