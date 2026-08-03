"""
Moist Atmosphere Physics Module (Clausius-Clapeyron, Specific Humidity, RH)
"""

import math


class MoistAtmospherePhysics:
    """Physique de l'atmosphère humide et équation de Clausius-Clapeyron."""

    @classmethod
    def saturation_vapor_pressure(cls, temp_k: float) -> float:
        """Formule de Tetens pour la pression de vapeur saturante e_sat (Pa)."""
        temp_c = temp_k - 273.15
        e_sat_hpa = 6.1078 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
        return e_sat_hpa * 100.0  # Pa
