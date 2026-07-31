"""
Shopify Integration
====================
Authenticates via OAuth2 and communicates with the Shopify REST Admin API.
Rate limit: 2 requests/second (leaky bucket, 40/burst).
"""
import httpx
import logging
from typing import Optional
from .base import BaseIntegration, with_retry

logger = logging.getLogger(__name__)

SHOPIFY_API_VERSION = "2024-01"


class ShopifyIntegration(BaseIntegration):
    platform_name = "shopify"

    @property
    def _shop_url(self) -> str:
        return self.credentials.get("shop_url", "").rstrip("/")

    @property
    def _headers(self) -> dict:
        return {
            "X-Shopify-Access-Token": self.credentials.get("access_token", ""),
            "Content-Type": "application/json",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(headers=self._headers, timeout=30.0)

    async def test_connection(self) -> dict:
        async with self._client() as client:
            url = f"{self._shop_url}/admin/api/{SHOPIFY_API_VERSION}/shop.json"
            try:
                r = await client.get(url)
                r.raise_for_status()
                return {"status": "success", "shop": r.json().get("shop", {}).get("name")}
            except Exception as e:
                return {"status": "failure", "message": str(e)}

    async def fetch_products(self) -> list[dict]:
        async with self._client() as client:
            url = f"{self._shop_url}/admin/api/{SHOPIFY_API_VERSION}/products.json?limit=250"
            r = await client.get(url)
            r.raise_for_status()
            products = r.json().get("products", [])
            # Flatten variants into product records
            result = []
            for p in products:
                for v in p.get("variants", []):
                    result.append({
                        "product_id": str(p["id"]),
                        "variant_id": str(v["id"]),
                        "sku": v.get("sku", str(v["id"])),
                        "title": f"{p['title']} - {v.get('title', '')}",
                        "price": float(v.get("price", 0)),
                        "inventory_quantity": v.get("inventory_quantity", 0),
                    })
            return result

    async def fetch_orders(self, since: Optional[str] = None) -> list[dict]:
        async with self._client() as client:
            url = f"{self._shop_url}/admin/api/{SHOPIFY_API_VERSION}/orders.json?limit=250&status=any"
            if since:
                url += f"&created_at_min={since}"
            r = await client.get(url)
            r.raise_for_status()
            orders = r.json().get("orders", [])
            result = []
            for o in orders:
                line_items = [
                    {
                        "sku": li.get("sku") or li.get("variant_id", ""),
                        "quantity": li.get("quantity", 1),
                        "price": float(li.get("price", 0)),
                    }
                    for li in o.get("line_items", [])
                ]
                result.append({
                    "order_id": str(o["id"]),
                    "date": o.get("created_at"),
                    "line_items": line_items,
                })
            return result

    async def push_price(self, variant_id: str, new_price: float) -> bool:
        async with self._client() as client:
            url = f"{self._shop_url}/admin/api/{SHOPIFY_API_VERSION}/variants/{variant_id}.json"
            body = {"variant": {"id": variant_id, "price": str(new_price)}}
            r = await client.put(url, json=body)
            r.raise_for_status()
            return True

    @staticmethod
    def get_auth_url(shop_domain: str, api_key: str, redirect_uri: str, scopes: str) -> str:
        """Build the OAuth2 authorization URL."""
        return (
            f"https://{shop_domain}/admin/oauth/authorize"
            f"?client_id={api_key}&scope={scopes}&redirect_uri={redirect_uri}&state=nonce"
        )
