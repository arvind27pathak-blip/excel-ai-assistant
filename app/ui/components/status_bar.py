"""
Status bar component for Excel AI Assistant.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional


class StatusBar:
    """Enhanced status bar with message types"""

    def __init__(self, parent: tk.Tk):
        """Initialize the status bar"""
        self.parent = parent

        # Create frame for status bar
        self.frame = ttk.Frame(parent, relief=tk.SUNKEN)
        self.frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Configure grid
        self.frame.columnconfigure(0, weight=1)  # Message expands
        self.frame.columnconfigure(1, weight=0)  # Fixed width for status icon

        # Status message
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            self.frame,
            textvariable=self.status_var,
            anchor=tk.W,
            padding=(5, 3)
        )
        self.status_label.grid(row=0, column=0, sticky=tk.W + tk.E)

        # Status icon
        self.icon_label = ttk.Label(self.frame, text="", width=3)
        self.icon_label.grid(row=0, column=1, sticky=tk.E, padx=5)

        # Progress indicator (initially hidden)
        self.progress_var = tk.IntVar(value=0)
        self.progress = ttk.Progressbar(
            self.frame,
            mode="indeterminate",
            variable=self.progress_var
        )

        # Auto-clear timer ID
        self.clear_timer = None

    def set_status(self, message: str, status_type: str = "normal", auto_clear: bool = False, timeout: int = 5000):
        """
        Set the status message

        Args:
            message: Status message
            status_type: Type of status (normal, info, warning, error, success)
            auto_clear: Whether to automatically clear the message after timeout
            timeout: Time in milliseconds before clearing
        """
        # Update message
        self.status_var.set(message)

        # Clear any existing auto-clear timer
        if self.clear_timer:
            self.parent.after_cancel(self.clear_timer)
            self.clear_timer = None

        # Reset progress bar if visible
        if self.progress.winfo_viewable():
            self.hide_progress()

        # Apply style based on status type
        if status_type == "info":
            self.status_label.configure(style="")
            self.icon_label.configure(text="ℹ")
        elif status_type == "warning":
            self.status_label.configure(style="")
            self.icon_label.configure(text="⚠")
        elif status_type == "error":
            self.status_label.configure(style="")
            self.icon_label.configure(text="✖")
        elif status_type == "success":
            self.status_label.configure(style="")
            self.icon_label.configure(text="✓")
        else:
            # Normal status
            self.status_label.configure(style="")
            self.icon_label.configure(text="")

        # Set up auto-clear if requested
        if auto_clear:
            # noinspection PyTypeChecker
            self.clear_timer = self.parent.after(timeout, self.clear)

    def clear(self):
        """Clear the status message"""
        self.status_var.set("Ready")
        self.icon_label.configure(text="")
        self.clear_timer = None

    def show_progress(self, mode: str = "indeterminate"):
        """
        Show progress indicator

        Args:
            mode: Progress bar mode ('indeterminate' or 'determinate')
        """
        # Hide the icon
        self.icon_label.grid_forget()

        # Configure progress bar
        # noinspection PyTypeChecker
        self.progress.configure(mode=mode)
        if mode == "indeterminate":
            self.progress.start(50)  # Start animation

        # Show progress bar
        self.progress.grid(row=0, column=1, sticky=tk.E, padx=5)

    def update_progress(self, value: int, maximum: Optional[int] = None):
        """
        Update progress bar value

        Args:
            value: Current progress value
            maximum: Maximum progress value (if None, don't change)
        """
        if not self.progress.winfo_viewable():
            self.show_progress(mode="determinate")

        if maximum is not None:
            self.progress.configure(maximum=maximum)

        self.progress_var.set(value)

    def hide_progress(self):
        """Hide progress indicator"""
        # Stop animation if running
        if self.progress['mode'] == 'indeterminate':
            self.progress.stop()

        # Hide progress bar
        self.progress.grid_forget()

        # Show icon again
        self.icon_label.grid(row=0, column=1, sticky=tk.E, padx=5)

    def update_theme(self, is_dark: bool):
        """Update status bar colors for the current theme"""
        if is_dark:
            self.frame.configure(style="Dark.TFrame")
            self.status_label.configure(style="Dark.TLabel")
            self.icon_label.configure(style="Dark.TLabel")
        else:
            self.frame.configure(style="")
            self.status_label.configure(style="")
            self.icon_label.configure(style="")
