"""
Abstract Base Integration
==========================
All platform integrations inherit from BaseIntegration.
Implementations must override: authenticate, fetch_products, fetch_orders, push_price.
"""
from abc import ABC, abstractmethod
from typing import Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

RETRY_DELAYS = [1, 2, 4, 8, 16]  # Exponential backoff in seconds


async def with_retry(coro, max_retries: int = 5):
    """Run a coroutine with exponential backoff on failure."""
    for attempt, delay in enumerate(RETRY_DELAYS[:max_retries], 1):
        try:
            return await coro
        except Exception as e:
            if attempt == max_retries:
                raise
            logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
            await asyncio.sleep(delay)


class BaseIntegration(ABC):
    """
    Abstract base class for all e-commerce platform integrations.
    """
    platform_name: str = "base"

    def __init__(self, integration_id: str, credentials: dict, config: dict):
        self.integration_id = integration_id
        self.credentials = credentials
        self.config = config

    @abstractmethod
    async def test_connection(self) -> dict:
        """Verify that credentials are valid and the platform is reachable."""
        pass

    @abstractmethod
    async def fetch_products(self) -> list[dict]:
        """
        Fetch all products from the platform.
        Returns list of dicts: [{sku_id, name, price, inventory_quantity, ...}]
        """
        pass

    @abstractmethod
    async def fetch_orders(self, since: Optional[str] = None) -> list[dict]:
        """
        Fetch orders from the platform since a given ISO date string.
        Returns list of dicts: [{order_id, date, line_items: [{sku_id, qty, price}]}]
        """
        pass

    @abstractmethod
    async def push_price(self, product_id: str, new_price: float) -> bool:
        """
        Push a new price for a product to the platform.
        Returns True on success, raises on failure.
        """
        pass

    async def sync_inventory(self) -> dict:
        """High-level sync: fetch products and return inventory data."""
        products = await with_retry(self.fetch_products())
        inventory = [
            {"sku_id": p.get("sku"), "quantity": p.get("inventory_quantity", 0)}
            for p in products
        ]
        return {"items": inventory, "count": len(inventory)}

    async def sync_sales(self, since: Optional[str] = None) -> dict:
        """High-level sync: fetch orders and flatten to sales records."""
        orders = await with_retry(self.fetch_orders(since=since))
        sales = []
        for order in orders:
            for item in order.get("line_items", []):
                sales.append({
                    "date": order.get("date"),
                    "sku_id": item.get("sku"),
                    "units_sold": item.get("quantity", 1),
                    "revenue": item.get("price", 0) * item.get("quantity", 1),
                    "price": item.get("price", 0),
                    "order_id": order.get("order_id"),
                })
        return {"sales": sales, "count": len(sales)}
