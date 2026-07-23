"""
Saturation Vapor Pressure
=========================

Calculation of saturation vapor pressure using the Tetens formula.

Formula
-------
es = 6.112 × exp((17.67 × Tc) / (Tc + 243.5))

where:
    es : saturation vapor pressure (hPa)
    Tc : temperature (°C)
"""

from math import exp


class SaturationVaporPressure:
    """Saturation vapor pressure calculator."""

    @staticmethod
    def calculate(temperature_celsius: float) -> float:
        """
        Calculate saturation vapor pressure.

        Parameters
        ----------
        temperature_celsius : float
            Air temperature in degrees Celsius.

        Returns
        -------
        float
            Saturation vapor pressure (hPa)
        """
        return 6.112 * exp(
            (17.67 * temperature_celsius)
            / (temperature_celsius + 243.5)
        )

