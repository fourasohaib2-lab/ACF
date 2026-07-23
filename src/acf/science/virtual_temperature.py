"""
Virtual Temperature
===================

Formula:
    Tv = T * (1 + 0.61 * q)
"""


class VirtualTemperature:
    """Virtual temperature calculator."""

    @staticmethod
    def calculate(temperature: float, specific_humidity: float) -> float:
        """
        Calculate virtual temperature.

        Parameters
        ----------
        temperature : float
            Air temperature in Kelvin.
        specific_humidity : float
            Specific humidity in kg/kg.

        Returns
        -------
        float
            Virtual temperature in Kelvin.
        """
        return temperature * (1.0 + 0.61 * specific_humidity)

