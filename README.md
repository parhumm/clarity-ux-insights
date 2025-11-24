# Clarity API Data Collection & Analysis

A Python-based system to fetch, store, and analyze data from Microsoft Clarity's Data Export API for televika.com.

## 🎯 Project Overview

This project collects behavioral analytics data from Microsoft Clarity API and provides insights for UX research and product management decisions.

### What Data is Collected

- **Sessions & Users:** Total sessions, bot sessions, distinct users
- **Engagement:** Pages per session, scroll depth, engagement time
- **Frustration Signals:** Rage clicks, dead clicks, quick backs, excessive scrolling
- **Errors:** JavaScript errors, error clicks
- **Dimensions:** Device, Country, Browser, and cross-segmentations
- **Traffic:** Popular pages, referrers, page titles

## 📊 Key Results (Last 3 Days)

### Overall Statistics
- **Total Sessions:** 6,562
- **Bot Sessions:** 274 (4.2%)
- **Distinct Users:** 4,235
- **Avg Pages/Session:** 2.94
- **Avg Scroll Depth:** 89.4%

### Device Distribution
- Mobile: 47.5%
- PC: 24.0%
- Desktop: 13.2%
- Other: 10.0%
- Tablet: 5.3%

### Top 3 Countries
1. Germany: 21.0%
2. United States: 13.9%
3. Turkey: 12.7%

### Top 3 Browsers
1. Chrome Mobile: 26.8%
2. Chrome: 25.0%
3. Mobile Safari: 22.4%

### Frustration Metrics (UX Insights)
- **Dead Clicks:** 2,913 total (12.18% of sessions affected)
  - 983 unique pages with dead clicks
  - Indicates elements users expect to be clickable but aren't

- **Quick Backs:** 3,674 total (28.64% of sessions affected)
  - Users navigating away and returning quickly
  - Suggests unmet expectations or confusing navigation

- **Rage Clicks:** 896 total (0.52% of sessions)
  - Rapid clicking on unresponsive elements
  - Sign of significant user frustration

- **Script Errors:** 239 total (1.69% of sessions)
  - JavaScript errors affecting user experience
  - 143 unique pages with errors

- **Excessive Scrolling:** 1 occurrence (0.02% of sessions)
  - Very rare, indicating good content organization

## 🗂 Project Structure

```
clarity_api/
├── .env                              # API token (not in git)
├── .gitignore                        # Git ignore file
├── config.py                         # Configuration management
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
│
├── clarity_client.py                 # API client module
├── fetch_clarity_data.py             # Main data collection script
├── generate_summary.py               # Summary report generator
├── validate_data.py                  # Data validation script
│
├── database/
│   ├── schema.sql                    # Database schema
│   └── db_manager.py                 # Database operations
│
├── data/
│   ├── raw/                          # Raw JSON responses (6 files)
│   │   ├── base_metrics_3days.json
│   │   ├── by_device_3days.json
│   │   ├── by_country_3days.json
│   │   ├── by_browser_3days.json
│   │   ├── device_browser_3days.json
│   │   └── country_device_3days.json
│   │
│   ├── exports/                      # CSV exports
│   │   ├── summary_last_3_days.csv
│   │   ├── device_summary.csv
│   │   ├── country_summary.csv
│   │   └── browser_summary.csv
│   │
│   └── clarity_data.db               # SQLite database (3,384 records)
│
├── clarity_api_research.md           # Comprehensive API research
└── clarity_api_implementation_plan.md # Implementation plan
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Clarity API token (Data Export scope)

### Installation

1. **Clone/Navigate to Project:**
   ```bash
   cd /Users/parhumm/Projects/clarity_api
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   The `.env` file is already set up with your API token.

4. **Test Configuration:**
   ```bash
   python config.py
   ```

## 📥 Data Collection

### Fetch All Data (Recommended)

Run the complete data collection (6 API calls):

```bash
python fetch_clarity_data.py
```

This will:
- ✅ Fetch base metrics (no dimensions)
- ✅ Fetch device breakdown
- ✅ Fetch country breakdown
- ✅ Fetch browser breakdown
- ✅ Fetch device+browser cross-segmentation
- ✅ Fetch country+device cross-segmentation
- ✅ Save raw JSON files to `data/raw/`
- ✅ Store parsed data in SQLite database
- ✅ Log all API requests

**Expected Output:**
```
✅ Successful: 6/6
📊 Total metrics: 3,384 records
📊 API requests: 6/10 daily quota used
```

### Test API Connection Only

```bash
python clarity_client.py
```

## 📊 Generate Reports

### Summary Report

Generate comprehensive summary with CSV exports:

```bash
python generate_summary.py
```

**Outputs:**
- Console summary with key metrics
- `data/exports/summary_last_3_days.csv` (full data)
- `data/exports/device_summary.csv`
- `data/exports/country_summary.csv`
- `data/exports/browser_summary.csv`

### Validate Data

Verify data completeness and quality:

```bash
python validate_data.py
```

**Checks:**
- ✅ All 6 JSON files present and valid
- ✅ Database records complete (3,384 total)
- ✅ All dimension types present
- ✅ CSV exports generated
- ✅ Duplicate rate acceptable (<5%)

## 🔧 API Details

### Authentication
- **Method:** JWT Bearer Token
- **Header:** `Authorization: Bearer <token>`
- **Scope:** Data.Export

