#!/usr/bin/env python3
"""
Cleanup script to remove all Televik data and reports.
This script will:
1. Delete all records from database tables
2. Remove all raw JSON files
3. Remove all generated reports
4. Keep database backups
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DATA_DIR, DB_PATH, PROJECT_ROOT

# Reports directory
REPORTS_DIR = PROJECT_ROOT / "reports"

def cleanup_database():
    """Delete all records from database tables."""
    print("🗄️  Cleaning up database...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tables_to_clean = [
        'daily_metrics',
        'weekly_metrics',
        'monthly_metrics',
        'fetch_log',
        'archive_log',
        'pages',
        'clarity_metrics',  # old schema
        'api_requests'      # old schema
    ]

    for table in tables_to_clean:
        try:
            cursor.execute(f"DELETE FROM {table}")
            deleted = cursor.rowcount
            print(f"  ✓ Deleted {deleted} records from {table}")
        except sqlite3.OperationalError as e:
            print(f"  ⚠ Warning: Could not clean {table}: {e}")

    conn.commit()
    conn.close()
    print("  ✓ Database cleanup complete\n")

def cleanup_raw_files():
    """Remove all raw JSON files."""
    print("📁 Cleaning up raw JSON files...")

    raw_dir = DATA_DIR / 'raw'
    if not raw_dir.exists():
        print("  ℹ No raw directory found\n")
        return

    deleted_count = 0
    for file in raw_dir.glob('*.json'):
        file.unlink()
        print(f"  ✓ Deleted {file.name}")
        deleted_count += 1

    print(f"  ✓ Deleted {deleted_count} raw JSON files\n")

def cleanup_reports():
    """Remove all generated reports."""
    print("📊 Cleaning up generated reports...")

    report_dirs = [
        REPORTS_DIR / 'general',
        REPORTS_DIR / 'pages'
    ]

    total_deleted = 0
    for report_dir in report_dirs:
        if not report_dir.exists():
            print(f"  ℹ No {report_dir.name} directory found")
            continue

        deleted_count = 0
        for file in report_dir.glob('*.md'):
            file.unlink()
            deleted_count += 1

        print(f"  ✓ Deleted {deleted_count} reports from {report_dir.name}/")
        total_deleted += deleted_count

    print(f"  ✓ Deleted {total_deleted} total reports\n")

def main():
    """Main cleanup function."""
    print("=" * 60)
    print("🧹 TELEVIK DATA CLEANUP")
    print("=" * 60)
    print()

    # Confirm with user
    print("⚠️  WARNING: This will delete ALL data and reports!")
    print("  - All database records")
    print("  - All raw JSON files")
    print("  - All generated reports")
    print()
    response = input("Are you sure you want to continue? (yes/no): ")

    if response.lower() != 'yes':
        print("\n❌ Cleanup cancelled")
        return

    print("\n🚀 Starting cleanup...\n")

    # Execute cleanup
    cleanup_database()
    cleanup_raw_files()
    cleanup_reports()

    print("=" * 60)
    print("✅ CLEANUP COMPLETE")
    print("=" * 60)
    print("\nAll Televik data and reports have been removed.")
    print("Database backups have been preserved.")

if __name__ == '__main__':
    main()
