import numpy as np
from typing import Tuple, List
import pandas as pd

class KalmanFilter:
    def __init__(self, delta: float = 1e-4, ve: float = 1e-4):
        self.delta = delta  # State transition variance
        self.ve = ve       # Measurement noise variance
        self.R = None      # State covariance
        self.x = None      # State estimate
        self.P = None      # Error covariance

    def initialize(self, y1: float, y2: float) -> None:
        """Initialize Kalman Filter with first observations"""
        self.R = np.array([[1, 0], [0, 1]])  # Initial state covariance
        self.x = np.array([y1, y2])          # Initial state estimate
        self.P = np.eye(2)                   # Initial error covariance

    def update(self, y1: float, y2: float) -> Tuple[float, float]:
        """Update Kalman Filter with new observations"""
        # Prediction step
        F = np.array([[1, 0], [0, 1]])  # State transition matrix
        x_pred = F @ self.x
        P_pred = F @ self.P @ F.T + self.R * self.delta

        # Update step
        H = np.array([[1, -1]])  # Measurement matrix
        y = np.array([y1 - y2])  # Measurement
        S = H @ P_pred @ H.T + self.ve
        K = P_pred @ H.T @ np.linalg.inv(S)  # Kalman gain

        self.x = x_pred + K @ (y - H @ x_pred)
        self.P = (np.eye(2) - K @ H) @ P_pred

        return self.x[0], self.x[1]

def estimate_hedge_ratio(prices1: pd.Series, prices2: pd.Series) -> Tuple[List[float], List[float]]:
    """Estimate dynamic hedge ratio using Kalman Filter"""
    kf = KalmanFilter()
    hedge_ratios = []
    spreads = []
    
    # Initialize with first observations
    kf.initialize(prices1.iloc[0], prices2.iloc[0])
    
    # Process each price pair
    for p1, p2 in zip(prices1, prices2):
        beta1, beta2 = kf.update(p1, p2)
        hedge_ratios.append(beta1 / beta2)
        spreads.append(p1 - (beta1 / beta2) * p2)
    
    return hedge_ratios, spreads

def calculate_zscore(spread: List[float], window: int = 20) -> List[float]:
    """Calculate rolling z-score of the spread"""
    spread_series = pd.Series(spread)
    mean = spread_series.rolling(window=window).mean()
    std = spread_series.rolling(window=window).std()
    return ((spread_series - mean) / std).tolist() 