"""
Atmospheric Complexity Framework (ACF)

Tsunami Wave Dynamics & Inundation Warning Engine Module (Phase 9)
(Celerity C = sqrt(g*d), Green's Law Coastal Amplification H2 = H1*(d1/d2)^(1/4), Tsunami Warnings)
"""

import math
from typing import Any


class TsunamiForecastEngine:
    """
    Moteur de prévision et de calcul de la célérité et du run-up côtoyer des tsunamis.
    """

    @staticmethod
    def tsunami_wave_celerity_m_s(water_depth_m: float) -> float:
        """Calcul de la vitesse de propagation d'un tsunami C = sqrt(g * d) (m/s)."""
        g = 9.80665
        return math.sqrt(max(0.0, g * water_depth_m))

    @staticmethod
    def greens_law_coastal_amplification(
        h1_open_ocean_m: float, d1_open_ocean_m: float, d2_coastal_depth_m: float
    ) -> float:
        """Loi de Green pour l'amplification de la hauteur de vague à l'approche de la côte H2 = H1 * (d1/d2)^(1/4)."""
        if d2_coastal_depth_m <= 0:
            return h1_open_ocean_m
        return h1_open_ocean_m * ((d1_open_ocean_m / d2_coastal_depth_m) ** 0.25)

    def evaluate_tsunami_hazard(
        self,
        earthquake_mw: float,
        fault_depth_km: float,
        distance_to_coast_km: float,
        ocean_depth_m: float = 4000.0,
    ) -> dict[str, Any]:
        """Évalue le risque de tsunami généré par un séisme sous-marin."""
        is_tsunamigenic = (earthquake_mw >= 7.0) and (fault_depth_km <= 100.0)

        c_ms = self.tsunami_wave_celerity_m_s(ocean_depth_m)
        c_km_h = c_ms * 3.6
        eta_arrival_minutes = (distance_to_coast_km / (c_ms / 1000.0)) / 60.0

        if not is_tsunamigenic:
            return {
                "tsunami_risk": "LOW / NO TSUNAMI GENERATED",
                "celerity_km_h": round(c_km_h, 1),
                "warning_level": "GREEN",
            }

        open_ocean_height_m = 0.05 * (10.0 ** (0.5 * (earthquake_mw - 7.0)))
        coastal_height_m = self.greens_law_coastal_amplification(open_ocean_height_m, ocean_depth_m, 10.0)

        warning_level = "RED / TSUNAMI WARNING" if coastal_height_m >= 1.0 else "ORANGE / TSUNAMI ADVISORY"

        return {
            "tsunami_risk": "HIGH / TSUNAMIGENIC MEGATHRUST EVENT",
            "open_ocean_wave_height_m": round(open_ocean_height_m, 2),
            "estimated_coastal_runup_m": round(coastal_height_m, 2),
            "celerity_km_h": round(c_km_h, 1),
            "estimated_arrival_minutes": round(eta_arrival_minutes, 1),
            "warning_level": warning_level,
        }
