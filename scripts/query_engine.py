#!/usr/bin/env python3
"""Query engine for flexible date range queries on Clarity data."""

import sqlite3
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


@dataclass
class DateRange:
    """Represents a date range."""
    start: date
    end: date
    description: str = ""

    @property
    def days(self) -> int:
        """Number of days in the range."""
        return (self.end - self.start).days + 1

    def __str__(self) -> str:
        if self.description:
            return f"{self.description} ({self.start} to {self.end})"
        return f"{self.start} to {self.end}"


class DateParser:
    """Parse flexible date expressions into date ranges."""

    @staticmethod
    def parse(expression: str, reference_date: Optional[date] = None) -> DateRange:
        """Parse date expression into a DateRange.

        Supported formats:
        - Numbers: "3", "7", "30" (last N days)
        - With suffix: "3days", "7d", "2weeks", "1month"
        - Relative: "last-week", "last-month", "yesterday", "today"
        - Month: "2025-11", "November", "Nov 2025"
        - Quarter: "2025-Q4", "Q4 2025", "2025Q4"
        - Year: "2025"
        - Custom range: "2025-11-01 to 2025-11-30"
        - ISO range: "2025-11-01:2025-11-30"

        Args:
            expression: Date expression to parse
            reference_date: Reference date for relative expressions (default: today)

        Returns:
            DateRange object

        Raises:
            ValueError: If expression cannot be parsed
        """
        if reference_date is None:
            reference_date = date.today()

        expression = expression.strip()

        # Try different parsers in order (specific to general)
        parsers = [
            DateParser._parse_custom_range,
            DateParser._parse_quarter,
            DateParser._parse_year,           # Try year before numeric (2025 vs 2025 days)
            DateParser._parse_month,
            DateParser._parse_relative,
            DateParser._parse_numeric,
        ]

        for parser in parsers:
            try:
                result = parser(expression, reference_date)
                if result:
                    return result
            except:
                continue

        raise ValueError(f"Unable to parse date expression: {expression}")

    @staticmethod
    def _parse_numeric(expr: str, ref_date: date) -> Optional[DateRange]:
        """Parse numeric expressions like '3', '7days', '2weeks'."""
        # Match: 3, 7d, 30days, 2weeks, 1month, etc.
        match = re.match(r'^(\d+)\s*(d|days?|w|weeks?|m|months?)?$', expr, re.I)
        if not match:
            return None

        number = int(match.group(1))
        unit = (match.group(2) or 'd').lower()

        # Convert to days
        if unit.startswith('d'):
            days = number
        elif unit.startswith('w'):
            days = number * 7
        elif unit.startswith('m'):
            days = number * 30
        else:
            return None

        end_date = ref_date
        start_date = end_date - timedelta(days=days - 1)

        return DateRange(
            start=start_date,
            end=end_date,
            description=f"Last {days} days"
        )

    @staticmethod
    def _parse_relative(expr: str, ref_date: date) -> Optional[DateRange]:
        """Parse relative expressions like 'yesterday', 'last-week', 'last-month'."""
        expr_lower = expr.lower().replace('_', '-')

        if expr_lower in ['today', 'now']:
            return DateRange(ref_date, ref_date, "Today")

        if expr_lower == 'yesterday':
            yesterday = ref_date - timedelta(days=1)
            return DateRange(yesterday, yesterday, "Yesterday")

        if expr_lower in ['last-week', 'lastweek']:
            end_date = ref_date - timedelta(days=ref_date.weekday() + 1)  # Last Sunday
            start_date = end_date - timedelta(days=6)
            return DateRange(start_date, end_date, "Last week")

        if expr_lower in ['this-week', 'thisweek']:
            start_date = ref_date - timedelta(days=ref_date.weekday())  # This Monday
            return DateRange(start_date, ref_date, "This week")

        if expr_lower in ['last-month', 'lastmonth']:
            # First day of last month
            first_of_this_month = ref_date.replace(day=1)
            last_month_end = first_of_this_month - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            return DateRange(last_month_start, last_month_end, f"Last month ({last_month_start.strftime('%B %Y')})")

        if expr_lower in ['this-month', 'thismonth']:
            start_date = ref_date.replace(day=1)
            return DateRange(start_date, ref_date, f"This month ({ref_date.strftime('%B %Y')})")

        return None

    @staticmethod
    def _parse_month(expr: str, ref_date: date) -> Optional[DateRange]:
        """Parse month expressions like '2025-11', 'November', 'Nov 2025'."""
        # Format: YYYY-MM
        match = re.match(r'^(\d{4})-(\d{1,2})$', expr)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            start_date = date(year, month, 1)
            # Last day of month
            if month == 12:
                end_date = date(year, 12, 31)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            return DateRange(start_date, end_date, f"{start_date.strftime('%B %Y')}")

        # Month name (current year or specified year)
        month_names = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12,
        }

        expr_lower = expr.lower().strip()

        # Try "Month Year" or "Month YYYY"
        for month_name, month_num in month_names.items():
            if expr_lower.startswith(month_name):
                # Extract year if present
                year_match = re.search(r'(\d{4})', expr)
                year = int(year_match.group(1)) if year_match else ref_date.year

                start_date = date(year, month_num, 1)
                if month_num == 12:
                    end_date = date(year, 12, 31)
                else:
                    end_date = date(year, month_num + 1, 1) - timedelta(days=1)

                return DateRange(start_date, end_date, f"{start_date.strftime('%B %Y')}")

        return None

    @staticmethod
    def _parse_quarter(expr: str, ref_date: date) -> Optional[DateRange]:
        """Parse quarter expressions like '2025-Q4', 'Q4 2025', '2025Q4'."""
        # Match: 2025-Q4, Q4 2025, 2025Q4, etc.
        match = re.match(r'^(?:(\d{4})[-\s]?Q(\d)|Q(\d)[-\s]?(\d{4}))$', expr, re.I)
        if not match:
            return None

        year = int(match.group(1) or match.group(4))
        quarter = int(match.group(2) or match.group(3))

        if quarter < 1 or quarter > 4:
            return None

        # Calculate quarter date range
        start_month = (quarter - 1) * 3 + 1
        start_date = date(year, start_month, 1)

        end_month = start_month + 2
        if end_month == 12:
            end_date = date(year, 12, 31)
        else:
            end_date = date(year, end_month + 1, 1) - timedelta(days=1)

        return DateRange(start_date, end_date, f"Q{quarter} {year}")

    @staticmethod
    def _parse_year(expr: str, ref_date: date) -> Optional[DateRange]:
        """Parse year expressions like '2025'."""
        match = re.match(r'^(\d{4})$', expr)
        if not match:
            return None

        year = int(match.group(1))
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        return DateRange(start_date, end_date, f"Year {year}")

    @staticmethod
    def _parse_custom_range(expr: str, ref_date: date) -> Optional[DateRange]:
        """Parse custom range like '2025-11-01 to 2025-11-30' or '2025-11-01:2025-11-30'."""
        # Try "DATE to DATE" format
        match = re.match(r'^(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})$', expr, re.I)
        if not match:
            # Try "DATE:DATE" format
            match = re.match(r'^(\d{4}-\d{2}-\d{2}):(\d{4}-\d{2}-\d{2})$', expr)

        if not match:
            return None

        start_date = date.fromisoformat(match.group(1))
        end_date = date.fromisoformat(match.group(2))

        if start_date > end_date:
            start_date, end_date = end_date, start_date

        return DateRange(start_date, end_date, f"{start_date} to {end_date}")


