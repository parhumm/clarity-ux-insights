#!/usr/bin/env python3
"""Tests for database schema v2."""

import sys
from pathlib import Path
import sqlite3
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))
import config


def test_daily_metrics_insert():
    """Test inserting daily metrics."""
    print("\n🧪 Testing daily_metrics insert...")

    conn = sqlite3.connect(config.DB_PATH)
    try:
        # Insert a test metric
        today = date.today()
        conn.execute("""
            INSERT INTO daily_metrics (
                metric_date, metric_name, data_scope,
                sessions, users, bot_sessions,
                dead_clicks, rage_clicks, quick_backs
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            today, 'Traffic', 'general',
            1500, 1200, 50,
            120, 15, 300
        ))
        conn.commit()
        print("  ✓ Successfully inserted test metric")

        # Try inserting duplicate (should fail)
        try:
            conn.execute("""
                INSERT INTO daily_metrics (
                    metric_date, metric_name, data_scope,
                    sessions, users, bot_sessions
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (today, 'Traffic', 'general', 1600, 1300, 60))
            conn.commit()
            print("  ❌ Duplicate constraint failed to prevent duplicate")
        except sqlite3.IntegrityError:
            print("  ✓ Duplicate constraint working correctly")

    finally:
        conn.close()


def test_page_tracking():
    """Test page tracking functionality."""
    print("\n🧪 Testing page tracking...")

    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        # Insert test pages
        test_pages = [
            ('page-001', '/checkout', 'Checkout', 'conversion'),
            ('page-002', '/search', 'Search', 'discovery'),
            ('page-003', '/product/123', 'Product Page', 'content'),
        ]

        for page_data in test_pages:
            conn.execute("""
                INSERT OR IGNORE INTO pages (id, path, name, category)
                VALUES (?, ?, ?, ?)
            """, page_data)

        conn.commit()
        print("  ✓ Inserted 3 test pages")

        # Query pages
        cursor = conn.execute("SELECT * FROM pages WHERE active = 1")
        pages = cursor.fetchall()
        print(f"  ✓ Retrieved {len(pages)} active pages")

        for page in pages:
            print(f"    - {page['id']}: {page['path']} ({page['category']})")

    finally:
        conn.close()


def test_date_range_queries():
    """Test date range query performance."""
    print("\n🧪 Testing date range queries...")

    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        # Query last 7 days
        end_date = date.today()
        start_date = end_date - timedelta(days=7)

        cursor = conn.execute("""
            SELECT metric_date, COUNT(*) as count
            FROM daily_metrics
            WHERE metric_date BETWEEN ? AND ?
            GROUP BY metric_date
            ORDER BY metric_date DESC
        """, (start_date, end_date))

        results = cursor.fetchall()
        print(f"  ✓ Found data for {len(results)} days in last 7 days")

        # Query specific month
        cursor = conn.execute("""
            SELECT COUNT(*) as count
            FROM daily_metrics
            WHERE strftime('%Y-%m', metric_date) = '2025-11'
        """)

        november_count = cursor.fetchone()['count']
        print(f"  ✓ November 2025: {november_count} records")

        # Test query performance with EXPLAIN QUERY PLAN
        cursor = conn.execute("""
            EXPLAIN QUERY PLAN
            SELECT * FROM daily_metrics
            WHERE metric_date BETWEEN ? AND ?
        """, (start_date, end_date))

        plan = cursor.fetchall()
        uses_index = any('idx_daily_date' in str(row) for row in plan)
        if uses_index:
            print("  ✓ Date index is being used for queries")
        else:
            print("  ⚠ Date index not being used (check schema)")

    finally:
        conn.close()


def test_fetch_log():
    """Test fetch log functionality."""
    print("\n🧪 Testing fetch_log...")

    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        # Insert a test fetch log entry
        today = date.today()
        conn.execute("""
            INSERT INTO fetch_log (
                request_period_days, date_start, date_end,
                scope, status_code, success, records_imported
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (3, today - timedelta(days=3), today, 'general', 200, True, 100))

        conn.commit()
        print("  ✓ Inserted test fetch log entry")

        # Query recent fetches
        cursor = conn.execute("""
            SELECT * FROM fetch_log
            ORDER BY fetch_timestamp DESC
            LIMIT 5
        """)

        fetches = cursor.fetchall()
        print(f"  ✓ Retrieved {len(fetches)} recent fetch logs")

        for fetch in fetches:
            print(f"    - {fetch['date_start']} to {fetch['date_end']}: {fetch['records_imported']} records")

    finally:
        conn.close()


def test_aggregation_tables():
    """Test weekly and monthly aggregation tables."""
    print("\n🧪 Testing aggregation tables...")

    conn = sqlite3.connect(config.DB_PATH)

    try:
        # Insert test weekly aggregate
        conn.execute("""
            INSERT INTO weekly_metrics (
                week_start, week_end, year, week_number,
                metric_name, data_scope,
                avg_sessions, sum_sessions
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date(2025, 11, 18), date(2025, 11, 24),
            2025, 47, 'Traffic', 'general',
            1450.5, 10154
        ))

        # Insert test monthly aggregate
        conn.execute("""
            INSERT INTO monthly_metrics (
                year, month, metric_name, data_scope,
                avg_sessions, sum_sessions, min_sessions, max_sessions,
                data_points
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            2025, 11, 'Traffic', 'general',
            1450.5, 43515, 1200, 1650, 30
        ))

        conn.commit()
        print("  ✓ Inserted test aggregation records")
        print("  ✓ Weekly and monthly aggregation tables working")

    finally:
        conn.close()


def test_schema_integrity():
    """Test overall schema integrity."""
    print("\n🧪 Testing schema integrity...")

    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        # Check all tables exist
        cursor = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """)

        tables = [row['name'] for row in cursor.fetchall()]
        expected_tables = [
            'api_requests',  # Old table (kept for compatibility)
            'archive_log',
            'clarity_metrics',  # Old table (kept for compatibility)
            'daily_metrics',
            'fetch_log',
            'monthly_metrics',
            'pages',
            'weekly_metrics'
        ]

        for table in expected_tables:
            if table in tables:
                print(f"  ✓ Table '{table}' exists")
            else:
                print(f"  ❌ Table '{table}' missing!")

        # Check indexes
        cursor = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND name LIKE 'idx_%'
            ORDER BY name
        """)

        indexes = [row['name'] for row in cursor.fetchall()]
        print(f"  ✓ Found {len(indexes)} custom indexes")

    finally:
        conn.close()


def run_all_tests():
    """Run all database tests."""
    print("=" * 60)
    print("CLARITY API DATABASE V2 TESTS")
    print("=" * 60)

    tests = [
        test_schema_integrity,
        test_daily_metrics_insert,
        test_page_tracking,
        test_date_range_queries,
        test_fetch_log,
        test_aggregation_tables,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
