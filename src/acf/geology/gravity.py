"""
Atmospheric Complexity Framework (ACF)

Gravimetry, Bouguer Anomalies & Satellite Gravity Engine Module (Phase 12)
(Free Air Anomaly, Bouguer Anomaly, Newton Gravity, GOCE / GRACE Gravity Field)
"""

import math
from typing import Dict


class GravityEngine:
    """
    Moteur de calculs gravimétriques et d'anomalies de pesanteur (Bouguer, Free-Air).
    """

    G_CONST = 6.67430e-11  # m³/(kg.s²)
    EARTH_MASS_KG = 5.972e24

    @classmethod
    def theoretical_gravity_somigliana(cls, latitude_deg: float) -> float:
        """Calcul de la pesanteur théorique de référence sur l'ellipsoïde WGS84 (Somigliana)."""
        rad = math.radians(latitude_deg)
        g_eq = 9.7803253359
        k = 0.00193185265241
        e2 = 0.00669437999014
        sin2 = (math.sin(rad)) ** 2

        return g_eq * (1.0 + k * sin2) / math.sqrt(1.0 - e2 * sin2)

    @classmethod
    def bouguer_gravity_anomaly_mgal(
        cls,
        observed_g_mgal: float,
        latitude_deg: float,
        elevation_m: float,
        rock_density_g_cm3: float = 2.67,
    ) -> Dict[str, float]:
        """
        Calcul de l'Anomalie de Bouguer Delta g_B (en mGal).
        Delta g_FA = g_obs - g_ref + 0.3086 * h (Anomalie à l'air libre).
        Delta g_B = Delta g_FA - 0.04193 * rho * h (Anomalie de Bouguer complète).
        """
        g_ref_mgal = cls.theoretical_gravity_somigliana(latitude_deg) * 100000.0  # m/s² -> mGal
        free_air_corr = 0.3086 * elevation_m
        free_air_anomaly = observed_g_mgal - g_ref_mgal + free_air_corr

        bouguer_corr = 0.04193 * rock_density_g_cm3 * elevation_m
        bouguer_anomaly = free_air_anomaly - bouguer_corr

        return {
            "theoretical_g_mgal": round(g_ref_mgal, 2),
            "free_air_anomaly_mgal": round(free_air_anomaly, 2),
            "bouguer_anomaly_mgal": round(bouguer_anomaly, 2),
        }
