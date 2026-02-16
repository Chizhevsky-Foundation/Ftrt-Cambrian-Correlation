# backend/app/core/cosmic_evolution_correlator.py
import numpy as np
import pandas as pd
from scipy import stats
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CosmicEvent:
    """Representa un evento cósmico con sus características"""
    timestamp: datetime
    event_type: str  # 'planetary_alignment', 'solar_storm', 'cosmic_ray_flux'
    magnitude: float
    duration: timedelta
    description: str

@dataclass
class EvolutionaryEvent:
    """Representa un evento evolutivo con sus características"""
    timestamp: datetime
    event_type: str  # 'speciation', 'extinction', 'mutation_burst'
    magnitude: float
    affected_taxa: List[str]
    description: str

@dataclass
class CorrelationResult:
    """Almacena el resultado de una correlación entre eventos cósmicos y evolutivos"""
    correlation_coefficient: float
    p_value: float
    time_lag: timedelta
    confidence_interval: Tuple[float, float]
    significant: bool

class PlanetaryTidalForceEngine:
    """Calcula las fuerzas de marea planetarias (FTRT) basadas en alineaciones"""
    
    def __init__(self):
        # Cargar datos efemérides de JPL (simulados para el ejemplo)
        self.planet_data = self._load_planet_data()
    
    def _load_planet_data(self) -> Dict:
        """Cargar datos de posiciones planetarias (simulado)"""
        # En una implementación real, usaríamos la API de JPL Horizons
        return {
            'mercury': {'mass': 3.3011e23, 'orbital_period': 87.97},
            'venus': {'mass': 4.8675e24, 'orbital_period': 224.70},
            'mars': {'mass': 6.4171e23, 'orbital_period': 686.98},
            'jupiter': {'mass': 1.8982e27, 'orbital_period': 4332.59},
            'saturn': {'mass': 5.6834e26, 'orbital_period': 10759.22},
        }
    
    def calculate_ftrt(self, timestamp: datetime) -> float:
        """
        Calcula la Fuerza de Marea Relativa Total (FTRT) en un momento dado
        Fórmula simplificada: FTRT = Σ(masa_planeta/distancia^3)
        """
        total_force = 0.0
        
        # En una implementación real, calcularíamos las posiciones exactas
        # para el timestamp dado usando las efemérides
        
        for planet_name, planet_info in self.planet_data.items():
            # Simulación: variación sinusoidal de la distancia
            phase = (timestamp.day % int(planet_info['orbital_period'])) / planet_info['orbital_period']
            distance_factor = 1.0 + 0.2 * np.sin(2 * np.pi * phase)
            
            # Fuerza de marea (simplificada)
            force = planet_info['mass'] / (distance_factor ** 3)
            total_force += force
        
        # Normalizar para obtener valores comparables
        return total_force / 1e24
    
    def find_peaks(self, start_date: datetime, end_date: datetime, 
                   threshold: float = 1.5) -> List[CosmicEvent]:
        """
        Encuentra picos de FTRT en un rango de fechas
        """
        peaks = []
        current_date = start_date
        ftrt_values = []
        dates = []
        
        # Calcular valores FTRT para el rango completo
        while current_date <= end_date:
            ftrt = self.calculate_ftrt(current_date)
            ftrt_values.append(ftrt)
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Encontrar picos usando un algoritmo simple
        for i in range(1, len(ftrt_values) - 1):
            if (ftrt_values[i] > ftrt_values[i-1] and 
                ftrt_values[i] > ftrt_values[i+1] and 
                ftrt_values[i] > threshold):
                
                # Estimar duración del pico (días hasta que cae por debajo del umbral)
                duration_days = 1
                j = i + 1
                while j < len(ftrt_values) and ftrt_values[j] > threshold:
                    duration_days += 1
                    j += 1
                
                peaks.append(CosmicEvent(
                    timestamp=dates[i],
                    event_type='planetary_alignment',
                    magnitude=ftrt_values[i],
                    duration=timedelta(days=duration_days),
                    description=f"FTRT peak of {ftrt_values[i]:.2f} detected"
                ))
        
        return peaks

