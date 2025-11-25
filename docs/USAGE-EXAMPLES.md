# Usage Examples

Common patterns and practical use cases for Clarity UX Insights.

---

## Daily Monitoring

Set up automated data collection to build your historical dataset.

```bash
# Set up a daily cron job to collect data
0 2 * * * cd /path/to/clarity-ux-insights && python fetch_clarity_data.py

# Weekly cleanup (archive old data beyond retention period)
0 3 * * 0 cd /path/to/clarity-ux-insights && python scripts/archive_manager.py cleanup
```

---

## Quick Data Checks

Get instant insights into your current data.

```bash
# Check system status and available data
python clarity_cli.py status

# Query last 7 days
python clarity_cli.py query 7

# Or use Claude Code:
/system-status
/query-data 7
```

---

## Compare Time Periods

Identify trends by comparing different time periods.

```bash
# Week-over-week comparison
python scripts/comparator.py "last week"

# Month-over-month
python scripts/comparator.py November October

# This quarter vs last quarter
python scripts/comparator.py 2025-Q4 2025-Q3

# Or via Claude Code:
Tell Claude: "Compare this week's metrics to last week"
```

---

## Analyze Trends

Understand long-term patterns with statistical analysis.

```bash
# 30-day trend analysis
python scripts/trend_analyzer.py 30

# Quarterly trend
python scripts/trend_analyzer.py 2025-Q4

# Full year analysis
python scripts/trend_analyzer.py 2025

# Shows: growth rate, CAGR, volatility, trend direction, patterns
```

---

## Generate Professional Reports

Create comprehensive reports for different audiences.

```bash
# UX health report for last 7 days
python scripts/report_generator.py ux-health 7

# Frustration analysis for November
python scripts/report_generator.py frustration-analysis November

# Device performance comparison
python scripts/report_generator.py device-performance 30

# Page-specific analysis
python scripts/report_generator.py page-analysis 30 --page /checkout

# Reports saved to reports/ directory as markdown files
```

---

## Analyze Specific Issues with Claude

Use natural language to dig into your data.

```bash
# Use Claude Code to analyze
Tell Claude: "Show me the devices with the highest frustration rates"
Tell Claude: "Which countries have the most dead clicks?"
Tell Claude: "Compare mobile vs desktop engagement"
Tell Claude: "What's the trend in rage clicks over the last month?"
```

---

## Export for Presentations

Get your data into formats ready for stakeholder presentations.

```bash
# Generate CSV files
python generate_summary.py

# Or archive data in CSV format
python scripts/archive_manager.py archive --format csv

# Files saved to data/exports/ or archive/ directory
```

---

## Query the Database

For developers who want programmatic access.

```python
from scripts.query_engine import QueryEngine, DateParser

engine = QueryEngine()

# Query last 7 days
date_range = DateParser.parse("7")
metrics = engine.query_metrics(date_range)

# Aggregate over a period
summary = engine.aggregate_metrics(date_range, metric_name="Traffic")
print(f"Total sessions: {summary['sum_sessions']}")
```

---

## Advanced: Automated Weekly Reports

Combine tools for automated reporting workflows.

```bash
#!/bin/bash
# weekly_report.sh

# Fetch latest data
python fetch_clarity_data.py

# Generate comprehensive reports
python scripts/report_generator.py ux-health 7
python scripts/report_generator.py frustration-analysis 7
python scripts/comparator.py "last week"

# Archive outputs
mkdir -p reports/weekly/$(date +%Y-%m-%d)
mv reports/*.md reports/weekly/$(date +%Y-%m-%d)/

echo "Weekly reports generated in reports/weekly/$(date +%Y-%m-%d)/"
```

---

**Need more examples?** Check the [Command Reference](COMMAND-REFERENCE.md) for all available commands and options.
