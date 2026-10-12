"""
Data Treeview component for Excel AI Assistant.
Custom treeview widget for displaying and interacting with tabular data.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Optional, List, Callable

import pandas as pd


def _tree_value(value):
    """Keep text intact when Tk would otherwise store it as a number.

    Tcl treeview values that look like integers are coerced, so ``0012``
    becomes ``12`` and a later cell update writes that number back.
    """
    if value is None:
        return "\u200b"
    try:
        missing = bool(pd.isna(value))
    except (TypeError, ValueError):
        missing = False
    if missing:
        return "\u200b"
    return "\u200b" + str(value)


class DataTreeview:
    """Enhanced treeview for displaying dataframe content with improved readability"""

    def __init__(self, parent: ttk.Frame, show_modified: bool = False, max_rows: int = 1000):
        """
        Initialize the data treeview

        Args:
            parent: Parent frame
            show_modified: Whether to highlight modified cells
        """
        self.parent = parent
        self.max_rows = max_rows
        self.show_modified = show_modified
        self.df = None
        self.modified_cells = set()  # Set of (row, col) tuples
        self.on_cell_edit = None  # Callback for cell edits

        # Create a frame for the treeview and scrollbars
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Create scrollbars
        self.y_scrollbar = ttk.Scrollbar(self.frame)
        self.y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.x_scrollbar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Create the treeview
        self.tree = ttk.Treeview(
            self.frame,
            show="headings",
            yscrollcommand=self.y_scrollbar.set,
            xscrollcommand=self.x_scrollbar.set
        )
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Configure scrollbars
        self.y_scrollbar.config(command=self.tree.yview)
        self.x_scrollbar.config(command=self.tree.xview)

        # Set up right-click context menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.tree.bind("<Button-3>", self._show_context_menu)

        # Configure row tags - ensure text always remains black for readability
        self.tree.tag_configure("row_even", background="#FFFFFF", foreground="#000000")
        self.tree.tag_configure("row_odd", background="#F0F5FA", foreground="#000000")  # Light blue tint
        self.tree.tag_configure("modified", background="#E0F0FF", foreground="#000000")  # Clearer highlight

        # Bind events
        self.tree.bind("<Double-1>", self._on_double_click)

        # Create placeholder
        self._show_placeholder()

    def _show_placeholder(self):
        """Show placeholder when no data is loaded"""
        # Clear existing columns
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")

        # Set placeholder column
        self.tree["columns"] = ["placeholder"]
        self.tree.heading("placeholder", text="No data loaded")
        self.tree.column("placeholder", width=400, anchor=tk.CENTER)

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add placeholder item
        self.tree.insert("", tk.END, values=["Open a file to view data"])

    def set_data(self, df: pd.DataFrame, max_rows: int = None):
        """
        Set data to display in the treeview

        Args:
            df: Pandas dataframe to display
            max_rows: Maximum number of rows to display
        """
        max_rows = self.max_rows if max_rows is None else max_rows
        self.df = df
        self.modified_cells = set()

        if df is None or len(df) == 0:
            self._show_placeholder()
            return

        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Configure columns - add a row number column first
        columns = ['row_number'] + [f'data_{index}' for index in range(len(df.columns))]
        self.tree["columns"] = columns
        
        # Add row number column heading with total row count
        total_rows = len(df)
        self.tree.heading('row_number', text=f"Row # (of {total_rows})")
        self.tree.column('row_number', width=100, anchor=tk.CENTER)
        
        # Configure data columns
        for index, col in enumerate(df.columns):
            column_id = f'data_{index}'
            self.tree.heading(column_id, text=col, command=lambda c=col: self._sort_by_column(c))

            # Calculate column width based on content
            max_width = max(len(str(col)), df[col].astype(str).str.len().max() if len(df) > 0 else 10)
            width = min(max(max_width * 10, 80), 300)  # Min 80px, max 300px
            self.tree.column(column_id, width=int(width))

        # Add data rows with alternating colors for better readability
        display_df = df.head(max_rows) if len(df) > max_rows else df

        for i, (idx, row) in enumerate(display_df.iterrows()):
            # Row numbers follow the source index so sorting and filtering keep identity.
            values = [_tree_value(idx + 1)] + [_tree_value(val) for val in row]
            
            # Set row tag for styling
            row_tag = "row_even" if i % 2 == 0 else "row_odd"
            
            # Insert row with row number into treeview
            self.tree.insert("", tk.END, iid=str(idx), values=values, tags=(row_tag,))

        # Add a "more rows" indicator if necessary
        if len(df) > max_rows:
            more_values = [""] * len(columns)  # One more column now for row numbers
            more_values[-1] = f"... {len(df) - max_rows} more rows"
            self.tree.insert("", tk.END, values=more_values, tags=("more_rows",))

    def update_cell(self, row: int, col: str, value: Any):
        """
        Update a cell in the treeview

        Args:
            row: Row index
            col: Column name
            value: New value
        """
        if self.df is None or col not in self.df.columns:
            return

        # Find the tree item for this row
        item_id = str(row)
        if item_id not in self.tree.get_children():
            return

        # Write the value into this view, then redraw the row from the dataframe.
        # Reading item values back would turn identifier text into integers.
        if row in self.df.index:
            if isinstance(value, str) and self.df[col].dtype != object:
                self.df[col] = self.df[col].astype(object)
            self.df.loc[row, col] = value
            values = [_tree_value(row + 1)] + [_tree_value(self.df.loc[row, name]) for name in self.df.columns]
            self.tree.item(item_id, values=values)

        # Mark as modified
        self.modified_cells.add((row, col))

        # Apply modified tag if showing modifications
        if self.show_modified:
            # Get current tags
            current_tags = list(self.tree.item(item_id)["tags"])

            # Add modified tag if not already present
            if "modified" not in current_tags:
                current_tags.append("modified")
                self.tree.item(item_id, tags=current_tags)

    def update_batch(self, updates: List[Dict[str, Any]]):
        """
        Update multiple cells at once

        Args:
            updates: List of dictionaries with row, col, and result keys
        """
        for update in updates:
            if 'row' in update and 'col' in update and 'result' in update and update.get('success', False):
                self.update_cell(update['row'], update['col'], update['result'])

    def _sort_by_column(self, column: str, reverse: bool = False):
        """
        Sort treeview by a column

        Args:
            column: Column name to sort by
            reverse: Whether to reverse the sort order
        """
        if self.df is None or column not in self.df.columns:
            return

        # Sort the dataframe. Mixed text and numbers (after an AI edit) cannot
        # be ordered with the default comparison.
        try:
            sorted_df = self.df.sort_values(by=column, ascending=not reverse)
        except TypeError:
            sorted_df = self.df.sort_values(
                by=column,
                ascending=not reverse,
                key=lambda series: series.map(
                    lambda value: "" if value is None or pd.isna(value) else str(value)),
            )

        # Update treeview
        self.set_data(sorted_df)

        # Update column header to show sort direction
        for index, col in enumerate(self.df.columns):
            column_id = f'data_{index}'
            if col == column:
                direction = "(descending)" if reverse else "(ascending)"
                self.tree.heading(column_id, text=f"{col} {direction}", command=lambda c=col: self._sort_by_column(c, not reverse))
            else:
                self.tree.heading(column_id, text=col)

        # Toggle sort direction for next click
        column_id = f'data_{list(self.df.columns).index(column)}'
        self.tree.heading(column_id, command=lambda: self._sort_by_column(column, not reverse))

    def _on_double_click(self, event):
        """Handle double-click on a cell"""
        # Get the row and column that was clicked
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            # Get the item and column
            item_id = self.tree.identify_row(event.y)
            col_id = self.tree.identify_column(event.x)

            if not item_id or not col_id:
                return

            # Convert column id (#1, #2, etc.) to column name
            col_idx = int(col_id.replace("#", "")) - 1
            
            # First column is row number, so we need to adjust the index
            if col_idx == 0:
                # This is the row number column, nothing to edit
                return
                
            # Adjust index for data columns (subtract 1 to account for row number column)
            data_col_idx = col_idx - 1
            if data_col_idx < 0 or data_col_idx >= len(self.df.columns):
                return

            col_name = self.df.columns[data_col_idx]

            # Convert item_id to row index
            try:
                row_idx = int(item_id)

                # Show cell editor
                self._edit_cell(row_idx, col_name)
            except ValueError:
                pass

    def _edit_cell(self, row: int, col: str):
        """Show cell editor with high-contrast text"""
        if self.df is None or row not in self.df.index or col not in self.df.columns:
            return

        # Get current value
        cell_value = self.df.loc[row, col]

        # Create editor dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Edit Cell [{row}, {col}]")
        dialog.geometry("400x200")
        # noinspection PyTypeChecker
        dialog.transient(self.parent)
        dialog.grab_set()

        # Make dialog modal
        dialog.focus_set()

        # Create text editor
        ttk.Label(dialog, text=f"Editing cell at row {row}, column '{col}':").pack(padx=10, pady=5, anchor=tk.W)

        text_editor = tk.Text(dialog, height=5, width=40)
        text_editor.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        text_editor.insert(tk.END, str(cell_value) if cell_value is not None else "")

        # Ensure text is black for visibility in both themes
        text_editor.configure(foreground="#000000", background="#FFFFFF")

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Save",
                   command=lambda: self._save_cell_edit(dialog, row, col, text_editor.get("1.0", tk.END).strip())).pack(
            side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def _save_cell_edit(self, dialog: tk.Toplevel, row: int, col: str, value: str):
        """Save edited cell value"""
        if self.df is None:
            dialog.destroy()
            return

        # Commit to the data manager before changing a sorted or filtered view.
        if self.on_cell_edit:
            if self.on_cell_edit(row, col, value) is False:
                return
        if isinstance(value, str) and self.df[col].dtype != object:
            self.df[col] = self.df[col].astype(object)
        self.df.loc[row, col] = value

        # Update treeview
        self.update_cell(row, col, value)

        # Close dialog
        dialog.destroy()

    def _show_context_menu(self, event):
        """Show context menu on right-click"""
        if self.df is None:
            return

        # Clear previous menu items
        self.context_menu.delete(0, tk.END)

        # Get the item and column that was clicked
        item_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)

        if not item_id or not col_id:
            return

        # Convert column id (#1, #2, etc.) to column name
        col_idx = int(col_id.replace("#", "")) - 1
        
        # First column is row number, so we need to adjust the index
        if col_idx == 0:
            # This is the row number column, nothing to edit
            return
            
        # Adjust index for data columns (subtract 1 to account for row number column)
        data_col_idx = col_idx - 1
        if data_col_idx < 0 or data_col_idx >= len(self.df.columns):
            return

        col_name = self.df.columns[data_col_idx]

        # Convert item_id to row index
        try:
            row_idx = int(item_id)

            # Add menu items
            self.context_menu.add_command(
                label="Edit Cell",
                command=lambda: self._edit_cell(row_idx, col_name)
            )

            self.context_menu.add_command(
                label="Copy Value",
                command=lambda: self._copy_cell_value(row_idx, col_name)
            )

            self.context_menu.add_separator()

            self.context_menu.add_command(
                label="Copy Row",
                command=lambda: self._copy_row(row_idx)
            )

            self.context_menu.add_command(
                label="Copy Column",
                command=lambda: self._copy_column(col_name)
            )

            # Show menu at click position
            self.context_menu.tk_popup(event.x_root, event.y_root)
        except ValueError:
            pass
        finally:
            # Make sure to release the grab
            self.context_menu.grab_release()

    def _copy_cell_value(self, row: int, col: str):
        """Copy cell value to clipboard"""
        if self.df is None or row not in self.df.index or col not in self.df.columns:
            return

        # Get cell value
        cell_value = self.df.loc[row, col]

        # Copy to clipboard
        self.parent.clipboard_clear()
        self.parent.clipboard_append(str(cell_value) if cell_value is not None else "")

    def _copy_row(self, row: int):
        """Copy entire row to clipboard"""
        if self.df is None or row not in self.df.index:
            return

        # Get row values
        row_values = self.df.loc[row].tolist()

        # Format as tab-separated values
        tsv = "\t".join(str(val) if val is not None else "" for val in row_values)

        # Copy to clipboard
        self.parent.clipboard_clear()
        self.parent.clipboard_append(tsv)

    def _copy_column(self, col: str):
        """Copy entire column to clipboard"""
        if self.df is None or col not in self.df.columns:
            return

        # Get column values
        col_values = self.df[col].tolist()

        # Format as newline-separated values
        text = "\n".join(str(val) if val is not None else "" for val in col_values)

        # Copy to clipboard
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)

    def set_on_cell_edit_callback(self, callback: Callable[[int, str, Any], None]):
        """Set callback for cell edits"""
        self.on_cell_edit = callback

    def clear_modified_flags(self):
        """Clear all modified cell flags"""
        self.modified_cells.clear()

        # Remove modified tags from all items
        for item_id in self.tree.get_children():
            current_tags = list(self.tree.item(item_id)["tags"])
            if "modified" in current_tags:
                current_tags.remove("modified")
                self.tree.item(item_id, tags=current_tags)

    def get_selected_cells(self) -> List[Dict[str, Any]]:
        """Get currently selected cells"""
        selected = []

        # Get selected items
        item_ids = self.tree.selection()
        if not item_ids or self.df is None:
            return selected

        # Get row indices
        for item_id in item_ids:
            try:
                row_idx = int(item_id)

                # Add all cells in this row
                for col in self.df.columns:
                    selected.append({
                        'row': row_idx,
                        'col': col,
                        'content': self.df.loc[row_idx, col]
                    })
            except ValueError:
                continue

        return selected

    def select_all(self):
        """Select all rows"""
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def select_none(self):
        """Clear selection"""
        self.tree.selection_remove(self.tree.selection())

    def update_theme(self, is_dark: bool):
        """Update treeview colors for the current theme with improved contrast"""
        if is_dark:
            # Dark theme colors - keep text black for readability
            self.tree.tag_configure("row_even", background="#2d2d2d", foreground="#000000")
            self.tree.tag_configure("row_odd", background="#363636", foreground="#000000")  # Better contrast
            self.tree.tag_configure("modified", background="#263846", foreground="#000000")  # Dark blue highlight
        else:
            # Light theme colors - keep text black for readability
            self.tree.tag_configure("row_even", background="#FFFFFF", foreground="#000000")
            self.tree.tag_configure("row_odd", background="#F0F5FA", foreground="#000000")  # Light blue tint
            self.tree.tag_configure("modified", background="#E0F0FF", foreground="#000000")  # Clear highlight

        # Update all rows
        if self.df is not None:
            for i, item_id in enumerate(self.tree.get_children()):
                try:
                    row_idx = int(item_id)

                    # Get current tags
                    current_tags = list(self.tree.item(item_id)["tags"])

                    # Replace row tags
                    if "row_even" in current_tags:
                        current_tags.remove("row_even")
                    if "row_odd" in current_tags:
                        current_tags.remove("row_odd")

                    # Add appropriate row tag
                    if i % 2 == 0:
                        current_tags.append("row_even")
                    else:
                        current_tags.append("row_odd")

                    # Update tags
                    self.tree.item(item_id, tags=current_tags)
                except ValueError:
                    continue

    def export_to_csv(self, file_path: str) -> bool:
        """Export current data to CSV"""
        if self.df is None:
            return False

        try:
            self.df.to_csv(file_path, index=False)
            return True
        except Exception:
            return False

    def filter_data(self, filter_text: str, columns: Optional[List[str]] = None):
        """
        Filter the treeview to show only rows matching the filter

        Args:
            filter_text: Text to filter by
            columns: List of columns to filter (if None, filter all columns)
        """
        if self.df is None or not filter_text:
            return

        # Make a copy of the original dataframe
        filtered_df = self.df.copy()

        # If no columns specified, filter all columns
        if not columns:
            columns = filtered_df.columns.tolist()

        # Create filter mask
        mask = pd.Series(False, index=filtered_df.index)

        for col in columns:
            # Convert column to string and check if it contains the filter text
            mask = mask | filtered_df[col].astype(str).str.contains(filter_text, case=False, na=False, regex=False)

        # Apply filter
        filtered_df = filtered_df[mask]

        # Update treeview with filtered data
        self.set_data(filtered_df)

    def reset_filter(self):
        """Reset any applied filters"""
        if self.df is not None:
            self.set_data(self.df)
