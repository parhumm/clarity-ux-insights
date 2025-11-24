# Clarity API Integration & Insights Dashboard - Implementation Plan

**Project:** televika.com Clarity Analytics System
**Client:** UX Researcher & Product Manager
**Date:** 2025-11-24

---

## Executive Summary

This plan outlines the development of a Python-based system to fetch, analyze, and generate actionable UX/PM insights from Microsoft Clarity's Data Export API. The solution will overcome API limitations (10 requests/day, 3-day data window) by building a local historical database and providing automated insight generation.

---

## Project Goals

### Primary Objectives
1. **Automated Data Collection:** Daily fetching of Clarity metrics via API
2. **Historical Data Storage:** Overcome 3-day API limitation with local database
3. **Insight Generation:** Automated reports for UX research and product management
4. **Trend Analysis:** Week-over-week and month-over-month comparisons
5. **Export & Integration:** CSV/JSON exports for further analysis or BI tools

### Success Criteria
- Successfully authenticate and fetch data from Clarity API
- Store data with no loss or duplication
- Generate actionable insights automatically
- Reduce manual data analysis time by 80%
- Enable data-driven decision making for UX and product priorities

---

## System Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                   Clarity API Integration System             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐      ┌─────────────────┐              │
│  │  API Client    │─────▶│  Data Storage   │              │
│  │  - Auth        │      │  - SQLite DB    │              │
│  │  - Fetching    │      │  - Historical   │              │
│  │  - Rate Limit  │      │  - Backup       │              │
│  └────────────────┘      └─────────────────┘              │
│         │                        │                          │
│         │                        │                          │
│  ┌──────▼────────────────────────▼────────────┐            │
│  │        Data Processing & Analysis          │            │
│  │  - Aggregation                             │            │
│  │  - Trend Calculation                       │            │
│  │  - Insight Generation                      │            │
│  └────────────────┬───────────────────────────┘            │
│                   │                                         │
│         ┌─────────┴──────────┬─────────────┐              │
│         │                    │             │              │
│  ┌──────▼──────┐     ┌──────▼──────┐  ┌──▼───────┐       │
│  │ UX Reports  │     │ PM Reports  │  │ Exports  │       │
│  │ - Frustr.   │     │ - Traffic   │  │ - CSV    │       │
│  │ - Usability │     │ - Features  │  │ - JSON   │       │
│  │ - Behavior  │     │ - Errors    │  │ - Power BI│      │
│  └─────────────┘     └─────────────┘  └──────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

## Phase 1: API Client & Authentication (Day 1)

### Deliverables
- Python module for Clarity API authentication
- Request builder with parameter validation
- Error handling and retry logic
- Rate limit tracking (10 requests/day)

### Technical Details

**File:** `clarity_client.py`

**Key Functions:**
```python
class ClarityAPIClient:
    def __init__(self, api_token: str)
    def fetch_project_insights(self, num_days: int, dimensions: List[str])
    def get_remaining_requests(self) -> int
    def validate_dimensions(self, dimensions: List[str]) -> bool
```

**Features:**
- JWT Bearer token authentication
- Request builder with validation
- Automatic retry on transient errors
- Rate limit tracking (local file or DB)
- Response parsing and validation
- Detailed logging

**Testing:**
- Successful authentication test
- Invalid token handling
- Rate limit enforcement
- Network error handling
- Response parsing validation

### Environment Configuration

**File:** `.env`
```
CLARITY_API_TOKEN=your_jwt_token_here
CLARITY_PROJECT_ID=televika_project_id
API_BASE_URL=https://www.clarity.ms/export-data/api/v1
```

**File:** `config.py`
- Load environment variables
- Configuration validation
- Default settings

---

## Phase 2: Data Storage System (Day 1-2)

### Deliverables
- SQLite database schema
- Data access layer
- Duplicate prevention
- Backup system

### Database Schema

**File:** `database/schema.sql`

```sql
-- Main metrics table
CREATE TABLE clarity_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    recorded_date DATE NOT NULL,
    total_session_count INTEGER,
    total_bot_session_count INTEGER,
    distinct_user_count INTEGER,
    pages_per_session REAL,
    dimension1_name TEXT,
    dimension1_value TEXT,
    dimension2_name TEXT,
    dimension2_value TEXT,
    dimension3_name TEXT,
    dimension3_value TEXT,
    raw_json TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_name, recorded_date, dimension1_value, dimension2_value, dimension3_value)
);

-- Traffic metrics
CREATE TABLE traffic_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    total_sessions INTEGER,
    bot_sessions INTEGER,
    distinct_users INTEGER,
    pages_per_session REAL,
    new_users INTEGER,
    returning_users INTEGER,
    device TEXT,
    browser TEXT,
    country TEXT,
    os TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, device, browser, country, os)
);

-- Engagement metrics
CREATE TABLE engagement_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    avg_engagement_time REAL,
    avg_scroll_depth REAL,
    total_clicks INTEGER,
    device TEXT,
    page_url TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, device, page_url)
);

-- Frustration metrics
CREATE TABLE frustration_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    rage_clicks INTEGER,
    dead_clicks INTEGER,
    excessive_scrolling INTEGER,
    quick_backs INTEGER,
    error_clicks INTEGER,
    js_errors INTEGER,
    page_url TEXT,
    device TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, page_url, device)
);

-- API request log
CREATE TABLE api_request_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_date DATE NOT NULL,
    request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    num_days INTEGER,
    dimensions TEXT,
    status TEXT,
    error_message TEXT,
    rows_returned INTEGER
);

-- Daily sync status
CREATE TABLE sync_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sync_date DATE UNIQUE NOT NULL,
    sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT,
    records_inserted INTEGER,
    errors TEXT
);
```

