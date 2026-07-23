"""
Horizontal Divergence
=====================
"""


class Divergence:
    """Horizontal divergence calculator."""

    @staticmethod
    def calculate(
        du_dx: float,
        dv_dy: float,
    ) -> float:
        """
        Horizontal divergence.

        δ = du/dx + dv/dy
        """

        return du_dx + dv_dy

    @staticmethod
    def category(value: float) -> str:
        """
        Classify divergence.
        """

        if abs(value) < 1e-5:
            return "Weak"

        if abs(value) < 5e-5:
            return "Moderate"

        return "Strong"

