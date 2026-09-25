"""
Dry Static Energy
=================
"""

from acf.science.constants import CP, G


class DryStaticEnergy:
    """Dry static energy calculator."""

    @staticmethod
    def calculate(
        temperature_k: float,
        height_m: float,
    ) -> float:

        if temperature_k <= 0:
            raise ValueError("temperature must be positive.")

        if height_m < 0:
            raise ValueError("height must be non-negative.")

        return CP * temperature_k + G * height_m
