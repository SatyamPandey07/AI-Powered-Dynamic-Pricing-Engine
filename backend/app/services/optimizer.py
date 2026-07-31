"""
Price Optimization Engine
=========================
Multi-objective optimizer that combines:
  - Demand forecast (Prophet/ARIMA ensemble from PR #3)
  - Price elasticity (regression from this PR)
  - Competitor prices (scraped in PR #4)
  - Inventory position
  - Business rules (configurable guardrails)
"""
import numpy as np
from scipy.optimize import minimize_scalar
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Demand model: Q(P) = Q_ref * (P / P_ref) ^ (-E)
# where E is price elasticity (positive number)
# ---------------------------------------------------------------------------

def demand_at_price(price: float, ref_price: float, ref_quantity: float, elasticity: float) -> float:
    """Estimate demand at a given price using constant-elasticity model."""
    if ref_price <= 0 or price <= 0:
        return ref_quantity
    return ref_quantity * (price / ref_price) ** (-abs(elasticity))


def _revenue(price, ref_price, ref_quantity, elasticity, cost=0.0):
    q = demand_at_price(price, ref_price, ref_quantity, elasticity)
    return -(price * q)  # negative because scipy minimizes


def _margin(price, ref_price, ref_quantity, elasticity, cost=0.0):
    q = demand_at_price(price, ref_price, ref_quantity, elasticity)
    return -((price - cost) * q)


def _clearance(price, ref_price, ref_quantity, elasticity, cost=0.0):
    """Clearance objective: maximize units moved (minimize negative quantity)."""
    q = demand_at_price(price, ref_price, ref_quantity, elasticity)
    return -q


OBJECTIVES = {
    "revenue": _revenue,
    "margin": _margin,
    "clearance": _clearance,
}

# ---------------------------------------------------------------------------
# Business rule enforcement
# ---------------------------------------------------------------------------

def apply_rules(price: float, constraints: dict, rules: list) -> tuple[float, list[str]]:
    """
    Apply hard and soft business rules to a candidate price.

    constraints = {
        "min_price": float,
        "max_price": float,
        "current_price": float,
        "max_change_pct": float,  # e.g. 0.10 = 10%
    }
    Returns (enforced_price, list_of_warnings)
    """
    warnings = []
    min_p = constraints.get("min_price", 0)
    max_p = constraints.get("max_price", 1e9)
    current = constraints.get("current_price", price)
    max_chg = constraints.get("max_change_pct", 0.10)

    # Hard: don't go below cost floor
    if price < min_p:
        warnings.append(f"Price ${price:.2f} below minimum ${min_p:.2f}. Clamped to minimum.")
        price = min_p

    # Hard: don't exceed MSRP
    if price > max_p:
        warnings.append(f"Price ${price:.2f} above maximum ${max_p:.2f}. Clamped to maximum.")
        price = max_p

    # Soft: ≤ max_change_pct in 24 hours
    if current > 0:
        change_pct = abs(price - current) / current
        if change_pct > max_chg:
            warnings.append(
                f"Recommended change of {change_pct*100:.1f}% exceeds {max_chg*100:.0f}% "
                f"24-hour limit. Consider staged rollout."
            )

    # Rule #5: Round to "nice" price (e.g. $49 → $49.99)
    price = _round_to_nice_price(price)

    return price, warnings


def _round_to_nice_price(price: float) -> float:
    """Round to nearest .99 or .49 psychological price point."""
    base = int(price)
    decimal = price - base
    if decimal < 0.25:
        return base - 0.01 if base > 0 else 0.99
    elif decimal < 0.74:
        return base + 0.49
    else:
        return base + 0.99


# ---------------------------------------------------------------------------
# Markdown schedule
# ---------------------------------------------------------------------------

