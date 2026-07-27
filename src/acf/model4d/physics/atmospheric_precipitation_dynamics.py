"""
ACF - Atmospheric Complexity Framework

Atmospheric Precipitation Dynamics Physics Module

Sprint 9.11
"""

from dataclasses import dataclass


@dataclass
class PrecipitationState:
    """
    Atmospheric precipitation parameters.
    """

    humidity: float
    condensation_rate: float
    convection_intensity: float
    precipitation_efficiency: float = 1.0


class AtmosphericPrecipitationDynamics:
    """
    Simplified precipitation physics model.

    Physical chain:

        humidity
            ↓
        condensation
            ↓
        convection
            ↓
        precipitation
    """


    def condensation_amount(
        self,
        state: PrecipitationState
    ) -> float:
        """
        Calculate condensed water amount.
        """

        return round(
            state.humidity
            * state.condensation_rate,
            6
        )


    def precipitation_rate(
        self,
        state: PrecipitationState
    ) -> float:
        """
        Calculate precipitation intensity.

        Formula:

            precipitation =
            condensation
            × convection
            × efficiency
        """

        condensation = self.condensation_amount(state)

        return round(
            condensation
            * state.convection_intensity
            * state.precipitation_efficiency,
            6
        )


    def water_state(
        self,
        state: PrecipitationState
    ) -> str:
        """
        Classify atmospheric water cycle state.
        """

        rain = self.precipitation_rate(state)

        if rain > 0:
            return "active_precipitation"

        return "dry_state"