**File:** `database/db_manager.py`

**Key Functions:**
```python
class DatabaseManager:
    def __init__(self, db_path: str)
    def insert_metrics(self, metrics: List[Dict])
    def get_metrics(self, start_date: str, end_date: str, filters: Dict)
    def check_duplicate(self, metric: Dict) -> bool
    def backup_database(self, backup_path: str)
    def get_date_range_available(self) -> Tuple[str, str]
```

**Features:**
- Duplicate prevention via UNIQUE constraints
- Indexed queries for fast retrieval
- Automatic date parsing
- Transaction support for batch inserts
- Daily backup functionality
- Data integrity validation

---

## Phase 3: Data Collection Orchestrator (Day 2-3)

### Deliverables
- Daily data fetching scheduler
- Strategic dimension selection
- Error recovery
- Progress tracking

### Strategic Data Collection Plan

**Daily Collection Strategy (Uses 6 of 10 requests):**

1. **Request 1:** Base metrics (no dimensions)
   - Overall traffic, engagement, frustration
   - Baseline for comparison

2. **Request 2:** Device dimension
   - Desktop vs Mobile vs Tablet behavior
   - Critical for UX research

3. **Request 3:** Country dimension
   - Geographic performance
   - Market insights

4. **Request 4:** Browser + Device (2 dimensions)
   - Detailed segmentation
   - Compatibility issues

5. **Request 5:** Source + Medium (2 dimensions)
   - Marketing attribution
   - Channel performance

6. **Request 6:** Page URL + Device (2 dimensions)
   - Page-specific behavior
   - Feature usage

**Reserve 4 requests for:**
- Ad-hoc analysis
- Troubleshooting
- Special reports
- Backfill missed days

**File:** `data_collector.py`

**Key Functions:**
```python
class DataCollector:
    def __init__(self, api_client: ClarityAPIClient, db_manager: DatabaseManager)
    def run_daily_collection(self) -> Dict
    def collect_base_metrics(self)
    def collect_device_breakdown(self)
    def collect_geographic_data(self)
    def collect_attribution_data(self)
    def backfill_missing_dates(self, start_date: str, end_date: str)
    def validate_collection(self, date: str) -> bool
```

**Features:**
- Sequential execution with delays
- Error handling per request
- Skip already-collected data
- Validation after each collection
- Detailed logging
- Email/notification on failure (optional)

---

## Phase 4: UX Research Insights Generator (Day 3-4)

### Deliverables
- Frustration analysis report
- Usability metrics dashboard
- Engagement analysis
- Cross-device comparison

### Reports & Insights

**File:** `insights/ux_insights.py`

#### 1. Frustration Analysis Report

**Metrics Included:**
- Rage clicks by page and device
- Dead clicks by element/page
- Quick backs rate
- Excessive scrolling patterns
- JavaScript error frequency

**Output Format:**
```
FRUSTRATION ANALYSIS REPORT
Generated: 2025-11-24
Date Range: Last 7 days

TOP 5 PAGES WITH RAGE CLICKS:
1. /checkout - 245 rage clicks (Desktop: 180, Mobile: 65)
2. /product/search - 123 rage clicks (Desktop: 89, Mobile: 34)
3. /account/settings - 98 rage clicks (Desktop: 70, Mobile: 28)
...

DEAD CLICK HOTSPOTS:
- /pricing page, "Compare Plans" button - 156 dead clicks
- /contact form, Submit button - 89 dead clicks
...

QUICK BACK RATE TREND:
Week 1: 12.3%
Week 2: 14.1% (↑ 14.6%)
Week 3: 11.8% (↓ 16.3%)

RECOMMENDATIONS:
1. [HIGH] Investigate checkout page rage clicks - potential payment issue
2. [MEDIUM] Review search functionality responsiveness
3. [LOW] Optimize account settings page load time
```

#### 2. Usability Metrics Dashboard

**Metrics Included:**
- Error rates by page
- Excessive scrolling by page
- Engagement time by feature
- Scroll depth analysis

