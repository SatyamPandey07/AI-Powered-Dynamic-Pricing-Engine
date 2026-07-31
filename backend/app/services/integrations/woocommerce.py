"""
WooCommerce Integration
========================
Authenticates via HTTP Basic Auth (API Key + API Secret).
Communicates with WooCommerce REST API v3.
"""
import httpx
from base64 import b64encode
import logging
from typing import Optional
from .base import BaseIntegration

logger = logging.getLogger(__name__)


class WooCommerceIntegration(BaseIntegration):
    platform_name = "woocommerce"

    @property
    def _base_url(self) -> str:
        return self.credentials.get("site_url", "").rstrip("/") + "/wp-json/wc/v3"

    @property
    def _auth_header(self) -> str:
        key = self.credentials.get("api_key", "")
        secret = self.credentials.get("api_secret", "")
        token = b64encode(f"{key}:{secret}".encode()).decode()
        return f"Basic {token}"

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            headers={"Authorization": self._auth_header, "Content-Type": "application/json"},
            timeout=30.0,
            verify=self.credentials.get("ssl_verify", True),
        )

    async def test_connection(self) -> dict:
        async with self._client() as client:
            try:
                r = await client.get(f"{self._base_url}/system_status")
                r.raise_for_status()
                return {"status": "success", "wc_version": r.json().get("environment", {}).get("wc_version")}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

    async def fetch_products(self) -> list[dict]:
        async with self._client() as client:
            r = await client.get(f"{self._base_url}/products", params={"per_page": 100})
            r.raise_for_status()
            products = r.json()
            result = []
            for p in products:
                result.append({
                    "product_id": str(p["id"]),
                    "sku": p.get("sku", str(p["id"])),
                    "title": p.get("name"),
                    "price": float(p.get("price", 0) or 0),
                    "inventory_quantity": p.get("stock_quantity") or 0,
                })
            return result

    async def fetch_orders(self, since: Optional[str] = None) -> list[dict]:
        async with self._client() as client:
            params: dict = {"per_page": 100, "status": "any"}
            if since:
                params["after"] = since
            r = await client.get(f"{self._base_url}/orders", params=params)
            r.raise_for_status()
            orders = r.json()
            result = []
            for o in orders:
                line_items = [
                    {
                        "sku": li.get("sku") or str(li.get("product_id", "")),
                        "quantity": li.get("quantity", 1),
                        "price": float(li.get("price", 0) or 0),
                    }
                    for li in o.get("line_items", [])
                ]
                result.append({
                    "order_id": str(o["id"]),
                    "date": o.get("date_created"),
                    "line_items": line_items,
                })
            return result

    async def push_price(self, product_id: str, new_price: float) -> bool:
        async with self._client() as client:
            url = f"{self._base_url}/products/{product_id}"
            body = {"regular_price": str(new_price)}
            r = await client.put(url, json=body)
            r.raise_for_status()
            return True