class QueryEngine:
    """Engine for querying Clarity metrics with flexible date ranges."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize query engine.

        Args:
            db_path: Path to database file (default: from config)
        """
        self.db_path = db_path or config.DB_PATH

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def query_metrics(
        self,
        date_range: Union[str, DateRange],
        metric_name: Optional[str] = None,
        data_scope: str = 'general',
        page_id: Optional[str] = None,
        dimension1: Optional[str] = None,
        dimension1_value: Optional[str] = None,
    ) -> List[Dict]:
        """Query metrics for a date range.

        Args:
            date_range: Date range (string expression or DateRange object)
            metric_name: Filter by metric name (optional)
            data_scope: 'general' or 'page'
            page_id: Page ID filter (for page scope)
            dimension1: First dimension name filter
            dimension1_value: First dimension value filter

        Returns:
            List of metric dictionaries
        """
        # Parse date range if string
        if isinstance(date_range, str):
            date_range = DateParser.parse(date_range)

        conn = self.get_connection()
        try:
            query = """
                SELECT *
                FROM daily_metrics
                WHERE metric_date BETWEEN ? AND ?
                  AND data_scope = ?
            """
            params = [date_range.start, date_range.end, data_scope]

            if metric_name:
                query += " AND metric_name = ?"
                params.append(metric_name)

            if page_id:
                query += " AND page_id = ?"
                params.append(page_id)

            if dimension1:
                query += " AND dimension1_name = ?"
                params.append(dimension1)

                if dimension1_value:
                    query += " AND dimension1_value = ?"
                    params.append(dimension1_value)

            query += " ORDER BY metric_date DESC, metric_name"

            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

        finally:
            conn.close()

    def aggregate_metrics(
        self,
        date_range: Union[str, DateRange],
        metric_name: str,
        data_scope: str = 'general',
        page_id: Optional[str] = None,
    ) -> Dict:
        """Aggregate metrics over a date range.

        Args:
            date_range: Date range to aggregate
            metric_name: Metric to aggregate
            data_scope: 'general' or 'page'
            page_id: Page ID (for page scope)

        Returns:
            Dictionary with aggregated values
        """
        # Parse date range if string
        if isinstance(date_range, str):
            date_range = DateParser.parse(date_range)

        conn = self.get_connection()
        try:
            query = """
                SELECT
                    COUNT(*) as data_points,
                    AVG(sessions) as avg_sessions,
                    SUM(sessions) as total_sessions,
                    MIN(sessions) as min_sessions,
                    MAX(sessions) as max_sessions,
                    AVG(users) as avg_users,
                    SUM(users) as total_users,
                    AVG(dead_clicks) as avg_dead_clicks,
                    AVG(rage_clicks) as avg_rage_clicks,
                    AVG(quick_backs) as avg_quick_backs,
                    AVG(scroll_depth) as avg_scroll_depth,
                    AVG(engagement_time) as avg_engagement_time
                FROM daily_metrics
                WHERE metric_date BETWEEN ? AND ?
                  AND metric_name = ?
                  AND data_scope = ?
            """
            params = [date_range.start, date_range.end, metric_name, data_scope]

            if page_id:
                query += " AND page_id = ?"
                params.append(page_id)

            cursor = conn.execute(query, params)
            result = cursor.fetchone()

            return {
                'date_range': str(date_range),
                'start_date': date_range.start,
                'end_date': date_range.end,
                'days': date_range.days,
                **dict(result)
            }

        finally:
            conn.close()

    def get_available_dates(self, data_scope: str = 'general') -> List[date]:
        """Get list of dates with available data.

        Args:
            data_scope: 'general' or 'page'

        Returns:
            List of dates with data
        """
        conn = self.get_connection()
        try:
            cursor = conn.execute("""
                SELECT DISTINCT metric_date
                FROM daily_metrics
                WHERE data_scope = ?
                ORDER BY metric_date DESC
            """, (data_scope,))

            return [row['metric_date'] for row in cursor.fetchall()]

        finally:
            conn.close()


