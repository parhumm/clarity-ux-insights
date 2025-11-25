# Microsoft Clarity Data Analytics

Automatically collect and analyze user behavior data from Microsoft Clarity to make better UX and product decisions.

## 🎯 What This Does

This tool fetches analytics data from Microsoft Clarity's API and stores it locally, giving you:

**For UX Researchers:**
- Identify frustration points (dead clicks, rage clicks, quick backs)
- Track scroll behavior and engagement patterns
- Compare user experience across devices and browsers
- Spot usability issues with real data

**For Product Managers:**
- Monitor product health metrics daily
- Track feature adoption and user engagement
- Prioritize fixes based on user impact
- Make data-driven roadmap decisions

**Key Benefit:** Microsoft Clarity's API only keeps 3 days of data. This tool collects it daily and stores it locally, so you can track trends over weeks and months.

---

## ⚡ Quick Start with Claude Code

The easiest way to get started is using [Claude Code](https://claude.ai/code).

### Step 1: Get Your Clarity API Token

1. Go to https://clarity.microsoft.com/
2. Click on your project
3. Go to **Settings** → **API** → **Data Export API**
4. Click **Generate Token**
5. Copy the token (starts with `eyJ...`)
6. Also note your **Project ID** (in Settings)

### Step 2: Clone This Repository with Claude Code

1. Open Claude Code (desktop app or web)
2. Tell Claude:
   ```
   Clone this repository: https://github.com/YOUR_USERNAME/clarity_api
   ```
3. Claude will clone it to your system

### Step 3: Set Up Environment with Claude Code

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

### Step 4: Install Dependencies with Claude Code

Tell Claude:
```
Install the Python dependencies for this project
```

Claude will run `pip install -r requirements.txt`

### Step 5: Test the Setup with Claude Code

Tell Claude:
```
Test if the Clarity API configuration is working
```

Claude will run `python config.py` and show you if everything is connected.

### Step 6: Collect Your First Data with Claude Code

Tell Claude:
```
Fetch my Clarity data for the last 3 days
```

Claude will run `python fetch_clarity_data.py` and:
- Fetch 6 types of analytics data
- Store it in a local SQLite database
- Save raw JSON files
- Show you a summary

### Step 7: Generate a Report with Claude Code

Tell Claude:
```
Generate a summary report of my Clarity data
```

Claude will run `python generate_summary.py` and show you:
- Total sessions and users
- Device breakdown
- Top countries
- Frustration metrics (dead clicks, rage clicks)
- CSV exports for further analysis

---

## 🔧 Manual Setup (Without Claude Code)

If you prefer to set up manually:

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/clarity_api.git
cd clarity_api
```

### 2. Configure Environment
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

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Test Configuration
```bash
python config.py
```

### 5. Fetch Data
```bash
python fetch_clarity_data.py
```

### 6. Generate Report
```bash
python generate_summary.py
```

---

## 📊 What Data Gets Collected

**User Behavior:**
- Sessions, unique users, bot traffic
- Pages per session, engagement time
- Scroll depth, navigation patterns

**Frustration Signals:**
- Dead clicks (clicking non-interactive elements)
- Rage clicks (rapid repeated clicking)
- Quick backs (immediate exits)
- JavaScript errors

**Segmentation:**
- Device type (Mobile, Desktop, Tablet)
- Browser (Chrome, Safari, Firefox, etc.)
- Country (geographic distribution)
- Cross-segmentation (e.g., Germany + Mobile users)

All data is stored in:
- SQLite database (`data/clarity_data.db`)
- Raw JSON files (`data/raw/`)
- CSV exports (`data/exports/`)

---

## 💡 Common Use Cases

### Daily Monitoring
```bash
# Set up a daily cron job to collect data
0 2 * * * cd /path/to/clarity_api && python fetch_clarity_data.py
```

### Analyze Specific Issues
```bash
# Use Claude Code to analyze
Tell Claude: "Show me the devices with the highest frustration rates"
Tell Claude: "Which countries have the most dead clicks?"
Tell Claude: "Compare mobile vs desktop engagement"
```

### Export for Presentations
```bash
# Generate CSV files
python generate_summary.py

# Files saved to data/exports/
# - summary_last_3_days.csv
# - device_summary.csv
# - country_summary.csv
# - browser_summary.csv
```

### Query the Database
```python
from database.db_manager import DatabaseManager

db = DatabaseManager()

# Get all mobile metrics
mobile_metrics = db.get_metrics(dimension1="Device", dimension1_value="Mobile")

# Get statistics
stats = db.get_statistics()
print(f"Total records: {stats['total_metrics']}")
```

---

## 📚 Documentation

**Quick References:**
- [API Features & Limitations](docs/clarity_api_features_and_limitations.md) - What you can and can't do with the API
- [Insights Guide](docs/clarity_insights_analysis.md) - Comprehensive analysis guide for UX/PM
- [Quick Reference](docs/clarity_quick_reference.md) - At-a-glance metrics and actions

**Detailed Documentation:**
- [Implementation Plan](clarity_api_implementation_plan.md) - Full technical implementation details
- [API Research](clarity_api_research.md) - Complete Clarity API research and capabilities
- [SECURITY.md](SECURITY.md) - Security guidelines and best practices

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

## 🚀 Benefits Summary

**Why use this tool?**

1. **Historical Tracking:** Clarity API only gives you 3 days of data. This tool stores it forever.

2. **Automation:** Set it and forget it - daily collection with cron jobs.

3. **Flexible Analysis:** Query your own database, export to CSV, build custom reports.

4. **No Rate Limits:** Once collected, analyze as much as you want without API limits.

5. **Trend Analysis:** Compare week-over-week, month-over-month, track improvements.

6. **Better Decisions:** Real data about user frustration, engagement, and behavior patterns.

7. **Claude Code Integration:** Use AI to help you analyze, query, and understand your data.

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

### API Connection Issues
```bash
# Test your connection
python clarity_client.py

# Check your token in .env file
cat .env | grep CLARITY_API_TOKEN
```

### Database Issues
```bash
# Validate your data
python validate_data.py

# Re-initialize database if needed
rm data/clarity_data.db
python fetch_clarity_data.py
```

### Using Claude Code for Help

Just tell Claude:
```
I'm getting an error with the Clarity API project
```

Then paste the error message. Claude can help debug and fix most issues.

---

**Questions?** Check the [docs](docs/) folder or create an issue on GitHub.

**Ready to start?** Jump to [Quick Start with Claude Code](#-quick-start-with-claude-code) 🚀
