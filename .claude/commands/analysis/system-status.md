# System Status

Show the current status of your Clarity UX Insights system.

## Usage

```bash
python clarity_cli.py status
```

## What It Shows

**Project Information:**
- Project name
- Project type
- Project URL (if configured)

**Data Statistics:**
- Total daily metrics
- Total weekly metrics
- Total monthly metrics
- Number of tracked pages

**Date Range:**
- First data date
- Latest data date

**Configuration:**
- Default period
- Output formats
- Data retention settings

## Example Output

```
📊 Clarity UX Insights - System Status
============================================================

📁 Project:
   Name: My Website
   Type: e-commerce

📊 Data:
   Daily metrics: 3,386
   Weekly metrics: 4
   Monthly metrics: 6
   Tracked pages: 3

📅 Date Range:
   First data: 2025-11-24
   Latest data: 2025-11-25

⚙️  Configuration:
   Default period: 7 days
   Output formats: markdown, csv
   Data retention: 90 days
```