def markdown_schedule(current_price: float, days_in_stock: int) -> list[dict]:
    """
    Generate a proactive markdown schedule for aging inventory.

    Week 1 (0–7d):   -10%
    Week 2 (7–14d):  -20%
    Week 3 (14–21d): -35%
    Week 4 (21+d):   -50%
    """
    brackets = [
        {"min_days": 0,  "max_days": 7,  "discount_pct": 0.10},
        {"min_days": 7,  "max_days": 14, "discount_pct": 0.20},
        {"min_days": 14, "max_days": 21, "discount_pct": 0.35},
        {"min_days": 21, "max_days": 9999, "discount_pct": 0.50},
    ]
    schedule = []
    for b in brackets:
        discounted = current_price * (1 - b["discount_pct"])
        schedule.append({
            "week_range": f"{b['min_days']}–{b['max_days']} days",
            "discount_pct": b["discount_pct"] * 100,
            "suggested_price": round(discounted, 2),
        })
    return schedule


# ---------------------------------------------------------------------------
# Inventory-based pricing signal
# ---------------------------------------------------------------------------

def inventory_signal(inventory_units: float, daily_demand: float) -> dict:
    """Returns a pricing signal based on days-to-stockout."""
    if daily_demand <= 0:
        days_to_stockout = 999
    else:
        days_to_stockout = inventory_units / daily_demand

    if days_to_stockout < 7:
        signal = "aggressive_discount"
        adjustment = -0.10
    elif days_to_stockout < 30:
        signal = "slight_discount"
        adjustment = -0.05
    elif days_to_stockout <= 90:
        signal = "maintain_margin"
        adjustment = 0.0
    else:
        signal = "excess_inventory"
        adjustment = -0.15

    return {"days_to_stockout": round(days_to_stockout, 1), "signal": signal, "price_adjustment": adjustment}


# ---------------------------------------------------------------------------
# Main optimization routine
# ---------------------------------------------------------------------------

def optimize_price(
    current_price: float,
    ref_quantity: float,
    elasticity: float,
    objective: str,
    constraints: dict,
    cost: float = 0.0,
    competitor_avg_price: Optional[float] = None,
    rules: list = None,
) -> dict:
    """
    Core price optimization function.

    Returns a dict with recommended_price, expected impact, reasoning and confidence.
    """
    obj_fn = OBJECTIVES.get(objective, _revenue)
    rules = rules or []

    min_p = constraints.get("min_price", cost * 1.2 if cost > 0 else current_price * 0.5)
    max_p = constraints.get("max_price", current_price * 2.0)

    result = minimize_scalar(
        obj_fn,
        bounds=(min_p, max_p),
        method="bounded",
        args=(current_price, ref_quantity, elasticity, cost),
    )

    optimal_price = result.x
    optimal_price, warnings = apply_rules(optimal_price, constraints, rules)

    # Expected impact
    current_q = ref_quantity
    new_q = demand_at_price(optimal_price, current_price, ref_quantity, elasticity)
    revenue_delta = (optimal_price * new_q) - (current_price * current_q)
    margin_delta = ((optimal_price - cost) * new_q) - ((current_price - cost) * current_q)

    # Confidence based on elasticity quality and competitor data freshness
    confidence = 0.7  # baseline
    if elasticity != 1.0:
        confidence += 0.1  # has a measured elasticity, not a default
    if competitor_avg_price is not None:
        confidence += 0.1
        if optimal_price > competitor_avg_price:
            warnings.append(
                f"Recommended price ${optimal_price:.2f} is above avg competitor ${competitor_avg_price:.2f}"
            )

    confidence = min(confidence, 0.95)

    # Build reasoning text
    reasoning_parts = [
        f"Objective: {objective}.",
        f"Elasticity: {elasticity:.2f}x (a 1% price change moves demand by {elasticity:.2f}%).",
        f"Demand at current price: ~{current_q:.0f} units/day.",
        f"Demand at recommended price: ~{new_q:.0f} units/day.",
    ]
    if competitor_avg_price:
        reasoning_parts.append(f"Avg competitor price: ${competitor_avg_price:.2f}.")
    if warnings:
        reasoning_parts.extend(warnings)

    return {
        "recommended_price": round(optimal_price, 2),
        "current_price": current_price,
        "expected_quantity_change": round(new_q - current_q, 1),
        "expected_revenue_delta": round(revenue_delta, 2),
        "expected_margin_delta": round(margin_delta, 2),
        "confidence": round(confidence, 2),
        "reasoning": " ".join(reasoning_parts),
        "warnings": warnings,
        "objective": objective,
    }
