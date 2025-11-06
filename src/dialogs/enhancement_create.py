"""
Enhancement Generator Dialog - Create enhancement files with Claude API assistance.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import date

from .base_dialog import BaseDialog
from .mixins.claude_generator_mixin import ClaudeGeneratorMixin
from ..utils import to_slug, validate_slug, PathUtils


class CreateEnhancementDialog(BaseDialog, ClaudeGeneratorMixin):
    """Dialog for generating enhancement files with Claude API."""

    def __init__(self, parent, queue_interface, settings):
        # Initialize both base classes
        BaseDialog.__init__(self, parent, "Generate New Enhancement", 750, 700)
        ClaudeGeneratorMixin.__init__(self, settings)

        self.queue = queue_interface
        self.reference_files = []

        self.build_ui()
        self.show()  # Changed from wait() to show()

    def build_ui(self):
        """Build the dialog UI."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(
            main_frame,
            text="Generate Enhancement Specification",
            font=('Arial', 12, 'bold')
        ).pack(pady=(0, 15))

        # Enhancement Title - Using BaseDialog helper
        _, self.title_entry, self.title_var = self.create_label_entry_pair(
            main_frame,
            "Enhancement Title",
            width=70,
            required=True
        )
        self.title_var.trace_add('write', self.on_title_changed)

        # Filename with auto-generate
        filename_frame = ttk.Frame(main_frame)
        filename_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(filename_frame, text="Filename (slug): *").pack(side="left")
        self.auto_filename_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            filename_frame,
            text="Auto-generate from title",
            variable=self.auto_filename_var,
            command=self.toggle_filename_auto
        ).pack(side="right")

        self.filename_var = tk.StringVar()
        self.filename_entry = ttk.Entry(main_frame, textvariable=self.filename_var, width=70)
        self.filename_entry.pack(fill="x", pady=(0, 5))
        self.filename_entry.config(state='readonly')

        self.filename_validation_label = ttk.Label(
            main_frame,
            text="(lowercase, hyphens only: my-feature-name)",
            font=('Arial', 8),
            foreground='gray'
        )
        self.filename_validation_label.pack(anchor="w", pady=(0, 10))

        # Output Directory
        ttk.Label(main_frame, text="Output Directory: *").pack(anchor="w")
        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill="x", pady=(0, 10))

        self.directory_var = tk.StringVar()
        default_dir = self.queue.project_root / "enhancements"
        self.directory_var.set(str(default_dir))

        dir_entry = ttk.Entry(dir_frame, textvariable=self.directory_var)
        dir_entry.pack(side="left", fill="x", expand=True)

        ttk.Button(dir_frame, text="Browse...", command=self.browse_directory).pack(side="left", padx=(5, 0))

        # Reference Files
        ttk.Label(main_frame, text="Reference Files (optional):").pack(anchor="w", pady=(0, 5))

        ref_frame = ttk.Frame(main_frame)
        ref_frame.pack(fill="x", pady=(0, 10))

        # List of reference files
        list_frame = ttk.Frame(ref_frame)
        list_frame.pack(side="left", fill="both", expand=True)

        self.ref_listbox = tk.Listbox(list_frame, height=5, relief='flat', borderwidth=1, highlightthickness=1)
        ref_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.ref_listbox.yview)
        self.ref_listbox.configure(yscrollcommand=ref_scroll.set)

        self.ref_listbox.pack(side="left", fill="both", expand=True)
        ref_scroll.pack(side="right", fill="y")

        # Buttons for reference files
        ref_buttons = ttk.Frame(ref_frame)
        ref_buttons.pack(side="right", fill="y", padx=(5, 0))

        ttk.Button(ref_buttons, text="Add Files...", command=self.add_reference_files, width=12).pack(pady=2)
        ttk.Button(ref_buttons, text="Remove", command=self.remove_reference_file, width=12).pack(pady=2)
        ttk.Button(ref_buttons, text="Clear All", command=self.clear_reference_files, width=12).pack(pady=2)

        # Description
        desc_header = ttk.Frame(main_frame)
        desc_header.pack(fill="x", pady=(0, 5))

        ttk.Label(desc_header, text="Description: *").pack(side="left")

        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill="both", expand=True, pady=(0, 5))

        self.description_text = tk.Text(desc_frame, height=5, wrap="word")
        desc_scroll = ttk.Scrollbar(desc_frame, orient="vertical", command=self.description_text.yview)
        self.description_text.configure(yscrollcommand=desc_scroll.set)

        self.description_text.pack(side="left", fill="both", expand=True)
        desc_scroll.pack(side="right", fill="y")

        ttk.Label(
            main_frame,
            text="Describe what you want to accomplish and why",
            font=('Arial', 8),
            foreground='gray'
        ).pack(anchor="w", pady=(5, 15))

        # Generate Button
        self.generate_btn = ttk.Button(
            main_frame,
            text="Generate with Claude",
            command=self.generate_enhancement,
            state=tk.DISABLED
        )
        self.generate_btn.pack(pady=10)

        # Bottom buttons - Using BaseDialog helper
        self.create_button_frame(main_frame, [("Cancel", self.cancel)])

        ttk.Label(main_frame, text="* Required fields", font=('Arial', 8), foreground='gray').pack(pady=(10, 0))

        # Validate initially
        self.validate_form()

        # Set focus - Using BaseDialog helper
        self.set_focus(self.title_entry)

    def on_title_changed(self, *args):
        """Auto-generate filename from title if enabled."""
        if self.auto_filename_var.get():
            title = self.title_var.get().strip()
            slug = to_slug(title)  # Using utility function!
            self.filename_var.set(slug)
        self.validate_form()

    def toggle_filename_auto(self):
        """Toggle auto-generation of filename."""
        if self.auto_filename_var.get():
            self.filename_entry.config(state='readonly')
            self.on_title_changed()
        else:
            self.filename_entry.config(state='normal')

    def browse_directory(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(
            parent=self.dialog,
            title="Select Enhancement Output Directory",
            initialdir=self.directory_var.get(),
            mustexist=False
        )
        if directory:
            self.directory_var.set(directory)

    def add_reference_files(self):
        """Add reference files."""
        files = filedialog.askopenfilenames(
            parent=self.dialog,
            title="Select Reference Files",
            initialdir=str(self.queue.project_root),
            filetypes=[
                ("All Files", "*.*"),
                ("Markdown", "*.md"),
                ("Python", "*.py"),
                ("Text", "*.txt")
            ]
        )

        for file in files:
            if file not in self.reference_files:
                self.reference_files.append(file)
                # Using PathUtils!
                rel_path = PathUtils.relative_or_name(Path(file), self.queue.project_root)
                self.ref_listbox.insert(tk.END, rel_path)

    def remove_reference_file(self):
        """Remove selected reference file."""
        selection = self.ref_listbox.curselection()
        if selection:
            index = selection[0]
            self.ref_listbox.delete(index)
            del self.reference_files[index]

    def clear_reference_files(self):
        """Clear all reference files."""
        self.ref_listbox.delete(0, tk.END)
        self.reference_files.clear()

    def validate_form(self):
        """Validate form and enable/disable generate button."""
        title = self.title_var.get().strip()
        filename = self.filename_var.get().strip()
        description = self.description_text.get('1.0', tk.END).strip()

        # Check required fields
        has_title = bool(title)
        has_filename = bool(filename) and validate_slug(filename)  # Using utility!
        has_description = bool(description)

        # Update filename validation label
        if filename and not validate_slug(filename):  # Using utility!
            self.filename_validation_label.config(
                text="✗ Invalid format (use lowercase and hyphens only)",
                foreground='red'
            )
        elif filename:
            self.filename_validation_label.config(
                text="✓ Valid slug format",
                foreground='green'
            )
        else:
            self.filename_validation_label.config(
                text="(lowercase, hyphens only: my-feature-name)",
                foreground='gray'
            )

        # Enable/disable generate button
        if has_title and has_filename and has_description:
            self.generate_btn.config(state=tk.NORMAL)
        else:
            self.generate_btn.config(state=tk.DISABLED)

        # Schedule next validation
        self.dialog.after(500, self.validate_form)

    def generate_enhancement(self):
        """Generate enhancement file with Claude API."""
        # Gather form data
        title = self.title_var.get().strip()
        filename = self.filename_var.get().strip()
        directory = self.directory_var.get().strip()
        description = self.description_text.get('1.0', tk.END).strip()

        # Build context for Claude
        context = self.build_generation_context(title, description)

        system_prompt = """You are an expert technical writer creating detailed enhancement specifications.

Generate a comprehensive enhancement specification document following this structure:

---
slug: [filename-slug]
status: NEW
created: [YYYY-MM-DD]
author: [Author Name]
priority: medium
---

# Enhancement: [Title]

## Overview
**Goal:** One sentence describing what this enhancement accomplishes.

**User Story:**
As a [type of user], I want [goal] so that [benefit].

[Include all standard sections: Context, Requirements, Constraints, Testing, etc.]

Generate detailed, comprehensive content for each section. Be specific and actionable."""

        # Using ClaudeGeneratorMixin - Much simpler!
        self.call_claude_async(
            context=context,
            system_prompt=system_prompt,
            message="Generating enhancement specification",
            estimate="30-60 seconds",
            # timeout will use configured value from settings
            on_success=lambda content: self.on_generation_complete(content, title, filename, directory),
            on_error=self.on_generation_error
        )

    def on_generation_complete(self, content: str, title: str, filename: str, directory: str):
        """Handle successful generation."""
        self.show_preview(content, title, filename, directory)

    def on_generation_error(self, error: Exception):
        """Handle generation error."""
        messagebox.showerror("Generation Error", f"Failed to generate enhancement:\n\n{error}")

    def build_generation_context(self, title: str, description: str) -> str:
        """Build context for Claude API."""
        context_parts = [
            f"Enhancement Title: {title}",
            f"\nDescription: {description}"
        ]

        # Add reference files content
        if self.reference_files:
            context_parts.append("\n\nReference Documents:")
            for file_path in self.reference_files:
                try:
                    path = Path(file_path)
                    if path.exists() and path.stat().st_size < 100_000:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if len(content) > 10_000:
                                content = content[:10_000] + "\n...[truncated]"

                            # Using PathUtils!
                            rel_path = PathUtils.relative_or_name(path, self.queue.project_root)
                            context_parts.append(f"\n--- {rel_path} ---")
                            context_parts.append(content)
                except Exception as e:
                    print(f"Could not read reference file {file_path}: {e}")

        return "\n".join(context_parts)

    def show_preview(self, content: str, title: str, filename: str, directory: str):
        """Show preview of generated enhancement."""
        preview = tk.Toplevel(self.dialog)
        preview.title("Preview Enhancement")
        preview.geometry("900x700")
        preview.transient(self.dialog)
        preview.grab_set()

        # Center - could use BaseDialog if preview was a BaseDialog subclass
        preview.update_idletasks()
        x = self.dialog.winfo_x() + (self.dialog.winfo_width() // 2) - (preview.winfo_width() // 2)
        y = self.dialog.winfo_y() + (self.dialog.winfo_height() // 2) - (preview.winfo_height() // 2)
        preview.geometry(f"+{x}+{y}")

        main_frame = ttk.Frame(preview, padding=10)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(
            main_frame,
            text=f"Preview: {title}",
            font=('Arial', 12, 'bold')
        ).pack(pady=(0, 10))

        # Text area
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill="both", expand=True, pady=(0, 10))

        text_widget = tk.Text(text_frame, wrap="word", font=('Courier', 9))
        text_scroll_y = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_scroll_x = ttk.Scrollbar(text_frame, orient="horizontal", command=text_widget.xview)
        text_widget.configure(yscrollcommand=text_scroll_y.set, xscrollcommand=text_scroll_x.set)

        text_widget.grid(row=0, column=0, sticky='nsew')
        text_scroll_y.grid(row=0, column=1, sticky='ns')
        text_scroll_x.grid(row=1, column=0, sticky='ew')

        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        text_widget.insert('1.0', content)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        def save_enhancement():
            try:
                # Create directory structure
                output_dir = Path(directory) / filename
                output_dir.mkdir(parents=True, exist_ok=True)

                # Save file
                output_file = output_dir / f"{filename}.md"

                # Get potentially edited content
                final_content = text_widget.get('1.0', tk.END).strip()

                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(final_content)

                messagebox.showinfo(
                    "Success",
                    f"Enhancement saved successfully!\n\n{output_file}"
                )

                # Use BaseDialog.close() with result
                self.close(result=str(output_file))
                preview.destroy()

            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save enhancement:\n\n{e}")

        def regenerate():
            preview.destroy()
            self.generate_enhancement()

        ttk.Button(button_frame, text="💾 Save", command=save_enhancement, width=15).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🔄 Regenerate", command=regenerate, width=15).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=preview.destroy, width=15).pack(side="left", padx=5)

        ttk.Label(
            main_frame,
            text="You can edit the content above before saving",
            font=('Arial', 8),
            foreground='gray'
        ).pack()