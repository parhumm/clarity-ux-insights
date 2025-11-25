#!/usr/bin/env python3
"""
Long-term trend analysis for UX metrics.
Analyze trends, growth rates, and patterns over extended periods.
"""

import sys
from pathlib import Path
from datetime import date, timedelta
from typing import Dict, List, Optional, Any, Tuple
import statistics

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.query_engine import QueryEngine, DateRange, DateParser


class TrendAnalyzer:
    """Analyze long-term trends in UX metrics."""

    def __init__(self):
        """Initialize trend analyzer."""
        self.query_engine = QueryEngine()

    def analyze_trend(
        self,
        date_range: DateRange,
        metric_name: Optional[str] = None,
        data_scope: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze trends over a date range.

        Args:
            date_range: Period to analyze
            metric_name: Optional specific metric
            data_scope: Data scope (general or page)

        Returns:
            Trend analysis results
        """
        # Query metrics
        metrics = self.query_engine.query_metrics(
            date_range,
            metric_name=metric_name,
            data_scope=data_scope
        )

        if not metrics:
            return {
                'error': 'No data found for period',
                'date_range': {
                    'start': date_range.start.isoformat(),
                    'end': date_range.end.isoformat()
                }
            }

        # Sort by date
        metrics.sort(key=lambda m: m.get('metric_date', ''))

        # Analyze different aspects
        analysis = {
            'period': {
                'start': date_range.start.isoformat(),
                'end': date_range.end.isoformat(),
                'days': (date_range.end - date_range.start).days + 1,
                'data_points': len(metrics)
            },
            'overall': self._analyze_overall(metrics),
            'growth': self._analyze_growth(metrics),
            'volatility': self._analyze_volatility(metrics),
            'trends': self._identify_trends(metrics),
            'patterns': self._identify_patterns(metrics)
        }

        return analysis

    def _analyze_overall(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Analyze overall metrics summary."""
        total_sessions = sum(m.get('sessions') or 0 for m in metrics)
        total_users = sum(m.get('users') or 0 for m in metrics)
        total_page_views = sum(m.get('page_views') or 0 for m in metrics)

        # Frustration totals
        total_dead_clicks = sum(m.get('dead_clicks') or 0 for m in metrics)
        total_rage_clicks = sum(m.get('rage_clicks') or 0 for m in metrics)
        total_quick_backs = sum(m.get('quick_backs') or 0 for m in metrics)

        return {
            'sessions': {
                'total': total_sessions,
                'average_per_day': total_sessions / len(metrics),
                'max': max((m.get('sessions') or 0 for m in metrics), default=0),
                'min': min((m.get('sessions') or 0 for m in metrics), default=0)
            },
            'users': {
                'total': total_users,
                'average_per_day': total_users / len(metrics)
            },
            'frustration': {
                'dead_clicks': total_dead_clicks,
                'rage_clicks': total_rage_clicks,
                'quick_backs': total_quick_backs,
                'total': total_dead_clicks + total_rage_clicks + total_quick_backs,
                'per_session': (total_dead_clicks + total_rage_clicks + total_quick_backs) / total_sessions if total_sessions else 0
            }
        }

    def _analyze_growth(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Analyze growth rates."""
        if len(metrics) < 2:
            return {'error': 'Insufficient data for growth analysis'}

        # Compare first and last periods
        first_sessions = metrics[0].get('sessions') or 0
        last_sessions = metrics[-1].get('sessions') or 0

        if first_sessions == 0:
            growth_rate = 100 if last_sessions > 0 else 0
        else:
            growth_rate = ((last_sessions - first_sessions) / first_sessions) * 100

        # Calculate CAGR if period > 30 days
        days = len(metrics)
        if days > 30:
            # Compound Annual Growth Rate
            # CAGR = (End/Start)^(365/days) - 1
            if first_sessions > 0:
                cagr = (pow(last_sessions / first_sessions, 365 / days) - 1) * 100
            else:
                cagr = 0
        else:
            cagr = None

        # Calculate average daily growth
        daily_changes = []
        for i in range(1, len(metrics)):
            prev = metrics[i-1].get('sessions') or 0
            curr = metrics[i].get('sessions') or 0
            if prev > 0:
                daily_changes.append(((curr - prev) / prev) * 100)

        avg_daily_growth = statistics.mean(daily_changes) if daily_changes else 0

        return {
            'total_growth': growth_rate,
            'cagr': cagr,
            'avg_daily_growth': avg_daily_growth,
            'first_period_sessions': first_sessions,
            'last_period_sessions': last_sessions,
            'absolute_change': last_sessions - first_sessions
        }

    def _analyze_volatility(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Analyze data volatility."""
        sessions_list = [m.get('sessions') or 0 for m in metrics]

        if len(sessions_list) < 2:
            return {'error': 'Insufficient data for volatility analysis'}

        mean = statistics.mean(sessions_list)
        std_dev = statistics.stdev(sessions_list)
        variance = statistics.variance(sessions_list)

        # Coefficient of variation (CV) - normalized volatility
        cv = (std_dev / mean * 100) if mean > 0 else 0

        return {
            'mean': mean,
            'std_dev': std_dev,
            'variance': variance,
            'coefficient_of_variation': cv,
            'stability': 'high' if cv < 10 else 'medium' if cv < 30 else 'low'
        }

    def _identify_trends(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Identify trends using simple linear regression."""
        if len(metrics) < 3:
            return {'error': 'Insufficient data for trend analysis'}

        sessions_list = [m.get('sessions') or 0 for m in metrics]

        # Simple linear regression: y = mx + b
        n = len(sessions_list)
        x = list(range(n))
        y = sessions_list

        # Calculate slope (m) and intercept (b)
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator

        intercept = y_mean - slope * x_mean

        # Determine trend direction
        if slope > 0.5:
            direction = 'increasing'
        elif slope < -0.5:
            direction = 'decreasing'
        else:
            direction = 'stable'

        # Calculate R-squared (goodness of fit)
        y_pred = [slope * i + intercept for i in x]
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        return {
            'direction': direction,
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_squared,
            'strength': 'strong' if r_squared > 0.7 else 'moderate' if r_squared > 0.4 else 'weak'
        }

    def _identify_patterns(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Identify patterns like weekly cycles."""
        if len(metrics) < 7:
            return {'note': 'Insufficient data for pattern analysis (need 7+ days)'}

        sessions_list = [m.get('sessions') or 0 for m in metrics]

        # Identify peaks and valleys
        peaks = []
        valleys = []

        for i in range(1, len(sessions_list) - 1):
            if sessions_list[i] > sessions_list[i-1] and sessions_list[i] > sessions_list[i+1]:
                peaks.append(i)
            elif sessions_list[i] < sessions_list[i-1] and sessions_list[i] < sessions_list[i+1]:
                valleys.append(i)

        # Calculate peak-to-peak and valley-to-valley distances
        if len(peaks) > 1:
            peak_distances = [peaks[i+1] - peaks[i] for i in range(len(peaks)-1)]
            avg_peak_distance = statistics.mean(peak_distances)
        else:
            avg_peak_distance = None

        if len(valleys) > 1:
            valley_distances = [valleys[i+1] - valleys[i] for i in range(len(valleys)-1)]
            avg_valley_distance = statistics.mean(valley_distances)
        else:
            avg_valley_distance = None

        # Detect weekly pattern (peaks ~7 days apart)
        weekly_pattern = False
        if avg_peak_distance and 6 <= avg_peak_distance <= 8:
            weekly_pattern = True

        return {
            'peaks_count': len(peaks),
            'valleys_count': len(valleys),
            'avg_peak_distance': avg_peak_distance,
            'avg_valley_distance': avg_valley_distance,
            'weekly_pattern_detected': weekly_pattern,
            'cyclical': avg_peak_distance is not None and avg_peak_distance > 0
        }

    def format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format analysis results as readable text."""
        lines = []

        # Header
        lines.append("=" * 60)
        lines.append("LONG-TERM TREND ANALYSIS")
        lines.append("=" * 60)

        if 'error' in analysis:
            lines.append(f"\nError: {analysis['error']}")
            return "\n".join(lines)

        # Period
        period = analysis['period']
        lines.append(f"\nPeriod: {period['start']} to {period['end']}")
        lines.append(f"Duration: {period['days']} days ({period['data_points']} data points)")

        # Overall metrics
        lines.append("\n" + "=" * 60)
        lines.append("OVERALL METRICS")
        lines.append("=" * 60)

        overall = analysis['overall']
        sessions = overall['sessions']
        lines.append(f"\nSessions:")
        lines.append(f"  Total: {sessions['total']:,}")
        lines.append(f"  Average per day: {sessions['average_per_day']:,.0f}")
        lines.append(f"  Range: {sessions['min']:,} - {sessions['max']:,}")

        if 'frustration' in overall:
            frust = overall['frustration']
            lines.append(f"\nFrustration Signals:")
            lines.append(f"  Total: {frust['total']:,}")
            lines.append(f"  Per session: {frust['per_session']:.2f}")

        # Growth
        if 'growth' in analysis and 'error' not in analysis['growth']:
            lines.append("\n" + "=" * 60)
            lines.append("GROWTH ANALYSIS")
            lines.append("=" * 60)

            growth = analysis['growth']
            lines.append(f"\nTotal Growth: {growth['total_growth']:+.1f}%")
            lines.append(f"  First period: {growth['first_period_sessions']:,} sessions")
            lines.append(f"  Last period: {growth['last_period_sessions']:,} sessions")
            lines.append(f"  Absolute change: {growth['absolute_change']:+,}")

            if growth.get('cagr') is not None:
                lines.append(f"\nCompound Annual Growth Rate (CAGR): {growth['cagr']:+.1f}%")

            lines.append(f"\nAverage Daily Growth: {growth['avg_daily_growth']:+.2f}%")

        # Volatility
        if 'volatility' in analysis and 'error' not in analysis['volatility']:
            lines.append("\n" + "=" * 60)
            lines.append("VOLATILITY ANALYSIS")
            lines.append("=" * 60)

            vol = analysis['volatility']
            lines.append(f"\nMean: {vol['mean']:,.0f} sessions/day")
            lines.append(f"Standard Deviation: {vol['std_dev']:,.0f}")
            lines.append(f"Coefficient of Variation: {vol['coefficient_of_variation']:.1f}%")
            lines.append(f"Stability: {vol['stability'].upper()}")

        # Trends
        if 'trends' in analysis and 'error' not in analysis['trends']:
            lines.append("\n" + "=" * 60)
            lines.append("TREND ANALYSIS")
            lines.append("=" * 60)

            trends = analysis['trends']
            lines.append(f"\nDirection: {trends['direction'].upper()}")
            lines.append(f"Slope: {trends['slope']:+.2f} sessions/day")
            lines.append(f"R-squared: {trends['r_squared']:.3f}")
            lines.append(f"Strength: {trends['strength'].upper()}")

        # Patterns
        if 'patterns' in analysis and 'note' not in analysis['patterns']:
            lines.append("\n" + "=" * 60)
            lines.append("PATTERN ANALYSIS")
            lines.append("=" * 60)

            patterns = analysis['patterns']
            lines.append(f"\nPeaks detected: {patterns['peaks_count']}")
            lines.append(f"Valleys detected: {patterns['valleys_count']}")

            if patterns.get('avg_peak_distance'):
                lines.append(f"Average peak distance: {patterns['avg_peak_distance']:.1f} days")

            if patterns['weekly_pattern_detected']:
                lines.append("\n✓ Weekly pattern detected (peaks ~7 days apart)")

            if patterns['cyclical']:
                lines.append("✓ Cyclical pattern present")

        lines.append("\n" + "=" * 60)

        return "\n".join(lines)


def main():
    """CLI interface for trend analyzer."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze long-term trends")
    parser.add_argument(
        'date_range',
        help='Date range to analyze (e.g., "30", "last-month", "2025-Q4")'
    )
    parser.add_argument('--metric', help='Specific metric to analyze')
    parser.add_argument(
        '--scope',
        default='general',
        choices=['general', 'page'],
        help='Data scope'
    )

    args = parser.parse_args()

    # Parse date range
    date_range = DateParser.parse(args.date_range)

    # Analyze trends
    analyzer = TrendAnalyzer()
    analysis = analyzer.analyze_trend(
        date_range,
        metric_name=args.metric,
        data_scope=args.scope
    )

    # Display results
    print(analyzer.format_analysis(analysis))


if __name__ == "__main__":
    main()
