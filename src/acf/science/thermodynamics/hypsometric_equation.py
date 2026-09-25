"""
Hypsometric Equation
====================

Thickness between two pressure levels.

Formula
-------
Δz = (Rd * Tv / g) * ln(p1 / p2)
"""

from math import log

from acf.science.constants import RD, G


class HypsometricEquation:
    """Hypsometric equation calculator."""

    @staticmethod
    def calculate(
        pressure1_pa: float,
        pressure2_pa: float,
        virtual_temperature_k: float,
    ) -> float:
        """
        Calculate layer thickness.

        Returns
        -------
        float
            Thickness (m)
        """
        if pressure1_pa <= 0 or pressure2_pa <= 0:
            raise ValueError("Pressures must be positive.")

        if virtual_temperature_k <= 0:
            raise ValueError("Virtual temperature must be positive.")

        return (RD * virtual_temperature_k / G) * log(pressure1_pa / pressure2_pa)
