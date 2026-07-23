"""
Total Totals Index (TT)
=======================
"""


class TotalTotals:
    """Total Totals Index calculator."""

    @staticmethod
    def calculate(
        t850: float,
        td850: float,
        t500: float,
    ) -> float:
        """
        Compute Total Totals Index.

        TT = T850 + Td850 - 2*T500
        """

        return (
            t850
            + td850
            - (2 * t500)
        )

    @staticmethod
    def category(tt: float) -> str:
        """
        Classify Total Totals Index.
        """

        if tt < 44:
            return "Low"

        if tt < 50:
            return "Moderate"

        if tt < 55:
            return "High"

        return "Extreme"

