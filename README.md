# btc-cent-forecast-01

Bitcoin cent-level 4-hour price forecaster competition entry.

## Approach
Uses a robust **Theil-Sen median slope estimator** sampled hourly over the 72-hour price window, scaled with conservative shrinkage and a strict move cap (±1.5%) relative to the checkpoint close. Beats persistence robustly across practice cases.
