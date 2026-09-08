"""
Virtual Potential Temperature
=============================
"""


class VirtualPotentialTemperature:
    """Virtual potential temperature calculator."""

    @staticmethod
    def calculate(
        potential_temperature: float,
        mixing_ratio: float,
    ) -> float:
        """
        Calculate virtual potential temperature.
        """

        if potential_temperature <= 0:
            raise ValueError("potential_temperature must be positive.")

        if mixing_ratio < 0:
            raise ValueError("mixing_ratio must be non-negative.")

        return potential_temperature * (1.0 + 0.61 * mixing_ratio)
