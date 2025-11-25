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
