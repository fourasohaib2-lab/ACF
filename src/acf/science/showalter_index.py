"""
Showalter Index (SI)
====================
"""


class ShowalterIndex:
    """Showalter Index calculator."""

    @staticmethod
    def calculate(
        parcel_temperature_500: float,
        environment_temperature_500: float,
    ) -> float:
        """
        Compute Showalter Index.

        SI = T_environment(500 hPa)
             - T_parcel(500 hPa)
        """

        return (
            environment_temperature_500
            - parcel_temperature_500
        )

    @staticmethod
    def category(si: float) -> str:
        """
        Classify Showalter Index.
        """

        if si > 6:
            return "Very Stable"

        if si > 3:
            return "Stable"

        if si > 1:
            return "Slightly Unstable"

        if si > -3:
            return "Moderately Unstable"

        if si > -6:
            return "Very Unstable"

        return "Extreme Instability"

