"""
Potential Temperature
"""

import math


class PotentialTemperature:
    P0 = 1000.0  # hPa
    RD_CP = 0.286  # R/Cp

    @staticmethod
    def calculate(temperature_k, pressure_hpa):
        """
        Calculate potential temperature (K)
        """

        return temperature_k * math.pow(
            PotentialTemperature.P0 / pressure_hpa,
            PotentialTemperature.RD_CP,
        )
