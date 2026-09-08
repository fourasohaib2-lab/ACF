"""
Atmospheric Complexity Framework (ACF)

Seismic Waves Hydrodynamics & Elastic Wave Propagation Module (Phase 5)
(P Waves Vp = sqrt((K + 4/3 mu)/rho), S Waves Vs = sqrt(mu/rho), Rayleigh/Love Waves, Snell's Law)
"""

import math


class SeismicWaveEngine:
    """
    Moteur de vitesse de propagation des ondes sismiques P, S et de surface (Rayleigh, Love).
    """

    @staticmethod
    def p_wave_velocity_m_s(bulk_modulus_k_pa: float, shear_modulus_mu_pa: float, density_kg_m3: float) -> float:
        """Calcul de la vitesse des ondes P Vp = sqrt((K + (4/3)*mu) / rho) (m/s)."""
        if density_kg_m3 <= 0:
            return 0.0
        val = (bulk_modulus_k_pa + (4.0 / 3.0) * shear_modulus_mu_pa) / density_kg_m3
        return math.sqrt(max(0.0, val))

    @staticmethod
    def s_wave_velocity_m_s(shear_modulus_mu_pa: float, density_kg_m3: float) -> float:
        """Calcul de la vitesse des ondes S Vs = sqrt(mu / rho) (m/s)."""
        if density_kg_m3 <= 0:
            return 0.0
        return math.sqrt(max(0.0, shear_modulus_mu_pa / density_kg_m3))

    @staticmethod
    def rayleigh_wave_velocity_m_s(vs_m_s: float) -> float:
        """Calcul approximatif de la vitesse des ondes de Rayleigh V_R ~ 0.92 * Vs."""
        return 0.92 * vs_m_s

    @staticmethod
    def snell_law_refraction_angle(incidence_angle_deg: float, v1: float, v2: float) -> float:
        """Loi de Snell-Descartes pour les rais sismiques : sin(i1)/v1 = sin(i2)/v2."""
        sin_i2 = (math.sin(math.radians(incidence_angle_deg)) / v1) * v2
        if abs(sin_i2) > 1.0:
            return 90.0  # Réflexion totale critique
        return math.degrees(math.asin(sin_i2))

    @classmethod
    def travel_time_p_and_s(cls, distance_km: float, vp_km_s: float = 6.0, vs_km_s: float = 3.5) -> dict[str, float]:
        """Calcul des temps de parcours des ondes P et S et du délai S-P."""
        t_p = distance_km / vp_km_s
        t_s = distance_km / vs_km_s
        delta_t = t_s - t_p

        return {
            "p_arrival_seconds": round(t_p, 2),
            "s_arrival_seconds": round(t_s, 2),
            "s_minus_p_delay_seconds": round(delta_t, 2),
        }
