"""
Mixing Ratio
============

Calculation of the mixing ratio.

Formula
-------
w = 0.622 * e / (p - e)

where:
    w : mixing ratio (kg/kg)
    e : vapor pressure (hPa)
    p : atmospheric pressure (hPa)
"""


class MixingRatio:
    """Mixing ratio calculator."""

    @staticmethod
    def calculate(vapor_pressure: float, pressure: float) -> float:
        """
        Calculate the mixing ratio.

        Parameters
        ----------
        vapor_pressure : float
            Vapor pressure (hPa)
        pressure : float
            Atmospheric pressure (hPa)

        Returns
        -------
        float
            Mixing ratio (kg/kg)
        """
        if vapor_pressure >= pressure:
            raise ValueError(
                "vapor_pressure must be smaller than pressure."
            )

        return 0.622 * vapor_pressure / (pressure - vapor_pressure)

