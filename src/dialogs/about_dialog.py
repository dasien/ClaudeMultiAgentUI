"""
About dialog showing application information.
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path

from ..config import Config

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


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

        # Icon
        try:
            icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.png"
            if icon_path.exists() and PIL_AVAILABLE:
                img = Image.open(icon_path)
                img = img.resize((96, 96), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                icon_label = ttk.Label(main_frame, image=photo)
                icon_label.image = photo  # Keep reference
                icon_label.pack(pady=(0, 10))
        except Exception as e:
            print(f"Could not load icon: {e}")

        # Title
        ttk.Label(
            main_frame,
            text="Claude Multi-Agent Manager",
            font=('Arial', 16, 'bold')
        ).pack(pady=10)

        ttk.Label(
            main_frame,
            text="Version 1.0.3",
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