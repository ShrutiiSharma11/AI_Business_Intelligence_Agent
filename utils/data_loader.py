"""
Data Loader for handling different file formats.
Supports CSV, Excel, and basic text files.
"""

import logging
import os
from typing import Optional, Tuple
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles loading and validation of data files."""

    SUPPORTED_FORMATS = ['.csv', '.xlsx', '.xls', '.txt']
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    @staticmethod
    def validate_file(file_path: str) -> Tuple[bool, str]:
        """
        Validate if file exists and is supported format.
        Returns (is_valid, message)
        """
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"

        file_size = os.path.getsize(file_path)
        if file_size > DataLoader.MAX_FILE_SIZE:
            return False, f"File too large. Max size: {DataLoader.MAX_FILE_SIZE / 1024 / 1024}MB"

        file_ext = Path(file_path).suffix.lower()
        if file_ext not in DataLoader.SUPPORTED_FORMATS:
            return False, f"Unsupported format: {file_ext}. Supported: {DataLoader.SUPPORTED_FORMATS}"

        return True, "File validation passed"

    @staticmethod
    def load_csv(file_path: str) -> Tuple[Optional[pd.DataFrame], str]:
        """Load CSV file."""
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                return None, "CSV file is empty"
            logger.info(f"Loaded CSV: {file_path} ({len(df)} rows, {len(df.columns)} columns)")
            return df, "CSV loaded successfully"
        except Exception as e:
            return None, f"Error loading CSV: {str(e)}"

    @staticmethod
    def load_excel(file_path: str) -> Tuple[Optional[pd.DataFrame], str]:
        """Load Excel file."""
        try:
            # Try to detect sheet name
            xls = pd.ExcelFile(file_path)
            sheet_name = xls.sheet_names[0] if xls.sheet_names else 0

            df = pd.read_excel(file_path, sheet_name=sheet_name)
            if df.empty:
                return None, "Excel file is empty"

            logger.info(
                f"Loaded Excel sheet '{sheet_name}': {file_path} "
                f"({len(df)} rows, {len(df.columns)} columns)"
            )
            return df, "Excel file loaded successfully"
        except Exception as e:
            return None, f"Error loading Excel: {str(e)}"

    @staticmethod
    def load_text(file_path: str) -> Tuple[Optional[pd.DataFrame], str]:
        """Attempt to load tab-separated or space-separated text file."""
        try:
            # Try different delimiters
            for delimiter in ['\t', ' ', ',', ';']:
                try:
                    df = pd.read_csv(file_path, delimiter=delimiter)
                    if not df.empty and len(df.columns) > 1:
                        logger.info(
                            f"Loaded text file with delimiter '{repr(delimiter)}': {file_path} "
                            f"({len(df)} rows, {len(df.columns)} columns)"
                        )
                        return df, "Text file loaded successfully"
                except Exception:
                    continue

            return None, "Could not parse text file with any common delimiter"
        except Exception as e:
            return None, f"Error loading text file: {str(e)}"

    @staticmethod
    def load_file(file_path: str) -> Tuple[Optional[pd.DataFrame], str]:
        """
        Load any supported file format.
        Returns (DataFrame, message)
        """
        is_valid, validation_msg = DataLoader.validate_file(file_path)
        if not is_valid:
            return None, validation_msg

        file_ext = Path(file_path).suffix.lower()

        if file_ext == '.csv':
            return DataLoader.load_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            return DataLoader.load_excel(file_path)
        elif file_ext == '.txt':
            return DataLoader.load_text(file_path)

        return None, f"Unsupported file format: {file_ext}"

    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Basic data cleaning.
        """
        # Remove completely empty rows and columns
        df = df.dropna(how='all')
        df = df.loc[:, ~df.columns.duplicated()]

        # Clean column names
        df.columns = df.columns.str.strip().str.replace(r'\s+', '_', regex=True)

        logger.info(f"DataFrame cleaned: {len(df)} rows, {len(df.columns)} columns")
        return df

    @staticmethod
    def get_data_info(df: pd.DataFrame) -> dict:
        """Get comprehensive information about a DataFrame."""
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
            'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
            'text_columns': df.select_dtypes(include=['object']).columns.tolist(),
        }
