"""
Atmospheric Complexity Framework (ACF)

Coupled Earth System Interactions Engine Module
(Atmosphere-Ocean, Atmosphere-Cryosphere, Atmosphere-Land, Ocean-Ice, Carbon-Vegetation)
"""

import math


class EarthSystemCoupler:
    """
    Simulateur et évaluateur des flux de couplage entre les composantes du système Terre.
    """

    @staticmethod
    def ocean_atmosphere_momentum_flux(wind_speed_10m: float, rho_air: float = 1.2, cd: float = 0.0013) -> float:
        """Calcul du flux de quantité de mouvement océan-atmosphère tau = rho_a * C_D * V^2 (N/m²)."""
        return rho_air * cd * (wind_speed_10m**2)

    @staticmethod
    def sea_ice_albedo_feedback(
        ice_concentration: float, albedo_ice: float = 0.80, albedo_ocean: float = 0.06
    ) -> float:
        """Calcul de l'albédo moyen effectif d'une maille mixte Océan-Glace."""
        ice_c = max(0.0, min(1.0, ice_concentration))
        return ice_c * albedo_ice + (1.0 - ice_c) * albedo_ocean

    @staticmethod
    def net_primary_production_co2_flux(par_radiation: float, temp_c: float, q_soil: float) -> float:
        """Estimation simplifiée du flux d'assimilation du carbone NPP par la végétation (g C / m² / jour)."""
        if temp_c < 0.0 or q_soil <= 0.0:
            return 0.0
        temp_factor = math.exp(-((temp_c - 25.0) ** 2) / 200.0)
        return max(0.0, 0.02 * par_radiation * temp_factor * min(1.0, q_soil * 2.0))

    @classmethod
    def evaluate_coupler_state(cls, state: dict[str, float]) -> dict[str, float]:
        """Évalue le bilan de masse et d'énergie aux interfaces du système Terre."""
        v10 = state.get("wind_speed_10m", 10.0)
        ice_c = state.get("ice_concentration", 0.5)
        par = state.get("par_radiation", 200.0)
        t_c = state.get("temp_c", 20.0)
        q_soil = state.get("q_soil", 0.5)

        tau = cls.ocean_atmosphere_momentum_flux(v10)
        albedo = cls.sea_ice_albedo_feedback(ice_c)
        npp = cls.net_primary_production_co2_flux(par, t_c, q_soil)

        return {
            "wind_stress_tau": tau,
            "surface_albedo": albedo,
            "npp_co2_uptake": npp,
        }
