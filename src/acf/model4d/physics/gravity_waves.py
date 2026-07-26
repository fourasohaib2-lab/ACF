"""
ACF - Atmospheric Complexity Framework
Gravity Waves Physics Module

Sprint 8.20
"""

import math


class GravityWavesPhysics:
    """
    Physics utilities for atmospheric gravity waves.
    """

    GRAVITY = 9.81

    @staticmethod
    def brunt_vaisala_frequency_squared(
        stability_parameter: float
    ) -> float:
        """
        Calculate squared Brunt-Vaisala frequency.

        N² = g / theta * dtheta/dz

        Here stability_parameter represents
        normalized potential temperature gradient.
        """

        if stability_parameter <= 0:
            raise ValueError(
                "Stability parameter must be positive"
            )

        return GravityWavesPhysics.GRAVITY * stability_parameter


    @staticmethod
    def wave_phase_speed(
        buoyancy_frequency: float,
        wavelength: float
    ) -> float:
        """
        Calculate simplified gravity wave phase speed.

        c = N * lambda / (2*pi)
        """

        if buoyancy_frequency <= 0:
            raise ValueError(
                "Buoyancy frequency must be positive"
            )

        if wavelength <= 0:
            raise ValueError(
                "Wavelength must be positive"
            )

        return (
            buoyancy_frequency *
            wavelength /
            (2 * math.pi)
        )


    @staticmethod
    def vertical_wavenumber(
        buoyancy_frequency: float,
        horizontal_wavenumber: float
    ) -> float:
        """
        Estimate vertical wave number.

        m = N / k
        """

        if buoyancy_frequency <= 0:
            raise ValueError(
                "Buoyancy frequency must be positive"
            )

        if horizontal_wavenumber <= 0:
            raise ValueError(
                "Horizontal wavenumber must be positive"
            )

        return buoyancy_frequency / horizontal_wavenumber


    @staticmethod
    def classify_wave(
        phase_speed: float
    ) -> str:
        """
        Classify gravity wave regime.
        """

        if phase_speed < 10:
            return "slow"

        elif phase_speed < 50:
            return "moderate"

        return "fast"
