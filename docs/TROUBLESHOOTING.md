# Troubleshooting Guide

Common issues and solutions for Clarity UX Insights.

---

## Quick System Check

**Start here - this solves most issues:**

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

---

## API Connection Issues

### Symptoms
- "API token is invalid"
- "Failed to connect to Clarity API"
- "Authentication failed"

### Solutions

```bash
# Test your connection
python config.py

# Check your token in .env file
cat .env | grep CLARITY_API_TOKEN

# Or check status
python clarity_cli.py status
```

### Common Fixes
1. **Token expired or invalid**: Regenerate token at [Clarity Settings](https://clarity.microsoft.com/) → API → Data Export API
2. **Wrong project ID**: Verify your project ID matches the token
3. **Token format**: Ensure token starts with `eyJ` and has no extra spaces
4. **Missing .env file**: Copy `.env.example` to `.env` and add your credentials

---

## API Rate Limiting

### Symptoms
- "⚠️ Rate limit hit"
- "HTTP 429" errors
- Fetch script waiting 60 seconds repeatedly
- All API requests failing after several attempts

### What's Happening
Microsoft Clarity API has rate limits to prevent abuse. When you hit the limit:
- The API returns HTTP 429 (Too Many Requests)
- The script automatically waits 60 seconds before retrying
- After 3 retries, the request fails
- Rate limits are tied to your Clarity account, not IP address

### Solutions

**Option 1: Wait it Out (Recommended)**
```bash
# The script handles rate limits automatically
# Just let it run - it will wait and retry
python fetch_clarity_data.py

# You'll see:
# ⚠️  Rate limit hit. Waiting 60 seconds...
# This is normal - the script is handling it for you
```

**Option 2: Retry Later**
```bash
# If all fetches fail, wait a few hours and try again
# Rate limits typically reset:
# - Hourly (most common)
# - Daily (for heavy usage)
# - Per request count

# Check when you can try again:
python clarity_cli.py status
# Look at "Latest fetch" to see when last successful fetch occurred
```

**Option 3: Generate New API Token**
```bash
# Sometimes a fresh token helps
# 1. Go to Clarity Settings → API → Data Export API
# 2. Generate new token
# 3. Update .env file with new token
# 4. Try fetching again
```

### Prevention Tips

1. **Don't fetch too frequently**: Wait at least 1 hour between fetch attempts
2. **Schedule fetches**: Run once per day at the same time
3. **Avoid multiple simultaneous fetches**: Only run one fetch script at a time
4. **Monitor fetch logs**: Check `fetch_log` table in database to see request history

```bash
# Check your fetch history
sqlite3 data/clarity_data.db "SELECT * FROM fetch_log ORDER BY fetch_timestamp DESC LIMIT 10;"
```

### Understanding Rate Limits

**Microsoft Clarity API Limits:**
- **Max requests per day**: ~10 (as per config)
- **Max days per request**: 3
- **Cooldown period**: ~60 seconds between requests
- **Daily reset**: Varies by account

**Why So Restrictive?**
Clarity is a free service, and the API is designed for periodic data collection, not high-frequency polling.

### Best Practices

1. **Daily Schedule**: Set up a cron job or scheduled task to run once per day:
   ```bash
   # Example cron (runs at 2 AM daily)
   0 2 * * * cd /path/to/clarity_api && python fetch_clarity_data.py
   ```

2. **Monitor, Don't Poll**: Check data once daily, not multiple times per hour

3. **Use Existing Data**: Query your database instead of re-fetching:
   ```bash
   python clarity_cli.py query 7
   python clarity_cli.py aggregate 30
   ```

4. **Archive Old Data**: Keep database lean to improve performance:
   ```bash
   python scripts/archive_manager.py cleanup
   ```

### When to Contact Support

If you experience persistent rate limiting:
1. Verify you're not running multiple fetch scripts
2. Check if someone else has access to your API token
3. Review the [Microsoft Clarity API documentation](https://learn.microsoft.com/en-us/clarity/)
4. Contact Microsoft Clarity support if limits seem too restrictive for your use case

---

## Database Issues

### Symptoms
- "Database file not found"
- "No table found"
- "Database is locked"

### Solutions

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

### Common Fixes
1. **Database doesn't exist**: Run `python fetch_clarity_data.py` to create it
2. **Corrupted database**: Back up data/, delete .db file, re-fetch data
3. **Database locked**: Close any open connections or tools accessing the database

---

## "No Data Found" Errors

### Symptoms
- "No data found for date range"
- "Empty result set"

### Solutions

```bash
# Check what data you have
python clarity_cli.py list

# Check date range
python clarity_cli.py status

# The date range might be outside your available data
# Try: python clarity_cli.py query 3  (for last 3 days)
```

### Common Fixes
1. **No data collected yet**: Run `python fetch_clarity_data.py` first
2. **Date range too old**: Check available data range with `/system-status`
3. **Date range in future**: Verify your date expression is correct
4. **Wrong metric scope**: Try `--scope general` or `--scope page`

---

## Date Format Not Recognized

### Symptoms
- "Date format not recognized"
- "Invalid date expression"
- "Could not parse date"

### Solutions

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

### Common Fixes
1. **Use quotes for multi-word dates**: `python clarity_cli.py query "last week"`
2. **Check spelling**: "November" not "Novemeber"
3. **Use supported formats**: See [DATE-FORMATS.md](DATE-FORMATS.md)

---

## Python/Dependency Issues

### Symptoms
- "Module not found"
- "No module named 'requests'"
- "Import Error"

### Solutions

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or upgrade specific packages
pip install --upgrade requests python-dotenv

# Check Python version (requires 3.7+)
python --version
```

### Common Fixes
1. **Wrong Python version**: Use Python 3.7 or later
2. **Virtual environment not activated**: Activate your venv
3. **Missing requirements**: Run `pip install -r requirements.txt`

---

## Permission Errors

### Symptoms
- "Permission denied"
- "Cannot write to directory"
- "Cannot create database"

### Solutions

```bash
# Check directory permissions
ls -la

# Fix permissions (Unix/Mac)
chmod 755 .
chmod -R 755 data/

# Check if you own the directory
whoami
ls -la | grep data
```

### Common Fixes
1. **Wrong directory ownership**: Use `sudo chown -R $USER:$USER .`
2. **Read-only filesystem**: Move project to writable location
3. **Docker/container issues**: Check volume mount permissions

---

## Using Claude Code for Help

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

## Still Stuck?

1. **Check logs**: Look for error details in terminal output
2. **Review docs**: Check [documentation](../README.md#-documentation)
3. **Create an issue**: [GitHub Issues](https://github.com/parhumm/clarity-ux-insights/issues)
4. **Contact author**: [LinkedIn - Parhum Khoshbakht](https://www.linkedin.com/in/parhumm/)

---

**Back to:** [Main README](../README.md) | [Quick Start](QUICK-START.md) | [Command Reference](COMMAND-REFERENCE.md)
