"""
ACF Model4D - Waves Physics Module

Atmospheric wave dynamics:
- Gravity waves
- Phase speed
- Wave frequency
- Wavelength relations
"""

import math


class Waves:
    """
    Atmospheric wave physics equations.
    """

    GRAVITY = 9.80665

    @staticmethod
    def wavelength(phase_speed: float, period: float) -> float:
        """
        Calculate wavelength.

        λ = c × T

        Parameters:
            phase_speed: wave speed (m/s)
            period: period (s)

        Returns:
            wavelength (m)
        """
        if period < 0:
            raise ValueError("Period must be positive")

        return phase_speed * period

    @staticmethod
    def frequency(period: float) -> float:
        """
        Calculate wave frequency.

        f = 1 / T
        """
        if period <= 0:
            raise ValueError("Period must be positive")

        return 1.0 / period

    @staticmethod
    def phase_speed(wavelength: float, period: float) -> float:
        """
        Calculate phase speed.

        c = λ / T
        """
        if period <= 0:
            raise ValueError("Period must be positive")

        return wavelength / period

    @staticmethod
    def gravity_wave_speed(height: float) -> float:
        """
        Simplified shallow-water gravity wave speed.

        c = sqrt(gH)
        """
        if height < 0:
            raise ValueError("Height must be positive")

        return math.sqrt(Waves.GRAVITY * height)
