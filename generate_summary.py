"""Generate summary report from collected Clarity data."""

import pandas as pd
from database.db_manager import DatabaseManager
import config
from pathlib import Path


def generate_summary_report():
    """Generate comprehensive summary report from database."""
    print("\n" + "="*60)
    print("GENERATING SUMMARY REPORT")
    print("="*60)

    db = DatabaseManager()

    # Get all metrics
    print("\n📊 Extracting data from database...")
    metrics = db.get_metrics()
    print(f"   Retrieved {len(metrics)} records")

    if not metrics:
        print("❌ No data found in database!")
        return False

    # Convert to DataFrame
    df = pd.DataFrame(metrics)

    # Generate overall statistics
    print("\n" + "="*60)
    print("OVERALL STATISTICS")
    print("="*60)

    total_sessions = df[df['total_session_count'].notna()]['total_session_count'].sum()
    total_bot_sessions = df[df['total_bot_session_count'].notna()]['total_bot_session_count'].sum()
    total_users = df[df['distinct_user_count'].notna()]['distinct_user_count'].max()

    print(f"Total Sessions: {int(total_sessions):,}")
    print(f"Bot Sessions: {int(total_bot_sessions):,}")
    print(f"Distinct Users: {int(total_users):,}")
    print(f"Avg Pages/Session: {df['pages_per_session'].mean():.2f}")

    # Device breakdown
    print("\n" + "="*60)
    print("DEVICE BREAKDOWN")
    print("="*60)

    device_df = df[df['dimension1_name'] == 'Device'].copy()
    if not device_df.empty:
        device_summary = device_df.groupby('dimension1_value').agg({
            'total_session_count': 'sum',
            'distinct_user_count': 'sum',
            'pages_per_session': 'mean'
        }).sort_values('total_session_count', ascending=False)

        for device, row in device_summary.iterrows():
            sessions = int(row['total_session_count'])
            users = int(row['distinct_user_count'])
            pps = row['pages_per_session']
            pct = (sessions / device_summary['total_session_count'].sum() * 100)
            print(f"{device:12} {sessions:6,} sessions ({pct:5.1f}%) | {users:6,} users | {pps:.2f} pages/session")

    # Country breakdown (top 10)
    print("\n" + "="*60)
    print("TOP 10 COUNTRIES")
    print("="*60)

    country_df = df[df['dimension1_name'] == 'Country'].copy()
    if not country_df.empty:
        country_summary = country_df.groupby('dimension1_value').agg({
            'total_session_count': 'sum',
            'distinct_user_count': 'sum'
        }).sort_values('total_session_count', ascending=False).head(10)

        for i, (country, row) in enumerate(country_summary.iterrows(), 1):
            sessions = int(row['total_session_count'])
            users = int(row['distinct_user_count'])
            pct = (sessions / country_summary['total_session_count'].sum() * 100)
            print(f"{i:2}. {country:25} {sessions:5,} sessions ({pct:5.1f}%) | {users:5,} users")

    # Browser breakdown
    print("\n" + "="*60)
    print("BROWSER BREAKDOWN")
    print("="*60)

    browser_df = df[df['dimension1_name'] == 'Browser'].copy()
    if not browser_df.empty:
        browser_summary = browser_df.groupby('dimension1_value').agg({
            'total_session_count': 'sum',
            'distinct_user_count': 'sum'
        }).sort_values('total_session_count', ascending=False).head(10)

        for browser, row in browser_summary.iterrows():
            sessions = int(row['total_session_count'])
            users = int(row['distinct_user_count'])
            pct = (sessions / browser_summary['total_session_count'].sum() * 100)
            print(f"{browser:20} {sessions:5,} sessions ({pct:5.1f}%) | {users:5,} users")

    # Metric types from base data
    print("\n" + "="*60)
    print("FRUSTRATION & BEHAVIOR METRICS (Base Data)")
    print("="*60)

    base_df = df[df['dimension1_name'].isna()].copy()
    if not base_df.empty:
        for metric_name in base_df['metric_name'].unique():
            metric_data = base_df[base_df['metric_name'] == metric_name]
            if not metric_data.empty:
                raw_json = metric_data.iloc[0]['raw_json']
                if raw_json:
                    import json
                    data = json.loads(raw_json)
                    print(f"\n{metric_name}:")
                    for key, value in data.items():
                        if key not in ['Device', 'Country', 'Browser']:
                            print(f"  {key}: {value}")

    # Export to CSV
    print("\n" + "="*60)
    print("EXPORTING DATA")
    print("="*60)

    export_dir = config.EXPORT_DIR
    export_dir.mkdir(parents=True, exist_ok=True)

    # Export full data
    csv_path = export_dir / "summary_last_3_days.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ Full data exported to: {csv_path}")

    # Export device summary
    if not device_df.empty:
        device_csv = export_dir / "device_summary.csv"
        device_summary.to_csv(device_csv)
        print(f"✅ Device summary exported to: {device_csv}")

    # Export country summary
    if not country_df.empty:
        country_csv = export_dir / "country_summary.csv"
        country_summary.to_csv(country_csv)
        print(f"✅ Country summary exported to: {country_csv}")

    # Export browser summary
    if not browser_df.empty:
        browser_csv = export_dir / "browser_summary.csv"
        browser_summary.to_csv(browser_csv)
        print(f"✅ Browser summary exported to: {browser_csv}")

    print("\n" + "="*60)
    print("SUMMARY REPORT COMPLETE")
    print("="*60)

    return True


if __name__ == "__main__":
    try:
        success = generate_summary_report()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error generating summary: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
