# Generate Summary Report

Generate a summary report from your Clarity data.

## Usage

```bash
python generate_summary.py
```

## What It Does

1. Reads data from SQLite database
2. Generates summary statistics
3. Creates CSV exports in `data/exports/`
4. Prints summary to console

## Output Files

**CSV Exports:**
- `summary_last_3_days.csv` - Complete flattened dataset
- `device_summary.csv` - Device aggregation
- `browser_summary.csv` - Browser aggregation
- `country_summary.csv` - Country aggregation

## Console Output

Shows:
- Total sessions and users
- Device breakdown (Mobile, Desktop, Tablet)
- Top 10 countries
- Top 10 browsers
- Frustration metrics
- Engagement metrics

## Example

```bash
python generate_summary.py
```

Output:
```
📊 Clarity Data Summary
==================================================
Period: Last 3 days

📈 Traffic:
   Total Sessions: 6,562
   Unique Users: 4,235
   Bot Sessions: 274

📱 Device Distribution:
   Mobile: 54.7% (3,590 sessions)
   Desktop: 27.6% (1,814 sessions)
   Tablet: 6.1% (399 sessions)

🌍 Top Countries:
   1. Germany: 16.1%
   2. United States: 10.7%
   3. Turkey: 9.8%

⚠️ Frustration Signals:
   Quick Backs: 28.64%
   Dead Clicks: 12.18%
   Rage Clicks: 0.52%
```

## Use Cases

**Daily monitoring:**
```bash
python fetch_clarity_data.py
python generate_summary.py
```

**Export for presentations:**
```bash
python generate_summary.py
# Use CSV files from data/exports/
```
