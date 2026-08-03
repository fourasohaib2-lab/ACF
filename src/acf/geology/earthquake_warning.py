"""
Atmospheric Complexity Framework (ACF)

Earthquake Early Warning System (EEWS) Module (Phase 6)
(P-wave Detection, S-wave Lead Time Warning, PGA Ground Motion, Exposed Population)
"""

from typing import Any, Dict


class EarthquakeWarningEngine:
    """
    Moteur d'alerte précoce aux séismes (EEWS) basé sur le délai de détection des ondes P.
    """

    def calculate_warning_lead_time(
        self,
        distance_epicenter_km: float,
        detection_delay_seconds: float = 3.0,
        vp_km_s: float = 6.0,
        vs_km_s: float = 3.5,
    ) -> Dict[str, Any]:
        """Calcul du délai d'avertissement utile avant l'arrivée des ondes S destructrices."""
        t_p = distance_epicenter_km / vp_km_s
        t_s = distance_epicenter_km / vs_km_s

        lead_time = max(0.0, t_s - (t_p + detection_delay_seconds))

        if lead_time > 15.0:
            alert = "EARLY WARNING ACTIVE / IMPACT HIGH"
            color = "RED"
        elif lead_time > 5.0:
            alert = "EARLY WARNING ACTIVE / IMPACT MODERATE"
            color = "ORANGE"
        else:
            alert = "BLIND ZONE / IMMINENT SHAKING"
            color = "YELLOW"

        return {
            "distance_epicenter_km": distance_epicenter_km,
            "p_arrival_seconds": round(t_p, 1),
            "s_arrival_seconds": round(t_s, 1),
            "warning_lead_time_seconds": round(lead_time, 1),
            "alert_status": alert,
            "alert_color": color,
        }
