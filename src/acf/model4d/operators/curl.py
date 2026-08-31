"""
ACF - Atmospheric Complexity Framework
Model4D - Curl Operator
"""

from __future__ import annotations

import math


class Curl:
    """
    Curl operator (rotationnel).

    Pour un champ vectoriel F = (u,v,w):

    ∇ × F =
    (
        dw/dy - dv/dz,
        du/dz - dw/dx,
        dv/dx - du/dy
    )
    """

    @staticmethod
    def calculate(
        dw_dy: float,
        dv_dz: float,
        du_dz: float = 0.0,
        dw_dx: float = 0.0,
        dv_dx: float = 0.0,
        du_dy: float = 0.0,
    ) -> tuple[float, float, float]:
        """
        Calculate curl components.
        """

        x = dw_dy - dv_dz
        y = du_dz - dw_dx
        z = dv_dx - du_dy

        return (
            round(x, 12),
            round(y, 12),
            round(z, 12),
        )

    @staticmethod
    def compute(*components: float) -> float:
        """
        Sum curl components.
        """
        return round(sum(components), 12)

    @staticmethod
    def horizontal(
        x: float,
        y: float,
    ) -> float:
        """
        Horizontal curl magnitude.
        """
        return round(math.sqrt(x * x + y * y), 12)

    @staticmethod
    def vertical(
        z: float,
    ) -> float:
        """
        Vertical curl component.
        """
        return round(z, 12)

    @staticmethod
    def magnitude(
        x: float,
        y: float,
        z: float,
    ) -> float:
        """
        Curl vector magnitude.
        """

        return round(
            math.sqrt(x * x + y * y + z * z),
            12,
        )

    @staticmethod
    def normalize(
        x: float,
        y: float,
        z: float,
    ) -> tuple[float, float, float]:

        mag = Curl.magnitude(x, y, z)

        if mag == 0:
            return (0.0, 0.0, 0.0)

        return (
            round(x / mag, 12),
            round(y / mag, 12),
            round(z / mag, 12),
        )

    @staticmethod
    def category(value: float) -> str:
        """
        Curl intensity classification.
        """

        value = abs(value)

        if value < 1e-5:
            return "Weak"

        if value < 5e-5:
            return "Moderate"

        return "Strong"

    @staticmethod
    def is_rotating(
        x: float,
        y: float,
        z: float,
    ) -> bool:

        return Curl.magnitude(x, y, z) > 0

    @staticmethod
    def direction(
        z: float,
    ) -> str:
        """
        Rotation direction.
        """

        if z > 0:
            return "Counterclockwise"

        if z < 0:
            return "Clockwise"

        return "None"
