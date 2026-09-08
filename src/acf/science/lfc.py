"""
Level of Free Convection (LFC)
==============================
"""


class LFC:
    """Simple LFC calculator."""

    @staticmethod
    def calculate(
        lcl_height: float,
        parcel_temperature: float,
        environment_temperature: float,
    ) -> float:
        """
        Simple approximation.

        Returns the LCL height if the parcel is warmer
        than the environment.
        """

        if lcl_height < 0:
            raise ValueError("lcl_height must be non-negative.")

        if parcel_temperature > environment_temperature:
            return lcl_height

        return float("nan")
