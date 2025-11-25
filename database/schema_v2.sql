-- Clarity API Data Storage Schema V2
-- Time-series optimized schema for long-term analysis

-- Main daily metrics table (time-series design)
CREATE TABLE IF NOT EXISTS daily_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date DATE NOT NULL,              -- The actual date the metric represents
    fetch_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- When we fetched this data
    metric_name TEXT NOT NULL,

    -- Scope
    data_scope TEXT DEFAULT 'general',      -- 'general' or 'page'
    page_id TEXT,                           -- References pages.id (NULL for general)

    -- Dimensions (device, browser, country, etc.)
    dimension1_name TEXT,
    dimension1_value TEXT,
    dimension2_name TEXT,
    dimension2_value TEXT,
    dimension3_name TEXT,
    dimension3_value TEXT,

    -- Traffic metrics
    sessions INTEGER,
    users INTEGER,
    bot_sessions INTEGER,
    pages_per_session REAL,

    -- Frustration signals
    dead_clicks INTEGER,
    rage_clicks INTEGER,
    quick_backs INTEGER,
    error_clicks INTEGER,
    script_errors INTEGER,
    excessive_scrolls INTEGER,

    -- Engagement metrics
    scroll_depth REAL,
    engagement_time REAL,
    active_time REAL,

    -- Metadata
    source_file TEXT,                       -- Reference to raw JSON file
    raw_json TEXT,                          -- Complete raw data

    -- Unique constraint
    UNIQUE(metric_date, metric_name, data_scope, page_id,
           dimension1_name, dimension1_value,
           dimension2_name, dimension2_value,
           dimension3_name, dimension3_value)
);

-- Page tracking configuration
CREATE TABLE IF NOT EXISTS pages (
    id TEXT PRIMARY KEY,                    -- page-001, page-002, etc.
    path TEXT NOT NULL,                     -- /checkout, /search, etc.
    name TEXT NOT NULL,                     -- "Checkout", "Search"
    category TEXT,                          -- conversion, discovery, content
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(path)
);

-- Weekly aggregated metrics cache (for performance)
CREATE TABLE IF NOT EXISTS weekly_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    year INTEGER NOT NULL,
    week_number INTEGER NOT NULL,
    metric_name TEXT NOT NULL,
    data_scope TEXT DEFAULT 'general',
    page_id TEXT,

    -- Aggregated values
    avg_sessions REAL,
    sum_sessions INTEGER,
    avg_users REAL,
    sum_users INTEGER,
    avg_dead_clicks REAL,
    avg_rage_clicks REAL,
    avg_quick_backs REAL,
    avg_scroll_depth REAL,
    avg_engagement_time REAL,

    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(week_start, week_end, metric_name, data_scope, page_id)
);

-- Monthly aggregated metrics cache
CREATE TABLE IF NOT EXISTS monthly_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    metric_name TEXT NOT NULL,
    data_scope TEXT DEFAULT 'general',
    page_id TEXT,

    -- Aggregated values
    avg_sessions REAL,
    sum_sessions INTEGER,
    avg_users REAL,
    sum_users INTEGER,
    avg_dead_clicks REAL,
    avg_rage_clicks REAL,
    avg_quick_backs REAL,
    avg_scroll_depth REAL,
    avg_engagement_time REAL,

    -- Min/Max for trends
    min_sessions INTEGER,
    max_sessions INTEGER,
    data_points INTEGER,

    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, month, metric_name, data_scope, page_id)
);

-- Enhanced API fetch log
CREATE TABLE IF NOT EXISTS fetch_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fetch_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Request parameters
    request_period_days INTEGER NOT NULL,   -- How many days were requested
    date_start DATE,                        -- Start of data period
    date_end DATE,                          -- End of data period
    scope TEXT DEFAULT 'general',           -- general or page
    page_id TEXT,

    -- Dimensions requested
    dimension1 TEXT,
    dimension2 TEXT,
    dimension3 TEXT,

    -- Response info
    status_code INTEGER,
    success BOOLEAN,
    error_message TEXT,
    response_size INTEGER,

    -- Import results
    raw_file_path TEXT,
    records_imported INTEGER DEFAULT 0,
    records_skipped INTEGER DEFAULT 0,

    duration_seconds REAL
);

-- Archive tracking log
CREATE TABLE IF NOT EXISTS archive_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    archive_date DATE DEFAULT (DATE('now')),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    data_scope TEXT,
    page_id TEXT,
    records_archived INTEGER,
    archive_file_path TEXT
);

-- Indexes for fast time-series queries
CREATE INDEX IF NOT EXISTS idx_daily_date ON daily_metrics(metric_date);
CREATE INDEX IF NOT EXISTS idx_daily_date_metric ON daily_metrics(metric_date, metric_name);
CREATE INDEX IF NOT EXISTS idx_daily_page_date ON daily_metrics(page_id, metric_date);
CREATE INDEX IF NOT EXISTS idx_daily_scope ON daily_metrics(data_scope);
CREATE INDEX IF NOT EXISTS idx_daily_fetch ON daily_metrics(fetch_timestamp);

CREATE INDEX IF NOT EXISTS idx_weekly_period ON weekly_metrics(week_start, week_end);
CREATE INDEX IF NOT EXISTS idx_weekly_year ON weekly_metrics(year, week_number);

CREATE INDEX IF NOT EXISTS idx_monthly_period ON monthly_metrics(year, month);
CREATE INDEX IF NOT EXISTS idx_monthly_page ON monthly_metrics(page_id, year, month);

CREATE INDEX IF NOT EXISTS idx_fetch_timestamp ON fetch_log(fetch_timestamp);
CREATE INDEX IF NOT EXISTS idx_fetch_date_range ON fetch_log(date_start, date_end);

CREATE INDEX IF NOT EXISTS idx_pages_active ON pages(active);
