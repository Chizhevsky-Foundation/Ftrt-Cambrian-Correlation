#!/usr/bin/env python3
"""
Script to process raw planetary position data to calculate FTRT (Planetary Tidal Force)
and identify significant peaks.
"""

import argparse
import logging
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.core.cosmic_evolution_correlator import PlanetaryTidalForceEngine
from app.utils.data_processing import DataProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Planet masses (kg) - needed for FTRT calculation
PLANET_MASSES = {
    'mercury': 3.3011e23,
    'venus': 4.8675e24,
    'earth': 5.9722e24,
    'mars': 6.4171e23,
    'jupiter': 1.8982e27,
    'saturn': 5.6834e26,
    'uranus': 8.6810e25,
    'neptune': 1.02413e26
}

def calculate_ftrt_for_date(planet_positions):
    """
    Calculate the total FTRT for a single day based on planet positions.
    FTRT is a simplified sum of (mass / distance^3) for all planets.
    """
    total_ftrt = 0.0
    sun_pos = planet_positions.get('sun')
    
    if sun_pos is None:
        # Assume sun is at origin (0,0,0) if not provided
        sun_pos = {'x': 0, 'y': 0, 'z': 0}

    for planet_name, pos in planet_positions.items():
        if planet_name == 'sun':
            continue
        
        # Calculate distance from the planet to the sun
        dx = pos['x'] - sun_pos['x']
        dy = pos['y'] - sun_pos['y']
        dz = pos['z'] - sun_pos['z']
        distance = np.sqrt(dx**2 + dy**2 + dz**2)
        
        if distance > 0:
            mass = PLANET_MASSES.get(planet_name.lower())
            if mass:
                # Tidal force is proportional to mass / distance^3
                total_ftrt += mass / (distance ** 3)
    
    return total_ftrt

def main():
    parser = argparse.ArgumentParser(description='Process raw planetary data to calculate FTRT.')
    parser.add_argument('--input-dir', type=str, required=True, help='Directory containing raw planetary CSV files')
    parser.add_argument('--output-file', type=str, required=True, help='Path to save the processed FTRT data (CSV)')
    parser.add_argument('--peak-threshold', type=float, default=1.5, help='Threshold for identifying FTRT peaks')
    
    args = parser.parse_args()
    
    # Load all planetary data
    all_planet_data = {}
    for filename in os.listdir(args.input_dir):
        if filename.endswith('.csv'):
            planet_name = filename.split('_')[0]
            filepath = os.path.join(args.input_dir, filename)
            df = pd.read_csv(filepath)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            all_planet_data[planet_name] = df
    
    if not all_planet_data:
        logger.error("No data found in the input directory.")
        sys.exit(1)
    
    # Combine data into a single DataFrame
    # Find the common date range
    common_index = all_planet_data[list(all_planet_data.keys())[0]].index
    for df in all_planet_data.values():
        common_index = common_index.intersection(df.index)
    
    if common_index.empty:
        logger.error("No common dates found among the planetary data files.")
        sys.exit(1)
    
    # Calculate FTRT for each day
    ftrt_series = pd.Series(index=common_index, dtype=float)
    logger.info(f"Calculating FTRT for {len(common_index)} days...")
    
    for date in common_index:
        daily_positions = {}
        for planet_name, df in all_planet_data.items():
            if date in df.index:
                row = df.loc[date]
                daily_positions[planet_name] = {
                    'x': row['x'],
                    'y': row['y'],
                    'z': row['z']
                }
        
        ftrt_value = calculate_ftrt_for_date(daily_positions)
        ftrt_series.loc[date] = ftrt_value
    
    # Normalize the FTRT series for better interpretability
    ftrt_normalized = DataProcessor.normalize_time_series(ftrt_series, method='minmax')
    
    # Identify peaks
    peaks = DataProcessor.find_peaks(ftrt_normalized, height=args.peak_threshold)
    
    # Create a DataFrame for the results
    result_df = pd.DataFrame({
        'ftrt_raw': ftrt_series,
        'ftrt_normalized': ftrt_normalized
    })
    
    # Add a column for peaks
    result_df['is_peak'] = False
    for peak in peaks:
        result_df.loc[peak['timestamp'], 'is_peak'] = True
    
    # Save the results
    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    result_df.to_csv(args.output_file)
    logger.info(f"Successfully processed and saved FTRT data to {args.output_file}")
    logger.info(f"Identified {len(peaks)} FTRT peaks above the threshold of {args.peak_threshold}.")

if __name__ == '__main__':
    main()
