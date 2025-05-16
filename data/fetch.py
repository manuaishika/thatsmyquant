import yfinance as yf
import pandas as pd
from typing import List, Dict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_sp500_symbols() -> List[str]:
    """
    Fetch the list of S&P 500 symbols.
    Returns:
        List[str]: List of ticker symbols
    """
    try:
        # Using Wikipedia to get S&P 500 symbols
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url)
        df = tables[0]
        return df['Symbol'].tolist()
    except Exception as e:
        logger.error(f"Error fetching S&P 500 symbols: {str(e)}")
        return []

def fetch_stock_data(symbols: List[str], 
                    start_date: str = '2020-01-01',
                    end_date: str = None) -> Dict[str, pd.DataFrame]:
    """
    Fetch historical stock data for a list of symbols.
    
    Args:
        symbols (List[str]): List of stock symbols
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format (defaults to today)
    
    Returns:
        Dict[str, pd.DataFrame]: Dictionary of DataFrames with OHLCV data
    """
    data = {}
    for symbol in symbols:
        try:
            logger.info(f"Fetching data for {symbol}")
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            if not df.empty:
                data[symbol] = df
            else:
                logger.warning(f"No data found for {symbol}")
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
    
    return data

def save_data(data: Dict[str, pd.DataFrame], directory: str = 'data/raw'):
    """
    Save the fetched data to CSV files.
    
    Args:
        data (Dict[str, pd.DataFrame]): Dictionary of DataFrames to save
        directory (str): Directory to save the files
    """
    import os
    os.makedirs(directory, exist_ok=True)
    
    for symbol, df in data.items():
        filepath = os.path.join(directory, f"{symbol}.csv")
        df.to_csv(filepath)
        logger.info(f"Saved data for {symbol} to {filepath}")

if __name__ == "__main__":
    # Example usage
    symbols = get_sp500_symbols()
    if symbols:
        data = fetch_stock_data(symbols[:5])  # Fetch first 5 symbols as example
        save_data(data) 