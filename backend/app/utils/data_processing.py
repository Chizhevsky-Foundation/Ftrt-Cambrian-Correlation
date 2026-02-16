import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Union
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Utility class for processing and transforming data
    """
    
    @staticmethod
    def normalize_time_series(series: pd.Series, method: str = 'zscore') -> pd.Series:
        """
        Normalize a time series
        
        Args:
            series: Time series to normalize
            method: Normalization method ('zscore', 'minmax', 'robust')
            
        Returns:
            Normalized time series
        """
        if method == 'zscore':
            return (series - series.mean()) / series.std()
        elif method == 'minmax':
            return (series - series.min()) / (series.max() - series.min())
        elif method == 'robust':
            median = series.median()
            mad = np.median(np.abs(series - median))
            return (series - median) / mad
        else:
            raise ValueError(f"Unknown normalization method: {method}")
    
    @staticmethod
    def resample_time_series(series: pd.Series, freq: str, method: str = 'mean') -> pd.Series:
        """
        Resample a time series to a different frequency
        
        Args:
            series: Time series to resample
            freq: Target frequency ('D', 'W', 'M', 'Y')
            method: Aggregation method ('mean', 'sum', 'max', 'min')
            
        Returns:
            Resampled time series
        """
        if method == 'mean':
            return series.resample(freq).mean()
        elif method == 'sum':
            return series.resample(freq).sum()
        elif method == 'max':
            return series.resample(freq).max()
        elif method == 'min':
            return series.resample(freq).min()
        else:
            raise ValueError(f"Unknown aggregation method: {method}")
    
    @staticmethod
    def create_time_series(events: List[Dict], value_col: str = 'magnitude') -> pd.Series:
        """
        Create a time series from a list of events
        
        Args:
            events: List of event dictionaries
            value_col: Column to use as values
            
        Returns:
            Time series
        """
        # Convert to DataFrame
        df = pd.DataFrame(events)
        
        # Ensure timestamp is datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Set timestamp as index
        df.set_index('timestamp', inplace=True)
        
        # Create time series
        return df[value_col]
    
    @staticmethod
    def detect_outliers(series: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> pd.Series:
        """
        Detect outliers in a time series
        
        Args:
            series: Time series to analyze
            method: Outlier detection method ('iqr', 'zscore', 'isolation_forest')
            threshold: Threshold for outlier detection
            
        Returns:
            Boolean series indicating outliers
        """
        if method == 'iqr':
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            return (series < lower_bound) | (series > upper_bound)
        
        elif method == 'zscore':
            z_scores = np.abs((series - series.mean()) / series.std())
            return z_scores > threshold
        
        elif method == 'isolation_forest':
            try:
                from sklearn.ensemble import IsolationForest
                
                # Reshape data
                X = series.values.reshape(-1, 1)
                
                # Fit model
                model = IsolationForest(contamination=0.1)
                outliers = model.fit_predict(X)
                
                # Return boolean series
                return pd.Series(outliers == -1, index=series.index)
            
            except ImportError:
                logger.warning("sklearn not installed, falling back to IQR method")
                return DataProcessor.detect_outliers(series, 'iqr', threshold)
        
        else:
            raise ValueError(f"Unknown outlier detection method: {method}")
    
    @staticmethod
    def fill_missing_values(series: pd.Series, method: str = 'interpolate') -> pd.Series:
        """
        Fill missing values in a time series
        
        Args:
            series: Time series with missing values
            method: Method to fill missing values ('interpolate', 'forward_fill', 'backward_fill', 'mean')
            
        Returns:
            Time series with filled values
        """
        if method == 'interpolate':
            return series.interpolate()
        elif method == 'forward_fill':
            return series.fillna(method='ffill')
        elif method == 'backward_fill':
            return series.fillna(method='bfill')
        elif method == 'mean':
            return series.fillna(series.mean())
        else:
            raise ValueError(f"Unknown fill method: {method}")
    
    @staticmethod
    def smooth_time_series(series: pd.Series, window: int = 5, method: str = 'rolling') -> pd.Series:
        """
        Smooth a time series
        
        Args:
            series: Time series to smooth
            window: Window size for smoothing
            method: Smoothing method ('rolling', 'exponential')
            
        Returns:
            Smoothed time series
        """
        if method == 'rolling':
            return series.rolling(window=window, center=True).mean()
        elif method == 'exponential':
            return series.ewm(span=window).mean()
        else:
            raise ValueError(f"Unknown smoothing method: {method}")
    
    @staticmethod
    def detrend_time_series(series: pd.Series, method: str = 'linear') -> pd.Series:
        """
        Detrend a time series
        
        Args:
            series: Time series to detrend
            method: Detrending method ('linear', 'difference')
            
        Returns:
            Detrended time series
        """
        if method == 'linear':
            # Fit linear trend
            x = np.arange(len(series))
            coeffs = np.polyfit(x, series, 1)
            trend = np.polyval(coeffs, x)
            
            # Remove trend
            return series - pd.Series(trend, index=series.index)
        
        elif method == 'difference':
            # First difference
            return series.diff()
        
        else:
            raise ValueError(f"Unknown detrending method: {method}")
    
    @staticmethod
    def align_time_series(series1: pd.Series, series2: pd.Series) -> Tuple[pd.Series, pd.Series]:
        """
        Align two time series to the same time index
        
        Args:
            series1: First time series
            series2: Second time series
            
        Returns:
            Tuple of aligned time series
        """
        # Find common index
        common_index = series1.index.intersection(series2.index)
        
        # Align both series
        aligned_series1 = series1.loc[common_index]
        aligned_series2 = series2.loc[common_index]
        
        return aligned_series1, aligned_series2
    
    @staticmethod
    def create_event_matrix(events: List[Dict], event_types: List[str], 
                          start_date: datetime, end_date: datetime, 
                          freq: str = 'D') -> pd.DataFrame:
        """
        Create a binary event matrix from a list of events
        
        Args:
            events: List of event dictionaries
            event_types: List of event types to include
            start_date: Start date for the matrix
            end_date: End date for the matrix
            freq: Frequency of the time index
            
        Returns:
            Binary event matrix
        """
        # Create time index
        time_index = pd.date_range(start=start_date, end=end_date, freq=freq)
        
        # Initialize DataFrame with zeros
        event_matrix = pd.DataFrame(0, index=time_index, columns=event_types)
        
        # Convert events to DataFrame
        events_df = pd.DataFrame(events)
        events_df['timestamp'] = pd.to_datetime(events_df['timestamp'])
        
        # Fill the matrix
        for _, event in events_df.iterrows():
            event_type = event['event_type']
            timestamp = event['timestamp']
            
            if event_type in event_types and timestamp in event_matrix.index:
                event_matrix.loc[timestamp, event_type] = 1
        
        return event_matrix
    
    @staticmethod
    def calculate_event_rates(events: List[Dict], window: str = '30D') -> pd.Series:
        """
        Calculate event rates over time
        
        Args:
            events: List of event dictionaries
            window: Rolling window for rate calculation
            
        Returns:
            Time series of event rates
        """
        # Convert events to DataFrame
        events_df = pd.DataFrame(events)
        events_df['timestamp'] = pd.to_datetime(events_df['timestamp'])
        
        # Count events per day
        daily_counts = events_df.groupby(events_df['timestamp'].dt.date).size()
        daily_counts.index = pd.to_datetime(daily_counts.index)
        
        # Calculate rolling rate
        event_rates = daily_counts.rolling(window=window).sum() / pd.Timedelta(window).days
        
        return event_rates
