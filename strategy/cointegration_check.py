"""
Cointegration analysis module for pairs trading.
"""
import logging
from typing import Tuple, Dict, List, Optional, Union

import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import coint, adfuller
from statsmodels.regression.linear_model import OLS

logger = logging.getLogger(__name__)

def check_cointegration(
    series1: pd.Series, 
    series2: pd.Series, 
    alpha: float = 0.05
) -> Tuple[bool, float, Dict]:
    """
    Test for cointegration between two time series.
    
    Args:
        series1: First price series
        series2: Second price series
        alpha: Significance level for the test
        
    Returns:
        Tuple containing:
        - Boolean indicating if series are cointegrated
        - p-value of the test
        - Dictionary with detailed test results
    """
    # Run the Engle-Granger cointegration test
    score, pvalue, critical_values = coint(series1, series2)
    
    # Check if the pair is cointegrated at the given significance level
    is_cointegrated = pvalue < alpha
    
    # Compile detailed results
    results = {
        "score": score,
        "pvalue": pvalue,
        "critical_values": critical_values,
        "is_cointegrated": is_cointegrated
    }
    
    logger.debug(f"Cointegration test: score={score:.4f}, pvalue={pvalue:.4f}, cointegrated={is_cointegrated}")
    
    return is_cointegrated, pvalue, results

def calculate_hedge_ratio(
    series1: pd.Series, 
    series2: pd.Series
) -> float:
    """
    Calculate the hedge ratio between two time series using OLS regression.
    
    Args:
        series1: Y series (dependent variable)
        series2: X series (independent variable)
        
    Returns:
        Hedge ratio (coefficient from regression)
    """
    # Add a constant to the independent variable
    model = OLS(series1, series2).fit()
    
    # Extract the hedge ratio (slope coefficient)
    hedge_ratio = model.params[0]
    
    logger.debug(f"Calculated hedge ratio: {hedge_ratio:.4f}")
    
    return hedge_ratio

def check_stationarity(
    series: pd.Series, 
    alpha: float = 0.05
) -> Tuple[bool, float, Dict]:
    """
    Test for stationarity using the Augmented Dickey-Fuller test.
    
    Args:
        series: Time series to test
        alpha: Significance level for the test
        
    Returns:
        Tuple containing:
        - Boolean indicating if series is stationary
        - p-value of the test
        - Dictionary with detailed test results
    """
    # Run the ADF test
    result = adfuller(series.dropna())
    
    # Extract results
    adf_stat, pvalue, _, _, critical_values, _ = result
    
    # Check if the series is stationary at the given significance level
    is_stationary = pvalue < alpha
    
    # Compile detailed results
    results = {
        "adf_stat": adf_stat,
        "pvalue": pvalue,
        "critical_values": critical_values,
        "is_stationary": is_stationary
    }
    
    logger.debug(f"Stationarity test: adf_stat={adf_stat:.4f}, pvalue={pvalue:.4f}, stationary={is_stationary}")
    
    return is_stationary, pvalue, results

def find_cointegrated_pairs(
    price_data: pd.DataFrame, 
    significance_level: float = 0.05
) -> List[Tuple[str, str, float, float]]:
    """
    Find all cointegrated pairs in a price DataFrame.
    
    Args:
        price_data: DataFrame with price data for multiple assets
        significance_level: Significance level for cointegration test
        
    Returns:
        List of tuples containing (ticker1, ticker2, p-value, hedge_ratio)
    """
    n = len(price_data.columns)
    cointegrated_pairs = []
    
    # Initialize progress counter
    total_pairs = n * (n - 1) // 2
    current_pair = 0
    
    logger.info(f"Testing {total_pairs} potential pairs for cointegration")
    
    # Loop through all possible pairs
    for i in range(n):
        for j in range(i+1, n):
            current_pair += 1
            ticker1 = price_data.columns[i]
            ticker2 = price_data.columns[j]
            
            series1 = price_data[ticker1]
            series2 = price_data[ticker2]
            
            # Check for cointegration
            try:
                is_cointegrated, pvalue, _ = check_cointegration(series1, series2, significance_level)
                
                if is_cointegrated:
                    # Calculate hedge ratio
                    hedge_ratio = calculate_hedge_ratio(series1, series2)
                    cointegrated_pairs.append((ticker1, ticker2, pvalue, hedge_ratio))
                    logger.info(f"Found cointegrated pair: {ticker1}-{ticker2}, p-value: {pvalue:.4f}, hedge ratio: {hedge_ratio:.4f}")
            except Exception as e:
                logger.warning(f"Error testing pair {ticker1}-{ticker2}: {str(e)}")
            
            # Log progress every 10%
            if current_pair % max(1, total_pairs // 10) == 0:
                logger.info(f"Progress: {current_pair}/{total_pairs} pairs tested ({current_pair/total_pairs*100:.1f}%)")
    
    # Sort by p-value (strongest cointegration first)
    cointegrated_pairs.sort(key=lambda x: x[2])
    
    logger.info(f"Found {len(cointegrated_pairs)} cointegrated pairs out of {total_pairs} tested")
    
    return cointegrated_pairs