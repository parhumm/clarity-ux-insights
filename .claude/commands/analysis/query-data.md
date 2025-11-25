# Query Clarity Data

Query Clarity UX metrics using flexible date expressions.

## Usage

Run the CLI query command with the specified date range.

## Date Range Examples

- `3` or `7` - Last N days
- `last-week` - Previous Monday-Sunday
- `November` - Full month by name
- `2025-11` - Month by ISO format
- `2025-Q4` - Quarter
- `2025-11-01 to 2025-11-30` - Custom range

## Command

```bash
python clarity_cli.py query {date_range}
```

Replace `{date_range}` with your desired date expression.

## Examples

```bash
# Last 7 days
python clarity_cli.py query 7

# Last week
python clarity_cli.py query last-week

# November 2025
python clarity_cli.py query November

# Q4 2025
python clarity_cli.py query 2025-Q4
```

## Options

- `--metric METRIC` - Specify metric name (default: Traffic)
- `--count-only` - Only show count, not sample data
- `--scope {general|page}` - Data scope
- `--page PAGE_ID` - Page ID for page scope

## Output

Shows:
- Date range parsed
- Number of records found
- Sample data (first 5 records)
- Total sessions, users, etc.
