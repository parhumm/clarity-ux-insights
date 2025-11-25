#!/usr/bin/env python3
"""Tests for trend analyzer."""

import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.trend_analyzer import TrendAnalyzer
from scripts.query_engine import DateRange


def test_trend_analyzer_initialization():
    """Test that trend analyzer initializes correctly."""
    print("\n🧪 Testing trend analyzer initialization...")

    analyzer = TrendAnalyzer()

    assert analyzer.query_engine is not None, "Query engine not initialized"

    print("  ✓ Trend analyzer initialized")
    print("  ✓ Query engine available")


def test_analyze_overall():
    """Test overall metrics analysis."""
    print("\n🧪 Testing overall metrics analysis...")

    analyzer = TrendAnalyzer()

    metrics = [
        {'sessions': 100, 'users': 50, 'dead_clicks': 5, 'rage_clicks': 2, 'quick_backs': 3},
        {'sessions': 150, 'users': 75, 'dead_clicks': 8, 'rage_clicks': 3, 'quick_backs': 4},
        {'sessions': 120, 'users': 60, 'dead_clicks': 6, 'rage_clicks': 2, 'quick_backs': 2},
    ]

    overall = analyzer._analyze_overall(metrics)

    assert overall['sessions']['total'] == 370, "Total sessions incorrect"
    assert overall['sessions']['average_per_day'] == 370/3, "Average sessions incorrect"
    assert overall['sessions']['max'] == 150, "Max sessions incorrect"
    assert overall['sessions']['min'] == 100, "Min sessions incorrect"
    assert overall['frustration']['total'] == 35, "Total frustration incorrect"

    print(f"  ✓ Total sessions: {overall['sessions']['total']}")
    print(f"  ✓ Average per day: {overall['sessions']['average_per_day']:.1f}")
    print(f"  ✓ Max/Min: {overall['sessions']['max']}/{overall['sessions']['min']}")
    print(f"  ✓ Total frustration: {overall['frustration']['total']}")


def test_analyze_growth():
    """Test growth rate analysis."""
    print("\n🧪 Testing growth analysis...")

    analyzer = TrendAnalyzer()

    # Growing trend
    metrics = [
        {'sessions': 100},
        {'sessions': 110},
        {'sessions': 121},
        {'sessions': 133},
    ]

    growth = analyzer._analyze_growth(metrics)

    assert growth['first_period_sessions'] == 100, "First period incorrect"
    assert growth['last_period_sessions'] == 133, "Last period incorrect"
    assert growth['absolute_change'] == 33, "Absolute change incorrect"
    assert growth['total_growth'] == 33.0, "Growth rate incorrect"

    print(f"  ✓ Total growth: {growth['total_growth']:.1f}%")
    print(f"  ✓ Absolute change: {growth['absolute_change']:+}")
    print(f"  ✓ Avg daily growth: {growth['avg_daily_growth']:.2f}%")


def test_analyze_volatility():
    """Test volatility analysis."""
    print("\n🧪 Testing volatility analysis...")

    analyzer = TrendAnalyzer()

    # Stable data
    stable_metrics = [
        {'sessions': 100},
        {'sessions': 102},
        {'sessions': 98},
        {'sessions': 101},
        {'sessions': 99},
    ]

    vol = analyzer._analyze_volatility(stable_metrics)

    assert 'mean' in vol, "Mean not calculated"
    assert 'std_dev' in vol, "Std dev not calculated"
    assert 'coefficient_of_variation' in vol, "CV not calculated"
    assert vol['stability'] in ['high', 'medium', 'low'], "Stability classification missing"

    print(f"  ✓ Mean: {vol['mean']:.1f}")
    print(f"  ✓ Std Dev: {vol['std_dev']:.1f}")
    print(f"  ✓ CV: {vol['coefficient_of_variation']:.1f}%")
    print(f"  ✓ Stability: {vol['stability'].upper()}")


