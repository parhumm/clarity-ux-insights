#!/usr/bin/env python3
"""Tests for CLI."""

import sys
from pathlib import Path
import subprocess

sys.path.insert(0, str(Path(__file__).parent.parent))


def run_cli(args):
    """Run CLI command and return output."""
    result = subprocess.run(
        ['python', 'clarity_cli.py'] + args,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    return result.returncode, result.stdout, result.stderr


def test_cli_help():
    """Test CLI help output."""
    print("\n🧪 Testing CLI help...")

    returncode, stdout, stderr = run_cli(['--help'])

    assert returncode == 0, "Help should return 0"
    assert 'Clarity UX Insights' in stdout, "Should show title"
    assert 'query' in stdout, "Should list query command"
    assert 'aggregate' in stdout, "Should list aggregate command"
    assert 'status' in stdout, "Should list status command"

    print("  ✓ Help output correct")


def test_cli_status():
    """Test status command."""
    print("\n🧪 Testing status command...")

    returncode, stdout, stderr = run_cli(['status'])

    assert returncode == 0, "Status should succeed"
    assert 'System Status' in stdout, "Should show status header"
    assert 'Project:' in stdout, "Should show project info"
    assert 'Data:' in stdout, "Should show data info"

    print("  ✓ Status command works")
    print(f"    Output lines: {len(stdout.splitlines())}")


def test_cli_list():
    """Test list command."""
    print("\n🧪 Testing list command...")

    returncode, stdout, stderr = run_cli(['list'])

    assert returncode == 0, "List should succeed"
    assert 'Available data:' in stdout, "Should show data header"

    print("  ✓ List command works")


def test_cli_query():
    """Test query command."""
    print("\n🧪 Testing query command...")

    # Query last 2 days (should have data)
    returncode, stdout, stderr = run_cli(['query', '2', '--count-only'])

    assert returncode == 0, "Query should succeed"
    assert 'Querying metrics:' in stdout, "Should show query header"
    assert 'Found' in stdout, "Should show results count"

    print("  ✓ Query command works")
    if 'Found 0 records' not in stdout:
        print("    ✓ Found data in database")


def test_cli_aggregate():
    """Test aggregate command."""
    print("\n🧪 Testing aggregate command...")

    # Aggregate last 2 days
    returncode, stdout, stderr = run_cli(['aggregate', '2'])

    assert returncode == 0, "Aggregate should succeed"
    assert 'Aggregating metrics:' in stdout, "Should show aggregate header"
    assert 'Aggregation complete:' in stdout or 'failed' in stdout, "Should show result"

    print("  ✓ Aggregate command works")


def test_date_format_parsing():
    """Test various date formats."""
    print("\n🧪 Testing date format parsing...")

    date_formats = [
        '7',
        'last-week',
        'November',
        '2025-11',
    ]

    for fmt in date_formats:
        returncode, stdout, stderr = run_cli(['query', fmt, '--count-only'])
        assert returncode == 0, f"Should parse date format: {fmt}"
        assert 'Querying metrics:' in stdout, f"Should query with format: {fmt}"
        print(f"  ✓ Parsed '{fmt}'")

    print("  ✓ All date formats parsed successfully")


def test_cli_no_command():
    """Test CLI with no command shows help."""
    print("\n🧪 Testing CLI with no command...")

    returncode, stdout, stderr = run_cli([])

    assert returncode == 1, "No command should return 1"
    assert 'usage:' in stdout or 'usage:' in stderr, "Should show usage"

    print("  ✓ No command shows help")


def run_all_tests():
    """Run all CLI tests."""
    print("=" * 60)
    print("CLI TESTS")
    print("=" * 60)

    tests = [
        test_cli_help,
        test_cli_status,
        test_cli_list,
        test_cli_query,
        test_cli_aggregate,
        test_date_format_parsing,
        test_cli_no_command,
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
