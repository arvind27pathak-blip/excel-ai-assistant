"""
Theme manager for the Excel AI Assistant.
Handles switching between light, dark, and system themes.
"""

import sys
import tkinter as tk
from tkinter import ttk


class ThemeManager:
    """
    Theme manager for handling light and dark mode with improved contrast.
    """

    def __init__(self, root):
        """Initialize the theme manager"""
        self.root = root
        self.theme_var = tk.StringVar(value="light")

        # Available themes with improved contrast
        self.themes = {
            'light': {
                'name': 'Light',
                'bg': '#ffffff',
                'fg': '#000000',
                'selectbg': '#0078d7',
                'selectfg': '#ffffff',
                'disabledfg': '#666666',  # Darker for better readability
                'insertbg': '#000000',
                'frame_bg': '#f0f0f0',
                'border': '#bbbbbb',  # Darker for better contrast
                'highlight_bg': '#d1e8ff',  # Brighter highlight
                'treeview_bg': '#ffffff',
                'treeview_fg': '#000000',  # Always black for cell text
                'treeview_rowbg_1': '#ffffff',
                'treeview_rowbg_2': '#f0f5fa',  # Subtle blue tint for better distinction
                'treeview_header_bg': '#e9e9e9',
                'treeview_header_fg': '#000000',
                'scrollbar_bg': '#f0f0f0',
                'scrollbar_fg': '#c0c0c0',  # Darker scrollbar for contrast
                'button_bg': '#f0f0f0',
                'button_fg': '#000000',
                'button_active_bg': '#e0e0e0',
                'entry_bg': '#ffffff',
                'text_bg': '#ffffff',
                'text_fg': '#000000',
                'tooltip_bg': '#fffff0',  # Light yellow
                'tooltip_fg': '#000000',
                'tab_bg': '#f0f0f0',
                'tab_selected_bg': '#ffffff',
                'status_bg': '#f5f5f5',
                'progress_bg': '#f0f0f0',
                'progress_fg': '#0078d7',
                'menu_bg': '#ffffff',
                'menu_fg': '#000000',
                'alert_success_bg': '#e6f7e6',
                'alert_success_fg': '#008000',
                'alert_error_bg': '#ffebeb',
                'alert_error_fg': '#cc0000',
                'alert_warning_bg': '#fff8e6',
                'alert_warning_fg': '#cc7700',
                'cell_text': '#000000',  # Always black for cell text
                'modified_bg': '#e0f0ff'  # Clearly visible but not distracting
            },
            'dark': {
                'name': 'Dark',
                'bg': '#1e1e1e',
                'fg': '#f0f0f0',  # Light gray instead of pure white for eye comfort
                'selectbg': '#0078d7',
                'selectfg': '#ffffff',
                'disabledfg': '#909090',  # Lighter for better visibility on dark
                'insertbg': '#cccccc',
                'frame_bg': '#252525',
                'border': '#555555',
                'highlight_bg': '#264f78',  # Blue that works well with dark theme
                'treeview_bg': '#2d2d2d',  # Slightly lighter than main bg
                'treeview_fg': '#000000',  # Always black for cell text
                'treeview_rowbg_1': '#2d2d2d',
                'treeview_rowbg_2': '#363636',  # Clear distinction between rows
                'treeview_header_bg': '#1f1f1f',  # Darker header
                'treeview_header_fg': '#f0f0f0',  # Light text
                'scrollbar_bg': '#2a2a2a',
                'scrollbar_fg': '#555555',  # Visible but not distracting
                'button_bg': '#333333',
                'button_fg': '#f0f0f0',
                'button_active_bg': '#444444',
                'entry_bg': '#2d2d2d',
                'text_bg': '#2d2d2d',
                'text_fg': '#f0f0f0',
                'tooltip_bg': '#3a3a3a',
                'tooltip_fg': '#f0f0f0',
                'tab_bg': '#252525',
                'tab_selected_bg': '#1e1e1e',
                'status_bg': '#252525',
                'progress_bg': '#333333',
                'progress_fg': '#0078d7',
                'menu_bg': '#1e1e1e',
                'menu_fg': '#f0f0f0',
                'alert_success_bg': '#1a331a',
                'alert_success_fg': '#6aba6a',
                'alert_error_bg': '#331a1a',
                'alert_error_fg': '#ff8080',
                'alert_warning_bg': '#332e1a',
                'alert_warning_fg': '#ffcc66',
                'cell_text': '#000000',  # Always black for cell text
                'modified_bg': '#263846'  # Dark blue highlight
            }
        }

        # Register theme change callback
        self.theme_var.trace_add('write', self._theme_changed)

    def detect_system_theme(self):
        """
        Attempt to detect system theme preference.
        Returns 'dark', 'light', or None if detection failed.
        """
        try:
            if sys.platform == "darwin":  # macOS
                # Try to use applescript to get dark mode status
                import subprocess
                cmd = 'defaults read -g AppleInterfaceStyle'
                try:
                    result = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
                    return 'dark' if result.strip() == b'Dark' else 'light'
                except subprocess.CalledProcessError:
                    # If command fails, it means light mode is set
                    return 'light'

            elif sys.platform == "win32":  # Windows
                try:
                    import winreg
                    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                    key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    return 'light' if value == 1 else 'dark'
                except Exception:
                    pass

            else:  # Linux/Unix
                # Try to detect GNOME theme
                try:
                    import subprocess
                    cmd = 'gsettings get org.gnome.desktop.interface color-scheme'
                    result = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
                    return 'dark' if 'dark' in result.decode('utf-8').lower() else 'light'
                except Exception:
                    pass
        except Exception:
            pass

        return None  # Detection failed

    def set_theme(self, theme_name):
        """Set the active theme"""
        if theme_name == 'system':
            # Try to detect system theme
            system_theme = self.detect_system_theme()
            theme_name = system_theme if system_theme else 'light'

        if theme_name not in self.themes:
            theme_name = 'light'  # Default to light theme

        self.theme_var.set(theme_name)

    def get_theme(self):
        """Get the current theme name"""
        return self.theme_var.get()

    def get_theme_color(self, color_name):
        """Get a specific color from the current theme"""
        theme = self.themes.get(self.theme_var.get(), self.themes['light'])
        return theme.get(color_name, self.themes['light'][color_name])

    def _theme_changed(self, *args):
        """Apply theme changes to all widgets with improved contrast"""
        theme_name = self.theme_var.get()
        theme = self.themes.get(theme_name, self.themes['light'])

        style = ttk.Style()

        # Configure the ttk theme
        if theme_name == 'dark':
            # Try to use a dark theme if available
            try:
                style.theme_use('clam')  # Clam is more customizable for dark themes
            except Exception:
                pass
        else:
            # For light theme, default or 'alt' works well
            try:
                if sys.platform == "darwin":  # macOS
                    style.theme_use('aqua')  # Native macOS theme
                else:
                    style.theme_use('alt')
            except Exception:
                pass

        # Configure main colors
        style.configure('.',
                        background=theme['bg'],
                        foreground=theme['fg'],
                        fieldbackground=theme['entry_bg'],
                        troughcolor=theme['scrollbar_bg'],
                        selectbackground=theme['selectbg'],
                        selectforeground=theme['selectfg'],
                        insertcolor=theme['insertbg'],
                        bordercolor=theme['border'],
                        disabledforeground=theme['disabledfg'])

        # Configure buttons with good contrast
        style.configure('TButton',
                        background=theme['button_bg'],
                        foreground=theme['button_fg'])
        style.map('TButton',
                  background=[('active', theme['button_active_bg']), ('pressed', theme['selectbg'])],
                  foreground=[('disabled', theme['disabledfg'])])

        # Configure entries
        style.configure('TEntry',
                        fieldbackground=theme['entry_bg'],
                        background=theme['entry_bg'],
                        foreground=theme['text_fg'],
                        insertcolor=theme['insertbg'])

        # Configure notebooks
        style.configure('TNotebook',
                        background=theme['frame_bg'],
                        tabmargins=[2, 5, 2, 0])
        style.configure('TNotebook.Tab',
                        background=theme['tab_bg'],
                        foreground=theme['fg'],
                        padding=[10, 2])
        style.map('TNotebook.Tab',
                  background=[('selected', theme['tab_selected_bg'])],
                  expand=[('selected', [1, 1, 1, 0])])

        # Configure frames
        style.configure('TFrame', background=theme['frame_bg'])
        style.configure('TLabelframe', background=theme['frame_bg'])
        style.configure('TLabelframe.Label', background=theme['frame_bg'], foreground=theme['fg'])

        # Configure progress bars
        style.configure('TProgressbar',
                        background=theme['progress_fg'],
                        troughcolor=theme['progress_bg'])

        # Configure treeview with better contrast and readability
        style.configure('Treeview',
                        background=theme['treeview_bg'],
                        foreground=theme['cell_text'],  # Always black for cell text
                        fieldbackground=theme['treeview_bg'])

        style.configure('Treeview.Heading',
                        background=theme['treeview_header_bg'],
                        foreground=theme['treeview_header_fg'])

        # Ensure selected text in treeview is visible
        style.map('Treeview',
                  background=[('selected', theme['selectbg'])],
                  foreground=[('selected', theme['selectfg'])])

        # Configure row colors for treeview
        self._customize_treeview(theme)

        # Configure scrollbar
        style.configure('TScrollbar',
                        background=theme['scrollbar_bg'],
                        troughcolor=theme['scrollbar_bg'],
                        arrowcolor=theme['fg'])
        style.map('TScrollbar',
                  background=[('active', theme['scrollbar_fg'])],
                  arrowcolor=[('active', theme['fg'])])

        # Configure status bar
        style.configure('StatusBar.TLabel',
                        background=theme['status_bg'],
                        foreground=theme['fg'])

        # Configure alert styles
        style.configure('Success.TFrame', background=theme['alert_success_bg'])
        style.configure('Success.TLabel', background=theme['alert_success_bg'], foreground=theme['alert_success_fg'])

        style.configure('Error.TFrame', background=theme['alert_error_bg'])
        style.configure('Error.TLabel', background=theme['alert_error_bg'], foreground=theme['alert_error_fg'])

        style.configure('Warning.TFrame', background=theme['alert_warning_bg'])
        style.configure('Warning.TLabel', background=theme['alert_warning_bg'], foreground=theme['alert_warning_fg'])

        # Configure text and scrolledtext
        try:
            self.root.option_add("*Text.Background", theme['text_bg'])
            self.root.option_add("*Text.Foreground", theme['text_fg'])
            self.root.option_add("*Text.selectBackground", theme['selectbg'])
            self.root.option_add("*Text.selectForeground", theme['selectfg'])
        except Exception:
            # Ignore if option_add fails, it's not critical
            pass

        # Update the main window background
        self.root.configure(background=theme['bg'])

        # Force redraw
        self.root.update_idletasks()

    def _customize_treeview(self, theme):
        """Apply custom colors to treeview rows with better contrast"""
        style = ttk.Style()

        # Configure alternating row colors with good contrast
        style.map('Treeview',
                  background=[('selected', theme['selectbg'])],
                  foreground=[('selected', theme['selectfg'])])

        # Configure tag colors for rows with improved visibility
        if hasattr(self, 'treeview_configured'):
            # These should only be configured once, then updated via tags
            return

        def fixed_map(option):
            """Fix for setting text color of Treeview items"""
            return [elm for elm in style.map('Treeview', query_opt=option)
                    if elm[:2] != ('!disabled', '!selected')]

        style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))
        self.treeview_configured = True
