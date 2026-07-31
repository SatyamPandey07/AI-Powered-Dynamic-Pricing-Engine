CREATE TABLE IF NOT EXISTS model_versions (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR REFERENCES organizations(id),
    sku_id VARCHAR REFERENCES skus(id),
    model_type VARCHAR,
    accuracy_mape DOUBLE PRECISION,
    accuracy_mae DOUBLE PRECISION,
    trained_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    activated_at TIMESTAMP WITH TIME ZONE,
    model_artifact VARCHAR,
    parameters JSON
);
