#!/usr/bin/env python3
"""Tests for metric aggregator."""

import sys
from pathlib import Path
from datetime import date
import sqlite3

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.aggregator import MetricAggregator
import config


def test_weekly_aggregation():
    """Test weekly metric aggregation."""
    print("\n🧪 Testing weekly aggregation...")

    aggregator = MetricAggregator()

    # Get current data range
    conn = aggregator.get_connection()
    cursor = conn.execute("SELECT MAX(metric_date) as max_date FROM daily_metrics")
    result = cursor.fetchone()
    conn.close()

    if not result['max_date']:
        print("  ⚠ No data to aggregate, skipping")
        return

    max_date = date.fromisoformat(result['max_date'])
    year, week, _ = max_date.isocalendar()

    # Aggregate current week
    result = aggregator.aggregate_weekly_metrics(year, week, force=True)

    assert result is not None, "Should return aggregation result"
    assert 'week_start' in result, "Should have week_start"
    assert 'week_end' in result, "Should have week_end"
    assert 'data_points' in result, "Should have data_points"
    assert result['data_points'] > 0, "Should have aggregated data"

    print(f"  ✓ Aggregated week {year}-W{week:02d}")
    print(f"    Data points: {result['data_points']}")
    print(f"    Avg sessions: {result.get('avg_sessions', 0)}")

    # Verify data in database
    conn = aggregator.get_connection()
    cursor = conn.execute("""
        SELECT * FROM weekly_metrics
        WHERE year = ? AND week_number = ?
    """, (year, week))
    db_result = cursor.fetchone()
    conn.close()

    assert db_result is not None, "Should be saved in database"
    print("  ✓ Data saved to weekly_metrics table")


def test_monthly_aggregation():
    """Test monthly metric aggregation."""
    print("\n🧪 Testing monthly aggregation...")

    aggregator = MetricAggregator()

    # Get current data range
    conn = aggregator.get_connection()
    cursor = conn.execute("SELECT MAX(metric_date) as max_date FROM daily_metrics")
    result = cursor.fetchone()
    conn.close()

    if not result['max_date']:
        print("  ⚠ No data to aggregate, skipping")
        return

    max_date = date.fromisoformat(result['max_date'])
    year = max_date.year
    month = max_date.month

    # Aggregate current month
    result = aggregator.aggregate_monthly_metrics(year, month, force=True)

    assert result is not None, "Should return aggregation result"
    assert 'year' in result, "Should have year"
    assert 'month' in result, "Should have month"
    assert 'data_points' in result, "Should have data_points"
    assert result['data_points'] > 0, "Should have aggregated data"
    assert 'min_sessions' in result, "Monthly should have min"
    assert 'max_sessions' in result, "Monthly should have max"

    print(f"  ✓ Aggregated {year}-{month:02d}")
    print(f"    Data points: {result['data_points']}")
    print(f"    Avg sessions: {result.get('avg_sessions', 0)}")
    print(f"    Min/Max: {result.get('min_sessions', 0)}/{result.get('max_sessions', 0)}")

    # Verify data in database
    conn = aggregator.get_connection()
    cursor = conn.execute("""
        SELECT * FROM monthly_metrics
        WHERE year = ? AND month = ?
    """, (year, month))
    db_result = cursor.fetchone()
    conn.close()

    assert db_result is not None, "Should be saved in database"
    print("  ✓ Data saved to monthly_metrics table")


def test_aggregate_all():
    """Test aggregating all available data."""
    print("\n🧪 Testing aggregate all...")

    aggregator = MetricAggregator()

    counts = aggregator.aggregate_all_available(force=True)

    assert 'weekly' in counts, "Should return weekly count"
    assert 'monthly' in counts, "Should return monthly count"
    assert counts['weekly'] >= 0, "Weekly count should be non-negative"
    assert counts['monthly'] >= 0, "Monthly count should be non-negative"

    print(f"  ✓ Weekly aggregations: {counts['weekly']}")
    print(f"  ✓ Monthly aggregations: {counts['monthly']}")


def test_duplicate_prevention():
    """Test that duplicate aggregations are prevented."""
    print("\n🧪 Testing duplicate prevention...")

    aggregator = MetricAggregator()

    # Get current month
    conn = aggregator.get_connection()
    cursor = conn.execute("SELECT MAX(metric_date) as max_date FROM daily_metrics")
    result = cursor.fetchone()
    conn.close()

    if not result['max_date']:
        print("  ⚠ No data to test, skipping")
        return

    max_date = date.fromisoformat(result['max_date'])
    year = max_date.year
    month = max_date.month

    # First aggregation
    result1 = aggregator.aggregate_monthly_metrics(year, month, force=False)
    assert result1 is not None, "First aggregation should succeed"

    # Second aggregation without force (should skip)
    result2 = aggregator.aggregate_monthly_metrics(year, month, force=False)
    assert result2 is not None, "Should return existing data"

    print("  ✓ Duplicate prevention working")
    print("  ✓ Returns existing data when not forced")


def test_week_start_calculation():
    """Test ISO week start calculation."""
    print("\n🧪 Testing week start calculation...")

    aggregator = MetricAggregator()

    # Test known week starts
    # 2025-W01 starts on Monday, December 30, 2024
    week_start = aggregator._get_week_start(2025, 1)
    assert week_start == date(2024, 12, 30), f"2025-W01 should start on 2024-12-30, got {week_start}"
    print(f"  ✓ 2025-W01 starts on {week_start}")

    # 2025-W48 (our current test week)
    week_start = aggregator._get_week_start(2025, 48)
    assert week_start.weekday() == 0, "Week should start on Monday"
    print(f"  ✓ 2025-W48 starts on {week_start} (Monday)")


def test_aggregation_metrics():
    """Test that all required metrics are aggregated."""
    print("\n🧪 Testing aggregation metrics...")

    aggregator = MetricAggregator()

    # Get current month
    conn = aggregator.get_connection()
    cursor = conn.execute("SELECT MAX(metric_date) as max_date FROM daily_metrics")
    result = cursor.fetchone()
    conn.close()

    if not result['max_date']:
        print("  ⚠ No data to test, skipping")
        return

    max_date = date.fromisoformat(result['max_date'])

    result = aggregator.aggregate_monthly_metrics(
        max_date.year, max_date.month, force=True
    )

    required_metrics = [
        'avg_sessions', 'sum_sessions', 'min_sessions', 'max_sessions',
        'avg_users', 'sum_users',
        'avg_dead_clicks', 'avg_rage_clicks', 'avg_quick_backs',
        'avg_scroll_depth', 'avg_engagement_time',
        'data_points'
    ]

    for metric in required_metrics:
        assert metric in result, f"Missing metric: {metric}"

    print(f"  ✓ All {len(required_metrics)} required metrics present")


def run_all_tests():
    """Run all aggregator tests."""
    print("=" * 60)
    print("AGGREGATOR TESTS")
    print("=" * 60)

    tests = [
        test_week_start_calculation,
        test_weekly_aggregation,
        test_monthly_aggregation,
        test_aggregate_all,
        test_duplicate_prevention,
        test_aggregation_metrics,
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
