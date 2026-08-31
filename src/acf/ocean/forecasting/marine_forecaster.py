"""
Atmospheric Complexity Framework (ACF)

Operational Marine Forecasting Engine Module (Phase 3 & Phase 7)
(Sea State Douglas Scale, Swell, Combined Seas, Storm Surge, Coastal Flooding, Rip Currents)
"""

import math
from typing import Any


class MarineForecastEngine:
    """
    Moteur de prévision de l'état de la mer, des surcotes de tempête et des risques côtiers.
    """

    @staticmethod
    def douglas_sea_state(hs_m: float) -> dict[str, str]:
        """Convertit la hauteur significative Hs en échelle de Douglas pour l'état de la mer."""
        if hs_m < 0.1:
            code = "0 - Calm (glassy)"
        elif hs_m < 0.5:
            code = "1 - Calm (rippled)"
        elif hs_m < 1.25:
            code = "2 - Smooth"
        elif hs_m < 2.5:
            code = "3 - Slight"
        elif hs_m < 4.0:
            code = "4 - Moderate"
        elif hs_m < 6.0:
            code = "5 - Rough"
        elif hs_m < 9.0:
            code = "6 - Very Rough"
        elif hs_m < 14.0:
            code = "7 - High"
        else:
            code = "8 - Very High / Phenomenal"

        return {"douglas_code": code, "hs_m": str(round(hs_m, 2))}

    def generate_marine_forecast(
        self,
        wind_speed_kts: float,
        fetch_km: float = 200.0,
        swell_hs_m: float = 2.0,
    ) -> dict[str, Any]:
        """Génère un bulletin complet d'état de mer et de sécurité maritime."""
        wind_ms = wind_speed_kts * 0.514444
        wind_wave_hs = 0.02 * wind_ms * math.sqrt(fetch_km)
        combined_hs = math.sqrt((wind_wave_hs**2) + (swell_hs_m**2))

        sea_state = self.douglas_sea_state(combined_hs)

        rip_risk = "HIGH" if combined_hs > 2.5 else "MODERATE"
        surge_m = 0.05 * (wind_ms**1.5) / 10.0

        return {
            "sea_state": sea_state["douglas_code"],
            "wind_wave_height_m": round(wind_wave_hs, 2),
            "primary_swell_height_m": round(swell_hs_m, 2),
            "combined_significant_wave_height_m": round(combined_hs, 2),
            "estimated_storm_surge_m": round(surge_m, 2),
            "rip_current_risk": rip_risk,
            "marine_warnings": ["High Surf Advisory"] if combined_hs > 3.0 else [],
        }
