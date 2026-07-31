from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, Enum, JSON
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"))
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(RoleEnum))
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

class Competitor(Base):
    __tablename__ = "competitors"
    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, ForeignKey("organizations.id"))
    name = Column(String)
    website_url = Column(String)
    api_type = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CompetitorSkuMapping(Base):
    __tablename__ = "competitor_sku_mappings"
    id = Column(String, primary_key=True, index=True)
    competitor_id = Column(String, ForeignKey("competitors.id"))
    sku_id = Column(String, ForeignKey("skus.id"))
    competitor_sku_id = Column(String)
    last_price = Column(Float)
    last_checked_at = Column(DateTime(timezone=True))

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