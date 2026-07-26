"""
ACF - Atmospheric Complexity Framework
Model4D Physics Module

Boundary Layer Physics

Handles:
- Planetary Boundary Layer (PBL)
- Mixing height
- Turbulent diffusion
- Surface layer calculations
"""


import math


class BoundaryLayerPhysics:
    """
    Atmospheric boundary layer physics engine.
    """

    GRAVITY = 9.81

    @staticmethod
    def pbl_height(temperature_gradient: float) -> float:
        """
        Estimate planetary boundary layer height.

        Parameters
        ----------
        temperature_gradient :
            Stability gradient parameter

        Returns
        -------
        float
            Boundary layer height (km)
        """

        if temperature_gradient < 0:
            raise ValueError("Invalid temperature gradient")

        return round(1000 * math.sqrt(temperature_gradient), 2)


    @staticmethod
    def mixing_length(height: float) -> float:
        """
        Calculate turbulent mixing length.

        l = 0.1 * z
        """

        if height <= 0:
            raise ValueError("Height must be positive")

        return round(0.1 * height, 3)


    @staticmethod
    def turbulent_diffusion(wind_speed: float) -> float:
        """
        Estimate turbulent diffusion coefficient.
        """

        if wind_speed < 0:
            raise ValueError("Wind speed cannot be negative")

        return round(0.4 * wind_speed, 3)


    @staticmethod
    def stability_parameter(temperature_difference: float) -> str:
        """
        Classify boundary layer stability.
        """

        if temperature_difference > 0.05:
            return "stable"

        if temperature_difference < -0.05:
            return "unstable"

        return "neutral"


    @staticmethod
    def friction_velocity(wind_speed: float) -> float:
        """
        Estimate friction velocity.
        """

        if wind_speed <= 0:
            raise ValueError("Wind speed must be positive")

        return round(math.sqrt(0.0025 * wind_speed), 3)
