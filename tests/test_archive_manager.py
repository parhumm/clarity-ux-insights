#!/usr/bin/env python3
"""Tests for archive manager."""

import sys
from pathlib import Path
from datetime import date, timedelta
import json
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.archive_manager import ArchiveManager


def test_archive_manager_initialization():
    """Test that archive manager initializes correctly."""
    print("\n🧪 Testing archive manager initialization...")

    manager = ArchiveManager()

    assert manager.query_engine is not None, "Query engine not initialized"
    assert manager.retention_days > 0, "Retention days not set"
    assert manager.archive_dir.exists(), "Archive directory not created"

    print(f"  ✓ Archive manager initialized")
    print(f"  ✓ Retention period: {manager.retention_days} days")
    print(f"  ✓ Archive directory: {manager.archive_dir}")


def test_identify_old_data():
    """Test identifying old data."""
    print("\n🧪 Testing old data identification...")

    manager = ArchiveManager()

    # Use a future reference date to make all data "old"
    reference_date = date.today() + timedelta(days=manager.retention_days + 10)

    old_data_info = manager.identify_old_data(reference_date)

    assert 'cutoff_date' in old_data_info, "Cutoff date missing"
    assert 'retention_days' in old_data_info, "Retention days missing"
    assert 'total_records' in old_data_info, "Total records missing"

    print(f"  ✓ Cutoff date: {old_data_info['cutoff_date']}")
    print(f"  ✓ Retention: {old_data_info['retention_days']} days")
    print(f"  ✓ Old records found: {old_data_info['total_records']:,}")

    if old_data_info.get('date_range'):
        print(f"  ✓ Date range: {old_data_info['date_range']['min']} to {old_data_info['date_range']['max']}")


def test_archive_old_data_dry_run():
    """Test archiving with dry run."""
    print("\n🧪 Testing archive dry run...")

    manager = ArchiveManager()

    # Use future reference to make data "old"
    reference_date = date.today() + timedelta(days=manager.retention_days + 10)

    result = manager.archive_old_data(reference_date, format='json', dry_run=True)

    if result['status'] == 'no_data':
        print("  ⚠ No old data to archive (expected for fresh database)")
    elif result['status'] == 'dry_run':
        assert 'would_archive' in result, "Would archive count missing"
        print(f"  ✓ Dry run successful")
        print(f"  ✓ Would archive: {result['would_archive']:,} records")
        print(f"  ✓ Cutoff: {result['cutoff_date']}")


def test_delete_old_data_dry_run():
    """Test deletion with dry run."""
    print("\n🧪 Testing delete dry run...")

    manager = ArchiveManager()

    # Use future reference to make data "old"
    reference_date = date.today() + timedelta(days=manager.retention_days + 10)

    result = manager.delete_old_data(reference_date, dry_run=True)

    if result['status'] == 'no_data':
        print("  ⚠ No old data to delete (expected for fresh database)")
    elif result['status'] == 'dry_run':
        assert 'would_delete' in result, "Would delete count missing"
        print(f"  ✓ Dry run successful")
        print(f"  ✓ Would delete: {result['would_delete']:,} records")
        print(f"  ✓ Cutoff: {result['cutoff_date']}")


def test_archive_formats():
    """Test both JSON and CSV archive formats."""
    print("\n🧪 Testing archive formats...")

    manager = ArchiveManager()

    # Test with future date
    reference_date = date.today() + timedelta(days=manager.retention_days + 10)

    # Test JSON format (dry run)
    json_result = manager.archive_old_data(reference_date, format='json', dry_run=True)
    print(f"  ✓ JSON format supported")

    # Test CSV format (dry run)
    csv_result = manager.archive_old_data(reference_date, format='csv', dry_run=True)
    print(f"  ✓ CSV format supported")

    # Both should have same record count
    if json_result['status'] == 'dry_run' and csv_result['status'] == 'dry_run':
        assert json_result['would_archive'] == csv_result['would_archive'], \
            "Format results should match"
        print(f"  ✓ Both formats would archive same count")


def test_list_archives():
    """Test listing archive files."""
    print("\n🧪 Testing archive listing...")

    manager = ArchiveManager()

    archives = manager.list_archives()

    assert isinstance(archives, list), "Archives not a list"

    print(f"  ✓ List archives working")
    print(f"  ✓ Found {len(archives)} archive files")

    for archive in archives[:3]:  # Show first 3
        size_mb = archive['size'] / (1024 * 1024)
        print(f"    - {archive['file']} ({size_mb:.2f} MB)")


def test_archive_and_delete_workflow():
    """Test the full archive and delete workflow (dry run)."""
    print("\n🧪 Testing archive and delete workflow...")

    manager = ArchiveManager()

    # Use future reference date
    reference_date = date.today() + timedelta(days=manager.retention_days + 10)

    # Test combined operation (dry run)
    result = manager.archive_and_delete(reference_date, format='json', dry_run=True)

    assert result['status'] in ['success', 'no_data', 'dry_run'], f"Unexpected status: {result['status']}"

    if result['status'] == 'success':
        print(f"  ✓ Workflow dry run successful")
        print(f"  ✓ Would archive: {result.get('archived_records', 0):,}")
        print(f"  ✓ Would delete: {result.get('deleted_records', 0):,}")
    elif result['status'] == 'dry_run':
        print(f"  ✓ Dry run successful")
        print(f"  ✓ Would archive: {result.get('would_archive', 0):,}")
    else:
        print("  ⚠ No old data (expected for fresh database)")


def test_cutoff_date_calculation():
    """Test cutoff date calculation."""
    print("\n🧪 Testing cutoff date calculation...")

    manager = ArchiveManager()

    reference = date(2025, 11, 25)
    expected_cutoff = reference - timedelta(days=manager.retention_days)

    old_data_info = manager.identify_old_data(reference)
    actual_cutoff = date.fromisoformat(old_data_info['cutoff_date'])

    assert actual_cutoff == expected_cutoff, "Cutoff date calculation incorrect"

    print(f"  ✓ Reference date: {reference}")
    print(f"  ✓ Retention: {manager.retention_days} days")
    print(f"  ✓ Cutoff date: {actual_cutoff}")
    print(f"  ✓ Calculation correct")


def run_all_tests():
    """Run all archive manager tests."""
    print("=" * 60)
    print("ARCHIVE MANAGER TESTS")
    print("=" * 60)

    tests = [
        test_archive_manager_initialization,
        test_identify_old_data,
        test_archive_old_data_dry_run,
        test_delete_old_data_dry_run,
        test_archive_formats,
        test_list_archives,
        test_archive_and_delete_workflow,
        test_cutoff_date_calculation,
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
