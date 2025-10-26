"""
Unified MatrixLoader class with hash-based caching for price matrix operations.

This module provides a centralized, robust implementation for loading and caching
price matrices from both CSV and Excel formats with comprehensive validation.
"""

import hashlib
import io
import logging
from datetime import datetime
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class MatrixLoader:
    """
    Unified matrix loader with hash-based caching for CSV and Excel formats.

    Provides consistent parsing, validation, and caching for price matrix data
    with support for both CSV (semicolon-separated) and Excel formats.
    """

    def __init__(self):
        """Initialize MatrixLoader with empty cache."""
        self._cache: dict[str, dict[str, Any]] = {}
        self._cache_keys: dict[str, str] = {}

    def _hash_bytes(self, data: bytes | None) -> str | None:
        """
        Generate SHA256 hash for bytes data.

        Args:
            data: Bytes data to hash

        Returns:
            SHA256 hash string or None if data is empty
        """
        if not data:
            return None
        try:
            return hashlib.sha256(data).hexdigest()
        except Exception:
            # Fallback to length-based hash if SHA256 fails
            return f"len_{len(data)}" if data else None

    def _hash_text(self, text: str | None) -> str | None:
        """
        Generate SHA256 hash for text data.

        Args:
            text: Text data to hash

        Returns:
            SHA256 hash string or None if text is empty
        """
        if not text:
            return None
        try:
            return hashlib.sha256(
                text.encode(
                    "utf-8",
                    errors="ignore")).hexdigest()
        except Exception:
            # Fallback to length-based hash if SHA256 fails
            return f"len_{len(text)}" if text else None

    def _validate_structure(self, df: pd.DataFrame) -> list[str]:
        """
        Validate matrix structure according to requirements.

        Expected structure:
        - First column (index): "Anzahl Module" with numeric module counts
        - Additional columns: Battery storage model names
        - Last column: "Ohne Speicher"

        Args:
            df: DataFrame to validate

        Returns:
            List of validation error messages
        """
        errors = []

        # Check if matrix is empty
        if df.empty:
            errors.append("Matrix is empty")
            return errors

        # Check for minimum required columns
        if len(df.columns) == 0:
            errors.append("Matrix must have at least one column")
            return errors

        # Check index name (should be "Anzahl Module")
        index_name = str(df.index.name).strip(
        ).lower() if df.index.name else ""
        if index_name not in ["anzahl module", "anzahl_module"]:
            errors.append(
                f"Index should be 'Anzahl Module', found: '{
                    df.index.name}'")

        # Check if last column is "Ohne Speicher" (case-insensitive)
        last_column = str(df.columns[-1]).strip().lower()
        if last_column != "ohne speicher":
            errors.append(
                f"Last column should be 'Ohne Speicher', found: '{df.columns[-1]}'")

        # Check for duplicate module counts in index
        if len(df.index) != len(set(df.index)):
            duplicates = df.index[df.index.duplicated()].tolist()
            errors.append(f"Duplicate module counts found: {duplicates}")

        # Check that index contains numeric values
        try:
            numeric_index = pd.to_numeric(df.index, errors='coerce')
            if numeric_index.isnull().any():
                invalid_indices = df.index[numeric_index.isnull()].tolist()
                errors.append(
                    f"Non-numeric module counts found: {invalid_indices}")
        except Exception as e:
            errors.append(f"Error validating index as numeric: {e}")

        # Check for non-numeric prices in data columns
        for col in df.columns:
            try:
                numeric_col = pd.to_numeric(df[col], errors='coerce')
                if numeric_col.isnull().any():
                    null_count = numeric_col.isnull().sum()
                    errors.append(
                        f"Column '{col}' contains {null_count} non-numeric values")
            except Exception as e:
                errors.append(
                    f"Error validating column '{col}' as numeric: {e}")

        # Check for completely empty rows or columns
        empty_rows = df.isnull().all(axis=1).sum()
        empty_cols = df.isnull().all(axis=0).sum()

        if empty_rows > 0:
            errors.append(
                f"Matrix contains {empty_rows} completely empty rows")
        if empty_cols > 0:
            errors.append(
                f"Matrix contains {empty_cols} completely empty columns")

        return errors

    def _parse_csv(self, csv_data: str |
                   io.StringIO) -> tuple[pd.DataFrame | None, list[str]]:
        """
        Parse CSV data to DataFrame with German formatting support.

        Expected CSV format:
        - Separator: semicolon (;)
        - Decimal: comma (,)
        - Thousands separator: period (.)
        - First column: "Anzahl Module" (used as index)

        Args:
            csv_data: CSV content as string or StringIO object

        Returns:
            Tuple of (DataFrame, error_messages)
        """
        errors = []

        if not csv_data:
            errors.append("CSV data is empty")
            return None, errors

        try:
            # Convert string to StringIO if needed
            if isinstance(csv_data, str):
                csv_file_like = io.StringIO(csv_data)
            else:
                csv_file_like = csv_data
                csv_file_like.seek(0)

            # Try to read CSV with expected format
            df = pd.read_csv(
                csv_file_like,
                sep=";",
                decimal=",",
                index_col=0,
                thousands=".",
                comment="#"
            )

            # Handle case where index column is not properly detected
            if df.empty or (
                df.index.name is None or str(
                    df.index.name).strip().lower() not in [
                    "anzahl module",
                    "anzahl_module"]):

                # Look for "Anzahl Module" column in the data
                csv_file_like.seek(0)
                temp_df = pd.read_csv(
                    csv_file_like,
                    sep=";",
                    decimal=",",
                    thousands=".",
                    comment="#")

                potential_index_cols = [col for col in temp_df.columns if str(
                    col).strip().lower() in ["anzahl module", "anzahl_module"]]

                if potential_index_cols:
                    df = temp_df.set_index(potential_index_cols[0])
                elif not temp_df.empty and pd.api.types.is_numeric_dtype(temp_df.iloc[:, 0]):
                    # Use first column as index if it's numeric
                    df = temp_df.set_index(temp_df.columns[0])
                else:
                    errors.append(
                        "Could not find 'Anzahl Module' column or suitable numeric index column")
                    return None, errors

            # Set proper index name
            df.index.name = "Anzahl Module"

            # Convert index to numeric and filter out invalid values
            df.index = pd.to_numeric(df.index, errors="coerce")
            df = df[df.index.notna()]

            if df.empty:
                errors.append("No valid numeric module counts found in index")
                return None, errors

            # Convert index to integer
            df.index = df.index.astype(int)

            # Process price columns: handle German number format
            for col in df.columns:
                if df[col].dtype == "object":
                    # Remove thousands separators (periods) and replace decimal
                    # comma with period
                    df[col] = (
                        df[col]
                        .astype(str)
                        # Remove thousands separator
                        .str.replace(".", "", regex=False)
                        # Replace decimal comma with period
                        .str.replace(",", ".", regex=False)
                    )

                # Convert to numeric
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # Remove completely empty rows and columns
            df.dropna(axis=0, how="all", inplace=True)
            df.dropna(axis=1, how="all", inplace=True)

            if df.empty:
                errors.append(
                    "Matrix is empty after cleaning and type conversion")
                return None, errors

            logger.info(
                f"Successfully parsed CSV matrix with shape: {
                    df.shape}")
            return df, errors

        except pd.errors.EmptyDataError:
            errors.append("CSV file is empty")
            return None, errors
        except ValueError as ve:
            errors.append(f"CSV value conversion error: {ve}")
            return None, errors
        except Exception as e:
            errors.append(f"Error parsing CSV: {e}")
            return None, errors

    def _parse_excel(
            self, excel_bytes: bytes) -> tuple[pd.DataFrame | None, list[str]]:
        """
        Parse Excel data to DataFrame.

        Expected Excel format:
        - First column: "Anzahl Module" (used as index)
        - Header row: Column names for storage models
        - Numeric data: Prices in German or international format

        Args:
            excel_bytes: Excel file content as bytes

        Returns:
            Tuple of (DataFrame, error_messages)
        """
        errors = []

        if not excel_bytes:
            errors.append("Excel data is empty")
            return None, errors

        try:
            excel_file_like = io.BytesIO(excel_bytes)

            # Read Excel file with first column as index
            df = pd.read_excel(excel_file_like, index_col=0, header=0)

            if df.empty:
                errors.append("Excel file is empty or first column is empty")
                return None, errors

            # Set proper index name
            df.index.name = "Anzahl Module"

            # Convert index to numeric and filter out invalid values
            df.index = pd.to_numeric(df.index, errors="coerce")
            df = df[df.index.notna()]

            if df.empty:
                errors.append(
                    "No valid numeric module counts found in Excel index")
                return None, errors

            # Convert index to integer
            df.index = df.index.astype(int)

            # Process price columns: handle German number format
            for col in df.columns:
                if df[col].dtype == "object":
                    # Handle string-formatted numbers (German format)
                    df[col] = (
                        df[col]
                        .astype(str)
                        # Remove thousands separator
                        .str.replace(".", "", regex=False)
                        # Replace decimal comma with period
                        .str.replace(",", ".", regex=False)
                    )

                # Convert to numeric
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # Remove completely empty rows and columns
            df.dropna(axis=0, how="all", inplace=True)
            df.dropna(axis=1, how="all", inplace=True)

            if df.empty:
                errors.append(
                    "Excel matrix is empty after cleaning and type conversion")
                return None, errors

            logger.info(
                f"Successfully parsed Excel matrix with shape: {
                    df.shape}")
            return df, errors

        except ValueError as ve:
            errors.append(f"Excel value conversion error: {ve}")
            return None, errors
        except Exception as e:
            errors.append(f"Error parsing Excel: {e}")
            return None, errors

    def load_matrix(self,
                    excel_bytes: bytes | None = None,
                    csv_data: str | None = None) -> tuple[pd.DataFrame | None,
                                                          str,
                                                          list[str]]:
        """
        Load matrix with caching based on data hash.

        Priority: Excel data is preferred over CSV if both are provided.

        Args:
            excel_bytes: Excel file content as bytes (optional)
            csv_data: CSV content as string (optional)

        Returns:
            Tuple of (DataFrame, source_type, error_messages)
            - DataFrame: Loaded and validated matrix or None if failed
            - source_type: "Excel", "CSV", or "None" indicating data source
            - error_messages: List of any errors or warnings encountered
        """
        all_errors = []

        # Generate hashes for caching
        excel_hash = self._hash_bytes(excel_bytes) if excel_bytes else None
        csv_hash = self._hash_text(csv_data) if csv_data else None

        # Try Excel first (higher priority)
        if excel_hash:
            # Check cache
            if (excel_hash in self._cache and
                    self._cache[excel_hash].get("dataframe") is not None):

                cached_entry = self._cache[excel_hash]
                logger.debug(
                    f"Using cached Excel matrix (hash: {excel_hash[:8]}...)")
                return (cached_entry["dataframe"],
                        cached_entry["source"],
                        cached_entry.get("errors", []))

            # Parse Excel data
            df_excel, excel_errors = self._parse_excel(excel_bytes)
            all_errors.extend([f"Excel: {err}" for err in excel_errors])

            if df_excel is not None and not df_excel.empty:
                # Validate structure
                validation_errors = self._validate_structure(df_excel)
                all_errors.extend(
                    [f"Excel validation: {err}" for err in validation_errors])

                # Cache the result (even with validation warnings)
                self._cache[excel_hash] = {
                    "dataframe": df_excel,
                    "source": "Excel",
                    "timestamp": datetime.now(),
                    "errors": excel_errors + validation_errors
                }

                logger.info(
                    f"Loaded Excel matrix with shape: {
                        df_excel.shape}")
                return df_excel, "Excel", all_errors
            # Excel parsing failed, invalidate cache
            if excel_hash in self._cache:
                del self._cache[excel_hash]

        # Try CSV if Excel failed or not provided
        if csv_hash:
            # Check cache
            if (csv_hash in self._cache and
                    self._cache[csv_hash].get("dataframe") is not None):

                cached_entry = self._cache[csv_hash]
                logger.debug(
                    f"Using cached CSV matrix (hash: {csv_hash[:8]}...)")
                return (cached_entry["dataframe"],
                        cached_entry["source"],
                        cached_entry.get("errors", []))

            # Parse CSV data
            df_csv, csv_errors = self._parse_csv(csv_data)
            all_errors.extend([f"CSV: {err}" for err in csv_errors])

            if df_csv is not None and not df_csv.empty:
                # Validate structure
                validation_errors = self._validate_structure(df_csv)
                all_errors.extend(
                    [f"CSV validation: {err}" for err in validation_errors])

                # Cache the result (even with validation warnings)
                self._cache[csv_hash] = {
                    "dataframe": df_csv,
                    "source": "CSV",
                    "timestamp": datetime.now(),
                    "errors": csv_errors + validation_errors
                }

                logger.info(f"Loaded CSV matrix with shape: {df_csv.shape}")
                return df_csv, "CSV", all_errors
            # CSV parsing failed, invalidate cache
            if csv_hash in self._cache:
                del self._cache[csv_hash]

        # Neither Excel nor CSV could be loaded
        if not excel_bytes and not csv_data:
            all_errors.append(
                "No matrix data provided (both Excel and CSV are empty)")
        else:
            all_errors.append(
                "Failed to load matrix from both Excel and CSV sources")

        return None, "None", all_errors

    def get_cache_info(self) -> dict[str, Any]:
        """
        Get information about current cache state.

        Returns:
            Dictionary with cache statistics and information
        """
        cache_info = {
            "total_entries": len(self._cache),
            "entries": []
        }

        for hash_key, entry in self._cache.items():
            cache_info["entries"].append({
                "hash": hash_key[:8] + "...",
                "source": entry.get("source", "Unknown"),
                "timestamp": entry.get("timestamp"),
                "shape": entry["dataframe"].shape if entry.get("dataframe") is not None else None,
                "error_count": len(entry.get("errors", []))
            })

        return cache_info

    def clear_cache(self) -> None:
        """Clear all cached matrix data."""
        self._cache.clear()
        self._cache_keys.clear()
        logger.info("Matrix cache cleared")

    def validate_matrix_file(self,
                             excel_bytes: bytes | None = None,
                             csv_data: str | None = None) -> tuple[bool,
                                                                   list[str]]:
        """
        Validate matrix file without caching (for upload validation).

        Args:
            excel_bytes: Excel file content as bytes (optional)
            csv_data: CSV content as string (optional)

        Returns:
            Tuple of (is_valid, error_messages)
        """
        df, source, errors = self.load_matrix(excel_bytes, csv_data)

        is_valid = df is not None and not df.empty

        # Add specific validation for upload requirements
        if is_valid:
            validation_errors = self._validate_structure(df)
            errors.extend(validation_errors)

            # Check for critical structural issues
            critical_errors = [
                err for err in errors
                if any(keyword in err.lower() for keyword in [
                    "empty", "anzahl module", "ohne speicher", "duplicate"
                ])
            ]

            if critical_errors:
                is_valid = False

        return is_valid, errors
