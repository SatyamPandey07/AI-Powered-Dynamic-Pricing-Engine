CREATE TABLE IF NOT EXISTS elasticity_measurements (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR REFERENCES organizations(id),
    sku_id VARCHAR REFERENCES skus(id),
    elasticity_value DOUBLE PRECISION,
    confidence_lower DOUBLE PRECISION,
    confidence_upper DOUBLE PRECISION,
    data_points INTEGER,
    r_squared DOUBLE PRECISION,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    model_type VARCHAR DEFAULT 'regression'
);

CREATE TABLE IF NOT EXISTS pricing_tests (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR REFERENCES organizations(id),
    sku_id VARCHAR REFERENCES skus(id),
    control_price DOUBLE PRECISION,
    treatment_price DOUBLE PRECISION,
    traffic_split DOUBLE PRECISION DEFAULT 0.5,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    control_conversions INTEGER DEFAULT 0,
    treatment_conversions INTEGER DEFAULT 0,
    control_revenue DOUBLE PRECISION DEFAULT 0,
    treatment_revenue DOUBLE PRECISION DEFAULT 0,
    p_value DOUBLE PRECISION,
    confidence DOUBLE PRECISION DEFAULT 0.95,
    winner VARCHAR,
    winner_revenue_lift DOUBLE PRECISION,
    status VARCHAR DEFAULT 'running'
);

CREATE TABLE IF NOT EXISTS price_recommendations (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR REFERENCES organizations(id),
    sku_id VARCHAR REFERENCES skus(id),
    recommended_price DOUBLE PRECISION,
    current_price DOUBLE PRECISION,
    objective VARCHAR,
    expected_revenue_impact DOUBLE PRECISION,
    expected_margin_impact DOUBLE PRECISION,
    confidence_score DOUBLE PRECISION,
    reasoning TEXT,
    factors JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    accepted_at TIMESTAMP WITH TIME ZONE,
    actual_impact DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS pricing_rules (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR REFERENCES organizations(id),
    name VARCHAR,
    condition JSON,
    action JSON,
    active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    last_applied_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
