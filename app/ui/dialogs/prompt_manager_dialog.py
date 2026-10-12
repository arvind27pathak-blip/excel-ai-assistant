"""
Prompt manager dialog for Excel AI Assistant.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from app.config import AppConfig


class PromptManagerDialog:
    """Dialog for managing prompt templates"""

    def __init__(self, parent: tk.Tk, config: AppConfig, callback: Callable[[], None] = None):
        """
        Initialize the prompt manager dialog

        Args:
            parent: Parent window
            config: Application configuration
            callback: Optional callback to run after changes
        """
        self.parent = parent
        self.config = config
        self.callback = callback

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Manage Prompt Templates")
        self.dialog.geometry("600x500")
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
        self._load_prompts()

    def _create_ui(self):
        """Create the UI elements"""
        # Main frame with padding
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Split into left (list) and right (editor) panels
        self.paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, pady=5)

        # Left panel - Template list
        left_panel = ttk.Frame(self.paned_window, width=200)
        self.paned_window.add(left_panel, weight=1)

        # Right panel - Template editor
        right_panel = ttk.Frame(self.paned_window)
        self.paned_window.add(right_panel, weight=2)

        # Create left panel contents (list with controls)
        self._create_list_panel(left_panel)

        # Create right panel contents (editor)
        self._create_editor_panel(right_panel)

        # Buttons at the bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        self.import_button = ttk.Button(button_frame, text="Import", command=self._import_prompts)
        self.import_button.pack(side=tk.LEFT, padx=5)
        self.export_button = ttk.Button(button_frame, text="Export", command=self._export_prompts)
        self.export_button.pack(side=tk.LEFT, padx=5)
        self.restore_defaults_button = ttk.Button(button_frame, text="Restore Defaults",
                                                  command=self._restore_default_templates)
        self.restore_defaults_button.pack(side=tk.LEFT, padx=5)

    def _create_list_panel(self, parent: ttk.Frame):
        """Create the template list panel"""
        # Template list with scrollbar
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Label
        ttk.Label(list_frame, text="Prompt Templates:").pack(anchor=tk.W, padx=5, pady=5)

        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.prompt_listbox = tk.Listbox(list_container, yscrollcommand=scrollbar.set)
        self.prompt_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.prompt_listbox.yview)

        # Bind selection event
        self.prompt_listbox.bind('<<ListboxSelect>>', self._on_prompt_selected)

        # Controls for list
        controls_frame = ttk.Frame(list_frame)
        controls_frame.pack(fill=tk.X, pady=5)

        self.add_button = ttk.Button(controls_frame, text="Add", command=self._add_prompt)
        self.add_button.pack(side=tk.LEFT, padx=2)

        self.delete_button = ttk.Button(controls_frame, text="Delete", command=self._delete_prompt)
        self.delete_button.pack(side=tk.LEFT, padx=2)

    def _create_editor_panel(self, parent: ttk.Frame):
        """Create the template editor panel"""
        editor_frame = ttk.Frame(parent)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5)

        # Template name
        name_frame = ttk.Frame(editor_frame)
        name_frame.pack(fill=tk.X, pady=5)

        ttk.Label(name_frame, text="Template Name:").pack(side=tk.LEFT, padx=5)

        self.template_name_var = tk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=self.template_name_var, width=30)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Category dropdown (optional)
        category_frame = ttk.Frame(editor_frame)
        category_frame.pack(fill=tk.X, pady=5)

        ttk.Label(category_frame, text="Category:").pack(side=tk.LEFT, padx=5)

        self.category_var = tk.StringVar()
        categories = ["General", "Text Formatting", "Data Extraction", "Analysis", "Custom"]
        self.category_dropdown = ttk.Combobox(category_frame, textvariable=self.category_var, values=categories)
        self.category_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Description
        ttk.Label(editor_frame, text="Description:").pack(anchor=tk.W, padx=5, pady=2)

        self.description_var = tk.StringVar()
        description_entry = ttk.Entry(editor_frame, textvariable=self.description_var)
        description_entry.pack(fill=tk.X, padx=5, pady=2)

        # Prompt content
        ttk.Label(editor_frame, text="Prompt Template:").pack(anchor=tk.W, padx=5, pady=5)

        # Create text editor with scrollbars
        text_frame = ttk.Frame(editor_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        y_scrollbar = ttk.Scrollbar(text_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        x_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.prompt_text = tk.Text(
            text_frame,
            wrap=tk.NONE,
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
        self.prompt_text.pack(fill=tk.BOTH, expand=True)

        y_scrollbar.config(command=self.prompt_text.yview)
        x_scrollbar.config(command=self.prompt_text.xview)

        # Editor controls
        controls_frame = ttk.Frame(editor_frame)
        controls_frame.pack(fill=tk.X, pady=10)

        self.save_button = ttk.Button(controls_frame, text="Save", command=self._save_current_prompt)
        self.save_button.pack(side=tk.RIGHT, padx=5)

        self.test_button = ttk.Button(controls_frame, text="Test", command=self._test_prompt)
        self.test_button.pack(side=tk.RIGHT, padx=5)

        # Disable editor initially
        self._set_editor_state(False)

    def _set_editor_state(self, enabled: bool):
        """Enable or disable the editor"""
        state = tk.NORMAL if enabled else tk.DISABLED

        self.template_name_var.set("")
        self.category_var.set("")
        self.description_var.set("")
        self.prompt_text.delete("1.0", tk.END)

        self.save_button.config(state=state)
        self.test_button.config(state=state)

    def _load_prompts(self):
        """Load prompt templates from config"""
        # Clear listbox
        self.prompt_listbox.delete(0, tk.END)

        # Get prompts from config
        prompts = self.config.get_prompt_templates()

        # Sort by name
        sorted_names = sorted(prompts.keys())

        # Add to listbox
        for name in sorted_names:
            self.prompt_listbox.insert(tk.END, name)

        # Select first item if available
        if self.prompt_listbox.size() > 0:
            self.prompt_listbox.selection_set(0)
            self._on_prompt_selected(None)

    def _on_prompt_selected(self, event):
        """Handle prompt selection"""
        # Get selected index
        selection = self.prompt_listbox.curselection()
        if not selection:
            self._set_editor_state(False)
            return

        # Get template name
        template_name = self.prompt_listbox.get(selection[0])

        # Get prompt data
        prompts = self.config.get_prompt_templates()

        # Get prompt data
        if template_name in prompts:
            prompt_data = prompts[template_name]

            # Handle both string and dictionary formats
            if isinstance(prompt_data, str):
                # Simple format (just the prompt text)
                self.template_name_var.set(template_name)
                self.category_var.set("General")
                self.description_var.set("")
                self.prompt_text.delete("1.0", tk.END)
                self.prompt_text.insert(tk.END, prompt_data)
            else:
                # Dictionary format (with metadata)
                self.template_name_var.set(template_name)
                self.category_var.set(prompt_data.get("category", "General"))
                self.description_var.set(prompt_data.get("description", ""))
                self.prompt_text.delete("1.0", tk.END)
                self.prompt_text.insert(tk.END, prompt_data.get("prompt", ""))

            # Enable editor
            self._set_editor_state(True)

    def _add_prompt(self):
        """Add a new prompt template"""
        # Create a default name based on the count
        default_name = f"New Template {self.prompt_listbox.size() + 1}"

        # Enable editor
        self._set_editor_state(True)

        # Set default values
        self.template_name_var.set(default_name)
        self.category_var.set("General")
        self.description_var.set("")
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert(tk.END, "Enter your prompt template here.")

        # Add to listbox
        self.prompt_listbox.insert(tk.END, default_name)

        # Select new item
        self.prompt_listbox.selection_clear(0, tk.END)
        self.prompt_listbox.selection_set(tk.END)
        self.prompt_listbox.see(tk.END)

    def _delete_prompt(self):
        """Delete the selected prompt template"""
        # Get selected index
        selection = self.prompt_listbox.curselection()
        if not selection:
            return

        # Get template name
        template_name = self.prompt_listbox.get(selection[0])

        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Delete prompt template '{template_name}'?"):
            return

        # Delete from config
        self.config.remove_prompt_template(template_name)

        # Delete from listbox
        self.prompt_listbox.delete(selection[0])

        # Save config
        self.config.save()

        # Disable editor if no items left
        if self.prompt_listbox.size() == 0:
            self._set_editor_state(False)
        else:
            # Select next item
            next_idx = min(selection[0], self.prompt_listbox.size() - 1)
            self.prompt_listbox.selection_set(next_idx)
            self._on_prompt_selected(None)

        # Run callback if provided
        if self.callback:
            self.callback()

    def _save_current_prompt(self):
        """Save the current prompt template"""
        # Get template name
        template_name = self.template_name_var.get().strip()

        if not template_name:
            messagebox.showerror("Error", "Template name cannot be empty.")
            return

        # Get selected index
        selection = self.prompt_listbox.curselection()
        old_name = self.prompt_listbox.get(selection[0]) if selection else None

        # Check if name changed and already exists
        if template_name != old_name and template_name in self.config.get_prompt_templates():
            if not messagebox.askyesno("Confirm Replace",
                                       f"A template named '{template_name}' already exists. Replace it?",
                                       icon=messagebox.WARNING):
                return

        # Get prompt data
        category = self.category_var.get()
        description = self.description_var.get()
        prompt_text = self.prompt_text.get("1.0", tk.END).strip()

        if not prompt_text:
            messagebox.showerror("Error", "Prompt template cannot be empty.")
            return

        # Create prompt data
        prompt_data = {
            "category": category,
            "description": description,
            "prompt": prompt_text
        }

        # Save to config
        self.config.add_prompt_template(template_name, prompt_data)

        # Update listbox if name changed
        if template_name != old_name and selection:
            self.prompt_listbox.delete(selection[0])
            self.prompt_listbox.insert(selection[0], template_name)
            self.prompt_listbox.selection_set(selection[0])
        elif not selection:
            # Find and select the item
            for i in range(self.prompt_listbox.size()):
                if self.prompt_listbox.get(i) == template_name:
                    self.prompt_listbox.selection_set(i)
                    break

        # Save config
        self.config.save()

        # Show confirmation
        self.dialog.bell()

        # Run callback if provided
        if self.callback:
            self.callback()

    def _test_prompt(self):
        """Test the current prompt template"""
        # Get prompt text
        prompt_text = self.prompt_text.get("1.0", tk.END).strip()

        if not prompt_text:
            messagebox.showerror("Error", "Prompt template cannot be empty.")
            return

        # Create test dialog
        test_dialog = tk.Toplevel(self.dialog)
        test_dialog.title("Test Prompt Template")
        test_dialog.geometry("500x400")
        test_dialog.transient(self.dialog)
        test_dialog.grab_set()

        # Create content
        main_frame = ttk.Frame(test_dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Sample Cell Content:").pack(anchor=tk.W, padx=5, pady=5)

        # Sample content entry
        sample_frame = ttk.Frame(main_frame)
        sample_frame.pack(fill=tk.X, padx=5, pady=5)

        sample_text = tk.Text(sample_frame, height=5)
        sample_text.pack(fill=tk.X)
        sample_text.insert(tk.END, "Enter sample cell content here to see how the prompt will be formatted.")

        # Result
        ttk.Label(main_frame, text="Resulting Prompt:").pack(anchor=tk.W, padx=5, pady=5)

        result_text = tk.Text(main_frame, height=10, wrap=tk.WORD)
        result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        result_text.config(state=tk.DISABLED)

        # Update button
        update_button = ttk.Button(
            main_frame,
            text="Update",
            command=lambda: self._update_test_result(prompt_text, sample_text.get("1.0", tk.END), result_text)
        )
        update_button.pack(pady=10)

        # Close button
        ttk.Button(main_frame, text="Close", command=test_dialog.destroy).pack(pady=5)

        # Initial update
        self._update_test_result(prompt_text, sample_text.get("1.0", tk.END), result_text)

    def _update_test_result(self, prompt_template, sample_content, result_text):
        """Update test result with formatted prompt"""
        # Format the prompt
        formatted_prompt = f"{prompt_template}\n\nCell content: {sample_content}"

        # Update result
        result_text.config(state=tk.NORMAL)
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, formatted_prompt)
        result_text.config(state=tk.DISABLED)

    def _import_prompts(self):
        """Import prompt templates from a file"""
        import json
        from tkinter import filedialog

        # Ask for file
        file_path = filedialog.askopenfilename(
            parent=self.dialog,
            title="Import Prompt Templates",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_prompts = json.load(f)

            # Validate format
            if not isinstance(imported_prompts, dict):
                messagebox.showerror("Error", "Invalid format. Expected a dictionary of prompt templates.")
                return

            # Count imported and overwritten
            import_count = 0
            overwrite_count = 0

            # Get current prompts
            current_prompts = self.config.get_prompt_templates()

            # Check for conflicts
            conflicts = set(imported_prompts.keys()) & set(current_prompts.keys())

            if conflicts and not messagebox.askyesno(
                    "Confirm Import",
                    f"Found {len(conflicts)} prompt templates that will be overwritten. Continue?",
                    icon=messagebox.WARNING
            ):
                return

            # Import prompts
            for name, data in imported_prompts.items():
                if name in current_prompts:
                    overwrite_count += 1
                else:
                    import_count += 1

                # Add to config
                self.config.add_prompt_template(name, data)

            # Save config
            self.config.save()

            # Reload prompts
            self._load_prompts()

            # Show success message
            messagebox.showinfo(
                "Import Successful",
                f"Imported {import_count} new prompt templates.\nOverwritten {overwrite_count} existing templates."
            )

            # Run callback if provided
            if self.callback:
                self.callback()

        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON file. Please check the file format.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import prompt templates: {str(e)}")

    def _export_prompts(self):
        """Export prompt templates to a file"""
        import json
        from tkinter import filedialog

        # Get prompts
        prompts = self.config.get_prompt_templates()

        if not prompts:
            messagebox.showinfo("Info", "No prompt templates to export.")
            return

        # Ask for file
        file_path = filedialog.asksaveasfilename(
            parent=self.dialog,
            title="Export Prompt Templates",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(prompts, f, indent=2)

            # Show success message
            messagebox.showinfo(
                "Export Successful",
                f"Exported {len(prompts)} prompt templates to {file_path}."
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export prompt templates: {str(e)}")

    def _restore_default_templates(self):
        """Restore default prompt templates"""
        if not messagebox.askyesno(
                "Restore Default Templates",
                "This will restore all default templates. Custom templates will be preserved unless they have the same name. Continue?",
                icon=messagebox.WARNING
        ):
            return

        # Default templates (same as in config.py)
        default_prompts = {
            # Basic text transformation
            'Capitalize': 'Capitalize all text in this cell.',
            'To Uppercase': 'Convert all text to uppercase.',
            'To Lowercase': 'Convert all text to lowercase.',
            'Sentence Case': 'Format the text in sentence case (capitalize first letter of each sentence).',
            'Title Case': 'Format the text in title case (capitalize first letter of each word, except for articles, prepositions, and conjunctions).',
            'Remove Extra Spaces': 'Remove all extra whitespace, including double spaces and leading/trailing spaces.',

            # Data formatting
            'Format Date': 'Format this as a standard date (YYYY-MM-DD).',
            'Format Phone Number': 'Format this as a standard phone number.',
            'Format Currency': 'Format this as a standard currency value.',
            'Format Percentage': 'Format this as a percentage.',
            'Extract Numbers': 'Extract all numbers from this text.',
            'Format Address': 'Format this as a properly structured address with standard capitalization.',
            'Format Email': 'Format this as a proper email address (lowercase, no extra spaces).',

            # Content transformation
            'Summarize': 'Summarize this text in one sentence.',
            'Expand': 'Expand this abbreviated or short text with more details while maintaining its meaning.',
            'Bullet Points': 'Convert this text into a bulleted list of key points.',
            'Fix Grammar': 'Fix any grammar or spelling errors in this text.',
            'Simplify': 'Simplify this text to make it easier to understand while preserving the key information.',
            'Formalize': 'Rewrite this text in a more formal, professional tone.',
            'Casualize': 'Rewrite this text in a more casual, conversational tone.',

            # Code and markup handling
            'Format JSON': 'Format this as valid, properly indented JSON.',
            'Format XML': 'Format this as valid, properly indented XML.',
            'Format CSV': 'Format this as valid CSV with proper delimiters and escaping.',
            'HTML to Text': 'Convert this HTML to well-structured plain text, preserving the semantic structure.',
            'Markdown to Text': 'Convert this Markdown to plain text while preserving the content structure.',
            'Clean Code': 'Clean up and format this code snippet with proper indentation and style.',

            # Multi-language translation
            'Translate to English': 'Translate this text to English.',
            'Translate to Arabic': 'Translate this text to Arabic.',
            'Translate to Hebrew': 'Translate this text to Hebrew.',

            # Data cleanup
            'Remove Duplicates': 'Remove any duplicate information from this text.',
            'Remove HTML Tags': 'Remove all HTML tags from this text, keeping only the content.',
            'Fix Encoding Issues': 'Fix text encoding issues like garbled characters or HTML entities.',
            'Fill Blank': 'Complete the blank or missing information in this cell based on context from surrounding cells.',
            'Standardize Format': 'Standardize the format of this data according to conventions.',
            'Extract Dates': 'Extract all dates from this text and format them consistently.',

            # Name handling
            'Split Name': 'Split this full name into separate first name and last name components.',
            'Format Name': 'Format this name with proper capitalization and spacing.',

            # Special formats
            'Convert to Citation': 'Convert this reference information to a proper citation format.',
        }

        # Add each default template to the config
        for name, prompt in default_prompts.items():
            # Create template data (using the new format with metadata)
            template_data = {
                "category": "Default",
                "description": f"Default template: {name}",
                "prompt": prompt
            }

            # Add to config
            self.config.add_prompt_template(name, template_data)

        # Save config
        self.config.save()

        # Reload the templates list
        self._load_prompts()

        # Show confirmation
        messagebox.showinfo("Templates Restored", "Default templates have been restored successfully.")

        # Run callback if provided
        if self.callback:
            self.callback()
