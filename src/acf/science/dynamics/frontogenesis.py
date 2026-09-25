"""
Frontogenesis
=============
"""


class Frontogenesis:
    """Simple frontogenesis calculator."""

    @staticmethod
    def calculate(
        temperature_gradient: float,
        deformation: float,
    ) -> float:
        """
        Simplified frontogenesis.

        F = |grad(T)| × deformation
        """

        return abs(temperature_gradient) * deformation

    @staticmethod
    def category(value: float) -> str:

        if value < 1e-5:
            return "Weak"

        if value < 5e-5:
            return "Moderate"

        return "Strong"
