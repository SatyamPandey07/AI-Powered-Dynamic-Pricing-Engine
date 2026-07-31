# Price Optimization Engine

The optimization engine is the decision-making core of the Dynamic Pricing system. It synthesizes demand forecasts, price elasticity, competitor benchmarks, and business rules to recommend revenue- or margin-maximizing prices.

## Algorithm

We use a **bounded scalar optimization** (`scipy.optimize.minimize_scalar`) on a constant-elasticity demand model:

```
Q(P) = Q_ref * (P / P_ref)^(-E)
```

Where:
- `Q_ref` = reference demand at `P_ref`
- `E` = price elasticity (measured via log-log regression)
- `P` = candidate price

**Objective functions**:
| Objective   | Formula |
|-------------|---------|
| `revenue`   | Maximize `P × Q(P)` |
| `margin`    | Maximize `(P - cost) × Q(P)` |
| `clearance` | Maximize `Q(P)` (units moved) |

## Business Constraints

| Rule | Type | Description |
|------|------|-------------|
| Min price | Hard | Must be ≥ cost × (1 + min_margin) |
| Max price | Hard | Must not exceed MSRP |
| Max daily change | Soft (warns) | ≤10% price change per 24h |
| Nice price rounding | Auto | Prices rounded to `.99`/`.49` |

## Inventory-Based Signals

| Days-to-stockout | Signal | Adjustment |
|------------------|--------|------------|
| < 7 days | aggressive_discount | −10% |
| 7–30 days | slight_discount | −5% |
| 30–90 days | maintain_margin | 0% |
| > 90 days | excess_inventory | −15% |

## Confidence Score

| Factor | Contribution |
|--------|-------------|
| Baseline | +0.70 |
| Has measured elasticity | +0.10 |
| Competitor price data available | +0.10 |
| Max | 0.95 |

## Example: Revenue Objective

```python
result = optimize_price(
    current_price=50.0,
    ref_quantity=100,
    elasticity=1.5,
    objective="revenue",
    constraints={"min_price": 30, "max_price": 75, "current_price": 50},
)
# result["recommended_price"] → $42.99
# result["reasoning"] → "Objective: revenue. Elasticity: 1.50x ..."
```