**Output Format:**
```
USABILITY METRICS DASHBOARD
Generated: 2025-11-24

JAVASCRIPT ERRORS:
Total Errors: 1,234
Error Rate: 2.3% of sessions
Top Error Pages:
  - /dashboard: 456 errors (Browser: Chrome 340, Firefox 116)
  - /reports: 234 errors (Browser: Safari 180, Edge 54)

SCROLL DEPTH ANALYSIS:
Pages with Poor Below-Fold Visibility (<25% reach bottom):
  - /about-us: 18% scroll to bottom
  - /blog/article-xyz: 22% scroll to bottom

ENGAGEMENT TIME:
Highest Engagement:
  - /product-demo: 4m 32s avg
  - /documentation: 3m 18s avg
Lowest Engagement:
  - /terms: 0m 12s avg (expected)
  - /404: 0m 08s avg
```

#### 3. Engagement Analysis

**Metrics Included:**
- Time on site trends
- Pages per session
- Scroll depth by content type
- Click patterns

**Output Format:**
```
ENGAGEMENT ANALYSIS
Date Range: Last 30 days

OVERALL TRENDS:
Avg Session Duration: 3m 24s (↑ 8% vs prev month)
Pages per Session: 2.8 (→ 0% vs prev month)
Avg Scroll Depth: 64% (↑ 5% vs prev month)

DEVICE COMPARISON:
Desktop: 4m 12s avg, 3.4 pages/session
Mobile: 2m 18s avg, 2.1 pages/session
Tablet: 3m 45s avg, 2.9 pages/session

CONTENT ENGAGEMENT:
Most Engaging Content Types:
  - Tutorials: 5m 30s avg
  - Product Pages: 3m 45s avg
  - Blog Posts: 2m 58s avg

Least Engaging:
  - Error Pages: 0m 15s avg
  - Legal Pages: 0m 30s avg
```

#### 4. Cross-Device Comparison

**Metrics Included:**
- Behavior differences across devices
- Frustration signals by device
- Conversion rates by device (if available)

**Output Format:**
```
CROSS-DEVICE BEHAVIOR COMPARISON

FRUSTRATION SIGNALS:
                    Desktop    Mobile    Tablet
Rage Clicks           234       456       34
Dead Clicks           345       567       45
Quick Backs          12.3%     18.7%    14.2%

ENGAGEMENT:
                    Desktop    Mobile    Tablet
Avg Time            4m 12s    2m 18s    3m 45s
Pages/Session          3.4       2.1       2.9
Scroll Depth            68%       58%       65%

INSIGHT: Mobile users show 95% higher rage clicks and 52% higher quick back rate - investigate mobile UX issues urgently.
```

**Key Functions:**
```python
class UXInsightsGenerator:
    def __init__(self, db_manager: DatabaseManager)
    def generate_frustration_report(self, days: int = 7) -> str
    def generate_usability_dashboard(self, days: int = 30) -> str
    def generate_engagement_analysis(self, days: int = 30) -> str
    def generate_cross_device_comparison(self, days: int = 7) -> str
    def get_recommendations(self, report_type: str) -> List[str]
```

---

## Phase 5: Product Management Insights (Day 4-5)

### Deliverables
- Traffic & conversion metrics
- Feature usage analysis
- Geographic performance
- Channel attribution

### Reports & Insights

**File:** `insights/pm_insights.py`

#### 1. Traffic & Conversion Metrics

**Metrics Included:**
- Total sessions and users
- Bot traffic percentage
- User type breakdown (new vs returning)
- Session quality metrics

**Output Format:**
```
TRAFFIC & CONVERSION REPORT
Date Range: Last 30 days

OVERVIEW:
Total Sessions: 45,678 (↑ 12% vs prev month)
Distinct Users: 32,456 (↑ 8% vs prev month)
Bot Sessions: 2,345 (5.1% of total, ↓ 2% vs prev month)

USER ACQUISITION:
New Users: 18,234 (56.2%)
Returning Users: 14,222 (43.8%)
Return Rate: 43.8% (↑ 3% vs prev month)

SESSION QUALITY:
Avg Pages/Session: 2.8
Avg Duration: 3m 24s
Engagement Rate: 78.3% (sessions with >30s engagement)

TOP TRAFFIC SOURCES:
1. Organic Search: 18,456 sessions (40.4%)
2. Direct: 12,345 sessions (27.0%)
3. Social: 8,234 sessions (18.0%)
4. Referral: 4,567 sessions (10.0%)
5. Paid: 2,076 sessions (4.6%)
```

#### 2. Feature Usage Analysis

**Metrics Included:**
- Popular pages
- Inactive pages
- Feature adoption trends
- Click distribution

