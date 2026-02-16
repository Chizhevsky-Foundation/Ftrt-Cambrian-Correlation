from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
from enum import Enum

class CorrelationType(str, Enum):
    PEARSON = "pearson"
    SPEARMAN = "spearman"
    KENDALL = "kendall"

class CorrelationResult(BaseModel):
    """
    Model for correlation results
    """
    correlation_coefficient: float
    p_value: float
    time_lag_days: int
    correlation_type: CorrelationType = CorrelationType.PEARSON
    confidence_interval: Tuple[float, float]
    significant: bool
    sample_size: int

class CorrelationAnalysis(BaseModel):
    """
    Model for a complete correlation analysis
    """
    id: Optional[str] = None
    start_date: datetime
    end_date: datetime
    max_lag_days: int
    correlation_results: List[CorrelationResult]
    best_correlation: Optional[CorrelationResult] = None
    significant_correlations_count: int
    total_correlations_count: int
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Cluster(BaseModel):
    """
    Model for event clusters
    """
    id: Optional[str] = None
    start_time: datetime
    end_time: datetime
    duration_days: int
    event_count: int
    event_types: List[str]
    significance: Optional[float] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ClusteringResult(BaseModel):
    """
    Model for clustering results
    """
    cosmic_clusters: List[Cluster]
    evolutionary_clusters: List[Cluster]
    noise_points: int
    total_events: int

class CorrelationSummary(BaseModel):
    """
    Model for correlation summary
    """
    analysis_id: Optional[str] = None
    period: Tuple[datetime, datetime]
    cosmic_events_count: int
    evolutionary_events_count: int
    best_correlation: Optional[CorrelationResult] = None
    significant_correlations_count: int
    cosmic_clusters_count: int
    evolutionary_clusters_count: int
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
