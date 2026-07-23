"""
Convective Available Potential Energy (CAPE)
============================================
"""

from typing import Sequence


class CAPE:
    """Simple CAPE calculator."""

    @staticmethod
    def calculate(
        parcel_temperature: Sequence[float],
        environment_temperature: Sequence[float],
        height: Sequence[float],
    ) -> float:
        """
        Simplified CAPE computation.

        Parameters
        ----------
        parcel_temperature : list[float]
        environment_temperature : list[float]
        height : list[float]
        """

        if not (
            len(parcel_temperature)
            == len(environment_temperature)
            == len(height)
        ):
            raise ValueError("profiles must have the same length.")

        if len(height) < 2:
            raise ValueError("at least two levels are required.")

        cape = 0.0

        for i in range(len(height) - 1):

            dz = height[i + 1] - height[i]

            delta = (
                parcel_temperature[i]
                - environment_temperature[i]
            )

            if delta > 0:
                cape += delta * dz

        return cape

