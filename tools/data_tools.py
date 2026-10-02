"""
Data analysis tools for business calculations.
All calculations use actual data, no hallucination.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class DataAnalyzer:
    """Analyzes business data with reliable calculations."""

    def __init__(self, df: pd.DataFrame, schema_map: Dict[str, str]):
        """
        Initialize analyzer with DataFrame and schema mapping.

        Args:
            df: Pandas DataFrame with business data
            schema_map: Dictionary mapping columns to field types
        """
        self.df = df
        self.schema_map = schema_map
        self.logger = logger

    def get_total_revenue(self, revenue_col: Optional[str] = None) -> Tuple[bool, float, str]:
        """
        Calculate total revenue.
        Returns (success, amount, message)
        """
        try:
            if revenue_col is None:
                revenue_col = self._find_column("revenue")

            if revenue_col is None:
                return False, 0, "Revenue column not found in data"

            if revenue_col not in self.df.columns:
                return False, 0, f"Column '{revenue_col}' not found"

            total = self.df[revenue_col].sum()
            return True, float(total), f"Total revenue: ${total:,.2f}"

        except Exception as e:
            return False, 0, f"Error calculating revenue: {str(e)}"

    def get_total_cost(self, cost_col: Optional[str] = None) -> Tuple[bool, float, str]:
        """Calculate total cost."""
        try:
            if cost_col is None:
                cost_col = self._find_column("cost")

            if cost_col is None:
                return False, 0, "Cost column not found in data"

            if cost_col not in self.df.columns:
                return False, 0, f"Column '{cost_col}' not found"

            total = self.df[cost_col].sum()
            return True, float(total), f"Total cost: ${total:,.2f}"

        except Exception as e:
            return False, 0, f"Error calculating cost: {str(e)}"

    def get_total_profit(
            self,
            profit_col: Optional[str] = None,
            revenue_col: Optional[str] = None,
            cost_col: Optional[str] = None
    ) -> Tuple[bool, float, str]:
        """
        Calculate total profit.
        Uses existing profit column if available, otherwise calculates from revenue - cost.
        """
        try:
            # Try to use profit column if it exists
            if profit_col is None:
                profit_col = self._find_column("profit")

            if profit_col and profit_col in self.df.columns:
                total = self.df[profit_col].sum()
                return True, float(total), f"Total profit: ${total:,.2f}"

            # Otherwise calculate from revenue - cost
            if revenue_col is None:
                revenue_col = self._find_column("revenue")
            if cost_col is None:
                cost_col = self._find_column("cost")

            if not revenue_col or not cost_col:
                missing = []
                if not revenue_col:
                    missing.append("revenue")
                if not cost_col:
                    missing.append("cost")
                return False, 0, f"Cannot calculate profit: {', '.join(missing)} column(s) not found"

            if revenue_col not in self.df.columns or cost_col not in self.df.columns:
                return False, 0, "Required columns for profit calculation not found"

            profit = (self.df[revenue_col] - self.df[cost_col]).sum()
            return True, float(profit), f"Total profit: ${profit:,.2f}"

        except Exception as e:
            return False, 0, f"Error calculating profit: {str(e)}"

    def get_total_loss(
            self,
            revenue_col: Optional[str] = None,
            cost_col: Optional[str] = None
    ) -> Tuple[bool, float, str]:
        """
        Calculate total loss (negative profit).
        """
        success, profit, msg = self.get_total_profit(
            revenue_col=revenue_col,
            cost_col=cost_col
        )

        if not success:
            return False, 0, msg

        if profit >= 0:
            return False, 0, f"No loss. Profit: ${profit:,.2f}"

        loss = abs(profit)
        return True, loss, f"Total loss: ${loss:,.2f}"

    def get_profit_margin(
            self,
            revenue_col: Optional[str] = None,
            cost_col: Optional[str] = None
    ) -> Tuple[bool, float, str]:
        """
        Calculate profit margin percentage.
        """
        try:
            success, profit, _ = self.get_total_profit(
                revenue_col=revenue_col,
                cost_col=cost_col
            )

            if not success:
                return False, 0, "Cannot calculate margin without profit"

            success, revenue, _ = self.get_total_revenue(revenue_col=revenue_col)
            if not success or revenue == 0:
                return False, 0, "Cannot calculate margin: invalid revenue"

            margin = (profit / revenue) * 100
            return True, float(margin), f"Profit margin: {margin:.2f}%"

        except Exception as e:
            return False, 0, f"Error calculating profit margin: {str(e)}"

    def get_average_order_value(self, revenue_col: Optional[str] = None) -> Tuple[bool, float, str]:
        """Calculate average order value."""
        try:
            if revenue_col is None:
                revenue_col = self._find_column("revenue")

            if revenue_col is None:
                return False, 0, "Revenue column not found"

            aov = self.df[revenue_col].mean()
            return True, float(aov), f"Average order value: ${aov:,.2f}"

        except Exception as e:
            return False, 0, f"Error calculating AOV: {str(e)}"

    def get_top_products(
            self,
            product_col: Optional[str] = None,
            revenue_col: Optional[str] = None,
            n: int = 5
    ) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Get top N products by revenue.
        """
        try:
            if product_col is None:
                product_col = self._find_column("product")
            if revenue_col is None:
                revenue_col = self._find_column("revenue")

            if not product_col or not revenue_col:
                missing = []
                if not product_col:
                    missing.append("product")
                if not revenue_col:
                    missing.append("revenue")
                return False, [], f"Missing columns: {', '.join(missing)}"

            if product_col not in self.df.columns or revenue_col not in self.df.columns:
                return False, [], "Required columns not found"

            top_products = self.df.groupby(product_col)[revenue_col].sum().nlargest(n)

            result = [
                {"product": product, "revenue": float(revenue)}
                for product, revenue in top_products.items()
            ]

            return True, result, f"Top {n} products by revenue"

        except Exception as e:
            return False, [], f"Error getting top products: {str(e)}"

    def get_revenue_by_region(
            self,
            region_col: Optional[str] = None,
            revenue_col: Optional[str] = None
    ) -> Tuple[bool, Dict[str, float], str]:
        """Get revenue breakdown by region."""
        try:
            if region_col is None:
                region_col = self._find_column("region")
            if revenue_col is None:
                revenue_col = self._find_column("revenue")

            if not region_col or not revenue_col:
                return False, {}, "Region or revenue column not found"

            if region_col not in self.df.columns or revenue_col not in self.df.columns:
                return False, {}, "Required columns not found"

            revenue_by_region = self.df.groupby(region_col)[revenue_col].sum().to_dict()

            return True, revenue_by_region, "Revenue by region"

        except Exception as e:
            return False, {}, f"Error calculating revenue by region: {str(e)}"

    def get_monthly_sales(
            self,
            date_col: Optional[str] = None,
            revenue_col: Optional[str] = None
    ) -> Tuple[bool, Dict[str, float], str]:
        """
        Get monthly sales trend.
        """
        try:
            if date_col is None:
                date_col = self._find_column("date")
            if revenue_col is None:
                revenue_col = self._find_column("revenue")

            if not date_col or not revenue_col:
                return False, {}, "Date or revenue column not found"

            if date_col not in self.df.columns or revenue_col not in self.df.columns:
                return False, {}, "Required columns not found"

            # Convert to datetime if needed
            df_temp = self.df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')

            # Remove rows with invalid dates
            df_temp = df_temp.dropna(subset=[date_col])

            if df_temp.empty:
                return False, {}, "No valid date data found"

            # Group by month
            monthly = df_temp.set_index(date_col).resample('M')[revenue_col].sum()

            result = {
                date.strftime("%Y-%m"): float(value)
                for date, value in monthly.items()
            }

            return True, result, "Monthly sales"

        except Exception as e:
            return False, {}, f"Error calculating monthly sales: {str(e)}"

    def get_highest_revenue_product(
            self,
            product_col: Optional[str] = None,
            revenue_col: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any], str]:
        """Get product with highest revenue."""
        try:
            success, top_products, msg = self.get_top_products(
                product_col=product_col,
                revenue_col=revenue_col,
                n=1
            )

            if not success or not top_products:
                return False, {}, msg

            return True, top_products[0], f"Highest revenue product: {top_products[0]['product']}"

        except Exception as e:
            return False, {}, f"Error finding highest revenue product: {str(e)}"

    def get_highest_revenue_region(
            self,
            region_col: Optional[str] = None,
            revenue_col: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any], str]:
        """Get region with highest revenue."""
        try:
            success, revenue_by_region, msg = self.get_revenue_by_region(
                region_col=region_col,
                revenue_col=revenue_col
            )

            if not success:
                return False, {}, msg

            if not revenue_by_region:
                return False, {}, "No regional data available"

            highest_region = max(revenue_by_region, key=revenue_by_region.get)
            result = {
                "region": highest_region,
                "revenue": revenue_by_region[highest_region]
            }

            return True, result, f"Highest revenue region: {highest_region}"

        except Exception as e:
            return False, {}, f"Error finding highest revenue region: {str(e)}"

    def get_data_summary(self) -> Dict[str, Any]:
        """Get comprehensive data summary."""
        return {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "column_names": self.df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            "missing_values": self.df.isnull().sum().to_dict(),
            "schema_map": self.schema_map
        }

    def _find_column(self, field_type: str) -> Optional[str]:
        """
        Find column name for a specific field type.
        """
        for col, ftype in self.schema_map.items():
            if ftype == field_type:
                return col
        return None
