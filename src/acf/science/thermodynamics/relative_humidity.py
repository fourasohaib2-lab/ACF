"""
Relative Humidity
=================

Calculation of relative humidity.

Formula
-------
RH = e / es
"""


class RelativeHumidity:
    """Relative humidity calculator."""

    @staticmethod
    def calculate(
        vapor_pressure: float,
        saturation_vapor_pressure: float,
    ) -> float:
        """
        Calculate relative humidity.

        Returns
        -------
        float
            Relative humidity (0-1)
        """
        if saturation_vapor_pressure <= 0:
            raise ValueError("saturation_vapor_pressure must be positive.")

        rh = vapor_pressure / saturation_vapor_pressure

        return max(0.0, min(1.0, rh))
