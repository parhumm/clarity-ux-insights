# Fetch Clarity Data

Fetch the latest data from Microsoft Clarity API.

## Usage

```bash
python fetch_clarity_data.py
```

## What It Does

1. Connects to Microsoft Clarity API
2. Fetches last 3 days of data (API limitation)
3. Retrieves metrics with multiple dimensions:
   - Base metrics (no dimensions)
   - By device (Mobile, Desktop, Tablet)
   - By country
   - By browser
   - Device × Browser combinations
   - Country × Device combinations
4. Saves raw JSON responses to `data/raw/`
5. Imports data to SQLite database
6. Logs all API requests

## Prerequisites

**Required:**
- `.env` file with `CLARITY_API_TOKEN` and `CLARITY_PROJECT_ID`
- Valid Microsoft Clarity API token
- Internet connection

## Output

Shows:
- API request progress
- Dimensions being fetched
- Number of records imported
- Any errors or warnings

## Rate Limits

- Maximum 10 requests per day (Clarity API limit)
- Maximum 3 days per request (Clarity API limit)
- 2-second delay between requests

## After Fetching

Run aggregation to create weekly/monthly summaries:
```bash
python clarity_cli.py aggregate-all
```
