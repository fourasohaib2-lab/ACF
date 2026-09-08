"""
Atmospheric Complexity Framework (ACF)

Linear Interpolation
====================

1D Linear interpolation utilities.
"""

from __future__ import annotations


class LinearInterpolation:
    """
    Performs simple linear interpolation.
    """

    @staticmethod
    def interpolate(
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        x: float,
    ) -> float:
        """
        Linear interpolation between two points.
        """

        if x0 == x1:
            raise ValueError("x0 and x1 cannot be equal.")

        return y0 + (x - x0) * (y1 - y0) / (x1 - x0)

    @staticmethod
    def midpoint(
        y0: float,
        y1: float,
    ) -> float:
        """
        Midpoint value.
        """

        return (y0 + y1) / 2.0

    @staticmethod
    def fraction(
        x0: float,
        x1: float,
        x: float,
    ) -> float:
        """
        Relative interpolation fraction.
        """

        if x0 == x1:
            raise ValueError("x0 and x1 cannot be equal.")

        return (x - x0) / (x1 - x0)

    @staticmethod
    def clamp(
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:
        """
        Clamp a value.
        """

        return max(minimum, min(maximum, value))
