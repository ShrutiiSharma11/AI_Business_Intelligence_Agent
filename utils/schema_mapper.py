"""
Schema Mapper for normalizing different column names across datasets.
Handles flexible column naming conventions for business data.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# Column name aliases for common business fields
COLUMN_ALIASES = {
    "revenue": [
        "revenue", "sales", "sales_amount", "net_sales", "total_sales",
        "amount", "total_amount", "sale_amount", "price", "total_price",
        "revenue_amount", "sales_revenue", "gross_sales"
    ],
    "cost": [
        "cost", "total_cost", "cogs", "cost_of_goods_sold", "production_cost",
        "unit_cost", "cost_amount", "expenses", "total_expenses"
    ],
    "profit": [
        "profit", "net_profit", "gross_profit", "earnings", "income",
        "net_income", "gain", "margin"
    ],
    "quantity": [
        "quantity", "qty", "qty_sold", "units", "units_sold", "amount",
        "count", "order_quantity", "units_ordered"
    ],
    "date": [
        "date", "order_date", "sale_date", "transaction_date", "created_at",
        "order_at", "purchase_date", "datetime", "timestamp"
    ],
    "product": [
        "product", "product_name", "product_id", "item", "item_name",
        "sku", "product_code"
    ],
    "category": [
        "category", "product_category", "category_name", "type", "product_type",
        "class", "classification"
    ],
    "region": [
        "region", "location", "state", "province", "territory", "area",
        "zone", "district", "city"
    ],
    "customer": [
        "customer", "customer_name", "customer_id", "buyer", "purchaser",
        "customer_email", "client", "account"
    ],
}


@dataclass
class ColumnMapping:
    """Represents a mapping of detected columns to standard schema."""
    original_column: str
    mapped_column: str
    field_type: str
    confidence: float  # 0.0 to 1.0


class SchemaMatcher:
    """
    Intelligent schema matcher for different dataset formats.
    Maps columns from various naming conventions to standard fields.
    """

    def __init__(self):
        self.aliases = COLUMN_ALIASES
        self.detected_mappings: List[ColumnMapping] = []

    def normalize_column_name(self, column_name: str) -> str:
        """Convert column name to lowercase and remove common separators."""
        return column_name.lower().strip().replace("_", " ").replace("-", " ")

    def find_best_match(self, column_name: str) -> Tuple[Optional[str], float]:
        """
        Find the best matching field type for a column.
        Returns (field_type, confidence_score)
        """
        normalized = self.normalize_column_name(column_name)

        for field_type, aliases in self.aliases.items():
            for alias in aliases:
                if normalized == alias.replace("_", " "):
                    return field_type, 1.0
                elif alias.replace("_", " ") in normalized:
                    return field_type, 0.8
                elif normalized in alias.replace("_", " "):
                    return field_type, 0.6

        return None, 0.0

    def detect_schema(self, columns: List[str]) -> Dict[str, str]:
        """
        Detect schema mappings from a list of column names.
        Returns a dictionary of {original_column: detected_field_type}
        """
        schema_map = {}
        self.detected_mappings = []

        for column in columns:
            field_type, confidence = self.find_best_match(column)

            if field_type and confidence >= 0.6:
                schema_map[column] = field_type
                self.detected_mappings.append(
                    ColumnMapping(
                        original_column=column,
                        mapped_column=field_type,
                        field_type=field_type,
                        confidence=confidence
                    )
                )
                logger.info(
                    f"Mapped '{column}' → '{field_type}' (confidence: {confidence})"
                )
            else:
                logger.debug(f"Could not map column: {column}")

        return schema_map

    def get_field_column(self, df, field_type: str) -> Optional[str]:
        """
        Get the actual column name for a specific field type.
        Field type should be one of the keys in COLUMN_ALIASES.
        """
        if field_type not in self.aliases:
            return None

        for mapping in self.detected_mappings:
            if mapping.field_type == field_type:
                return mapping.original_column

        return None

    def get_available_fields(self) -> List[str]:
        """Get list of detected fields in the dataset."""
        return list(set(m.field_type for m in self.detected_mappings))

    def validate_required_fields(self, required_fields: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate if all required fields are available.
        Returns (is_valid, missing_fields)
        """
        available = self.get_available_fields()
        missing = [f for f in required_fields if f not in available]
        return len(missing) == 0, missing

    def get_mapping_report(self) -> str:
        """Generate a human-readable mapping report."""
        if not self.detected_mappings:
            return "No columns detected."

        report = "Column Mapping Report:\n"
        report += "-" * 50 + "\n"

        for mapping in self.detected_mappings:
            report += f"{mapping.original_column:30} → {mapping.mapped_column:15} ({mapping.confidence:.0%})\n"

        return report


def detect_date_column(df) -> Optional[str]:
    """
    Detect the date column in a DataFrame.
    Returns the column name if found.
    """
    matcher = SchemaMatcher()

    for column in df.columns:
        field_type, confidence = matcher.find_best_match(column)
        if field_type == "date" and confidence > 0.6:
            # Verify it contains datetime-like data
            try:
                pd_datetime = __import__('pandas')
                __import__('pandas').to_datetime(df[column], errors='coerce')
                return column
            except Exception:
                continue

    return None


def detect_numeric_columns(df, schema_map: Dict[str, str]) -> List[str]:
    """
    Detect numeric columns that represent business metrics.
    """
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

    # Prioritize columns that are mapped to known business fields
    business_numeric = [
        col for col in numeric_cols
        if col in schema_map and schema_map[col] in ['revenue', 'cost', 'profit', 'quantity']
    ]

    return business_numeric if business_numeric else numeric_cols
