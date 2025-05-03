"""
Configuration settings for the pairs trading project.
"""

# Default parameters
DEFAULT_PARAMS = {
    # Data parameters
    "start_date": "2020-01-01",
    "end_date": "2023-12-31",
    
    # Default pairs
    "default_pairs": [
        ("KO", "PEP"),  # Coca-Cola and PepsiCo
        ("XOM", "CVX"),  # Exxon and Chevron
        ("JPM", "BAC"),  # JPMorgan and Bank of America
        ("MSFT", "AAPL")  # Microsoft and Apple
    ],
    
    # Strategy parameters
    "lookback_window": 30,  # Days for rolling statistics
    "entry_threshold": 2.0,  # Z-score for entry
    "exit_threshold": 0.5,   # Z-score for exit
    
    # Backtest parameters
    "initial_capital": 100000,
    "position_size": 10000,  # Per pair
    "commission_rate": 0.001,  # 0.1% per trade
    "slippage": 0.0005,      # 0.05% slippage
    
    # Technical parameters
    "random_seed": 42,
    "log_level": "INFO"
}

# paths
DATA_DIR = "data/raw"
RESULTS_DIR = "results"
LOG_DIR = "logs"


PLOT_STYLE = "seaborn"
PLOT_FIGSIZE = (12, 6)