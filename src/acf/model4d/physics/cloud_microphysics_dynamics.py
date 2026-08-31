"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Cloud Microphysics Dynamics
=====================================
Advanced physics routines for mixed-phase cloud microphysics, hydrometeor size distributions,
and phase transitions.
"""

from __future__ import annotations

import math


class CloudMicrophysicsDynamics:
    """
    Advanced mixed-phase cloud microphysical dynamics for 4D atmospheric solvers.
    """

    @staticmethod
    def saturation_vapor_pressure_ice(temperature_k: float) -> float:
        """
        Calculates saturation vapor pressure over ice using Goff-Gratch formulation (Pa).
        """
        if temperature_k <= 0:
            raise ValueError("Temperature must be positive Kelvin.")
        t_c = temperature_k - 273.15
        # Huang (2018) / Tetens ice formulation in Pa
        return round(611.2 * math.exp((21.875 * t_c) / (t_c + 265.5)), 2)

    @staticmethod
    def bergeron_findeisen_potential(
        e_sat_water: float,
        e_sat_ice: float,
        actual_vapor_pressure: float,
    ) -> float:
        """
        Calculates the vapor pressure gradient driving the Wegener-Bergeron-Findeisen ice growth mechanism.
        Returns positive value when vapor pressure exceeds ice saturation while below water saturation.
        """
        if actual_vapor_pressure < e_sat_ice:
            return 0.0
        return round(min(actual_vapor_pressure, e_sat_water) - e_sat_ice, 4)

    @staticmethod
    def terminal_velocity_hydrometeor(
        diameter_m: float,
        density_air: float = 1.225,
        species: str = "rain",
    ) -> float:
        """
        Calculates terminal fall velocity (m/s) based on hydrometeor diameter and category.
        """
        if diameter_m < 0:
            raise ValueError("Diameter must be non-negative.")
        if density_air <= 0:
            raise ValueError("Air density must be positive.")

        rho_factor = math.sqrt(1.225 / density_air)

        if species == "cloud_droplet":
            # Stokes regime: v ~ k * r^2
            return round(1.19e8 * (diameter_m / 2.0) ** 2 * rho_factor, 4)
        elif species == "ice_crystal":
            return round(0.8 * (diameter_m * 1000) ** 0.5 * rho_factor, 4)
        elif species == "graupel":
            return round(3.0 * (diameter_m * 1000) ** 0.5 * rho_factor, 4)
        else:  # rain
            # Atlas et al. formulation
            v_terminal = 9.65 - 10.3 * math.exp(-600.0 * diameter_m)
            return round(max(0.0, v_terminal * rho_factor), 4)

    @staticmethod
    def autoconversion_kessler(
        q_cloud: float,
        q_crit: float = 0.0005,
        rate_const: float = 0.001,
    ) -> float:
        """
        Kessler-type autoconversion rate from cloud liquid water to rainwater (kg/kg/s).
        """
        if q_cloud <= q_crit:
            return 0.0
        return round(rate_const * (q_cloud - q_crit), 8)

