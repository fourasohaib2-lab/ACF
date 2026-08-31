"""
ACF - Atmospheric Complexity Framework
Model4D Ocean Coupling Physics Module

Couplage atmosphère-océan simplifié :
- température de surface océanique (SST)
- flux thermique air-mer
- échange humidité océan-atmosphère
- coefficient de couplage
"""


class OceanCoupling:
    """
    Physics model for atmosphere-ocean interaction.
    """

    AIR_DENSITY = 1.225  # kg/m3
    SPECIFIC_HEAT_AIR = 1005  # J/(kg.K)
    OCEAN_DENSITY = 1025  # kg/m3
    OCEAN_HEAT_CAPACITY = 4186  # J/(kg.K)

    @staticmethod
    def sensible_heat_flux(wind_speed, air_temp, sea_temp, coefficient=0.0012):
        """
        Sensible heat flux between ocean and atmosphere.

        Q = rho * Cp * Cd * U * (Ts - Ta)
        """

        return (
            OceanCoupling.AIR_DENSITY
            * OceanCoupling.SPECIFIC_HEAT_AIR
            * coefficient
            * wind_speed
            * (sea_temp - air_temp)
        )

    @staticmethod
    def latent_heat_flux(wind_speed, humidity_difference, coefficient=0.0015):
        """
        Simplified latent heat exchange.

        Positive value = ocean evaporation.
        """

        latent_heat = 2.5e6

        return OceanCoupling.AIR_DENSITY * latent_heat * coefficient * wind_speed * humidity_difference

    @staticmethod
    def ocean_temperature_change(heat_flux, duration, depth=10):
        """
        Ocean mixed-layer temperature variation.

        dT = Q*t/(rho*Cp*depth)
        """

        denominator = OceanCoupling.OCEAN_DENSITY * OceanCoupling.OCEAN_HEAT_CAPACITY * depth

        return heat_flux * duration / denominator

    @staticmethod
    def coupling_strength(sst, air_temperature):
        """
        Coupling indicator between ocean and atmosphere.
        """

        return abs(sst - air_temperature)
