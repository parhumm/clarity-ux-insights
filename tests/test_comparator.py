#!/usr/bin/env python3
"""Tests for period comparator."""

import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.comparator import PeriodComparator
from scripts.query_engine import DateRange


def test_comparator_initialization():
    """Test that comparator initializes correctly."""
    print("\n🧪 Testing comparator initialization...")

    comparator = PeriodComparator()

    assert comparator.query_engine is not None, "Query engine not initialized"

    print("  ✓ Comparator initialized")
    print("  ✓ Query engine available")


def test_aggregate_period():
    """Test period aggregation."""
    print("\n🧪 Testing period aggregation...")

    comparator = PeriodComparator()

    # Sample metrics
    metrics = [
        {'sessions': 100, 'users': 50, 'dead_clicks': 5, 'rage_clicks': 2},
        {'sessions': 150, 'users': 75, 'dead_clicks': 8, 'rage_clicks': 3},
    ]

    result = comparator._aggregate_period(metrics)

    assert result['sessions'] == 250, "Sessions not aggregated correctly"
    assert result['users'] == 125, "Users not aggregated correctly"
    assert result['dead_clicks'] == 13, "Dead clicks not aggregated"
    assert result['dead_clicks_rate'] == 13/250, "Dead clicks rate incorrect"

    print(f"  ✓ Aggregated sessions: {result['sessions']}")
    print(f"  ✓ Aggregated users: {result['users']}")
    print(f"  ✓ Calculated rates correctly")


def test_calculate_changes():
    """Test change calculation."""
    print("\n🧪 Testing change calculation...")

    comparator = PeriodComparator()

    current = {'sessions': 150, 'dead_clicks': 5}
    previous = {'sessions': 100, 'dead_clicks': 10}

    result = comparator._calculate_changes(current, previous)

    assert 'changes' in result, "Changes not calculated"
    assert 'improvements' in result, "Improvements not identified"
    assert 'regressions' in result, "Regressions not identified"

    # Check sessions change
    sessions_change = result['changes']['sessions']
    assert sessions_change['absolute_change'] == 50, "Absolute change incorrect"
    assert sessions_change['percent_change'] == 50.0, "Percent change incorrect"
    assert sessions_change['direction'] == 'up', "Direction incorrect"

    # Check dead clicks change (decrease is improvement)
    dead_clicks_change = result['changes']['dead_clicks']
    assert dead_clicks_change['absolute_change'] == -5, "Dead clicks change incorrect"
    assert dead_clicks_change['direction'] == 'down', "Dead clicks direction incorrect"

    print(f"  ✓ Sessions change: +{sessions_change['percent_change']}%")
    print(f"  ✓ Dead clicks change: {dead_clicks_change['percent_change']:.1f}%")
    print(f"  ✓ Improvements identified: {len(result['improvements'])}")
    print(f"  ✓ Regressions identified: {len(result['regressions'])}")


def test_improvement_detection():
    """Test improvement detection logic."""
    print("\n🧪 Testing improvement detection...")

    comparator = PeriodComparator()

    # Positive changes that are good
    assert comparator._is_improvement('sessions', 10), "Sessions increase should be improvement"
    assert comparator._is_improvement('users', 5), "Users increase should be improvement"

    # Negative changes that are good (frustration signals)
    assert comparator._is_improvement('dead_clicks', -5), "Dead clicks decrease should be improvement"
    assert comparator._is_improvement('rage_clicks', -2), "Rage clicks decrease should be improvement"

    # Not improvements
    assert not comparator._is_improvement('sessions', -10), "Sessions decrease not improvement"
    assert not comparator._is_improvement('dead_clicks', 5), "Dead clicks increase not improvement"

    print("  ✓ Traffic increase detected as improvement")
    print("  ✓ Frustration decrease detected as improvement")
    print("  ✓ Negative changes correctly classified")


