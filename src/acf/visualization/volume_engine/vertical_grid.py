"""
Atmospheric Complexity Framework (ACF)

Vertical Coordinate & Atmospheric Stratification System Module (Phase 3)
"""

from typing import List


PRESSURE_LEVELS_HPA = [1000, 925, 850, 700, 500, 400, 300, 250, 200, 150, 100, 70, 50, 30, 10]


class VerticalCoordinateSystem:
    """Système de coordonnées verticales (Pression hPa, Sigma Hybride, Eta, Altitude géométrique)."""

    @classmethod
    def get_standard_pressure_levels(cls) -> List[int]:
        return PRESSURE_LEVELS_HPA

    @classmethod
    def get_layer_name_by_altitude(cls, altitude_km: float) -> str:
        if altitude_km < 2.0:
            return "Planetary Boundary Layer (PBL)"
        elif altitude_km < 11.0:
            return "Troposphere"
        elif altitude_km < 13.0:
            return "Tropopause"
        else:
            return "Stratosphere"
