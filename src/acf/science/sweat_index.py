"""
Severe Weather Threat Index (SWEAT)
===================================
"""

import math


class SWEATIndex:
    """Severe Weather Threat Index."""

    @staticmethod
    def calculate(
        td850: float,
        tt: float,
        wind850: float,
        wind500: float,
        dir850: float,
        dir500: float,
    ) -> float:
        """
        Compute SWEAT Index.

        Parameters
        ----------
        td850 : Dew point at 850 hPa (°C)
        tt : Total Totals Index
        wind850 : Wind speed at 850 hPa (kt)
        wind500 : Wind speed at 500 hPa (kt)
        dir850 : Wind direction at 850 hPa (deg)
        dir500 : Wind direction at 500 hPa (deg)
        """

        shear = math.sin(
            math.radians(dir500 - dir850)
        )

        sweat = (
            12 * td850
            + 20 * (tt - 49)
            + 2 * wind850
            + wind500
            + 125 * (shear + 0.2)
        )

        return max(sweat, 0.0)

    @staticmethod
    def category(value: float) -> str:

        if value < 150:
            return "Low"

        if value < 300:
            return "Moderate"

        if value < 400:
            return "High"

        return "Extreme"

