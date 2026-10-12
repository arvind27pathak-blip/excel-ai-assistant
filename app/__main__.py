#!/usr/bin/env python3
"""
Excel AI Assistant - Main Application Entry Point

This application allows users to apply AI transformations to Excel and CSV data
using OpenAI's API.
"""

import os
import sys
import tkinter as tk

# Local application imports
from app.config import AppConfig
from app.ui.main_window import ExcelAIAssistantApp
from app.utils.theme_manager import ThemeManager


def main():
    """Main application entry point and installed-environment diagnostics."""
    import argparse
    parser = argparse.ArgumentParser(description='Excel AI Assistant')
    parser.add_argument('--check-install', action='store_true', help='Check dependencies and the Tk display without contacting an AI provider')
    arguments = parser.parse_args()
    if arguments.check_install:
        return check_install()
    # Create the root window
    root = tk.Tk()
    root.title("Excel AI Assistant")
    root.geometry("1200x800")
    root.minsize(900, 600)

    # Set application icon if available
    try:
        if sys.platform == "darwin":  # macOS
            # macOS handles app icons differently
            pass
        elif sys.platform == "win32":  # Windows
            root.iconbitmap(os.path.join(os.path.dirname(__file__), "resources", "app_icon.ico"))
        else:  # Linux/Unix
            img = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__), "resources", "app_icon.png"))
            root.tk.call('wm', 'iconphoto', root._w, img)
    except Exception:
        # If icon loading fails, continue without an icon
        pass

    # Load configuration
    config = AppConfig()

    # Setup theme manager
    theme_manager = ThemeManager(root)

    # Default to system theme if possible, otherwise use light theme
    system_theme = theme_manager.detect_system_theme()
    theme_manager.set_theme(config.get('theme', system_theme or 'light'))

    # Initialize the main application
    app = ExcelAIAssistantApp(root, config, theme_manager)

    # Start the application main loop
    root.mainloop()

    # Save configuration on exit
    config.save()


def check_install():
    """Exercise the installed package with an actual Tk root and no user settings."""
    import importlib.metadata
    import json
    root = tk.Tk()
    root.withdraw()
    try:
        from tkinter import ttk
        tree = ttk.Treeview(root, columns=['test'], show='headings')
        tree.insert('', 'end', values=['ready'])
        root.update_idletasks()
        print(json.dumps({
            'status': 'ok', 'python': sys.version.split()[0],
            'package_path': os.path.dirname(__file__),
            'tk': root.tk.call('info', 'patchlevel'),
            'dependencies': {name: importlib.metadata.version(name) for name in
                ['pandas', 'numpy', 'openai', 'openpyxl', 'python-dotenv', 'requests']}
        }, indent=2))
    finally:
        root.destroy()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