**Output Format:**
```
FEATURE USAGE ANALYSIS
Date Range: Last 30 days

MOST POPULAR PAGES:
1. /dashboard - 12,456 sessions (27.3% of total)
2. /products - 8,234 sessions (18.0%)
3. /search - 6,789 sessions (14.9%)
4. /account - 5,432 sessions (11.9%)
5. /reports - 3,456 sessions (7.6%)

UNDERUTILIZED FEATURES:
- /advanced-filters - 234 sessions (0.5%) - Consider redesign or deprecation
- /integrations - 456 sessions (1.0%) - Low adoption, needs promotion
- /analytics-export - 345 sessions (0.8%) - Niche feature

NEW FEATURE ADOPTION (if custom events tracked):
- Feature X (launched Week 1): 1,234 users (3.8% adoption)
  Week 1: 234 users
  Week 2: 456 users (↑ 95%)
  Week 3: 544 users (↑ 19%)

CLICK DISTRIBUTION:
Navigation Menu: 45.2% of clicks
CTAs: 23.8% of clicks
Content Links: 18.3% of clicks
Footer: 7.2% of clicks
Other: 5.5% of clicks
```

#### 3. Geographic Performance

**Metrics Included:**
- Traffic by country
- Engagement by region
- Market opportunities

**Output Format:**
```
GEOGRAPHIC PERFORMANCE
Date Range: Last 30 days

TOP 10 COUNTRIES BY TRAFFIC:
1. United States - 18,456 sessions (40.4%)
2. United Kingdom - 6,789 sessions (14.9%)
3. Canada - 4,567 sessions (10.0%)
4. Germany - 3,456 sessions (7.6%)
5. France - 2,345 sessions (5.1%)
...

ENGAGEMENT BY COUNTRY:
Highest Engagement:
  - Netherlands: 4m 56s avg, 3.8 pages/session
  - Sweden: 4m 32s avg, 3.6 pages/session
  - Denmark: 4m 18s avg, 3.4 pages/session

Lowest Engagement:
  - Country X: 1m 12s avg, 1.4 pages/session
  - Country Y: 1m 34s avg, 1.6 pages/session

GROWTH OPPORTUNITIES:
- Germany: High traffic but low engagement (2m 18s) - localization needed?
- Japan: Low traffic but high engagement (4m 45s) - marketing opportunity?
```

#### 4. Channel Attribution Report

**Metrics Included:**
- Performance by source/medium
- Campaign effectiveness
- Channel quality comparison

**Output Format:**
```
CHANNEL ATTRIBUTION REPORT
Date Range: Last 30 days

CHANNEL PERFORMANCE:
                    Sessions    Users    Pages/Sess    Avg Duration
Organic Search      18,456     14,234       3.2          4m 12s
Direct              12,345     10,234       2.8          3m 45s
Social               8,234      7,123       2.1          2m 18s
Referral             4,567      3,890       2.9          3m 22s
Paid (CPC)           2,076      1,890       2.3          2m 45s

BEST PERFORMING CAMPAIGNS (if UTM tracked):
1. summer_promo_2024 - 3,456 sessions, 4m 30s avg duration
2. product_launch_email - 2,345 sessions, 3m 55s avg duration
3. retargeting_campaign - 1,234 sessions, 3m 12s avg duration

CHANNEL QUALITY INSIGHTS:
- Organic Search: Highest quality (longest duration, most pages)
- Social: High volume but lower engagement - optimize landing pages
- Paid: Consider optimization - lower engagement than organic
```

**Key Functions:**
```python
class PMInsightsGenerator:
    def __init__(self, db_manager: DatabaseManager)
    def generate_traffic_report(self, days: int = 30) -> str
    def generate_feature_usage_report(self, days: int = 30) -> str
    def generate_geographic_report(self, days: int = 30) -> str
    def generate_attribution_report(self, days: int = 30) -> str
    def calculate_trends(self, metric: str, days: int) -> Dict
```

---

## Phase 6: Automated Reports & Exports (Day 5)

### Deliverables
- Weekly/monthly summary reports
- Trend analysis
- CSV/JSON exports
- Email delivery (optional)

**File:** `reporting/report_generator.py`

**Key Functions:**
```python
class ReportGenerator:
    def __init__(self, db_manager: DatabaseManager, ux_insights: UXInsightsGenerator, pm_insights: PMInsightsGenerator)
    def generate_weekly_report(self) -> str
    def generate_monthly_report(self) -> str
    def export_to_csv(self, data: List[Dict], filename: str)
    def export_to_json(self, data: Dict, filename: str)
    def generate_powerbi_export(self) -> str
    def send_email_report(self, recipients: List[str], report: str)
```

### Weekly Summary Report Template

