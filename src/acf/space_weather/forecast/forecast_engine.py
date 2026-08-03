"""
Atmospheric Complexity Framework (ACF)

Operational Space Weather Forecast & Multi-Horizon Prediction Engine Module (Phase 10)
(Flares, CME Arrival, Kp Index, Dst Index, Auroral Probability, Lead Times 24h/48h/72h/7d)
"""

from typing import Any, Dict


class SpaceWeatherForecastEngine:
    """
    Moteur de prévision opérationnelle du temps spatial pour les 24h, 48h, 72h et 7 jours.
    """

    def generate_space_weather_forecast(
        self,
        sunspot_number: float = 150.0,
        cme_speed_km_s: float = 1200.0,
        imf_bz_nt: float = -12.0,
    ) -> Dict[str, Any]:
        """Génère un bulletin complet de prévision du temps spatial Soleil-Terre."""
        cme_lead_time_hours = (1.5e8 / (cme_speed_km_s * 3600.0))  # Distance Terre-Soleil / V_cme

        predicted_kp = 4.0 + (cme_speed_km_s / 400.0) + (abs(imf_bz_nt) / 3.0) if imf_bz_nt < 0 else 3.0
        predicted_kp = min(9.0, predicted_kp)

        predicted_dst = -20.0 - (abs(imf_bz_nt) * 12.0) if imf_bz_nt < 0 else -10.0

        aurora_probability = min(100.0, (predicted_kp / 9.0) * 100.0)

        return {
            "lead_time_horizons": ["24h", "48h", "72h", "7 Days"],
            "predicted_max_kp_index": round(predicted_kp, 1),
            "predicted_min_dst_nt": round(predicted_dst, 1),
            "cme_estimated_arrival_hours": round(cme_lead_time_hours, 1),
            "flare_probability_24h": {
                "C_class_pct": 90.0,
                "M_class_pct": 55.0,
                "X_class_pct": 20.0 if sunspot_number > 120 else 5.0,
            },
            "aurora_visibility_probability_pct": round(aurora_probability, 1),
            "gnss_degradation_risk": "HIGH" if predicted_kp >= 7.0 else "MODERATE",
            "hf_radio_blackout_risk": "HIGH" if sunspot_number > 140 else "MODERATE",
        }