def test_regression_detection():
    """Test regression detection logic."""
    print("\n🧪 Testing regression detection...")

    comparator = PeriodComparator()

    # Negative changes that are bad
    assert comparator._is_regression('sessions', -10), "Sessions decrease should be regression"
    assert comparator._is_regression('users', -5), "Users decrease should be regression"

    # Positive changes that are bad (frustration signals)
    assert comparator._is_regression('dead_clicks', 5), "Dead clicks increase should be regression"
    assert comparator._is_regression('rage_clicks', 2), "Rage clicks increase should be regression"

    # Not regressions
    assert not comparator._is_regression('sessions', 10), "Sessions increase not regression"
    assert not comparator._is_regression('dead_clicks', -5), "Dead clicks decrease not regression"

    print("  ✓ Traffic decrease detected as regression")
    print("  ✓ Frustration increase detected as regression")
    print("  ✓ Positive changes correctly classified")


def test_compare_periods():
    """Test comparing two periods."""
    print("\n🧪 Testing period comparison...")

    comparator = PeriodComparator()

    # Get real data from database
    end_date = date.today()
    start_date = end_date - timedelta(days=2)
    period1 = DateRange(start_date, end_date)

    start_date2 = start_date - timedelta(days=3)
    end_date2 = start_date - timedelta(days=1)
    period2 = DateRange(start_date2, end_date2)

    comparison = comparator.compare_periods(period1, period2)

    assert 'period1' in comparison, "Period 1 info missing"
    assert 'period2' in comparison, "Period 2 info missing"
    assert 'current' in comparison, "Current metrics missing"
    assert 'previous' in comparison, "Previous metrics missing"
    assert 'changes' in comparison, "Changes missing"
    assert 'improvements' in comparison, "Improvements missing"
    assert 'regressions' in comparison, "Regressions missing"

    print("  ✓ Comparison structure correct")
    print(f"  ✓ Period 1: {comparison['period1']['days']} days")
    print(f"  ✓ Period 2: {comparison['period2']['days']} days")
    print(f"  ✓ Changes calculated: {len(comparison['changes'])} metrics")
    print(f"  ✓ Improvements: {len(comparison['improvements'])}")
    print(f"  ✓ Regressions: {len(comparison['regressions'])}")


def test_compare_to_previous():
    """Test auto-comparison to previous period."""
    print("\n🧪 Testing auto-comparison to previous period...")

    comparator = PeriodComparator()

    # Current period: last 3 days
    end_date = date.today()
    start_date = end_date - timedelta(days=2)
    current_period = DateRange(start_date, end_date)

    comparison = comparator.compare_to_previous(current_period)

    # Previous period should be 3 days immediately before
    prev_period = comparison['period2']
    assert prev_period['days'] == 3, "Previous period should be same length"

    # Check that period2 ends day before period1 starts
    period1_start = date.fromisoformat(comparison['period1']['start'])
    period2_end = date.fromisoformat(comparison['period2']['end'])
    assert (period1_start - period2_end).days == 1, "Periods should be adjacent"

    print(f"  ✓ Current period: {comparison['period1']['start']} to {comparison['period1']['end']}")
    print(f"  ✓ Previous period: {comparison['period2']['start']} to {comparison['period2']['end']}")
    print(f"  ✓ Both periods same length: {prev_period['days']} days")
    print("  ✓ Periods are adjacent")


def test_format_comparison():
    """Test comparison formatting."""
    print("\n🧪 Testing comparison formatting...")

    comparator = PeriodComparator()

    # Get real comparison
    end_date = date.today()
    start_date = end_date - timedelta(days=2)
    period1 = DateRange(start_date, end_date)

    comparison = comparator.compare_to_previous(period1)
    formatted = comparator.format_comparison(comparison)

    assert 'PERIOD COMPARISON' in formatted, "Header missing"
    assert 'KEY METRICS' in formatted, "Key metrics section missing"
    assert 'SUMMARY' in formatted, "Summary section missing"
    assert 'Period 1:' in formatted, "Period 1 info missing"
    assert 'Period 2:' in formatted, "Period 2 info missing"

    print("  ✓ Header included")
    print("  ✓ Period info included")
    print("  ✓ Key metrics section included")
    print("  ✓ Summary section included")
    print(f"  ✓ Output length: {len(formatted)} characters")


def run_all_tests():
    """Run all comparator tests."""
    print("=" * 60)
    print("PERIOD COMPARATOR TESTS")
    print("=" * 60)

    tests = [
        test_comparator_initialization,
        test_aggregate_period,
        test_calculate_changes,
        test_improvement_detection,
        test_regression_detection,
        test_compare_periods,
        test_compare_to_previous,
        test_format_comparison,
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
