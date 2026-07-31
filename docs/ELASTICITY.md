# Price Elasticity Measurement

Price elasticity of demand measures how sensitive consumer purchasing behavior is to price changes.

```
E = (% Change in Quantity Demanded) / (% Change in Price)
```

## Elasticity Categories

| Range | Category | Interpretation |
|-------|----------|----------------|
| `|E| > 1` | **Elastic** | Consumers are price-sensitive. Small price drop = big sales increase. |
| `|E| = 1` | **Unit Elastic** | Price change % = Quantity change % |
| `|E| < 1` | **Inelastic** | Price changes barely affect quantity (e.g., medicines, necessities) |

## Regression Method (Default)

We use a **log-log OLS regression** which directly estimates the constant-elasticity coefficient:

```
ln(Q) = α + E × ln(P) + ε
```

The coefficient `E` is the price elasticity. It requires at minimum **30 historical data points** to compute.

## A/B Testing Method

For products without sufficient history, a controlled A/B test can be configured:

1. **Setup**: Define `control_price` (current) and `treatment_price` (test).
2. **Traffic split**: Randomly assign 50% of traffic to each arm.
3. **Evaluation**: After the test period, a **two-proportion z-test** determines if conversion rate differences are statistically significant (`p < 0.05`).
4. **Winner**: Declared if `p_value < 0.05`, otherwise `no_significant_difference`.

## Confidence Intervals

The regression method produces 95% confidence intervals via the t-distribution. Wider intervals indicate fewer data points or noisier relationships.
