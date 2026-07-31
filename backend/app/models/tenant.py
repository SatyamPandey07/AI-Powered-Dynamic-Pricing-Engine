from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, Enum, JSON, Boolean
from sqlalchemy.sql import func
from .base import Base
import enum

class RoleEnum(str, enum.Enum):
    admin = "admin"
    viewer = "viewer"
    editor = "editor"

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    subscription_tier = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"))
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(RoleEnum))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PasswordHistory(Base):
    __tablename__ = "password_history"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"))
    key_hash = Column(String)
    name = Column(String)
    last_used_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Sku(Base):
    __tablename__ = "skus"
    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"))
    name = Column(String)
    cost = Column(Float)
    min_price = Column(Float)
    max_price = Column(Float)
    category = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"))
    name = Column(String)
    api_endpoint = Column(String)
    auth_type = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PriceHistory(Base):
    __tablename__ = "price_history"
    time = Column(DateTime(timezone=True), primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), primary_key=True)
    sku_id = Column(String, ForeignKey("skus.id"), primary_key=True)
    price = Column(Float)
    source = Column(String) # internal/competitor
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SalesHistory(Base):
    __tablename__ = "sales_history"
    time = Column(DateTime(timezone=True), primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), primary_key=True)
    sku_id = Column(String, ForeignKey("skus.id"), primary_key=True)
    units_sold = Column(Integer)
    revenue = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ForecastHistory(Base):
    __tablename__ = "forecast_history"
    time = Column(DateTime(timezone=True), primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), primary_key=True)
    sku_id = Column(String, ForeignKey("skus.id"), primary_key=True)
    forecast_date = Column(DateTime(timezone=True))
    forecasted_units = Column(Float)
    confidence_lower = Column(Float)
    confidence_upper = Column(Float)
    model_version = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"))
    user_id = Column(String, ForeignKey("users.id"))
    action = Column(String)
    resource_type = Column(String)
    resource_id = Column(String)
    changes_before = Column(JSON)
    changes_after = Column(JSON)
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ModelVersion(Base):
    __tablename__ = "model_versions"
    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"))
    sku_id = Column(String, ForeignKey("skus.id"))
    model_type = Column(String)
    accuracy_mape = Column(Float)
    accuracy_mae = Column(Float)
    trained_at = Column(DateTime(timezone=True), server_default=func.now())
    activated_at = Column(DateTime(timezone=True))
    model_artifact = Column(String)
    parameters = Column(JSON)

class Competitor(Base):
    __tablename__ = "competitors"
    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"))
    name = Column(String)
    website_url = Column(String)
    api_type = Column(String)
    scrape_config = Column(JSON)
    last_checked_at = Column(DateTime(timezone=True))
    status = Column(String)
    error_message = Column(String)
    update_frequency_hours = Column(Integer, default=24)

class CompetitorSKUMapping(Base):
    __tablename__ = "competitor_sku_mappings"
    id = Column(String, primary_key=True, index=True)
    competitor_id = Column(String, ForeignKey("competitors.id"))
    sku_id = Column(String, ForeignKey("skus.id"))
    competitor_sku_id = Column(String)
    competitor_product_url = Column(String)
    last_price = Column(Float)
    last_updated_at = Column(DateTime(timezone=True))

class WeatherSignal(Base):
    __tablename__ = "weather_signals"
    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"))
    time = Column(DateTime(timezone=True), server_default=func.now())
    location = Column(String)
    temperature = Column(Float)
    humidity = Column(Float)
    precipitation = Column(Float)
    condition = Column(String)
    forecast_next_7_days = Column(JSON)

class EventSignal(Base):
    __tablename__ = "event_signals"
    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"))
    event_name = Column(String)
    event_date = Column(DateTime(timezone=True))
    affected_skus = Column(JSON) # List of SKU IDs
    impact_percent = Column(Float)

class ElasticityMeasurement(Base):
    __tablename__ = "elasticity_measurements"
    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"))
    sku_id = Column(String, ForeignKey("skus.id"))
    elasticity_value = Column(Float)
    confidence_lower = Column(Float)
    confidence_upper = Column(Float)
    data_points = Column(Integer)
    r_squared = Column(Float)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    model_type = Column(String, default="regression")  # regression | ab_test

class PricingTest(Base):
    __tablename__ = "pricing_tests"
    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"))
    sku_id = Column(String, ForeignKey("skus.id"))
    control_price = Column(Float)
    treatment_price = Column(Float)
    traffic_split = Column(Float, default=0.5)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    control_conversions = Column(Integer, default=0)
    treatment_conversions = Column(Integer, default=0)
    control_revenue = Column(Float, default=0.0)
    treatment_revenue = Column(Float, default=0.0)
    p_value = Column(Float)
    confidence = Column(Float, default=0.95)
    winner = Column(String)  # control | treatment | no_significant_difference
    winner_revenue_lift = Column(Float)
    status = Column(String, default="running")  # running | completed

class PriceRecommendation(Base):
    __tablename__ = "price_recommendations"
    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"))
    sku_id = Column(String, ForeignKey("skus.id"))
    recommended_price = Column(Float)
    current_price = Column(Float)
    objective = Column(String)  # revenue | margin | clearance
    expected_revenue_impact = Column(Float)
    expected_margin_impact = Column(Float)
    confidence_score = Column(Float)
    reasoning = Column(String)
    factors = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True))
    actual_impact = Column(Float)

class PricingRule(Base):
    __tablename__ = "pricing_rules"
    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"))
    name = Column(String)
    condition = Column(JSON)
    action = Column(JSON)
    active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    last_applied_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Integration(Base):
    __tablename__ = "integrations"
    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"))
    platform = Column(String)           # shopify | woocommerce | custom
    name = Column(String)
    status = Column(String, default="pending_auth")  # connected | disconnected | error | pending_auth
    error_message = Column(String)
    credentials = Column(String)        # Fernet-encrypted JSON text
    config = Column(JSON)               # sync_frequency_hours, field_mappings, etc.
    last_sync_at = Column(DateTime(timezone=True))
    next_sync_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class IntegrationCredentialHistory(Base):
    __tablename__ = "integration_credentials_history"
    id = Column(String, primary_key=True, index=True)
    integration_id = Column(String, ForeignKey("integrations.id"))
    old_credentials_hash = Column(String)
    new_credentials_hash = Column(String)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

class SyncLog(Base):
    __tablename__ = "sync_logs"
    id = Column(String, primary_key=True, index=True)
    integration_id = Column(String, ForeignKey("integrations.id"))
    sync_type = Column(String)          # inventory | sales | prices
    status = Column(String)             # running | completed | failed
    items_processed = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    errors = Column(JSON)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

class Webhook(Base):
    __tablename__ = "webhooks"
    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"))
    endpoint_type = Column(String)       # price / forecast / alert
    target_url = Column(String)
    events_subscribed = Column(JSON)     # e.g., ["price.updated", "forecast.generated"]
    signing_secret = Column(String)      # HMAC-SHA256 secret
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"
    id = Column(String, primary_key=True, index=True)
    webhook_id = Column(String, ForeignKey("webhooks.id"))
    event_type = Column(String)
    payload = Column(JSON)
    status = Column(String, default="pending")  # pending | success | failed
    attempt_number = Column(Integer, default=0)
    next_retry_at = Column(DateTime(timezone=True))
    response_code = Column(Integer)
    response_body = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())