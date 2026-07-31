# Feature Engineering

The Dynamic Pricing Engine leverages advanced feature engineering to supply the ML models (Prophet/ARIMA) with necessary predictive signals.

## Temporal Features
- **Seasonality Detection**: Automatically parses daily (morning vs evening), weekly (weekday vs weekend), and yearly cycles (holidays, Black Friday).
- **Cyclical Encoding**: Days of the week and months are transformed using sine/cosine encoding to preserve the circular nature of time.

## Auto-Regressive Features
- **Lag Features**: Past demand strictly affects future demand. The previous 1-day, 7-day, and 30-day demand averages are extracted as features.
- **Trend Detection**: Moving averages calculate whether the overall demand is growing or shrinking.

## External Signals
*(Fully integrated in PR #4)*
- Weather parameters (temperature, precipitation).
- External Events and Promotions.
