"""
Bulk Wind Shear
===============
"""

from math import sqrt


class BulkWindShear:
    """Bulk wind shear calculator."""

    @staticmethod
    def calculate(
        u_bottom: float,
        v_bottom: float,
        u_top: float,
        v_top: float,
    ) -> float:
        """
        Compute bulk wind shear magnitude.
        """

        du = u_top - u_bottom
        dv = v_top - v_bottom

        return sqrt(du ** 2 + dv ** 2)

    @staticmethod
    def category(value: float) -> str:
        """
        Classify bulk shear (m/s).
        """

        if value < 10:
            return "Weak"

        if value < 20:
            return "Moderate"

        if value < 30:
            return "Strong"

        return "Extreme"

