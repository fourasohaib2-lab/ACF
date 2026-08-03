"""
Atmospheric Complexity Framework (ACF)

Global Geological Natural Hazards & Multi-Risk Assessment Module (Phase 14)
(Earthquakes, Tsunamis, Volcanoes, Landslides, Liquefaction, Subsidence)
"""

from typing import Any, Dict


class HazardEngine:
    """
    Moteur d'évaluation multi-risques géologiques et d'impacts environnementaux.
    """

    @classmethod
    def evaluate_multi_hazard_risk(
        cls,
        earthquake_mw: float,
        coastal_distance_km: float,
        slope_angle_deg: float,
    ) -> Dict[str, Any]:
        """Évalue les risques géologiques combinés (Séisme + Tsunami + Glissement de terrain + Liquéfaction)."""
        hazards = []

        if earthquake_mw >= 6.0:
            hazards.append("Strong Ground Shaking (PGA > 0.2g)")
            if earthquake_mw >= 7.0:
                hazards.append("Soil Liquefaction in Unconsolidated Sediments")

        if earthquake_mw >= 7.0 and coastal_distance_km < 50.0:
            hazards.append("Tsunami Wave Inundation Hazard")

        if slope_angle_deg >= 25.0 and earthquake_mw >= 5.5:
            hazards.append("Earthquake-Induced Landslides and Rockfalls")

        severity = "CRITICAL / MULTI-HAZARD WARNING" if len(hazards) >= 3 else ("HIGH RISK" if len(hazards) >= 1 else "LOW HAZARD")

        return {
            "earthquake_magnitude_mw": earthquake_mw,
            "identified_geological_hazards": hazards,
            "multi_hazard_severity": severity,
        }
