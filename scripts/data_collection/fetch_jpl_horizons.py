#!/usr/bin/env python3
"""
Script to fetch planetary ephemeris data from NASA JPL Horizons API.
This data is essential for calculating Planetary Tidal Forces (FTRT).
"""

import argparse
import logging
import os
import sys
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.core.data_sources import JPLHorizonsAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Planet IDs for JPL Horizons API
PLANET_IDS = {
    'mercury': '199',
    'venus': '299',
    'earth': '399',
    'mars': '499',
    'jupiter': '599',
    'saturn': '699',
    'uranus': '799',
    'neptune': '899'
}

def fetch_planet_data(planet_name, start_date, end_date, output_dir):
    """
    Fetch ephemeris data for a single planet and save it to a CSV file.
    """
    logger.info(f"Fetching data for {planet_name} from {start_date} to {end_date}")
    
    api = JPLHorizonsAPI(cache_dir=output_dir)
    planet_id = PLANET_IDS.get(planet_name.lower())
    
    if not planet_id:
        logger.error(f"Unknown planet: {planet_name}")
        return False
    
    try:
        df = api.get_planet_positions(planet_id, start_date, end_date)
        
        if df.empty:
            logger.warning(f"No data returned for {planet_name}")
            return False
        
        # Save to CSV
        output_file = os.path.join(
            output_dir, 
            f"{planet_name}_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv"
        )
        df.to_csv(output_file, index=False)
        logger.info(f"Successfully saved data for {planet_name} to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to fetch data for {planet_name}: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Fetch planetary ephemeris data from JPL Horizons.')
    parser.add_argument('--start-date', type=str, required=True, help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end-date', type=str, required=True, help='End date in YYYY-MM-DD format')
    parser.add_argument('--planets', nargs='+', default=list(PLANET_IDS.keys()), help='List of planets to fetch data for')
    parser.add_argument('--output-dir', type=str, default='data/cosmic/raw', help='Directory to save the fetched data')
    
    args = parser.parse_args()
    
    # Parse dates
    try:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    except ValueError:
        logger.error("Invalid date format. Please use YYYY-MM-DD.")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Fetch data for each planet
    success_count = 0
    for planet in args.planets:
        if fetch_planet_data(planet, start_date, end_date, args.output_dir):
            success_count += 1
    
    logger.info(f"Successfully fetched data for {success_count}/{len(args.planets)} planets.")

if __name__ == '__main__':
    main()