class GeomagneticHistoryAPI:
    """API simulada para acceder a datos históricos del campo geomagnético"""
    
    def __init__(self):
        # Cargar datos paleomagnéticos (simulados)
        self.paleomag_data = self._load_paleomag_data()
    
    def _load_paleomag_data(self) -> pd.DataFrame:
        """Cargar datos paleomagnéticos (simulado)"""
        # En una implementación real, usaríamos GEOMAGIA50 u otra base de datos
        dates = pd.date_range(start='1900-01-01', end='2100-01-01', freq='M')
        # Simular variaciones del campo magnético con tendencia a la disminución
        values = 50000 - 50 * np.arange(len(dates)) + 5000 * np.sin(np.arange(len(dates)) / 12)
        noise = np.random.normal(0, 1000, len(dates))
        values += noise
        
        return pd.DataFrame({'date': dates, 'intensity': values})
    
    def get_field_weaknesses(self, start_date: datetime, end_date: datetime, 
                             threshold_percentile: float = 10.0) -> List[CosmicEvent]:
        """
        Identifica períodos de debilitamiento del campo geomagnético
        """
        # Filtrar datos en el rango solicitado
        mask = (self.paleomag_data['date'] >= start_date) & (self.paleomag_data['date'] <= end_date)
        filtered_data = self.paleomag_data.loc[mask]
        
        # Calcular umbral de debilitamiento
        threshold = np.percentile(filtered_data['intensity'], threshold_percentile)
        
        # Encontrar períodos por debajo del umbral
        weaknesses = []
        in_weak_period = False
        start_weak_period = None
        
        for _, row in filtered_data.iterrows():
            if row['intensity'] < threshold and not in_weak_period:
                # Comienzo de un período débil
                in_weak_period = True
                start_weak_period = row['date']
            elif row['intensity'] >= threshold and in_weak_period:
                # Fin de un período débil
                in_weak_period = False
                duration = row['date'] - start_weak_period
                
                # Calcular intensidad promedio durante el período
                weak_period_data = filtered_data[
                    (filtered_data['date'] >= start_weak_period) & 
                    (filtered_data['date'] < row['date'])
                ]
                avg_intensity = weak_period_data['intensity'].mean()
                
                weaknesses.append(CosmicEvent(
                    timestamp=start_weak_period,
                    event_type='geomagnetic_weakness',
                    magnitude=avg_intensity,
                    duration=duration,
                    description=f"Geomagnetic field weakened to {avg_intensity:.0f} nT for {duration.days} days"
                ))
        
        return weaknesses

class PaleontologicalRecordParser:
    """Parser para registros paleontológicos y eventos evolutivos"""
    
    def __init__(self):
        # Cargar datos fósiles (simulados)
        self.fossil_data = self._load_fossil_data()
    
    def _load_fossil_data(self) -> pd.DataFrame:
        """Cargar datos fósiles (simulado)"""
        # En una implementación real, usaríamos Paleobiology Database
        np.random.seed(42)  # Para reproducibilidad
        
        # Generar eventos de especiación simulados
        dates = pd.date_range(start='1900-01-01', end='2100-01-01', freq='M')
        
        # Simular eventos de especiación con cierta aleatoriedad
        speciation_probability = 0.1  # 10% de probabilidad cada mes
        speciation_events = []
        
        for date in dates:
            if np.random.random() < speciation_probability:
                # Magnitud aleatoria entre 1 y 10
                magnitude = np.random.uniform(1, 10)
                
                # Número de taxones afectados (aleatorio entre 1 y 5)
                num_taxa = np.random.randint(1, 6)
                taxa = [f"Taxus_{i}" for i in range(num_taxa)]
                
                speciation_events.append({
                    'date': date,
                    'event_type': 'speciation',
                    'magnitude': magnitude,
                    'taxa': taxa,
                    'description': f"Speciation event affecting {num_taxa} taxa"
                })
        
        # Generar eventos de extinción simulados
        extinction_probability = 0.05  # 5% de probabilidad cada mes
        
        for date in dates:
            if np.random.random() < extinction_probability:
                # Magnitud aleatoria entre 1 y 8
                magnitude = np.random.uniform(1, 8)
                
                # Número de taxones afectados (aleatorio entre 1 y 3)
                num_taxa = np.random.randint(1, 4)
                taxa = [f"Extinctus_{i}" for i in range(num_taxa)]
                
                speciation_events.append({
                    'date': date,
                    'event_type': 'extinction',
                    'magnitude': magnitude,
                    'taxa': taxa,
                    'description': f"Extinction event affecting {num_taxa} taxa"
                })
        
        return pd.DataFrame(speciation_events)
    
    def identify_radiations(self, start_date: datetime, end_date: datetime) -> List[EvolutionaryEvent]:
        """
        Identifica eventos de radiación evolutiva en un rango de fechas
        """
        # Filtrar datos en el rango solicitado
        mask = (self.fossil_data['date'] >= start_date) & (self.fossil_data['date'] <= end_date)
        filtered_data = self.fossil_data.loc[mask]
        
        radiation_events = []
        
        for _, row in filtered_data.iterrows():
            radiation_events.append(EvolutionaryEvent(
                timestamp=row['date'],
                event_type=row['event_type'],
                magnitude=row['magnitude'],
                affected_taxa=row['taxa'],
                description=row['description']
            ))
        
        return radiation_events

