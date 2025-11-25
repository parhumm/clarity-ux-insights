# Clarity UX Insights

Transform user behavior into actionable insights. Automatically collect, analyze, and preserve Microsoft Clarity analytics data to discover what users really experience on your site.

## 🎯 What You'll Discover

Stop guessing. Start knowing. This tool captures Microsoft Clarity analytics and preserves it forever, revealing:

**For UX Researchers:**
- **Uncover frustration patterns** - See exactly where users rage click, encounter dead clicks, or quickly abandon
- **Reveal engagement insights** - Discover how users actually scroll, navigate, and interact with your design
- **Compare experiences** - Identify device- and browser-specific usability issues with real behavioral data
- **Validate design decisions** - Replace assumptions with evidence from actual user sessions

**For Product Managers:**
- **Track product health** - Monitor daily metrics that show how your product is really performing
- **Measure feature impact** - See which features users adopt and which they ignore
- **Prioritize confidently** - Fix what hurts users most, backed by frustration and engagement data
- **Build smarter roadmaps** - Make strategic decisions based on long-term trends, not gut feelings

**Critical Advantage:** Microsoft Clarity's API only retains 3 days of data. This tool automatically collects it daily and preserves it indefinitely, letting you analyze trends across weeks, months, and product cycles.

---

## ✨ What's New - Powerful Analysis Tools

This project now includes a complete suite of professional analytics tools:

**🎯 Unified CLI** - Single command interface for all operations
- Query any time period with natural language ("last week", "November", "Q4 2025")
- Instant system status and data overview
- Smart aggregation and summarization

**🤖 Claude Slash Commands** - 7 ready-to-use commands
- `/query-data` - Query metrics with flexible dates
- `/aggregate-metrics` - Summarize data over periods
- `/system-status` - Check system health and data
- Plus 4 more for fetching, maintenance, and reporting

**📊 Advanced Analysis** - Professional statistical tools
- **Period Comparison** - Compare week-over-week, month-over-month, any period to any period
- **Trend Detection** - Statistical analysis with R², CAGR, pattern recognition
- **Report Generation** - 7 professional templates with multi-audience insights
- **Archive Management** - Automated data retention and cleanup

**🗓️ Smart Date Parsing** - 30+ date formats supported
- Natural: "7", "last-week", "yesterday"
- Months: "November", "2025-11", "Nov 2024"
- Quarters: "2025-Q4", "Q4 2025"
- Custom: "2025-11-01 to 2025-11-30"

