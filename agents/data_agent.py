"""
Data Agent: Handles uploaded business data analysis.
Uses Pandas for reliable calculations, never hallucinating numbers.
"""

import logging
from typing import Dict, Any, Optional, List
import json

import pandas as pd
from langchain.tools import tool
from langchain.pydantic_v1 import BaseModel, Field

from utils.schema_mapper import SchemaMatcher
from utils.validators import DataValidator
from tools.data_tools import DataAnalyzer

logger = logging.getLogger(__name__)


class DataAgentState(BaseModel):

    """State for data agent."""

    df: Optional[pd.DataFrame] = None

    schema_map: Optional[Dict[str, str]] = None

    analyzer: Optional[DataAnalyzer] = None

    last_result: Optional[Dict[str, Any]] = None

    error_message: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True


class DataAgent:
    """
    Agent for analyzing uploaded business datasets.
    Performs actual calculations using Pandas, no hallucination.
    """

    def __init__(self):
        self.state = DataAgentState()
        self.logger = logger
        self.matcher = SchemaMatcher()

    def load_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Load and initialize data for analysis.

        Returns:
            Dictionary with data info and schema
        """
        try:
            # Store DataFrame
            self.state.df = df

            # Detect schema
            self.state.schema_map = self.matcher.detect_schema(df.columns.tolist())

            # Initialize analyzer
            self.state.analyzer = DataAnalyzer(df, self.state.schema_map)

            # Get data summary
            summary = self.state.analyzer.get_data_summary()

            self.logger.info(f"Data loaded successfully: {len(df)} rows, {len(df.columns)} columns")

            return {
                "success": True,
                "message": "Data loaded successfully",
                "summary": summary,
                "schema_mapping": self.state.schema_map
            }

        except Exception as e:
            self.state.error_message = str(e)
            self.logger.error(f"Error loading data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def process_question(self, question: str) -> Dict[str, Any]:
        """
        Process a natural language question about the data.
        Routes to appropriate calculation method.

        Returns:
            Analysis result
        """
        if self.state.df is None or self.state.analyzer is None:
            return {
                "success": False,
                "error": "No data loaded. Please upload a file first."
            }

        question_lower = question.lower()

        # Route to appropriate calculation
        if "total revenue" in question_lower:
            return self._handle_total_revenue()

        elif "total cost" in question_lower or "total expense" in question_lower:
            return self._handle_total_cost()

        elif "total profit" in question_lower:
            return self._handle_total_profit()

        elif "profit margin" in question_lower or "margin" in question_lower:
            return self._handle_profit_margin()

        elif "average order value" in question_lower or "aov" in question_lower:
            return self._handle_average_order_value()

        elif "top" in question_lower and ("product" in question_lower or "seller" in question_lower):
            return self._handle_top_products(question)

        elif "highest revenue" in question_lower and "region" in question_lower:
            return self._handle_highest_revenue_region()

        elif "revenue by region" in question_lower or "region" in question_lower:
            return self._handle_revenue_by_region()

        elif "monthly" in question_lower or "trend" in question_lower:
            return self._handle_monthly_sales()

        elif "loss" in question_lower:
            return self._handle_total_loss()

        else:
            return self._handle_general_query(question)

    def _handle_total_revenue(self) -> Dict[str, Any]:
        """Calculate total revenue."""
        success, amount, msg = self.state.analyzer.get_total_revenue()

        return {
            "success": success,
            "result": msg,
            "value": amount if success else None,
            "type": "revenue_total"
        }

    def _handle_total_cost(self) -> Dict[str, Any]:
        """Calculate total cost."""
        success, amount, msg = self.state.analyzer.get_total_cost()

        return {
            "success": success,
            "result": msg,
            "value": amount if success else None,
            "type": "cost_total"
        }

    def _handle_total_profit(self) -> Dict[str, Any]:
        """Calculate total profit."""
        success, amount, msg = self.state.analyzer.get_total_profit()

        return {
            "success": success,
            "result": msg,
            "value": amount if success else None,
            "type": "profit_total"
        }

    def _handle_total_loss(self) -> Dict[str, Any]:
        """Calculate total loss."""
        success, amount, msg = self.state.analyzer.get_total_loss()

        return {
            "success": success,
            "result": msg,
            "value": amount if success else None,
            "type": "loss_total"
        }

    def _handle_profit_margin(self) -> Dict[str, Any]:
        """Calculate profit margin."""
        success, margin, msg = self.state.analyzer.get_profit_margin()

        return {
            "success": success,
            "result": msg,
            "value": margin if success else None,
            "type": "profit_margin"
        }

    def _handle_average_order_value(self) -> Dict[str, Any]:
        """Calculate average order value."""
        success, aov, msg = self.state.analyzer.get_average_order_value()

        return {
            "success": success,
            "result": msg,
            "value": aov if success else None,
            "type": "average_order_value"
        }

    def _handle_top_products(self, question: str) -> Dict[str, Any]:
        """Get top products."""
        # Extract number if specified
        n = 5  # default
        if "top" in question:
            words = question.split()
            for i, word in enumerate(words):
                if word.lower() == "top" and i + 1 < len(words):
                    try:
                        n = int(words[i + 1])
                    except ValueError:
                        pass

        success, products, msg = self.state.analyzer.get_top_products(n=n)

        return {
            "success": success,
            "result": msg,
            "data": products if success else [],
            "type": "top_products"
        }

    def _handle_highest_revenue_region(self) -> Dict[str, Any]:
        """Get highest revenue region."""
        success, result, msg = self.state.analyzer.get_highest_revenue_region()

        return {
            "success": success,
            "result": msg,
            "data": result if success else {},
            "type": "highest_revenue_region"
        }

    def _handle_revenue_by_region(self) -> Dict[str, Any]:
        """Get revenue breakdown by region."""
        success, revenue_by_region, msg = self.state.analyzer.get_revenue_by_region()

        return {
            "success": success,
            "result": msg,
            "data": revenue_by_region if success else {},
            "type": "revenue_by_region"
        }

    def _handle_monthly_sales(self) -> Dict[str, Any]:
        """Get monthly sales trend."""
        success, monthly_data, msg = self.state.analyzer.get_monthly_sales()

        return {
            "success": success,
            "result": msg,
            "data": monthly_data if success else {},
            "type": "monthly_sales"
        }

    def _handle_general_query(self, question: str) -> Dict[str, Any]:
        """Handle general queries."""
        return {
            "success": False,
            "error": f"Could not understand question: {question}",
            "suggestion": "Try asking about: total revenue, profit, top products, revenue by region, monthly sales, etc."
        }

    def get_data_info(self) -> Dict[str, Any]:
        """Get current data information."""
        if self.state.df is None:
            return {"error": "No data loaded"}

        return {
            "rows": len(self.state.df),
            "columns": len(self.state.df.columns),
            "column_names": self.state.df.columns.tolist(),
            "schema_map": self.state.schema_map,
            "available_fields": self.matcher.get_available_fields()
        }


# LangChain tool definitions for integration with other agents
def get_data_schema(agent: DataAgent) -> str:
    """
    Analyze uploaded business data and answer questions about it.

    Args:
        question: Natural language question about the data
        agent: DataAgent instance with loaded data

    Returns:
        Analysis result as JSON string
    """
    result = agent.process_question(question)
    return json.dumps(result, indent=2, default=str)


def analyze_business_data(question: str, agent: DataAgent) -> str:
    """
    Get the detected schema and available fields in the data.

    Args:
        agent: DataAgent instance

    Returns:
        Schema information as JSON string
    """
    info = agent.get_data_info()
    return json.dumps(info, indent=2, default=str)
