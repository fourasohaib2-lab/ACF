"""
ACF - Atmospheric Complexity Framework

Advanced Parameterization Physics Module
Sprint 8.26

Handles advanced atmospheric parameterization:
- subgrid scale processes
- turbulence closure factors
- cloud parameterization coefficients
- convection adjustment
- boundary layer tuning
"""


import math


class AdvancedParameterizationPhysics:
    """
    Advanced atmospheric parameterization calculations.
    """

    @staticmethod
    def turbulence_closure(coefficient: float) -> float:
        """
        Compute turbulence closure parameter.

        Parameters
        ----------
        coefficient : float
            Mixing coefficient.

        Returns
        -------
        float
            Closure value.
        """

        if coefficient <= 0:
            raise ValueError("Coefficient must be positive")

        return coefficient * 1.5


    @staticmethod
    def cloud_parameterization(
        cloud_fraction: float,
        efficiency: float = 0.8
    ) -> float:
        """
        Estimate cloud sub-grid contribution.
        """

        if not 0 <= cloud_fraction <= 1:
            raise ValueError("Cloud fraction must be between 0 and 1")

        if efficiency <= 0:
            raise ValueError("Efficiency must be positive")

        return cloud_fraction * efficiency


    @staticmethod
    def convection_adjustment(
        temperature_gradient: float
    ) -> float:
        """
        Convective adjustment intensity.
        """

        if temperature_gradient < 0:
            raise ValueError("Gradient cannot be negative")

        return math.sqrt(temperature_gradient)


    @staticmethod
    def boundary_layer_parameterization(
        wind_speed: float,
        roughness: float
    ) -> float:
        """
        Boundary layer exchange coefficient.
        """

        if wind_speed < 0:
            raise ValueError("Wind speed cannot be negative")

        if roughness <= 0:
            raise ValueError("Roughness must be positive")

        return wind_speed * math.log(1 + roughness)


    @staticmethod
    def stability_correction(
        richardson_number: float
    ) -> str:
        """
        Stability correction classification.
        """

        if richardson_number < 0:
            return "unstable"

        if richardson_number < 0.25:
            return "neutral"

        return "stable"
