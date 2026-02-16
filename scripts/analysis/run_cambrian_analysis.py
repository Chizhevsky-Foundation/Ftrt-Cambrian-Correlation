#!/usr/bin/env python3
"""
Script to perform a focused correlation analysis on the Cambrian Explosion period.
This is the flagship analysis proposed by the project.
"""

import argparse
import logging
import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.core.cosmic_evolution_correlator import CosmicEvolutionCorrelator
from app.utils.visualization import Visualizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define the Cambrian Period time frame
CAMBRIAN_START = datetime(year=-541, month=1, day=1) # Using negative years for BP
CAMBRIAN_END = datetime(year=-485, month=1, day=1)

def main():
    parser = argparse.ArgumentParser(description='Run the FTRT-Cambrian correlation analysis.')
    parser.add_argument('--ftrt-data', type=str, required=True, help='Path to processed FTRT data (CSV)')
    parser.add_argument('--evolutionary-data', type=str, required=True, help='Path to processed evolutionary event data (CSV)')
    parser.add_argument('--output-dir', type=str, default='analysis_output/cambrian', help='Directory to save analysis results and plots')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load data
    logger.info("Loading FTRT and evolutionary data...")
    ftrt_df = pd.read_csv(args.ftrt_data)
    evo_df = pd.read_csv(args.evolutionary_data)
    
    ftrt_df['date'] = pd.to_datetime(ftrt_df['date'])
    evo_df['timestamp'] = pd.to_datetime(evo_df['timestamp'])
    
    # Filter data for the Cambrian Period
    # Note: This is a simplified filter. Real data would use Ma (Million years ago).
    # For this script, we'll assume the dataframes have a 'age_ma' column.
    if 'age_ma' in ftrt_df.columns:
        cambrian_ftrt = ftrt_df[(ftrt_df['age_ma'] <= 541) & (ftrt_df['age_ma'] > 485)]
    else:
        logger.warning("FTRT data does not have 'age_ma' column. Using full dataset.")
        cambrian_ftrt = ftrt_df

    if 'age_ma' in evo_df.columns:
        cambrian_evo = evo_df[(evo_df['age_ma'] <= 541) & (evo_df['age_ma'] > 485)]
    else:
        logger.warning("Evolutionary data does not have 'age_ma' column. Using full dataset.")
        cambrian_evo = evo_df
    
    # Initialize the correlator
    correlator = CosmicEvolutionCorrelator()
    
    # Manually set the data for the correlator (bypassing API calls)
    # This is a simplified approach for a standalone script.
    # A more robust way would be to mock the API calls.
    correlator.ftrt_calculator = type('obj', (object,), {'find_peaks': lambda *a, **k: []})()
    correlator.paleomag_database = type('obj', (object,), {'get_field_weaknesses': lambda *a, **k: []})()
    correlator.fossil_parser = type('obj', (object,), {'identify_radiations': lambda *a, **k: []})()

    # Convert dataframes to event lists for the correlator
    cosmic_events = []
    for _, row in cambrian_ftrt.iterrows():
        if row.get('is_peak', False):
            cosmic_events.append({
                'timestamp': row['date'],
                'event_type': 'ftrt_peak',
                'magnitude': row['ftrt_normalized'],
                'duration': timedelta(days=1), # Simplified duration
                'description': f"FTRT peak with normalized value {row['ftrt_normalized']:.2f}"
            })

    evolutionary_events = []
    for _, row in cambrian_evo.iterrows():
        evolutionary_events.append({
            'timestamp': row['timestamp'],
            'event_type': row.get('event_type', 'unknown'),
            'magnitude': row.get('magnitude', 1.0),
            'affected_taxa': [row.get('taxon', 'Unknown')],
            'description': row.get('description', 'Evolutionary event')
        })
    
    logger.info(f"Found {len(cosmic_events)} cosmic events and {len(evolutionary_events)} evolutionary events in the Cambrian period.")
    
    if not cosmic_events or not evolutionary_events:
        logger.error("Not enough data for analysis in the specified period. Exiting.")
        sys.exit(1)

    # Perform the correlation analysis
    # We need to adapt the correlator's method to work with our pre-loaded data
    # This is a simplified version of the correlation logic
    cosmic_series = pd.DataFrame(cosmic_events).set_index('timestamp')['magnitude']
    evo_series = pd.DataFrame(evolutionary_events).set_index('timestamp')['magnitude']
    
    # Align series
    aligned_cosmic, aligned_evo = DataProcessor.align_time_series(cosmic_series, evo_series)
    
    # Calculate cross-correlation
    max_lag_days = 50 # 50 million years in our simplified model
    correlation_results = correlator.statistical_analyzer.cross_correlation(
        aligned_cosmic, aligned_evo, max_lag=max_lag_days
    )
    
    # Save results
    results_df = pd.DataFrame(correlation_results)
    results_file = os.path.join(args.output_dir, 'cambrian_correlation_results.csv')
    results_df.to_csv(results_file, index=False)
    logger.info(f"Saved correlation results to {results_file}")

    # Generate visualizations
    Visualizer.setup_style()
    
    # Plot FTRT vs Evolutionary Events
    plot1 = Visualizer.plot_multiple_series(
        {'FTRT': aligned_cosmic, 'Evolutionary Events': aligned_evo},
        title="FTRT and Evolutionary Events during the Cambrian Period"
    )
    with open(os.path.join(args.output_dir, 'cambrian_timeseries.png'), 'wb') as f:
        f.write(base64.b64decode(plot1))
    
    # Plot correlation results
    plot2 = Visualizer.plot_correlation(
        correlation_results,
        title="Cross-Correlation: FTRT vs Evolutionary Events (Cambrian)"
    )
    with open(os.path.join(args.output_dir, 'cambrian_correlation_plot.png'), 'wb') as f:
        f.write(base64.b64decode(plot2))
        
    logger.info(f"Analysis complete. Results and plots saved to {args.output_dir}")

if __name__ == '__main__':
    import base64
    main()
