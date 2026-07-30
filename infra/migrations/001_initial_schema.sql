-- organizations
CREATE TABLE IF NOT EXISTS organizations (
    id VARCHAR PRIMARY KEY,
    name VARCHAR,
    subscription_tier VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- users
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR REFERENCES organizations(id),
    email VARCHAR UNIQUE,
    hashed_password VARCHAR,
    role VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- api_keys
CREATE TABLE IF NOT EXISTS api_keys (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR REFERENCES organizations(id),
    key_hash VARCHAR,
    name VARCHAR,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- skus
CREATE TABLE IF NOT EXISTS skus (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR REFERENCES organizations(id),
    name VARCHAR,
    cost DOUBLE PRECISION,
    min_price DOUBLE PRECISION,
    max_price DOUBLE PRECISION,
    category VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- suppliers
CREATE TABLE IF NOT EXISTS suppliers (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR REFERENCES organizations(id),
    name VARCHAR,
    api_endpoint VARCHAR,
    auth_type VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- competitors
CREATE TABLE IF NOT EXISTS competitors (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR REFERENCES organizations(id),
    name VARCHAR,
    website_url VARCHAR,
    api_type VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- competitor_sku_mappings
CREATE TABLE IF NOT EXISTS competitor_sku_mappings (
    id VARCHAR PRIMARY KEY,
    competitor_id VARCHAR REFERENCES competitors(id),
    sku_id VARCHAR REFERENCES skus(id),
    competitor_sku_id VARCHAR,
    last_price DOUBLE PRECISION,
    last_checked_at TIMESTAMP WITH TIME ZONE
);

-- price_history (TimescaleDB Hypertable)
CREATE TABLE IF NOT EXISTS price_history (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    org_id VARCHAR REFERENCES organizations(id),
    sku_id VARCHAR REFERENCES skus(id),
    price DOUBLE PRECISION,
    source VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (time, org_id, sku_id)
);
SELECT create_hypertable('price_history', 'time', if_not_exists => TRUE);

-- sales_history (TimescaleDB Hypertable)
CREATE TABLE IF NOT EXISTS sales_history (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    org_id VARCHAR REFERENCES organizations(id),
    sku_id VARCHAR REFERENCES skus(id),
    units_sold INTEGER,
    revenue DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (time, org_id, sku_id)
);
SELECT create_hypertable('sales_history', 'time', if_not_exists => TRUE);

-- forecast_history (TimescaleDB Hypertable)
CREATE TABLE IF NOT EXISTS forecast_history (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    org_id VARCHAR REFERENCES organizations(id),
    sku_id VARCHAR REFERENCES skus(id),
    forecast_date TIMESTAMP WITH TIME ZONE,
    forecasted_units DOUBLE PRECISION,
    confidence_lower DOUBLE PRECISION,
    confidence_upper DOUBLE PRECISION,
    model_version VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (time, org_id, sku_id)
);
SELECT create_hypertable('forecast_history', 'time', if_not_exists => TRUE);

-- audit_logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR REFERENCES organizations(id),
    user_id VARCHAR REFERENCES users(id),
    action VARCHAR,
    resource_type VARCHAR,
    resource_id VARCHAR,
    changes_before JSONB,
    changes_after JSONB,
    ip_address VARCHAR,
    user_agent VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
