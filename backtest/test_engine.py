import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import pandas as pd
from engine import PairsBacktest

def generate_sample_data(n_days=100):
    """Generate sample price data for two correlated assets."""
    np.random.seed(42)
    
    # Generate base prices
    t = np.linspace(0, 10, n_days)
    base = 100 + 0.1 * t + np.random.normal(0, 1, n_days)
    
    # Generate correlated prices
    spread = np.random.normal(0, 0.5, n_days)
    asset1 = base + spread
    asset2 = base - spread
    
    # Create DataFrame
    prices = pd.DataFrame({
        'asset1': asset1,
        'asset2': asset2
    }, index=pd.date_range(start='2024-01-01', periods=n_days))
    
    return prices

def generate_signals(prices, threshold=2.0):
    """Generate trading signals based on price spread."""
    spread = prices['asset1'] - prices['asset2']
    zscore = (spread - spread.mean()) / spread.std()
    
    signals = pd.DataFrame(index=prices.index)
    signals['signal'] = 0
    signals.loc[zscore > threshold, 'signal'] = -1  # Short asset1, long asset2
    signals.loc[zscore < -threshold, 'signal'] = 1   # Long asset1, short asset2
    
    return signals

def main():
    # Generate sample data
    prices = generate_sample_data()
    signals = generate_signals(prices)
    
    # Initialize and run backtest
    backtest = PairsBacktest(
        prices1=prices['asset1'].values,
        prices2=prices['asset2'].values,
        signals=signals['signal'].values,
        initial_capital=100000,
        slippage=0.001,
        commission=0.001,
        max_leverage=2.0
    )
    
    trades, pnl = backtest.run()
    
    # Evaluate performance
    from evaluator.performance import evaluate_performance
    evaluate_performance(trades, pnl)
    
    # Print results
    print("\nBacktest Results:")
    print(trades)
    print("PnL:", pnl)

if __name__ == "__main__":
    main() 