# Demand Forecasting System

The Demand Forecasting service is powered by an **Ensemble Model** combining **Facebook Prophet** and **Auto-ARIMA**.

## Why Prophet?
Prophet is highly robust to missing data and shifts in the trend. It excels at capturing strong seasonal effects (daily, weekly, yearly). We use Prophet when there is a minimum of 90 days of historical data to properly evaluate yearly and weekly cycles.

## Why ARIMA?
ARIMA (AutoRegressive Integrated Moving Average) is excellent at capturing local trends and autocorrelation in stationary series. It adapts quickly to recent changes but struggles with long-term seasonalities if not tuned properly (SARIMA). 

## Ensemble Logic
By averaging the predictions of Prophet and ARIMA, we reduce the variance and avoid large misses caused by either model over-indexing on noise.

## Fallback Mechanism
- `< 30 days of data`: Rejects training (Insufficient data).
- `30 - 90 days of data`: Prophet is skipped. ARIMA (5,1,0) is trained on short-term data to capture linear/autoregressive trends.
