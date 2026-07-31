"""
Custom API Integration
=======================
A configurable adapter for any REST API. Users define endpoint paths,
auth type, and field mappings so we can normalize arbitrary external APIs.
"""
import httpx
import logging
from typing import Optional
from .base import BaseIntegration

logger = logging.getLogger(__name__)


class CustomIntegration(BaseIntegration):
    platform_name = "custom"

    @property
    def _base_url(self) -> str:
        return self.credentials.get("base_url", "").rstrip("/")

    def _auth_headers(self) -> dict:
        auth_type = self.credentials.get("auth_type", "api_key")
        if auth_type == "api_key":
            return {self.credentials.get("api_key_header", "X-API-Key"): self.credentials.get("api_key", "")}
        elif auth_type == "bearer":
            return {"Authorization": f"Bearer {self.credentials.get('token', '')}"}
        elif auth_type == "basic":
            from base64 import b64encode
            u = self.credentials.get("username", "")
            p = self.credentials.get("password", "")
            token = b64encode(f"{u}:{p}".encode()).decode()
            return {"Authorization": f"Basic {token}"}
        return {}

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(headers=self._auth_headers(), timeout=30.0)

    def _map_fields(self, record: dict, mapping: dict) -> dict:
        """Translate external field names to internal names using a mapping dict."""
        result = dict(record)
        for internal_key, external_key in mapping.items():
            if external_key in record:
                result[internal_key] = record[external_key]
        return result

    async def test_connection(self) -> dict:
        async with self._client() as client:
            test_path = self.config.get("test_endpoint", "/")
            try:
                r = await client.get(f"{self._base_url}{test_path}")
                return {"status": "success" if r.status_code < 400 else "failure", "http_status": r.status_code}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

    async def fetch_products(self) -> list[dict]:
        async with self._client() as client:
            path = self.config.get("products_endpoint", "/products")
            r = await client.get(f"{self._base_url}{path}")
            r.raise_for_status()
            raw = r.json()
            # Support both root list and nested {"products": [...]}
            items = raw if isinstance(raw, list) else raw.get("products", raw.get("items", []))
            field_map = self.config.get("field_mappings", {}).get("products", {})
            return [self._map_fields(item, field_map) for item in items]

    async def fetch_orders(self, since: Optional[str] = None) -> list[dict]:
        async with self._client() as client:
            path = self.config.get("orders_endpoint", "/orders")
            params = {}
            if since:
                date_param = self.config.get("date_filter_param", "since")
                params[date_param] = since
            r = await client.get(f"{self._base_url}{path}", params=params)
            r.raise_for_status()
            raw = r.json()
            items = raw if isinstance(raw, list) else raw.get("orders", [])
            field_map = self.config.get("field_mappings", {}).get("orders", {})
            return [self._map_fields(item, field_map) for item in items]

    async def push_price(self, product_id: str, new_price: float) -> bool:
        async with self._client() as client:
            path_template = self.config.get("update_price_endpoint", "/products/{product_id}")
            path = path_template.replace("{product_id}", product_id)
            price_field = self.config.get("price_field", "price")
            body = {price_field: new_price}
            method = self.config.get("update_price_method", "PUT").upper()
            r = await client.request(method, f"{self._base_url}{path}", json=body)
            r.raise_for_status()
            return True