if __name__ == "__main__":
    # Test query engine
    print("=" * 60)
    print("QUERY ENGINE TESTS")
    print("=" * 60)

    # Test date parser
    print("\n📅 Testing Date Parser...")
    test_expressions = [
        "3",
        "7days",
        "2weeks",
        "yesterday",
        "last-week",
        "last-month",
        "2025-11",
        "November",
        "2025-Q4",
        "Q4 2025",
        "2025",
        "2025-11-01 to 2025-11-30",
    ]

    for expr in test_expressions:
        try:
            range_obj = DateParser.parse(expr)
            print(f"  ✓ '{expr}' → {range_obj}")
        except Exception as e:
            print(f"  ❌ '{expr}' → {e}")

    # Test query engine
    print("\n📊 Testing Query Engine...")
    engine = QueryEngine()

    # Get available dates
    dates = engine.get_available_dates()
    print(f"\n  Available dates: {len(dates)}")
    if dates:
        print(f"    Latest: {dates[0]}")
        print(f"    Earliest: {dates[-1]}")

    # Test query
    if dates:
        metrics = engine.query_metrics("last-week", metric_name="Traffic")
        print(f"\n  Last week Traffic metrics: {len(metrics)} records")

        if metrics:
            sample = metrics[0]
            print(f"    Sample: {sample.get('metric_date')} - {sample.get('sessions')} sessions")

    print("\n✅ Query engine tests complete!")
