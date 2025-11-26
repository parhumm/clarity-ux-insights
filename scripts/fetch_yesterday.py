#!/usr/bin/env python3
"""
Fetch yesterday's data only from Clarity API.
Uses num_days=1 to minimize API calls and reduce rate limit impact.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fetch_clarity_data import fetch_and_store_data
from clarity_client import ClarityAPIClient
from database.db_manager import DatabaseManager
import config

def main():
    """Fetch yesterday's data only (1 day)."""
    print("\n" + "="*60)
    print("FETCHING YESTERDAY'S TELEVIKA DATA")
    print("="*60)
    print(f"Project: {config.CLARITY_PROJECT_ID}")
    print(f"Fetching: Yesterday only (1 day)")
    print(f"API calls planned: 6 (one per dimension)")
    print("="*60)

    # Initialize
    config.ensure_directories()
    client = ClarityAPIClient()
    db = DatabaseManager()

    success_count = 0
    failed_count = 0

    # Collection plan - all 6 dimensions
    collections = [
        {
            'name': 'Base Metrics',
            'dimension1': None,
            'dimension2': None,
            'dimension3': None,
            'filename': 'base_metrics_1day.json'
        },
        {
            'name': 'Device Breakdown',
            'dimension1': 'Device',
            'dimension2': None,
            'dimension3': None,
            'filename': 'by_device_1day.json'
        },
        {
            'name': 'Country Breakdown',
            'dimension1': 'Country',
            'dimension2': None,
            'dimension3': None,
            'filename': 'by_country_1day.json'
        },
        {
            'name': 'Browser Breakdown',
            'dimension1': 'Browser',
            'dimension2': None,
            'dimension3': None,
            'filename': 'by_browser_1day.json'
        },
        {
            'name': 'Device + Browser',
            'dimension1': 'Device',
            'dimension2': 'Browser',
            'dimension3': None,
            'filename': 'device_browser_1day.json'
        },
        {
            'name': 'Country + Device',
            'dimension1': 'Country',
            'dimension2': 'Device',
            'dimension3': None,
            'filename': 'country_device_1day.json'
        }
    ]

    # Execute collections
    for i, collection in enumerate(collections, 1):
        print(f"\n[{i}/{len(collections)}] {collection['name']}")
        success = fetch_and_store_data(
            client=client,
            db=db,
            num_days=1,  # ONLY 1 DAY (yesterday)
            dimension1=collection['dimension1'],
            dimension2=collection['dimension2'],
            dimension3=collection['dimension3'],
            filename=collection['filename']
        )

        if success:
            success_count += 1
        else:
            failed_count += 1

        # Small delay between requests
        if i < len(collections):
            print("⏱️  Waiting 2 seconds before next request...")
            import time
            time.sleep(2)

    # Final summary
    print("\n" + "="*60)
    print("DATA COLLECTION COMPLETE")
    print("="*60)
    print(f"✅ Successful: {success_count}/{len(collections)}")
    print(f"❌ Failed: {failed_count}/{len(collections)}")

    # Database statistics
    stats = db.get_statistics()
    print(f"\n📊 DATABASE STATISTICS:")
    print(f"   Total metrics: {stats['total_metrics']}")
    print(f"   API requests: {stats['total_api_requests']}")
    print(f"   Successful requests: {stats['successful_requests']}")
    print(f"   Latest fetch: {stats['latest_fetch']}")

    # Show data directory
    print(f"\n📁 DATA SAVED TO:")
    print(f"   JSON files: {config.RAW_DATA_DIR}")
    print(f"   Database: {config.DB_PATH}")

    print("\n" + "="*60)

    return success_count == len(collections)


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
