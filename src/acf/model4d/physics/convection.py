"""
ACF - Atmospheric Complexity Framework
Model4D Physics
Convection Module

Handles atmospheric convection calculations:
- buoyancy
- convective velocity
- temperature instability
"""


class Convection:
    """
    Atmospheric convection physics equations.
    """

    GRAVITY = 9.81

    @staticmethod
    def buoyancy(temperature_parcel, temperature_environment):
        """
        Calculate thermal buoyancy.

        B = g * (Tp - Te) / Te

        Parameters:
            temperature_parcel (float): Parcel temperature K
            temperature_environment (float): Environment temperature K

        Returns:
            float: buoyancy acceleration
        """

        if temperature_environment <= 0:
            raise ValueError("Temperature must be positive")

        return (
            Convection.GRAVITY
            * (temperature_parcel - temperature_environment)
            / temperature_environment
        )


    @staticmethod
    def convective_velocity(buoyancy, height):
        """
        Estimate convective velocity.

        w = sqrt(2 * B * H)

        Parameters:
            buoyancy (float)
            height (float)

        Returns:
            float: vertical velocity
        """

        if height < 0:
            raise ValueError("Height cannot be negative")

        if buoyancy <= 0:
            return 0.0

        return (2 * buoyancy * height) ** 0.5


    @staticmethod
    def instability_index(surface_temperature, upper_temperature):
        """
        Simple thermal instability index.

        I = Ts - Tu

        Positive value means unstable atmosphere.
        """

        return surface_temperature - upper_temperature
