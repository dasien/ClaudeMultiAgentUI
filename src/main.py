#!/usr/bin/env python3
"""
Multi-Agent Task Queue Manager v3.0
Enhanced with Skills, Workflows, and Integration features.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from .queue_interface import QueueInterface
from .models import ConnectionState, QueueUIState
from .config import Config
from .settings import Settings
from .utils import TimeUtils

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class TaskQueueUI:
    """Main application window for Task Queue Manager v3.0."""

    def __init__(self, root):
        self.root = root
        self.root.title("Claude Multi-Agent Manager")
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)

        # Set window icon
        self.set_window_icon()

        # Settings
        self.settings = Settings()

        # State
        self.state = QueueUIState()
        self.state.connection_state = ConnectionState.DISCONNECTED
        self.state.auto_refresh_enabled = False
        self.state.auto_refresh_interval = Config.AUTO_REFRESH_INTERVAL
        self.auto_refresh_timer = None

        # Queue interface
        self.queue = None

        # Build UI
        self.build_menu_bar()
        self.build_connection_header()
        self.build_task_table()
        self.build_status_bar()
        self.configure_styles()

        # Initial state
        self.update_ui_state()

        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        # Try auto-connect
        self.try_auto_connect()

    def set_window_icon(self):
        """Set the window icon."""
        try:
            # Get icon path
            assets_dir = Path(__file__).parent.parent / "assets"
            icon_png = assets_dir / "icon.png"

            # Try to load PNG icon with PIL
            if icon_png.exists() and PIL_AVAILABLE:
                # Load original image
                img = Image.open(icon_png)

                # Create icons at multiple sizes including high-res for dialogs
                # Start with largest first for better quality fallback
                sizes = [256, 128, 64, 48, 32, 16]
                photos = []

                for size in sizes:
                    resized = img.resize((size, size), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(resized)
                    photos.append(photo)

                # Set all icon sizes (largest first)
                # The True parameter makes it default for all child windows (messageboxes)
                self.root.iconphoto(True, *photos)

                # Keep references to prevent garbage collection
                self.root._icon_photos = photos
                print(f"Icon loaded successfully from {icon_png} ({len(sizes)} sizes)")
            else:
                if not icon_png.exists():
                    print(f"Icon file not found: {icon_png}")
                if not PIL_AVAILABLE:
                    print("PIL/Pillow not available for icon loading")

        except Exception as e:
            # Icon is optional, don't fail if it doesn't work
            print(f"Could not set window icon: {e}")

    def build_menu_bar(self):
        """Create enhanced menu bar with v3.0 features."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Connect...", command=self.show_connect_dialog, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.quit_app, accelerator="Ctrl+Q")

        # Tasks menu
        tasks_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tasks", menu=tasks_menu)
        tasks_menu.add_command(label="Create Task...", command=self.create_task, accelerator="Ctrl+N")
        tasks_menu.add_separator()
        tasks_menu.add_command(label="Cancel All Tasks", command=self.cancel_all_tasks)
        tasks_menu.add_separator()
        tasks_menu.add_command(label="Refresh List", command=self.refresh, accelerator="F5")

        # Agents menu
        agents_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Agents", menu=agents_menu)
        agents_menu.add_command(label="Manage Agents...", command=self.show_agent_manager)

        # Skills menu
        skills_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Skills", menu=skills_menu)
        skills_menu.add_command(label="Browse Skills...", command=self.show_skills_viewer, accelerator="Ctrl+K")
        skills_menu.add_separator()
        skills_menu.add_command(label="View Agent Skills...", command=self.show_agent_skills)

        # Enhancements menu
        enhancements_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Enhancements", menu=enhancements_menu)
        enhancements_menu.add_command(label="Generate...", command=self.show_enhancement_generator, accelerator="Ctrl+E")

        # Workflows menu
        workflows_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Workflows", menu=workflows_menu)
        workflows_menu.add_command(label="View Active Workflows...", command=self.show_workflow_viewer,
                                   accelerator="Ctrl+W")

        # Integration menu
        integration_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Integration", menu=integration_menu)
        integration_menu.add_command(label="Integration Dashboard...", command=self.show_integration_dashboard,
                                     accelerator="Ctrl+I")
        integration_menu.add_separator()
        integration_menu.add_command(label="Sync All Unsynced Tasks", command=self.sync_all_tasks)

        # Logs menu
        logs_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Logs", menu=logs_menu)
        logs_menu.add_command(label="View Operations Log", command=self.show_operations_log, accelerator="Ctrl+L")

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        self.auto_refresh_var = tk.BooleanVar(value=False)
        settings_menu.add_command(label="Claude Settings", command=self.configure_api_key)
        settings_menu.add_separator()
        settings_menu.add_checkbutton(label="Auto Refresh Task List", variable=self.auto_refresh_var, command=self.toggle_auto_refresh)

        # About menu
        about_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="About", menu=about_menu)
        about_menu.add_command(label="About Task Queue UI", command=self.show_about_dialog)

        # Keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.show_connect_dialog())
        self.root.bind('<Control-q>', lambda e: self.quit_app())
        self.root.bind('<Control-n>', lambda e: self.create_task())
        self.root.bind('<Control-e>', lambda e: self.show_enhancement_generator())
        self.root.bind('<Control-w>', lambda e: self.show_workflow_viewer())
        self.root.bind('<Control-k>', lambda e: self.show_skills_viewer())
        self.root.bind('<Control-i>', lambda e: self.show_integration_dashboard())
        self.root.bind('<Control-l>', lambda e: self.show_operations_log())
        self.root.bind('<F5>', lambda e: self.refresh())
        self.root.bind('<Delete>', lambda e: self.cancel_task())
        self.root.bind('<Return>', lambda e: self.start_task())

    def build_connection_header(self):
        """Create connection status header."""
        self.connection_frame = ttk.Frame(self.root, style='Connection.TFrame', padding=5)
        self.connection_frame.pack(fill="x")

        self.connection_label = ttk.Label(
            self.connection_frame,
            text="Not connected - File > Connect to select project",
            font=('Arial', 9),
            style='Connection.TLabel'
        )
        self.connection_label.pack(side="left")

        # System version indicator
        self.version_label = ttk.Label(
            self.connection_frame,
            text="",
            font=('Arial', 9),
            style='Connection.TLabel'
        )
        self.version_label.pack(side="right", padx=10)

    def build_task_table(self):
        """Create main task table with external links column."""
        table_frame = ttk.Frame(self.root, padding=10)
        table_frame.pack(fill="both", expand=True)

        label_frame = ttk.LabelFrame(table_frame, text="TASK QUEUE", padding=5)
        label_frame.pack(fill="both", expand=True)

        tree_frame = ttk.Frame(label_frame)
        tree_frame.pack(fill="both", expand=True)

        # Columns without external_links
        columns = ('task_id', 'title', 'agent', 'status', 'start_date', 'end_date', 'runtime')
        self.task_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )

        self.task_tree.heading('task_id', text='Task ID', command=lambda: self.sort_by('task_id'))
        self.task_tree.heading('title', text='Title', command=lambda: self.sort_by('title'))
        self.task_tree.heading('agent', text='Agent', command=lambda: self.sort_by('agent'))
        self.task_tree.heading('status', text='Status', command=lambda: self.sort_by('status'))
        self.task_tree.heading('start_date', text='Start Date', command=lambda: self.sort_by('start_date'))
        self.task_tree.heading('end_date', text='End Date', command=lambda: self.sort_by('end_date'))
        self.task_tree.heading('runtime', text='Runtime', command=lambda: self.sort_by('runtime'))

        self.task_tree.column('task_id', width=160, minwidth=120)
        self.task_tree.column('title', width=300, minwidth=200)
        self.task_tree.column('agent', width=150, minwidth=120)
        self.task_tree.column('status', width=90, minwidth=80)
        self.task_tree.column('start_date', width=140, minwidth=120)
        self.task_tree.column('end_date', width=140, minwidth=120)
        self.task_tree.column('runtime', width=80, minwidth=70)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.task_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.task_tree.xview)
        self.task_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.task_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Hint
        ttk.Label(
            label_frame,
            text="[Right-click for actions | Double-click for details | Ctrl+W for workflows]",
            font=('Arial', 9),
            foreground='gray'
        ).pack(pady=(5, 0))

        # Events
        self.task_tree.bind('<Double-Button-1>', self.on_double_click)
        self.task_tree.bind('<Button-3>', self.show_context_menu)
        self.task_tree.bind('<Button-2>', self.show_context_menu)
        self.task_tree.bind('<Control-Button-1>', self.show_context_menu)

        self.sort_column = None
        self.sort_reverse = False

    def build_status_bar(self):
        """Create status bar."""
        status_frame = ttk.Frame(self.root, relief="sunken", padding=2)
        status_frame.pack(fill="x", side="bottom")

        self.status_label = ttk.Label(status_frame, text="Not connected", font=('Arial', 9))
        self.status_label.pack(side="left", padx=5)

        self.refresh_label = ttk.Label(status_frame, text="Auto-refresh: OFF", font=('Arial', 9))
        self.refresh_label.pack(side="right", padx=5)

    def configure_styles(self):
        """Configure styles."""
        style = ttk.Style()
        style.configure('Connection.TFrame', background='#F0F0F0')
        style.configure('Connection.TLabel', background='#F0F0F0')

        self.task_tree.tag_configure('pending', background='white')
        self.task_tree.tag_configure('active', background='#FFF9E6')
        self.task_tree.tag_configure('completed', background='#E8F5E9')
        self.task_tree.tag_configure('failed', background='#FFEBEE')

    def update_ui_state(self):
        """Update UI based on connection state."""
        if self.state.connection_state == ConnectionState.DISCONNECTED:
            self.connection_label.config(text="Not connected - File > Connect")
            self.version_label.config(text="")
            self.status_label.config(text="Not connected")

            for item in self.task_tree.get_children():
                self.task_tree.delete(item)

        elif self.state.connection_state == ConnectionState.CONNECTED:
            self.connection_label.config(text=f"Connected: {self.state.project_root}")

            # Show system version
            version = self.queue.get_version()
            self.version_label.config(text=f"CMAT v{version}")

            if self.state.auto_refresh_enabled:
                self.start_auto_refresh()

        elif self.state.connection_state == ConnectionState.ERROR:
            self.connection_label.config(text=f"Error: {self.state.error_message}", foreground='red')

    def show_connect_dialog(self):
        """Show connect dialog."""
        from .dialogs import ConnectDialog
        dialog = ConnectDialog(self.root)
        if dialog.result:
            self.connect_to_queue(dialog.result)

    def try_auto_connect(self):
        """Try to auto-connect to last project."""
        last_path = self.settings.get_last_queue_manager()
        if last_path and Path(last_path).exists():
            try:
                self.connect_to_queue(last_path, silent=True)
            except Exception as e:
                print(f"Auto-connect failed: {e}")
                self.settings.clear_last_queue_manager()

    def connect_to_queue(self, cmat_path, silent=False):
        """Connect to a project."""
        try:
            # Initialize queue interface
            self.queue = QueueInterface(str(cmat_path))

            # Update state
            self.state.connection_state = ConnectionState.CONNECTED
            self.state.project_root = self.queue.project_root
            self.state.queue_file = self.queue.queue_file
            self.state.logs_dir = self.queue.logs_dir

            # Save path
            self.settings.set_last_queue_manager(str(cmat_path))

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
        """Refresh task list."""
        if self.state.connection_state != ConnectionState.CONNECTED:
            return

        try:
            queue_state = self.queue.get_queue_state()

            # Clear
            for item in self.task_tree.get_children():
                self.task_tree.delete(item)

            # Combine tasks
            all_tasks = (
                    queue_state.pending_tasks +
                    queue_state.active_workflows +
                    queue_state.completed_tasks[-50:] +
                    queue_state.failed_tasks
            )

            # Populate
            for task in all_tasks:
                status_display = task.status.capitalize()
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
                    tags=(task.status.lower(),)
                )

            # Update status
            self.status_label.config(
                text=f"{len(queue_state.pending_tasks)} Pending | "
                     f"{len(queue_state.active_workflows)} Active | "
                     f"{len(queue_state.completed_tasks)} Completed | "
                     f"{len(queue_state.failed_tasks)} Failed"
            )

        except Exception as e:
            messagebox.showerror("Refresh Error", f"Failed to refresh: {e}")

    def format_runtime(self, seconds):
        """Format runtime using TimeUtils."""
        return TimeUtils.format_runtime(seconds)

    def toggle_auto_refresh(self):
        """Toggle auto-refresh."""
        self.state.auto_refresh_enabled = self.auto_refresh_var.get()

        if self.state.auto_refresh_enabled:
            if self.state.connection_state == ConnectionState.CONNECTED:
                self.start_auto_refresh()
            self.refresh_label.config(text=f"Auto-refresh: ✓ ON ({self.state.auto_refresh_interval}s)")
        else:
            if self.auto_refresh_timer:
                self.root.after_cancel(self.auto_refresh_timer)
                self.auto_refresh_timer = None
            self.refresh_label.config(text="Auto-refresh: OFF")

    def start_auto_refresh(self):
        """Start auto-refresh timer."""
        if self.auto_refresh_timer:
            self.root.after_cancel(self.auto_refresh_timer)

        if self.state.auto_refresh_enabled and self.state.connection_state == ConnectionState.CONNECTED:
            self.refresh()
            interval_ms = self.state.auto_refresh_interval * 1000
            self.auto_refresh_timer = self.root.after(interval_ms, self.start_auto_refresh)

    def on_double_click(self, event):
        """Handle double-click - show enhanced details."""
        task = self.get_selected_task()
        if task:
            from .dialogs import TaskDetailsDialog
            TaskDetailsDialog(self.root, task, self.queue)

    def show_context_menu(self, event):
        """Show context menu."""
        item = self.task_tree.identify_row(event.y)
        menu = tk.Menu(self.root, tearoff=0)

        if item:
            self.task_tree.selection_set(item)
            task = self.get_selected_task()

            if task:
                can_start = task.status == 'pending'
                can_cancel = task.status in ['pending', 'active']

                menu.add_command(label="Start Task", command=self.start_task,
                                 state="normal" if can_start else "disabled")
                menu.add_command(label="Cancel Task", command=self.cancel_task,
                                 state="normal" if can_cancel else "disabled")
                menu.add_separator()
                menu.add_command(label="View Details...", command=self.show_task_details)

                if self.queue.task_log_exists(task.id, task.source_file):
                    menu.add_command(label="View Log...", command=self.show_task_log)

                menu.add_separator()

                # Integration options
                if task.status == 'completed' and task.metadata:
                    if not task.metadata.get('github_issue'):
                        menu.add_command(label="Sync to External Systems", command=lambda: self.sync_task(task.id))

                menu.add_separator()
                menu.add_command(label="Copy Task ID", command=self.copy_task_id)
        else:
            menu.add_command(label="Create Task...", command=self.create_task)
            menu.add_separator()
            menu.add_command(label="Refresh", command=self.refresh)

        menu.post(event.x_root, event.y_root)

    def get_selected_task(self):
        """Get selected task."""
        selection = self.task_tree.selection()
        if not selection:
            return None

        values = self.task_tree.item(selection[0], 'values')
        if not values:
            return None

        task_id = values[0]
        queue_state = self.queue.get_queue_state()

        for task in (queue_state.pending_tasks + queue_state.active_workflows +
                     queue_state.completed_tasks + queue_state.failed_tasks):
            if task.id == task_id:
                return task
        return None

    def create_task(self):
        """Show enhanced create task dialog."""
        if self.state.connection_state != ConnectionState.CONNECTED:
            messagebox.showwarning("Not Connected", "Please connect first.")
            return

        from .dialogs import CreateTaskDialog
        dialog = CreateTaskDialog(self.root, self.queue, self.settings)

        if dialog.result:
            if dialog.should_start:
                try:
                    self.queue.start_task(dialog.result)
                except Exception as e:
                    messagebox.showerror("Error", f"Created but failed to start: {e}")
            self.refresh()

    def quick_workflow(self, agent: str, workflow_name: str):
        """Quick start a workflow."""
        if self.state.connection_state != ConnectionState.CONNECTED:
            messagebox.showwarning("Not Connected", "Please connect first.")
            return

        # This would open Create Task dialog with pre-filled workflow settings
        self.create_task()

    def start_task(self):
        """Start selected task."""
        task = self.get_selected_task()
        if not task:
            messagebox.showwarning("No Selection", "Select a task to start.")
            return

        if task.status != 'pending':
            messagebox.showwarning("Invalid Status", "Only pending tasks can be started.")
            return

        if messagebox.askyesno("Confirm", f"Start task {task.id}?"):
            try:
                self.queue.start_task(task.id)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start: {e}")

    def cancel_task(self):
        """Cancel selected task."""
        task = self.get_selected_task()
        if not task or task.status not in ['pending', 'active']:
            return

        if messagebox.askyesno("Confirm", f"Cancel task {task.id}?"):
            try:
                self.queue.cancel_task(task.id, "Cancelled by user")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to cancel: {e}")

    def cancel_all_tasks(self):
        """Cancel all tasks."""
        if messagebox.askyesno("Confirm", "Cancel ALL pending and active tasks?"):
            try:
                self.queue.cancel_all_tasks("Bulk cancellation")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {e}")

    def sync_task(self, task_id: str):
        """Sync task to external systems."""
        try:
            self.queue.sync_task_external(task_id)
            messagebox.showinfo("Success", "Integration task created")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to sync: {e}")

    def sync_all_tasks(self):
        """Sync all unsynced tasks."""
        if messagebox.askyesno("Confirm", "Sync all unsynced tasks?"):
            try:
                self.queue.sync_all_external()
                messagebox.showinfo("Success", "Integration tasks created")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {e}")

    def show_task_details(self):
        """Show enhanced task details."""
        task = self.get_selected_task()
        if task:
            from .dialogs import TaskDetailsDialog
            TaskDetailsDialog(self.root, task, self.queue)

    def show_task_log(self):
        """Show task log."""
        task = self.get_selected_task()
        if task:
            # Use enhanced details which has better log viewer
            self.show_task_details()

    def copy_task_id(self):
        """Copy task ID."""
        task = self.get_selected_task()
        if task:
            self.root.clipboard_clear()
            self.root.clipboard_append(task.id)
            messagebox.showinfo("Copied", f"Task ID copied: {task.id}")

    def show_skills_viewer(self):
        """Show skills viewer dialog."""
        if self.state.connection_state != ConnectionState.CONNECTED:
            messagebox.showwarning("Not Connected", "Please connect first.")
            return

        from .dialogs import SkillsViewerDialog
        SkillsViewerDialog(self.root, self.queue)

    def show_agent_skills(self):
        """Show agent skills summary."""
        if self.state.connection_state != ConnectionState.CONNECTED:
            messagebox.showwarning("Not Connected", "Please connect first.")
            return

        # Create summary window
        window = tk.Toplevel(self.root)
        window.title("Agent Skills Summary")
        window.geometry("600x500")

        frame = ttk.Frame(window, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Agent Skills Summary", font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        text_widget = tk.Text(frame, wrap="word", font=('Courier', 9))
        scroll = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scroll.set)

        text_widget.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Build summary
        agents = self.queue.get_agent_list()
        for agent_file, agent_name in sorted(agents.items(), key=lambda x: x[1]):
            skills = self.queue.get_agent_skills(agent_file)
            text_widget.insert(tk.END, f"{agent_name}:\n", 'bold')

            if skills:
                for skill in skills:
                    text_widget.insert(tk.END, f"  • {skill}\n")
            else:
                text_widget.insert(tk.END, "  (no skills assigned)\n", 'gray')

            text_widget.insert(tk.END, "\n")

        text_widget.tag_config('bold', font=('Courier', 9, 'bold'))
        text_widget.tag_config('gray', foreground='gray')
        text_widget.config(state="disabled")

        ttk.Button(window, text="Close", command=window.destroy).pack(pady=10)

    def show_workflow_viewer(self):
        """Show workflow state viewer."""
        if self.state.connection_state != ConnectionState.CONNECTED:
            messagebox.showwarning("Not Connected", "Please connect first.")
            return

        from .dialogs import WorkflowStateViewer
        WorkflowStateViewer(self.root, self.queue)

    def show_enhancement_generator(self):
        """Show enhancement generator dialog."""
        if self.state.connection_state != ConnectionState.CONNECTED:
            messagebox.showwarning("Not Connected", "Please connect to a project first.")
            return

        from .dialogs import CreateEnhancementDialog
        dialog = CreateEnhancementDialog(self.root, self.queue, self.settings)

        if dialog.result:
            messagebox.showinfo(
                "Enhancement Created",
                f"Enhancement file created:\n\n{dialog.result}\n\n"
                "You can now create a task for this enhancement!"
            )

    def show_integration_dashboard(self):
        """Show integration dashboard."""
        if self.state.connection_state != ConnectionState.CONNECTED:
            messagebox.showwarning("Not Connected", "Please connect first.")
            return

        from .dialogs import IntegrationDashboardDialog
        IntegrationDashboardDialog(self.root, self.queue)

    def show_agent_manager(self):
        """Show enhanced agent manager."""
        if self.state.connection_state != ConnectionState.CONNECTED:
            messagebox.showwarning("Not Connected", "Please connect first.")
            return

        from .dialogs import AgentListDialog
        AgentListDialog(self.root, self.queue, self.settings)

    def show_operations_log(self):
        """Show operations log."""
        if self.state.connection_state != ConnectionState.CONNECTED:
            messagebox.showwarning("Not Connected", "Please connect first.")
            return

        from .dialogs import LogViewerDialog
        LogViewerDialog(self.root, self.queue)

    def configure_api_key(self):
        """Configure Claude API settings."""
        from .dialogs import ClaudeSettingsDialog
        ClaudeSettingsDialog(self.root, self.settings)

    def show_about_dialog(self):
        """Show about dialog."""
        from .dialogs import AboutDialog
        AboutDialog(self.root)

    def sort_by(self, column):
        """Sort table by column."""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        items = [(self.task_tree.set(item, column), item) for item in self.task_tree.get_children('')]
        items.sort(reverse=self.sort_reverse)

        for index, (val, item) in enumerate(items):
            self.task_tree.move(item, '', index)

    def quit_app(self):
        """Quit application."""
        if messagebox.askyesno("Quit", "Are you sure?"):
            self.root.quit()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = TaskQueueUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()