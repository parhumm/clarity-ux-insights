# Clarity UX Insights - User Guide

**A practical, non-technical guide to understanding your website's user experience**

---

## What Questions Can You Answer?

This tool helps you discover what's really happening on your website:

### Traffic & Growth
- **Is my traffic growing?** See if more people are visiting your site
- **When are users most active?** Identify peak hours and days
- **Which devices do users prefer?** Mobile vs Desktop breakdown
- **Where are users coming from?** Geographic distribution

### User Experience
- **Are users getting frustrated?** Spot rage clicks and dead clicks
- **Do users engage with my content?** See scroll depth and time on page
- **Which pages cause problems?** Identify high-frustration pages
- **How do different devices compare?** Mobile UX vs Desktop UX

### Business Impact
- **Is this week better than last week?** Week-over-week comparison
- **Are we improving over time?** Long-term trend analysis
- **Did our latest update help or hurt?** Before/after comparison
- **What should we fix first?** Prioritize by frustration signals

---

## Getting Started - Choose Your Method

### Method 1: Using Claude (Easiest 👍)

If you have [Claude Code](https://claude.ai/code), just talk to it naturally:

**Check Your Data:**
```
/system-status
```
Shows: How much data you have, date range, system health

**Query Your Metrics:**
```
/query-data 7
```
Shows: Last 7 days of metrics

**Check Trends:**
```
Tell Claude: "Show me if traffic is increasing"
Tell Claude: "Compare this week to last week"
Tell Claude: "Which device has the most frustration?"
```

**That's it!** Claude understands natural language and shows you the insights.

---

### Method 2: Using Commands (More Control 💪)

If you're comfortable with commands, use the unified CLI:

**See What You Have:**
```bash
python clarity_cli.py status
```
Shows: Your data range, metrics count, configuration

**Query Any Time Period:**
```bash
python clarity_cli.py query 7        # Last 7 days
python clarity_cli.py query "last week"
python clarity_cli.py query November
```

**Get Summaries:**
```bash
python clarity_cli.py aggregate 30   # 30-day summary with averages
```

---

## Common Tasks (Step-by-Step)

### Task 1: See Your Latest Data

**What it does:** Shows you what data you have available

**Using Claude:**
```
/system-status
```

**Using Commands:**
```bash
python clarity_cli.py status
```

**What You'll See:**
- Total sessions (visits)
- Total users (unique visitors)
- Date range (earliest to latest data)
- Number of metrics collected

**What It Means:**
- **Sessions** = Total visits to your site
- **Users** = Unique people who visited
- **Date Range** = Time period of collected data

---

### Task 2: Compare This Week to Last Week

**What it does:** Shows if things are getting better or worse

**Using Claude:**
```
Tell Claude: "Compare this week to last week"
```

**Using Commands:**
```bash
python scripts/comparator.py "last week"
```

**What You'll See:**
- 📈 **Improvements** (green) - Things that got better
  - Example: "Sessions: +15% (+1,234)"
  - Example: "Dead Clicks: -20% (-45)"

- 📉 **Regressions** (red) - Things that got worse
  - Example: "Rage Clicks: +10% (+23)"

- 📊 **Overall Trend** - ↑ (positive), ↓ (negative), or → (neutral)

**What It Means:**
- **+% in sessions/users** = More traffic (good!)
- **-% in frustration signals** = Better UX (good!)
- **+% in frustration signals** = More problems (needs attention!)

---

### Task 3: Check for Long-Term Trends

**What it does:** Analyzes trends over weeks or months

**Using Claude:**
```
Tell Claude: "Analyze trends for the last 30 days"
```

**Using Commands:**
```bash
python scripts/trend_analyzer.py 30
```

**What You'll See:**
- **Growth Rate** - Is traffic increasing or decreasing?
- **Trend Direction** - INCREASING, DECREASING, or STABLE
- **Stability** - HIGH (predictable), MEDIUM, or LOW (volatile)
- **Patterns** - Weekly cycles detected? Peak days?

**What It Means:**
- **INCREASING trend** = Growing traffic or engagement
- **HIGH stability** = Predictable, consistent performance
- **Weekly pattern detected** = Regular weekly cycles (e.g., weekends vs weekdays)

**Examples:**
```
Growth: +25%        → Traffic is growing
Trend: INCREASING   → Upward trajectory
Stability: HIGH     → Consistent, reliable data
```

---

### Task 4: Generate a Professional Report

**What it does:** Creates a comprehensive report with insights

**Using Commands:**
```bash
# Choose a template and time period:

# Overall UX health
python scripts/report_generator.py ux-health 7

# Frustration analysis (where users struggle)
python scripts/report_generator.py frustration-analysis 30

# Device comparison (Mobile vs Desktop)
python scripts/report_generator.py device-performance 7

# Page-specific analysis
python scripts/report_generator.py page-analysis 30 --page /checkout
```

**What You Get:**
- Markdown report in `reports/` directory
- Multi-audience insights:
  - **Technical Team** - What to fix
  - **UX Team** - User experience insights
  - **Business Team** - Impact on metrics
  - **Marketing Team** - Audience behavior
- Actionable recommendations
- Key findings highlighted

**Best Use:** Share with your team, export to PDF, or keep for records

---

### Task 5: Clean Up Old Data

**What it does:** Archives old data and frees up space

**Check What Would Be Archived:**
```bash
python scripts/archive_manager.py check
```

**See What Would Happen (Dry Run):**
```bash
python scripts/archive_manager.py cleanup --dry-run
```

**Actually Archive and Delete:**
```bash
python scripts/archive_manager.py cleanup
```

**What It Does:**
1. Exports old data to a backup file (JSON or CSV)
2. Saves it in `archive/` directory
3. Removes it from the active database
4. Keeps your database fast and manageable

**When to Use:**
- Your database is getting large
- You want to keep old data but not actively query it
- You need to comply with data retention policies

---

## Understanding Your Results

### Good Signs (What You Want to See) ✅

**Traffic Metrics:**
- ✅ Sessions increasing week-over-week
- ✅ Users growing month-over-month
- ✅ High engagement (scroll depth, time on page)
- ✅ INCREASING trend with HIGH stability

**UX Metrics:**
- ✅ Frustration signals decreasing
- ✅ Dead clicks going down
- ✅ Rage clicks reducing
- ✅ Quick backs dropping

**Example Good Report:**
```
Sessions: +15% (↑)
Dead Clicks: -20% (↓)
Trend: INCREASING
Stability: HIGH
Overall: Positive trend ↑
```
**Translation:** More visitors, fewer problems, growing consistently!

---

### Warning Signs (What Needs Attention) ⚠️

**Traffic Metrics:**
- ⚠️ Sessions decreasing
- ⚠️ Users dropping week-over-week
- ⚠️ DECREASING trend
- ⚠️ LOW stability (erratic numbers)

**UX Metrics:**
- ⚠️ Frustration signals increasing
- ⚠️ Dead clicks growing
- ⚠️ Rage clicks spiking
- ⚠️ Quick backs rising

**Example Warning Report:**
```
Sessions: -10% (↓)
Rage Clicks: +35% (↑)
Dead Clicks: +28% (↑)
Trend: DECREASING
Overall: Negative trend ↓
```
**Translation:** Losing visitors, users are frustrated, needs immediate attention!

---

### What the Numbers Mean

**Frustration Signals Explained:**

| Metric | What It Is | What It Means | Good Range |
|--------|-----------|---------------|------------|
| **Dead Clicks** | Clicks on non-interactive elements | Users expect something to work but it doesn't | < 0.05 per session |
| **Rage Clicks** | Rapid, repeated clicks | Users are frustrated and clicking frantically | < 0.02 per session |
| **Quick Backs** | Immediate page exits | Users land on a page and immediately leave | < 0.10 per session |
| **Error Clicks** | Clicks that trigger errors | Technical problems interrupting users | 0 (ideally) |

**Engagement Metrics:**

| Metric | What It Is | Good Range |
|--------|-----------|------------|
| **Scroll Depth** | How far down users scroll | > 70% |
| **Time on Page** | How long users stay | > 30 seconds |
| **Active Time** | Actual interaction time | > 20 seconds |

---

## When to Take Action

### High Priority (Fix Immediately) 🚨

**If you see:**
- Frustration signals **increasing by 30%+**
- Rage clicks **spike** suddenly
- Traffic **dropping 20%+**
- Overall trend is **DECREASING**

**Action:**
1. Generate a frustration analysis report
2. Identify the problematic pages/elements
3. Check for recent changes (deployments, updates)
4. Review device-specific issues
5. Prioritize fixes based on impact

---

### Medium Priority (Monitor & Plan) 📊

**If you see:**
- Frustration signals **stable but high** (> 0.05 per session)
- Traffic **flat** (not growing)
- **Weekly patterns** with dips on certain days
- **Device disparity** (Mobile much worse than Desktop)

**Action:**
1. Compare time periods to understand patterns
2. Analyze trends to see long-term direction
3. Generate device performance reports
4. Plan improvements based on data

---

### Low Priority (Keep Watching) 👀

**If you see:**
- Frustration signals **low and decreasing**
- Traffic **growing steadily**
- Trend is **INCREASING**
- **HIGH stability**

**Action:**
1. Monitor weekly with comparisons
2. Keep collecting data for long-term insights
3. Document what's working
4. Share successes with team

---

## Troubleshooting for Non-Technical Users

### "I don't see any data"

**Try this:**
```bash
# Check what data you have
python clarity_cli.py status
```

**If it says "No data":**
- Data hasn't been collected yet
- Ask your technical team to run: `python fetch_clarity_data.py`
- Or tell Claude: "Fetch my Clarity data"

---

### "The date doesn't work"

**These formats work:**
- Simple numbers: `7`, `30`, `90`
- Relative: `yesterday`, `last-week`, `last-month`
- Months: `November`, `2025-11`
- Quarters: `2025-Q4`, `Q4 2025`
- Custom: `"2025-11-01 to 2025-11-30"` (with quotes)

**These DON'T work:**
- `last 7 days` (use `7` or `"last-week"`)
- `Nov` without year (use `November` or `2025-11`)
- Dates without quotes: `2025-11-01 to 2025-11-30` (add quotes)

---

### "The numbers seem wrong"

**Check your data range:**
```bash
python clarity_cli.py status
```

Make sure:
- You have data for the period you're querying
- The date range is what you expect
- You're not querying future dates

---

### "I want to share this with my team"

**Generate a report:**
```bash
python scripts/report_generator.py ux-health 7
```

**Find the report:**
- Look in `reports/general/` directory
- File name includes the date
- Format: Markdown (opens in any text editor)

**Share it:**
- Copy and paste into email/Slack
- Export to PDF (many markdown viewers support this)
- Share the markdown file directly

---

## Quick Reference Cheat Sheet

### Most Useful Commands

```bash
# Check status (ALWAYS START HERE)
python clarity_cli.py status

# Query recent data
python clarity_cli.py query 7

# Compare weeks
python scripts/comparator.py "last week"

# Analyze trends
python scripts/trend_analyzer.py 30

# Generate report
python scripts/report_generator.py ux-health 7
```

### With Claude Code

```
/system-status              # Check system
/query-data 7               # Query data
Tell Claude: "Compare this week to last week"
Tell Claude: "Show me trends for the last month"
Tell Claude: "Generate a UX health report"
```

---

## Getting Help

### Use Claude Code
Tell Claude what you need:
```
"Help me understand my UX metrics"
"Show me how to compare time periods"
"I need to generate a report for my team"
"Something's not working, here's the error: [paste error]"
```

### Check System Status First
```bash
python clarity_cli.py status
```
This often reveals the issue!

### Review Documentation
- [Complete README](README.md) - Full technical details
- [Quick Start Guide](docs/QUICK-START.md) - Setup instructions
- [Date Formats Reference](docs/DATE-FORMATS.md) - All date formats

### Ask Your Team
If you have technical teammates, they can:
- Check database status
- Verify data collection
- Debug any errors
- Set up automated reports

---

**Remember:** This tool is here to help you make data-driven decisions about your website's UX. Start simple, explore gradually, and don't hesitate to ask Claude for help! 🚀
