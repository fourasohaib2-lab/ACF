"""
Relative Vorticity
==================
"""


class Vorticity:
    """Relative vorticity calculator."""

    @staticmethod
    def calculate(
        dv_dx: float,
        du_dy: float,
    ) -> float:
        """
        Relative vorticity (s^-1)

        ζ = dv/dx − du/dy
        """

        return dv_dx - du_dy

    @staticmethod
    def category(value: float) -> str:
        """
        Simple classification.
        """

        if abs(value) < 1e-5:
            return "Weak"

        if abs(value) < 5e-5:
            return "Moderate"

        return "Strong"