```
═══════════════════════════════════════════════════════════
     CLARITY INSIGHTS - WEEKLY SUMMARY REPORT
═══════════════════════════════════════════════════════════

Report Period: Nov 17-23, 2025
Generated: Nov 24, 2025 08:00 AM UTC

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. EXECUTIVE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Sessions: 12,456 (↑ 8% WoW)
Distinct Users: 8,234 (↑ 5% WoW)
Avg Engagement: 3m 24s (↑ 12% WoW)

🔴 HIGH PRIORITY ISSUES: 2
🟡 MEDIUM PRIORITY: 4
🟢 LOW PRIORITY: 3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. UX INSIGHTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FRUSTRATION SIGNALS:
  Rage Clicks: 456 (↑ 23% WoW) ⚠️
  Dead Clicks: 234 (→ 0% WoW)
  Quick Backs: 14.2% (↑ 3% WoW) ⚠️

TOP USABILITY ISSUES:
  1. [HIGH] Checkout page rage clicks +45% - URGENT
  2. [HIGH] Mobile quick back rate 18.7% (vs 12.3% desktop)
  3. [MED] Search page dead clicks on filter buttons

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. PRODUCT INSIGHTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TRAFFIC TRENDS:
  Organic Search: 40.4% (↑ 5% WoW)
  Direct: 27.0% (→ 0% WoW)
  Social: 18.0% (↓ 8% WoW)

FEATURE ADOPTION:
  /dashboard: 27.3% of traffic
  /new-feature-x: 3.8% adoption (launched 3 weeks ago)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. RECOMMENDED ACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMMEDIATE (This Week):
  1. Investigate checkout page rage clicks
  2. Review mobile UX for quick back causes
  3. Test search filter button responsiveness

SHORT TERM (Next 2 Weeks):
  1. Promote underutilized /integrations feature
  2. Optimize social traffic landing pages (low engagement)
  3. Consider A/B test for new feature X placement

LONG TERM (This Month):
  1. Evaluate /advanced-filters for redesign or deprecation
  2. Improve below-fold content on /about-us page
  3. Expand marketing in high-engagement countries

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. DATA QUALITY NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Data Collection: ✓ Complete (7/7 days)
API Requests Used: 42 of 70 available
Bot Traffic Filtered: 5.1% of sessions
Data Freshness: Current (last sync: Nov 24, 2025 07:30 AM)

═══════════════════════════════════════════════════════════

For detailed analysis, visit Clarity Dashboard:
https://clarity.microsoft.com/projects/view/{project_id}/

Questions? Contact: [your email]
```

### Export Formats

**CSV Export (for Excel/Google Sheets):**
```
exports/
  ├── traffic_metrics_2025-11-24.csv
  ├── engagement_metrics_2025-11-24.csv
  ├── frustration_metrics_2025-11-24.csv
  └── geographic_metrics_2025-11-24.csv
```

**JSON Export (for Power BI/Custom Tools):**
```
exports/
  ├── weekly_summary_2025-11-24.json
  ├── monthly_summary_2025-11.json
  └── powerbi_feed.json (continuously updated)
```

**Power BI Format:**
```json
{
  "last_updated": "2025-11-24T08:00:00Z",
  "date_range": {
    "start": "2025-11-17",
    "end": "2025-11-23"
  },
  "metrics": [
    {
      "date": "2025-11-23",
      "total_sessions": 1840,
      "distinct_users": 1234,
      "avg_engagement_time": 204,
      "rage_clicks": 67,
      "dead_clicks": 34,
      "device": "Desktop"
    },
    ...
  ]
}
```

---

## Phase 7: Scheduling & Automation (Day 6)

### Deliverables
- Daily automated collection script
- Weekly report generation
- Error monitoring and alerts
- Health check dashboard

**File:** `scheduler/daily_run.py`

**Daily Schedule:**
```
00:00 UTC - Rate limit counter resets
01:00 UTC - Daily data collection starts
          - Collect yesterday's data (3 days ago for safety)
          - Run 6 strategic API requests
          - Store in database
          - Validate completeness
02:00 UTC - Data processing complete
          - Generate quick insights
          - Check for anomalies
          - Send alerts if issues detected

Every Monday 08:00 UTC - Weekly report generation
          - Generate UX insights report
          - Generate PM insights report
          - Create summary email
          - Export CSV files
          - Send to stakeholders

1st of Month 08:00 UTC - Monthly report generation
          - Comprehensive monthly analysis
          - Month-over-month trends
          - Executive summary
          - Export for Power BI
```

**Setup Methods:**

**Option 1: Cron (Linux/Mac)**
```bash
# Edit crontab
crontab -e

# Add daily collection at 1 AM UTC
0 1 * * * cd /path/to/clarity_api && /usr/bin/python3 scheduler/daily_run.py

# Add weekly report every Monday at 8 AM UTC
0 8 * * 1 cd /path/to/clarity_api && /usr/bin/python3 scheduler/weekly_report.py

# Add monthly report on 1st of month at 8 AM UTC
0 8 1 * * cd /path/to/clarity_api && /usr/bin/python3 scheduler/monthly_report.py
```

**Option 2: Windows Task Scheduler**
- Create scheduled tasks for each script
- Set appropriate triggers and actions

