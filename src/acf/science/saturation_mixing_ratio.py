"""
Saturation Mixing Ratio
=======================

Calculation of the saturation mixing ratio.

Formula
-------
ws = 0.622 * es / (p - es)

where:
    ws : saturation mixing ratio (kg/kg)
    es : saturation vapor pressure (hPa)
    p  : atmospheric pressure (hPa)
"""


class SaturationMixingRatio:
    """Saturation mixing ratio calculator."""

    @staticmethod
    def calculate(saturation_vapor_pressure: float, pressure: float) -> float:
        """
        Calculate the saturation mixing ratio.

        Parameters
        ----------
        saturation_vapor_pressure : float
            Saturation vapor pressure (hPa)

        pressure : float
            Atmospheric pressure (hPa)

        Returns
        -------
        float
            Saturation mixing ratio (kg/kg)
        """
        if saturation_vapor_pressure >= pressure:
            raise ValueError(
                "saturation_vapor_pressure must be smaller than pressure."
            )

        return (
            0.622
            * saturation_vapor_pressure
            / (pressure - saturation_vapor_pressure)
        )

