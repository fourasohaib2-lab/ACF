"""
ACF - Atmospheric Complexity Framework
Model4D - Laplacian Operator
"""

from __future__ import annotations


class Laplacian:
    """
    Laplacian operator.

    ∇²φ = ∂²φ/∂x² + ∂²φ/∂y² + ∂²φ/∂z²
    """

    @staticmethod
    def calculate(
        d2_dx2: float,
        d2_dy2: float,
        d2_dz2: float = 0.0,
    ) -> float:
        """
        Compute Laplacian from second derivatives.
        """
        result = d2_dx2 + d2_dy2 + d2_dz2

        # Remove floating-point artifacts
        return round(result, 12)

    @staticmethod
    def horizontal(
        d2_dx2: float,
        d2_dy2: float,
    ) -> float:
        """
        Horizontal Laplacian.
        """
        return round(d2_dx2 + d2_dy2, 12)

    @staticmethod
    def vertical(
        d2_dz2: float,
    ) -> float:
        """
        Vertical Laplacian.
        """
        return round(d2_dz2, 12)

    @staticmethod
    def compute(*values: float) -> float:
        """
        Generic computation.

        Examples
        --------
        compute(2,3)
        compute(2,3,4)
        compute(7)
        """
        return round(sum(values), 12)

    @staticmethod
    def magnitude(value: float) -> float:
        """
        Absolute Laplacian magnitude.
        """
        return abs(value)

    @staticmethod
    def category(value: float) -> str:
        """
        Classify Laplacian intensity.
        """

        value = abs(value)

        if value < 1e-5:
            return "Weak"

        if value < 5e-5:
            return "Moderate"

        return "Strong"

    @staticmethod
    def is_positive(value: float) -> bool:
        return value > 0

    @staticmethod
    def is_negative(value: float) -> bool:
        return value < 0

    @staticmethod
    def is_zero(value: float) -> bool:
        return value == 0
