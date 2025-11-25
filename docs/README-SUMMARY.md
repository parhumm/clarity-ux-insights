# Clarity UX Insights - Complete System

Universal UX insights and reporting system for Microsoft Clarity.

## What's Included

### ✅ Core Infrastructure (Completed)

1. **Time-Series Database**
   - Optimized for date-range queries
   - Daily, weekly, and monthly metrics
   - Page-specific tracking
   - 3,384+ records migrated

2. **Universal Configuration**
   - Works for any website type
   - YAML-based configuration
   - Page tracking with categories
   - Auto-track patterns

3. **Flexible Query Engine**
   - 30+ date format support
   - Smart date parsing
   - Fast database queries
   - Metric aggregation

4. **Universal Templates**
   - 7 report templates
   - Multi-audience insights
   - No hardcoded data
   - 65-71 dynamic placeholders

5. **Aggregation Engine**
   - Weekly summaries (ISO weeks)
   - Monthly summaries
   - Auto-aggregation
   - Duplicate prevention

6. **Documentation**
   - Quick start guide
   - Date format reference
   - Configuration guide
   - Example configs

## Features

### Data Collection
- Microsoft Clarity API integration
- Multi-dimensional queries (Device, Country, Browser)
- Rate limiting and retry logic
- Audit trail (fetch_log table)

### Data Storage
- SQLite database (time-series optimized)
- Daily metrics with date indexing
- Weekly/monthly aggregation cache
- Page tracking configuration

### Data Query
- Flexible date expressions ("7", "last-week", "November", "2025-Q4")
- Metric filtering by name, scope, page, dimensions
- Fast aggregation (avg, sum, min, max)
- Available date discovery

### Reports (Templates Ready)
1. **UX Health Overview** - Overall health with critical issues
2. **Frustration Analysis** - Deep dive into user frustration
3. **Device Performance** - Mobile/Desktop/Tablet comparison
4. **Geographic Insights** - Global reach and top markets
5. **Content Performance** - Page and category analysis
6. **Engagement Analysis** - Time, scroll, behavior metrics
7. **Page Analysis** - Single page deep dive

### Configuration
- Project metadata (name, type, URL)
- Page tracking (custom pages + auto-track patterns)
- Data management (retention, cleanup, storage)
- Report settings (formats, auto-generation)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Microsoft Clarity API               │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              fetch_clarity_data.py                  │
│  (API client with rate limiting & retry logic)      │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│         data/clarity_data.db (SQLite)               │
│  ┌──────────────┬──────────────┬─────────────────┐  │
│  │daily_metrics │weekly_metrics│monthly_metrics  │  │
│  │   (3,386)    │    (cache)   │    (cache)      │  │
│  └──────────────┴──────────────┴─────────────────┘  │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌──────────────────┐    ┌──────────────────┐
│  Query Engine    │    │   Aggregator     │
│  (date parsing)  │    │  (weekly/monthly)│
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌──────────────────────┐
         │  Report Generator    │
         │  (template → report) │
         └───────────┬──────────┘
                     ▼
         ┌──────────────────────┐
         │   reports/generated/ │
         │   (markdown + CSV)   │
         └──────────────────────┘
```

## Directory Structure

```
clarity-ux-insights/
├── config.yaml              # User configuration (gitignored)
├── config.template.yaml     # Configuration template
├── config_loader.py         # Configuration parser
├── clarity_client.py        # Clarity API client
├── fetch_clarity_data.py    # Data fetching script
│
├── database/
│   ├── schema_v2.sql        # Time-series schema
│   ├── migrate_to_v2.py     # Migration script
│   └── db_manager.py        # Database operations
│
├── scripts/
│   ├── query_engine.py      # Flexible date queries
│   └── aggregator.py        # Weekly/monthly aggregation
│
├── templates/
│   ├── general/             # General report templates (6)
│   └── pages/               # Page-specific templates (1)
│
├── examples/
│   ├── ecommerce-config.yaml
│   ├── saas-config.yaml
│   └── media-streaming-config.yaml
│
├── tests/                   # Comprehensive test suite
│   ├── test_database_v2.py
│   ├── test_config.py
│   ├── test_query_engine.py
│   ├── test_aggregator.py
│   ├── test_templates.py
│   └── test_results/        # Test documentation
│
├── docs/
│   ├── QUICK-START.md
│   ├── DATE-FORMATS.md
│   └── README-SUMMARY.md
│
├── data/                    # User data (gitignored)
│   └── clarity_data.db
│
└── reports/                 # Generated reports (gitignored)
    ├── generated/
    └── archive/
```

## Test Coverage

- **26+ tests** across 5 test suites
- **All tests passing** (26/26)
- Database operations
- Configuration loading
- Date parsing (30+ formats)
- Query engine
- Aggregation
- Template validation

## Performance

- Date parsing: <1ms
- Database queries: <100ms (with indexes)
- Weekly aggregation: <50ms
- Monthly aggregation: <100ms
- Works with thousands of records

## Usage Examples

### Configuration

```yaml
# config.yaml
project:
  name: "My Website"
  type: "e-commerce"

tracking:
  pages:
    - id: page-001
      path: "/checkout"
      name: "Checkout"
      category: "conversion"

reports:
  default_period_days: 7
  output_formats: ["markdown", "csv"]
```

### Query Data

```python
from scripts.query_engine import QueryEngine

engine = QueryEngine()

# Last 7 days
metrics = engine.query_metrics("7", metric_name="Traffic")

# November 2025
metrics = engine.query_metrics("November")

# Aggregate
agg = engine.aggregate_metrics("2025-Q4", "Traffic")
```

### Aggregate Data

```python
from scripts.aggregator import MetricAggregator

aggregator = MetricAggregator()

# Aggregate all available data
counts = aggregator.aggregate_all_available()
# Returns: {'weekly': 4, 'monthly': 2}
```

## Commits

6 commits with full testing and documentation:

1. **Directory structure & .gitignore** - Safe data handling
2. **Time-series database schema** - Optimized storage
3. **Universal configuration system** - Any project type
4. **Flexible query engine** - 30+ date formats
5. **Universal templates** - Multi-audience insights
6. **Aggregation engine** - Weekly/monthly summaries

## Next Steps

Remaining features to implement:
- Report generator (database → templates)
- Period comparison tool
- Trend analysis engine
- Archive manager
- CLI with date parsing
- Claude slash commands

## License

See LICENSE file.

## Support

- Documentation: See `docs/` directory
- Examples: See `examples/` directory
- Issues: GitHub Issues
- Tests: Run `python tests/test_*.py`
