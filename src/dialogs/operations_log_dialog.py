"""
Operations log dialog for viewing queue operations log.
"""

import tkinter as tk
from tkinter import ttk


class OperationsLogDialog:
    """Dialog for viewing operations log."""

    def __init__(self, parent, queue_interface):
        self.queue = queue_interface

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Queue Operations Log")
        self.dialog.geometry("900x600")
        self.dialog.transient(parent)

        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.build_ui()
        self.load_log()

    def build_ui(self):
        # Header
        header_frame = ttk.Frame(self.dialog, padding=10)
        header_frame.pack(fill=tk.X)

        ttk.Label(header_frame, text="Log File: .claude/logs/queue_operations.log").pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Refresh", command=self.load_log).pack(side=tk.RIGHT)

        # Log text
        text_frame = ttk.Frame(self.dialog, padding=10)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.text_widget = tk.Text(text_frame, wrap=tk.NONE, font=('Courier', 9))
        scrollbar_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        scrollbar_x = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.text_widget.xview)
        self.text_widget.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.text_widget.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')

        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        # Footer
        footer_frame = ttk.Frame(self.dialog, padding=10)
        footer_frame.pack(fill=tk.X)

        self.status_label = ttk.Label(footer_frame, text="")
        self.status_label.pack(side=tk.LEFT)

        ttk.Button(footer_frame, text="Close", command=self.dialog.destroy).pack(side=tk.RIGHT)

    def load_log(self):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete('1.0', tk.END)

        try:
            log_content = self.queue.get_operations_log(max_lines=1000)
            self.text_widget.insert('1.0', log_content)

            # Auto-scroll to bottom
            self.text_widget.see(tk.END)

            # Update status
            lines = log_content.count('\n')
            self.status_label.config(text=f"Showing last {lines} lines")

        except Exception as e:
            self.text_widget.insert('1.0', f"Error loading log: {e}")
            self.status_label.config(text="Error")

        self.text_widget.config(state=tk.DISABLED)