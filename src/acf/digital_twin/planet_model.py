"""
Atmospheric Complexity Framework (ACF)

Planet Model Representation Module
"""

from typing import Any


class PlanetModel:
    """Modèle physique unifié de la planète Terre."""

    @classmethod
    def get_planet_parameters(cls) -> dict[str, Any]:
        return {"planet": "Earth", "radius_km": 6371.0, "gravity_m_s2": 9.80665, "status": "MODEL_VALID"}
