import httpx
import logging
import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ExternalSignalsService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=10.0)

    async def fetch_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Fetches weather data from OpenWeatherMap (mocked if no API key).
        """
        if not self.api_key:
            logger.info(f"No OpenWeatherMap API key found, mocking weather for {location}")
            # Mocked data structure
            return {
                "temperature": 72.5,
                "humidity": 45.0,
                "precipitation": 0.0,
                "condition": "Clear",
                "forecast_next_7_days": [
                    {"day": 1, "temp": 73.0, "condition": "Clear"},
                    {"day": 2, "temp": 71.0, "condition": "Cloudy"},
                    {"day": 3, "temp": 68.0, "condition": "Rain"},
                    {"day": 4, "temp": 65.0, "condition": "Rain"},
                    {"day": 5, "temp": 69.0, "condition": "Partly Cloudy"},
                    {"day": 6, "temp": 74.0, "condition": "Clear"},
                    {"day": 7, "temp": 76.0, "condition": "Clear"}
                ]
            }
            
        try:
            # Placeholder for actual OpenWeatherMap API call
            url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.api_key}&units=imperial"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            return {
                "temperature": data.get("main", {}).get("temp"),
                "humidity": data.get("main", {}).get("humidity"),
                "precipitation": data.get("rain", {}).get("1h", 0.0),
                "condition": data.get("weather", [{}])[0].get("main"),
                "forecast_next_7_days": [] # Would require a OneCall API request
            }
        except Exception as e:
            logger.error(f"Failed to fetch weather for {location}: {e}")
            return None

    async def fetch_events(self, location: str, date_from: datetime.date, date_to: datetime.date) -> list:
        """
        Fetches local events/holidays (mocked implementation).
        """
        logger.info(f"Mocking event fetch for {location} between {date_from} and {date_to}")
        return [
            {
                "event_name": "Local Music Festival",
                "event_date": str(date_from + datetime.timedelta(days=2)),
                "impact_percent": 15.0
            }
        ]

    async def close(self):
        await self.client.aclose()
