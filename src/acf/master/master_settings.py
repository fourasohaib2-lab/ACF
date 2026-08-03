"""
Atmospheric Complexity Framework (ACF)

Master Settings & Global Configuration Module (Phase 16)
(MasterSettings providing centralized configuration for GPU, MPI, Cloud, Precision, Units, and Logging)
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class MasterSettings:
    """Configuration centralisée unifiée d'ACF Master Framework."""
    active_mode: str = "OPERATIONAL_FULL"
    enable_gpu: bool = True
    enable_mpi: bool = False
    enable_cloud_workers: bool = True
    floating_precision: str = "float64"
    units_system: str = "SI"
    language: str = "en_US"
    logging_level: str = "INFO"
    enabled_subsystems: List[str] = field(default_factory=lambda: [
        "Atmosphere", "Ocean", "Hydrology", "Climate", "Cryosphere",
        "Geology", "SpaceWeather", "PlanetaryDefense", "Geoengineering",
        "DigitalTwin", "AEOS", "EarthIntelligence", "AI"
    ])
