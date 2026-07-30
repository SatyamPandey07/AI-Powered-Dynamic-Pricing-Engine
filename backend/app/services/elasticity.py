import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from scipy import stats
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def measure_elasticity_regression(
    prices: list[float], quantities: list[float]
) -> dict:
    """
    Measures price elasticity using log-log OLS regression.

    The log-log model: ln(Q) = a + E * ln(P) + e
    The slope coefficient E is the price elasticity.

    Args:
        prices: Historical prices for a SKU.
        quantities: Corresponding units sold for each price point.

    Returns:
        dict with elasticity_value, confidence_lower, confidence_upper, r_squared.
    """
    if len(prices) < 30:
        raise ValueError("At least 30 data points required for elasticity measurement.")

    log_prices = np.log(np.array(prices)).reshape(-1, 1)
    log_quantities = np.log(np.array(quantities) + 1)  # +1 to avoid log(0)

    model = LinearRegression()
    model.fit(log_prices, log_quantities)
    elasticity = model.coef_[0]
    r_squared = model.score(log_prices, log_quantities)

    # Confidence interval via scipy OLS
    n = len(prices)
    se = np.std(log_quantities - model.predict(log_prices)) / np.sqrt(n)
    t_crit = stats.t.ppf(0.975, df=n - 2)
    ci_half = t_crit * se

    return {
        "elasticity_value": float(elasticity),
        "confidence_lower": float(elasticity - ci_half),
        "confidence_upper": float(elasticity + ci_half),
        "data_points": n,
        "r_squared": float(r_squared),
        "model_type": "regression",
    }


def evaluate_ab_test(
    control_conversions: int,
    control_impressions: int,
    treatment_conversions: int,
    treatment_impressions: int,
) -> dict:
    """
    Evaluates an A/B pricing test using a two-proportion z-test.

    Returns p_value, winner, and lift.
    """
    p_control = control_conversions / max(control_impressions, 1)
    p_treatment = treatment_conversions / max(treatment_impressions, 1)

    # Pooled proportion
    p_pool = (control_conversions + treatment_conversions) / (
        control_impressions + treatment_impressions
    )
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / control_impressions + 1 / treatment_impressions))

    if se == 0:
        return {"p_value": 1.0, "winner": "no_significant_difference", "lift": 0.0}

    z_score = (p_treatment - p_control) / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))  # Two-tailed

    lift = (p_treatment - p_control) / max(p_control, 1e-8)
    if p_value < 0.05:
        winner = "treatment" if p_treatment > p_control else "control"
    else:
        winner = "no_significant_difference"

    return {
        "p_value": float(p_value),
        "winner": winner,
        "lift": float(lift),
        "control_rate": float(p_control),
        "treatment_rate": float(p_treatment),
    }
