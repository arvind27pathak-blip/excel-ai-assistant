"""
Data Manager for the Excel AI Assistant.
Handles loading, saving, and manipulating Excel and CSV data.
"""

import logging
import os
import tempfile
import hashlib
import shutil
import zipfile
from uuid import uuid4
from typing import Tuple, List, Dict, Any, Optional

import numpy as np
import pandas as pd
from pandas.errors import ParserError, EmptyDataError
from app.services.excel_package import inspect_workbook, save_patched_workbook


class DataManager:
    """Manager for handling Excel and CSV data operations"""

    def __init__(self):
        """Initialize the data manager"""
        self.df = None
        self.file_path = None
        self.file_type = None
        self.logger = logging.getLogger("DataManager")
        self.modified = False
        self._changed_cells = set()
        self.document_id = uuid4().hex
        self._source_hash = None
        self._undo_stack = []
        self.last_backup_path = None
        self.sheet_name = None
        self.sheets = []

    def load_file(self, file_path: str, sheet_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Load data from Excel or CSV file

        Args:
            file_path: Path to the file to load

        Returns:
            Tuple of (success, error_message)
        """
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"

        try:
            before_hash = self._fingerprint(file_path)
            # Get file extension
            file_ext = os.path.splitext(file_path)[1].lower()

            # Load based on file extension
            sheets = []
            selected_sheet = None
            if file_ext in ('.xlsx', '.xlsm'):
                sheets = inspect_workbook(file_path)
                selected_sheet = sheet_name if sheet_name is not None else sheets[0]['name']
                if selected_sheet not in [sheet['name'] for sheet in sheets]:
                    return False, f"Worksheet not found: {selected_sheet}"
                df = pd.read_excel(file_path, sheet_name=selected_sheet, dtype=object,
                                   keep_default_na=False, engine_kwargs={'data_only': False})
                # Infer native numeric/date cells without converting text identifiers.
                df = df.infer_objects()
            elif file_ext == '.xls':
                return False, 'Legacy .xls files must be converted to .xlsx before opening.'
            elif file_ext == '.csv':
                # Try different encodings
                try:
                    df = pd.read_csv(file_path, dtype=object, keep_default_na=False)
                except UnicodeDecodeError:
                    # Try with different encodings
                    for encoding in ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']:
                        try:
                            df = pd.read_csv(file_path, encoding=encoding, dtype=object, keep_default_na=False)
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        return False, "Could not decode file with any common encoding"
            else:
                return False, f"Unsupported file format: {file_ext}"

            # Check if dataframe is valid
            if df is None or len(df) == 0:
                return False, "File contains no data"

            # Clean up column names (remove whitespace)
            df.columns = [str(col).strip() for col in df.columns]
            if len(set(df.columns)) != len(df.columns):
                return False, "Column names must be unique after removing whitespace"

            # Handle any NaN values gracefully
            df = df.replace({np.nan: None})

            if self._fingerprint(file_path) != before_hash:
                return False, "The file changed while loading. Please open it again."
            self.df = df
            self.sheets = sheets
            self.sheet_name = selected_sheet
            self.file_path = file_path
            self.file_type = 'csv' if file_ext == '.csv' else 'excel'
            self.modified = False
            self._changed_cells.clear()
            self._undo_stack.clear()
            self._source_hash = before_hash
            self.document_id = uuid4().hex
            return True, ""

        except EmptyDataError:
            return False, "The file is empty"
        except ParserError:
            return False, "Error parsing the file. It may be corrupted."
        except PermissionError:
            return False, "Permission denied. The file may be in use by another program."
        except Exception as e:
            self.logger.error(f"Error loading file: {str(e)}")
            return False, f"Failed to load file: {str(e)}"

    def save_file(self, file_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Save data to Excel or CSV file

        Args:
            file_path: Path to save to (if None, use the current file_path)

        Returns:
            Tuple of (success, error_message)
        """
        if self.df is None:
            return False, "No data to save"

        # Use current path if not specified
        if file_path is None:
            if self.file_path is None:
                return False, "No file path specified"
            file_path = self.file_path

        temporary_path = None
        try:
            # Get file extension
            file_path = os.fspath(file_path)
            file_ext = os.path.splitext(file_path)[1].lower()
            if not file_ext:
                file_path += '.xlsx'
                file_ext = '.xlsx'
            if file_ext not in ('.xlsx', '.xlsm', '.csv'):
                return False, f"Unsupported save format: {file_ext}. Use .xlsx or .csv."

            if self.file_path and self._source_hash is not None:
                if self._fingerprint(self.file_path) != self._source_hash:
                    return False, "The source file changed outside this app. Save is blocked to protect both versions. Export a data snapshot to keep your unsaved work, then reopen the source."

            # Write beside the destination, then replace it only after success.
            fd, temporary_path = tempfile.mkstemp(
                suffix=file_ext, dir=os.path.dirname(os.path.abspath(file_path)))
            os.close(fd)

            # Save based on file extension
            if file_ext in ('.xlsx', '.xlsm'):
                source_ext = os.path.splitext(self.file_path or '')[1].lower()
                if file_ext == '.xlsm' and source_ext != '.xlsm':
                    return False, 'Use .xlsx for a workbook without macros.'
                if source_ext in ('.xlsx', '.xlsm'):
                    if source_ext != file_ext:
                        return False, "Keep the source workbook's .xlsx/.xlsm extension to preserve its package type."
                    from openpyxl.utils.cell import get_column_letter
                    updates = {}
                    for row, col in self._changed_cells:
                        coordinate = f"{get_column_letter(self.df.columns.get_loc(col) + 1)}{row + 2}"
                        value = self.df.loc[row, col]
                        updates[coordinate] = None if pd.isna(value) else value
                    save_patched_workbook(self.file_path, temporary_path, self.sheet_name, updates)
                elif file_ext == '.xlsm':
                    return False, "Save as .xlsx when the source is not a macro workbook."
                else:
                    self.df.to_excel(temporary_path, index=False)
                    from openpyxl import load_workbook
                    workbook = load_workbook(temporary_path)
                    try:
                        for cells in workbook.active:
                            for cell in cells:
                                if cell.data_type == 'f':
                                    cell.data_type = 's'
                        workbook.save(temporary_path)
                    finally:
                        workbook.close()
            elif file_ext == '.csv':
                export_df = self.df.copy()
                for col in export_df.columns:
                    export_df[col] = export_df[col].map(self._csv_text)
                export_df.columns = [self._csv_text(col) for col in export_df.columns]
                export_df.to_csv(temporary_path, index=False)

            if self.file_path and self._source_hash is not None:
                if self._fingerprint(self.file_path) != self._source_hash:
                    return False, "The source file changed during save. No changes were written."
            if os.path.exists(file_path):
                backup_path = file_path + '.bak'
                shutil.copy2(file_path, backup_path)
                self.last_backup_path = backup_path
            os.replace(temporary_path, file_path)
            self.file_path = file_path
            self.file_type = 'csv' if file_ext == '.csv' else 'excel'
            self._source_hash = self._fingerprint(file_path)
            if file_ext == '.csv':
                self.sheet_name = None
                self.sheets = []
            elif not self.sheets:
                self.sheets = inspect_workbook(file_path)
                self.sheet_name = self.sheets[0]['name']
            self.modified = False
            self._changed_cells.clear()
            self._undo_stack.clear()
            return True, ""

        except PermissionError:
            return False, "Permission denied. The file may be in use by another program."
        except Exception as e:
            self.logger.error(f"Error saving file: {str(e)}")
            return False, f"Failed to save file: {str(e)}"
        finally:
            if temporary_path and os.path.exists(temporary_path):
                try:
                    os.remove(temporary_path)
                except OSError as e:
                    self.logger.warning(f"Could not remove temporary save file: {e}")

    @staticmethod
    def _fingerprint(path):
        digest = hashlib.sha256()
        with open(path, 'rb') as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b''):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _csv_text(value):
        if isinstance(value, str) and value.lstrip(' \t\r\n').startswith(('=', '+', '-', '@')):
            return "'" + value
        return value

    def undo(self):
        if not self._undo_stack:
            return False
        row, col, previous, was_changed = self._undo_stack.pop()
        self.df.loc[row, col] = previous
        if was_changed:
            self._changed_cells.add((row, col))
        else:
            self._changed_cells.discard((row, col))
        self.modified = bool(self._changed_cells)
        return True

    def get_data(self) -> pd.DataFrame:
        """Get the current dataframe"""
        return self.df

    def get_meta_info(self) -> Dict[str, Any]:
        """Get metadata about the current dataframe"""
        if self.df is None:
            return {"loaded": False}

        return {
            "loaded": True,
            "file_path": self.file_path,
            "file_name": os.path.basename(self.file_path) if self.file_path else None,
            "file_type": self.file_type,
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "column_names": list(self.df.columns),
            "sheet_name": self.sheet_name,
            "worksheets": [sheet['name'] for sheet in self.sheets],
            "modified": self.modified
        }

    def get_column_data_types(self) -> Dict[str, str]:
        """Get data types for each column"""
        if self.df is None:
            return {}

        types = {}
        for col in self.df.columns:
            # Get pandas dtype as string and simplify it
            dtype = str(self.df[col].dtype)

            if dtype.startswith('int'):
                types[col] = 'integer'
            elif dtype.startswith('float'):
                types[col] = 'float'
            elif dtype.startswith('datetime'):
                types[col] = 'datetime'
            elif dtype.startswith('bool'):
                types[col] = 'boolean'
            else:
                types[col] = 'text'

        return types

    def get_cell_value(self, row: int, col: str) -> Any:
        """Get the value of a specific cell"""
        if self.df is None or row < 0 or row >= len(self.df) or col not in self.df.columns:
            return None

        return self.df.loc[row, col]

    def update_cell(self, row: int, col: str, value: Any) -> bool:
        """Update the value of a specific cell"""
        if self.df is None or row < 0 or row >= len(self.df) or col not in self.df.columns:
            return False

        try:
            previous = self.df.loc[row, col]
            # AI responses and manual edits can replace numeric values with text.
            if isinstance(value, str) and self.df[col].dtype != object:
                self.df[col] = self.df[col].astype(object)
            self.df.loc[row, col] = value
            self.modified = True
            self._undo_stack.append((row, col, previous, (row, col) in self._changed_cells))
            # Bound memory use for large processing runs.
            if len(self._undo_stack) > 10000:
                del self._undo_stack[:len(self._undo_stack) - 10000]
            self._changed_cells.add((row, col))
            return True
        except Exception as e:
            self.logger.error(f"Error updating cell: {str(e)}")
            return False

    def update_range(self, updates: List[Dict[str, Any]], auto_save: bool = False) -> Tuple[int, int]:
        """
        Update multiple cells at once and optionally auto-save

        Args:
            updates: List of dictionaries with row, col, and value keys
            auto_save: Whether to automatically save changes to the source file after updating

        Returns:
            Tuple of (updates_applied, failed_updates)
        """
        if self.df is None:
            return 0, len(updates)

        success_count = 0
        error_count = 0

        for update in updates:
            row = update.get('row')
            col = update.get('col')
            value = update.get('result')
            if update.get('success') is False:
                error_count += 1
                continue

            if row is None or col is None or value is None:
                error_count += 1
                continue

            if self.update_cell(row, col, value):
                success_count += 1
            else:
                error_count += 1

        if success_count > 0:
            self.modified = True
            
            # Auto-save if requested and we have a file path
            if auto_save and self.file_path and success_count > 0:
                self.logger.info(f"Auto-saving changes to {self.file_path}")
                try:
                    save_success, error_msg = self.save_file()
                    if not save_success:
                        self.logger.error(f"Auto-save failed: {error_msg}")
                    else:
                        self.logger.info("Auto-save successful")
                except Exception as e:
                    self.logger.error(f"Auto-save exception: {str(e)}")

        return success_count, error_count

    def get_range(self, start_row: int, end_row: int, columns: List[str], 
                context_columns: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get a range of cells with optional context columns

        Args:
            start_row: Starting row index
            end_row: Ending row index (exclusive)
            columns: List of column names to process
            context_columns: Optional list of column names to include as context

        Returns:
            List of dictionaries with row, col, content, and optional context_data keys
        """
        if self.df is None:
            return []

        # Validate parameters
        if start_row < 0:
            start_row = 0

        if end_row > len(self.df):
            end_row = len(self.df)

        # Validate columns
        valid_columns = [col for col in columns if col in self.df.columns]
        if not valid_columns:
            return []
            
        # Validate context columns
        valid_context_columns = []
        if context_columns:
            valid_context_columns = [col for col in context_columns if col in self.df.columns and col not in valid_columns]

        # Build result
        result = []
        for row in range(start_row, end_row):
            for col in valid_columns:
                cell_data = {
                    'row': row,
                    'col': col,
                    'content': self.df.loc[row, col]
                }
                
                # Add context data from other columns if requested
                if valid_context_columns:
                    context_data = {}
                    # Add column headers as context
                    for ctx_col in valid_context_columns:
                        context_data[ctx_col] = self.df.loc[row, ctx_col]
                    
                    # Add column headers as additional context
                    context_data["headers"] = {col: col for col in valid_columns + valid_context_columns}
                    
                    cell_data['context_data'] = context_data
                
                result.append(cell_data)

        return result

    def get_data_summary(self) -> Dict[str, Any]:
        """Get a summary of the data"""
        if self.df is None:
            return {"summary": "No data loaded"}

        summary = {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "column_types": self.get_column_data_types(),
            "missing_values": self.df.isna().sum().to_dict(),
            "column_stats": {}
        }

        # Get basic stats for each column
        for col in self.df.columns:
            col_type = summary["column_types"][col]

            if col_type in ('integer', 'float'):
                # Numeric stats
                stats = {
                    "min": float(self.df[col].min()) if not pd.isna(self.df[col].min()) else None,
                    "max": float(self.df[col].max()) if not pd.isna(self.df[col].max()) else None,
                    "mean": float(self.df[col].mean()) if not pd.isna(self.df[col].mean()) else None,
                    "median": float(self.df[col].median()) if not pd.isna(self.df[col].median()) else None
                }
            elif col_type == 'datetime':
                # Date stats
                stats = {
                    "min": str(self.df[col].min()) if not pd.isna(self.df[col].min()) else None,
                    "max": str(self.df[col].max()) if not pd.isna(self.df[col].max()) else None
                }
            else:
                # Text stats
                unique_count = self.df[col].nunique()
                stats = {
                    "unique_values": unique_count,
                    "most_common": self.df[col].value_counts().head(5).to_dict() if unique_count < 100 else {}
                }

            # noinspection PyTypeChecker
            summary["column_stats"][col] = stats

        return summary

    # noinspection PyTypeChecker
    def analyze_column(self, column: str) -> Dict[str, Any]:
        """Analyze a specific column"""
        if self.df is None or column not in self.df.columns:
            return {"error": "Column not found"}

        col_data = self.df[column]
        col_type = self.get_column_data_types().get(column, 'unknown')

        # Start with basic information that works for all data types
        analysis = {
            "name": column,
            "type": col_type,
            "count": len(col_data),
            "missing": int(col_data.isna().sum()),
            "unique": int(col_data.nunique())
        }

        # Add type-specific stats with proper null handling
        if col_type in ('integer', 'float'):
            # Handle numeric statistics safely
            try:
                analysis["min"] = float(col_data.min()) if not pd.isna(col_data.min()) else None
            except (TypeError, ValueError):
                analysis["min"] = None

            try:
                analysis["max"] = float(col_data.max()) if not pd.isna(col_data.max()) else None
            except (TypeError, ValueError):
                analysis["max"] = None

            try:
                analysis["mean"] = float(col_data.mean()) if not pd.isna(col_data.mean()) else None
            except (TypeError, ValueError):
                analysis["mean"] = None

            try:
                analysis["median"] = float(col_data.median()) if not pd.isna(col_data.median()) else None
            except (TypeError, ValueError):
                analysis["median"] = None

            try:
                analysis["std"] = float(col_data.std()) if not pd.isna(col_data.std()) else None
            except (TypeError, ValueError):
                analysis["std"] = None

            # Calculate quartiles safely
            try:
                analysis["quartiles"] = {
                    "25%": float(col_data.quantile(0.25)) if not pd.isna(col_data.quantile(0.25)) else None,
                    "50%": float(col_data.quantile(0.5)) if not pd.isna(col_data.quantile(0.5)) else None,
                    "75%": float(col_data.quantile(0.75)) if not pd.isna(col_data.quantile(0.75)) else None
                }
            except (TypeError, ValueError):
                analysis["quartiles"] = {"25%": None, "50%": None, "75%": None}

        # Add histogram data for numeric columns
        if col_type in ('integer', 'float'):
            try:
                # Filter out null values before creating histogram
                valid_data = col_data.dropna()
                if len(valid_data) > 0:
                    hist_values, hist_edges = np.histogram(valid_data, bins=10)
                    analysis["histogram"] = {
                        "values": hist_values.tolist(),
                        "edges": hist_edges.tolist()
                    }
                else:
                    analysis["histogram"] = None
            except Exception:
                analysis["histogram"] = None

        # Add most common values for all types - with safe conversion to string
        try:
            value_counts = col_data.value_counts().head(10).to_dict()
            # Convert all keys to strings to avoid display issues
            analysis["most_common"] = {str(k): int(v) for k, v in value_counts.items()}
        except Exception:
            analysis["most_common"] = {}

        return analysis
