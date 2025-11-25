#!/usr/bin/env python3
"""
Archive manager for data retention and cleanup.
Manages old data by archiving and removing from active database.
"""

import sys
import json
import csv
from pathlib import Path
from datetime import date, timedelta
from typing import Dict, List, Optional, Any
import sqlite3

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.query_engine import QueryEngine
from config_loader import load_config


class ArchiveManager:
    """Manage data archiving and retention."""

    def __init__(self):
        """Initialize archive manager."""
        self.query_engine = QueryEngine()
        try:
            self.config = load_config()
            self.retention_days = self.config.data.retention_days
        except:
            self.config = None
            self.retention_days = 90  # Default

        self.archive_dir = Path(__file__).parent.parent / "archive"
        self.archive_dir.mkdir(exist_ok=True)

    def identify_old_data(self, reference_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Identify data older than retention period.

        Args:
            reference_date: Reference date (defaults to today)

        Returns:
            Info about old data
        """
        if reference_date is None:
            reference_date = date.today()

        cutoff_date = reference_date - timedelta(days=self.retention_days)

        conn = self.query_engine.get_connection()

        # Count old records in daily_metrics
        cursor = conn.execute("""
            SELECT COUNT(*) as count
            FROM daily_metrics
            WHERE metric_date < ?
        """, (cutoff_date.isoformat(),))
        daily_count = cursor.fetchone()['count']

        # Get date range of old data
        cursor = conn.execute("""
            SELECT MIN(metric_date) as min_date, MAX(metric_date) as max_date
            FROM daily_metrics
            WHERE metric_date < ?
        """, (cutoff_date.isoformat(),))
        date_range = cursor.fetchone()

        # Count by metric type
        cursor = conn.execute("""
            SELECT metric_name, COUNT(*) as count
            FROM daily_metrics
            WHERE metric_date < ?
            GROUP BY metric_name
        """, (cutoff_date.isoformat(),))
        by_metric = {row['metric_name']: row['count'] for row in cursor.fetchall()}

        conn.close()

        return {
            'cutoff_date': cutoff_date.isoformat(),
            'retention_days': self.retention_days,
            'total_records': daily_count,
            'date_range': {
                'min': date_range['min_date'],
                'max': date_range['max_date']
            } if date_range['min_date'] else None,
            'by_metric': by_metric
        }

    def archive_old_data(
        self,
        reference_date: Optional[date] = None,
        format: str = 'json',
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Archive old data to files.

        Args:
            reference_date: Reference date (defaults to today)
            format: Archive format ('json' or 'csv')
            dry_run: If True, don't actually archive (just show what would happen)

        Returns:
            Archiving results
        """
        if reference_date is None:
            reference_date = date.today()

        cutoff_date = reference_date - timedelta(days=self.retention_days)

        # Identify old data
        old_data_info = self.identify_old_data(reference_date)

        if old_data_info['total_records'] == 0:
            return {
                'status': 'no_data',
                'message': 'No data to archive',
                'cutoff_date': cutoff_date.isoformat()
            }

        if dry_run:
            return {
                'status': 'dry_run',
                'would_archive': old_data_info['total_records'],
                'cutoff_date': cutoff_date.isoformat(),
                'date_range': old_data_info['date_range'],
                'by_metric': old_data_info['by_metric']
            }

        # Export old data
        conn = self.query_engine.get_connection()
        cursor = conn.execute("""
            SELECT *
            FROM daily_metrics
            WHERE metric_date < ?
            ORDER BY metric_date
        """, (cutoff_date.isoformat(),))

        records = [dict(row) for row in cursor.fetchall()]

        # Create archive file
        timestamp = reference_date.isoformat()
        archive_file = self.archive_dir / f"archive_{timestamp}.{format}"

        if format == 'json':
            with open(archive_file, 'w') as f:
                json.dump(records, f, indent=2)
        elif format == 'csv':
            if records:
                with open(archive_file, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=records[0].keys())
                    writer.writeheader()
                    writer.writerows(records)

        conn.close()

        return {
            'status': 'success',
            'archived_records': len(records),
            'archive_file': str(archive_file),
            'cutoff_date': cutoff_date.isoformat(),
            'date_range': old_data_info['date_range'],
            'by_metric': old_data_info['by_metric']
        }

    def delete_old_data(
        self,
        reference_date: Optional[date] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Delete old data from database.

        Args:
            reference_date: Reference date (defaults to today)
            dry_run: If True, don't actually delete (just show what would happen)

        Returns:
            Deletion results
        """
        if reference_date is None:
            reference_date = date.today()

        cutoff_date = reference_date - timedelta(days=self.retention_days)

        # Identify old data
        old_data_info = self.identify_old_data(reference_date)

        if old_data_info['total_records'] == 0:
            return {
                'status': 'no_data',
                'message': 'No data to delete',
                'cutoff_date': cutoff_date.isoformat()
            }

        if dry_run:
            return {
                'status': 'dry_run',
                'would_delete': old_data_info['total_records'],
                'cutoff_date': cutoff_date.isoformat(),
                'date_range': old_data_info['date_range']
            }

        # Delete old records
        conn = self.query_engine.get_connection()
        cursor = conn.execute("""
            DELETE FROM daily_metrics
            WHERE metric_date < ?
        """, (cutoff_date.isoformat(),))

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        return {
            'status': 'success',
            'deleted_records': deleted_count,
            'cutoff_date': cutoff_date.isoformat(),
            'date_range': old_data_info['date_range']
        }

    def archive_and_delete(
        self,
        reference_date: Optional[date] = None,
        format: str = 'json',
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Archive old data and then delete from database.

        Args:
            reference_date: Reference date (defaults to today)
            format: Archive format ('json' or 'csv')
            dry_run: If True, don't actually archive/delete

        Returns:
            Combined results
        """
        # Archive first
        archive_result = self.archive_old_data(reference_date, format, dry_run)

        if archive_result['status'] != 'success':
            return archive_result

        # Then delete
        delete_result = self.delete_old_data(reference_date, dry_run)

        return {
            'status': 'success',
            'archived_records': archive_result['archived_records'],
            'deleted_records': delete_result['deleted_records'],
            'archive_file': archive_result['archive_file'],
            'cutoff_date': archive_result['cutoff_date']
        }

    def list_archives(self) -> List[Dict[str, Any]]:
        """List all archive files."""
        archives = []

        for archive_file in sorted(self.archive_dir.glob("archive_*.json")):
            archives.append({
                'file': archive_file.name,
                'path': str(archive_file),
                'size': archive_file.stat().st_size,
                'format': 'json'
            })

        for archive_file in sorted(self.archive_dir.glob("archive_*.csv")):
            archives.append({
                'file': archive_file.name,
                'path': str(archive_file),
                'size': archive_file.stat().st_size,
                'format': 'csv'
            })

        return archives

    def restore_archive(
        self,
        archive_file: Path,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Restore data from an archive file.

        Args:
            archive_file: Path to archive file
            dry_run: If True, don't actually restore

        Returns:
            Restore results
        """
        if not archive_file.exists():
            return {
                'status': 'error',
                'message': f'Archive file not found: {archive_file}'
            }

        # Load archive
        if archive_file.suffix == '.json':
            with open(archive_file, 'r') as f:
                records = json.load(f)
        elif archive_file.suffix == '.csv':
            with open(archive_file, 'r') as f:
                reader = csv.DictReader(f)
                records = list(reader)
        else:
            return {
                'status': 'error',
                'message': f'Unsupported format: {archive_file.suffix}'
            }

        if dry_run:
            return {
                'status': 'dry_run',
                'would_restore': len(records),
                'archive_file': str(archive_file)
            }

        # Restore to database
        conn = self.query_engine.get_connection()

        restored = 0
        for record in records:
            try:
                # Try to insert (ignore if already exists)
                conn.execute("""
                    INSERT OR IGNORE INTO daily_metrics
                    (metric_date, metric_name, data_scope, page_id, sessions, users,
                     page_views, mobile_sessions, desktop_sessions, tablet_sessions,
                     dead_clicks, rage_clicks, quick_backs, error_clicks,
                     avg_scroll_depth, avg_time_on_page, avg_active_time,
                     total_session_time, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.get('metric_date'),
                    record.get('metric_name'),
                    record.get('data_scope'),
                    record.get('page_id'),
                    record.get('sessions'),
                    record.get('users'),
                    record.get('page_views'),
                    record.get('mobile_sessions'),
                    record.get('desktop_sessions'),
                    record.get('tablet_sessions'),
                    record.get('dead_clicks'),
                    record.get('rage_clicks'),
                    record.get('quick_clicks'),
                    record.get('error_clicks'),
                    record.get('avg_scroll_depth'),
                    record.get('avg_time_on_page'),
                    record.get('avg_active_time'),
                    record.get('total_session_time'),
                    record.get('created_at')
                ))
                if conn.total_changes > 0:
                    restored += 1
            except Exception as e:
                print(f"Warning: Could not restore record: {e}")

        conn.commit()
        conn.close()

        return {
            'status': 'success',
            'restored_records': restored,
            'archive_file': str(archive_file),
            'skipped': len(records) - restored
        }


def main():
    """CLI interface for archive manager."""
    import argparse

    parser = argparse.ArgumentParser(description="Manage data archiving and retention")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Check command
    check_parser = subparsers.add_parser('check', help='Check for old data')
    check_parser.add_argument('--date', help='Reference date (YYYY-MM-DD)')

    # Archive command
    archive_parser = subparsers.add_parser('archive', help='Archive old data')
    archive_parser.add_argument('--date', help='Reference date (YYYY-MM-DD)')
    archive_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Archive format')
    archive_parser.add_argument('--dry-run', action='store_true', help='Dry run (don\'t actually archive)')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete old data')
    delete_parser.add_argument('--date', help='Reference date (YYYY-MM-DD)')
    delete_parser.add_argument('--dry-run', action='store_true', help='Dry run (don\'t actually delete)')

    # Archive and delete command
    cleanup_parser = subparsers.add_parser('cleanup', help='Archive and delete old data')
    cleanup_parser.add_argument('--date', help='Reference date (YYYY-MM-DD)')
    cleanup_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Archive format')
    cleanup_parser.add_argument('--dry-run', action='store_true', help='Dry run')

    # List archives command
    list_parser = subparsers.add_parser('list', help='List archive files')

    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from archive')
    restore_parser.add_argument('archive_file', help='Archive file to restore')
    restore_parser.add_argument('--dry-run', action='store_true', help='Dry run')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    manager = ArchiveManager()

    # Parse date if provided
    ref_date = None
    if hasattr(args, 'date') and args.date:
        ref_date = date.fromisoformat(args.date)

    # Execute command
    if args.command == 'check':
        result = manager.identify_old_data(ref_date)
        print(f"\n📊 Old Data Check")
        print(f"Retention Period: {result['retention_days']} days")
        print(f"Cutoff Date: {result['cutoff_date']}")
        print(f"Total Records: {result['total_records']:,}")
        if result.get('date_range'):
            print(f"Date Range: {result['date_range']['min']} to {result['date_range']['max']}")
        if result.get('by_metric'):
            print("\nBy Metric:")
            for metric, count in result['by_metric'].items():
                print(f"  {metric}: {count:,}")

    elif args.command == 'archive':
        result = manager.archive_old_data(ref_date, args.format, args.dry_run)
        if result['status'] == 'dry_run':
            print(f"\n🔍 Dry Run: Would archive {result['would_archive']:,} records")
            print(f"Cutoff: {result['cutoff_date']}")
        elif result['status'] == 'success':
            print(f"\n✓ Archived {result['archived_records']:,} records")
            print(f"File: {result['archive_file']}")
        else:
            print(f"\n{result['message']}")

    elif args.command == 'delete':
        result = manager.delete_old_data(ref_date, args.dry_run)
        if result['status'] == 'dry_run':
            print(f"\n🔍 Dry Run: Would delete {result['would_delete']:,} records")
        elif result['status'] == 'success':
            print(f"\n✓ Deleted {result['deleted_records']:,} records")
        else:
            print(f"\n{result['message']}")

    elif args.command == 'cleanup':
        result = manager.archive_and_delete(ref_date, args.format, args.dry_run)
        if result['status'] == 'success':
            print(f"\n✓ Cleanup complete:")
            print(f"  Archived: {result['archived_records']:,} records")
            print(f"  Deleted: {result['deleted_records']:,} records")
            print(f"  File: {result['archive_file']}")
        else:
            print(f"\n{result.get('message', 'No data to process')}")

    elif args.command == 'list':
        archives = manager.list_archives()
        print(f"\n📁 Archive Files: {len(archives)}")
        for archive in archives:
            size_mb = archive['size'] / (1024 * 1024)
            print(f"  {archive['file']} ({size_mb:.2f} MB)")

    elif args.command == 'restore':
        archive_path = Path(args.archive_file)
        result = manager.restore_archive(archive_path, args.dry_run)
        if result['status'] == 'dry_run':
            print(f"\n🔍 Dry Run: Would restore {result['would_restore']:,} records")
        elif result['status'] == 'success':
            print(f"\n✓ Restored {result['restored_records']:,} records")
            if result['skipped'] > 0:
                print(f"  Skipped {result['skipped']:,} duplicates")
        else:
            print(f"\n❌ Error: {result['message']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
