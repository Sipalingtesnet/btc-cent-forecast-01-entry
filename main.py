#!/usr/bin/env python3
"""
btc-cent-forecast-01: Theil-Sen Robust Trend Bitcoin 4h Forecaster.

Forecasts Bitcoin's price 240 minutes ahead from the checkpoint close.
Approach:
1. Extract close prices from the 72-hour window. Validate finite positive numbers.
2. Compute Theil-Sen robust median slope from hourly sampled log prices.
3. Forecast = checkpoint_close * exp(shrink * slope * 240), capped at ±1.5%.
4. Fully deterministic, standard library only, outputs exact required JSON shape.
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
    
    # Theil-Sen robust median slope sampled hourly
    step = 60
    sampled = []
    for idx in range(0, len(valid), step):
        sampled.append((idx, math.log(valid[idx])))
        
    if len(sampled) < 3:
        return p0
        
    slopes = []
    for i in range(len(sampled)):
        for j in range(i + 1, len(sampled)):
            dt = sampled[j][0] - sampled[i][0]
            if dt > 0:
                slopes.append((sampled[j][1] - sampled[i][1]) / dt)
                
    if not slopes:
        return p0
        
    slopes.sort()
    mid_slope = slopes[len(slopes) // 2]
    
    # Robust parameters: shrink=0.75, max_cap=0.015 (1.5%)
    shrink = 0.75
    max_cap = 0.015
    
    move = shrink * mid_slope * 240.0
    move = max(-max_cap, min(max_cap, move))
    
    predicted = p0 * math.exp(move)
    
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
