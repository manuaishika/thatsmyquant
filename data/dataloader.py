"""
Data loading and preprocessing module for pairs trading.
"""
import os
import logging
from typing import Tuple, List, Optional, Dict, Union

import pandas as pd
import numpy as np
import yfinance as yf

logger = logging.getLogger(__name__)

class DataLoader:
    """
    Class for loading and preprocessing financial data for pairs trading.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the DataLoader.
        
        Args:
            cache_dir: Directory to cache downloaded data
        """
        self.cache_dir = cache_dir
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def fetch_stock_data(
        self, 
        tickers: List[str], 
        start_date: str, 
        end_date: str,
        interval: str = "1d",
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Download stock price data for multiple tickers.
        
        Args:
            tickers: List of stock tickers
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            interval: Data frequency ('1d', '1wk', etc.)
            use_cache: Whether to use cached data if available
            
        Returns:
            DataFrame with adjusted close prices for all tickers
        """
        if use_cache and self.cache_dir:
            cache_file = os.path.join(
                self.cache_dir, 
                f"{'_'.join(tickers)}_{start_date}_{end_date}_{interval}.csv"
            )
            if os.path.exists(cache_file):
                logger.info(f"Loading cached data from {cache_file}")
                return pd.read_csv(cache_file, index_col=0, parse_dates=True)
        
        logger.info(f"Downloading data for {tickers} from {start_date} to {end_date}")
        data = yf.download(tickers, start=start_date, end=end_date, interval=interval)
        
        # Extract adjusted close and handle single ticker case
        if isinstance(data.columns, pd.MultiIndex):
            data = data['Adj Close']
        else:
            data = pd.DataFrame(data['Adj Close'], columns=tickers)
        
        # Cache the data
        if use_cache and self.cache_dir:
            data.to_csv(cache_file)
            
        return data
    
    def prepare_pair_data(
        self, 
        data: pd.DataFrame, 
        ticker1: str, 
        ticker2: str
    ) -> pd.DataFrame:
        """
        Prepare data for a specific pair of stocks.
        
        Args:
            data: DataFrame with price data
            ticker1: First ticker symbol
            ticker2: Second ticker symbol
            
        Returns:
            DataFrame with pair-specific data
        """
        # Extract the relevant columns and drop any rows with missing values
        pair_data = data[[ticker1, ticker2]].copy().dropna()
        
        if pair_data.empty:
            raise ValueError(f"No valid data found for pair {ticker1}-{ticker2}")
            
        # Calculate returns
        pair_data[f'{ticker1}_returns'] = pair_data[ticker1].pct_change()
        pair_data[f'{ticker2}_returns'] = pair_data[ticker2].pct_change()
        
        # Calculate spread
        pair_data['spread'] = pair_data[ticker1] - pair_data[ticker2]
        
        # Calculate spread returns
        pair_data['spread_returns'] = pair_data['spread'].pct_change()
        
        # Drop the first row which will have NaN values due to returns calculation
        pair_data = pair_data.dropna()
        
        return pair_data
    
    def normalize_prices(
        self, 
        data: pd.DataFrame, 
        method: str = 'first'
    ) -> pd.DataFrame:
        """
        Normalize prices for better comparison.
        
        Args:
            data: DataFrame with price data
            method: Normalization method ('first', 'mean', 'zscore')
            
        Returns:
            DataFrame with normalized prices
        """
        result = data.copy()
        
        if method == 'first':
            # Normalize by the first value
            for col in data.columns:
                result[col] = data[col] / data[col].iloc[0]
        elif method == 'mean':
            # Normalize by the mean
            for col in data.columns:
                result[col] = data[col] / data[col].mean()
        elif method == 'zscore':
            # Normalize to z-score
            for col in data.columns:
                result[col] = (data[col] - data[col].mean()) / data[col].std()
        else:
            raise ValueError(f"Unknown normalization method: {method}")
            
        return result


# Utility functions
def get_multiple_pairs_data(
    pairs: List[Tuple[str, str]],
    start_date: str,
    end_date: str,
    cache_dir: Optional[str] = None
) -> Dict[str, pd.DataFrame]:
    """
    Get data for multiple pairs in one go.
    
    Args:
        pairs: List of ticker pairs
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        cache_dir: Directory to cache downloaded data
        
    Returns:
        Dictionary with pair string as key and DataFrame as value
    """
    # Flatten the pairs list to get all unique tickers
    all_tickers = list(set([ticker for pair in pairs for ticker in pair]))
    
    # Initialize DataLoader
    loader = DataLoader(cache_dir=cache_dir)
    
    # Fetch data for all tickers at once
    all_data = loader.fetch_stock_data(all_tickers, start_date, end_date)
    
    # Prepare data for each pair
    pair_data = {}
    for ticker1, ticker2 in pairs:
        pair_name = f"{ticker1}_{ticker2}"
        try:
            pair_data[pair_name] = loader.prepare_pair_data(all_data, ticker1, ticker2)
        except ValueError as e:
            logger.warning(f"Skipping pair {pair_name}: {str(e)}")
    
    return pair_data