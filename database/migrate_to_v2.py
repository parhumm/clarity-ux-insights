#!/usr/bin/env python3
"""Migration script from schema v1 to v2 (time-series optimized)."""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
import config


def migrate_database():
    """Migrate database from v1 to v2 schema."""
    db_path = config.DB_PATH
    print(f"Migrating database: {db_path}")

    if not db_path.exists():
        print("No existing database found. Creating new v2 schema...")
        create_v2_schema(db_path)
        print("✓ New v2 database created")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Check if v2 schema already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_metrics'")
        if cursor.fetchone():
            print("✓ Database is already using v2 schema")
            conn.close()
            return

        print("Step 1: Backing up existing database...")
        backup_path = db_path.parent / f"{db_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✓ Backup created: {backup_path}")

        print("\nStep 2: Creating v2 schema tables...")
        schema_v2_path = Path(__file__).parent / "schema_v2.sql"
        with open(schema_v2_path, 'r') as f:
            schema_v2 = f.read()
        conn.executescript(schema_v2)
        conn.commit()
        print("✓ V2 tables created")

        print("\nStep 3: Migrating data from clarity_metrics to daily_metrics...")
        cursor.execute("SELECT COUNT(*) as count FROM clarity_metrics")
        total_records = cursor.fetchone()['count']
        print(f"Found {total_records} records to migrate")

        if total_records > 0:
            # Migrate existing data
            cursor.execute("""
                SELECT * FROM clarity_metrics
                ORDER BY fetch_timestamp
            """)

            migrated = 0
            skipped = 0

            for row in cursor.fetchall():
                # Calculate metric_date from fetch_timestamp and num_days
                # Assume the fetch represents data UP TO that date
                fetch_ts = datetime.fromisoformat(row['fetch_timestamp'])
                metric_date = fetch_ts.date()

                # Parse raw_json to extract additional metrics
                raw_json = row['raw_json']
                try:
                    info = json.loads(raw_json) if raw_json else {}
                except:
                    info = {}

                # Map v1 fields to v2 fields
                sessions = row['total_session_count']
                users = row['distinct_user_count']
                bot_sessions = row['total_bot_session_count']
                pages_per_session = row['pages_per_session']

                # Extract frustration metrics from raw_json if available
                dead_clicks = _parse_int(info.get('subTotal')) if row['metric_name'] == 'DeadClickCount' else None
                rage_clicks = _parse_int(info.get('subTotal')) if row['metric_name'] == 'RageClickCount' else None
                quick_backs = _parse_int(info.get('subTotal')) if row['metric_name'] == 'QuickbackClick' else None
                scroll_depth = _parse_float(info.get('subTotal')) if row['metric_name'] == 'ScrollDepth' else None

                try:
                    conn.execute("""
                        INSERT INTO daily_metrics (
                            metric_date, fetch_timestamp, metric_name,
                            data_scope, page_id,
                            dimension1_name, dimension1_value,
                            dimension2_name, dimension2_value,
                            dimension3_name, dimension3_value,
                            sessions, users, bot_sessions, pages_per_session,
                            dead_clicks, rage_clicks, quick_backs,
                            scroll_depth,
                            source_file, raw_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        metric_date, row['fetch_timestamp'], row['metric_name'],
                        'general', None,  # All old data is general scope
                        row['dimension1_name'], row['dimension1_value'],
                        row['dimension2_name'], row['dimension2_value'],
                        row['dimension3_name'], row['dimension3_value'],
                        sessions, users, bot_sessions, pages_per_session,
                        dead_clicks, rage_clicks, quick_backs,
                        scroll_depth,
                        None, row['raw_json']
                    ))
                    migrated += 1
                except sqlite3.IntegrityError:
                    skipped += 1

            conn.commit()
            print(f"✓ Migrated {migrated} records ({skipped} duplicates skipped)")

        print("\nStep 4: Migrating API request log...")
        cursor.execute("SELECT COUNT(*) as count FROM api_requests")
        total_requests = cursor.fetchone()['count']

        if total_requests > 0:
            cursor.execute("SELECT * FROM api_requests")
            migrated_requests = 0

            for row in cursor.fetchall():
                # Calculate date range from request_timestamp and num_days
                request_ts = datetime.fromisoformat(row['request_timestamp'])
                date_end = request_ts.date()
                date_start = date_end - timedelta(days=row['num_days'] or 1)

                conn.execute("""
                    INSERT INTO fetch_log (
                        fetch_timestamp, request_period_days,
                        date_start, date_end, scope,
                        dimension1, dimension2, dimension3,
                        status_code, success, error_message, response_size,
                        records_imported
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['request_timestamp'], row['num_days'],
                    date_start, date_end, 'general',
                    row['dimension1'], row['dimension2'], row['dimension3'],
                    row['status_code'], row['success'], row['error_message'],
                    row['response_size'], row['rows_returned'] or 0
                ))
                migrated_requests += 1

            conn.commit()
            print(f"✓ Migrated {migrated_requests} API request records")

        print("\n✅ Migration completed successfully!")
        print(f"Backup saved at: {backup_path}")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def create_v2_schema(db_path: Path):
    """Create new v2 database schema."""
    conn = sqlite3.connect(db_path)
    try:
        schema_v2_path = Path(__file__).parent / "schema_v2.sql"
        with open(schema_v2_path, 'r') as f:
            schema_v2 = f.read()
        conn.executescript(schema_v2)
        conn.commit()
    finally:
        conn.close()


def _parse_int(value):
    """Parse integer value."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _parse_float(value):
    """Parse float value."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def test_migration():
    """Test the migrated database."""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("\n📊 Testing migrated database...")

    # Check daily_metrics
    cursor.execute("SELECT COUNT(*) as count FROM daily_metrics")
    daily_count = cursor.fetchone()['count']
    print(f"  - daily_metrics: {daily_count} records")

    # Check pages
    cursor.execute("SELECT COUNT(*) as count FROM pages")
    pages_count = cursor.fetchone()['count']
    print(f"  - pages: {pages_count} records")

    # Check fetch_log
    cursor.execute("SELECT COUNT(*) as count FROM fetch_log")
    fetch_count = cursor.fetchone()['count']
    print(f"  - fetch_log: {fetch_count} records")

    # Check weekly_metrics
    cursor.execute("SELECT COUNT(*) as count FROM weekly_metrics")
    weekly_count = cursor.fetchone()['count']
    print(f"  - weekly_metrics: {weekly_count} records")

    # Check monthly_metrics
    cursor.execute("SELECT COUNT(*) as count FROM monthly_metrics")
    monthly_count = cursor.fetchone()['count']
    print(f"  - monthly_metrics: {monthly_count} records")

    # Show sample data
    cursor.execute("SELECT metric_date, metric_name, sessions FROM daily_metrics LIMIT 5")
    samples = cursor.fetchall()
    if samples:
        print("\n  Sample records:")
        for s in samples:
            print(f"    {s['metric_date']}: {s['metric_name']} - {s['sessions']} sessions")

    conn.close()
    print("\n✅ Database verification complete")


if __name__ == "__main__":
    print("=== Clarity API Database Migration V1 → V2 ===\n")
    migrate_database()
    test_migration()
    print("\n✅ All done!")
