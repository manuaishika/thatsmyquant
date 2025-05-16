import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint
from typing import List, Tuple, Dict
import logging
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_cointegration(series1: pd.Series, series2: pd.Series) -> Tuple[float, float]:
    """
    Calculate cointegration between two price series.
    
    Args:
        series1 (pd.Series): First price series
        series2 (pd.Series): Second price series
    
    Returns:
        Tuple[float, float]: (cointegration test statistic, p-value)
    """
    # Remove any missing values
    mask = ~(np.isnan(series1) | np.isnan(series2))
    series1 = series1[mask]
    series2 = series2[mask]
    
    if len(series1) < 30:  # Minimum required length for meaningful test
        return np.nan, np.nan
    
    # Calculate cointegration
    score, pvalue, _ = coint(series1, series2)
    return score, pvalue

def find_cointegrated_pairs(prices: pd.DataFrame, 
                          significance: float = 0.05,
                          min_pairs: int = 10) -> List[Dict]:
    """
    Find cointegrated pairs from a DataFrame of price series.
    
    Args:
        prices (pd.DataFrame): DataFrame where columns are price series
        significance (float): Significance level for cointegration test
        min_pairs (int): Minimum number of pairs to return
    
    Returns:
        List[Dict]: List of dictionaries containing pair information
    """
    n = len(prices.columns)
    pairs = []
    
    # Create all possible pairs
    for i, j in combinations(range(n), 2):
        stock1 = prices.columns[i]
        stock2 = prices.columns[j]
        
        # Calculate cointegration
        score, pvalue = calculate_cointegration(prices[stock1], prices[stock2])
        
        if pvalue < significance:
            pairs.append({
                'stock1': stock1,
                'stock2': stock2,
                'score': score,
                'pvalue': pvalue
            })
    
    # Sort pairs by p-value
    pairs.sort(key=lambda x: x['pvalue'])
    
    # Return top pairs
    return pairs[:min_pairs]

def parallel_pairs_scan(prices: pd.DataFrame,
                       significance: float = 0.05,
                       min_pairs: int = 10,
                       n_workers: int = 4) -> List[Dict]:
    """
    Parallel implementation of pairs scanning.
    
    Args:
        prices (pd.DataFrame): DataFrame of price series
        significance (float): Significance level
        min_pairs (int): Minimum number of pairs to return
        n_workers (int): Number of parallel workers
    
    Returns:
        List[Dict]: List of cointegrated pairs
    """
    n = len(prices.columns)
    pairs = []
    
    def process_chunk(chunk):
        chunk_pairs = []
        for i, j in chunk:
            stock1 = prices.columns[i]
            stock2 = prices.columns[j]
            score, pvalue = calculate_cointegration(prices[stock1], prices[stock2])
            if pvalue < significance:
                chunk_pairs.append({
                    'stock1': stock1,
                    'stock2': stock2,
                    'score': score,
                    'pvalue': pvalue
                })
        return chunk_pairs
    
    # Create chunks of pairs for parallel processing
    all_pairs = list(combinations(range(n), 2))
    chunk_size = len(all_pairs) // n_workers
    chunks = [all_pairs[i:i + chunk_size] for i in range(0, len(all_pairs), chunk_size)]
    
    # Process chunks in parallel
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        results = list(executor.map(process_chunk, chunks))
    
    # Combine results
    for chunk_result in results:
        pairs.extend(chunk_result)
    
    # Sort and return top pairs
    pairs.sort(key=lambda x: x['pvalue'])
    return pairs[:min_pairs]

if __name__ == "__main__":
    # Example usage
    from data.fetch import fetch_stock_data, get_sp500_symbols
    
    # Get some sample data
    symbols = get_sp500_symbols()[:20]  # First 20 symbols as example
    data = fetch_stock_data(symbols)
    
    # Convert to price DataFrame
    prices = pd.DataFrame({symbol: df['Close'] for symbol, df in data.items()})
    
    # Find cointegrated pairs
    pairs = find_cointegrated_pairs(prices)
    
    # Print results
    for pair in pairs:
        print(f"Pair: {pair['stock1']} - {pair['stock2']}")
        print(f"P-value: {pair['pvalue']:.4f}")
        print(f"Score: {pair['score']:.4f}")
        print("---") 