### Rate Limits
- **Max Requests:** 10 per project per day
- **Current Usage:** 6 requests (4 remaining)
- **Counter Resets:** Midnight UTC

### Data Range
- **Days per Request:** 1-3 days
- **Current Collection:** 3 days (Nov 21-24, 2025)

### Available Dimensions
- Device (Desktop, Mobile, Tablet, Other)
- Country (geographic distribution)
- Browser (Chrome, Safari, Firefox, etc.)
- OS (Operating System)
- Source/Medium (traffic attribution)
- Page URL, Page Title, Referrer

## 💾 Database Schema

### Main Tables

**clarity_metrics** - All collected metrics
- Primary key: auto-increment ID
- Unique constraint on metric+dimensions
- Stores raw JSON for flexibility

**api_requests** - Request log
- Tracks all API calls
- Success/failure status
- Response metadata

### Query Examples

```python
from database.db_manager import DatabaseManager

db = DatabaseManager()

# Get all device metrics
device_metrics = db.get_metrics(dimension1="Device")

# Get statistics
stats = db.get_statistics()
print(f"Total records: {stats['total_metrics']}")

# Get specific metric
all_metrics = db.get_metrics(metric_name="DeadClickCount")
```

## 📈 Key Insights for UX Research

### High Priority Issues

1. **Dead Clicks (12.18% of sessions)**
   - Most affected page: `/asparagus/` (226 visits)
   - Issue: Users clicking on non-interactive elements
   - Recommendation: Review UI elements that look clickable

2. **Quick Backs (28.64% of sessions)**
   - 3,674 quick back events
   - Issue: Users not finding expected content
   - Recommendation: Review navigation labels and page content

3. **Mobile Experience**
   - 47.5% of traffic is mobile
   - Consider mobile-specific UX improvements
   - Test responsive design thoroughly

### Positive Indicators

1. **Low Rage Clicks (0.52%)**
   - Only 896 events across 6,562 sessions
   - Indicates generally responsive UI

2. **Excellent Scroll Depth (89.4%)**
   - Users engaging with content
   - Content is relevant and well-organized

3. **Low Excessive Scrolling (0.02%)**
   - Content is findable
   - Good information architecture

## 🛠 Development

### Add New Dimensions

Edit `fetch_clarity_data.py` and add to collections list:

```python
{
    'name': 'OS Breakdown',
    'dimension1': 'OS',
    'dimension2': None,
    'dimension3': None,
    'filename': 'by_os_3days.json'
}
```

### Custom Analysis

```python
from database.db_manager import DatabaseManager
import pandas as pd

db = DatabaseManager()
metrics = db.get_metrics()
df = pd.DataFrame(metrics)

# Your custom analysis here
mobile_data = df[df['dimension1_value'] == 'Mobile']
print(mobile_data['pages_per_session'].mean())
```

## 📚 Additional Resources

- **API Research:** See [clarity_api_research.md](clarity_api_research.md)
- **Implementation Plan:** See [clarity_api_implementation_plan.md](clarity_api_implementation_plan.md)
- **Official Docs:** https://learn.microsoft.com/en-us/clarity/

## 🔐 Security Notes

- ✅ API token stored in `.env` (not committed to git)
- ✅ Data files excluded from git (in `.gitignore`)
- ✅ Client-side hashing for custom IDs
- ✅ No PII collected (aggregated data only)

## 📝 Git History

### Commits Made

1. `feat: initialize project with configuration and dependencies`
2. `feat: add database schema and manager with SQLite storage`
3. `feat: implement Clarity API client with authentication and error handling`
4. `feat: fetch and store all Clarity metrics for last 3 days`
5. `feat: generate summary report from collected data`
6. `feat: add validation and documentation`

## 🎓 Next Steps

### For UX Research
1. Review dead click pages and identify UI improvements
2. Investigate quick back patterns on key pages
3. Analyze mobile vs desktop behavior differences
4. Create heatmaps in Clarity dashboard for visual analysis

### For Product Management
1. Monitor frustration metrics after each release
2. Track device distribution trends over time
3. Analyze geographic expansion opportunities
4. Set up automated daily data collection

### For Further Development
1. **Automated Scheduling:** Set up cron job for daily collection
2. **Alerting:** Email notifications for metric spikes
3. **Dashboard:** Build web-based visualization dashboard
4. **Power BI:** Connect database for executive reporting
5. **Trend Analysis:** Compare week-over-week and month-over-month
6. **ML Insights:** Anomaly detection and predictive analytics

## 🐛 Troubleshooting

### API Connection Issues
```bash
# Test connection
python clarity_client.py

# Check token validity
python config.py
```

### Database Issues
```bash
# Re-initialize database
rm data/clarity_data.db
python -m database.db_manager
```

### Missing Data
```bash
# Re-fetch data
python fetch_clarity_data.py

# Validate
python validate_data.py
```

## 📞 Support

- **Clarity Documentation:** https://learn.microsoft.com/en-us/clarity/
- **API Reference:** https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-data-export-api
- **Project Issues:** Review git log for implementation details

---

**Last Updated:** 2025-11-24
**Data Coverage:** Last 3 days (Nov 21-24, 2025)
**Total Records:** 3,384 metrics across 6 API calls
**Status:** ✅ Operational & Validated
