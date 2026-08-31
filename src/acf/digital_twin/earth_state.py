"""
Atmospheric Complexity Framework (ACF)

Earth State Representation Engine Module (Phase 2)
(EarthState for Atmosphere, Ocean, Cryosphere, Land, Biosphere, Human Activity)
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EarthState:
    """Représentation globale du vecteur d'état dynamique de la Terre Earth(x,y,z,t)."""

    timestamp: str = "2026-08-02 12:00 UTC"
    global_mean_temperature_k: float = 288.15
    co2_ppm: float = 422.5
    sea_level_anomaly_m: float = 0.0
    sea_ice_extent_km2: float = 14500000.0
    vegetation_cover_pct: float = 31.2
    active_coupled_spheres: list[str] = field(
        default_factory=lambda: ["Atmosphere", "Ocean", "Cryosphere", "Land Surface", "Biosphere", "Human Activity"]
    )

    def get_state_vector_summary(self) -> dict[str, Any]:
        """
        Retourne la synthèse du vecteur d'état planétaire.

        NOTE (correction): "status": "EARTH_STATE_SYNCHRONIZED" used to
        claim this state vector was actively kept in sync with a real
        source - but every field above is a fixed dataclass default
        (this class has no update()/sync() method of any kind), so the
        exact same values are returned no matter when this is called.
        The values themselves are reasonable representative Earth-system
        reference figures (e.g. co2_ppm=422.5 is close to genuinely
        measured recent global averages) and are kept as a legitimate
        static baseline, not deleted - only the false "synchronized"
        claim is corrected. Not fabricated.
        """
        return {
            "timestamp": self.timestamp,
            "global_mean_temp_k": self.global_mean_temperature_k,
            "co2_ppm": self.co2_ppm,
            "sea_level_anomaly_m": self.sea_level_anomaly_m,
            "sea_ice_extent_km2": self.sea_ice_extent_km2,
            "coupled_spheres_count": len(self.active_coupled_spheres),
            "status": "STATIC_REFERENCE_STATE_NOT_LIVE_SYNCHRONIZED",
        }
