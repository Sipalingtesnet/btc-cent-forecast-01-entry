#!/usr/bin/env python3
"""
btc-cent-forecast-01: Micro-Damped Persistence Bitcoin 4h Forecaster.

Forecasts Bitcoin's price 240 minutes ahead from the checkpoint close.
Approach:
1. Extract 4,320 minute close prices (72 hours). Validate finite positive numbers.
2. Apply an extremely conservative micro-drift adjustment (multiplier 0.01) from 180m trend, capped at ±0.05% to hug the persistence baseline closely while capturing structural micro-momentum.
3. Fully deterministic, standard library only, outputs exact required JSON shape.
"""

import os
import json
import math
from pathlib import Path

def forecast_price(prices: list[float]) -> float:
    valid = [float(p) for p in prices if p is not None and math.isfinite(float(p)) and float(p) > 0]
    if not valid:
        return 50000.0
    
    p0 = valid[-1]  # Checkpoint close (persistence baseline)
    
    if len(valid) < 60:
        return p0
    
    # Conservative micro-trend over last 180 minutes, heavily shrunk
    p_past = valid[-180] if len(valid) >= 180 else valid[0]
    if p_past > 0:
        log_return = math.log(p0 / p_past)
        damped_return = log_return * 0.01
    else:
        damped_return = 0.0
        
    # Strict narrow cap of ±0.05% to remain robust against high volatility
    max_move = 0.0005
    if damped_return > max_move:
        damped_return = max_move
    elif damped_return < -max_move:
        damped_return = -max_move
        
    predicted = p0 * math.exp(damped_return)
    
    if not math.isfinite(predicted) or predicted <= 0:
        predicted = p0
    if predicted >= 10000000.0:
        predicted = 9999999.0
        
    return round(predicted, 5)

def main():
    input_dir = Path(os.environ.get('MAKEFUN_INPUT_DIR', '/input'))
    output_dir = Path(os.environ.get('MAKEFUN_OUTPUT_DIR', '/output'))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for path in sorted(input_dir.glob('*.in')):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            case_id = data.get('case', path.stem)
            markets = data.get('markets', [])
            prices = markets[0].get('prices', []) if markets else []
            
            guess = forecast_price(prices)
            
            out_data = {
                "forecasts": [
                    {
                        "case": case_id,
                        "price": guess
                    }
                ]
            }
            
            out_path = output_dir / f"{case_id}.out"
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(out_data, f, ensure_ascii=False)
        except Exception as e:
            case_id = path.stem
            out_data = {
                "forecasts": [
                    {
                        "case": case_id,
                        "price": 70000.0
                    }
                ]
            }
            out_path = output_dir / f"{case_id}.out"
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(out_data, f, ensure_ascii=False)

if __name__ == '__main__':
    main()
