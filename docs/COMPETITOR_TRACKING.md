# Competitor Price Tracking

The system uses an async HTML parser (`httpx` + `BeautifulSoup`) to scrape competitor websites and extract pricing data.

## Configuration
Each competitor requires a JSON `scrape_config` specifying how to extract the price.
For example, for Amazon:
```json
{
  "price_selector": ".a-price-whole"
}
```

## SKU Mapping
Competitor SKUs are mapped to internal SKUs in the `competitor_sku_mappings` table. A single internal SKU can map to multiple competitor SKUs (e.g., matching against Walmart, Target, and BestBuy).

## Background Worker
A Celery task (`scrape_competitor_prices`) fires every 4 hours to re-fetch the latest prices. Prices are logged into the `price_history` hypertable for time-series forecasting.
