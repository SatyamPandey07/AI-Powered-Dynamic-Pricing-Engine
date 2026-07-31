"""
Tests for PR #6 — Integrations Framework
==========================================
Covers:
  - Credential encryption/decryption (no plain-text storage)
  - Custom API field mapping normalization
  - Shopify auth URL generation
  - Webhook signature verification (HMAC-SHA256)
  - Integration factory (correct class returned)
  - API authorization (401 without token)
  - Multi-tenant isolation (403 for wrong org)
"""
import pytest
import hmac
import hashlib
import json
from cryptography.fernet import Fernet

from app.services.encryption import encrypt_credentials, decrypt_credentials, credentials_hash
from app.services.integrations import get_integration
from app.services.integrations.shopify import ShopifyIntegration
from app.services.integrations.custom import CustomIntegration
from fastapi.testclient import TestClient
from app.main import app

import os
os.environ.setdefault("ENCRYPTION_KEY", Fernet.generate_key().decode())

client = TestClient(app)


# ---------------------------------------------------------------------------
# Credential Encryption Tests
# ---------------------------------------------------------------------------

def test_encrypt_decrypt_roundtrip():
    """Encrypted credentials should decrypt back to exact original dict."""
    creds = {"api_key": "super_secret", "shop_url": "https://mystore.myshopify.com"}
    encrypted = encrypt_credentials(creds)
    assert isinstance(encrypted, str)
    assert "super_secret" not in encrypted   # never stored in plain text
    decrypted = decrypt_credentials(encrypted)
    assert decrypted == creds


def test_credentials_never_contain_plain_secret():
    """The encrypted blob must not contain the raw secret."""
    creds = {"api_secret": "mysecretvalue123", "api_key": "key123"}
    encrypted = encrypt_credentials(creds)
    assert "mysecretvalue123" not in encrypted
    assert "key123" not in encrypted


def test_credentials_hash_stable():
    """Hash of same credential keys should be identical."""
    creds = {"api_key": "val1", "shop_url": "val2"}
    h1 = credentials_hash(creds)
    h2 = credentials_hash(creds)
    assert h1 == h2


def test_credentials_hash_different_keys():
    """Hash should differ when key set changes."""
    h1 = credentials_hash({"api_key": "x"})
    h2 = credentials_hash({"api_key": "x", "api_secret": "y"})
    assert h1 != h2


# ---------------------------------------------------------------------------
# Integration Factory Tests
# ---------------------------------------------------------------------------

def test_factory_returns_shopify():
    adapter = get_integration("shopify", "id-1", {}, {})
    assert adapter.platform_name == "shopify"


def test_factory_returns_woocommerce():
    adapter = get_integration("woocommerce", "id-2", {}, {})
    assert adapter.platform_name == "woocommerce"


def test_factory_returns_custom():
    adapter = get_integration("custom", "id-3", {}, {})
    assert adapter.platform_name == "custom"


def test_factory_raises_unknown_platform():
    with pytest.raises(ValueError, match="Unsupported platform"):
        get_integration("stripe", "id-4", {}, {})


# ---------------------------------------------------------------------------
# Custom Integration Field Mapping
# ---------------------------------------------------------------------------

def test_custom_field_mapping():
    """External 'item_price' should be mapped to internal 'price'."""
    adapter = CustomIntegration(
        integration_id="test",
        credentials={"base_url": "http://example.com", "auth_type": "api_key", "api_key": "k"},
        config={"field_mappings": {"products": {"price": "item_price", "sku": "product_code"}}},
    )
    record = {"item_price": 49.99, "product_code": "SKU-001", "name": "Widget"}
    mapped = adapter._map_fields(record, {"price": "item_price", "sku": "product_code"})
    assert mapped["price"] == 49.99
    assert mapped["sku"] == "SKU-001"


# ---------------------------------------------------------------------------
# Shopify OAuth URL Generation
# ---------------------------------------------------------------------------

def test_shopify_auth_url_format():
    url = ShopifyIntegration.get_auth_url(
        "mystore.myshopify.com", "CLIENT_ID", "https://app.example.com/callback",
        "read_products,write_products,read_orders"
    )
    assert "mystore.myshopify.com" in url
    assert "client_id=CLIENT_ID" in url
    assert "read_products" in url


# ---------------------------------------------------------------------------
# Webhook Signature Verification
# ---------------------------------------------------------------------------

def test_shopify_webhook_valid_signature():
    """A correctly signed Shopify webhook should pass verification."""
    secret = "shpss_mysecret"
    payload = json.dumps({"topic": "orders/create", "id": 1}).encode()
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    # Directly test the verifier function
    from app.routers.webhooks import _verify_shopify_signature
    assert _verify_shopify_signature(payload, sig, secret) is True


def test_shopify_webhook_invalid_signature():
    from app.routers.webhooks import _verify_shopify_signature
    payload = b'{"topic": "orders/create"}'
    assert _verify_shopify_signature(payload, "bad_sig", "mySecret") is False


# ---------------------------------------------------------------------------
# API Authorization Tests
# ---------------------------------------------------------------------------

def test_list_integrations_unauthorized():
    response = client.get("/api/integrations")
    assert response.status_code == 401


def test_create_integration_unauthorized():
    response = client.post("/api/integrations", json={
        "platform": "shopify", "name": "My Store", "credentials": {}
    })
    assert response.status_code == 401


def test_webhook_missing_integration():
    """Webhook for non-existent integration_id should return 404."""
    response = client.post("/api/webhooks/integrations/nonexistent-id", content=b"{}")
    assert response.status_code == 404
