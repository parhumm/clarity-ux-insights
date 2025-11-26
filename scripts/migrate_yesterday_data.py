#!/usr/bin/env python3
"""
Migrate yesterday's data from clarity_metrics to daily_metrics.
Properly parses the different metric structures.
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config

def extract_metric_values(metric_name, raw_json_str):
    """Extract metric values from raw JSON based on metric type."""
    try:
        info = json.loads(raw_json_str)
    except:
        return {}

    result = {
        'sessions': None,
        'users': None,
        'bot_sessions': None,
        'pages_per_session': None,
        'dead_clicks': None,
        'rage_clicks': None,
        'quick_backs': None,
        'error_clicks': None,
        'script_errors': None,
        'excessive_scrolls': None,
        'scroll_depth': None,
        'engagement_time': None,
        'active_time': None
    }

    # Traffic metric - main session/user data
    if 'totalSessionCount' in info:
        result['sessions'] = int(info['totalSessionCount']) if info['totalSessionCount'] else 0
        result['bot_sessions'] = int(info.get('totalBotSessionCount', 0)) if info.get('totalBotSessionCount') else 0
        result['users'] = int(info.get('distinctUserCount', 0)) if info.get('distinctUserCount') else 0
        result['pages_per_session'] = float(info.get('pagesPerSessionPercentage', 0)) if info.get('pagesPerSessionPercentage') else 0

    # Frustration metrics - have sessionsCount and subTotal
    if 'sessionsCount' in info:
        base_sessions = int(info['sessionsCount']) if info['sessionsCount'] else 0
        subtotal = int(info.get('subTotal', 0)) if info.get('subTotal') else 0

        if metric_name == 'DeadClickCount':
            result['sessions'] = base_sessions
            result['dead_clicks'] = subtotal
        elif metric_name == 'RageClickCount':
            result['sessions'] = base_sessions
            result['rage_clicks'] = subtotal
        elif metric_name == 'QuickbackClick':
            result['sessions'] = base_sessions
            result['quick_backs'] = subtotal
        elif metric_name == 'ErrorClickCount':
            result['sessions'] = base_sessions
            result['error_clicks'] = subtotal
        elif metric_name == 'ScriptErrorCount':
            result['sessions'] = base_sessions
            result['script_errors'] = subtotal
        elif metric_name == 'ExcessiveScroll':
            result['sessions'] = base_sessions
            result['excessive_scrolls'] = subtotal

    # Scroll depth
    if 'averageScrollDepth' in info:
        result['scroll_depth'] = float(info['averageScrollDepth'])

    # Engagement time
    if 'totalTime' in info:
        result['engagement_time'] = float(info.get('totalTime', 0))
    if 'activeTime' in info:
        result['active_time'] = float(info.get('activeTime', 0))

    return result

def main():
    """Migrate data from clarity_metrics to daily_metrics."""
    print("="*60)
    print("MIGRATING YESTERDAY'S DATA")
    print("="*60)

    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all records from clarity_metrics
    cursor.execute("""
        SELECT * FROM clarity_metrics
        WHERE DATE(fetch_timestamp) = DATE('now')
        ORDER BY metric_name, dimension1_name, dimension1_value
    """)

    records = cursor.fetchall()
    print(f"\nFound {len(records)} records to migrate")

    inserted = 0
    skipped = 0

    for record in records:
        # Extract values from JSON
        values = extract_metric_values(record['metric_name'], record['raw_json'] or '{}')

        # Skip if no useful data
        if all(v is None or v == 0 for v in values.values()):
            skipped += 1
            continue

        try:
            cursor.execute("""
                INSERT INTO daily_metrics (
                    metric_date, fetch_timestamp, metric_name, data_scope,
                    dimension1_name, dimension1_value,
                    dimension2_name, dimension2_value,
                    dimension3_name, dimension3_value,
                    sessions, users, bot_sessions, pages_per_session,
                    dead_clicks, rage_clicks, quick_backs,
                    error_clicks, script_errors, excessive_scrolls,
                    scroll_depth, engagement_time, active_time,
                    source_file, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record['fetch_timestamp'][:10],  # metric_date
                record['fetch_timestamp'],
                record['metric_name'],
                'general',
                record['dimension1_name'],
                record['dimension1_value'],
                record['dimension2_name'],
                record['dimension2_value'],
                record['dimension3_name'],
                record['dimension3_value'],
                values['sessions'],
                values['users'],
                values['bot_sessions'],
                values['pages_per_session'],
                values['dead_clicks'],
                values['rage_clicks'],
                values['quick_backs'],
                values['error_clicks'],
                values['script_errors'],
                values['excessive_scrolls'],
                values['scroll_depth'],
                values['engagement_time'],
                values['active_time'],
                'API',
                record['raw_json']
            ))
            inserted += 1
        except sqlite3.IntegrityError as e:
            print(f"  Duplicate: {record['metric_name']}")
            skipped += 1

    conn.commit()

    print(f"\n✓ Migrated {inserted} records")
    print(f"  Skipped {skipped} records")

    # Summary
    cursor.execute("SELECT metric_date, COUNT(*) FROM daily_metrics GROUP BY metric_date")
    print(f"\n📊 Database Summary:")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} records")

    # Check Traffic metric
    cursor.execute("""
        SELECT SUM(sessions) as total_sessions, SUM(users) as total_users
        FROM daily_metrics
        WHERE metric_name = 'Traffic' AND metric_date = DATE('now')
    """)
    row = cursor.fetchone()
    print(f"\n✓ Traffic Data:")
    print(f"   Total Sessions: {row[0]}")
    print(f"   Total Users: {row[1]}")

    conn.close()
    print("\n" + "="*60)
    print("MIGRATION COMPLETE")
    print("="*60)

if __name__ == '__main__':
    main()
