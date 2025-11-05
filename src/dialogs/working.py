"""
Claude Working Dialog - Reusable animated progress dialog for Claude API calls.
Shows whimsical "Claude-ifying" style messages with spinner animation.
"""

import tkinter as tk
from tkinter import ttk
import random


class WorkingDialog:
    """Animated progress dialog with Claude's whimsical working messages."""

    # Unicode spinner frames (braille patterns)
    SPINNER_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

    # Claude's whimsical working words
    WORKING_WORDS = [
        # Classic Claude-isms
        "Claudeifying",
        "Bedazzling",
        "Cogitating",
        "Pondering",
        "Ruminating",
        "Contemplating",
        "Synthesizing",
        "Analyzing",
        "Processing",
        "Computing",

        # Creative thinking
        "Brainstorming",
        "Ideating",
        "Conceptualizing",
        "Envisioning",
        "Imagining",
        "Innovating",
        "Designing",
        "Crafting",
        "Composing",
        "Formulating",

        # Data/AI themed
        "Tokenizing",
        "Embedding",
        "Inferring",
        "Predicting",
        "Modeling",
        "Optimizing",
        "Calibrating",
        "Fine-tuning",
        "Training",
        "Learning",

        # Whimsical/fun
        "Sprinkling magic",
        "Weaving spells",
        "Conjuring",
        "Enchanting",
        "Transmuting",
        "Alchemizing",
        "Mystifying",
        "Hexing (nicely)",
        "Bewitching",
        "Sorcerizing",

        # Professional but fun
        "Architecting",
        "Engineering",
        "Constructing",
        "Assembling",
        "Fabricating",
        "Manufacturing",
        "Producing",
        "Generating",
        "Creating",
        "Building",

        # Thinking words
        "Deliberating",
        "Meditating",
        "Reflecting",
        "Considering",
        "Evaluating",
        "Examining",
        "Studying",
        "Investigating",
        "Researching",
        "Exploring",

        # Writing themed
        "Drafting",
        "Authoring",
        "Penning",
        "Scribing",
        "Documenting",
        "Chronicling",
        "Recording",
        "Transcribing",
        "Noting",
        "Inscribing",

        # Organizational
        "Organizing",
        "Structuring",
        "Arranging",
        "Categorizing",
        "Sorting",
        "Classifying",
        "Ordering",
        "Systematizing",
        "Coordinating",
        "Orchestrating",

        # Quality focused
        "Refining",
        "Polishing",
        "Perfecting",
        "Enhancing",
        "Improving",
        "Upgrading",
        "Elevating",
        "Enriching",
        "Beautifying",
        "Optimizing",

        # Fun technical
        "Compiling",
        "Parsing",
        "Rendering",
        "Transpiling",
        "Minifying",
        "Bundling",
        "Deploying",
        "Initializing",
        "Bootstrapping",
        "Instantiating",

        # More whimsy
        "Pixel-pushing",
        "Bit-twiddling",
        "Quantum-leaping",
        "Neural-netting",
        "Cyber-spacing",
        "Matrix-diving",
    ]

    def __init__(self, parent, message="Generating", estimated_time="15-30 seconds"):
        """Initialize the working dialog.

        Args:
            parent: Parent window
            message: Base message (e.g., "Generating enhancement")
            estimated_time: Estimated time string (e.g., "15-30 seconds")
        """
        self.parent = parent
        self.base_message = message
        self.estimated_time = estimated_time

        self.dialog = None

        # Animation state
        self.spinner_index = 0
        self.word_index = 0
        self.current_word = random.choice(self.WORKING_WORDS)
        self.spinner_id = None
        self.word_id = None

    def show(self):
        """Show the working dialog and start animations."""
        if self.dialog:
            return  # Already shown

        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Working")
        self.dialog.geometry("400x150")
        self.dialog.transient(self.parent)
        self.dialog.resizable(False, False)

        # Center on parent
        self.center_on_parent()

        self.build_ui()
        self.start_animation()

    def center_on_parent(self):
        """Center dialog on parent window."""
        if not self.dialog:
            return

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
        """Build the dialog UI."""
        main_frame = ttk.Frame(self.dialog, padding=30)
        main_frame.pack(fill="both", expand=True)

        # Spinner and working word
        self.spinner_label = ttk.Label(
            main_frame,
            text="⠋",
            font=('Arial', 24),
            foreground='#6366f1'  # Indigo color
        )
        self.spinner_label.pack(pady=(0, 10))

        self.working_label = ttk.Label(
            main_frame,
            text=f"{self.current_word}...",
            font=('Arial', 12, 'bold'),
            foreground='#6366f1'
        )
        self.working_label.pack(pady=(0, 15))

        # Base message
        ttk.Label(
            main_frame,
            text=self.base_message,
            font=('Arial', 10)
        ).pack(pady=(0, 5))

        # Estimated time
        ttk.Label(
            main_frame,
            text=f"This typically takes {self.estimated_time}",
            font=('Arial', 9),
            foreground='gray'
        ).pack()

    def start_animation(self):
        """Start the spinner and word animations."""
        self.animate_spinner()
        self.animate_word()

    def animate_spinner(self):
        """Animate the spinner character."""
        if not self.dialog or not self.dialog.winfo_exists():
            return

        self.spinner_index = (self.spinner_index + 1) % len(self.SPINNER_FRAMES)
        self.spinner_label.config(text=self.SPINNER_FRAMES[self.spinner_index])

        # Update every 80ms for smooth animation
        self.spinner_id = self.dialog.after(80, self.animate_spinner)

    def animate_word(self):
        """Change the working word every few seconds."""
        if not self.dialog or not self.dialog.winfo_exists():
            return

        # Pick a new random word
        new_word = random.choice(self.WORKING_WORDS)
        # Make sure it's different from current
        while new_word == self.current_word and len(self.WORKING_WORDS) > 1:
            new_word = random.choice(self.WORKING_WORDS)

        self.current_word = new_word
        self.working_label.config(text=f"{self.current_word}...")

        # Change word every 10 seconds
        self.word_id = self.dialog.after(10000, self.animate_word)

    def stop_animation(self):
        """Stop all animations."""
        if self.spinner_id:
            self.dialog.after_cancel(self.spinner_id)
            self.spinner_id = None
        if self.word_id:
            self.dialog.after_cancel(self.word_id)
            self.word_id = None

    def close(self):
        """Close the dialog."""
        self.stop_animation()
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.destroy()
            self.dialog = None
