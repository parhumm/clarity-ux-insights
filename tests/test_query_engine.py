#!/usr/bin/env python3
"""Tests for query engine and date parser."""

import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.query_engine import DateParser, QueryEngine, DateRange


def test_numeric_dates():
    """Test numeric date expressions."""
    print("\n🧪 Testing numeric date expressions...")

    ref_date = date(2025, 11, 25)

    tests = [
        ("3", 3, "Last 3 days"),
        ("7", 7, "Last 7 days"),
        ("30", 30, "Last 30 days"),
        ("7d", 7, "Last 7 days"),
        ("7days", 7, "Last 7 days"),
        ("2weeks", 14, "Last 14 days"),
        ("1month", 30, "Last 30 days"),
    ]

    for expr, expected_days, desc in tests:
        range_obj = DateParser.parse(expr, ref_date)
        assert range_obj.days == expected_days, f"{expr}: expected {expected_days} days, got {range_obj.days}"
        assert range_obj.end == ref_date, f"{expr}: end date should be reference date"
        print(f"  ✓ '{expr}' → {range_obj.days} days ({range_obj.start} to {range_obj.end})")

    print("  ✓ All numeric tests passed")


def test_relative_dates():
    """Test relative date expressions."""
    print("\n🧪 Testing relative date expressions...")

    ref_date = date(2025, 11, 25)  # Tuesday

    tests = [
        ("today", ref_date, ref_date),
        ("yesterday", ref_date - timedelta(days=1), ref_date - timedelta(days=1)),
    ]

    for expr, expected_start, expected_end in tests:
        range_obj = DateParser.parse(expr, ref_date)
        assert range_obj.start == expected_start, f"{expr}: wrong start date"
        assert range_obj.end == expected_end, f"{expr}: wrong end date"
        print(f"  ✓ '{expr}' → {range_obj}")

    print("  ✓ All relative tests passed")


def test_month_dates():
    """Test month date expressions."""
    print("\n🧪 Testing month date expressions...")

    ref_date = date(2025, 11, 25)

    tests = [
        ("2025-11", date(2025, 11, 1), date(2025, 11, 30)),
        ("2025-01", date(2025, 1, 1), date(2025, 1, 31)),
        ("2025-12", date(2025, 12, 1), date(2025, 12, 31)),
        ("November", date(2025, 11, 1), date(2025, 11, 30)),
        ("Nov 2024", date(2024, 11, 1), date(2024, 11, 30)),
        ("January 2025", date(2025, 1, 1), date(2025, 1, 31)),
    ]

    for expr, expected_start, expected_end in tests:
        range_obj = DateParser.parse(expr, ref_date)
        assert range_obj.start == expected_start, f"{expr}: wrong start date - expected {expected_start}, got {range_obj.start}"
        assert range_obj.end == expected_end, f"{expr}: wrong end date - expected {expected_end}, got {range_obj.end}"
        print(f"  ✓ '{expr}' → {range_obj}")

    print("  ✓ All month tests passed")


def test_quarter_dates():
    """Test quarter date expressions."""
    print("\n🧪 Testing quarter date expressions...")

    ref_date = date(2025, 11, 25)

    tests = [
        ("2025-Q1", date(2025, 1, 1), date(2025, 3, 31)),
        ("2025-Q2", date(2025, 4, 1), date(2025, 6, 30)),
        ("2025-Q3", date(2025, 7, 1), date(2025, 9, 30)),
        ("2025-Q4", date(2025, 10, 1), date(2025, 12, 31)),
        ("Q4 2025", date(2025, 10, 1), date(2025, 12, 31)),
        ("2024Q1", date(2024, 1, 1), date(2024, 3, 31)),
    ]

    for expr, expected_start, expected_end in tests:
        range_obj = DateParser.parse(expr, ref_date)
        assert range_obj.start == expected_start, f"{expr}: wrong start date"
        assert range_obj.end == expected_end, f"{expr}: wrong end date"
        print(f"  ✓ '{expr}' → {range_obj}")

    print("  ✓ All quarter tests passed")


def test_year_dates():
    """Test year date expressions."""
    print("\n🧪 Testing year date expressions...")

    ref_date = date(2025, 11, 25)

    tests = [
        ("2025", date(2025, 1, 1), date(2025, 12, 31)),
        ("2024", date(2024, 1, 1), date(2024, 12, 31)),
    ]

    for expr, expected_start, expected_end in tests:
        range_obj = DateParser.parse(expr, ref_date)
        assert range_obj.start == expected_start, f"{expr}: wrong start date"
        assert range_obj.end == expected_end, f"{expr}: wrong end date"
        print(f"  ✓ '{expr}' → {range_obj}")

    print("  ✓ All year tests passed")


def test_custom_range():
    """Test custom range expressions."""
    print("\n🧪 Testing custom range expressions...")

    ref_date = date(2025, 11, 25)

    tests = [
        ("2025-11-01 to 2025-11-30", date(2025, 11, 1), date(2025, 11, 30)),
        ("2025-01-01 to 2025-12-31", date(2025, 1, 1), date(2025, 12, 31)),
        ("2025-11-01:2025-11-15", date(2025, 11, 1), date(2025, 11, 15)),
    ]

    for expr, expected_start, expected_end in tests:
        range_obj = DateParser.parse(expr, ref_date)
        assert range_obj.start == expected_start, f"{expr}: wrong start date"
        assert range_obj.end == expected_end, f"{expr}: wrong end date"
        print(f"  ✓ '{expr}' → {range_obj}")

    print("  ✓ All custom range tests passed")


def test_query_engine():
    """Test query engine functionality."""
    print("\n🧪 Testing query engine...")

    engine = QueryEngine()

    # Test get available dates
    dates = engine.get_available_dates()
    print(f"  ✓ Found {len(dates)} dates with data")
    if dates:
        print(f"    Latest: {dates[0]}, Earliest: {dates[-1]}")

    # Test query metrics
    if dates:
        metrics = engine.query_metrics("7", data_scope='general')
        print(f"  ✓ Query last 7 days: {len(metrics)} records")

        # Test with metric filter
        traffic_metrics = engine.query_metrics("7", metric_name="Traffic")
        print(f"  ✓ Query Traffic metrics: {len(traffic_metrics)} records")

    # Test aggregate metrics
    if dates:
        try:
            agg = engine.aggregate_metrics("7", metric_name="Traffic")
            print(f"  ✓ Aggregate metrics:")
            print(f"    Data points: {agg['data_points']}")
            print(f"    Avg sessions: {agg['avg_sessions']}")
        except Exception as e:
            print(f"  ⚠ Aggregate failed (may not have Traffic data): {e}")

    print("  ✓ Query engine tests passed")


def test_date_range_object():
    """Test DateRange object."""
    print("\n🧪 Testing DateRange object...")

    start = date(2025, 11, 1)
    end = date(2025, 11, 30)
    range_obj = DateRange(start, end, "November 2025")

    assert range_obj.days == 30, "Should be 30 days"
    assert str(range_obj) == "November 2025 (2025-11-01 to 2025-11-30)"

    print(f"  ✓ DateRange object: {range_obj}")
    print(f"  ✓ Days: {range_obj.days}")


def run_all_tests():
    """Run all query engine tests."""
    print("=" * 60)
    print("QUERY ENGINE & DATE PARSER TESTS")
    print("=" * 60)

    tests = [
        test_date_range_object,
        test_numeric_dates,
        test_relative_dates,
        test_month_dates,
        test_quarter_dates,
        test_year_dates,
        test_custom_range,
        test_query_engine,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
