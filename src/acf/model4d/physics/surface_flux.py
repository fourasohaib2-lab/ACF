"""
ACF - Atmospheric Complexity Framework
Surface Flux Physics Module

Handles simplified surface-atmosphere exchanges:
- sensible heat flux
- latent heat flux
- momentum flux
- bulk transfer relations
"""


class SurfaceFlux:
    """
    Surface exchange parameterizations.
    """

    AIR_DENSITY = 1.225  # kg/m3
    CP_AIR = 1004.0  # J/(kg K)
    LV = 2.5e6  # J/kg latent heat vaporization

    @staticmethod
    def sensible_heat_flux(temperature_surface, temperature_air, transfer_coefficient=0.001):
        """
        Compute sensible heat flux.

        H = rho * Cp * Ch * (Ts - Ta)
        """
        delta_t = temperature_surface - temperature_air

        return SurfaceFlux.AIR_DENSITY * SurfaceFlux.CP_AIR * transfer_coefficient * delta_t

    @staticmethod
    def latent_heat_flux(evaporation_rate, latent_heat=LV):
        """
        Compute latent heat flux.

        LE = Lv * evaporation
        """
        return latent_heat * evaporation_rate

    @staticmethod
    def momentum_flux(wind_speed, drag_coefficient=0.001):
        """
        Compute surface momentum flux.

        tau = rho * Cd * U²
        """
        return SurfaceFlux.AIR_DENSITY * drag_coefficient * wind_speed**2

    @staticmethod
    def bulk_exchange(variable_difference, coefficient):
        """
        Generic bulk aerodynamic exchange.
        """
        return coefficient * variable_difference
