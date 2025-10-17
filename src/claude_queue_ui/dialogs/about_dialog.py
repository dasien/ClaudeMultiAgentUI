"""
About dialog showing application information.
"""

import tkinter as tk
from tkinter import ttk

from ..config import Config


class AboutDialog:
    """About dialog."""

    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("About")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)

        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.build_ui()

    def build_ui(self):
        main_frame = ttk.Frame(self.dialog, padding=30)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Icon/Title
        ttk.Label(
            main_frame,
            text="📋 Task Queue Manager",
            font=('Arial', 16, 'bold')
        ).pack(pady=10)

        ttk.Label(
            main_frame,
            text=f"Version {Config.VERSION}",
            font=('Arial', 12)
        ).pack(pady=5)

        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)

        # Description
        desc_text = (
            "A graphical interface for managing multi-agent\n"
            "development workflows using Claude Code.\n\n"
            "Part of the Claude Multi-Agent Development Template"
        )
        ttk.Label(
            main_frame,
            text=desc_text,
            justify=tk.CENTER,
            font=('Arial', 10)
        ).pack(pady=10)

        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)

        # Credits
        ttk.Label(
            main_frame,
            text="Built with Python and Tkinter",
            font=('Arial', 9)
        ).pack(pady=5)

        ttk.Label(
            main_frame,
            text="© 2025 Claude Multi-Agent Template Project",
            font=('Arial', 9),
            foreground='gray'
        ).pack(pady=5)

        # Close button
        ttk.Button(
            main_frame,
            text="Close",
            command=self.dialog.destroy
        ).pack(pady=20)