class MolecularDivergenceTimer:
    """Estima tiempos de divergencia molecular (simulado)"""
    
    def __init__(self):
        # En una implementación real, usaríamos TimeTree database
        pass
    
    def estimate_divergence_times(self, taxa: List[str]) -> Dict[str, datetime]:
        """
        Estima tiempos de divergencia para una lista de taxones
        """
        # Simulación: generar tiempos de divergencia aleatorios
        divergence_times = {}
        
        for taxon in taxa:
            # Generar una fecha aleatoria en los últimos 100 años
            days_ago = np.random.randint(0, 365 * 100)
            divergence_date = datetime.now() - timedelta(days=days_ago)
            divergence_times[taxon] = divergence_date
        
        return divergence_times

class StatisticalAnalyzer:
    """Realiza análisis estadísticos para correlaciones"""
    
    def __init__(self):
        pass
    
    def cross_correlation(self, cosmic_events: List[CosmicEvent], 
                          evolutionary_events: List[EvolutionaryEvent],
                          max_lag_days: int = 365) -> List[CorrelationResult]:
        """
        Calcula la correlación cruzada entre eventos cósmicos y evolutivos
        """
        results = []
        
        # Convertir eventos a series temporales binarias
        start_date = min(
            min(event.timestamp for event in cosmic_events),
            min(event.timestamp for event in evolutionary_events)
        )
        
        end_date = max(
            max(event.timestamp for event in cosmic_events),
            max(event.timestamp for event in evolutionary_events)
        )
        
        # Crear series temporales con resolución diaria
        days = (end_date - start_date).days + 1
        cosmic_series = np.zeros(days)
        evolutionary_series = np.zeros(days)
        
        # Marcar eventos cósmicos
        for event in cosmic_events:
            day_index = (event.timestamp - start_date).days
            if 0 <= day_index < days:
                cosmic_series[day_index] = event.magnitude
        
        # Marcar eventos evolutivos
        for event in evolutionary_events:
            day_index = (event.timestamp - start_date).days
            if 0 <= day_index < days:
                evolutionary_series[day_index] = event.magnitude
        
        # Calcular correlación cruzada para diferentes lags
        for lag in range(0, max_lag_days + 1, 30):  # Cada 30 días hasta max_lag_days
            if lag >= len(cosmic_series):
                continue
                
            # Desplazar la serie cósmica
            shifted_cosmic = cosmic_series[lag:]
            aligned_evolutionary = evolutionary_series[:len(shifted_cosmic)]
            
            # Calcular correlación
            if len(shifted_cosmic) > 0 and np.std(shifted_cosmic) > 0 and np.std(aligned_evolutionary) > 0:
                corr, p_value = stats.pearsonr(shifted_cosmic, aligned_evolutionary)
                
                # Calcular intervalo de confianza (95%)
                n = len(shifted_cosmic)
                if n > 3:
                    se = 1 / np.sqrt(n - 3)
                    z = np.arctanh(corr)
                    ci_low = np.tanh(z - 1.96 * se)
                    ci_high = np.tanh(z + 1.96 * se)
                    confidence_interval = (ci_low, ci_high)
                else:
                    confidence_interval = (0, 0)
                
                results.append(CorrelationResult(
                    correlation_coefficient=corr,
                    p_value=p_value,
                    time_lag=timedelta(days=lag),
                    confidence_interval=confidence_interval,
                    significant=p_value < 0.05
                ))
        
        return results
    
    def time_series_clustering(self, events: List[CosmicEvent]) -> Dict:
        """
        Agrupa eventos en clusters temporales
        """
        # Extraer timestamps
        timestamps = [event.timestamp for event in events]
        
        # Convertir a valores numéricos (días desde el primer evento)
        if not timestamps:
            return {}
            
        start_date = min(timestamps)
        numeric_times = [(ts - start_date).days for ts in timestamps]
        
        # Simple clustering basado en densidad (simulación)
        # En una implementación real, usaríamos DBSCAN o similar
        clusters = {}
        cluster_id = 0
        
        # Umbral para considerar dos eventos en el mismo cluster (días)
        threshold = 30
        
        for i, time in enumerate(numeric_times):
            # Buscar si este evento pertenece a un cluster existente
            assigned = False
            for cid, cluster_times in clusters.items():
                # Verificar si está cerca de algún evento en este cluster
                for cluster_time in cluster_times:
                    if abs(time - cluster_time) < threshold:
                        clusters[cid].append(time)
                        assigned = True
                        break
                
                if assigned:
                    break
            
            # Si no se asignó a ningún cluster, crear uno nuevo
            if not assigned:
                clusters[cluster_id] = [time]
                cluster_id += 1
        
        return clusters

