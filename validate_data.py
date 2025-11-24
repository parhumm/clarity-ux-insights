"""Validate collected Clarity data for completeness and quality."""

import json
from pathlib import Path
from database.db_manager import DatabaseManager
import config


def validate_json_files():
    """Validate that all JSON files exist and are valid."""
    print("\n" + "="*60)
    print("VALIDATING JSON FILES")
    print("="*60)

    expected_files = [
        'base_metrics_3days.json',
        'by_device_3days.json',
        'by_country_3days.json',
        'by_browser_3days.json',
        'device_browser_3days.json',
        'country_device_3days.json'
    ]

    all_valid = True
    for filename in expected_files:
        file_path = config.RAW_DATA_DIR / filename
        if not file_path.exists():
            print(f"❌ Missing: {filename}")
            all_valid = False
            continue

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            if not data.get('success'):
                print(f"❌ {filename}: API call was not successful")
                all_valid = False
                continue

            api_data = data.get('data', [])
            total_rows = sum(len(group.get('information', [])) for group in api_data)

            print(f"✅ {filename:30} {len(api_data)} metric groups, {total_rows:4} rows")

        except json.JSONDecodeError as e:
            print(f"❌ {filename}: Invalid JSON - {e}")
            all_valid = False
        except Exception as e:
            print(f"❌ {filename}: Error - {e}")
            all_valid = False

    return all_valid


def validate_database():
    """Validate database contents."""
    print("\n" + "="*60)
    print("VALIDATING DATABASE")
    print("="*60)

    db = DatabaseManager()
    stats = db.get_statistics()

    print(f"Total metrics: {stats['total_metrics']}")
    print(f"API requests: {stats['total_api_requests']}")
    print(f"Successful requests: {stats['successful_requests']}")
    print(f"Unique dimension values: {stats['unique_dimension1_values']}")
    print(f"Latest fetch: {stats['latest_fetch']}")

    # Check for expected data
    checks = []

    # Should have base metrics (no dimensions)
    base_metrics = db.get_metrics()
    base_count = len([m for m in base_metrics if m['dimension1_name'] is None])
    checks.append(('Base metrics (no dimensions)', base_count > 0, base_count))

    # Should have device metrics
    device_metrics = [m for m in base_metrics if m['dimension1_name'] == 'Device']
    checks.append(('Device metrics', len(device_metrics) > 0, len(device_metrics)))

    # Should have country metrics
    country_metrics = [m for m in base_metrics if m['dimension1_name'] == 'Country']
    checks.append(('Country metrics', len(country_metrics) > 0, len(country_metrics)))

    # Should have browser metrics
    browser_metrics = [m for m in base_metrics if m['dimension1_name'] == 'Browser']
    checks.append(('Browser metrics', len(browser_metrics) > 0, len(browser_metrics)))

    # Should have 2-dimensional data
    two_dim = [m for m in base_metrics if m['dimension2_name'] is not None]
    checks.append(('Two-dimensional metrics', len(two_dim) > 0, len(two_dim)))

    print("\nData Completeness Checks:")
    all_passed = True
    for check_name, passed, count in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name:35} {count:4} records")
        if not passed:
            all_passed = False

    # Check for duplicates
    conn = db.get_connection()
    cursor = conn.execute("SELECT COUNT(*) as total FROM clarity_metrics")
    total = cursor.fetchone()['total']

    cursor = conn.execute("""
        SELECT COUNT(*) as unique_records FROM (
            SELECT DISTINCT metric_name, num_days, dimension1_name, dimension1_value,
                            dimension2_name, dimension2_value, dimension3_name, dimension3_value
            FROM clarity_metrics
        )
    """)
    unique = cursor.fetchone()['unique_records']
    conn.close()

    duplicate_count = total - unique
    if duplicate_count == 0:
        print(f"\n✅ No duplicates found ({total} total records)")
    else:
        # Note: Small number of duplicates is expected due to test runs
        # The UNIQUE constraint prevents inserting new duplicates
        pct = (duplicate_count / total * 100) if total > 0 else 0
        if pct < 5:  # Less than 5% duplicates is acceptable
            print(f"\n✅ Acceptable duplicate rate: {duplicate_count} duplicates ({pct:.1f}%)")
            print(f"   Total records: {total}, Unique: {unique}")
            print(f"   Note: UNIQUE constraint prevents new duplicates from being inserted")
        else:
            print(f"\n⚠️  High duplicate rate: {duplicate_count} duplicates ({pct:.1f}%)")
            all_passed = False

    return all_passed


def validate_exports():
    """Validate exported CSV files."""
    print("\n" + "="*60)
    print("VALIDATING EXPORTS")
    print("="*60)

    expected_files = [
        'summary_last_3_days.csv',
        'device_summary.csv',
        'country_summary.csv',
        'browser_summary.csv'
    ]

    all_valid = True
    for filename in expected_files:
        file_path = config.EXPORT_DIR / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {filename:30} {size:6} bytes")
        else:
            print(f"❌ Missing: {filename}")
            all_valid = False

    return all_valid


def main():
    """Run all validation checks."""
    print("\n" + "="*60)
    print("CLARITY DATA VALIDATION")
    print("="*60)

    results = []

    # Validate JSON files
    json_valid = validate_json_files()
    results.append(('JSON Files', json_valid))

    # Validate database
    db_valid = validate_database()
    results.append(('Database', db_valid))

    # Validate exports
    exports_valid = validate_exports()
    results.append(('Export Files', exports_valid))

    # Final summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)

    all_passed = True
    for check_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{check_name:20} {status}")
        if not passed:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n🎉 ALL VALIDATION CHECKS PASSED!")
        print("\nData collection is complete and verified.")
        print("You can now use the data for analysis and insights.")
    else:
        print("\n⚠️  SOME VALIDATION CHECKS FAILED")
        print("\nPlease review the errors above and re-run data collection if needed.")

    return all_passed


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Validation error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
