"""
Claude API Settings Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox

from .base_dialog import BaseDialog
from ..config import ClaudeConfig


class ClaudeSettingsDialog(BaseDialog):
    """Dialog for configuring Claude API settings."""

    def __init__(self, parent, settings):
        super().__init__(parent, "Claude API Settings", 600, 550, resizable=False)
        self.settings = settings
        self.build_ui()
        self.load_current_settings()
        self.show()

    def build_ui(self):
        """Build the settings UI."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(
            main_frame,
            text="Configure Claude API",
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 20))

        # API Key Section
        key_frame = ttk.LabelFrame(main_frame, text="API Key", padding=15)
        key_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(
            key_frame,
            text="Your Claude API key (get one at console.anthropic.com):",
            font=('Arial', 9)
        ).pack(anchor="w", pady=(0, 5))

        key_entry_frame = ttk.Frame(key_frame)
        key_entry_frame.pack(fill="x", pady=(0, 10))

        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(
            key_entry_frame,
            textvariable=self.api_key_var,
            width=50,
            show="•"
        )
        self.api_key_entry.pack(side="left", fill="x", expand=True)

        self.show_key_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            key_frame,
            text="Show API Key",
            variable=self.show_key_var,
            command=self.toggle_api_key_visibility
        ).pack(anchor="w")

        # Model Selection Section
        model_frame = ttk.LabelFrame(main_frame, text="Model Selection", padding=15)
        model_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(
            model_frame,
            text="Choose which Claude model to use:",
            font=('Arial', 9)
        ).pack(anchor="w", pady=(0, 5))

        self.model_var = tk.StringVar()

        # Create dropdown using ClaudeConfig
        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            state='readonly',
            width=50
        )

        # Use ClaudeConfig helper methods
        model_display_values = ClaudeConfig.get_all_display_names()
        model_combo['values'] = model_display_values
        model_combo.pack(fill="x", pady=(0, 10))
        model_combo.bind('<<ComboboxSelected>>', self.on_model_changed)

        # Max Tokens Section
        tokens_frame = ttk.LabelFrame(main_frame, text="Output Token Limit", padding=15)
        tokens_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(
            tokens_frame,
            text="Maximum tokens for Claude's response:",
            font=('Arial', 9)
        ).pack(anchor="w", pady=(0, 5))

        tokens_entry_frame = ttk.Frame(tokens_frame)
        tokens_entry_frame.pack(fill="x", pady=(0, 5))

        self.max_tokens_var = tk.StringVar()
        self.max_tokens_entry = ttk.Entry(
            tokens_entry_frame,
            textvariable=self.max_tokens_var,
            width=10
        )
        self.max_tokens_entry.pack(side="left")

        self.max_tokens_label = ttk.Label(
            tokens_entry_frame,
            text="",
            font=('Arial', 9),
            foreground='gray'
        )
        self.max_tokens_label.pack(side="left", padx=(10, 0))

        ttk.Label(
            tokens_frame,
            text="Higher values allow longer responses but use more API credits.",
            font=('Arial', 8),
            foreground='gray',
            wraplength=550
        ).pack(anchor="w", pady=(5, 0))

        # Buttons - Using BaseDialog helper
        self.create_button_frame(main_frame, [
            ("Save Settings", self.save_settings),
            ("Reset to Defaults", self.reset_to_defaults),
            ("Cancel", self.cancel)
        ])

    def toggle_api_key_visibility(self):
        """Toggle API key visibility."""
        if self.show_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="•")

    def on_model_changed(self, event=None):
        """Handle model selection change."""
        display_name = self.model_var.get()
        model_id = ClaudeConfig.get_model_from_display(display_name)

        if model_id:
            default_tokens = ClaudeConfig.get_max_tokens(model_id)

            # Update max tokens to model's default if current value is from another model
            current_tokens = self.max_tokens_var.get()
            if not current_tokens or int(current_tokens) in [m["max_tokens"] for m in ClaudeConfig.MODELS.values()]:
                self.max_tokens_var.set(str(default_tokens))

            # Update label
            self.max_tokens_label.config(
                text=f"(Maximum for this model: {default_tokens:,})"
            )

    def load_current_settings(self):
        """Load current settings from Settings object."""
        # Load API key
        api_key = self.settings.get_claude_api_key()
        if api_key:
            self.api_key_var.set(api_key)

        # Load model (with default)
        model_id = self.settings.get_claude_model()
        if not model_id or model_id not in ClaudeConfig.MODELS:
            model_id = ClaudeConfig.DEFAULT_MODEL

        # Use ClaudeConfig helper
        display_name = ClaudeConfig.get_display_name(model_id)
        self.model_var.set(display_name)

        # Load max tokens (with default based on model)
        max_tokens = self.settings.get_claude_max_tokens()
        if not max_tokens:
            max_tokens = ClaudeConfig.get_max_tokens(model_id)
        self.max_tokens_var.set(str(max_tokens))

        # Trigger model change to update label
        self.on_model_changed()

    def reset_to_defaults(self):
        """Reset settings to defaults."""
        default_model_info = ClaudeConfig.get_model_info(ClaudeConfig.DEFAULT_MODEL)

        if messagebox.askyesno(
                "Reset to Defaults",
                "Reset Claude settings to defaults?\n\n"
                f"Model: {default_model_info['name']}\n"
                f"Max Tokens: {default_model_info['max_tokens']:,}\n\n"
                "Your API key will not be changed."
        ):
            display_name = ClaudeConfig.get_display_name(ClaudeConfig.DEFAULT_MODEL)
            self.model_var.set(display_name)
            self.max_tokens_var.set(str(ClaudeConfig.DEFAULT_MAX_TOKENS))
            self.on_model_changed()

    def validate(self) -> bool:
        """Validate settings before saving."""
        # Validate API key
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showwarning(
                "API Key Required",
                "Please enter your Claude API key.\n\n"
                "Get one at: console.anthropic.com"
            )
            return False

        # Validate max tokens
        try:
            max_tokens = int(self.max_tokens_var.get())
            if max_tokens < 1:
                messagebox.showwarning(
                    "Invalid Token Limit",
                    "Max tokens must be at least 1."
                )
                return False

            # Warn if exceeds model maximum
            display_name = self.model_var.get()
            model_id = ClaudeConfig.get_model_from_display(display_name)
            model_max = ClaudeConfig.get_max_tokens(model_id)
            model_name = ClaudeConfig.get_model_info(model_id)['name']

            if max_tokens > model_max:
                if not messagebox.askyesno(
                        "Token Limit Exceeds Maximum",
                        f"You've set max tokens to {max_tokens:,}, but {model_name} "
                        f"has a maximum of {model_max:,}.\n\n"
                        f"The API will use {model_max:,} tokens maximum.\n\n"
                        "Continue with this value?"
                ):
                    return False
        except ValueError:
            messagebox.showwarning(
                "Invalid Token Limit",
                "Max tokens must be a number."
            )
            return False

        return True

    def save_settings(self):
        """Save settings to Settings object."""
        if not self.validate():
            return

        try:
            # Save API key
            api_key = self.api_key_var.get().strip()
            self.settings.set_claude_api_key(api_key)

            # Save model
            display_name = self.model_var.get()
            model_id = ClaudeConfig.get_model_from_display(display_name)
            self.settings.set_claude_model(model_id)

            # Save max tokens
            max_tokens = int(self.max_tokens_var.get())
            self.settings.set_claude_max_tokens(max_tokens)

            messagebox.showinfo(
                "Settings Saved",
                "Claude API settings saved successfully!"
            )

            # Use BaseDialog.close() with result
            self.close(result=True)

        except Exception as e:
            messagebox.showerror(
                "Save Error",
                f"Failed to save settings:\n\n{e}"
            )