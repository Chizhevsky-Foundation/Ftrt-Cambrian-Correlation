from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class CosmicEventType(str, Enum):
    FTRT_PEAK = "ftrt_peak"
    GEOMAGNETIC_WEAKNESS = "geomagnetic_weakness"
    SOLAR_STORM = "solar_storm"
    COSMIC_RAY_FLUX = "cosmic_ray_flux"

class CosmicEvent(BaseModel):
    """
    Model for cosmic events
    """
    id: Optional[str] = None
    timestamp: datetime
    event_type: CosmicEventType
    magnitude: float
    duration_days: int
    description: str
    location: Optional[str] = None
    metadata: Optional[dict] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FTRTEvent(CosmicEvent):
    """
    Model for FTRT (Planetary Tidal Force) events
    """
    event_type: CosmicEventType = CosmicEventType.FTRT_PEAK
    planetary_configuration: Optional[List[str]] = None
    tidal_force_value: float
    
class GeomagneticEvent(CosmicEvent):
    """
    Model for geomagnetic events
    """
    event_type: CosmicEventType = CosmicEventType.GEOMAGNETIC_WEAKNESS
    field_intensity: float
    location: str  # Required for geomagnetic events
    
class SolarStormEvent(CosmicEvent):
    """
    Model for solar storm events
    """
    event_type: CosmicEventType = CosmicEventType.SOLAR_STORM
    flare_class: Optional[str] = None
    cme_speed: Optional[float] = None
    
class CosmicRayEvent(CosmicEvent):
    """
    Model for cosmic ray flux events
    """
    event_type: CosmicEventType = CosmicEventType.COSMIC_RAY_FLUX
    energy_range: Optional[str] = None
    flux_value: float
