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
   Clone this repository: https://github.com/parhumm/clarity-ux-insights
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
git clone https://github.com/parhumm/clarity-ux-insights.git
cd clarity-ux-insights
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
- [API Features & Limitations](docs/features_and_limitations.md) - What you can and can't do with the API
- [Insights Guide](docs/clarity_insights_analysis.md) - Comprehensive analysis guide for UX/PM
- [Quick Reference](docs/clarity_quick_reference.md) - At-a-glance metrics and actions

**Detailed Documentation:**
- [Implementation Plan](implementation_plan.md) - Full technical implementation details
- [API Research](api_research.md) - Complete Clarity API research and capabilities
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
