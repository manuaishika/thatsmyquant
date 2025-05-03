"""
Backtesting engine for pairs trading strategies.
"""
import logging
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class Position:
    """Class to track an open trading position."""
    ticker1: str
    ticker2: str
    direction: int  # 1 for long spread, -1 for short spread
    qty1: float
    qty2: float
    entry_date: pd.Timestamp
    entry_price1: float
    entry_price2: float
    entry_spread: float
    hedge_ratio: float = 1.0
    pnl: float = 0.0
    unrealized_pnl: float = 0.0
    exit_date: Optional[pd.Timestamp] = None
    exit_price1: Optional[float] = None
    exit_price2: Optional[float] = None
    exit_spread: Optional[float] = None
    exit_reason: Optional[str] = None


class BacktestEngine:
    """
    Engine for backtesting pairs trading strategies.
    """
    
    def __init__(
        self,
        ticker1: str,
        ticker2: str,
        initial_capital: float = 100000.0,