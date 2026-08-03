"""
Atmospheric Complexity Framework (ACF)

Soil Hydrology & Groundwater Flow Module (Phases 5 & 6)
(Soil Moisture, Field Capacity, Wilting Point, Darcy's Law q = -K * dh/dl, Aquifers)
"""

from typing import Any, Dict


class SoilHydrologyEngine:
    """
    Moteur de physique de l'humidité du sol, capacité au champ et point de flétrissement.
    """

    @staticmethod
    def soil_water_status(moisture_pct: float, field_capacity_pct: float = 30.0, wilting_point_pct: float = 12.0) -> Dict[str, Any]:
        """Évalue l'état de l'eau dans le sol (Ressource en eau disponible pour les plantes)."""
        if moisture_pct <= wilting_point_pct:
            status = "Point de Flétrissement Atteint (Sécheresse Agricole)"
            available_water_pct = 0.0
        elif moisture_pct >= field_capacity_pct:
            status = "Capacité au Champ Rassie (Saturation / Sursaturation)"
            available_water_pct = 100.0
        else:
            available_water_pct = ((moisture_pct - wilting_point_pct) / (field_capacity_pct - wilting_point_pct)) * 100.0
            status = "Humidité Disponible Utilisable"

        return {
            "moisture_pct": moisture_pct,
            "field_capacity_pct": field_capacity_pct,
            "wilting_point_pct": wilting_point_pct,
            "available_water_pct": round(available_water_pct, 1),
            "status": status,
        }


class GroundwaterEngine:
    """
    Moteur d'écoulement souterrain dans les aquifères (Loi de Darcy & Hydrogéologie).
    """

    @staticmethod
    def darcy_flux_m_s(hydraulic_conductivity_m_s: float, hydraulic_gradient_dh_dl: float) -> float:
        """Calcul du flux de Darcy q = - K * (dh / dl) (m/s)."""
        return -hydraulic_conductivity_m_s * hydraulic_gradient_dh_dl

    @classmethod
    def evaluate_aquifer_recharge(cls, rainfall_mm: float, evapotranspiration_mm: float, soil_percolation_rate: float = 0.15) -> float:
        """Estimation de la recharge des nappes phréatiques (mm/jour)."""
        net_water = max(0.0, rainfall_mm - evapotranspiration_mm)
        return net_water * soil_percolation_rate