**Option 3: Python APScheduler (Cross-platform)**
```python
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

# Daily at 1 AM UTC
scheduler.add_job(run_daily_collection, 'cron', hour=1, minute=0)

# Weekly Monday 8 AM UTC
scheduler.add_job(run_weekly_report, 'cron', day_of_week='mon', hour=8, minute=0)

# Monthly 1st day 8 AM UTC
scheduler.add_job(run_monthly_report, 'cron', day=1, hour=8, minute=0)

scheduler.start()
```

**File:** `scheduler/health_check.py`

**Health Monitoring:**
- Check last successful data collection
- Verify API request quota
- Validate database integrity
- Monitor disk space
- Alert if issues detected

---

## Technology Stack

### Core Technologies

**Language:**
- Python 3.9+ (recommended 3.11 or 3.12)

**Essential Libraries:**
```
requests==2.31.0          # HTTP requests to Clarity API
python-dotenv==1.0.0      # Environment variable management
```

**Data Storage:**
```
sqlite3 (built-in)        # Lightweight database for historical data
```

**Data Processing:**
```
pandas==2.1.4            # Data manipulation and analysis
numpy==1.26.2            # Numerical computations
```

**Scheduling:**
```
apscheduler==3.10.4      # Job scheduling (optional, can use cron)
```

**Optional Enhancements:**
```
matplotlib==3.8.2        # Data visualization
plotly==5.18.0           # Interactive charts
jinja2==3.1.2            # HTML report templating
sendgrid==6.11.0         # Email delivery
openpyxl==3.1.2          # Excel export
```

### File Structure

```
clarity_api/
├── .env                          # Environment variables (API token, config)
├── .gitignore                    # Git ignore (exclude .env, database, etc.)
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies
├── config.py                     # Configuration management
│
├── clarity_client.py             # API client module
├── database/
│   ├── __init__.py
│   ├── schema.sql               # Database schema
│   ├── db_manager.py            # Database operations
│   └── migrations/              # Schema updates
│
├── data_collector.py            # Data collection orchestrator
├── insights/
│   ├── __init__.py
│   ├── ux_insights.py           # UX research insights
│   ├── pm_insights.py           # Product management insights
│   └── trend_analyzer.py        # Trend calculation
│
├── reporting/
│   ├── __init__.py
│   ├── report_generator.py      # Report generation
│   ├── templates/               # Report templates
│   │   ├── weekly_report.txt
│   │   └── monthly_report.txt
│   └── exporters.py             # CSV/JSON export
│
├── scheduler/
│   ├── __init__.py
│   ├── daily_run.py             # Daily collection script
│   ├── weekly_report.py         # Weekly report script
│   ├── monthly_report.py        # Monthly report script
│   └── health_check.py          # System health monitoring
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                # Logging configuration
│   ├── validators.py            # Input validation
│   └── helpers.py               # Utility functions
│
├── data/
│   ├── clarity_data.db          # SQLite database (gitignored)
│   └── backups/                 # Database backups (gitignored)
│
├── exports/
│   ├── csv/                     # CSV exports (gitignored)
│   ├── json/                    # JSON exports (gitignored)
│   └── reports/                 # Generated reports (gitignored)
│
├── logs/
│   ├── app.log                  # Application logs (gitignored)
│   ├── api_requests.log         # API request logs (gitignored)
│   └── errors.log               # Error logs (gitignored)
│
└── tests/
    ├── __init__.py
    ├── test_api_client.py
    ├── test_db_manager.py
    ├── test_data_collector.py
    └── test_insights.py
```

---

## Sample Usage

### Basic Usage

**1. Initial Setup:**
```bash
# Clone/create project
mkdir clarity_api
cd clarity_api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API token

# Initialize database
python -c "from database.db_manager import DatabaseManager; db = DatabaseManager(); db.init_database()"
```

**2. Manual Data Collection:**
```bash
# Collect data for the past 3 days
python data_collector.py --days 3

# Collect with specific dimensions
python data_collector.py --days 2 --dimensions Device,Country
```

**3. Generate Reports:**
```bash
# Generate weekly UX report
python reporting/report_generator.py --type ux --period weekly

# Generate monthly PM report
python reporting/report_generator.py --type pm --period monthly

# Export to CSV
python reporting/report_generator.py --export csv --output exports/
```

**4. Start Automated Scheduler:**
```bash
# Start background scheduler
python scheduler/daily_run.py &

# Or use cron (see Phase 7)
```

### Python API Usage

