"""Main script to fetch all Clarity data and store it."""

import json
from pathlib import Path
from clarity_client import ClarityAPIClient
from database.db_manager import DatabaseManager
import config


def fetch_and_store_data(client: ClarityAPIClient, db: DatabaseManager,
                         num_days: int = 3,
                         dimension1: str = None,
                         dimension2: str = None,
                         dimension3: str = None,
                         filename: str = None) -> bool:
    """Fetch data from API and store in database and file.

    Args:
        client: ClarityAPIClient instance
        db: DatabaseManager instance
        num_days: Number of days to fetch
        dimension1: First dimension
        dimension2: Second dimension
        dimension3: Third dimension
        filename: Output filename for JSON

    Returns:
        True if successful, False otherwise
    """
    # Build dimension description
    dims = []
    if dimension1:
        dims.append(dimension1)
    if dimension2:
        dims.append(dimension2)
    if dimension3:
        dims.append(dimension3)
    dim_desc = " + ".join(dims) if dims else "No dimensions"

    print(f"\n{'='*60}")
    print(f"Fetching: {dim_desc} ({num_days} days)")
    print(f"{'='*60}")

    # Fetch from API
    result = client.fetch_project_insights(
        num_days=num_days,
        dimension1=dimension1,
        dimension2=dimension2,
        dimension3=dimension3
    )

    if not result['success']:
        print(f"❌ Failed to fetch data: {result.get('error')}")
        db.log_api_request(
            endpoint=config.API_ENDPOINT_PROJECT_INSIGHTS,
            num_days=num_days,
            dimension1=dimension1,
            dimension2=dimension2,
            dimension3=dimension3,
            status_code=result.get('status_code'),
            success=False,
            error_message=result.get('error')
        )
        return False

    # Save to JSON file
    if filename:
        client.save_response_to_file(result, filename)

    # Extract data
    data = result['data']

    # Count rows
    total_rows = 0
    for metric_group in data:
        total_rows += len(metric_group.get('information', []))

    print(f"📊 Received {len(data)} metric groups, {total_rows} total rows")

    # Insert into database
    inserted = db.insert_metrics(
        data,
        num_days=num_days,
        dimension1=dimension1,
        dimension2=dimension2,
        dimension3=dimension3
    )

    print(f"💾 Inserted {inserted} new records into database")

    # Log request
    db.log_api_request(
        endpoint=config.API_ENDPOINT_PROJECT_INSIGHTS,
        num_days=num_days,
        dimension1=dimension1,
        dimension2=dimension2,
        dimension3=dimension3,
        status_code=result['status_code'],
        success=True,
        response_size=result['response_size'],
        rows_returned=total_rows
    )

    print(f"✅ Success!")
    return True


def main():
    """Main execution function."""
    print("\n" + "="*60)
    print("CLARITY DATA COLLECTION - FULL RUN")
    print("="*60)
    print(f"Project: {config.CLARITY_PROJECT_ID}")
    print(f"Fetching last 3 days of data")
    print(f"API calls planned: 6")
    print("="*60)

    # Initialize
    config.ensure_directories()
    client = ClarityAPIClient()
    db = DatabaseManager()

    success_count = 0
    failed_count = 0

    # Collection plan
    collections = [
        {
            'name': 'Base Metrics',
            'dimension1': None,
            'dimension2': None,
            'dimension3': None,
            'filename': 'base_metrics_3days.json'
        },
        {
            'name': 'Device Breakdown',
            'dimension1': 'Device',
            'dimension2': None,
            'dimension3': None,
            'filename': 'by_device_3days.json'
        },
        {
            'name': 'Country Breakdown',
            'dimension1': 'Country',
            'dimension2': None,
            'dimension3': None,
            'filename': 'by_country_3days.json'
        },
        {
            'name': 'Browser Breakdown',
            'dimension1': 'Browser',
            'dimension2': None,
            'dimension3': None,
            'filename': 'by_browser_3days.json'
        },
        {
            'name': 'Device + Browser',
            'dimension1': 'Device',
            'dimension2': 'Browser',
            'dimension3': None,
            'filename': 'device_browser_3days.json'
        },
        {
            'name': 'Country + Device',
            'dimension1': 'Country',
            'dimension2': 'Device',
            'dimension3': None,
            'filename': 'country_device_3days.json'
        }
    ]

    # Execute collections
    for i, collection in enumerate(collections, 1):
        print(f"\n[{i}/{len(collections)}] {collection['name']}")
        success = fetch_and_store_data(
            client=client,
            db=db,
            num_days=3,
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
    print(f"   Unique dimensions: {stats['unique_dimension1_values']}")
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
