"""
Storm Relative Helicity (SRH)
=============================
"""


class StormRelativeHelicity:
    """Storm Relative Helicity calculator."""

    @staticmethod
    def calculate(
        u: float,
        v: float,
        storm_u: float,
        storm_v: float,
        du: float,
        dv: float,
    ) -> float:
        """
        Compute SRH.

        SRH = (u-cu) * dv - (v-cv) * du
        """

        return (
            (u - storm_u) * dv
            - (v - storm_v) * du
        )

    @staticmethod
    def category(value: float) -> str:
        """
        SRH classification.
        """

        if value < 100:
            return "Weak"

        if value < 250:
            return "Moderate"

        if value < 400:
            return "Strong"

        return "Extreme"
