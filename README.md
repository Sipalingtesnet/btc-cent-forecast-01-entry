# btc-cent-forecast-01 entry

Forecasts Bitcoin's USDC price 4 hours (240 minutes) ahead from each checkpoint.
Uses a robust damped momentum and median-anchor model with strict bounding to outperform persistence while maintaining high stability.
- Fully deterministic, standard library only, zero network usage.
- Run locally: `MAKEFUN_INPUT_DIR=... MAKEFUN_OUTPUT_DIR=... python3 main.py`
