"""
Equivalent Potential Temperature
================================

Approximate equivalent potential temperature.
"""

from math import exp

from acf.science.constants import CP, LV


class EquivalentPotentialTemperature:
    """Equivalent potential temperature calculator."""

    @staticmethod
    def calculate(
        temperature_k: float,
        specific_humidity: float,
    ) -> float:
        """
        Calculate equivalent potential temperature.

        Parameters
        ----------
        temperature_k : float
            Temperature (K)

        specific_humidity : float
            Specific humidity (kg/kg)

        Returns
        -------
        float
            Equivalent potential temperature (K)
        """

        if temperature_k <= 0:
            raise ValueError("temperature must be positive.")

        if specific_humidity < 0:
            raise ValueError(
                "specific_humidity must be non-negative."
            )

        return temperature_k * exp(
            LV * specific_humidity /
            (CP * temperature_k)
        )
