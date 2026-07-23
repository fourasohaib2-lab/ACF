"""
Lifted Index (LI)
=================
"""


class LiftedIndex:
    """Lifted Index calculator."""

    @staticmethod
    def calculate(
        parcel_temperature: float,
        environment_temperature: float,
    ) -> float:
        """
        Compute Lifted Index.

        LI = T_environment - T_parcel
        """

        return (
            environment_temperature
            - parcel_temperature
        )

    @staticmethod
    def category(li: float) -> str:
        """
        Classify Lifted Index.
        """

        if li > 6:
            return "Very Stable"

        if li > 2:
            return "Stable"

        if li > 0:
            return "Slightly Unstable"

        if li > -3:
            return "Unstable"

        if li > -6:
            return "Very Unstable"

        return "Extreme Instability"