```python
from clarity_client import ClarityAPIClient
from database.db_manager import DatabaseManager
from insights.ux_insights import UXInsightsGenerator
from insights.pm_insights import PMInsightsGenerator

# Initialize
api_client = ClarityAPIClient(api_token="your_token")
db_manager = DatabaseManager(db_path="data/clarity_data.db")

# Collect data
from data_collector import DataCollector
collector = DataCollector(api_client, db_manager)
results = collector.run_daily_collection()

# Generate insights
ux_insights = UXInsightsGenerator(db_manager)
frustration_report = ux_insights.generate_frustration_report(days=7)
print(frustration_report)

pm_insights = PMInsightsGenerator(db_manager)
traffic_report = pm_insights.generate_traffic_report(days=30)
print(traffic_report)

# Export data
import pandas as pd
metrics = db_manager.get_metrics(
    start_date="2025-11-01",
    end_date="2025-11-24",
    filters={"device": "Desktop"}
)
df = pd.DataFrame(metrics)
df.to_csv("exports/desktop_metrics.csv", index=False)
```

---

## Testing Strategy

### Unit Tests

**Test Coverage:**
- API client authentication and requests
- Database operations (insert, query, duplicate prevention)
- Data validation and parsing
- Report generation
- Export functionality

**Run Tests:**
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test
python -m pytest tests/test_api_client.py
```

### Integration Tests

**Test Scenarios:**
1. End-to-end data collection
2. Multi-day backfill
3. Report generation with real data
4. Export format validation
5. Scheduler execution

### Manual Testing Checklist

- [ ] API authentication successful
- [ ] Data fetched and stored correctly
- [ ] No duplicate records created
- [ ] Reports generate without errors
- [ ] CSV/JSON exports valid
- [ ] Email delivery works (if enabled)
- [ ] Scheduler runs at correct times
- [ ] Error handling and logging working
- [ ] Rate limit tracking accurate
- [ ] Database backup successful

---

## Error Handling & Monitoring

### Error Scenarios

**1. API Errors:**
- Authentication failure → Retry once, then alert
- Rate limit exceeded → Log and skip, resume next day
- Network timeout → Retry up to 3 times with exponential backoff
- Invalid response → Log error, continue with other requests

**2. Database Errors:**
- Duplicate insert → Skip silently (expected behavior)
- Disk space full → Alert immediately, stop collection
- Database corruption → Restore from backup, alert

**3. Scheduling Errors:**
- Missed scheduled run → Run on next opportunity, log warning
- Long-running job → Timeout after 30 minutes, alert
- Concurrent execution → Prevent with lock file

### Logging Strategy

**Log Levels:**
- DEBUG: API requests/responses, database queries
- INFO: Successful collections, report generation
- WARNING: Retries, skipped requests, minor issues
- ERROR: Failed collections, invalid data
- CRITICAL: System failures, data loss risk

**Log Rotation:**
- Daily rotation
- Keep 30 days of logs
- Compress old logs

### Alerting (Optional)

**Alert Triggers:**
- Failed data collection 2 days in a row
- API rate limit exceeded
- Database errors
- Disk space < 10%
- No data collected in 48 hours

**Alert Methods:**
- Email notification
- Slack webhook
- SMS (via Twilio)
- Log monitoring service (e.g., Sentry)

---

## Security Considerations

### API Token Security

**Best Practices:**
- Store token in `.env` file (never commit to git)
- Use environment variables in production
- Rotate token periodically
- Restrict token permissions to Data Export only
- Use separate tokens for dev/prod

**Example `.env`:**
```bash
# Clarity API Configuration
CLARITY_API_TOKEN=your_jwt_token_here
CLARITY_PROJECT_ID=televika_project_id

# Database
DB_PATH=data/clarity_data.db
BACKUP_PATH=data/backups/

# Reporting
REPORTS_PATH=exports/reports/
CSV_EXPORT_PATH=exports/csv/
JSON_EXPORT_PATH=exports/json/

# Email (optional)
EMAIL_ENABLED=false
SENDGRID_API_KEY=your_sendgrid_key
EMAIL_FROM=reports@televika.com
EMAIL_TO=your.email@televika.com

