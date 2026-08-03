"""
Atmospheric Complexity Framework (ACF)

Atmosphere-Ocean Physics Coupling Module (Phase 4)
(Wind Stress Tau = rho_air * Cd * V², Sensible & Latent Heat Fluxes Q_lh = rho * L_v * C_e * V * dq)
"""



class AtmosphereOceanCouplingEngine:
    """
    Moteur de calcul des flux d'échange quantité de mouvement et chaleur entre l'atmosphère et l'océan.
    """

    @staticmethod
    def momentum_flux_tau_n_m2(wind_speed_10m_ms: float, air_density: float = 1.225, drag_coefficient: float = 0.0013) -> float:
        """Calcul de la tension du vent sur la surface océanique Tau = rho_air * Cd * V² (N/m²)."""
        return air_density * drag_coefficient * (wind_speed_10m_ms ** 2)

    @staticmethod
    def latent_heat_flux_w_m2(wind_speed_ms: float, q_sea: float, q_air: float, air_density: float = 1.225) -> float:
        """Calcul du flux de chaleur latente d'évapotranspiration Q_lh (W/m²)."""
        lv_j_kg = 2.5e6  # Chaleur latente de vaporisation
        ce_coeff = 0.0012
        dq = max(0.0, q_sea - q_air)
        return air_density * lv_j_kg * ce_coeff * wind_speed_ms * dq
