# A/B Testing Guide

The Dynamic Pricing Engine includes a statistical A/B testing framework to scientifically measure the impact of price changes.

## Experiment Design
- **Control Group**: Sees the baseline price.
- **Treatment Group**: Sees the AI-recommended price.
- **Assignment**: Users are deterministically assigned via a hash of their `user_id` and `experiment_id`. This ensures a user doesn't see fluctuating prices on refresh.

## Statistical Rigor
- **Significance (p-value < 0.05)**: We use a Chi-squared contingency test to evaluate conversion rates. A p-value under 0.05 indicates the result is statistically significant (95% confidence).
- **Power Analysis**: Before running a test, use `/api/experiments/power-analysis` to determine how long the test should run based on the expected effect size.

## Interpreting Results
- If an experiment reaches statistical significance, the winner should be concluded (`POST /api/experiments/{id}/conclude`). 
- **Warning**: Do not peek early and conclude tests just because the p-value dips below 0.05; wait for the required sample size to avoid false positives (unless using Bayesian approaches).
