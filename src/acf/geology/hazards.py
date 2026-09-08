"""
Atmospheric Complexity Framework (ACF)

Global Geological Natural Hazards & Multi-Risk Assessment Module (Phase 14)
(Earthquakes, Tsunamis, Landslides, Liquefaction)

NOTE (correction — scope overclaim, found during the post-model4d
audit, 2026-09-06): this header used to also list "Volcanoes" and
"Subsidence" - evaluate_multi_hazard_risk() below takes no volcanic or
subsidence-related input at all and never assesses either hazard, no
matter what is passed in. Corrected to name only the 4 hazard types
this module's one function genuinely evaluates (earthquake shaking/
liquefaction, tsunami, earthquake-induced landslides), rather than
leaving a broader claim than the code delivers.
"""

from typing import Any


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
    ) -> dict[str, Any]:
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

        severity = (
            "CRITICAL / MULTI-HAZARD WARNING"
            if len(hazards) >= 3
            else ("HIGH RISK" if len(hazards) >= 1 else "LOW HAZARD")
        )

        return {
            "earthquake_magnitude_mw": earthquake_mw,
            "identified_geological_hazards": hazards,
            "multi_hazard_severity": severity,
        }
