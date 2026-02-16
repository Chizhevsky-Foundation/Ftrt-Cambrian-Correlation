import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import io
import base64
import logging

logger = logging.getLogger(__name__)

class Visualizer:
    """
    Utility class for creating visualizations
    """
    
    @staticmethod
    def setup_style(style: str = 'seaborn-v0_8', figsize: Tuple[int, int] = (12, 8)):
        """
        Set up the visualization style
        
        Args:
            style: Matplotlib style
            figsize: Default figure size
        """
        plt.style.use(style)
        plt.rcParams['figure.figsize'] = figsize
    
    @staticmethod
    def plot_time_series(series: pd.Series, title: str = 'Time Series', 
                        xlabel: str = 'Date', ylabel: str = 'Value',
                        color: str = 'blue', alpha: float = 0.7) -> str:
        """
        Plot a time series
        
        Args:
            series: Time series to plot
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            color: Line color
            alpha: Line transparency
            
        Returns:
            Base64 encoded image
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(series.index, series.values, color=color, alpha=alpha)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    @staticmethod
    def plot_multiple_series(series_dict: Dict[str, pd.Series], 
                            title: str = 'Multiple Time Series',
                            xlabel: str = 'Date', ylabel: str = 'Value') -> str:
        """
        Plot multiple time series
        
        Args:
            series_dict: Dictionary of time series with names as keys
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            
        Returns:
            Base64 encoded image
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for name, series in series_dict.items():
            ax.plot(series.index, series.values, label=name, alpha=0.7)
        
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend()
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    @staticmethod
    def plot_correlation(correlation_results: List[Dict], 
                        title: str = 'Cross-Correlation Analysis',
                        xlabel: str = 'Time Lag (days)', 
                        ylabel: str = 'Correlation Coefficient') -> str:
        """
        Plot correlation results
        
        Args:
            correlation_results: List of correlation dictionaries
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            
        Returns:
            Base64 encoded image
        """
        # Extract data
        lags = [r['time_lag_days'] for r in correlation_results]
        correlations = [r['correlation_coefficient'] for r in correlation_results]
        p_values = [r['p_value'] for r in correlation_results]
        significant = [r['significant'] for r in correlation_results]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot all correlations
        ax.plot(lags, correlations, 'o-', color='blue', alpha=0.7)
        
        # Highlight significant correlations
        for i, (lag, corr, sig) in enumerate(zip(lags, correlations, significant)):
            if sig:
                ax.plot(lag, corr, 'ro', markersize=8)
        
        # Add horizontal line at y=0
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        
        # Add significance region
        ax.fill_between(lags, 0, max(correlations) if max(correlations) > 0 else 1, 
                        where=[s for s in significant], color='red', alpha=0.1)
        ax.fill_between(lags, min(correlations) if min(correlations) < 0 else -1, 0, 
                        where=[s for s in significant], color='red', alpha=0.1)
        
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    @staticmethod
    def plot_events_on_timeline(events: List[Dict], 
                               title: str = 'Event Timeline',
                               xlabel: str = 'Date',
                               color_by_type: bool = True) -> str:
        """
        Plot events on a timeline
        
        Args:
            events: List of event dictionaries
            title: Plot title
            xlabel: X-axis label
            color_by_type: Whether to color events by type
            
        Returns:
            Base64 encoded image
        """
        # Convert to DataFrame
        events_df = pd.DataFrame(events)
        events_df['timestamp'] = pd.to_datetime(events_df['timestamp'])
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if color_by_type:
            # Get unique event types
            event_types = events_df['event_type'].unique()
            colors = plt.cm.tab10(np.linspace(0, 1, len(event_types)))
            
            # Plot events by type
            for event_type, color in zip(event_types, colors):
                type_events = events_df[events_df['event_type'] == event_type]
                ax.scatter(type_events['timestamp'], 
                          np.zeros(len(type_events)), 
                          label=event_type, 
                          color=color, 
                          alpha=0.7, 
                          s=50)
            
            ax.legend()
        else:
            # Plot all events with the same color
            ax.scatter(events_df['timestamp'], 
                      np.zeros(len(events_df)), 
                      color='blue', 
                      alpha=0.7, 
                      s=50)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()
        
        # Remove y-axis
        ax.set_yticks([])
        
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    @staticmethod
    def plot_event_heatmap(event_matrix: pd.DataFrame, 
                          title: str = 'Event Heatmap') -> str:
        """
        Plot a heatmap of events
        
        Args:
            event_matrix: Binary event matrix
            title: Plot title
            
        Returns:
            Base64 encoded image
        """
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create heatmap
        sns.heatmap(event_matrix.T, cmap='YlOrRd', cbar=True, ax=ax)
        
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Event Type')
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    @staticmethod
    def plot_clusters(clusters: Dict, title: str = 'Event Clusters') -> str:
        """
        Plot event clusters
        
        Args:
            clusters: Dictionary of cluster information
            title: Plot title
            
        Returns:
            Base64 encoded image
        """
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot clusters
        for cluster_id, cluster_info in clusters.items():
            start = cluster_info['start_time']
            end = cluster_info['end_time']
            event_count = cluster_info['event_count']
            
            # Plot cluster as a horizontal bar
            ax.barh(cluster_id, (end - start).days, left=start, height=0.5, 
                    alpha=0.7, label=f"Cluster {cluster_id} ({event_count} events)")
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()
        
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Cluster ID')
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    @staticmethod
    def plot_fourier_spectrum(frequencies: np.ndarray, power: np.ndarray,
                             dominant_freqs: Optional[np.ndarray] = None,
                             dominant_powers: Optional[np.ndarray] = None,
                             title: str = 'Fourier Power Spectrum') -> str:
        """
        Plot Fourier power spectrum
        
        Args:
            frequencies: Array of frequencies
            power: Array of power values
            dominant_freqs: Array of dominant frequencies
            dominant_powers: Array of dominant power values
            title: Plot title
            
        Returns:
            Base64 encoded image
        """
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot power spectrum
        ax.plot(frequencies, power, 'b-', alpha=0.7)
        
        # Highlight dominant frequencies
        if dominant_freqs is not None and dominant_powers is not None:
            ax.plot(dominant_freqs, dominant_powers, 'ro', markersize=8)
        
        ax.set_title(title)
        ax.set_xlabel('Frequency')
        ax.set_ylabel('Power')
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    @staticmethod
    def plot_wavelet_power(time: np.ndarray, scales: np.ndarray, 
                          power: np.ndarray, title: str = 'Wavelet Power Spectrum') -> str:
        """
        Plot wavelet power spectrum
        
        Args:
            time: Array of time values
            scales: Array of scales
            power: 2D array of power values
            title: Plot title
            
        Returns:
            Base64 encoded image
        """
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create meshgrid for contour plot
        T, S = np.meshgrid(time, scales)
        
        # Plot contour
        contour = ax.contourf(T, S, power, 100, cmap='viridis')
        fig.colorbar(contour, ax=ax, label='Power')
        
        ax.set_title(title)
        ax.set_xlabel('Time')
        ax.set_ylabel('Scale')
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
