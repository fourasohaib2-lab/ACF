"""
Atmospheric Precipitation Dynamics
Sprint 9.21
"""

from dataclasses import dataclass


@dataclass
class PrecipitationState:
    humidity: float
    condensation_rate: float
    convection_intensity: float
    precipitation_efficiency: float = 1.0


class AtmosphericPrecipitationDynamics:

    def __init__(self):
        self.name = "Atmospheric Precipitation Dynamics"
        self.version = "9.21"


    def condensation_amount(self, state: PrecipitationState) -> float:
        """
        Formation de condensation.
        """

        result = (
            state.humidity
            * state.condensation_rate
            * 0.1
        )

        return round(result, 2)


    def precipitation_rate(self, state: PrecipitationState) -> float:
        """
        Taux de précipitation.
        """

        result = (
            state.humidity
            * state.condensation_rate
            * state.convection_intensity
            * state.precipitation_efficiency
            * 0.1
        )

        return round(result, 2)


    def precipitation_efficiency(
        self,
        state: PrecipitationState
    ) -> float:
        """
        Rendement conversion nuage → pluie.
        """

        result = (
            state.condensation_rate
            * state.convection_intensity
            * state.precipitation_efficiency
        )

        return round(result, 2)


    def water_state(self, state: PrecipitationState) -> float:
        """
        Etat de l'eau atmosphérique.
        """

        result = (
            state.humidity
            * state.condensation_rate
        )

        return round(result, 2)


    def cloud_conversion(
        self,
        state: PrecipitationState
    ) -> float:
        """
        Conversion eau nuageuse vers hydrométéores.
        """

        result = (
            state.humidity
            * state.precipitation_efficiency
            * 0.05
        )

        return round(result, 2)