class CosmicEvolutionCorrelator:
    """
    Clase principal que orquesta el análisis de correlaciones entre eventos cósmicos y evolutivos
    """
    
    def __init__(self):
        self.ftrt_calculator = PlanetaryTidalForceEngine()
        self.paleomag_database = GeomagneticHistoryAPI()
        self.fossil_parser = PaleontologicalRecordParser()
        self.genome_clock = MolecularDivergenceTimer()
        self.statistical_analyzer = StatisticalAnalyzer()
        
        logger.info("CosmicEvolutionCorrelator initialized")
    
    def correlate_events(self, start_date: datetime, end_date: datetime) -> Dict:
        """
        Realiza la correlación completa entre eventos cósmicos y evolutivos
        """
        logger.info(f"Starting correlation analysis from {start_date} to {end_date}")
        
        # Obtener eventos cósmicos
        ftrt_peaks = self.ftrt_calculator.find_peaks(start_date, end_date)
        geomag_minima = self.paleomag_database.get_field_weaknesses(start_date, end_date)
        
        # Combinar todos los eventos cósmicos
        cosmic_events = ftrt_peaks + geomag_minima
        
        # Obtener eventos evolutivos
        speciation_events = self.fossil_parser.identify_radiations(start_date, end_date)
        
        # Realizar análisis estadístico
        correlation_results = self.statistical_analyzer.cross_correlation(
            cosmic_events, speciation_events
        )
        
        # Encontrar la correlación más significativa
        best_correlation = None
        if correlation_results:
            best_correlation = max(
                correlation_results, 
                key=lambda x: abs(x.correlation_coefficient) if x.significant else 0
            )
        
        # Agrupar eventos en clusters temporales
        cosmic_clusters = self.statistical_analyzer.time_series_clustering(cosmic_events)
        evolutionary_clusters = self.statistical_analyzer.time_series_clustering(
            [CosmicEvent(
                timestamp=event.timestamp,
                event_type=event.event_type,
                magnitude=event.magnitude,
                duration=timedelta(days=1),
                description=event.description
            ) for event in speciation_events]
        )
        
        # Preparar resultados
        results = {
            'cosmic_events': [
                {
                    'timestamp': event.timestamp.isoformat(),
                    'type': event.event_type,
                    'magnitude': event.magnitude,
                    'duration_days': event.duration.days,
                    'description': event.description
                }
                for event in cosmic_events
            ],
            'evolutionary_events': [
                {
                    'timestamp': event.timestamp.isoformat(),
                    'type': event.event_type,
                    'magnitude': event.magnitude,
                    'affected_taxa': event.affected_taxa,
                    'description': event.description
                }
                for event in speciation_events
            ],
            'correlation_results': [
                {
                    'correlation_coefficient': result.correlation_coefficient,
                    'p_value': result.p_value,
                    'time_lag_days': result.time_lag.days,
                    'confidence_interval': result.confidence_interval,
                    'significant': result.significant
                }
                for result in correlation_results
            ],
            'best_correlation': {
                'correlation_coefficient': best_correlation.correlation_coefficient,
                'p_value': best_correlation.p_value,
                'time_lag_days': best_correlation.time_lag.days,
                'significant': best_correlation.significant
            } if best_correlation else None,
            'cosmic_clusters': cosmic_clusters,
            'evolutionary_clusters': evolutionary_clusters
        }
        
        logger.info("Correlation analysis completed")
        return results
