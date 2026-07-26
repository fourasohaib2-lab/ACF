"""
ACF - Atmospheric Complexity Framework
Boundary Layer Physics Module

Provides simplified atmospheric boundary layer calculations.
"""


class BoundaryLayer:
    """
    Atmospheric boundary layer utilities.

    The boundary layer is the lowest part of the atmosphere
    influenced directly by surface interactions.
    """

    @staticmethod
    def friction_velocity(wind_speed, roughness_length=0.1):
        """
        Estimate friction velocity.

        Parameters
        ----------
        wind_speed : float
            Wind speed (m/s)
        roughness_length : float
            Surface roughness length (m)

        Returns
        -------
        float
            Friction velocity (m/s)
        """

        kappa = 0.41  # von Karman constant

        if wind_speed < 0:
            raise ValueError("Wind speed must be positive")

        if roughness_length <= 0:
            raise ValueError("Roughness length must be positive")

        return (kappa * wind_speed) / (
            __import__("math").log(10 / roughness_length)
        )

    @staticmethod
    def mixing_height(temperature, surface_temperature):
        """
        Estimate mixing layer height.

        Parameters
        ----------
        temperature : float
            Air temperature (K)
        surface_temperature : float
            Surface temperature (K)

        Returns
        -------
        float
            Mixing height (m)
        """

        if temperature <= 0 or surface_temperature <= 0:
            raise ValueError("Temperature must be positive")

        delta = surface_temperature - temperature

        return max(0.0, delta * 100)

    @staticmethod
    def stability(surface_temperature, air_temperature):
        """
        Determine atmospheric stability.

        Returns
        -------
        str
            Stable / Neutral / Unstable
        """

        difference = surface_temperature - air_temperature

        if difference > 2:
            return "Unstable"

        if difference < -2:
            return "Stable"

        return "Neutral"

