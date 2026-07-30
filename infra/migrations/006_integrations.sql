CREATE TABLE IF NOT EXISTS integrations (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR REFERENCES organizations(id),
    platform VARCHAR,
    name VARCHAR,
    status VARCHAR DEFAULT 'pending_auth',
    error_message VARCHAR,
    credentials TEXT,
    config JSON,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    next_sync_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS integration_credentials_history (
    id VARCHAR PRIMARY KEY,
    integration_id VARCHAR REFERENCES integrations(id),
    old_credentials_hash VARCHAR,
    new_credentials_hash VARCHAR,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sync_logs (
    id VARCHAR PRIMARY KEY,
    integration_id VARCHAR REFERENCES integrations(id),
    sync_type VARCHAR,
    status VARCHAR,
    items_processed INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    errors JSON,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);
