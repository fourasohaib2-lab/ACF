"""
K Index (KI)
============
"""


class KIndex:
    """K Index calculator."""

    @staticmethod
    def calculate(
        t850: float,
        t700: float,
        t500: float,
        td850: float,
        td700: float,
    ) -> float:
        """
        Compute K Index.
        """

        return (t850 - t500) + td850 - (t700 - td700)

    @staticmethod
    def category(ki: float) -> str:
        """
        Classify K Index.
        """

        if ki < 15:
            return "Very Low"

        if ki < 25:
            return "Low"

        if ki < 35:
            return "Moderate"

        if ki < 40:
            return "High"

        return "Extreme"