[See all commands below](#-all-available-commands)

---

## ⚡ Quick Start - Choose Your Path

### Path 1: Claude Code (Easiest 🌟)

The easiest way to get started is using [Claude Code](https://claude.ai/code).

#### Step 1: Get Your Clarity API Token

1. Go to https://clarity.microsoft.com/
2. Click on your project
3. Go to **Settings** → **API** → **Data Export API**
4. Click **Generate Token**
5. Copy the token (starts with `eyJ...`)
6. Also note your **Project ID** (in Settings)

#### Step 2: Clone This Repository with Claude Code

1. Open Claude Code (desktop app or web)
2. Tell Claude:
   ```
   Clone this repository: https://github.com/parhumm/clarity-ux-insights
   ```
3. Claude will clone it to your system

#### Step 3: Set Up Environment with Claude Code

Tell Claude:
```
Set up the environment for this Clarity project:
1. Copy .env.example to .env
2. Help me configure it with my API credentials
```

Claude will:
- Copy the example file
- Ask you for your API token and Project ID
- Configure the `.env` file securely

**Paste your values when Claude asks:**
- `CLARITY_API_TOKEN`: Your token from Step 1
- `CLARITY_PROJECT_ID`: Your project ID from Step 1

#### Step 4: Install Dependencies with Claude Code

Tell Claude:
```
Install the Python dependencies for this project
```

Claude will run `pip install -r requirements.txt`

#### Step 5: Test the Setup with Claude Code

Tell Claude:
```
Test if the Clarity API configuration is working
```

Claude will run `python config.py` and show you if everything is connected.

#### Step 6: Collect Your First Data with Claude Code

Tell Claude:
```
Fetch my Clarity data for the last 3 days
```

Claude will run `python fetch_clarity_data.py` and:
- Fetch 6 types of analytics data
- Store it in a local SQLite database
- Save raw JSON files
- Show you a summary

#### Step 7: Use Claude Slash Commands (Optional - Even Easier!)

Once setup is complete, you can use slash commands directly:
```
/system-status
/query-data 7
/aggregate-metrics last-week
```

---

### Path 2: Unified CLI (Powerful 💪)

After completing setup (Steps 1-5 above), use the modern CLI for powerful queries:

```bash
# Check system status and available data
python clarity_cli.py status

# Query last 7 days
python clarity_cli.py query 7

# Query with natural language dates
python clarity_cli.py query "last week"
python clarity_cli.py query November
python clarity_cli.py query 2025-Q4

# Aggregate and summarize
python clarity_cli.py aggregate 30
python clarity_cli.py aggregate-all

# List available data
python clarity_cli.py list --verbose
```

---

### Path 3: Manual Setup (Advanced 🔧)

If you prefer to set up manually:

#### 1. Clone the Repository
```bash
git clone https://github.com/parhumm/clarity-ux-insights.git
cd clarity-ux-insights
```

#### 2. Configure Environment
```bash
# Copy example file
cp .env.example .env

# Edit with your credentials
nano .env
```

Add your values:
```
CLARITY_API_TOKEN=your_token_here
CLARITY_PROJECT_ID=your_project_id
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Test Configuration
```bash
python config.py
```

#### 5. Fetch Data
```bash
python fetch_clarity_data.py
```

#### 6. Start Analyzing
```bash
# Use the unified CLI
python clarity_cli.py status

# Or use individual scripts
python generate_summary.py
```

---

## 🎯 All Available Commands

### Unified CLI Commands (Recommended)

The modern interface for all operations:

#### Query Command
```bash
# Query data with flexible date expressions
python clarity_cli.py query <date_range> [options]

# Examples:
python clarity_cli.py query 7                    # Last 7 days
python clarity_cli.py query "last week"          # Previous week
python clarity_cli.py query November             # Entire month
python clarity_cli.py query 2025-Q4              # Quarter
python clarity_cli.py query "2025-11-01 to 2025-11-30"  # Custom range

# Options:
--metric METRIC          # Filter by metric name (default: Traffic)
--scope {general,page}   # Data scope
--page PAGE_ID           # Specific page ID
--count-only             # Only show count
```

#### Aggregate Command
```bash
# Aggregate metrics over a period
python clarity_cli.py aggregate <date_range> [options]

# Examples:
python clarity_cli.py aggregate 30               # Last 30 days summary
python clarity_cli.py aggregate "last month"     # Previous month
python clarity_cli.py aggregate 2025-Q3          # Quarter summary

# Shows: total, average, min, max for all metrics
```

#### Aggregate-All Command
```bash
# Aggregate all available data into weekly/monthly summaries
python clarity_cli.py aggregate-all [--force]

# Creates pre-calculated summaries for faster queries
# Use --force to recalculate existing summaries
```

#### List Command
```bash
# List available data dates
python clarity_cli.py list [options]

# Options:
--scope {general,page}   # Data scope
--verbose, -v            # Show all dates (not just range)
```

#### Status Command
```bash
# Show complete system status
python clarity_cli.py status

# Shows:
# - Project configuration
# - Database metrics count (daily/weekly/monthly)
# - Date range of available data
# - Tracked pages
# - Configuration settings
```

### Claude Slash Commands

Use these directly in Claude Code:

#### Analysis Commands
```
/query-data <date_range>
# Query metrics with flexible date expressions
# Example: /query-data 7
# Example: /query-data last-week

/aggregate-metrics <date_range>
# Summarize data over a period with statistics
# Example: /aggregate-metrics 30
# Example: /aggregate-metrics November

/system-status
# Show system health, data counts, configuration
```

#### Fetch Commands
```
/fetch-clarity-data
# Fetch latest data from Microsoft Clarity API
# Stores in database and creates JSON backups
```

#### Maintenance Commands
```
/aggregate-all [--force]
# Create weekly/monthly summaries from daily data
# Use --force to recalculate existing summaries

/list-data [--scope general|page] [--verbose]
# List all available data dates
# Shows date range and data counts
```

#### Reports Commands
```
/generate-summary <date_range>
# Generate comprehensive summary report (coming soon)
# Will use report generator with templates
```

### Advanced Analysis Scripts

Professional analysis tools for deep insights:

#### Report Generator
```bash
# Generate reports from templates
python scripts/report_generator.py <template> <date_range> [options]

# Templates:
# - ux-health             # Overall UX health report
# - frustration-analysis  # Frustration signals deep dive
# - device-performance    # Mobile/Desktop/Tablet comparison
# - geographic-insights   # Global reach and top markets
# - content-performance   # Page and category analysis
# - engagement-analysis   # Time, scroll, behavior metrics
# - page-analysis         # Single page deep dive (use --page)

# Examples:
python scripts/report_generator.py ux-health "last 7 days"
python scripts/report_generator.py frustration-analysis November
python scripts/report_generator.py page-analysis 30 --page /checkout

# Output: Markdown reports in reports/ directory
```

#### Period Comparator
```bash
# Compare two time periods
python scripts/comparator.py <period1> [period2] [options]

# Examples:
python scripts/comparator.py "last week"         # Auto-compares to previous week
python scripts/comparator.py 7                   # Last 7 days vs previous 7 days
python scripts/comparator.py November October    # Month-over-month
python scripts/comparator.py 2025-Q4 2025-Q3     # Quarter-over-quarter

# Shows:
# - Key metrics comparison (sessions, users, pageviews)
# - Improvements (positive changes)
# - Regressions (negative changes)
# - Overall trend (↑/↓/→)
```

#### Trend Analyzer
```bash
# Analyze long-term trends with statistics
python scripts/trend_analyzer.py <date_range> [options]

# Examples:
python scripts/trend_analyzer.py 30              # Last 30 days trend
python scripts/trend_analyzer.py "last month"    # Previous month
python scripts/trend_analyzer.py 2025            # Entire year
python scripts/trend_analyzer.py 90              # 90-day trend

# Shows:
# - Overall metrics (totals, averages, max/min)
# - Growth analysis (%, CAGR, daily average)
# - Volatility analysis (stability, coefficient of variation)
# - Trend detection (increasing/decreasing/stable with R²)
# - Pattern analysis (peaks, valleys, weekly cycles)
```

#### Archive Manager
```bash
# Manage data retention and archiving
python scripts/archive_manager.py <command> [options]

# Commands:
python scripts/archive_manager.py check          # Check for old data
python scripts/archive_manager.py archive [--format json|csv] [--dry-run]
python scripts/archive_manager.py delete [--dry-run]
python scripts/archive_manager.py cleanup [--dry-run]  # Archive + delete
python scripts/archive_manager.py list           # List archive files
python scripts/archive_manager.py restore <file> [--dry-run]

# Examples:
python scripts/archive_manager.py check
python scripts/archive_manager.py cleanup --dry-run  # See what would happen
python scripts/archive_manager.py cleanup            # Actually archive and delete
python scripts/archive_manager.py list
python scripts/archive_manager.py restore archive/archive_2025-10-15.json
```

### Legacy Scripts (Still Supported)

Original scripts that still work:

```bash
# Fetch data from Clarity API
python fetch_clarity_data.py

# Generate summary reports
python generate_summary.py

# Test configuration
python config.py

# Validate data
python validate_data.py
```

---

## 📊 Insights You'll Capture

**Behavioral Patterns:**
- Session flows, unique visitor trends, bot vs. human traffic
- Engagement depth (pages per session, time spent)
- Scroll behavior and content consumption patterns
- Navigation paths that reveal user intent

**Frustration Signals (Your UX Red Flags):**
- **Dead clicks** - Users clicking on elements they expect to be interactive
- **Rage clicks** - Rapid, frustrated clicking indicating broken functionality
- **Quick backs** - Users immediately abandoning pages (high bounce indicators)
- **JavaScript errors** - Technical issues disrupting user experience

**Audience Segmentation:**
- Device breakdown (Mobile, Desktop, Tablet)
- Browser analysis (Chrome, Safari, Firefox, Edge)
- Geographic insights (Country-level distribution)
- Cross-dimensional patterns (e.g., Mobile users in Germany vs. Desktop users in US)

**Data Storage (All Local, All Yours):**
- SQLite database for fast querying (`data/clarity_data.db`)
- Raw JSON archives for deep analysis (`data/raw/`)
- Ready-to-use CSV exports (`data/exports/`)

---

## 💡 Common Use Cases

### Daily Monitoring
```bash
# Set up a daily cron job to collect data
0 2 * * * cd /path/to/clarity-ux-insights && python fetch_clarity_data.py

# Weekly cleanup (archive old data beyond retention period)
0 3 * * 0 cd /path/to/clarity-ux-insights && python scripts/archive_manager.py cleanup
```

### Quick Data Checks
```bash
# Check system status and available data
python clarity_cli.py status

# Query last 7 days
python clarity_cli.py query 7

# Or use Claude Code:
/system-status
/query-data 7
```

### Compare Time Periods
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

### Analyze Trends
```bash
# 30-day trend analysis
python scripts/trend_analyzer.py 30

# Quarterly trend
python scripts/trend_analyzer.py 2025-Q4

# Full year analysis
python scripts/trend_analyzer.py 2025

# Shows: growth rate, CAGR, volatility, trend direction, patterns
```

### Generate Professional Reports
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

### Analyze Specific Issues with Claude
```bash
# Use Claude Code to analyze
Tell Claude: "Show me the devices with the highest frustration rates"
Tell Claude: "Which countries have the most dead clicks?"
Tell Claude: "Compare mobile vs desktop engagement"
Tell Claude: "What's the trend in rage clicks over the last month?"
```

### Export for Presentations
```bash
# Generate CSV files
python generate_summary.py

# Or archive data in CSV format
python scripts/archive_manager.py archive --format csv

# Files saved to data/exports/ or archive/ directory
```

### Query the Database
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

## 📚 Documentation

**Quick Start:**
- [Quick Start Guide](docs/QUICK-START.md) - Get started in 5 minutes
- [Complete System Overview](docs/README-SUMMARY.md) - Architecture and features
- [Date Format Reference](docs/DATE-FORMATS.md) - All 30+ supported date expressions

**Command References:**
- [All Commands](#-all-available-commands) - Complete command reference (above)
- [Unified CLI](#unified-cli-commands-recommended) - Modern interface commands
- [Claude Commands](#claude-slash-commands) - Slash commands for Claude Code
- [Advanced Tools](#advanced-analysis-scripts) - Professional analysis scripts

**Analysis Guides:**
- [Insights Guide](docs/clarity_insights_analysis.md) - Comprehensive analysis guide for UX/PM
- [Quick Reference](docs/clarity_quick_reference.md) - At-a-glance metrics and actions
- [API Features & Limitations](docs/features_and_limitations.md) - What you can and can't do

**Technical Documentation:**
- [Implementation Plan](implementation_plan.md) - Full technical implementation details
- [API Research](api_research.md) - Complete Clarity API research and capabilities
- [SECURITY.md](SECURITY.md) - Security guidelines and best practices

**Configuration Examples:**
- [E-commerce Configuration](examples/ecommerce-config.yaml)
- [SaaS Platform Configuration](examples/saas-config.yaml)
- [Media/Streaming Configuration](examples/media-streaming-config.yaml)

---

## 🔐 Security Important

**Never commit these files to git:**
- `.env` (contains your API token)
- `data/` directory (contains your analytics data)
- `*.db` files (your database)

**These are already protected by `.gitignore`**, but be aware:
- Your API token is sensitive - treat it like a password
- Regenerate your token if you suspect it's compromised
- Don't share your `.env` file

See [SECURITY.md](SECURITY.md) for complete security guidelines.

---

## 🚀 Why This Matters

**Turn ephemeral data into lasting insights:**

1. **Preserve Your History** - Clarity's API discards data after 3 days. This tool captures and preserves it indefinitely, building a historical record you can analyze across product cycles.

2. **Automate Intelligence Gathering** - Set up once, collect forever. Daily cron jobs capture insights while you sleep, building a comprehensive behavioral dataset.

3. **Analyze Without Limits** - Query, slice, export, and explore your data endlessly. No API rate limits, no restrictions. It's your data, stored locally.

4. **Spot Trends That Matter** - Compare week-over-week patterns, track month-over-month improvements, measure the impact of releases and design changes.

5. **Make Evidence-Based Decisions** - Replace opinions with observations. Replace assumptions with real user behavior data. Know what's working and what's frustrating users.

6. **Build Custom Insights** - Export to CSV for presentations, query the database for specific patterns, or build custom dashboards that answer your unique questions.

7. **Leverage AI Analysis** - Claude Code integration lets you ask natural language questions about your data and get instant insights without writing SQL.

---

## 🤝 Contributing

Found a bug? Have a feature request?

1. Check existing issues
2. Create a new issue with details
3. Or submit a pull request

---

## 👨‍💻 Author

Created by **[Parhum Khoshbakht](https://www.linkedin.com/in/parhumm/)**

Connect on LinkedIn for questions, feedback, or collaboration opportunities.

---

## 📄 License

This project is open source. Feel free to use and modify for your needs.

---

## 🆘 Troubleshooting

### Quick System Check
```bash
# Check everything at once (RECOMMENDED FIRST STEP)
python clarity_cli.py status

# Or use Claude Code:
/system-status
```

This shows:
- Project configuration
- Database health
- Available data range
- Any configuration issues

### API Connection Issues
```bash
# Test your connection
python config.py

# Check your token in .env file
cat .env | grep CLARITY_API_TOKEN

# Or check status
python clarity_cli.py status
```

### Database Issues
```bash
# Check database stats
python clarity_cli.py status

# List available data
python clarity_cli.py list --verbose

# Validate your data
python validate_data.py

# Re-initialize database if needed (CAUTION: This deletes data)
rm database/clarity_data.db
python fetch_clarity_data.py
```

### "No Data Found" Errors
```bash
# Check what data you have
python clarity_cli.py list

# Check date range
python clarity_cli.py status

# The date range might be outside your available data
# Try: python clarity_cli.py query 3  (for last 3 days)
```

### Date Format Not Recognized
```bash
# See all supported formats
cat docs/DATE-FORMATS.md

# Common formats that work:
# - Numbers: 7, 30, 90
# - Relative: yesterday, last-week, last-month
# - Months: November, 2025-11
# - Quarters: 2025-Q4, Q4 2025
# - Custom: "2025-11-01 to 2025-11-30"
```

### Using Claude Code for Help

Just tell Claude:
```
I'm getting an error with the Clarity API project
```

Then paste the error message. Claude can help debug and fix most issues.

Or try specific commands:
```
/system-status                    # Check system health
/list-data --verbose              # Show all available data
Tell Claude: "Help me debug this error: [paste error]"
```

---

**Questions?** Check the [docs](docs/) folder or create an issue on GitHub.

**Ready to start?** Jump to [Quick Start with Claude Code](#-quick-start-with-claude-code) 🚀
