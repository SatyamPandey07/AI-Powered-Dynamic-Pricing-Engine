# External Signals Integration

The dynamic pricing engine absorbs external context via two main signal vectors:

## Weather Signals
Weather heavily impacts physical goods. A background Celery worker `fetch_weather_signals` runs daily to ping the OpenWeatherMap API and fetch the 7-day forecast.
*(Note: Mocked gracefully if no API key is provided).*

## Event Signals
Local events (music festivals, holidays, sports games) spike demand for related SKUs. Events can be manually inserted or fetched via third-party calendar APIs. They store a direct `impact_percent` which the forecasting model reads when calculating expected future demand.
