"""
Tests for the Price Optimization Engine (PR #5)
================================================
"""
import pytest
import numpy as np
from app.services.elasticity import measure_elasticity_regression, evaluate_ab_test
from app.services.optimizer import (
    demand_at_price,
    optimize_price,
    markdown_schedule,
    inventory_signal,
    apply_rules,
    _round_to_nice_price,
)
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Unit tests: Elasticity
# ---------------------------------------------------------------------------

def test_elasticity_regression_output_keys():
    """Regression elasticity should return expected keys."""
    prices = [50 + i * 0.5 for i in range(40)]
    quantities = [1000 * (50 / p) ** 1.5 for p in prices]
    result = measure_elasticity_regression(prices, quantities)
    assert "elasticity_value" in result
    assert "r_squared" in result
    assert 0.0 <= result["r_squared"] <= 1.0


def test_elasticity_regression_insufficient_data():
    """Should raise ValueError if fewer than 30 data points."""
    with pytest.raises(ValueError, match="30 data points"):
        measure_elasticity_regression([50.0] * 10, [100.0] * 10)


def test_elasticity_regression_direction():
    """Elasticity should be negative for classic demand curve (price up → qty down)."""
    prices = [40, 45, 50, 55, 60] * 10
    quantities = [200, 170, 150, 130, 110] * 10
    result = measure_elasticity_regression(prices, quantities)
    # Elasticity from log-log regression on downsloping demand should be negative
    assert result["elasticity_value"] < 0


# ---------------------------------------------------------------------------
# Unit tests: A/B test evaluation
# ---------------------------------------------------------------------------

def test_ab_test_no_conversions():
    result = evaluate_ab_test(0, 1, 0, 1)
    assert result["winner"] == "no_significant_difference"


def test_ab_test_significant_winner():
    result = evaluate_ab_test(
        control_conversions=50, control_impressions=500,
        treatment_conversions=80, treatment_impressions=500,
    )
    assert result["p_value"] < 0.05
    assert result["winner"] in ("control", "treatment")


# ---------------------------------------------------------------------------
# Unit tests: Optimizer
# ---------------------------------------------------------------------------

def test_demand_at_price_elastic():
    """Elastic good: higher price → significantly fewer units."""
    q = demand_at_price(55, 50, 100, 2.0)
    assert q < 100.0  # price went up, demand down


def test_demand_at_price_inelastic():
    """Inelastic good: higher price has minimal effect."""
    q_elastic = demand_at_price(60, 50, 100, 2.0)
    q_inelastic = demand_at_price(60, 50, 100, 0.3)
    # Inelastic product retains more demand
    assert q_inelastic > q_elastic


def test_optimize_price_revenue_objective():
    """Revenue optimization should return a price within constraints."""
    constraints = {"min_price": 30.0, "max_price": 70.0, "current_price": 50.0, "max_change_pct": 0.30}
    result = optimize_price(50.0, 100.0, 1.5, "revenue", constraints)
    assert constraints["min_price"] <= result["recommended_price"] <= constraints["max_price"]
    assert "reasoning" in result
    assert result["confidence"] > 0


def test_optimize_price_clearance_objective_lower():
    """Clearance objective should push price lower than revenue objective."""
    constraints = {"min_price": 20.0, "max_price": 70.0, "current_price": 50.0, "max_change_pct": 0.50}
    rev = optimize_price(50.0, 100.0, 1.5, "revenue", constraints)
    clr = optimize_price(50.0, 100.0, 1.5, "clearance", constraints)
    assert clr["recommended_price"] <= rev["recommended_price"]


def test_apply_rules_clamps_below_min():
    price, warnings = apply_rules(15.0, {"min_price": 20.0, "max_price": 100.0, "current_price": 50.0}, [])
    assert price >= 20.0
    assert any("minimum" in w for w in warnings)


def test_apply_rules_clamps_above_max():
    price, warnings = apply_rules(120.0, {"min_price": 20.0, "max_price": 100.0, "current_price": 50.0}, [])
    assert price <= 100.0


def test_nice_price_rounding():
    assert _round_to_nice_price(49.0) == 48.99
    assert _round_to_nice_price(49.6) == 49.99


# ---------------------------------------------------------------------------
# Unit tests: Markdown & Inventory
# ---------------------------------------------------------------------------

def test_markdown_schedule_returns_4_brackets():
    schedule = markdown_schedule(100.0, 5)
    assert len(schedule) == 4


def test_markdown_schedule_discounts_increase():
    schedule = markdown_schedule(100.0, 5)
    discounts = [s["discount_pct"] for s in schedule]
    assert discounts == sorted(discounts)


def test_inventory_signal_low_stock():
    sig = inventory_signal(50, 10)
    assert sig["signal"] == "aggressive_discount"


def test_inventory_signal_excess():
    sig = inventory_signal(5000, 10)
    assert sig["signal"] == "excess_inventory"


# ---------------------------------------------------------------------------
# API tests: Authorization checks
# ---------------------------------------------------------------------------

def test_optimize_price_unauthorized():
    response = client.post("/api/optimize/price", json={
        "sku_id": "sku-test", "objective": "revenue", "current_price": 50.0
    })
    assert response.status_code == 401


def test_elasticity_unauthorized():
    response = client.get("/api/elasticity/sku-test")
    assert response.status_code == 401


def test_rules_unauthorized():
    response = client.get("/api/rules")
    assert response.status_code == 401
