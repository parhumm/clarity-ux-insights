# Aggregate Metrics

Aggregate Clarity metrics over a specified date range to get summary statistics.

## Usage

Run the CLI aggregate command with the specified date range.

## Command

```bash
python clarity_cli.py aggregate {date_range}
```

## Examples

```bash
# Last 30 days
python clarity_cli.py aggregate 30

# November 2025
python clarity_cli.py aggregate November

# Q4 2025
python clarity_cli.py aggregate 2025-Q4

# Custom range
python clarity_cli.py aggregate "2025-11-01 to 2025-11-30"
```

## Options

- `--metric METRIC` - Specify metric name (default: Traffic)
- `--scope {general|page}` - Data scope
- `--page PAGE_ID` - Page ID for page scope

## Output

Shows:
- Data points count
- Average sessions
- Total sessions
- Average frustration metrics (dead clicks, rage clicks, quick backs)
- Engagement metrics
