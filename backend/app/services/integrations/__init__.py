"""
Integration factory — maps platform name to the right class.
"""
from .shopify import ShopifyIntegration
from .woocommerce import WooCommerceIntegration
from .custom import CustomIntegration
from .base import BaseIntegration

PLATFORM_MAP = {
    "shopify": ShopifyIntegration,
    "woocommerce": WooCommerceIntegration,
    "custom": CustomIntegration,
}


def get_integration(platform: str, integration_id: str, credentials: dict, config: dict) -> BaseIntegration:
    """Instantiate the correct integration class for the given platform."""
    cls = PLATFORM_MAP.get(platform)
    if not cls:
        raise ValueError(f"Unsupported platform: {platform}. Choose from: {list(PLATFORM_MAP.keys())}")
    return cls(integration_id=integration_id, credentials=credentials, config=config)
