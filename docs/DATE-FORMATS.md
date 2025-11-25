# Date Format Reference

Clarity UX Insights supports 30+ flexible date formats for queries and reports.

## Numeric Formats

Simple numbers represent "last N days":

```python
"3"         # Last 3 days
"7"         # Last 7 days
"30"        # Last 30 days
```

With explicit units:

```python
"7d"        # Last 7 days
"7days"     # Last 7 days
"2weeks"    # Last 14 days
"1month"    # Last 30 days
```

## Relative Dates

```python
"today"         # Today only
"yesterday"     # Yesterday only
"last-week"     # Previous Monday-Sunday
"this-week"     # Current week to today
"last-month"    # Previous calendar month
"this-month"    # Current month to today
```

## Month Formats

ISO format:
```python
"2025-11"       # November 2025 (full month)
"2025-01"       # January 2025
"2025-12"       # December 2025
```

Month names:
```python
"November"      # November (current year)
"Nov"           # November (current year)
"Nov 2024"      # November 2024
"January 2025"  # January 2025
```

## Quarter Formats

```python
"2025-Q1"       # Q1 2025 (Jan-Mar)
"2025-Q2"       # Q2 2025 (Apr-Jun)
"2025-Q3"       # Q3 2025 (Jul-Sep)
"2025-Q4"       # Q4 2025 (Oct-Dec)
"Q4 2025"       # Alternative format
"2024Q1"        # Compact format
```

Quarter boundaries:
- Q1: January 1 - March 31
- Q2: April 1 - June 30
- Q3: July 1 - September 30
- Q4: October 1 - December 31

## Year Format

```python
"2025"          # Full year 2025 (Jan 1 - Dec 31)
"2024"          # Full year 2024
```

## Custom Ranges

With "to" syntax:
```python
"2025-11-01 to 2025-11-30"  # November 2025
"2025-01-01 to 2025-12-31"  # Full year 2025
```

With colon syntax:
```python
"2025-11-01:2025-11-30"     # November 2025
"2025-11-01:2025-11-15"     # First half of November
```

## Examples

### Query Engine

```python
from scripts.query_engine import QueryEngine

engine = QueryEngine()

# Last week
metrics = engine.query_metrics("last-week")

# November 2025
metrics = engine.query_metrics("November")

# Q4 2025
metrics = engine.query_metrics("2025-Q4")

# Custom range
metrics = engine.query_metrics("2025-11-01 to 2025-11-30")
```

### Aggregator

```python
from scripts.aggregator import MetricAggregator

aggregator = MetricAggregator()

# Week 48 of 2025
result = aggregator.aggregate_weekly_metrics(2025, 48)

# November 2025
result = aggregator.aggregate_monthly_metrics(2025, 11)
```

## Tips

1. **Be specific**: Parser tries specific formats first (Q4 2025 before just 2025)
2. **ISO weeks**: Weeks follow ISO 8601 standard (Monday-Sunday)
3. **Auto-swap**: Custom ranges auto-swap if end date is before start
4. **Case insensitive**: Month names work in any case (NOVEMBER, november, November)

## Error Handling

Invalid dates raise clear errors:

```python
try:
    range_obj = DateParser.parse("invalid")
except ValueError as e:
    print(f"Error: {e}")  # "Unable to parse date expression: invalid"
```

## Reference Date

All relative dates use "today" as reference. For testing:

```python
from scripts.query_engine import DateParser
from datetime import date

# Use custom reference date
ref_date = date(2025, 11, 25)
range_obj = DateParser.parse("last-week", reference_date=ref_date)
```
