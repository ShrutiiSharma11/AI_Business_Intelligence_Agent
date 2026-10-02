"""
Test and validation script for business calculations.
Verifies that calculations are correct and data is not hallucinated.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from utils.data_loader import DataLoader
from utils.schema_mapper import SchemaMatcher
from agents.data_agent import DataAgent


def test_revenue_calculation():
    """Test total revenue calculation."""
    print("\n" + "="*60)
    print("TEST: Total Revenue Calculation")
    print("="*60)

    # Create test data
    df = pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Product': ['A', 'B', 'A'],
        'Revenue': [100, 200, 150]
    })

    agent = DataAgent()
    agent.load_data(df)

    result = agent.process_question("What is the total revenue?")

    print(f"Result: {result}")
    expected_revenue = 450
    actual_revenue = result.get("value")

    if actual_revenue == expected_revenue:
        print(f"✅ PASS: Revenue calculation correct ({actual_revenue})")
        return True
    else:
        print(f"❌ FAIL: Expected {expected_revenue}, got {actual_revenue}")
        return False


def test_profit_calculation():
    """Test profit calculation."""
    print("\n" + "="*60)
    print("TEST: Profit Calculation")
    print("="*60)

    # Create test data
    df = pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Sales': [1000, 2000, 1500],
        'Cost': [400, 800, 600]
    })

    agent = DataAgent()
    agent.load_data(df)

    result = agent.process_question("What is the total profit?")

    print(f"Result: {result}")
    expected_profit = (1000 + 2000 + 1500) - (400 + 800 + 600)
    actual_profit = result.get("value")

    if actual_profit == expected_profit:
        print(f"✅ PASS: Profit calculation correct ({actual_profit})")
        return True
    else:
        print(f"❌ FAIL: Expected {expected_profit}, got {actual_profit}")
        return False


def test_profit_margin_calculation():
    """Test profit margin calculation."""
    print("\n" + "="*60)
    print("TEST: Profit Margin Calculation")
    print("="*60)

    # Create test data
    df = pd.DataFrame({
        'Revenue': [1000, 2000],
        'Cost': [600, 1200]
    })

    agent = DataAgent()
    agent.load_data(df)

    result = agent.process_question("What is the profit margin?")

    print(f"Result: {result}")
    total_revenue = 3000
    total_profit = 1200
    expected_margin = (total_profit / total_revenue) * 100

    actual_margin = result.get("value")

    if actual_margin and abs(actual_margin - expected_margin) < 0.1:
        print(f"✅ PASS: Profit margin correct ({actual_margin:.2f}%)")
        return True
    else:
        print(f"❌ FAIL: Expected {expected_margin:.2f}%, got {actual_margin}")
        return False


def test_schema_mapping():
    """Test schema mapping for different column names."""
    print("\n" + "="*60)
    print("TEST: Schema Mapping")
    print("="*60)

    # Test different column name variations
    test_columns = [
        ['sales', 'expenses', 'transaction_date'],
        ['Revenue', 'Cost', 'OrderDate'],
        ['Sales_Amount', 'COGS', 'created_at'],
    ]

    matcher = SchemaMatcher()
    all_passed = True

    for columns in test_columns:
        schema = matcher.detect_schema(columns)
        print(f"Columns: {columns}")
        print(f"Detected: {schema}")

        # Check if key fields were detected
        has_revenue = any(v == "revenue" for v in schema.values())
        has_cost = any(v == "cost" for v in schema.values())
        has_date = any(v == "date" for v in schema.values())

        if has_revenue and has_cost and has_date:
            print("✅ Correctly mapped all fields")
        else:
            print("❌ Failed to map some fields")
            all_passed = False

        print()

    return all_passed


def test_missing_column_handling():
    """Test handling of missing required columns."""
    print("\n" + "="*60)
    print("TEST: Missing Column Handling")
    print("="*60)

    # Create data without revenue column
    df = pd.DataFrame({
        'Product': ['A', 'B'],
        'Quantity': [10, 20]
    })

    agent = DataAgent()
    agent.load_data(df)

    result = agent.process_question("What is the total revenue?")

    print(f"Result: {result}")

    if not result.get("success") and "not found" in str(result.get("error", "")):
        print("✅ PASS: Correctly handled missing column")
        return True
    else:
        print("❌ FAIL: Should have reported missing column")
        return False


def test_empty_data_handling():
    """Test handling of empty datasets."""
    print("\n" + "="*60)
    print("TEST: Empty Data Handling")
    print("="*60)

    # Create empty DataFrame
    df = pd.DataFrame({
        'Revenue': [],
        'Cost': []
    })

    agent = DataAgent()
    result = agent.load_data(df)

    print(f"Load result: {result}")

    # Should still load but with 0 rows
    if result.get("success") and result.get("summary", {}).get("rows") == 0:
        print("✅ PASS: Correctly handled empty data")
        return True
    else:
        print("❌ FAIL: Should handle empty data")
        return False


def test_top_products():
    """Test top products calculation."""
    print("\n" + "="*60)
    print("TEST: Top Products Calculation")
    print("="*60)

    df = pd.DataFrame({
        'Product': ['A', 'B', 'C', 'A', 'B'],
        'Sales': [100, 500, 200, 150, 300]
    })

    agent = DataAgent()
    agent.load_data(df)

    result = agent.process_question("What are the top 2 products?")

    print(f"Result: {result}")

    if result.get("success"):
        data = result.get("data", [])
        if len(data) >= 2:
            # Should be B (800) and A (250) and C (200)
            print("✅ PASS: Top products identified")
            return True

    print("❌ FAIL: Top products calculation failed")
    return False


def run_all_tests():
    """Run all validation tests."""
    print("\n" + "="*80)
    print("AI BUSINESS INTELLIGENCE AGENT - VALIDATION TEST SUITE")
    print("="*80)

    tests = [
        ("Revenue Calculation", test_revenue_calculation),
        ("Profit Calculation", test_profit_calculation),
        ("Profit Margin", test_profit_margin_calculation),
        ("Schema Mapping", test_schema_mapping),
        ("Missing Columns", test_missing_column_handling),
        ("Empty Data", test_empty_data_handling),
        ("Top Products", test_top_products),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {str(e)}")
            results[test_name] = False

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
