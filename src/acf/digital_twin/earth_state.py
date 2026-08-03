"""
Atmospheric Complexity Framework (ACF)

Earth State Representation Engine Module (Phase 2)
(EarthState for Atmosphere, Ocean, Cryosphere, Land, Biosphere, Human Activity)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class EarthState:
    """Représentation globale du vecteur d'état dynamique de la Terre Earth(x,y,z,t)."""

    timestamp: str = "2026-08-02 12:00 UTC"
    global_mean_temperature_k: float = 288.15
    co2_ppm: float = 422.5
    sea_level_anomaly_m: float = 0.0
    sea_ice_extent_km2: float = 14500000.0
    vegetation_cover_pct: float = 31.2
    active_coupled_spheres: List[str] = field(default_factory=lambda: [
        "Atmosphere", "Ocean", "Cryosphere", "Land Surface", "Biosphere", "Human Activity"
    ])

    def get_state_vector_summary(self) -> Dict[str, Any]:
        """Retourne la synthèse du vecteur d'état planétaire."""
        return {
            "timestamp": self.timestamp,
            "global_mean_temp_k": self.global_mean_temperature_k,
            "co2_ppm": self.co2_ppm,
            "sea_level_anomaly_m": self.sea_level_anomaly_m,
            "sea_ice_extent_km2": self.sea_ice_extent_km2,
            "coupled_spheres_count": len(self.active_coupled_spheres),
            "status": "EARTH_STATE_SYNCHRONIZED",
        }
