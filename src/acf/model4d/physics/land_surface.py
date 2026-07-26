"""
ACF - Atmospheric Complexity Framework
Land Surface Physics Module

Handles simplified land surface interactions:
- soil temperature
- soil moisture balance
- evaporation
- sensible heat flux
- surface energy balance
"""


class LandSurface:
    """
    Land surface physical parameterizations.
    """

    STEFAN_BOLTZMANN = 5.670374419e-8

    @staticmethod
    def soil_temperature(energy, heat_capacity):
        """
        Estimate soil temperature variation.

        ΔT = E / C
        """
        if heat_capacity <= 0:
            raise ValueError("Heat capacity must be positive")

        return energy / heat_capacity


    @staticmethod
    def soil_moisture_balance(initial, precipitation, evaporation):
        """
        Soil moisture evolution.

        M = M0 + P - E
        """
        value = initial + precipitation - evaporation

        return max(value, 0)


    @staticmethod
    def evaporation_rate(temperature, humidity, coefficient=0.1):
        """
        Simplified evaporation parameterization.
        """
        if temperature < 0:
            return 0

        deficit = max(1 - humidity, 0)

        return coefficient * temperature * deficit


    @staticmethod
    def sensible_heat_flux(temperature_surface,
                           temperature_air,
                           coefficient=10):
        """
        Sensible heat exchange.
        """
        return coefficient * (
            temperature_surface - temperature_air
        )


    @staticmethod
    def energy_balance(net_radiation,
                       sensible_heat,
                       latent_heat,
                       ground_heat):
        """
        Surface energy conservation.

        Rn = H + LE + G
        """

        return net_radiation - (
            sensible_heat +
            latent_heat +
            ground_heat
        )
