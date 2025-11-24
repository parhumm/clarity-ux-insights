-- Clarity API Data Storage Schema

-- Main metrics table for all fetched data
CREATE TABLE IF NOT EXISTS clarity_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fetch_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metric_name TEXT NOT NULL,
    num_days INTEGER NOT NULL,

    -- Metrics data
    total_session_count INTEGER,
    total_bot_session_count INTEGER,
    distinct_user_count INTEGER,
    pages_per_session REAL,

    -- Dimensions
    dimension1_name TEXT,
    dimension1_value TEXT,
    dimension2_name TEXT,
    dimension2_value TEXT,
    dimension3_name TEXT,
    dimension3_value TEXT,

    -- Raw data
    raw_json TEXT,

    -- Prevent duplicates
    UNIQUE(metric_name, num_days, dimension1_name, dimension1_value, dimension2_name, dimension2_value, dimension3_name, dimension3_value)
);

-- API request log
CREATE TABLE IF NOT EXISTS api_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    endpoint TEXT NOT NULL,
    num_days INTEGER,
    dimension1 TEXT,
    dimension2 TEXT,
    dimension3 TEXT,
    status_code INTEGER,
    success BOOLEAN,
    error_message TEXT,
    response_size INTEGER,
    rows_returned INTEGER
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_metrics_dimensions ON clarity_metrics(dimension1_name, dimension1_value, dimension2_name, dimension2_value);
CREATE INDEX IF NOT EXISTS idx_metrics_fetch_time ON clarity_metrics(fetch_timestamp);
CREATE INDEX IF NOT EXISTS idx_requests_timestamp ON api_requests(request_timestamp);
