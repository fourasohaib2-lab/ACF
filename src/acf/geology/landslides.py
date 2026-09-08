"""
Atmospheric Complexity Framework (ACF)

Slope Stability, Landslides & Debris Flow Engine Module (Phase 10)
(Factor of Safety FS = (c' + (sigma - u)*tan(phi')) / tau, Soil Saturation Rainfall Trigger)
"""

import math
from typing import Any


class SlopeStabilityEngine:
    """
    Moteur de stabilité des pentes et d'évaluation du risque de glissement de terrain.
    """

    @staticmethod
    def factor_of_safety(
        cohesion_kpa: float,
        normal_stress_kpa: float,
        pore_water_pressure_kpa: float,
        friction_angle_deg: float,
        shear_stress_kpa: float,
    ) -> float:
        """
        Calcul du Facteur de Sécurité FS = (c' + (sigma - u) * tan(phi')) / tau.
        FS < 1.0 : Rupture de pente / Glissement instable.
        FS >= 1.5 : Pente stable.
        """
        if shear_stress_kpa <= 0:
            return 99.0

        effective_normal_stress = max(0.0, normal_stress_kpa - pore_water_pressure_kpa)
        shear_strength = cohesion_kpa + effective_normal_stress * math.tan(math.radians(friction_angle_deg))

        return shear_strength / shear_stress_kpa

    @classmethod
    def evaluate_landslide_trigger_risk(
        cls,
        slope_angle_deg: float,
        rainfall_24h_mm: float,
        soil_saturation_pct: float,
    ) -> dict[str, Any]:
        """Évalue le risque de déclenchement de glissement de terrain suite à de fortes pluies."""
        trigger_index = (slope_angle_deg / 30.0) * (rainfall_24h_mm / 100.0) * (soil_saturation_pct / 100.0)

        if trigger_index > 1.2:
            status = "CRITICAL / HIGH LANDSLIDE & DEBRIS FLOW RISK"
            alert = "RED"
        elif trigger_index > 0.6:
            status = "MODERATE / LANDSLIDE WATCH"
            alert = "ORANGE"
        else:
            status = "LOW RISK / STABLE SLOPE"
            alert = "GREEN"

        return {
            "trigger_index": round(trigger_index, 2),
            "landslide_risk": status,
            "alert_level": alert,
        }
