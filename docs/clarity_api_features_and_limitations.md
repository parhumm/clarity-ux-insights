# Microsoft Clarity API: Features & Limitations Guide

**Document Version:** 1.0
**Last Updated:** November 25, 2024
**Purpose:** Comprehensive reference for Clarity API capabilities and constraints

---

## Table of Contents

1. [Overview](#overview)
2. [API Features - What IS Possible](#api-features---what-is-possible)
3. [API Limitations - What IS NOT Possible](#api-limitations---what-is-not-possible)
4. [Specific Questions Answered](#specific-questions-answered)
5. [API Constraints & Rate Limits](#api-constraints--rate-limits)
6. [Practical Workarounds](#practical-workarounds)
7. [Code Examples](#code-examples)
8. [Quick Reference Table](#quick-reference-table)
9. [Recommendations](#recommendations)

---

## Overview

The Microsoft Clarity API provides programmatic access to **aggregated analytics data** from your Clarity projects. This document clarifies exactly what you can and cannot do with the API, based on actual implementation experience and official documentation.

**Primary API Endpoint Used:**
```
GET https://www.clarity.ms/export-data/api/v1/project-live-insights
```

**Authentication:** Cookie-based authentication (required headers in requests)

---

## API Features - What IS Possible

### ✅ 1. Aggregated Dashboard Metrics

**Available Metrics:**
- **Traffic Metrics:**
  - Total sessions
  - Unique users (distinct user count)
  - Bot sessions (filtered automatically)
  - Pages per session

- **Engagement Metrics:**
  - Total engagement time
  - Active engagement time
  - Scroll depth (average scroll percentage)
  - Time on site

- **Frustration Signals:**
  - Dead clicks (clicks on non-interactive elements)
  - Rage clicks (rapid repeated clicks)
  - Quick backs (immediate exit after arrival)
  - Excessive scrolling
  - Error clicks

- **Technical Metrics:**
  - JavaScript errors (script error count)
  - Error details and frequencies

**Data Format:** JSON

**Example Response Structure:**
```json
{
  "success": true,
  "status_code": 200,
  "data": [
    {
      "metricName": "Traffic",
      "information": [
        {
          "totalSessionCount": "6562",
          "totalBotSessionCount": "274",
          "distinctUserCount": "4235",
          "pagesPerSessionPercentage": 2.94
        }
      ]
    }
  ]
}
```

---

### ✅ 2. Multi-Dimensional Analysis

**Supported Dimensions (Up to 3 per request):**

**Device Dimensions:**
- Device type (Mobile, PC, Tablet, Other)
- Browser (Chrome, Safari, Firefox, Edge, etc.)
- Operating System (iOS, Android, Windows, MacOSX, Linux)

**Geographic Dimensions:**
- Country (130+ countries)
- Region/State (if available)

**Content Dimensions:**
- Page URL (page path)
- Page Title
- Referrer URL

**User Dimensions:**
- User ID (if custom tracking implemented)
- Custom tags/events

**Example Request:**
```python
# Request traffic data broken down by country and device
result = client.fetch_project_insights(
    num_days=3,
    dimension1='Country',
    dimension2='Device',
    dimension3=None
)
```

**Response:** All combinations of Country × Device with metrics for each

---

### ✅ 3. Historical Data Access

**Via API:**
- 1-3 days per request (configurable)
- Rolling window (always relative to current date)

**Via Dashboard:**
- 12-month visitor history
- Long-term trend analysis
- Extended retention for selected recordings

**Best Practice:**
- Use API for regular data collection
- Store locally for historical analysis
- Build your own time-series database (like the SQLite implementation in this project)

---

### ✅ 4. Bot Traffic Filtering

- Automatic bot detection and separation
- `totalBotSessionCount` provided in metrics
- Clean human-only metrics available
- Transparency in bot vs. human traffic

---

### ✅ 5. Cross-Device & Cross-Browser Tracking

- 12-month visitor journey continuity
- Track users across devices
- Consistent user identity
- Seamless experience tracking

---

### ✅ 6. Custom Event Tracking

**JavaScript API Available:**
```javascript
// Track custom events
window.clarity('event', 'button_clicked');
window.clarity('set', 'user_type', 'premium');
window.clarity('identify', 'user_12345');
```

**Use Cases:**
- Button clicks
- Form submissions
- Custom user actions
- Business-specific events
- Conversion tracking

**Retrieval:** Events appear in dashboard and can be used for segmentation

---

### ✅ 7. Multiple Heatmap Types (Dashboard Only)

**Available Heatmap Visualizations:**
- **Click Maps:** Where users click
- **Scroll Maps:** How far users scroll
- **Area Maps:** Attention distribution
- **Conversion Maps:** User path to conversion
- **Attention Maps:** Time spent on elements

**Export Format:** PNG/Image only (manual download from dashboard)

---

## API Limitations - What IS NOT Possible

### ❌ 1. Direct Page URL Filtering

**What You Cannot Do:**
```python
# This type of direct filtering is NOT supported
result = client.fetch_project_insights(
    num_days=3,
    page_url_filter='/checkout'  # ❌ NOT AVAILABLE
)
```

**Why:** The API doesn't accept query parameters for filtering by specific pages.

**Workaround:** Request data with URL as a dimension, then filter locally (see Workarounds section).

---

### ❌ 2. Heatmap Data Export via API

**What You Cannot Do:**
- Download heatmap data as CSV
- Get pixel coordinates of clicks programmatically
- Export click intensity maps as data
- Access scroll map data via API
- Retrieve heatmap metrics in JSON format

**What You CAN Do:**
- View heatmaps in Clarity dashboard
- Manually export heatmap images (PNG)
- Get aggregated click counts (but not coordinates)
- Share heatmap URLs with team members

**Why:** Heatmap visualization data is only available through the dashboard UI.

---

### ❌ 3. Session Recording Access via API

**What You Cannot Do:**
- Download session recording video files
- Stream recordings programmatically
- Export recording data via API
- Access individual session playback data
- Automate recording analysis

**What You CAN Do:**
- Get shareable links to recordings
- View recordings in Clarity UI
- Filter recordings by criteria (device, frustration, etc.)
- Get session metadata (duration, pages visited, device type)
- Manually review sessions in dashboard

**Why:** Session recordings are visual reconstructions (not videos) that are only viewable through the Clarity web interface.

---

### ❌ 4. Individual Session-Level Data

**What You Cannot Do:**
- Export raw session data via API
- Get click-by-click user actions programmatically
- Access granular user behavior data
- Retrieve individual session metrics

**What You CAN Do:**
- Get aggregated metrics across sessions
- Filter sessions by dimensions
- View individual sessions in dashboard
- Get session counts and percentages

**Why:** API provides only aggregated data, not individual session details.

---

### ❌ 5. Raw Click Coordinates

**What You Cannot Do:**
- Get X/Y pixel coordinates of clicks
- Export mouse movement paths
- Access raw interaction data
- Build custom heatmaps from API data

**What You CAN Do:**
- View pre-built heatmaps in dashboard
- Get aggregated click counts
- Identify elements receiving clicks (via dashboard)

**Why:** Clarity uses element-based tracking, not raw coordinate capture.

---

### ❌ 6. Unlimited Historical Data via API

**What You Cannot Do:**
- Request more than 3 days of data per API call
- Access unlimited historical data programmatically
- Get multi-month trends in single request

**What You CAN Do:**
- Request up to 3 days per call
- Make multiple calls for different time periods (within rate limits)
- Store data locally for historical analysis
- View 12 months of history in dashboard

**Why:** API has a 3-day maximum per request to manage performance and cost.

---

### ❌ 7. Video File Export

**What You Cannot Do:**
- Download session recordings as MP4/video files
- Save recordings locally
- Archive recordings as videos

**What You CAN Do:**
- View recordings in Clarity UI indefinitely (with extended retention)
- Share recording URLs
- Screenshot or screen-record your review (manual process)

**Why:** Recordings are DOM reconstructions, not actual video captures.

---

## Specific Questions Answered

### Q1: Is it possible to filter and get data of a specific page URL?

**Answer:** ⚠️ **PARTIALLY POSSIBLE**

**What Works:**
```python
# Request data with URL as a dimension
result = client.fetch_project_insights(
    num_days=3,
    dimension1='URL',  # Get all pages
    dimension2=None,
    dimension3=None
)

# Then filter locally in your code
checkout_data = [
    item for item in result['data']
    if '/checkout' in item.get('dimension1_value', '')
]
```

**Limitations:**
- Cannot filter at API level
- Must retrieve all pages, then filter locally
- May hit 1,000 row limit if you have many pages
- More data transfer than necessary

**Best Practice:**
- Request URL dimension for comprehensive page analysis
- Store in local database (as implemented in this project)
- Query local database for specific pages

---

### Q2: Is it possible to download heatmap CSV with API?

**Answer:** ❌ **NOT POSSIBLE**

**Why:**
- API only provides aggregated metrics (JSON)
- Heatmap data is visual, not tabular
- Pixel/coordinate data not exposed via API

**Alternative:**
1. Use Clarity dashboard to view heatmaps
2. Manually export heatmap images (PNG)
3. Get aggregated click metrics via API (counts, not coordinates)
4. Consider implementing custom click tracking if you need programmatic access

**What You DO Get via API:**
- Dead click counts
- Rage click counts
- Total click metrics
- Scroll depth percentages

But **NOT:**
- Click coordinates
- Click heatmap visualizations
- Pixel-level interaction data

---

### Q3: Do you have access to session recordings with API?

**Answer:** ❌ **NOT POSSIBLE**

**Why:**
- Session recordings are only viewable in Clarity UI
- No API endpoint for recording retrieval
- Recordings are DOM reconstructions, not exportable files

**What You CAN Do:**
1. **Identify problem sessions via API:**
   ```python
   # Get sessions with high frustration
   result = client.fetch_project_insights(
       num_days=3,
       dimension1='Device'
   )
   # Check for high RageClickCount, DeadClickCount
   ```

2. **Manually review in Clarity dashboard:**
   - Filter by device, date, frustration signals
   - Watch specific sessions
   - Take notes for analysis

3. **Get recording metadata:**
   - Session duration
   - Pages visited
   - Device/browser info
   - Frustration signals

**Workflow:**
```
API → Identify problematic sessions → Dashboard → Watch recordings → Document findings
```

---

## API Constraints & Rate Limits

### Rate Limits

| Constraint | Limit | Notes |
|------------|-------|-------|
| **Requests per day** | 10 per project | Counter resets at midnight UTC |
| **Historical data** | 3 days max per request | Cannot request 4+ days in single call |
| **Response rows** | 1,000 rows max | May truncate if many dimension combinations |
| **Dimensions per request** | 3 maximum | dimension1, dimension2, dimension3 |
| **Session recordings** | 100,000 per project/day | Capture limit |
| **Recording retention** | 30 days standard | Extended retention available |

### Data Freshness

- **API data:** Near real-time (minutes delay)
- **Dashboard data:** Real-time
- **Historical data:** Updated continuously

### Request Guidelines

**Recommended Usage:**
```python
# Good: Request complementary dimensions
client.fetch_project_insights(
    num_days=3,
    dimension1='Country',    # Geographic
    dimension2='Device',     # Device type
    dimension3='Browser'     # Browser type
)
```

**Avoid:**
```python
# Bad: Requesting same dimension type redundantly
client.fetch_project_insights(
    num_days=3,
    dimension1='Country',
    dimension2='Region',    # Both geographic - redundant
    dimension3='City'       # Overly granular
)
```

---

## Practical Workarounds

### Workaround 1: Page-Specific Analysis

**Problem:** Cannot directly filter by page URL in API.

**Solution:**
```python
# Step 1: Request all pages with URL dimension
result = client.fetch_project_insights(
    num_days=3,
    dimension1='URL'
)

# Step 2: Filter locally
def get_page_metrics(data, page_url_pattern):
    """Extract metrics for specific page(s)"""
    filtered = []
    for item in data:
        if 'dimension1_value' in item:
            if page_url_pattern in item['dimension1_value']:
                filtered.append(item)
    return filtered

# Step 3: Use it
checkout_metrics = get_page_metrics(result['data'], '/checkout')
```

**Store in Database:**
```python
# Store all pages in database (as implemented in this project)
db_manager.insert_metrics(result)

# Query specific pages later
checkout_data = db.execute("""
    SELECT * FROM clarity_metrics
    WHERE dimension1_value LIKE '%/checkout%'
""").fetchall()
```

---

### Workaround 2: Heatmap Analysis Without API

**Problem:** Heatmap data not available via API.

**Solution:**

**Option A: Manual Process**
1. Visit Clarity dashboard
2. Navigate to Heatmaps section
3. Filter by page, device, date range
4. Export heatmap images (PNG)
5. Document findings manually

**Option B: Implement Custom Tracking**
```javascript
// Track clicks with custom events
document.addEventListener('click', function(e) {
    const element = e.target;
    const selector = getCSSPath(element);

    // Send to Clarity as custom event
    window.clarity('event', `click:${selector}`);

    // Also send to your own analytics
    yourAnalytics.trackClick({
        x: e.clientX,
        y: e.clientY,
        element: selector,
        page: window.location.pathname
    });
});
```

**Option C: Use API Metrics as Proxy**
- Dead click counts indicate problem areas
- Rage click counts show frustration points
- Use these metrics to guide manual heatmap review

---

### Workaround 3: Session Recording Analysis

**Problem:** Cannot access recordings via API.

**Solution:**

**Automated Identification + Manual Review:**
```python
# Step 1: Identify high-frustration sessions via API
result = client.fetch_project_insights(
    num_days=3,
    dimension1='Device'
)

# Step 2: Calculate frustration score
for metric in result['data']:
    if metric['metricName'] == 'RageClickCount':
        rage_percentage = metric['information'][0]['sessionsWithMetricPercentage']
        if rage_percentage > 5:  # High frustration threshold
            device = metric['dimension1_value']
            print(f"High frustration on {device}: {rage_percentage}%")
            print(f"→ Go to Clarity dashboard and filter recordings by {device}")
```

**Workflow:**
1. API identifies problem areas (device, page, date)
2. Dashboard filters recordings by those criteria
3. Manual review of filtered recordings
4. Document findings in spreadsheet/database
5. Track action items

---

### Workaround 4: Historical Trend Analysis

**Problem:** Only 3 days of data per API request.

**Solution:**

**Daily Data Collection (Implemented in This Project):**
```python
# Schedule daily data fetch (cron job)
# 0 2 * * * /usr/bin/python3 /path/to/fetch_clarity_data.py

# Fetch yesterday's data every day
result = client.fetch_project_insights(num_days=1)

# Store in local database
db_manager.insert_metrics(result)

# Build historical trends from local data
df = pd.read_sql("""
    SELECT
        DATE(fetch_timestamp) as date,
        metric_name,
        SUM(total_session_count) as sessions
    FROM clarity_metrics
    WHERE metric_name = 'Traffic'
    GROUP BY DATE(fetch_timestamp), metric_name
    ORDER BY date
""", conn)

# Plot 30-day trend
df.plot(x='date', y='sessions', title='30-Day Traffic Trend')
```

**Benefits:**
- Build unlimited historical data
- Custom retention periods
- Fast local queries
- No API rate limit concerns

---

## Code Examples

### Example 1: Basic Metrics Fetch

```python
from clarity_client import ClarityClient

# Initialize client
client = ClarityClient(
    project_id="your_project_id",
    cookie="your_auth_cookie"
)

# Fetch overall metrics (no dimensions)
result = client.fetch_project_insights(num_days=3)

# Extract traffic metrics
for metric in result['data']:
    if metric['metricName'] == 'Traffic':
        info = metric['information'][0]
        print(f"Sessions: {info['totalSessionCount']}")
        print(f"Users: {info['distinctUserCount']}")
        print(f"Pages/Session: {info['pagesPerSessionPercentage']}")
```

---

### Example 2: Multi-Dimensional Analysis

```python
# Get country + device breakdown
result = client.fetch_project_insights(
    num_days=3,
    dimension1='Country',
    dimension2='Device'
)

# Analyze
country_device_sessions = {}
for metric in result['data']:
    if metric['metricName'] == 'Traffic':
        country = metric.get('dimension1_value', 'Unknown')
        device = metric.get('dimension2_value', 'Unknown')
        sessions = metric['information'][0]['totalSessionCount']

        key = f"{country} - {device}"
        country_device_sessions[key] = sessions

# Print top combinations
sorted_combos = sorted(
    country_device_sessions.items(),
    key=lambda x: int(x[1]),
    reverse=True
)
print("Top Country-Device Combinations:")
for combo, sessions in sorted_combos[:10]:
    print(f"{combo}: {sessions} sessions")
```

---

### Example 3: Frustration Analysis

```python
# Get frustration metrics by device
result = client.fetch_project_insights(
    num_days=3,
    dimension1='Device'
)

frustration_metrics = ['DeadClickCount', 'RageClickCount', 'QuickbackClick']

# Calculate frustration score per device
device_scores = {}
for metric in result['data']:
    if metric['metricName'] in frustration_metrics:
        device = metric.get('dimension1_value', 'Overall')
        if device not in device_scores:
            device_scores[device] = {
                'sessions': 0,
                'dead_clicks': 0,
                'rage_clicks': 0,
                'quick_backs': 0
            }

        info = metric['information'][0]
        if metric['metricName'] == 'DeadClickCount':
            device_scores[device]['dead_clicks'] = info.get('sessionsWithMetricPercentage', 0)
        elif metric['metricName'] == 'RageClickCount':
            device_scores[device]['rage_clicks'] = info.get('sessionsWithMetricPercentage', 0)
        elif metric['metricName'] == 'QuickbackClick':
            device_scores[device]['quick_backs'] = info.get('sessionsWithMetricPercentage', 0)

# Calculate composite frustration score
for device, scores in device_scores.items():
    frustration_score = (
        scores['dead_clicks'] * 1.0 +
        scores['rage_clicks'] * 3.0 +
        scores['quick_backs'] * 2.0
    )
    print(f"{device}: Frustration Score = {frustration_score:.2f}")
```

---

### Example 4: Page-Specific Filtering (Local)

```python
# Fetch all pages
result = client.fetch_project_insights(
    num_days=3,
    dimension1='URL'
)

# Filter for specific pages locally
def filter_by_page(data, page_pattern):
    """Filter metrics for pages matching pattern"""
    filtered = []
    for item in data:
        if 'dimension1_value' in item:
            url = item['dimension1_value']
            if page_pattern in url:
                filtered.append(item)
    return filtered

# Get checkout page metrics
checkout_data = filter_by_page(result['data'], '/checkout')

# Get homepage metrics
homepage_data = filter_by_page(result['data'], '/')

# Analyze checkout vs homepage
def get_sessions(data):
    for item in data:
        if item['metricName'] == 'Traffic':
            return item['information'][0]['totalSessionCount']
    return 0

print(f"Checkout sessions: {get_sessions(checkout_data)}")
print(f"Homepage sessions: {get_sessions(homepage_data)}")
```

---

### Example 5: Error Tracking by Browser

```python
# Get error metrics by browser
result = client.fetch_project_insights(
    num_days=3,
    dimension1='Browser'
)

# Extract script errors
browser_errors = {}
for metric in result['data']:
    if metric['metricName'] == 'ScriptErrorCount':
        browser = metric.get('dimension1_value', 'Unknown')
        info = metric['information'][0]

        error_percentage = info.get('sessionsWithMetricPercentage', 0)
        error_count = info.get('subTotal', 0)

        browser_errors[browser] = {
            'error_rate': error_percentage,
            'error_count': error_count
        }

# Identify problematic browsers
print("Browsers with highest error rates:")
sorted_browsers = sorted(
    browser_errors.items(),
    key=lambda x: x[1]['error_rate'],
    reverse=True
)
for browser, errors in sorted_browsers[:5]:
    print(f"{browser}: {errors['error_rate']}% error rate ({errors['error_count']} errors)")
```

---

## Quick Reference Table

| Feature | Available via API | Available via Dashboard | Notes |
|---------|-------------------|------------------------|-------|
| **Aggregated Metrics** | ✅ YES | ✅ YES | JSON format via API |
| **Traffic Data** | ✅ YES | ✅ YES | Sessions, users, pages/session |
| **Engagement Metrics** | ✅ YES | ✅ YES | Time on site, scroll depth |
| **Frustration Signals** | ✅ YES | ✅ YES | Dead clicks, rage clicks, etc. |
| **Multi-Dimensional Data** | ✅ YES (up to 3) | ✅ YES | Country, device, browser, URL, etc. |
| **Historical Data** | ⚠️ LIMITED (3 days) | ✅ YES (12 months) | Store locally for history |
| **Bot Filtering** | ✅ YES | ✅ YES | Automatic separation |
| **Custom Events** | ⚠️ PARTIAL | ✅ YES | Set via JS, view in dashboard |
| **Page URL Filtering** | ⚠️ PARTIAL | ✅ YES | Request as dimension, filter locally |
| **Heatmap Data** | ❌ NO | ✅ YES | Visual only, PNG export |
| **Heatmap CSV** | ❌ NO | ❌ NO | Not available anywhere |
| **Click Coordinates** | ❌ NO | ⚠️ PARTIAL | Element-based, not pixel-based |
| **Session Recordings** | ❌ NO | ✅ YES | UI viewing only |
| **Recording Export** | ❌ NO | ❌ NO | No video file export |
| **Recording Metadata** | ⚠️ PARTIAL | ✅ YES | Some info via API metrics |
| **Individual Sessions** | ❌ NO | ✅ YES | Aggregated only via API |
| **Real-Time Data** | ⚠️ NEAR | ✅ YES | Minutes delay for API |
| **Raw Interaction Data** | ❌ NO | ⚠️ PARTIAL | Aggregated views only |

**Legend:**
- ✅ **YES**: Fully supported
- ⚠️ **PARTIAL**: Limited or requires workaround
- ❌ **NO**: Not available

---

## Recommendations

### For Data Collection & Analysis

1. **Set Up Daily Automated Fetching**
   ```bash
   # Add to crontab: daily at 2 AM
   0 2 * * * /usr/bin/python3 /path/to/fetch_clarity_data.py
   ```
   - Collect 1-3 days of data daily
   - Store in local database (SQLite/PostgreSQL)
   - Build historical trends over time

2. **Use Multiple Dimension Requests**
   - Different dimension combinations reveal different insights
   - Country + Device: Geographic device preferences
   - Device + Browser: Compatibility testing priorities
   - URL + Device: Page-specific device issues

3. **Monitor Rate Limits**
   - Track your 10 requests/day quota
   - Log all API calls to `api_requests` table
   - Plan requests strategically

---

### For Heatmap Analysis

Since heatmaps aren't available via API:

1. **Schedule Regular Dashboard Reviews**
   - Weekly heatmap review sessions
   - Focus on high-traffic pages
   - Document findings in spreadsheet

2. **Use API Frustration Metrics as Guide**
   - High dead clicks → Check click heatmap
   - Low scroll depth → Check scroll heatmap
   - Let data guide manual review

3. **Consider Custom Click Tracking**
   - Implement your own click tracking if you need programmatic access
   - Store click data in your database
   - Build custom heatmap visualizations

---

### For Session Recording Review

Since recordings aren't accessible via API:

1. **API-Guided Manual Review Workflow**
   ```
   API → Identify issues → Filter in dashboard → Review recordings → Document
   ```

2. **Prioritize Reviews**
   - High frustration sessions (rage clicks, errors)
   - Conversion drop-offs
   - Specific user segments (country, device)
   - Random sampling for general UX

3. **Create Review Schedule**
   - Daily: Critical errors/issues
   - Weekly: Random sampling (10-20 sessions)
   - Monthly: Comprehensive UX audit

---

### For Page-Specific Analysis

Since direct filtering isn't available:

1. **Request URL Dimension Daily**
   ```python
   result = client.fetch_project_insights(
       num_days=1,
       dimension1='URL'
   )
   ```

2. **Store All Pages in Database**
   - Full page coverage
   - Query locally for specific pages
   - Fast, flexible analysis

3. **Build Page-Level Reports**
   ```sql
   -- Top pages by traffic
   SELECT dimension1_value, SUM(total_session_count)
   FROM clarity_metrics
   WHERE dimension1_name = 'URL'
   GROUP BY dimension1_value
   ORDER BY SUM(total_session_count) DESC;

   -- Pages with highest frustration
   SELECT dimension1_value, COUNT(*) as frustration_incidents
   FROM clarity_metrics
   WHERE dimension1_name = 'URL'
     AND metric_name IN ('DeadClickCount', 'RageClickCount')
   GROUP BY dimension1_value
   ORDER BY frustration_incidents DESC;
   ```

---

### For Long-Term Success

1. **Accept API Limitations**
   - API is for programmatic metrics access
   - Dashboard is for visual exploration
   - Use each tool for its strengths

2. **Build Complementary Systems**
   - API for automated data collection
   - Local database for historical analysis
   - Dashboard for deep-dive investigations
   - Custom tracking for specific needs

3. **Document Your Workflow**
   - How you use API + Dashboard together
   - Which analyses are automated vs. manual
   - Division of responsibilities in team

4. **Stay Within Rate Limits**
   - 10 requests/day is enough for most use cases
   - Plan your requests strategically
   - Don't waste requests on redundant calls

5. **Combine Multiple Data Sources**
   - Clarity API: User behavior analytics
   - Google Analytics: Traffic sources, conversions
   - Custom tracking: Business-specific events
   - User surveys: Qualitative feedback

---

## Summary

### What You CAN Do

✅ **Programmatically access:**
- Aggregated metrics (traffic, engagement, frustration)
- Multi-dimensional breakdowns (country, device, browser, URL)
- Bot-filtered data
- 1-3 day rolling windows
- Custom event data (with JS API)

✅ **Build:**
- Automated data collection pipelines
- Historical trend databases
- Custom analytics dashboards
- Alerting systems (based on metric thresholds)

---

### What You CANNOT Do

❌ **Via API:**
- Access session recordings
- Download heatmap data
- Get individual session details
- Direct page URL filtering
- Access more than 3 days per request
- Get raw click coordinates
- Export video files

❌ **Workarounds Required For:**
- Page-specific analysis (request URL dimension, filter locally)
- Historical trends (store data locally over time)
- Heatmap insights (manual dashboard review)
- Recording review (dashboard viewing only)

---

### Key Takeaways

1. **API = Automated Metrics**: Use for programmatic data collection
2. **Dashboard = Visual Exploration**: Use for heatmaps and recordings
3. **Local Storage = Historical Analysis**: Build your own data warehouse
4. **Combine All Three**: Comprehensive analytics strategy

5. **Rate Limits Matter**: 10 requests/day, plan strategically
6. **Dimensions Are Powerful**: Up to 3 per request, use wisely
7. **Workarounds Exist**: Most limitations can be mitigated with proper architecture

---

## Document Maintenance

**Update Frequency:** When API changes are announced or discovered

**Owner:** Engineering/Analytics Team

**Next Review Date:** February 25, 2025

**Changelog:**
- v1.0 (Nov 25, 2024): Initial documentation based on implementation experience

---

## Additional Resources

### Official Documentation
- **Microsoft Clarity:** https://clarity.microsoft.com/
- **Clarity API Docs:** https://docs.microsoft.com/en-us/clarity/
- **JavaScript API:** https://docs.microsoft.com/en-us/clarity/setup-and-installation/javascript-api

### Internal Project Files
- **Implementation Plan:** `/clarity_api_implementation_plan.md`
- **Research Notes:** `/clarity_api_research.md`
- **Client Code:** `/clarity_client.py`
- **Data Fetching:** `/fetch_clarity_data.py`
- **Database Schema:** `/database/schema.sql`

### Support
- **Clarity Support:** Through Microsoft Azure portal
- **GitHub Issues:** https://github.com/microsoft/clarity (community support)

---

**END OF DOCUMENT**
