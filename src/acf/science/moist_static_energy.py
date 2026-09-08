"""
Moist Static Energy
===================
"""

from acf.science.constants import CP, LV, G


class MoistStaticEnergy:
    """Moist static energy calculator."""

    @staticmethod
    def calculate(
        temperature_k: float,
        height_m: float,
        specific_humidity: float,
    ) -> float:

        if temperature_k <= 0:
            raise ValueError("temperature must be positive.")

        if height_m < 0:
            raise ValueError("height must be non-negative.")

        if specific_humidity < 0:
            raise ValueError("specific_humidity must be non-negative.")

        return CP * temperature_k + G * height_m + LV * specific_humidity
