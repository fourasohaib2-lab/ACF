"""
Atmospheric Complexity Framework (ACF)

Operational Flood Forecasting & Risk Inundation Engine Module (Phase 4)
(River Floods, Flash Floods, Hydrographs, Return Period T_return, Peak Discharge Qp)
"""

from typing import Any


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
        basin_area_km2: float | None = None,
    ) -> dict[str, Any]:
        """
        Évalue le risque de crue éclair (Flash Flood) dans un sous-bassin versant réactif.

        NOTE (correction): estimated_peak_discharge_m3_s used to be
        precip_3h_mm * 12.5 with no basin_area involved at all - a 1
        km² sub-basin and a 10,000 km² one hit by the identical 3h
        rainfall got the identical "peak discharge in m3/s" prediction,
        which is dimensionally impossible: converting a rainfall depth
        (mm) into a volumetric flow rate (m3/s) requires the drainage
        area, and peak discharge genuinely scales with it. Fixed to use
        the Rational Method Qp = C * i * A / 3.6 (i in mm/h, A in km²,
        C dimensionless runoff coefficient, Qp in m3/s - the 1/3.6
        factor converts mm*km2/h to m3/s), a standard textbook
        estimator for small/reactive watersheds. C is taken as
        soil_saturation_pct/100 (a saturated soil produces more
        runoff, consistent with flash_index's existing use of the same
        ratio) capped at 1.0. Returns None when basin_area_km2 is not
        supplied rather than a fabricated area-independent number.
        """
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

        if basin_area_km2 is not None and basin_area_km2 > 0:
            runoff_coefficient = min(1.0, soil_saturation_pct / 100.0)
            intensity_mm_h = precip_3h_mm / 3.0
            peak_discharge_m3_s = round(runoff_coefficient * intensity_mm_h * basin_area_km2 / 3.6, 1)
        else:
            peak_discharge_m3_s = None

        return {
            "flash_flood_index": round(flash_index, 2),
            "risk_level": risk,
            "alert_color": color,
            "estimated_peak_discharge_m3_s": peak_discharge_m3_s,
            "expected_lead_time_hours": max(0.5, 4.0 - basin_slope_m_km / 5.0),
        }
