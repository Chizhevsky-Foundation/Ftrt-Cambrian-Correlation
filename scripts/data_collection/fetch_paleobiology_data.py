#!/usr/bin/env python3
"""
Script to fetch fossil occurrence data from the Paleobiology Database.
This data is crucial for identifying evolutionary events like speciation and extinction.
"""

import argparse
import logging
import os
import sys
import pandas as pd

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.core.data_sources import PaleobiologyDBAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Fetch fossil data from the Paleobiology Database.')
    parser.add_argument('--taxa', nargs='+', required=True, help='List of taxa to fetch data for (e.g., "Trilobita" "Dinosauria")')
    parser.add_argument('--start-age', type=float, default=0.0, help='Start age in million years ago (e.g., 0 for present)')
    parser.add_argument('--end-age', type=float, default=541.0, help='End age in million years ago (e.g., 541 for Cambrian start)')
    parser.add_argument('--output-dir', type=str, default='data/evolutionary/raw', help='Directory to save the fetched data')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    api = PaleobiologyDBAPI()
    
    for taxon in args.taxa:
        logger.info(f"Fetching data for taxon: {taxon}")
        try:
            df = api.get_fossil_occurrences(taxon, args.start_age, args.end_age)
            
            if df.empty:
                logger.warning(f"No data returned for taxon: {taxon}")
                continue
            
            # Save to CSV
            output_file = os.path.join(args.output_dir, f"{taxon}_occurrences.csv")
            df.to_csv(output_file, index=False)
            logger.info(f"Successfully saved data for {taxon} to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to fetch data for {taxon}: {str(e)}")

if __name__ == '__main__':
    main()
