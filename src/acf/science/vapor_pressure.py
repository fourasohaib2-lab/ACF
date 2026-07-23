"""
Vapor Pressure
==============

Calculation of vapor pressure.

Formula
-------
e = RH × es

where:
    e  : vapor pressure (hPa)
    RH : relative humidity (0–1)
    es : saturation vapor pressure (hPa)
"""


class VaporPressure:
    """Vapor pressure calculator."""

    @staticmethod
    def calculate(relative_humidity: float,
                  saturation_vapor_pressure: float) -> float:
        """
        Calculate vapor pressure.

        Parameters
        ----------
        relative_humidity : float
            Relative humidity (0-1)

        saturation_vapor_pressure : float
            Saturation vapor pressure (hPa)

        Returns
        -------
        float
            Vapor pressure (hPa)
        """
        if not 0.0 <= relative_humidity <= 1.0:
            raise ValueError(
                "relative_humidity must be between 0 and 1."
            )

        return relative_humidity * saturation_vapor_pressure

