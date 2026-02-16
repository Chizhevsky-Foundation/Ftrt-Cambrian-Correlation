from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class EvolutionaryEventType(str, Enum):
    SPECIATION = "speciation"
    EXTINCTION = "extinction"
    MUTATION_BURST = "mutation_burst"
    ADAPTIVE_RADIATION = "adaptive_radiation"

class EvolutionaryEvent(BaseModel):
    """
    Model for evolutionary events
    """
    id: Optional[str] = None
    timestamp: datetime
    event_type: EvolutionaryEventType
    magnitude: float
    affected_taxa: List[str]
    description: str
    location: Optional[str] = None
    environment: Optional[str] = None
    metadata: Optional[dict] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SpeciationEvent(EvolutionaryEvent):
    """
    Model for speciation events
    """
    event_type: EvolutionaryEventType = EvolutionaryEventType.SPECIATION
    parent_taxon: Optional[str] = None
    new_taxon: Optional[str] = None
    speciation_mechanism: Optional[str] = None

class ExtinctionEvent(EvolutionaryEvent):
    """
    Model for extinction events
    """
    event_type: EvolutionaryEventType = EvolutionaryEventType.EXTINCTION
    extinction_rate: float
    affected_percentage: Optional[float] = None
    recovery_time: Optional[int] = None  # In million years

class MutationBurstEvent(EvolutionaryEvent):
    """
    Model for mutation burst events
    """
    event_type: EvolutionaryEventType = EvolutionaryEventType.MUTATION_BURST
    mutation_rate: float
    affected_genes: Optional[List[str]] = None
    mutagenic_factor: Optional[str] = None

class AdaptiveRadiationEvent(EvolutionaryEvent):
    """
    Model for adaptive radiation events
    """
    event_type: EvolutionaryEventType = EvolutionaryEventType.ADAPTIVE_RADIATION
    ecological_niche: Optional[str] = None
    morphological_innovation: Optional[str] = None
    key_innovation: Optional[str] = None
