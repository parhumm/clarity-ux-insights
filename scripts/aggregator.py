#!/usr/bin/env python3
"""Aggregation engine for weekly and monthly metrics."""

import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class MetricAggregator:
    """Aggregate daily metrics into weekly and monthly summaries."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize aggregator.

        Args:
            db_path: Path to database (default: from config)
        """
        self.db_path = db_path or config.DB_PATH

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def aggregate_weekly_metrics(
        self,
        year: int,
        week_number: int,
        metric_name: str = "Traffic",
        data_scope: str = "general",
        page_id: Optional[str] = None,
        force: bool = False
    ) -> Dict:
        """Aggregate daily metrics into weekly summary.

        Args:
            year: Year
            week_number: ISO week number (1-53)
            metric_name: Metric to aggregate
            data_scope: 'general' or 'page'
            page_id: Page ID (for page scope)
            force: Force recalculation even if exists

        Returns:
            Dictionary with aggregated metrics
        """
        conn = self.get_connection()
        try:
            # Calculate week start and end dates
            week_start = self._get_week_start(year, week_number)
            week_end = week_start + timedelta(days=6)

            # Check if already exists
            if not force:
                cursor = conn.execute("""
                    SELECT * FROM weekly_metrics
                    WHERE week_start = ? AND week_end = ?
                      AND metric_name = ? AND data_scope = ?
                      AND (page_id = ? OR (page_id IS NULL AND ? IS NULL))
                """, (week_start, week_end, metric_name, data_scope, page_id, page_id))

                existing = cursor.fetchone()
                if existing:
                    print(f"  ℹ Weekly metrics already exist for {week_start} to {week_end}")
                    return dict(existing)

            # Aggregate from daily metrics
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as data_points,
                    AVG(sessions) as avg_sessions,
                    SUM(sessions) as sum_sessions,
                    AVG(users) as avg_users,
                    SUM(users) as sum_users,
                    AVG(dead_clicks) as avg_dead_clicks,
                    AVG(rage_clicks) as avg_rage_clicks,
                    AVG(quick_backs) as avg_quick_backs,
                    AVG(scroll_depth) as avg_scroll_depth,
                    AVG(engagement_time) as avg_engagement_time
                FROM daily_metrics
                WHERE metric_date BETWEEN ? AND ?
                  AND metric_name = ?
                  AND data_scope = ?
                  AND (page_id = ? OR (page_id IS NULL AND ? IS NULL))
            """, (week_start, week_end, metric_name, data_scope, page_id, page_id))

            result = cursor.fetchone()

            if result['data_points'] == 0:
                print(f"  ⚠ No data found for week {year}-W{week_number}")
                return {}

            # Insert aggregated data
            conn.execute("""
                INSERT OR REPLACE INTO weekly_metrics (
                    week_start, week_end, year, week_number,
                    metric_name, data_scope, page_id,
                    avg_sessions, sum_sessions,
                    avg_users, sum_users,
                    avg_dead_clicks, avg_rage_clicks, avg_quick_backs,
                    avg_scroll_depth, avg_engagement_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                week_start, week_end, year, week_number,
                metric_name, data_scope, page_id,
                result['avg_sessions'], result['sum_sessions'],
                result['avg_users'], result['sum_users'],
                result['avg_dead_clicks'], result['avg_rage_clicks'],
                result['avg_quick_backs'], result['avg_scroll_depth'],
                result['avg_engagement_time']
            ))

            conn.commit()

            return {
                'week_start': week_start,
                'week_end': week_end,
                'data_points': result['data_points'],
                **dict(result)
            }

        finally:
            conn.close()

    def aggregate_monthly_metrics(
        self,
        year: int,
        month: int,
        metric_name: str = "Traffic",
        data_scope: str = "general",
        page_id: Optional[str] = None,
        force: bool = False
    ) -> Dict:
        """Aggregate daily metrics into monthly summary.

        Args:
            year: Year
            month: Month (1-12)
            metric_name: Metric to aggregate
            data_scope: 'general' or 'page'
            page_id: Page ID (for page scope)
            force: Force recalculation even if exists

        Returns:
            Dictionary with aggregated metrics
        """
        conn = self.get_connection()
        try:
            # Check if already exists
            if not force:
                cursor = conn.execute("""
                    SELECT * FROM monthly_metrics
                    WHERE year = ? AND month = ?
                      AND metric_name = ? AND data_scope = ?
                      AND (page_id = ? OR (page_id IS NULL AND ? IS NULL))
                """, (year, month, metric_name, data_scope, page_id, page_id))

                existing = cursor.fetchone()
                if existing:
                    print(f"  ℹ Monthly metrics already exist for {year}-{month:02d}")
                    return dict(existing)

            # Calculate month start and end
            month_start = date(year, month, 1)
            if month == 12:
                month_end = date(year, 12, 31)
            else:
                month_end = date(year, month + 1, 1) - timedelta(days=1)

            # Aggregate from daily metrics
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as data_points,
                    AVG(sessions) as avg_sessions,
                    SUM(sessions) as sum_sessions,
                    MIN(sessions) as min_sessions,
                    MAX(sessions) as max_sessions,
                    AVG(users) as avg_users,
                    SUM(users) as sum_users,
                    AVG(dead_clicks) as avg_dead_clicks,
                    AVG(rage_clicks) as avg_rage_clicks,
                    AVG(quick_backs) as avg_quick_backs,
                    AVG(scroll_depth) as avg_scroll_depth,
                    AVG(engagement_time) as avg_engagement_time
                FROM daily_metrics
                WHERE metric_date BETWEEN ? AND ?
                  AND metric_name = ?
                  AND data_scope = ?
                  AND (page_id = ? OR (page_id IS NULL AND ? IS NULL))
            """, (month_start, month_end, metric_name, data_scope, page_id, page_id))

            result = cursor.fetchone()

            if result['data_points'] == 0:
                print(f"  ⚠ No data found for {year}-{month:02d}")
                return {}

            # Insert aggregated data
            conn.execute("""
                INSERT OR REPLACE INTO monthly_metrics (
                    year, month, metric_name, data_scope, page_id,
                    avg_sessions, sum_sessions,
                    min_sessions, max_sessions,
                    avg_users, sum_users,
                    avg_dead_clicks, avg_rage_clicks, avg_quick_backs,
                    avg_scroll_depth, avg_engagement_time,
                    data_points
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                year, month, metric_name, data_scope, page_id,
                result['avg_sessions'], result['sum_sessions'],
                result['min_sessions'], result['max_sessions'],
                result['avg_users'], result['sum_users'],
                result['avg_dead_clicks'], result['avg_rage_clicks'],
                result['avg_quick_backs'], result['avg_scroll_depth'],
                result['avg_engagement_time'],
                result['data_points']
            ))

            conn.commit()

            return {
                'year': year,
                'month': month,
                'data_points': result['data_points'],
                **dict(result)
            }

        finally:
            conn.close()

    def aggregate_all_available(self, force: bool = False) -> Dict[str, int]:
        """Aggregate all available daily data into weekly and monthly summaries.

        Args:
            force: Force recalculation of existing aggregations

        Returns:
            Dictionary with counts of aggregations created
        """
        conn = self.get_connection()
        try:
            # Get date range of available data
            cursor = conn.execute("""
                SELECT
                    MIN(metric_date) as min_date,
                    MAX(metric_date) as max_date,
                    COUNT(DISTINCT metric_date) as date_count
                FROM daily_metrics
            """)
            result = cursor.fetchone()

            if not result['min_date']:
                print("  ⚠ No daily metrics found")
                return {'weekly': 0, 'monthly': 0}

            min_date = datetime.strptime(result['min_date'], '%Y-%m-%d').date()
            max_date = datetime.strptime(result['max_date'], '%Y-%m-%d').date()

            print(f"\n📊 Aggregating data from {min_date} to {max_date}")
            print(f"   ({result['date_count']} days of data)")

            weekly_count = 0
            monthly_count = 0

            # Aggregate by weeks
            print("\n  Aggregating weekly metrics...")
            current_date = min_date
            while current_date <= max_date:
                iso_year, iso_week, _ = current_date.isocalendar()
                try:
                    result = self.aggregate_weekly_metrics(iso_year, iso_week, force=force)
                    if result:
                        weekly_count += 1
                        print(f"    ✓ Week {iso_year}-W{iso_week:02d}")
                except Exception as e:
                    print(f"    ✗ Week {iso_year}-W{iso_week:02d}: {e}")

                # Move to next week
                current_date += timedelta(days=7)

            # Aggregate by months
            print("\n  Aggregating monthly metrics...")
            current_year = min_date.year
            current_month = min_date.month
            end_year = max_date.year
            end_month = max_date.month

            while (current_year, current_month) <= (end_year, end_month):
                try:
                    result = self.aggregate_monthly_metrics(current_year, current_month, force=force)
                    if result:
                        monthly_count += 1
                        print(f"    ✓ {current_year}-{current_month:02d}")
                except Exception as e:
                    print(f"    ✗ {current_year}-{current_month:02d}: {e}")

                # Move to next month
                if current_month == 12:
                    current_year += 1
                    current_month = 1
                else:
                    current_month += 1

            return {'weekly': weekly_count, 'monthly': monthly_count}

        finally:
            conn.close()

    def _get_week_start(self, year: int, week: int) -> date:
        """Get the start date (Monday) of an ISO week.

        Args:
            year: Year
            week: ISO week number

        Returns:
            Date of Monday in that week
        """
        # ISO week 1 is the week with the year's first Thursday
        jan_4 = date(year, 1, 4)
        week_1_monday = jan_4 - timedelta(days=jan_4.weekday())
        return week_1_monday + timedelta(weeks=week - 1)


if __name__ == "__main__":
    print("=" * 60)
    print("METRIC AGGREGATOR")
    print("=" * 60)

    aggregator = MetricAggregator()

    # Test individual week aggregation
    print("\n🧪 Testing weekly aggregation...")
    result = aggregator.aggregate_weekly_metrics(2025, 47, force=True)
    if result:
        print(f"  ✓ Week 2025-W47: {result['data_points']} data points")
        print(f"    Avg sessions: {result.get('avg_sessions', 0)}")

    # Test individual month aggregation
    print("\n🧪 Testing monthly aggregation...")
    result = aggregator.aggregate_monthly_metrics(2025, 11, force=True)
    if result:
        print(f"  ✓ November 2025: {result['data_points']} data points")
        print(f"    Avg sessions: {result.get('avg_sessions', 0)}")
        print(f"    Total sessions: {result.get('sum_sessions', 0)}")

    # Test aggregate all
    print("\n🧪 Testing aggregate all...")
    counts = aggregator.aggregate_all_available(force=True)
    print(f"\n✅ Aggregation complete:")
    print(f"   Weekly aggregations: {counts['weekly']}")
    print(f"   Monthly aggregations: {counts['monthly']}")
