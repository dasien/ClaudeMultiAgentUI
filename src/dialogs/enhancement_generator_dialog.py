"""
Enhancement Generator Dialog - Create enhancement files with Claude API assistance.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json
import urllib.request
import re
from datetime import date
import threading
from .claude_working_dialog import ClaudeWorkingDialog

class EnhancementGeneratorDialog:
    """Dialog for generating enhancement files with Claude API."""

    def __init__(self, parent, queue_interface, settings):
        self.queue = queue_interface
        self.settings = settings
        self.result = None  # Path to created file

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Generate New Enhancement")
        self.dialog.geometry("750x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center on parent
        self.center_on_parent(parent)

        # Reference files list
        self.reference_files = []

        self.build_ui()
        self.dialog.wait_window()

    def center_on_parent(self, parent):
        """Center dialog on parent window."""
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

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

        # Enhancement Title
        ttk.Label(main_frame, text="Enhancement Title: *").pack(anchor="w")
        self.title_var = tk.StringVar()
        self.title_var.trace_add('write', self.on_title_changed)
        self.title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=70)
        self.title_entry.pack(fill="x", pady=(0, 10))

        # Filename
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

        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(10, 0))

        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side="left", padx=5)

        ttk.Label(main_frame, text="* Required fields", font=('Arial', 8), foreground='gray').pack(pady=(10, 0))

        # Validate initially
        self.validate_form()

        # Set focus
        self.dialog.after(100, self.title_entry.focus_set)

    def on_title_changed(self, *args):
        """Auto-generate filename from title if enabled."""
        if self.auto_filename_var.get():
            title = self.title_var.get().strip()
            slug = self.title_to_slug(title)
            self.filename_var.set(slug)
        self.validate_form()

    def title_to_slug(self, title: str) -> str:
        """Convert title to slug format."""
        # Convert to lowercase
        slug = title.lower()
        # Replace spaces and underscores with hyphens
        slug = re.sub(r'[\s_]+', '-', slug)
        # Remove non-alphanumeric characters except hyphens
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        # Strip leading/trailing hyphens
        slug = slug.strip('-')
        return slug

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
                # Show relative path if possible
                try:
                    rel_path = Path(file).relative_to(self.queue.project_root)
                    self.ref_listbox.insert(tk.END, str(rel_path))
                except ValueError:
                    self.ref_listbox.insert(tk.END, file)

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
        has_filename = bool(filename) and self.is_valid_slug(filename)
        has_description = bool(description)  # Just needs any content

        # Update filename validation label
        if filename and not self.is_valid_slug(filename):
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

    def is_valid_slug(self, slug: str) -> bool:
        """Check if slug is valid format."""
        return bool(re.match(r'^[a-z0-9-]+$', slug))

    def generate_enhancement(self):
        """Generate enhancement file with Claude API."""
        # Check API key
        api_key = self.settings.get_claude_api_key()
        if not api_key:
            messagebox.showwarning(
                "No API Key",
                "Claude API key not configured.\n\n"
                "Go to Settings > Configure Claude API Key..."
            )
            return

        # Gather form data
        title = self.title_var.get().strip()
        filename = self.filename_var.get().strip()
        directory = self.directory_var.get().strip()
        description = self.description_text.get('1.0', tk.END).strip()

        # Build context for Claude
        context = self.build_generation_context(title, description)

        # Show working dialog
        working_dialog = ClaudeWorkingDialog(
            self.dialog,
            "Generating enhancement specification",
            "30-60 seconds"
        ).show()

        # Run API call in separate thread
        def api_thread():
            try:
                generated_content = self.call_claude_api(context)
                # Schedule UI update on main thread
                self.dialog.after(0, lambda: self.on_generation_complete(
                    generated_content, title, filename, directory, working_dialog
                ))
            except Exception as e:
                # Schedule error handling on main thread
                self.dialog.after(0, lambda: self.on_generation_error(e, working_dialog))

        thread = threading.Thread(target=api_thread, daemon=True)
        thread.start()

    def on_generation_complete(self, content, title, filename, directory, working_dialog):
        """Handle successful generation (runs on UI thread)."""
        working_dialog.close()
        self.show_preview(content, title, filename, directory)

    def on_generation_error(self, error, working_dialog):
        """Handle generation error (runs on UI thread)."""
        working_dialog.close()
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
                    if path.exists() and path.stat().st_size < 100_000:  # Max 100KB per file
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if len(content) > 10_000:  # Truncate large files
                                content = content[:10_000] + "\n...[truncated]"

                            # Show relative path if possible
                            try:
                                rel_path = path.relative_to(self.queue.project_root)
                                context_parts.append(f"\n--- {rel_path} ---")
                            except ValueError:
                                context_parts.append(f"\n--- {path.name} ---")

                            context_parts.append(content)
                except Exception as e:
                    print(f"Could not read reference file {file_path}: {e}")

        return "\n".join(context_parts)

    def call_claude_api(self, context_prompt: str) -> str:
        """Call Claude API to generate enhancement."""
        api_key = self.settings.get_claude_api_key()
        config = self.settings.get_claude_config()
        model = config['model']
        max_tokens = config['max_tokens']
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

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

## Context & Background
**Current State:**
- What exists today
- Why this enhancement is needed

**Technical Context:**
- Target platform/environment
- Dependencies
- Integration points

## Requirements

### Functional Requirements
1. [Specific capability]
2. [Another requirement]

### Non-Functional Requirements
- **Performance:** [metrics]
- **Memory:** [constraints]
- **Reliability:** [requirements]

### Must Have (MVP)
- [ ] Feature X
- [ ] Feature Y

### Should Have (if time permits)
- [ ] Enhancement A

### Won't Have (out of scope)
- Feature X (reason)

## Open Questions
1. [Question about design approach]
2. [Question about requirements]

## Constraints & Limitations
**Technical Constraints:**
- [Constraint 1]

**Business/Timeline Constraints:**
- [Constraint 1]

## Success Criteria
**Definition of Done:**
- [ ] Criteria 1
- [ ] Criteria 2

**Acceptance Tests:**
1. Given [state], when [action], then [result]

## Security & Safety Considerations
- Data validation requirements
- Error handling approach
- Potential risks and mitigations

## Testing Strategy
**Unit Tests:**
- [Test area 1]

**Integration Tests:**
- [Test scenario 1]

**Manual Test Scenarios:**
1. [Step-by-step test]

## References & Research
- [Link to relevant documentation]
- [Similar implementations]

Generate detailed, comprehensive content for each section. Be specific and actionable."""

        data = {
            "model": model,  # Use configured model
            "max_tokens": max_tokens,  # Use configured max tokens
            "messages": [{"role": "user", "content": context_prompt}]
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['content'][0]['text']

    def show_preview(self, content: str, title: str, filename: str, directory: str):
        """Show preview of generated enhancement."""
        preview = tk.Toplevel(self.dialog)
        preview.title("Preview Enhancement")
        preview.geometry("900x700")
        preview.transient(self.dialog)
        preview.grab_set()

        # Center
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

                self.result = str(output_file)
                preview.destroy()
                self.dialog.destroy()

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

    def cancel(self):
        """Cancel dialog."""
        self.result = None
        self.dialog.destroy()