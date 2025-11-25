#!/usr/bin/env python3
"""
Clarity UX Insights - Unified CLI
Intelligent command-line interface for all operations.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.query_engine import QueryEngine, DateParser
from scripts.aggregator import MetricAggregator
from config_loader import load_config


class ClarityCLI:
    """Unified CLI for Clarity UX Insights."""

    def __init__(self):
        """Initialize CLI."""
        self.config = None
        try:
            self.config = load_config()
        except Exception as e:
            print(f"⚠️  Configuration warning: {e}")
            print("💡 Using default configuration")

        self.query_engine = QueryEngine()
        self.aggregator = MetricAggregator()

    def query(self, args):
        """Query metrics with flexible date parsing."""
        print(f"\n📊 Querying metrics: {args.date_range}")

        try:
            # Parse date range
            date_range = DateParser.parse(args.date_range)
            print(f"   Period: {date_range}")

            # Query metrics
            metrics = self.query_engine.query_metrics(
                date_range,
                metric_name=args.metric,
                data_scope=args.scope,
                page_id=args.page
            )

            print(f"\n✓ Found {len(metrics)} records")

            if metrics and not args.count_only:
                # Show summary
                print("\nSample data:")
                for i, metric in enumerate(metrics[:5]):
                    print(f"  - {metric['metric_date']}: {metric.get('sessions', 'N/A')} sessions")
                if len(metrics) > 5:
                    print(f"  ... and {len(metrics) - 5} more")

            return metrics

        except Exception as e:
            print(f"❌ Query failed: {e}")
            return []

    def aggregate(self, args):
        """Aggregate metrics into summaries."""
        print(f"\n📊 Aggregating metrics: {args.date_range}")

        try:
            date_range = DateParser.parse(args.date_range)
            print(f"   Period: {date_range}")

            result = self.query_engine.aggregate_metrics(
                date_range,
                metric_name=args.metric,
                data_scope=args.scope,
                page_id=args.page
            )

            print("\n✓ Aggregation complete:")
            print(f"   Data points: {result.get('data_points', 0)}")
            print(f"   Avg sessions: {result.get('avg_sessions', 0):.2f}")
            print(f"   Total sessions: {result.get('sum_sessions', 0):,}")

            if result.get('avg_dead_clicks') is not None:
                print(f"   Avg dead clicks: {result.get('avg_dead_clicks', 0):.2f}")
            if result.get('avg_quick_backs') is not None:
                print(f"   Avg quick backs: {result.get('avg_quick_backs', 0):.2f}")

            return result

        except Exception as e:
            print(f"❌ Aggregation failed: {e}")
            return {}

    def aggregate_all(self, args):
        """Aggregate all available data."""
        print("\n📊 Aggregating all available data...")

        try:
            counts = self.aggregator.aggregate_all_available(force=args.force)

            print("\n✓ Aggregation complete:")
            print(f"   Weekly summaries: {counts['weekly']}")
            print(f"   Monthly summaries: {counts['monthly']}")

            return counts

        except Exception as e:
            print(f"❌ Aggregation failed: {e}")
            return {}

    def list_data(self, args):
        """List available data."""
        print("\n📋 Available data:")

        try:
            dates = self.query_engine.get_available_dates(data_scope=args.scope)

            if not dates:
                print("   No data found")
                return []

            print(f"   Total dates: {len(dates)}")
            print(f"   Latest: {dates[0]}")
            print(f"   Earliest: {dates[-1]}")

            if args.verbose:
                print("\n   All dates:")
                for date in dates[:20]:
                    print(f"     - {date}")
                if len(dates) > 20:
                    print(f"     ... and {len(dates) - 20} more")

            return dates

        except Exception as e:
            print(f"❌ Failed to list data: {e}")
            return []

    def status(self, args):
        """Show system status."""
        print("\n📊 Clarity UX Insights - System Status")
        print("=" * 60)

        # Project info
        if self.config:
            print(f"\n📁 Project:")
            print(f"   Name: {self.config.project.name}")
            print(f"   Type: {self.config.project.type}")
            if self.config.project.url:
                print(f"   URL: {self.config.project.url}")

        # Data status
        try:
            conn = self.query_engine.get_connection()

            # Daily metrics
            cursor = conn.execute("SELECT COUNT(*) as count FROM daily_metrics")
            daily_count = cursor.fetchone()['count']

            # Weekly metrics
            cursor = conn.execute("SELECT COUNT(*) as count FROM weekly_metrics")
            weekly_count = cursor.fetchone()['count']

            # Monthly metrics
            cursor = conn.execute("SELECT COUNT(*) as count FROM monthly_metrics")
            monthly_count = cursor.fetchone()['count']

            # Date range
            cursor = conn.execute("""
                SELECT MIN(metric_date) as min_date, MAX(metric_date) as max_date
                FROM daily_metrics
            """)
            date_range = cursor.fetchone()

            # Pages
            cursor = conn.execute("SELECT COUNT(*) as count FROM pages")
            pages_count = cursor.fetchone()['count']

            conn.close()

            print(f"\n📊 Data:")
            print(f"   Daily metrics: {daily_count:,}")
            print(f"   Weekly metrics: {weekly_count:,}")
            print(f"   Monthly metrics: {monthly_count:,}")
            print(f"   Tracked pages: {pages_count}")

            if date_range['min_date']:
                print(f"\n📅 Date Range:")
                print(f"   First data: {date_range['min_date']}")
                print(f"   Latest data: {date_range['max_date']}")

        except Exception as e:
            print(f"\n⚠️  Could not fetch data status: {e}")

        # Configuration
        if self.config:
            print(f"\n⚙️  Configuration:")
            print(f"   Default period: {self.config.reports.default_period_days} days")
            print(f"   Output formats: {', '.join(self.config.reports.output_formats)}")
            print(f"   Data retention: {self.config.data.retention_days} days")

        print("\n" + "=" * 60)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Clarity UX Insights - Unified CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query last 7 days
  python clarity_cli.py query 7

  # Query November 2025
  python clarity_cli.py query November

  # Query Q4 2025
  python clarity_cli.py query 2025-Q4

  # Aggregate last 30 days
  python clarity_cli.py aggregate 30

  # Aggregate all available data
  python clarity_cli.py aggregate-all

  # List available data
  python clarity_cli.py list

  # Show system status
  python clarity_cli.py status
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query metrics')
    query_parser.add_argument('date_range', help='Date range (e.g., 7, last-week, November, 2025-Q4)')
    query_parser.add_argument('--metric', default='Traffic', help='Metric name (default: Traffic)')
    query_parser.add_argument('--scope', default='general', choices=['general', 'page'], help='Data scope')
    query_parser.add_argument('--page', help='Page ID (for page scope)')
    query_parser.add_argument('--count-only', action='store_true', help='Only show count')

    # Aggregate command
    agg_parser = subparsers.add_parser('aggregate', help='Aggregate metrics')
    agg_parser.add_argument('date_range', help='Date range to aggregate')
    agg_parser.add_argument('--metric', default='Traffic', help='Metric name (default: Traffic)')
    agg_parser.add_argument('--scope', default='general', choices=['general', 'page'], help='Data scope')
    agg_parser.add_argument('--page', help='Page ID (for page scope)')

    # Aggregate all command
    agg_all_parser = subparsers.add_parser('aggregate-all', help='Aggregate all available data')
    agg_all_parser.add_argument('--force', action='store_true', help='Force recalculation')

    # List command
    list_parser = subparsers.add_parser('list', help='List available data')
    list_parser.add_argument('--scope', default='general', choices=['general', 'page'], help='Data scope')
    list_parser.add_argument('--verbose', '-v', action='store_true', help='Show all dates')

    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize CLI
    cli = ClarityCLI()

    # Execute command
    try:
        if args.command == 'query':
            cli.query(args)
        elif args.command == 'aggregate':
            cli.aggregate(args)
        elif args.command == 'aggregate-all':
            cli.aggregate_all(args)
        elif args.command == 'list':
            cli.list_data(args)
        elif args.command == 'status':
            cli.status(args)
        else:
            parser.print_help()
            return 1

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
