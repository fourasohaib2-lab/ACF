"""
Atmospheric Complexity Framework (ACF)

Operational Space Weather Alert & Space Hazard Warning Engine Module (Phase 11)
(Solar Flare Alert, CME Alert, Geomagnetic G1-G5, Radio R1-R5, Radiation S1-S5 Alerts)
"""

from typing import Any


class SpaceWeatherAlertEngine:
    """
    Moteur de génération et de diffusion des bulletins d'alerte météo-spatiale (NOAA SWPC / OACI).
    """

    @classmethod
    def evaluate_system_alerts(
        self,
        kp_index: float,
        xray_flux_w_m2: float,
        proton_flux_gt_10mev: float = 10.0,
    ) -> list[dict[str, Any]]:
        """Génère les alertes temps spatial actives pour les opérateurs réseaux, satellites et aviation."""
        alerts = []

        # 1. Alerte Tempête Géomagnétique (G1-G5)
        if kp_index >= 5.0:
            severity = "RED" if kp_index >= 8.0 else ("ORANGE" if kp_index >= 7.0 else "YELLOW")
            alerts.append(
                {
                    "alert_type": "GEOMAGNETIC_STORM_WARNING",
                    "severity": severity,
                    "kp_index": kp_index,
                    "affected_systems": ["Power Grids", "Satellites", "HF Comms", "GNSS / GPS Navigation"],
                    "recommended_action": "Activer la surveillance des transformateurs de puissance et orienter les panneaux solaires satellites.",
                }
            )

        # 2. Alerte Éruption Solaire X-Ray (R1-R5)
        if xray_flux_w_m2 >= 1e-4:
            alerts.append(
                {
                    "alert_type": "SOLAR_FLARE_XRAY_ALERT",
                    "severity": "RED",
                    "xray_flux_w_m2": xray_flux_w_m2,
                    "affected_systems": ["HF Aviation Comms", "Over-The-Horizon Radar"],
                    "recommended_action": "Bascule des liaisons HF aéronautiques vers les fréquences de secours et SATCOM.",
                }
            )

        # 3. Alerte Tempête de Radiation Solaire (S1-S5)
        if proton_flux_gt_10mev >= 1e3:
            alerts.append(
                {
                    "alert_type": "SOLAR_RADIATION_STORM_WARNING",
                    "severity": "RED",
                    "proton_flux_pfu": proton_flux_gt_10mev,
                    "affected_systems": ["Polar Aviation Routes", "Astronaut EVA", "Satellite Star Trackers"],
                    "recommended_action": "Déroutement des vols polaires vers des latitudes plus basses et mise en sécurité des instruments spatiaux.",
                }
            )

        return alerts
