"""
Ollama settings dialog for Excel AI Assistant.
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

from app.config import AppConfig
from app.services.api_manager import APIManager
from app.ui.dispatcher import UIDispatcher


# noinspection PyTypeChecker
class OllamaSettingsDialog:
    """Dialog for configuring Ollama settings"""

    def __init__(self, parent: tk.Tk, config: AppConfig, api_manager: APIManager,
                 callback: Optional[Callable] = None):
        """
        Initialize the Ollama settings dialog

        Args:
            parent: Parent window
            config: Application configuration
            api_manager: API manager for testing connection
            callback: Optional callback to run after changes
        """
        self.parent = parent
        self.config = config
        self.api_manager = api_manager
        self.callback = callback
        self.available_models = []
        self.dispatcher = UIDispatcher(parent)
        self._request_id = 0

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.bind('<Destroy>', lambda event: self.dispatcher.close() if event.widget is self.dialog else None)
        self.dialog.title("Ollama Settings")
        self.dialog.geometry("550x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Make dialog modal
        self.dialog.focus_set()

        # Center on parent
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (parent.winfo_width() // 2) - (width // 2) + parent.winfo_x()
        y = (parent.winfo_height() // 2) - (height // 2) + parent.winfo_y()
        self.dialog.geometry(f"+{x}+{y}")

        # Initialize UI
        self._create_ui()
        self._load_settings()

        # Get available models (in a separate thread)
        self._refresh_models()

    def _create_ui(self):
        """Create the UI elements"""
        # Main frame with padding
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Connection settings
        connection_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding=10)
        connection_frame.pack(fill=tk.X, padx=5, pady=5)

        # URL field
        ttk.Label(connection_frame, text="Ollama Server URL:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(connection_frame, textvariable=self.url_var, width=40)
        url_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W + tk.E)

        # Test connection button
        test_button = ttk.Button(connection_frame, text="Test Connection", command=self._test_connection)
        test_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

        # Connection status
        self.status_var = tk.StringVar(value="Status: Not tested")
        status_label = ttk.Label(connection_frame, textvariable=self.status_var)
        status_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

        # Models settings
        models_frame = ttk.LabelFrame(main_frame, text="Available Models", padding=10)
        models_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

        # Models list
        self.models_listbox = tk.Listbox(models_frame, height=10)
        self.models_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Refresh button
        refresh_button = ttk.Button(models_frame, text="Refresh Models", command=self._refresh_models)
        refresh_button.pack(anchor=tk.W, padx=5, pady=5)

        # Default model setting
        default_frame = ttk.Frame(main_frame)
        default_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(default_frame, text="Default model:").pack(side=tk.LEFT, padx=5)
        self.default_model_var = tk.StringVar()
        self.default_model_combo = ttk.Combobox(default_frame,
                                                textvariable=self.default_model_var,
                                                state="readonly", width=30)
        self.default_model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Set to make current button
        set_default_button = ttk.Button(default_frame, text="Set Selected as Default",
                                        command=self._set_selected_as_default)
        set_default_button.pack(side=tk.LEFT, padx=5)

        # Buttons at the bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # Show "Loading..." in the listbox initially
        self.models_listbox.insert(tk.END, "Loading models...")

        ttk.Button(button_frame, text="Save", command=self._save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def _load_settings(self):
        """Load settings from config"""
        # Set URL
        self.url_var.set(self.config.get('ollama_url', 'http://localhost:11434'))

        # Set default model
        self.default_model_var.set(self.config.get('ollama_model', 'llama3'))

    def _fetch_available_models(self, url, request_id):
        try:
            manager = APIManager(api_type='ollama', ollama_url=url)
            models = manager.get_available_models()
            self.dispatcher.post(self._receive_models, models, request_id)
        except ValueError as error:
            self.dispatcher.post(self._update_connection_status, False, str(error))

    def _receive_models(self, models, request_id):
        if not self.dialog.winfo_exists() or request_id != self._request_id:
            return
        self.available_models = models
        self._update_models_list()

    def _update_models_list(self):
        """Update the models listbox with fetched models"""
        # Clear the listbox
        self.models_listbox.delete(0, tk.END)

        # Add models to the listbox
        model_names = [model["name"] for model in self.available_models]
        for model in model_names:
            self.models_listbox.insert(tk.END, model)

        # Update the combobox
        self.default_model_combo['values'] = model_names

        # Select the currently set default model if available
        current_default = self.default_model_var.get()
        if current_default in model_names:
            self.default_model_combo.set(current_default)
            # Select in listbox too
            try:
                index = model_names.index(current_default)
                self.models_listbox.selection_set(index)
                self.models_listbox.see(index)
            except ValueError:
                pass
        elif model_names:
            # Select first model as default if current default not available
            self.default_model_combo.set(model_names[0])

        # Update status if models were found
        if model_names:
            self.status_var.set(f"Status: Found {len(model_names)} models")
        else:
            self.status_var.set("Status: No models found. Is Ollama running?")

    def _refresh_models(self):
        self._request_id += 1
        url = self.url_var.get()
        self.models_listbox.delete(0, tk.END)
        self.models_listbox.insert(tk.END, "Loading models...")
        self.status_var.set("Status: Refreshing models...")
        threading.Thread(target=self._fetch_available_models, args=(url, self._request_id), daemon=True).start()

    def _test_connection(self):
        url = self.url_var.get()
        model = self.default_model_var.get()
        self.status_var.set("Status: Testing connection...")
        def test_thread():
            try:
                manager = APIManager(api_type='ollama', ollama_url=url, model=model)
                success, message = manager.test_connection()
            except ValueError as error:
                success, message = False, str(error)
            self.dispatcher.post(self._update_connection_status, success, message)
        threading.Thread(target=test_thread, daemon=True).start()

    def _update_connection_status(self, success: bool, message: str):
        """Update the connection status label"""
        if not self.dialog.winfo_exists():
            return
        if success:
            self.status_var.set(f"Status: Connected successfully")
        else:
            self.status_var.set(f"Status: Connection failed - {message}")

    def _set_selected_as_default(self):
        """Set the selected model as default"""
        selection = self.models_listbox.curselection()
        if selection:
            selected_model = self.models_listbox.get(selection[0])
            self.default_model_var.set(selected_model)
        else:
            messagebox.showinfo("No Selection", "Please select a model from the list first.")

    def _save_settings(self):
        """Save settings and close dialog"""
        try:
            APIManager(api_type='ollama', ollama_url=self.url_var.get())
        except ValueError as error:
            messagebox.showerror("Invalid URL", str(error))
            return
        # Save URL
        self.config.set('ollama_url', self.url_var.get())

        # Save default model
        self.config.set('ollama_model', self.default_model_var.get())

        # Save config to file
        self.config.save()

        # Run callback if provided
        if self.callback:
            self.callback()

        # Close dialog
        self.dialog.destroy()
