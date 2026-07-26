"""
Atmospheric Complexity Framework
Divergence Operator
"""

from __future__ import annotations


class Divergence:
    """Divergence operator."""

    @staticmethod
    def horizontal(du_dx: float, dv_dy: float) -> float:
        """
        Horizontal divergence.
        """
        return du_dx + dv_dy

    @staticmethod
    def vertical(dw_dz: float) -> float:
        """
        Vertical divergence.
        """
        return dw_dz

    @staticmethod
    def compute(*components: float) -> float:
        """
        Generic divergence.

        Accepts:
            1 component -> 1D
            2 components -> 2D
            3 components -> 3D
        """
        return sum(components)

    @staticmethod
    def calculate(
        du_dx: float = 0.0,
        dv_dy: float = 0.0,
        dw_dz: float = 0.0,
    ) -> float:
        """
        Meteorological divergence.
        """
        return du_dx + dv_dy + dw_dz

    @staticmethod
    def category(value: float) -> str:
        """
        Qualitative classification.
        """

        value = abs(value)

        if value < 5e-6:
            return "Weak"

        elif value <= 2e-5:
            return "Moderate"

        else:
            return "Strong"
