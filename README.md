# Clarity UX Insights

Transform user behavior into actionable insights. Automatically collect, analyze, and preserve Microsoft Clarity analytics data to discover what users really experience on your site.

---

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

---

## ⚡ Quick Start

### Step 1: Get Your Clarity API Token

1. Go to [Microsoft Clarity](https://clarity.microsoft.com/)
2. Open your project → **Settings** → **API** → **Data Export API**
3. Click **Generate Token** and copy it (starts with `eyJ...`)
4. Note your **Project ID** (also in Settings)

### Step 2: Setup with Claude

Copy and paste this complete setup prompt into [Claude Code](https://claude.ai/code):

```
Please help me set up the Clarity UX Insights project:

1. Clone this repository: https://github.com/parhumm/clarity-ux-insights
2. Navigate into the project directory
3. Copy .env.example to .env
4. Help me configure the .env file with my credentials:
   - CLARITY_API_TOKEN: [I'll provide this]
   - CLARITY_PROJECT_ID: [I'll provide this]
5. Install Python dependencies from requirements.txt
6. Test the configuration by running config.py
7. Show me a summary of what was set up

After setup, let me know if everything is working correctly.
```

Claude will handle all the technical setup - you just provide your API token and project ID when asked.

### Step 3: Start Analyzing

Once setup is complete, tell Claude what you want to know:

**Example prompts to try:**
```
Show me my Clarity data for the last 7 days

What are the frustration patterns over the last month?

Compare this week's metrics to last week

Generate a UX health report for November

Show me device performance trends

Which pages have the highest rage clicks?
```

Or use slash commands directly:
```
/system-status
/query-data 7
/aggregate-metrics last-week
```

**That's it!** Claude handles the complexity - you just ask questions in plain English.

---

## 📚 Documentation

All detailed documentation is organized by topic:

**Quick Start Guides:**
- [5-Minute Quick Start](docs/QUICK-START.md) - Fast setup with all methods
- [Usage Examples](docs/USAGE-EXAMPLES.md) - Practical patterns and workflows
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common issues and solutions

**Command References:**
- [Complete Command Reference](docs/COMMAND-REFERENCE.md) - All commands with examples
- [Date Format Reference](docs/DATE-FORMATS.md) - 30+ supported date expressions

**Analysis Guides:**
- [Insights Analysis Guide](docs/clarity_insights_analysis.md) - Comprehensive guide for UX/PM teams
- [Quick Reference Card](docs/clarity_quick_reference.md) - At-a-glance metrics cheat sheet
- [API Features & Limitations](docs/features_and_limitations.md) - What you can and can't do

**Technical Documentation:**
- [System Overview](docs/README-SUMMARY.md) - Architecture and technical details
- [Implementation Plan](implementation_plan.md) - Full technical implementation
- [API Research](api_research.md) - Complete Clarity API documentation

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

## 👨‍💻 Author

Created by **[Parhum Khoshbakht](https://www.linkedin.com/in/parhumm/)**

Connect on LinkedIn for questions, feedback, or collaboration opportunities.

---

## 🚀 Why This Matters

**Turn ephemeral data into lasting insights:**

1. **Preserve Your History** - Clarity's API discards data after 3 days. This tool captures and preserves it indefinitely, building a historical record you can analyze across product cycles.

2. **Automate Intelligence Gathering** - Set up once, collect forever. Daily automation captures insights while you sleep, building a comprehensive behavioral dataset.

3. **Analyze Without Limits** - Query, slice, export, and explore your data endlessly. No API rate limits, no restrictions. It's your data, stored locally.

4. **Spot Trends That Matter** - Compare week-over-week patterns, track month-over-month improvements, measure the impact of releases and design changes.

5. **Make Evidence-Based Decisions** - Replace opinions with observations. Replace assumptions with real user behavior data. Know what's working and what's frustrating users.

6. **Build Custom Insights** - Export to CSV for presentations, query the database for specific patterns, or build custom dashboards that answer your unique questions.

7. **Leverage AI Analysis** - Claude Code integration lets you ask natural language questions about your data and get instant insights without writing code.

---

## 🤝 Contributing

Found a bug? Have a feature request?

1. Check [existing issues](https://github.com/parhumm/clarity-ux-insights/issues)
2. Create a new issue with details
3. Or submit a pull request

---

## 📄 License

This project is open source. Feel free to use and modify for your needs.

---

**Questions?** Check the [docs](docs/) folder or create an issue on GitHub.

**Ready to start?** Jump to [Quick Start](#-quick-start) 🚀
