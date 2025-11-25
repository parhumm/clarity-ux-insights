#!/usr/bin/env python3
"""
Fetch script for Televik data.

NOTE: Microsoft Clarity API limitation - the 'project-live-insights' endpoint
only supports fetching the last 1-3 days of data. To get 7 days of historical data,
this would require running the fetch daily over a week to accumulate the data.

This script fetches the maximum available (3 days) from the API.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fetch_clarity_data import main as fetch_main

if __name__ == "__main__":
    print("\n" + "="*60)
    print("FETCHING TELEVIK DATA")
    print("="*60)
    print("⚠️  API Limitation: Clarity API only provides last 3 days")
    print("   For 7-day historical data, the fetch needs to run daily")
    print("   over a week to accumulate the data.")
    print("="*60)
    print("\n📥 Fetching maximum available data (last 3 days)...\n")

    # Run the standard fetch (already configured for 3 days, all dimensions)
    try:
        success = fetch_main()
        if success:
            print("\n✅ Successfully fetched last 3 days of Televik data")
            print("   To accumulate 7 days, run this daily for a week")
        else:
            print("\n❌ Some fetches failed - check logs above")
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
