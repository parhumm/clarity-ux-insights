#!/usr/bin/env python3
"""
Period comparison tool for UX metrics.
Compare metrics between two time periods to identify trends.
"""

import sys
from pathlib import Path
from datetime import date, timedelta
from typing import Dict, List, Optional, Any, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.query_engine import QueryEngine, DateRange, DateParser


class PeriodComparator:
    """Compare metrics between two time periods."""

    def __init__(self):
        """Initialize comparator."""
        self.query_engine = QueryEngine()

    def compare_periods(
        self,
        period1: DateRange,
        period2: DateRange,
        metric_name: Optional[str] = None,
        data_scope: str = "general"
    ) -> Dict[str, Any]:
        """
        Compare metrics between two periods.

        Args:
            period1: First period (usually "current" or "recent")
            period2: Second period (usually "previous" or "baseline")
            metric_name: Optional specific metric to compare
            data_scope: Data scope (general or page)

        Returns:
            Comparison results with changes and percentages
        """
        # Query both periods
        metrics1 = self.query_engine.query_metrics(
            period1,
            metric_name=metric_name,
            data_scope=data_scope
        )
        metrics2 = self.query_engine.query_metrics(
            period2,
            metric_name=metric_name,
            data_scope=data_scope
        )

        # Aggregate each period
        agg1 = self._aggregate_period(metrics1)
        agg2 = self._aggregate_period(metrics2)

        # Calculate changes
        comparison = self._calculate_changes(agg1, agg2)

        # Add period info
        comparison['period1'] = {
            'start': period1.start.isoformat(),
            'end': period1.end.isoformat(),
            'days': (period1.end - period1.start).days + 1
        }
        comparison['period2'] = {
            'start': period2.start.isoformat(),
            'end': period2.end.isoformat(),
            'days': (period2.end - period2.start).days + 1
        }

        return comparison

    def compare_to_previous(
        self,
        current_period: DateRange,
        metric_name: Optional[str] = None,
        data_scope: str = "general"
    ) -> Dict[str, Any]:
        """
        Compare current period to equivalent previous period.

        Args:
            current_period: Current time period
            metric_name: Optional specific metric
            data_scope: Data scope

        Returns:
            Comparison results
        """
        # Calculate previous period (same length, immediately before)
        period_length = (current_period.end - current_period.start).days + 1
        previous_end = current_period.start - timedelta(days=1)
        previous_start = previous_end - timedelta(days=period_length - 1)
        previous_period = DateRange(previous_start, previous_end)

        return self.compare_periods(
            current_period,
            previous_period,
            metric_name,
            data_scope
        )

    def _aggregate_period(self, metrics: List[Dict]) -> Dict[str, float]:
        """Aggregate metrics for a period."""
        if not metrics:
            return {}

        result = {}

        # Sum metrics
        total_sessions = sum(m.get('sessions') or 0 for m in metrics)
        result['sessions'] = total_sessions
        result['users'] = sum(m.get('users') or 0 for m in metrics)
        result['page_views'] = sum(m.get('page_views') or 0 for m in metrics)

        # Device breakdown
        result['mobile_sessions'] = sum(m.get('mobile_sessions') or 0 for m in metrics)
        result['desktop_sessions'] = sum(m.get('desktop_sessions') or 0 for m in metrics)
        result['tablet_sessions'] = sum(m.get('tablet_sessions') or 0 for m in metrics)

        # Frustration signals
        result['dead_clicks'] = sum(m.get('dead_clicks') or 0 for m in metrics)
        result['rage_clicks'] = sum(m.get('rage_clicks') or 0 for m in metrics)
        result['quick_backs'] = sum(m.get('quick_backs') or 0 for m in metrics)
        result['error_clicks'] = sum(m.get('error_clicks') or 0 for m in metrics)

        # Engagement (weighted averages)
        if total_sessions > 0:
            result['avg_scroll_depth'] = sum(
                (m.get('avg_scroll_depth') or 0) * (m.get('sessions') or 0)
                for m in metrics
            ) / total_sessions

            result['avg_time_on_page'] = sum(
                (m.get('avg_time_on_page') or 0) * (m.get('sessions') or 0)
                for m in metrics
            ) / total_sessions

            result['avg_active_time'] = sum(
                (m.get('avg_active_time') or 0) * (m.get('sessions') or 0)
                for m in metrics
            ) / total_sessions

            # Rates per session
            result['dead_clicks_rate'] = result['dead_clicks'] / total_sessions
            result['rage_clicks_rate'] = result['rage_clicks'] / total_sessions
            result['quick_backs_rate'] = result['quick_backs'] / total_sessions
            result['error_clicks_rate'] = result['error_clicks'] / total_sessions

        return result

    def _calculate_changes(
        self,
        current: Dict[str, float],
        previous: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate changes between periods."""
        comparison = {
            'current': current,
            'previous': previous,
            'changes': {},
            'improvements': [],
            'regressions': []
        }

        # Calculate changes for each metric
        for key in current.keys():
            if key not in previous:
                continue

            curr_val = current[key]
            prev_val = previous[key]

            if prev_val == 0:
                if curr_val == 0:
                    change_pct = 0
                else:
                    change_pct = 100  # Arbitrary for "new activity"
            else:
                change_pct = ((curr_val - prev_val) / prev_val) * 100

            change_abs = curr_val - prev_val

            comparison['changes'][key] = {
                'current': curr_val,
                'previous': prev_val,
                'absolute_change': change_abs,
                'percent_change': change_pct,
                'direction': 'up' if change_abs > 0 else 'down' if change_abs < 0 else 'flat'
            }

            # Classify as improvement or regression
            if self._is_improvement(key, change_abs):
                comparison['improvements'].append({
                    'metric': key,
                    'change_pct': change_pct,
                    'change_abs': change_abs
                })
            elif self._is_regression(key, change_abs):
                comparison['regressions'].append({
                    'metric': key,
                    'change_pct': change_pct,
                    'change_abs': change_abs
                })

        # Sort by impact
        comparison['improvements'].sort(key=lambda x: abs(x['change_pct']), reverse=True)
        comparison['regressions'].sort(key=lambda x: abs(x['change_pct']), reverse=True)

        return comparison

    def _is_improvement(self, metric: str, change: float) -> bool:
        """Determine if change is an improvement."""
        # Positive changes that are good
        good_increase = [
            'sessions', 'users', 'page_views',
            'avg_scroll_depth', 'avg_time_on_page', 'avg_active_time'
        ]

        # Negative changes that are good (frustration signals)
        good_decrease = [
            'dead_clicks', 'rage_clicks', 'quick_backs', 'error_clicks',
            'dead_clicks_rate', 'rage_clicks_rate', 'quick_backs_rate', 'error_clicks_rate'
        ]

        if metric in good_increase and change > 0:
            return True
        if metric in good_decrease and change < 0:
            return True

        return False

    def _is_regression(self, metric: str, change: float) -> bool:
        """Determine if change is a regression."""
        # Opposite of improvement
        good_increase = [
            'sessions', 'users', 'page_views',
            'avg_scroll_depth', 'avg_time_on_page', 'avg_active_time'
        ]

        good_decrease = [
            'dead_clicks', 'rage_clicks', 'quick_backs', 'error_clicks',
            'dead_clicks_rate', 'rage_clicks_rate', 'quick_backs_rate', 'error_clicks_rate'
        ]

        if metric in good_increase and change < 0:
            return True
        if metric in good_decrease and change > 0:
            return True

        return False

    def format_comparison(self, comparison: Dict[str, Any]) -> str:
        """Format comparison results as readable text."""
        lines = []

        # Header
        lines.append("=" * 60)
        lines.append("PERIOD COMPARISON")
        lines.append("=" * 60)

        # Period info
        p1 = comparison['period1']
        p2 = comparison['period2']
        lines.append(f"\nPeriod 1: {p1['start']} to {p1['end']} ({p1['days']} days)")
        lines.append(f"Period 2: {p2['start']} to {p2['end']} ({p2['days']} days)")

        # Key metrics
        lines.append("\n" + "=" * 60)
        lines.append("KEY METRICS")
        lines.append("=" * 60)

        key_metrics = ['sessions', 'users', 'page_views']
        for metric in key_metrics:
            if metric in comparison['changes']:
                change = comparison['changes'][metric]
                lines.append(
                    f"\n{metric.replace('_', ' ').title()}:"
                )
                lines.append(
                    f"  Current: {change['current']:,.0f} | "
                    f"Previous: {change['previous']:,.0f}"
                )
                lines.append(
                    f"  Change: {change['absolute_change']:+,.0f} ({change['percent_change']:+.1f}%) "
                    f"[{change['direction']}]"
                )

        # Improvements
        if comparison['improvements']:
            lines.append("\n" + "=" * 60)
            lines.append("IMPROVEMENTS")
            lines.append("=" * 60)

            for imp in comparison['improvements'][:5]:  # Top 5
                lines.append(
                    f"\n✓ {imp['metric'].replace('_', ' ').title()}: "
                    f"{imp['change_pct']:+.1f}% "
                    f"({imp['change_abs']:+,.2f})"
                )

        # Regressions
        if comparison['regressions']:
            lines.append("\n" + "=" * 60)
            lines.append("REGRESSIONS")
            lines.append("=" * 60)

            for reg in comparison['regressions'][:5]:  # Top 5
                lines.append(
                    f"\n✗ {reg['metric'].replace('_', ' ').title()}: "
                    f"{reg['change_pct']:+.1f}% "
                    f"({reg['change_abs']:+,.2f})"
                )

        # Summary
        lines.append("\n" + "=" * 60)
        lines.append("SUMMARY")
        lines.append("=" * 60)
        lines.append(f"\nImprovements: {len(comparison['improvements'])}")
        lines.append(f"Regressions: {len(comparison['regressions'])}")

        if len(comparison['improvements']) > len(comparison['regressions']):
            lines.append("\nOverall: Positive trend ↑")
        elif len(comparison['regressions']) > len(comparison['improvements']):
            lines.append("\nOverall: Negative trend ↓")
        else:
            lines.append("\nOverall: Mixed results →")

        lines.append("\n" + "=" * 60)

        return "\n".join(lines)


def main():
    """CLI interface for period comparator."""
    import argparse

    parser = argparse.ArgumentParser(description="Compare metrics between periods")
    parser.add_argument(
        'period1',
        help='First period (e.g., "7", "last-week", "November")'
    )
    parser.add_argument(
        'period2',
        nargs='?',
        help='Second period (optional, defaults to previous equivalent period)'
    )
    parser.add_argument('--metric', help='Specific metric to compare')
    parser.add_argument(
        '--scope',
        default='general',
        choices=['general', 'page'],
        help='Data scope'
    )

    args = parser.parse_args()

    # Parse periods
    period1 = DateParser.parse(args.period1)

    comparator = PeriodComparator()

    if args.period2:
        # Compare two specific periods
        period2 = DateParser.parse(args.period2)
        comparison = comparator.compare_periods(
            period1,
            period2,
            metric_name=args.metric,
            data_scope=args.scope
        )
    else:
        # Compare to previous equivalent period
        comparison = comparator.compare_to_previous(
            period1,
            metric_name=args.metric,
            data_scope=args.scope
        )

    # Display results
    print(comparator.format_comparison(comparison))


if __name__ == "__main__":
    main()
