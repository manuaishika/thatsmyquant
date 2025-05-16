import pandas as pd
import numpy as np

def evaluate_performance(trades, pnl):
    """Evaluate the performance of the pairs trading strategy."""
    # Calculate total return
    total_return = pnl.sum() / trades['size'].iloc[0] * 100

    # Calculate Sharpe ratio
    sharpe_ratio = pnl.mean() / pnl.std() * np.sqrt(252)  # Annualized

    # Calculate maximum drawdown
    cumulative_pnl = pnl.cumsum()
    max_drawdown = (cumulative_pnl - cumulative_pnl.cummax()).min() / cumulative_pnl.cummax().max() * 100

    # Calculate win rate
    win_rate = (pnl > 0).mean() * 100

    # Calculate average trade return
    avg_trade_return = pnl.mean() / trades['size'].iloc[0] * 100

    # Print results
    print("\nPerformance Metrics:")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"Maximum Drawdown: {max_drawdown:.2f}%")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Average Trade Return: {avg_trade_return:.2f}%")

if __name__ == "__main__":
    # Example usage
    trades = pd.DataFrame({
        'type': ['entry', 'exit', 'entry', 'exit'],
        'i': [10, 11, 13, 14],
        'signal': [1, 1, -1, -1],
        'price1': [98.77, 99.53, 99.54, 98.22],
        'price2': [100.69, 99.55, 97.08, 98.41],
        'size': [1003.63, 1003.63, -3057.20, -3057.20],
        'pnl': [np.nan, 657.57, np.nan, 3152.04]
    })
    pnl = pd.Series([657.57, 3152.04])
    evaluate_performance(trades, pnl) 