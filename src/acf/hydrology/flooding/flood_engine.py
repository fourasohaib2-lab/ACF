"""
Atmospheric Complexity Framework (ACF)

Operational Flood Forecasting & Risk Inundation Engine Module (Phase 4)
(River Floods, Flash Floods, Hydrographs, Return Period T_return, Peak Discharge Qp)
"""

from typing import Any, Dict


class FloodForecastEngine:
    """
    Moteur de prévision opérationnelle des inondations, crues éclair et calcul d'hydrogrammes de pointe.
    """

    @staticmethod
    def return_period_weibull(rank: int, total_years: int) -> float:
        """Calcul de la période de retour T = (N + 1) / m d'une crue selon la formule de Weibull."""
        if rank <= 0:
            return 1.0
        return (total_years + 1.0) / float(rank)

    def evaluate_flash_flood_risk(
        self,
        precip_3h_mm: float,
        soil_saturation_pct: float,
        basin_slope_m_km: float,
    ) -> Dict[str, Any]:
        """Évalue le risque de crue éclair (Flash Flood) dans un sous-bassin versant réactif."""
        flash_index = (precip_3h_mm / 30.0) * (soil_saturation_pct / 100.0) * (1.0 + basin_slope_m_km / 10.0)

        if flash_index > 2.0:
            risk = "CRITICAL / FLASH FLOOD WARNING"
            color = "RED"
        elif flash_index > 1.0:
            risk = "HIGH / FLASH FLOOD WATCH"
            color = "ORANGE"
        else:
            risk = "MODERATE / NORMAL FLOW"
            color = "GREEN"

        return {
            "flash_flood_index": round(flash_index, 2),
            "risk_level": risk,
            "alert_color": color,
            "estimated_peak_discharge_m3_s": round(precip_3h_mm * 12.5, 1),
            "expected_lead_time_hours": max(0.5, 4.0 - basin_slope_m_km / 5.0),
        }
