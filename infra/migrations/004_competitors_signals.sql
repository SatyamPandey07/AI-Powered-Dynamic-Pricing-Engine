CREATE TABLE IF NOT EXISTS competitors (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR REFERENCES organizations(id),
    name VARCHAR,
    website_url VARCHAR,
    api_type VARCHAR,
    scrape_config JSON,
    last_checked_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR,
    error_message VARCHAR,
    update_frequency_hours INTEGER DEFAULT 24
);

CREATE TABLE IF NOT EXISTS competitor_sku_mappings (
    id VARCHAR PRIMARY KEY,
    competitor_id VARCHAR REFERENCES competitors(id),
    sku_id VARCHAR REFERENCES skus(id),
    competitor_sku_id VARCHAR,
    competitor_product_url VARCHAR,
    last_price DOUBLE PRECISION,
    last_updated_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS weather_signals (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR REFERENCES organizations(id),
    time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    location VARCHAR,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    precipitation DOUBLE PRECISION,
    condition VARCHAR,
    forecast_next_7_days JSON
);

CREATE TABLE IF NOT EXISTS event_signals (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR REFERENCES organizations(id),
    event_name VARCHAR,
    event_date TIMESTAMP WITH TIME ZONE,
    affected_skus JSON,
    impact_percent DOUBLE PRECISION
);

ALTER TABLE price_history ADD COLUMN IF NOT EXISTS source VARCHAR;
