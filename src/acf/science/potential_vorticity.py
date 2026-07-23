"""
Potential Vorticity (PV)
========================
"""


class PotentialVorticity:
    """Potential Vorticity calculator."""

    GRAVITY = 9.81

    @staticmethod
    def calculate(
        relative_vorticity: float,
        coriolis: float,
        dtheta_dp: float,
    ) -> float:
        """
        Compute Ertel Potential Vorticity.

        PV = -g (ζ + f) dθ/dp
        """

        return (
            -PotentialVorticity.GRAVITY
            * (relative_vorticity + coriolis)
            * dtheta_dp
        )

    @staticmethod
    def category(value: float) -> str:
        """
        Simple PV classification.
        """

        magnitude = abs(value)

        if magnitude < 1e-6:
            return "Weak"

        if magnitude < 5e-6:
            return "Moderate"

        return "Strong"
