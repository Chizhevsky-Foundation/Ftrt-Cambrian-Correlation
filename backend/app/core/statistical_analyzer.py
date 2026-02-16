import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import find_peaks
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Union
import logging

logger = logging.getLogger(__name__)

class StatisticalAnalyzer:
    """
    Performs statistical analyses for cosmic-evolutionary correlations
    """
    
    def __init__(self):
        self.random_seed = 42
        np.random.seed(self.random_seed)
    
    def cross_correlation(self, cosmic_series: pd.Series, evolutionary_series: pd.Series,
                         max_lag: int = 365) -> List[Dict]:
        """
        Calculate cross-correlation between two time series
        
        Args:
            cosmic_series: Time series of cosmic events
            evolutionary_series: Time series of evolutionary events
            max_lag: Maximum lag to consider in days
            
        Returns:
            List of dictionaries with correlation information for each lag
        """
        # Ensure both series have the same time index
        common_index = cosmic_series.index.intersection(evolutionary_series.index)
        cosmic_aligned = cosmic_series.loc[common_index]
        evolutionary_aligned = evolutionary_series.loc[common_index]
        
        # Calculate cross-correlation for different lags
        correlations = []
        
        for lag in range(0, max_lag + 1, 30):  # Every 30 days
            if lag >= len(cosmic_aligned):
                continue
                
            # Shift the cosmic series
            shifted_cosmic = cosmic_aligned.iloc[lag:]
            aligned_evolutionary = evolutionary_aligned.iloc[:len(shifted_cosmic)]
            
            # Calculate correlation
            if len(shifted_cosmic) > 0 and np.std(shifted_cosmic) > 0 and np.std(aligned_evolutionary) > 0:
                corr, p_value = stats.pearsonr(shifted_cosmic, aligned_evolutionary)
                
                # Calculate confidence interval (95%)
                n = len(shifted_cosmic)
                if n > 3:
                    se = 1 / np.sqrt(n - 3)
                    z = np.arctanh(corr)
                    ci_low = np.tanh(z - 1.96 * se)
                    ci_high = np.tanh(z + 1.96 * se)
                    confidence_interval = (ci_low, ci_high)
                else:
                    confidence_interval = (0, 0)
                
                correlations.append({
                    'lag_days': lag,
                    'correlation_coefficient': corr,
                    'p_value': p_value,
                    'confidence_interval': confidence_interval,
                    'significant': p_value < 0.05
                })
        
        return correlations
    
    def time_series_clustering(self, events_df: pd.DataFrame, eps: float = 30, 
                              min_samples: int = 2) -> Dict:
        """
        Cluster events in time using DBSCAN
        
        Args:
            events_df: DataFrame with events and timestamps
            eps: Maximum distance between samples for DBSCAN
            min_samples: Minimum number of samples in a neighborhood
            
        Returns:
            Dictionary with clustering results
        """
        # Extract timestamps and convert to numeric values
        timestamps = events_df['timestamp'].astype(np.int64) // 10**9  # Convert to seconds
        
        # Reshape for clustering
        X = timestamps.values.reshape(-1, 1)
        
        # Standardize the data
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Apply DBSCAN
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(X_scaled)
        
        # Add cluster labels to the original dataframe
        events_df = events_df.copy()
        events_df['cluster'] = clustering.labels_
        
        # Group by cluster
        clusters = {}
        for cluster_id in np.unique(clustering.labels_):
            if cluster_id == -1:  # Noise points
                continue
                
            cluster_events = events_df[events_df['cluster'] == cluster_id]
            clusters[cluster_id] = {
                'events': cluster_events.to_dict('records'),
                'start_time': cluster_events['timestamp'].min(),
                'end_time': cluster_events['timestamp'].max(),
                'duration_days': (cluster_events['timestamp'].max() - cluster_events['timestamp'].min()).days,
                'event_count': len(cluster_events)
            }
        
        return {
            'clusters': clusters,
            'noise_count': len(events_df[events_df['cluster'] == -1]),
            'total_events': len(events_df)
        }
    
    def find_peaks(self, series: pd.Series, height: Optional[float] = None, 
                  distance: Optional[int] = None) -> List[Dict]:
        """
        Find peaks in a time series
        
        Args:
            series: Time series data
            height: Minimum height of peaks
            distance: Minimum distance between peaks
            
        Returns:
            List of dictionaries with peak information
        """
        # Find peaks
        peaks, properties = find_peaks(series.values, height=height, distance=distance)
        
        # Extract peak information
        peak_info = []
        for i, peak_idx in enumerate(peaks):
            peak_info.append({
                'index': peak_idx,
                'timestamp': series.index[peak_idx],
                'value': series.iloc[peak_idx],
                'prominence': properties['prominences'][i] if 'prominences' in properties else None,
                'width': properties['widths'][i] if 'widths' in properties else None
            })
        
        return peak_info
    
    def wavelet_analysis(self, series: pd.Series, scales: Optional[List] = None) -> Dict:
        """
        Perform wavelet analysis on a time series
        
        Args:
            series: Time series data
            scales: List of scales to use for wavelet transform
            
        Returns:
            Dictionary with wavelet analysis results
        """
        try:
            import pywt
        except ImportError:
            logger.warning("PyWavelets not installed, skipping wavelet analysis")
            return {}
        
        if scales is None:
            # Default scales: powers of 2 from 1 to 128
            scales = [2**i for i in range(0, 8)]
        
        # Perform continuous wavelet transform
        coefficients, frequencies = pywt.cwt(series.values, scales, 'morl')
        
        # Calculate power spectrum
        power = (abs(coefficients)) ** 2
        
        # Find significant regions
        # This is a simplified approach - in a real implementation, 
        # we would use statistical significance testing
        threshold = np.percentile(power, 95)
        significant = power > threshold
        
        return {
            'coefficients': coefficients.tolist(),
            'frequencies': frequencies.tolist(),
            'scales': scales,
            'power': power.tolist(),
            'significant': significant.tolist(),
            'threshold': threshold
        }
    
    def fourier_analysis(self, series: pd.Series) -> Dict:
        """
        Perform Fourier analysis on a time series
        
        Args:
            series: Time series data
            
        Returns:
            Dictionary with Fourier analysis results
        """
        # Perform Fast Fourier Transform
        fft_values = np.fft.fft(series.values)
        fft_freq = np.fft.fftfreq(len(series))
        
        # Calculate power spectrum
        power = np.abs(fft_values) ** 2
        
        # Only keep positive frequencies
        pos_freq_idx = fft_freq > 0
        fft_freq = fft_freq[pos_freq_idx]
        power = power[pos_freq_idx]
        
        # Find dominant frequencies
        dominant_freq_idx = np.argsort(power)[-5:]  # Top 5 frequencies
        dominant_freqs = fft_freq[dominant_freq_idx]
        dominant_powers = power[dominant_freq_idx]
        
        return {
            'frequencies': fft_freq.tolist(),
            'power': power.tolist(),
            'dominant_frequencies': dominant_freqs.tolist(),
            'dominant_powers': dominant_powers.tolist()
        }
    
    def mutual_information(self, series1: pd.Series, series2: pd.Series, 
                          bins: int = 10) -> float:
        """
        Calculate mutual information between two time series
        
        Args:
            series1: First time series
            series2: Second time series
            bins: Number of bins for histogram
            
        Returns:
            Mutual information value
        """
        # Ensure both series have the same length
        min_length = min(len(series1), len(series2))
        s1 = series1.iloc[:min_length]
        s2 = series2.iloc[:min_length]
        
        # Create 2D histogram
        hist_xy, xedges, yedges = np.histogram2d(s1, s2, bins=bins)
        
        # Calculate joint and marginal probabilities
        p_xy = hist_xy / float(np.sum(hist_xy))
        p_x = np.sum(p_xy, axis=1)
        p_y = np.sum(p_xy, axis=0)
        
        # Calculate mutual information
        mi = 0.0
        for i in range(bins):
            for j in range(bins):
                if p_xy[i, j] > 0:
                    mi += p_xy[i, j] * np.log(p_xy[i, j] / (p_x[i] * p_y[j]))
        
        return mi
    
    def granger_causality(self, series1: pd.Series, series2: pd.Series, 
                         max_lag: int = 5, alpha: float = 0.05) -> Dict:
        """
        Perform Granger causality test between two time series
        
        Args:
            series1: First time series (potential cause)
            series2: Second time series (potential effect)
            max_lag: Maximum lag to test
            alpha: Significance level
            
        Returns:
            Dictionary with Granger causality test results
        """
        try:
            from statsmodels.tsa.stattools import grangercausalitytests
        except ImportError:
            logger.warning("statsmodels not installed, skipping Granger causality test")
            return {}
        
        # Ensure both series have the same length
        min_length = min(len(series1), len(series2))
        s1 = series1.iloc[:min_length]
        s2 = series2.iloc[:min_length]
        
        # Combine into a DataFrame
        data = pd.concat([s1, s2], axis=1)
        data.columns = ['series1', 'series2']
        
        # Perform Granger causality test
        results = grangercausalitytests(data, max_lag, verbose=False)
        
        # Extract p-values for F-test
        p_values = [results[i][0]['ssr_ftest'][1] for i in range(1, max_lag + 1)]
        
        # Determine if causality is significant
        significant = [p < alpha for p in p_values]
        
        return {
            'p_values': p_values,
            'significant': significant,
            'min_p_value': min(p_values),
            'significant_lag': p_values.index(min(p_values)) + 1 if min(p_values) < alpha else None
        }
