"""
Validators for data integrity and business logic.
"""

import logging
from typing import List, Tuple, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates data quality and business constraints."""

    @staticmethod
    def check_missing_values(df: pd.DataFrame, columns: List[str]) -> Tuple[bool, str]:
        """Check if specified columns have missing values."""
        missing_cols = [col for col in columns if col in df.columns and df[col].isnull().any()]

        if not missing_cols:
            return True, f"No missing values in {columns}"

        missing_info = ", ".join(
            [f"{col} ({df[col].isnull().sum()} missing)" for col in missing_cols]
        )
        return False, f"Missing values found in: {missing_info}"

    @staticmethod
    def check_numeric_columns(df: pd.DataFrame, columns: List[str]) -> Tuple[bool, str]:
        """Check if specified columns are numeric."""
        non_numeric = [
            col for col in columns
            if col in df.columns and not pd.api.types.is_numeric_dtype(df[col])
        ]

        if not non_numeric:
            return True, f"All {columns} are numeric"

        return False, f"Non-numeric columns: {non_numeric}"

    @staticmethod
    def validate_revenue_calculation(
            df: pd.DataFrame,
            revenue_col: Optional[str] = None,
            cost_col: Optional[str] = None,
            profit_col: Optional[str] = None
    ) -> Tuple[bool, str, dict]:
        """
        Validate revenue/cost/profit calculations.
        Returns (is_valid, message, validation_details)
        """
        details = {}

        # Check revenue column
        if revenue_col and revenue_col not in df.columns:
            return False, f"Revenue column not found: {revenue_col}", details

        if revenue_col:
            is_numeric, msg = DataValidator.check_numeric_columns(df, [revenue_col])
            if not is_numeric:
                return False, f"Revenue column is not numeric: {msg}", details
            details['revenue_sum'] = df[revenue_col].sum()
            details['revenue_count'] = df[revenue_col].count()

        # Check cost column
        if cost_col and cost_col not in df.columns:
            return False, f"Cost column not found: {cost_col}", details

        if cost_col:
            is_numeric, msg = DataValidator.check_numeric_columns(df, [cost_col])
            if not is_numeric:
                return False, f"Cost column is not numeric: {msg}", details
            details['cost_sum'] = df[cost_col].sum()
            details['cost_count'] = df[cost_col].count()

        # Check profit column
        if profit_col and profit_col not in df.columns:
            logger.info(f"Profit column not found: {profit_col}. Will calculate from revenue - cost.")
            details['profit_calculated'] = True
        elif profit_col:
            is_numeric, msg = DataValidator.check_numeric_columns(df, [profit_col])
            if not is_numeric:
                return False, f"Profit column is not numeric: {msg}", details
            details['profit_sum'] = df[profit_col].sum()
            details['profit_count'] = df[profit_col].count()

        return True, "Validation passed", details

    @staticmethod
    def check_date_range(df: pd.DataFrame, date_col: str) -> Tuple[bool, str, dict]:
        """Check date column range and validity."""
        if date_col not in df.columns:
            return False, f"Date column not found: {date_col}", {}

        try:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            null_dates = df[date_col].isnull().sum()

            if null_dates > 0:
                logger.warning(f"Found {null_dates} invalid dates in {date_col}")

            min_date = df[date_col].min()
            max_date = df[date_col].max()

            details = {
                'min_date': str(min_date),
                'max_date': str(max_date),
                'invalid_dates': int(null_dates)
            }

            return True, f"Date range: {min_date.date()} to {max_date.date()}", details
        except Exception as e:
            return False, f"Error processing date column: {str(e)}", {}

    @staticmethod
    def validate_quantity_column(df: pd.DataFrame, qty_col: str) -> Tuple[bool, str]:
        """Validate quantity column."""
        if qty_col not in df.columns:
            return False, f"Quantity column not found: {qty_col}"

        is_numeric, msg = DataValidator.check_numeric_columns(df, [qty_col])
        if not is_numeric:
            return False, msg

        # Check for negative quantities (should not exist)
        negative_qty = (df[qty_col] < 0).sum()
        if negative_qty > 0:
            logger.warning(f"Found {negative_qty} rows with negative quantities")

        return True, f"Quantity column valid ({df[qty_col].sum()} total units)"


class BusinessRulesValidator:
    """Validates business logic and rules."""

    @staticmethod
    def validate_profit_calculation(
            revenue: float,
            cost: float,
            profit: Optional[float] = None
    ) -> Tuple[bool, str, float]:
        """
        Validate profit calculation logic.
        Returns (is_valid, message, calculated_profit)
        """
        if revenue < 0 or cost < 0:
            return False, "Revenue and cost must be non-negative", 0

        calculated_profit = revenue - cost

        if profit is not None and abs(calculated_profit - profit) > 0.01:
            return False, "Profit mismatch: expected revenue - cost", calculated_profit

        return True, "Profit calculation valid", calculated_profit

    @staticmethod
    def calculate_profit_margin(
            revenue: float,
            profit: float
    ) -> Tuple[bool, str, float]:
        """
        Calculate profit margin percentage.
        Returns (is_valid, message, margin_percentage)
        """
        if revenue == 0:
            return False, "Revenue cannot be zero for margin calculation", 0

        margin = (profit / revenue) * 100
        return True, f"Profit margin: {margin:.2f}%", margin

    @staticmethod
    def validate_aggregation(
            values: List[float],
            expected_sum: Optional[float] = None
    ) -> Tuple[bool, str, float]:
        """Validate sum aggregation."""
        try:
            total = sum(float(v) for v in values if pd.notna(v))

            if expected_sum is not None and abs(total - expected_sum) > 0.01:
                return False, "Sum mismatch", total

            return True, f"Aggregation valid: {total:.2f}", total
        except (ValueError, TypeError) as e:
            return False, f"Aggregation error: {str(e)}", 0
