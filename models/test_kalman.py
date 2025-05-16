import pandas as pd
import numpy as np
from kalman_filter import KalmanFilter, estimate_hedge_ratio, calculate_zscore

def test_kalman_filter():
    # Generate synthetic cointegrated data
    np.random.seed(42)
    n = 1000
    t = np.linspace(0, 1, n)
    
    # Generate two cointegrated series
    y1 = np.sin(2 * np.pi * t) + np.random.normal(0, 0.1, n)
    y2 = 2 * np.sin(2 * np.pi * t) + np.random.normal(0, 0.1, n)
    
    # Convert to pandas Series
    prices1 = pd.Series(y1)
    prices2 = pd.Series(y2)
    
    # Estimate hedge ratio and spread
    hedge_ratios, spreads = estimate_hedge_ratio(prices1, prices2)
    
    # Calculate z-scores
    zscores = calculate_zscore(spreads)
    
    # Basic validation
    assert len(hedge_ratios) == n
    assert len(spreads) == n
    assert len(zscores) == n
    assert not np.any(np.isnan(hedge_ratios))
    assert not np.any(np.isnan(spreads))
    
    print("Kalman Filter test passed!")
    print(f"Average hedge ratio: {np.mean(hedge_ratios):.4f}")
    print(f"Spread std dev: {np.std(spreads):.4f}")

if __name__ == "__main__":
    test_kalman_filter() 