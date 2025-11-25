# Quick Start Guide

Get started with Clarity UX Insights in 5 minutes.

## Prerequisites

- Python 3.8+
- Microsoft Clarity account with API token
- Git (for cloning)

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/clarity-ux-insights.git
cd clarity-ux-insights

# Install dependencies
pip install -r requirements.txt

# Copy configuration template
cp config.template.yaml config.yaml
```

## Configuration

### 1. Set up API Token

Create `.env` file:
```bash
CLARITY_API_TOKEN=your_jwt_token_here
CLARITY_PROJECT_ID=your_project_id
```

Get your API token from [Microsoft Clarity](https://clarity.microsoft.com/).

### 2. Configure Project

Edit `config.yaml`:
```yaml
project:
  name: "My Website"
  type: "website"  # e-commerce, saas, media, etc.

tracking:
  pages: []  # Add pages to track (optional)

reports:
  default_period_days: 3
  output_formats: ["markdown", "csv"]
```

## Basic Usage

### Fetch Data

```bash
# Fetch last 3 days of data
python fetch_clarity_data.py
```

### Query Data

```python
from scripts.query_engine import QueryEngine

engine = QueryEngine()

# Query last 7 days
metrics = engine.query_metrics("7", metric_name="Traffic")

# Query specific month
metrics = engine.query_metrics("November", metric_name="Traffic")
```

### Aggregate Data

```bash
# Aggregate into weekly/monthly summaries
python scripts/aggregator.py
```

## Next Steps

- [Configuration Guide](CONFIGURATION.md) - Detailed configuration options
- [CLI Reference](CLI-REFERENCE.md) - Command-line tools
- [Date Formats](DATE-FORMATS.md) - All supported date expressions
- [Report Types](REPORTS.md) - Available report types

## Getting Help

- Check [documentation](README.md)
- Review [examples](../examples/)
- Open an [issue](https://github.com/yourusername/clarity-ux-insights/issues)
