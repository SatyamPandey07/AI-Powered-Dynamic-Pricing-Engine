import httpx
from bs4 import BeautifulSoup
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CompetitorScraper:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=15.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            }
        )

    async def fetch_price(self, url: str, scrape_config: dict) -> Optional[float]:
        """
        Fetches the price from a URL based on the scrape config (CSS selector).
        scrape_config example: {"price_selector": ".product-price"}
        """
        if not scrape_config or "price_selector" not in scrape_config:
            logger.error(f"Missing price_selector in scrape_config for {url}")
            return None

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            price_element = soup.select_one(scrape_config["price_selector"])
            
            if not price_element:
                logger.warning(f"Price element not found for {url} using selector {scrape_config['price_selector']}")
                return None
                
            price_text = price_element.get_text()
            # Extract numeric value (handling commas, currency symbols)
            match = re.search(r'[\d,]+\.?\d*', price_text)
            if match:
                clean_price = match.group().replace(',', '')
                return float(clean_price)
                
            return None
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return None
            
    async def close(self):
        await self.client.aclose()
