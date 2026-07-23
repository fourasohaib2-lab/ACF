"""
Wet Bulb Temperature
====================

Approximation using the Stull (2011) formula.

Reference
---------
Stull, R. (2011)
Wet-Bulb Temperature from Relative Humidity and Air Temperature.
Journal of Applied Meteorology and Climatology.
"""

from math import atan, sqrt


class WetBulbTemperature:
    """Wet bulb temperature calculator."""

    @staticmethod
    def calculate(
        temperature_c: float,
        relative_humidity: float,
    ) -> float:
        """
        Calculate wet bulb temperature.

        Parameters
        ----------
        temperature_c : float
            Air temperature (°C)

        relative_humidity : float
            Relative humidity (0-1)

        Returns
        -------
        float
            Wet bulb temperature (°C)
        """

        if not (0.0 <= relative_humidity <= 1.0):
            raise ValueError(
                "relative_humidity must be between 0 and 1."
            )

        rh = relative_humidity * 100.0

        return (
            temperature_c * atan(0.151977 * sqrt(rh + 8.313659))
            + atan(temperature_c + rh)
            - atan(rh - 1.676331)
            + 0.00391838 * rh ** 1.5 * atan(0.023101 * rh)
            - 4.686035
        )
