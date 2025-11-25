# Aggregate All Data

Aggregate all available daily data into weekly and monthly summaries.

## Usage

```bash
python clarity_cli.py aggregate-all
```

## What It Does

1. Scans all available daily metrics in database
2. Calculates weekly summaries (ISO weeks, Monday-Sunday)
3. Calculates monthly summaries (calendar months)
4. Stores summaries in `weekly_metrics` and `monthly_metrics` tables
5. Skips existing aggregations (unless --force is used)

## Options

```bash
# Normal run (skip existing)
python clarity_cli.py aggregate-all

# Force recalculation
python clarity_cli.py aggregate-all --force
```

## When to Use

**After fetching new data:**
```bash
python fetch_clarity_data.py
python clarity_cli.py aggregate-all
```

**To recalculate summaries:**
```bash
python clarity_cli.py aggregate-all --force
```

**For initial setup:**
```bash
python clarity_cli.py aggregate-all
```

## Output

Shows:
- Date range being aggregated
- Progress for each week
- Progress for each month
- Total weekly aggregations created
- Total monthly aggregations created

## Benefits

- Pre-calculated summaries for fast reporting
- Weekly and monthly trend analysis
- Reduced database queries for reports
- Consistent calculations across reports
