"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Cloud Radiative Feedback
==================================
Formulations for cloud shortwave albedo forcing, longwave greenhouse trapping,
optical depth parameterizations, and net cloud radiative feedback.
"""

from __future__ import annotations


class CloudRadiativeFeedback:
    """
    Physical parameterizations for shortwave and longwave cloud radiative feedbacks.
    """

    @staticmethod
    def cloud_optical_thickness(
        liquid_water_path: float,
        effective_radius_um: float,
    ) -> float:
        """
        Calculates cloud optical thickness (tau) from liquid water path (g/m2)
        and droplet effective radius (micrometers).
        tau ≈ 3/2 * (LWP / (rho_w * r_eff))

        NOTE (Physics Guard, 2026-09-06 Tier X sweep - model4d/physics/
        is a real, disconnected reserve, see model4d/__init__.py's own
        NOTE): the formula above includes the water density rho_w
        divisor, but the implementation below computes
        1.5*(LWP/r_eff), omitting rho_w entirely - a real formula-vs-
        implementation mismatch, not fixed here (disconnected package,
        would need a documented unit-convention decision - e.g. rho_w
        folded into an implicit unit choice - rather than a guessed
        constant), disclosed rather than silently trusted.
        """
        if effective_radius_um <= 0:
            raise ValueError("Effective radius must be positive.")
        if liquid_water_path < 0:
            raise ValueError("Liquid water path must be non-negative.")
        return round(1.5 * (liquid_water_path / effective_radius_um), 4)

    @staticmethod
    def shortwave_cloud_forcing(
        solar_irradiance: float,
        cloud_albedo: float,
        surface_albedo: float = 0.15,
    ) -> float:
        """
        Calculates shortwave cooling cloud radiative effect (W/m2).
        SW_CRE = - S0 * (cloud_albedo - surface_albedo)
        """
        if solar_irradiance < 0:
            raise ValueError("Solar irradiance must be non-negative.")
        delta_albedo = max(0.0, cloud_albedo - surface_albedo)
        return round(-solar_irradiance * delta_albedo, 4)

    @staticmethod
    def longwave_cloud_forcing(
        surface_emission: float,
        cloud_top_emission: float,
        cloud_fraction: float = 1.0,
    ) -> float:
        """
        Calculates longwave warming cloud radiative effect (W/m2).
        LW_CRE = (E_surface - E_cloud_top) * cloud_fraction
        """
        if cloud_fraction < 0 or cloud_fraction > 1:
            raise ValueError("Cloud fraction must be in [0, 1].")
        return round((surface_emission - cloud_top_emission) * cloud_fraction, 4)

    @staticmethod
    def net_cloud_radiative_forcing(sw_forcing: float, lw_forcing: float) -> float:
        """
        Calculates net cloud radiative forcing (W/m2).
        Net_CRE = SW_CRE + LW_CRE
        """
        return round(sw_forcing + lw_forcing, 4)

