CREATE TABLE IF NOT EXISTS webhooks (
    id VARCHAR PRIMARY KEY,
    org_id VARCHAR REFERENCES organizations(id),
    endpoint_type VARCHAR,
    target_url VARCHAR,
    events_subscribed JSON,
    signing_secret VARCHAR,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS webhook_deliveries (
    id VARCHAR PRIMARY KEY,
    webhook_id VARCHAR REFERENCES webhooks(id),
    event_type VARCHAR,
    payload JSON,
    status VARCHAR DEFAULT 'pending',
    attempt_number INTEGER DEFAULT 0,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    response_code INTEGER,
    response_body TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