def test_identify_trends():
    """Test trend identification."""
    print("\n🧪 Testing trend identification...")

    analyzer = TrendAnalyzer()

    # Increasing trend
    increasing_metrics = [
        {'sessions': 100},
        {'sessions': 110},
        {'sessions': 120},
        {'sessions': 130},
        {'sessions': 140},
    ]

    trends = analyzer._identify_trends(increasing_metrics)

    assert trends['direction'] == 'increasing', "Should detect increasing trend"
    assert trends['slope'] > 0, "Slope should be positive"
    assert 'r_squared' in trends, "R-squared not calculated"
    assert 'strength' in trends, "Trend strength not classified"

    print(f"  ✓ Direction: {trends['direction'].upper()}")
    print(f"  ✓ Slope: {trends['slope']:+.2f}")
    print(f"  ✓ R-squared: {trends['r_squared']:.3f}")
    print(f"  ✓ Strength: {trends['strength'].upper()}")


def test_identify_patterns():
    """Test pattern identification."""
    print("\n🧪 Testing pattern identification...")

    analyzer = TrendAnalyzer()

    # Weekly pattern (peaks every 7 days)
    weekly_metrics = [
        {'sessions': 100},  # Valley
        {'sessions': 120},
        {'sessions': 140},  # Peak day 2
        {'sessions': 120},
        {'sessions': 100},  # Valley
        {'sessions': 120},
        {'sessions': 140},  # Peak day 6 (should be ~7 days from first)
        {'sessions': 120},
        {'sessions': 100},  # Valley
        {'sessions': 120},
        {'sessions': 140},  # Peak day 10
    ]

    patterns = analyzer._identify_patterns(weekly_metrics)

    assert 'peaks_count' in patterns, "Peaks not counted"
    assert 'valleys_count' in patterns, "Valleys not counted"
    assert 'weekly_pattern_detected' in patterns, "Weekly pattern check missing"

    print(f"  ✓ Peaks detected: {patterns['peaks_count']}")
    print(f"  ✓ Valleys detected: {patterns['valleys_count']}")
    if patterns.get('avg_peak_distance'):
        print(f"  ✓ Average peak distance: {patterns['avg_peak_distance']:.1f} days")
    if patterns['weekly_pattern_detected']:
        print("  ✓ Weekly pattern detected")


def test_analyze_trend_full():
    """Test full trend analysis."""
    print("\n🧪 Testing full trend analysis...")

    analyzer = TrendAnalyzer()

    # Get real data from database
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    date_range = DateRange(start_date, end_date)

    analysis = analyzer.analyze_trend(date_range)

    if 'error' not in analysis:
        assert 'period' in analysis, "Period info missing"
        assert 'overall' in analysis, "Overall metrics missing"
        assert 'growth' in analysis, "Growth analysis missing"
        assert 'volatility' in analysis, "Volatility analysis missing"
        assert 'trends' in analysis, "Trend analysis missing"
        assert 'patterns' in analysis, "Pattern analysis missing"

        print(f"  ✓ Period: {analysis['period']['days']} days")
        print(f"  ✓ Data points: {analysis['period']['data_points']}")
        print("  ✓ Overall metrics calculated")
        print("  ✓ Growth analysis completed")
        print("  ✓ Volatility calculated")
        print("  ✓ Trends identified")
        print("  ✓ Patterns analyzed")
    else:
        print(f"  ⚠ No data available: {analysis['error']}")


def test_format_analysis():
    """Test analysis formatting."""
    print("\n🧪 Testing analysis formatting...")

    analyzer = TrendAnalyzer()

    # Get real data
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    date_range = DateRange(start_date, end_date)

    analysis = analyzer.analyze_trend(date_range)
    formatted = analyzer.format_analysis(analysis)

    assert 'LONG-TERM TREND ANALYSIS' in formatted, "Header missing"
    assert 'Period:' in formatted, "Period info missing"

    if 'error' not in analysis:
        assert 'OVERALL METRICS' in formatted, "Overall section missing"
        assert 'Sessions:' in formatted, "Sessions info missing"

    print("  ✓ Header included")
    print("  ✓ Period info included")
    print(f"  ✓ Output length: {len(formatted)} characters")


def run_all_tests():
    """Run all trend analyzer tests."""
    print("=" * 60)
    print("TREND ANALYZER TESTS")
    print("=" * 60)

    tests = [
        test_trend_analyzer_initialization,
        test_analyze_overall,
        test_analyze_growth,
        test_analyze_volatility,
        test_identify_trends,
        test_identify_patterns,
        test_analyze_trend_full,
        test_format_analysis,
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
