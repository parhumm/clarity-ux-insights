# Complete Command Reference

**Comprehensive technical reference for all available commands**

---

## Table of Contents

1. [Unified CLI Commands](#unified-cli-commands)
2. [Claude Slash Commands](#claude-slash-commands)
3. [Advanced Analysis Scripts](#advanced-analysis-scripts)
4. [Utility Scripts](#utility-scripts)
5. [Legacy Scripts](#legacy-scripts)
6. [Date Format Reference](#date-format-reference)
7. [Common Examples](#common-examples)

---

## Unified CLI Commands

**Entry Point:** `clarity_cli.py`
**Purpose:** Modern unified interface for all operations

### query - Query Metrics

**Syntax:**
```bash
python clarity_cli.py query <date_range> [options]
```

**Parameters:**
- `date_range` (required) - Time period to query (see [Date Formats](#date-format-reference))
- `--metric METRIC` - Filter by metric name (default: Traffic)
- `--scope {general,page}` - Data scope (default: general)
- `--page PAGE_ID` - Page ID when scope=page
- `--count-only` - Only show record count

**Examples:**
```bash
# Last 7 days
python clarity_cli.py query 7

# Last week
python clarity_cli.py query "last week"

# November 2025
python clarity_cli.py query November

# Q4 2025
python clarity_cli.py query 2025-Q4

# Custom range
python clarity_cli.py query "2025-11-01 to 2025-11-30"

# Specific metric
python clarity_cli.py query 30 --metric "Frustration signals"

# Count only
python clarity_cli.py query 7 --count-only
```

**Output:**
```
📊 Querying metrics: 7
   Period: 2025-11-18 to 2025-11-25

✓ Found 3,386 records

Sample data:
  - 2025-11-24: 14,820 sessions
  - 2025-11-25: 14,821 sessions
```

---

### aggregate - Aggregate Metrics

**Syntax:**
```bash
python clarity_cli.py aggregate <date_range> [options]
```

**Parameters:**
- `date_range` (required) - Time period to aggregate
- `--metric METRIC` - Specific metric to aggregate
- `--scope {general,page}` - Data scope
- `--page PAGE_ID` - Page ID when scope=page

**Examples:**
```bash
# 30-day summary
python clarity_cli.py aggregate 30

# Last month
python clarity_cli.py aggregate "last month"

# Q3 2025
python clarity_cli.py aggregate 2025-Q3

# Specific metric
python clarity_cli.py aggregate 90 --metric Traffic
```

**Output:**
```
📊 Aggregating metrics: 30
   Period: 2025-10-26 to 2025-11-25

✓ Aggregation complete:
   Data points: 90
   Avg sessions: 14,820.5
   Total sessions: 1,333,845
   Avg dead clicks: 123.4
   Avg rage clicks: 45.2
```

---

### aggregate-all - Batch Aggregation

**Syntax:**
```bash
python clarity_cli.py aggregate-all [--force]
```

**Parameters:**
- `--force` - Force recalculation of existing summaries

**Examples:**
```bash
# Create all summaries
python clarity_cli.py aggregate-all

# Force recalculation
python clarity_cli.py aggregate-all --force
```

**What It Does:**
- Scans all daily metrics
- Creates weekly summaries (Monday-Sunday, ISO weeks)
- Creates monthly summaries (calendar months)
- Skips existing summaries unless --force used

**Output:**
```
📊 Aggregating all available data...

✓ Aggregation complete:
   Weekly summaries: 12
   Monthly summaries: 3
```

---

### list - List Available Data

**Syntax:**
```bash
python clarity_cli.py list [options]
```

**Parameters:**
- `--scope {general,page}` - Data scope
- `--verbose, -v` - Show all dates (not just range)

**Examples:**
```bash
# List general data
python clarity_cli.py list

# Show all dates
python clarity_cli.py list --verbose

# Page-specific data
python clarity_cli.py list --scope page
```

**Output:**
```
📋 Available data:
   Total dates: 45
   Latest: 2025-11-25
   Earliest: 2025-10-11

   All dates:
     - 2025-11-25
     - 2025-11-24
     ...
```

---

### status - System Status

**Syntax:**
```bash
python clarity_cli.py status
```

**Parameters:** None

**Examples:**
```bash
python clarity_cli.py status
```

**Output:**
```
📊 Clarity UX Insights - System Status
============================================================

📁 Project:
   Name: My Website
   Type: website
   URL: https://example.com

📊 Data:
   Daily metrics: 3,386
   Weekly metrics: 12
   Monthly metrics: 3
   Tracked pages: 5

📅 Date Range:
   First data: 2025-10-11
   Latest data: 2025-11-25

⚙️  Configuration:
   Default period: 7 days
   Output formats: markdown, csv
   Data retention: 90 days

============================================================
```

---

## Claude Slash Commands

**Usage:** Type directly in Claude Code
**Location:** `.claude/commands/`

### Analysis Commands

#### /query-data

**Syntax:**
```
/query-data <date_range>
```

**Examples:**
```
/query-data 7
/query-data last-week
/query-data November
```

**What It Does:** Runs `python clarity_cli.py query <date_range>`

---

#### /aggregate-metrics

**Syntax:**
```
/aggregate-metrics <date_range>
```

**Examples:**
```
/aggregate-metrics 30
/aggregate-metrics last-month
```

**What It Does:** Runs `python clarity_cli.py aggregate <date_range>`

---

#### /system-status

**Syntax:**
```
/system-status
```

**What It Does:** Runs `python clarity_cli.py status`

---

### Fetch Commands

#### /fetch-clarity-data

**Syntax:**
```
/fetch-clarity-data
```

**What It Does:**
- Runs `python fetch_clarity_data.py`
- Fetches latest data from Microsoft Clarity API
- Stores in database and creates JSON backups

---

### Maintenance Commands

#### /aggregate-all

**Syntax:**
```
/aggregate-all [--force]
```

**Examples:**
```
/aggregate-all
/aggregate-all --force
```

**What It Does:** Runs `python clarity_cli.py aggregate-all [--force]`

---

#### /list-data

**Syntax:**
```
/list-data [--scope general|page] [--verbose]
```

**Examples:**
```
/list-data
/list-data --verbose
```

**What It Does:** Runs `python clarity_cli.py list [options]`

---

### Reports Commands

#### /generate-summary

**Syntax:**
```
/generate-summary <date_range>
```

**Status:** Coming soon - will use report_generator.py

---

## Advanced Analysis Scripts

**Location:** `scripts/` directory

### report_generator.py - Generate Reports

**Syntax:**
```bash
python scripts/report_generator.py <template> <date_range> [options]
```

**Templates:**
- `ux-health` - Overall UX health overview
- `frustration-analysis` - Frustration signals deep dive
- `device-performance` - Mobile/Desktop/Tablet comparison
- `geographic-insights` - Global reach and top markets
- `content-performance` - Page and category analysis
- `engagement-analysis` - Time, scroll, behavior metrics
- `page-analysis` - Single page deep dive

**Parameters:**
- `template` (required) - Template name
- `date_range` (required) - Time period
- `--page PAGE_ID` - Page ID for page-analysis template
- `--output PATH` - Custom output path

**Examples:**
```bash
# UX health report
python scripts/report_generator.py ux-health 7

# Frustration analysis for November
python scripts/report_generator.py frustration-analysis November

# Device comparison last 30 days
python scripts/report_generator.py device-performance 30

# Page-specific analysis
python scripts/report_generator.py page-analysis 30 --page /checkout

# Custom output
python scripts/report_generator.py ux-health 7 --output custom_report.md
```

**Output:**
- Markdown files in `reports/general/` or `reports/pages/`
- Filename format: `{template}_{date_range}_{timestamp}.md`
- Includes YAML frontmatter with metadata
- Multi-audience insights (Technical, UX, Business, Marketing)

---

### comparator.py - Compare Time Periods

**Syntax:**
```bash
python scripts/comparator.py <period1> [period2] [options]
```

**Parameters:**
- `period1` (required) - First period (current/recent)
- `period2` (optional) - Second period (if omitted, auto-calculates previous equivalent)
- `--metric METRIC` - Specific metric to compare
- `--scope {general,page}` - Data scope

**Examples:**
```bash
# Auto-compare to previous period
python scripts/comparator.py "last week"
python scripts/comparator.py 7

# Specific periods
python scripts/comparator.py November October
python scripts/comparator.py 2025-Q4 2025-Q3
python scripts/comparator.py "this week" "last week"

# Custom date ranges
python scripts/comparator.py "2025-11-15 to 2025-11-21" "2025-11-08 to 2025-11-14"

# Specific metric
python scripts/comparator.py 7 --metric Traffic
```

**Output:**
```
============================================================
PERIOD COMPARISON
============================================================

Period 1: 2025-11-18 to 2025-11-24 (7 days)
Period 2: 2025-11-11 to 2025-11-17 (7 days)

============================================================
KEY METRICS
============================================================

Sessions:
  Current: 44,461 | Previous: 42,000
  Change: +2,461 (+5.9%) [up]

============================================================
IMPROVEMENTS
============================================================

✓ Sessions: +5.9% (+2,461)
✓ Dead Clicks: -12.3% (-150)

============================================================
REGRESSIONS
============================================================

✗ Rage Clicks: +8.4% (+25)

============================================================
SUMMARY
============================================================

Improvements: 2
Regressions: 1

Overall: Positive trend ↑

============================================================
```

---

### trend_analyzer.py - Trend Analysis

**Syntax:**
```bash
python scripts/trend_analyzer.py <date_range> [options]
```

**Parameters:**
- `date_range` (required) - Period to analyze
- `--metric METRIC` - Specific metric
- `--scope {general,page}` - Data scope

**Examples:**
```bash
# 30-day trend
python scripts/trend_analyzer.py 30

# Monthly trend
python scripts/trend_analyzer.py "last month"

# Quarterly trend
python scripts/trend_analyzer.py 2025-Q4

# Full year
python scripts/trend_analyzer.py 2025

# 90-day analysis
python scripts/trend_analyzer.py 90
```

**Output:**
```
============================================================
LONG-TERM TREND ANALYSIS
============================================================

Period: 2025-10-26 to 2025-11-25 (30 days)
Duration: 30 days (3456 data points)

============================================================
OVERALL METRICS
============================================================

Sessions:
  Total: 445,230
  Average per day: 14,841
  Range: 12,500 - 17,300

Frustration Signals:
  Total: 15,230
  Per session: 0.034

============================================================
GROWTH ANALYSIS
============================================================

Total Growth: +12.5%
  First period: 13,400 sessions
  Last period: 15,075 sessions
  Absolute change: +1,675

Compound Annual Growth Rate (CAGR): +167.3%

Average Daily Growth: +0.41%

============================================================
VOLATILITY ANALYSIS
============================================================

Mean: 14,841 sessions/day
Standard Deviation: 892
Coefficient of Variation: 6.0%
Stability: HIGH

============================================================
TREND ANALYSIS
============================================================

Direction: INCREASING
Slope: +28.5 sessions/day
R-squared: 0.842
Strength: STRONG

============================================================
PATTERN ANALYSIS
============================================================

Peaks detected: 4
Valleys detected: 4
Average peak distance: 7.2 days

✓ Weekly pattern detected (peaks ~7 days apart)
✓ Cyclical pattern present

============================================================
```

---

### archive_manager.py - Data Archiving

**Syntax:**
```bash
python scripts/archive_manager.py <command> [options]
```

**Commands:**
- `check` - Identify old data
- `archive` - Export old data to files
- `delete` - Remove old data from database
- `cleanup` - Archive and delete (recommended)
- `list` - List archive files
- `restore` - Restore from archive

**Common Options:**
- `--date YYYY-MM-DD` - Reference date
- `--format {json,csv}` - Archive format
- `--dry-run` - Preview without executing

#### check - Check Old Data

**Syntax:**
```bash
python scripts/archive_manager.py check [--date YYYY-MM-DD]
```

**Examples:**
```bash
python scripts/archive_manager.py check
python scripts/archive_manager.py check --date 2025-11-25
```

**Output:**
```
📊 Old Data Check
Retention Period: 90 days
Cutoff Date: 2025-08-27
Total Records: 1,234
Date Range: 2025-06-01 to 2025-08-26

By Metric:
  Traffic: 617
  Frustration signals: 617
```

#### archive - Archive Old Data

**Syntax:**
```bash
python scripts/archive_manager.py archive [--date YYYY-MM-DD] [--format json|csv] [--dry-run]
```

**Examples:**
```bash
# Archive as JSON (default)
python scripts/archive_manager.py archive

# Archive as CSV
python scripts/archive_manager.py archive --format csv

# Dry run (preview)
python scripts/archive_manager.py archive --dry-run
```

**Output:**
```
✓ Archived 1,234 records
File: archive/archive_2025-11-25.json
```

#### delete - Delete Old Data

**Syntax:**
```bash
python scripts/archive_manager.py delete [--date YYYY-MM-DD] [--dry-run]
```

**Examples:**
```bash
# Delete old data
python scripts/archive_manager.py delete

# Dry run
python scripts/archive_manager.py delete --dry-run
```

**Output:**
```
✓ Deleted 1,234 records
Cutoff: 2025-08-27
```

#### cleanup - Archive and Delete

**Syntax:**
```bash
python scripts/archive_manager.py cleanup [--date YYYY-MM-DD] [--format json|csv] [--dry-run]
```

**Examples:**
```bash
# Archive and delete (recommended workflow)
python scripts/archive_manager.py cleanup

# Dry run first
python scripts/archive_manager.py cleanup --dry-run

# CSV format
python scripts/archive_manager.py cleanup --format csv
```

**Output:**
```
✓ Cleanup complete:
  Archived: 1,234 records
  Deleted: 1,234 records
  File: archive/archive_2025-11-25.json
```

#### list - List Archives

**Syntax:**
```bash
python scripts/archive_manager.py list
```

**Output:**
```
📁 Archive Files: 3
  archive_2025-11-25.json (12.34 MB)
  archive_2025-10-25.json (11.89 MB)
  archive_2025-09-25.csv (8.45 MB)
```

#### restore - Restore Archive

**Syntax:**
```bash
python scripts/archive_manager.py restore <archive_file> [--dry-run]
```

**Examples:**
```bash
# Restore from archive
python scripts/archive_manager.py restore archive/archive_2025-10-25.json

# Dry run
python scripts/archive_manager.py restore archive/archive_2025-10-25.json --dry-run
```

**Output:**
```
✓ Restored 1,234 records
Skipped 0 duplicates
```

---

## Utility Scripts

**Location:** `scripts/` directory
**Purpose:** Data management and maintenance utilities

### cleanup_all_data.py - Clean All Data

**Syntax:**
```bash
python scripts/cleanup_all_data.py
```

**What It Does:**
- Deletes all records from all database tables
- Removes all raw JSON files from `data/raw/`
- Removes all generated reports from `reports/`
- Preserves database backups
- Prompts for confirmation before deletion

**Use Cases:**
- Fresh start with new data
- Reset testing environment
- Clear corrupted data
- Prepare for data re-import

**Safety Features:**
- Interactive confirmation required (type `yes`)
- Database backups are NOT deleted
- Shows summary of what will be deleted
- Provides detailed feedback during cleanup

**Example Session:**
```bash
$ python scripts/cleanup_all_data.py

============================================================
🧹 TELEVIK DATA CLEANUP
============================================================

⚠️  WARNING: This will delete ALL data and reports!
  - All database records
  - All raw JSON files
  - All generated reports

Are you sure you want to continue? (yes/no): yes

🚀 Starting cleanup...

🗄️  Cleaning up database...
  ✓ Deleted 3386 records from daily_metrics
  ✓ Deleted 4 records from weekly_metrics
  ✓ Deleted 6 records from monthly_metrics
  ✓ Database cleanup complete

📁 Cleaning up raw JSON files...
  ✓ Deleted 6 raw JSON files

📊 Cleaning up generated reports...
  ✓ Deleted 14 total reports

============================================================
✅ CLEANUP COMPLETE
============================================================
```

**Note:** This is a destructive operation. Ensure you have backups if you need to preserve data.

---

### fetch_yesterday.py - Fetch Yesterday's Data (Recommended)

**Syntax:**
```bash
python scripts/fetch_yesterday.py
```

**What It Does:**
- Fetches only yesterday's data (1 day) from Clarity API
- Minimizes API calls to avoid rate limits (6 calls total)
- Stores data in database with duplicate prevention
- Creates JSON backups in `data/raw/`
- Logs all API requests in `fetch_log` table

**Why Use This Instead of fetch_7days.py:**
- **Lower rate limit impact** - Fetches 1 day instead of 3
- **Faster execution** - Smaller data volume per request
- **More reliable** - Less likely to hit rate limits
- **Daily workflow friendly** - Designed to run once per day

**Features:**
- Fetches all 6 dimension breakdowns:
  - Base metrics (no dimensions)
  - Device breakdown (Mobile, Desktop, Tablet)
  - Country breakdown
  - Browser breakdown
  - Device + Browser combinations
  - Country + Device combinations
- Automatic retry with exponential backoff
- Rate limit handling (waits 60 seconds when hit)
- Duplicate detection and prevention

**Example Output:**
```bash
$ python scripts/fetch_yesterday.py

============================================================
FETCHING YESTERDAY'S TELEVIKA DATA
============================================================
Project: televika
Fetching: Yesterday only (1 day)
API calls planned: 6 (one per dimension)
============================================================

[1/6] Base Metrics
💾 Saved to: data/raw/base_metrics_1day.json
📊 Received 16 metric groups, 71 total rows
💾 Inserted 71 new records into database
✅ Success!

[2/6] Device Breakdown
💾 Saved to: data/raw/by_device_1day.json
📊 Received 9 metric groups, 36 total rows
💾 Inserted 36 new records into database
✅ Success!

...

============================================================
DATA COLLECTION COMPLETE
============================================================
✅ Successful: 6/6
❌ Failed: 0/6

📊 DATABASE STATISTICS:
   Total metrics: 2,502
   Latest fetch: 2025-11-26 07:08:53
```

**Recommended Schedule:**
Set up a daily cron job to automatically fetch yesterday's data:
```bash
# Run at 2 AM daily to fetch previous day's data
0 2 * * * cd /path/to/clarity_api && python scripts/fetch_yesterday.py
```

**Troubleshooting:**
- **Rate Limits:** If you see "⚠️ Rate limit hit", wait a few hours and retry
- **Token Expired:** Update `CLARITY_API_TOKEN` in `.env` file with a fresh token
- **No Data:** Ensure project had activity yesterday in Microsoft Clarity

---

### migrate_yesterday_data.py - Migrate Old Schema Data

**Syntax:**
```bash
python scripts/migrate_yesterday_data.py
```

**What It Does:**
- Migrates data from old schema (`clarity_metrics`) to new schema (`daily_metrics`)
- Properly parses varying JSON structures for different metric types
- Extracts specific values based on metric type (Traffic, Dead Clicks, etc.)
- Skips records with no useful data
- Provides detailed migration summary

**When to Use:**
- After fetching data that went into the old `clarity_metrics` table
- When you need to convert legacy data to the new schema
- Automatically called by newer fetch workflows

**Metric Types Handled:**
- **Traffic metrics:** Sessions, users, bot sessions, pages per session
- **Frustration signals:** Dead clicks, rage clicks, quick backs, error clicks, script errors
- **Engagement metrics:** Scroll depth, engagement time, active time

**Example Output:**
```bash
$ python scripts/migrate_yesterday_data.py

============================================================
MIGRATING YESTERDAY'S DATA
============================================================

Found 2502 records to migrate

✓ Migrated 2431 records
  Skipped 71 records

📊 Database Summary:
   2025-11-26: 2431 records

✓ Traffic Data:
   Total Sessions: 16,382
   Total Users: 13,564

============================================================
MIGRATION COMPLETE
============================================================
```

**Note:** This script is part of the data ingestion pipeline. Newer versions of the fetch scripts may automatically migrate data.

---

### fetch_7days.py - Fetch Latest Data

**Syntax:**
```bash
python scripts/fetch_7days.py
```

**What It Does:**
- Wrapper around `fetch_clarity_data.py`
- Fetches maximum available data from Clarity API (last 3 days)
- Stores data in database with duplicate prevention
- Creates JSON backups in `data/raw/`
- Logs all API requests in `fetch_log` table

**API Limitation Notice:**
Microsoft Clarity's "project-live-insights" API endpoint only supports fetching the last 1-3 days of data. To accumulate 7 days of historical data, this script needs to be run daily over a week.

**⚠️ Note:** Consider using `fetch_yesterday.py` instead for daily workflows to minimize rate limit issues.

**Features:**
- Fetches all 6 dimension breakdowns
- Automatic retry with exponential backoff
- Rate limit handling (waits 60 seconds when hit)
- Duplicate detection and prevention

**Troubleshooting:**
- **Rate Limits:** If you see "⚠️ Rate limit hit", the script will automatically wait and retry
- **Token Expired:** Update `CLARITY_API_TOKEN` in `.env` file with a fresh token
- **No Data:** Ensure project has recent activity in Microsoft Clarity

---

## Legacy Scripts

Original scripts that still work (located in root directory):

### fetch_clarity_data.py

**Syntax:**
```bash
python fetch_clarity_data.py
```

**What It Does:**
- Fetches data from Microsoft Clarity API
- Stores in SQLite database
- Creates JSON backups in `data/raw/`

### generate_summary.py

**Syntax:**
```bash
python generate_summary.py
```

**What It Does:**
- Generates summary CSV reports
- Exports to `data/exports/`

### config.py

**Syntax:**
```bash
python config.py
```

**What It Does:**
- Tests API configuration
- Validates credentials

### validate_data.py

**Syntax:**
```bash
python validate_data.py
```

**What It Does:**
- Validates database integrity
- Checks for data issues

---

## Date Format Reference

### Numeric Formats

```
3               # Last 3 days
7               # Last 7 days
30              # Last 30 days
90              # Last 90 days
3days           # Last 3 days (explicit)
2weeks          # Last 2 weeks (14 days)
1month          # Last 1 month (~30 days)
```

### Relative Dates

```
today           # Today
yesterday       # Yesterday
last-week       # Previous week (Monday-Sunday)
last-month      # Previous calendar month
this-week       # Current week (Monday-now)
this-month      # Current month (1st-now)
```

### Month Formats

```
November        # Entire month (current or previous year)
2025-11         # November 2025 (YYYY-MM)
Nov 2024        # November 2024
2024-11         # November 2024
```

### Quarter Formats

```
2025-Q4         # Q4 2025 (Oct-Dec)
Q4 2025         # Q4 2025 (alternate format)
2024-Q1         # Q1 2024 (Jan-Mar)
```

### Year Format

```
2025            # Entire year 2025 (Jan 1-Dec 31)
2024            # Entire year 2024
```

### Custom Ranges

```
"2025-11-01 to 2025-11-30"         # Custom range (requires quotes)
"2025-10-15 to 2025-11-15"         # Any date range
```

**Note:** Custom ranges require quotes in command line

---

## Common Examples

### Daily Workflow

```bash
# Morning check
python clarity_cli.py status
python clarity_cli.py query yesterday

# Weekly review
python scripts/comparator.py "last week"
python scripts/trend_analyzer.py 7
```

### Monthly Reporting

```bash
# Month-end analysis
python clarity_cli.py aggregate November
python scripts/comparator.py November October
python scripts/report_generator.py ux-health November

# Archive old data
python scripts/archive_manager.py cleanup --dry-run
python scripts/archive_manager.py cleanup
```

### Quarterly Review

```bash
# Quarterly comparison
python scripts/comparator.py 2025-Q4 2025-Q3

# Quarterly trend
python scripts/trend_analyzer.py 2025-Q4

# Generate reports
python scripts/report_generator.py ux-health 2025-Q4
python scripts/report_generator.py frustration-analysis 2025-Q4
python scripts/report_generator.py device-performance 2025-Q4
```

### Problem Investigation

```bash
# Check recent issues
python clarity_cli.py query 3
python scripts/report_generator.py frustration-analysis 7

# Compare to baseline
python scripts/comparator.py 7

# Analyze trend
python scripts/trend_analyzer.py 30
```

---

## Tips and Best Practices

### Date Format Tips

1. **Use quotes for custom ranges:** `"2025-11-01 to 2025-11-30"`
2. **Numeric is fastest:** `7` is simpler than `"last week"`
3. **Be specific for months:** `2025-11` is clearer than `November`
4. **Quarters use Q:** `2025-Q4` not `2025-4` or `Q4-2025`

### Performance Tips

1. **Use aggregate-all:** Pre-calculate weekly/monthly summaries
2. **Query specific scopes:** Use `--scope` to reduce data
3. **Use count-only:** When you just need record counts
4. **Archive old data:** Keep database lean and fast

### Workflow Tips

1. **Start with status:** Always run `status` first
2. **Dry run archives:** Use `--dry-run` before cleanup
3. **Compare before analyzing:** Quick comparison shows if deep analysis is needed
4. **Use templates:** Report templates are faster than custom queries

---

## Error Handling

### Common Errors

**"No data found for period"**
- Check: `python clarity_cli.py list`
- Solution: Use date range with available data

**"Date format not recognized"**
- Check: Date format matches supported formats
- Solution: Use numeric (7) or add quotes for custom ranges

**"Database locked"**
- Check: Another process using database
- Solution: Wait or close other processes

**"Template not found"**
- Check: Template name is correct
- Solution: Use one of the 7 supported templates

### Debug Commands

```bash
# Check system health
python clarity_cli.py status

# Verify data availability
python clarity_cli.py list --verbose

# Test with small query
python clarity_cli.py query 1 --count-only

# Validate configuration
python config.py
```

---

**For more information, see:**
- [User Guide](../USER-GUIDE.md) - Non-technical guide
- [README](../README.md) - Main documentation
- [Quick Start](QUICK-START.md) - Setup guide
- [Date Formats](DATE-FORMATS.md) - Complete date format reference
