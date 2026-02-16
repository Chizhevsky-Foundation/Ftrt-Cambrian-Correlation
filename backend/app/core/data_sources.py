import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import json
import os
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class JPLHorizonsAPI:
    """
    Interface to JPL Horizons ephemeris data for planetary positions
    """
    
    def __init__(self, cache_dir=None):
        self.base_url = "https://ssd.jpl.nasa.gov/api/horizons.api"
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), '../../data/cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def get_planet_positions(self, planet_id: str, start_date: datetime, 
                            end_date: datetime, step: str = '1d') -> pd.DataFrame:
        """
        Get planetary positions for a specific time range
        
        Args:
            planet_id: Planet identifier (e.g., '10' for Sun, '199' for Mercury, etc.)
            start_date: Start date for ephemeris data
            end_date: End date for ephemeris data
            step: Time step (e.g., '1d' for daily)
            
        Returns:
            DataFrame with time series of planetary positions
        """
        # Check if we have cached data
        cache_file = os.path.join(
            self.cache_dir, 
            f"planet_{planet_id}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        )
        
        if os.path.exists(cache_file):
            logger.info(f"Loading cached data for planet {planet_id}")
            return pd.read_csv(cache_file, parse_dates=['date'])
        
        # Format dates for API
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        # Build API request
        params = {
            'format': 'json',
            'COMMAND': f'"{planet_id}"',
            'EPHEM_TYPE': 'VECTORS',
            'CENTER': '500@0',  # Solar System Barycenter
            'START_TIME': start_str,
            'STOP_TIME': end_str,
            'STEP_SIZE': step,
            'QUANTITIES': '20,21,22,23,24,25'  # X, Y, Z positions and velocities
        }
        
        try:
            logger.info(f"Fetching data for planet {planet_id} from JPL Horizons")
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse the result
            if 'result' not in data:
                raise ValueError(f"No data returned for planet {planet_id}")
            
            # Extract the vector data from the result string
            result_str = data['result']
            lines = result_str.split('\n')
            
            # Find the start of the data table
            start_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('$$SOE'):
                    start_idx = i + 1
                    break
            
            # Parse the data rows
            positions = []
            for line in lines[start_idx:]:
                if line.startswith('$$EOE'):
                    break
                
                parts = line.split()
                if len(parts) >= 13:
                    date_str = parts[0] + ' ' + parts[1]
                    date = datetime.strptime(date_str, '%Y-%b-%d %H:%M:%S')
                    x = float(parts[2])
                    y = float(parts[3])
                    z = float(parts[4])
                    
                    positions.append({
                        'date': date,
                        'x': x,
                        'y': y,
                        'z': z
                    })
            
            # Create DataFrame
            df = pd.DataFrame(positions)
            
            # Cache the result
            df.to_csv(cache_file, index=False)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching planetary data: {str(e)}")
            # Return empty DataFrame with proper columns
            return pd.DataFrame(columns=['date', 'x', 'y', 'z'])
    
    def calculate_relative_positions(self, planet1_id: str, planet2_id: str, 
                                   start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Calculate relative positions between two planets
        
        Args:
            planet1_id: First planet identifier
            planet2_id: Second planet identifier
            start_date: Start date for calculation
            end_date: End date for calculation
            
        Returns:
            DataFrame with relative positions
        """
        # Get positions for both planets
        pos1 = self.get_planet_positions(planet1_id, start_date, end_date)
        pos2 = self.get_planet_positions(planet2_id, start_date, end_date)
        
        # Merge on date
        merged = pd.merge(pos1, pos2, on='date', suffixes=('_1', '_2'))
        
        # Calculate relative position
        merged['dx'] = merged['x_1'] - merged['x_2']
        merged['dy'] = merged['y_1'] - merged['y_2']
        merged['dz'] = merged['z_1'] - merged['z_2']
        
        # Calculate distance
        merged['distance'] = np.sqrt(merged['dx']**2 + merged['dy']**2 + merged['dz']**2)
        
        return merged

class GEOMAGIA50API:
    """
    Interface to GEOMAGIA50 database for paleomagnetic data
    """
    
    def __init__(self, cache_dir=None):
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), '../../data/cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def get_paleomagnetic_data(self, location: str, start_year: int, 
                              end_year: int) -> pd.DataFrame:
        """
        Get paleomagnetic intensity data for a specific location and time range
        
        Args:
            location: Location identifier
            start_year: Start year for data
            end_year: End year for data
            
        Returns:
            DataFrame with paleomagnetic intensity data
        """
        # Check if we have cached data
        cache_file = os.path.join(
            self.cache_dir, 
            f"paleomag_{location}_{start_year}_{end_year}.csv"
        )
        
        if os.path.exists(cache_file):
            logger.info(f"Loading cached paleomagnetic data for {location}")
            return pd.read_csv(cache_file, parse_dates=['date'])
        
        # In a real implementation, we would query the GEOMAGIA50 database
        # For now, we'll simulate the data
        logger.info(f"Simulating paleomagnetic data for {location}")
        
        # Create a date range
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        dates = pd.date_range(start=start_date, end=end_date, freq='M')
        
        # Generate simulated intensity data with trend and noise
        n_points = len(dates)
        trend = np.linspace(50000, 45000, n_points)  # Decreasing trend
        noise = np.random.normal(0, 1000, n_points)
        seasonal = 2000 * np.sin(np.linspace(0, 20*np.pi, n_points))
        
        intensity = trend + noise + seasonal
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'intensity': intensity,
            'location': location
        })
        
        # Cache the result
        df.to_csv(cache_file, index=False)
        
        return df

class PaleobiologyDBAPI:
    """
    Interface to Paleobiology Database for fossil data
    """
    
    def __init__(self, cache_dir=None):
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), '../../data/cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def get_fossil_occurrences(self, taxon: str, start_age: float, 
                              end_age: float) -> pd.DataFrame:
        """
        Get fossil occurrences for a specific taxon and time range
        
        Args:
            taxon: Taxon name
            start_age: Start age in million years ago
            end_age: End age in million years ago
            
        Returns:
            DataFrame with fossil occurrence data
        """
        # Check if we have cached data
        cache_file = os.path.join(
            self.cache_dir, 
            f"fossil_{taxon}_{start_age}_{end_age}.csv"
        )
        
        if os.path.exists(cache_file):
            logger.info(f"Loading cached fossil data for {taxon}")
            return pd.read_csv(cache_file)
        
        # In a real implementation, we would query the Paleobiology Database
        # For now, we'll simulate the data
        logger.info(f"Simulating fossil data for {taxon}")
        
        # Generate random occurrence data
        n_occurrences = np.random.randint(10, 100)
        ages = np.random.uniform(start_age, end_age, n_occurrences)
        
        # Create DataFrame
        df = pd.DataFrame({
            'taxon': [taxon] * n_occurrences,
            'age_ma': ages,
            'location': [f"Location_{i}" for i in range(n_occurrences)],
            'reference': [f"Reference_{i}" for i in range(n_occurrences)]
        })
        
        # Cache the result
        df.to_csv(cache_file, index=False)
        
        return df
    
    def get_first_appearances(self, taxon_rank: str = 'genus') -> pd.DataFrame:
        """
        Get first appearance data for taxa of a specific rank
        
        Args:
            taxon_rank: Taxonomic rank (genus, family, etc.)
            
        Returns:
            DataFrame with first appearance data
        """
        # Check if we have cached data
        cache_file = os.path.join(
            self.cache_dir, 
            f"first_appearances_{taxon_rank}.csv"
        )
        
        if os.path.exists(cache_file):
            logger.info(f"Loading cached first appearance data for {taxon_rank}")
            return pd.read_csv(cache_file)
        
        # In a real implementation, we would query the Paleobiology Database
        # For now, we'll simulate the data
        logger.info(f"Simulating first appearance data for {taxon_rank}")
        
        # Generate random taxa with first appearances
        n_taxa = 100
        taxa_names = [f"{taxon_rank.capitalize()}_{i}" for i in range(n_taxa)]
        first_ages = np.random.uniform(0, 541, n_taxa)  # From present to Cambrian
        
        # Create DataFrame
        df = pd.DataFrame({
            'taxon': taxa_names,
            'rank': [taxon_rank] * n_taxa,
            'first_appearance_ma': first_ages
        })
        
        # Cache the result
        df.to_csv(cache_file, index=False)
        
        return df

class TimeTreeAPI:
    """
    Interface to TimeTree database for molecular divergence times
    """
    
    def __init__(self, cache_dir=None):
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), '../../data/cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def get_divergence_time(self, taxon1: str, taxon2: str) -> Dict:
        """
        Get divergence time between two taxa
        
        Args:
            taxon1: First taxon name
            taxon2: Second taxon name
            
        Returns:
            Dictionary with divergence time information
        """
        # Check if we have cached data
        cache_file = os.path.join(
            self.cache_dir, 
            f"divergence_{taxon1}_{taxon2}.json"
        )
        
        if os.path.exists(cache_file):
            logger.info(f"Loading cached divergence data for {taxon1} and {taxon2}")
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        # In a real implementation, we would query the TimeTree database
        # For now, we'll simulate the data
        logger.info(f"Simulating divergence data for {taxon1} and {taxon2}")
        
        # Generate random divergence time
        divergence_time = np.random.uniform(1, 500)  # Million years ago
        
        result = {
            'taxon1': taxon1,
            'taxon2': taxon2,
            'divergence_time_ma': divergence_time,
            'confidence_interval': (
                divergence_time * 0.8,
                divergence_time * 1.2
            ),
            'studies_count': np.random.randint(1, 20)
        }
        
        # Cache the result
        with open(cache_file, 'w') as f:
            json.dump(result, f)
        
        return result
