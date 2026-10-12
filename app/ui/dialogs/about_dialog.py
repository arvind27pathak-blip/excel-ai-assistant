"""
About dialog for Excel AI Assistant.
"""

import platform
import tkinter as tk
from tkinter import ttk

import pandas as pd
from app import __version__


class AboutDialog:
    """About dialog showing application information"""

    def __init__(self, parent: tk.Tk):
        """Initialize the about dialog"""
        self.parent = parent

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("About Excel AI Assistant")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (parent.winfo_width() // 2) - (width // 2) + parent.winfo_x()
        y = (parent.winfo_height() // 2) - (height // 2) + parent.winfo_y()
        self.dialog.geometry(f"+{x}+{y}")

        # Create content
        self._create_content()

    def _create_content(self):
        """Create dialog content"""
        # Main frame with padding
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # App name and version
        app_name = ttk.Label(main_frame, text="Excel AI Assistant", font=("Helvetica", 16, "bold"))
        app_name.pack(pady=(0, 5))

        version = ttk.Label(main_frame, text=f"Version {__version__} (beta)")
        version.pack(pady=(0, 10))

        # Description
        description = ttk.Label(
            main_frame,
            text="An application for applying AI transformations to Excel and CSV data using OpenAI's API.",
            wraplength=400,
            justify=tk.CENTER
        )
        description.pack(pady=(0, 20))

        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # System information
        sys_frame = ttk.LabelFrame(main_frame, text="System Information")
        sys_frame.pack(fill=tk.X, pady=10)

        # Grid for system info
        sys_frame.columnconfigure(0, weight=1)
        sys_frame.columnconfigure(1, weight=2)

        # Python version
        ttk.Label(sys_frame, text="Python Version:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(sys_frame, text=platform.python_version()).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        # Operating System
        ttk.Label(sys_frame, text="Operating System:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(sys_frame, text=f"{platform.system()} {platform.release()}").grid(row=1, column=1, sticky=tk.W,
                                                                                    padx=5, pady=2)

        # Pandas version
        ttk.Label(sys_frame, text="Pandas Version:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(sys_frame, text=pd.__version__).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

        # Tkinter version
        ttk.Label(sys_frame, text="Tkinter Version:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        tk_version = f"{tk.TkVersion} (Tcl {tk.TclVersion})"
        ttk.Label(sys_frame, text=tk_version).grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)

        # Credits
        credits_frame = ttk.Frame(main_frame)
        credits_frame.pack(fill=tk.X, pady=10)

        credits_text = (
            "Created for data professionals to streamline AI-assisted data transformations.\n"
            "Uses OpenAI API for intelligent text processing."
        )

        credits = ttk.Label(
            credits_frame,
            text=credits_text,
            wraplength=400,
            justify=tk.CENTER
        )
        credits.pack(pady=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.RIGHT)