# Scheduling
COLLECTION_TIME_UTC=01:00
WEEKLY_REPORT_DAY=monday
MONTHLY_REPORT_DAY=1
```

### Data Privacy

**Considerations:**
- Clarity data is aggregated (no PII in API responses)
- Session recordings not exported (only metadata)
- Local database should be secured (file permissions)
- Backup encryption recommended
- Access control on reports

### Access Control

**Recommendations:**
- Restrict file system access to authorized users
- Use read-only database connections where possible
- Secure report output directories
- Audit log access

---

## Performance Optimization

### Database Optimization

**Indexes:**
```sql
CREATE INDEX idx_metrics_date ON clarity_metrics(recorded_date);
CREATE INDEX idx_traffic_date_device ON traffic_metrics(date, device);
CREATE INDEX idx_frustration_date_page ON frustration_metrics(date, page_url);
```

**Query Optimization:**
- Use date range filters
- Limit result sets
- Use aggregation in SQL when possible
- Cache frequently accessed data

### API Request Optimization

**Strategies:**
- Batch data collection
- Avoid redundant requests
- Cache responses temporarily
- Strategic dimension selection
- Skip already-collected dates

### Report Generation Optimization

**Techniques:**
- Generate reports asynchronously
- Cache intermediate calculations
- Use database views for common queries
- Incremental updates vs full regeneration

---

## Maintenance & Support

### Daily Maintenance

- Monitor data collection success
- Check log files for errors
- Verify disk space
- Review API request quota usage

### Weekly Maintenance

- Review generated reports
- Check data quality
- Backup database
- Update documentation if needed

### Monthly Maintenance

- Analyze historical trends
- Optimize database (VACUUM)
- Review and adjust collection strategy
- Update dependencies if needed
- Test disaster recovery

### Quarterly Maintenance

- Security review (token rotation)
- Performance optimization
- Feature additions based on needs
- Documentation updates

---

## Future Enhancements

### Phase 8: Advanced Features (Optional)

**1. Power BI Direct Integration**
- REST API endpoint to serve data to Power BI
- Real-time dashboard refresh
- Custom DAX measures

**2. Machine Learning Insights**
- Anomaly detection (unusual patterns)
- Predictive analytics (forecast trends)
- User segmentation clustering
- Churn prediction

**3. Custom Alerting**
- Threshold-based alerts (e.g., rage clicks > 100/day)
- Pattern detection alerts
- Slack/Teams integration
- Mobile app notifications

**4. Interactive Dashboard**
- Web-based UI for report viewing
- Real-time metrics display
- Drill-down capabilities
- Custom date range selection
- Flask or FastAPI backend

**5. Integration with Other Tools**
- Google Analytics data merge
- Jira ticket creation from insights
- Confluence documentation sync
- GitHub issue tracking

**6. Advanced Visualizations**
- Heatmap-style visualizations
- Trend charts and graphs
- Geographic maps
- Funnel visualizations

---

## Success Metrics

### System Performance

- **Data Collection Success Rate:** > 95%
- **API Request Efficiency:** Use all 10 daily requests strategically
- **Report Generation Time:** < 5 minutes
- **Data Freshness:** < 24 hours old
- **System Uptime:** > 99%

### Business Impact

- **Time Saved:** 80% reduction in manual data analysis
- **Issue Detection Time:** Identify UX issues within 24 hours
- **Data-Driven Decisions:** 100% of UX/PM decisions backed by data
- **Insight Actionability:** > 70% of recommendations implemented

---

## Estimated Timeline

**Total Duration:** 6-7 days

- **Day 1:** API Client & Database Setup (Phase 1-2)
- **Day 2-3:** Data Collection & Storage (Phase 3)
- **Day 3-4:** UX Insights Generation (Phase 4)
- **Day 4-5:** PM Insights Generation (Phase 5)
- **Day 5:** Reporting & Exports (Phase 6)
- **Day 6:** Scheduling & Automation (Phase 7)
- **Day 7:** Testing, Documentation, Training

---

## Deliverables Checklist

### Core System
- [x] API authentication module
- [x] Database schema and manager
- [x] Data collection orchestrator
- [x] Strategic dimension collection plan

### Insights
- [x] UX frustration analysis
- [x] UX usability metrics
- [x] UX engagement analysis
- [x] UX cross-device comparison
- [x] PM traffic & conversion report
- [x] PM feature usage analysis
- [x] PM geographic performance
- [x] PM channel attribution

### Automation
- [x] Daily collection scheduler
- [x] Weekly report generator
- [x] Monthly report generator
- [x] Error handling and logging
- [x] Health check monitoring

### Exports
- [x] CSV export functionality
- [x] JSON export functionality
- [x] Power BI compatible format
- [x] Email delivery (optional)

### Documentation
- [x] Setup instructions (README.md)
- [x] Configuration guide
- [x] Usage examples
- [x] API documentation
- [x] Troubleshooting guide

---

## Getting Started

After plan approval, the implementation will proceed in the order outlined above. Each phase builds on the previous one, ensuring a solid foundation before adding complexity.

**First Steps:**
1. Confirm API token is valid and has Data Export permissions
2. Verify Python 3.9+ is installed
3. Confirm project directory location
4. Review strategic dimension collection plan
5. Clarify reporting preferences (email delivery, format, etc.)

**Questions to Address:**
- Preferred report delivery method (file, email, dashboard)?
- Specific pages or features to prioritize in analysis?
- Any custom events or tags already implemented in Clarity?
- Preferred schedule for automated reports?
- Any integration requirements (Power BI, other tools)?

---

## Contact & Support

For questions during implementation or after deployment:
- Review documentation in README.md
- Check logs in `logs/` directory
- Consult Microsoft Clarity docs: https://learn.microsoft.com/en-us/clarity/
- Contact project developer: [your contact info]

---

**Plan Status:** Ready for Implementation
**Last Updated:** 2025-11-24
**Version:** 1.0
