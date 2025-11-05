"""
Claude API Settings Dialog
Manages Claude API configuration including API key, model, and max tokens.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class ClaudeSettingsDialog:
    """Dialog for configuring Claude API settings."""

    # Available Claude models with their max output tokens
    CLAUDE_MODELS = {
        "claude-opus-4-20250514": {
            "name": "Claude Opus 4",
            "max_tokens": 16384,
            "description": "Most capable model, 16K output"
        },
        "claude-sonnet-4-5-20250929": {
            "name": "Claude Sonnet 4.5",
            "max_tokens": 8192,
            "description": "Smartest model, efficient, 8K output"
        },
        "claude-sonnet-4-20250514": {
            "name": "Claude Sonnet 4",
            "max_tokens": 8192,
            "description": "Balanced performance, 8K output"
        },
        "claude-haiku-4-20250514": {
            "name": "Claude Haiku 4",
            "max_tokens": 8192,
            "description": "Fastest and most cost-effective, 8K output"
        },
    }

    # Default model
    DEFAULT_MODEL = "claude-sonnet-4-5-20250929"

    def __init__(self, parent, settings):
        self.parent = parent
        self.settings = settings
        self.result = False

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Claude API Settings")
        self.dialog.geometry("600x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)

        # Center on parent
        self.center_on_parent()

        self.build_ui()
        self.load_current_settings()

        self.dialog.wait_window()

    def center_on_parent(self):
        """Center dialog on parent window."""
        self.dialog.update_idletasks()

        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()

        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)

        self.dialog.geometry(f"+{x}+{y}")

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

        # Create dropdown for model selection
        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            state='readonly',
            width=50
        )

        # Build dropdown values with formatted display names
        model_display_values = []
        self.model_id_map = {}  # Map display name to model ID

        for model_id, model_info in self.CLAUDE_MODELS.items():
            display = f"{model_info['name']} — {model_info['description']}"
            model_display_values.append(display)
            self.model_id_map[display] = model_id

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

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(20, 0))

        ttk.Button(
            button_frame,
            text="Save Settings",
            command=self.save_settings,
            width=15
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Reset to Defaults",
            command=self.reset_to_defaults,
            width=15
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel,
            width=15
        ).pack(side="left", padx=5)

    def toggle_api_key_visibility(self):
        """Toggle API key visibility."""
        if self.show_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="•")

    def on_model_changed(self, event=None):
        """Handle model selection change."""
        # Get model ID from display name
        display_name = self.model_var.get()
        model_id = self.model_id_map.get(display_name)

        if model_id and model_id in self.CLAUDE_MODELS:
            model_info = self.CLAUDE_MODELS[model_id]
            default_tokens = model_info["max_tokens"]

            # Update max tokens to model's default if current value is from another model
            current_tokens = self.max_tokens_var.get()
            if not current_tokens or int(current_tokens) in [m["max_tokens"] for m in self.CLAUDE_MODELS.values()]:
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
        if not model_id or model_id not in self.CLAUDE_MODELS:
            model_id = self.DEFAULT_MODEL

        # Find the display name for this model ID
        model_info = self.CLAUDE_MODELS[model_id]
        display_name = f"{model_info['name']} — {model_info['description']}"
        self.model_var.set(display_name)

        # Load max tokens (with default based on model)
        max_tokens = self.settings.get_claude_max_tokens()
        if not max_tokens:
            max_tokens = self.CLAUDE_MODELS[model_id]["max_tokens"]
        self.max_tokens_var.set(str(max_tokens))

        # Trigger model change to update label
        self.on_model_changed()

    def reset_to_defaults(self):
        """Reset settings to defaults."""
        if messagebox.askyesno(
                "Reset to Defaults",
                "Reset Claude settings to defaults?\n\n"
                f"Model: {self.CLAUDE_MODELS[self.DEFAULT_MODEL]['name']}\n"
                f"Max Tokens: {self.CLAUDE_MODELS[self.DEFAULT_MODEL]['max_tokens']:,}\n\n"
                "Your API key will not be changed."
        ):
            self.model_var.set(self.DEFAULT_MODEL)
            self.max_tokens_var.set(str(self.CLAUDE_MODELS[self.DEFAULT_MODEL]["max_tokens"]))
            self.on_model_changed()

    def validate_settings(self):
        """Validate settings before saving."""
        # Validate API key (just check it's not empty)
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
            model_id = self.model_id_map.get(display_name)
            if model_id:
                model_max = self.CLAUDE_MODELS[model_id]["max_tokens"]
                if max_tokens > model_max:
                    if not messagebox.askyesno(
                            "Token Limit Exceeds Maximum",
                            f"You've set max tokens to {max_tokens:,}, but {self.CLAUDE_MODELS[model_id]['name']} "
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
        if not self.validate_settings():
            return

        try:
            # Save API key
            api_key = self.api_key_var.get().strip()
            self.settings.set_claude_api_key(api_key)

            # Save model (convert display name back to model ID)
            display_name = self.model_var.get()
            model_id = self.model_id_map.get(display_name)
            self.settings.set_claude_model(model_id)

            # Save max tokens
            max_tokens = int(self.max_tokens_var.get())
            self.settings.set_claude_max_tokens(max_tokens)

            self.result = True
            messagebox.showinfo(
                "Settings Saved",
                "Claude API settings saved successfully!"
            )
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror(
                "Save Error",
                f"Failed to save settings:\n\n{e}"
            )

    def cancel(self):
        """Cancel without saving."""
        self.result = False
        self.dialog.destroy()