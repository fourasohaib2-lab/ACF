"""
Atmospheric Precipitation Dynamics
Sprint 9.21

Module de dynamique des précipitations atmosphériques :
- formation pluie/neige/grêle
- transitions de phase eau-glace
- accumulation
- interaction nuages-précipitations
"""

from dataclasses import dataclass


@dataclass
class PrecipitationState:
    cloud_water: float
    ice_content: float
    temperature: float
    vertical_velocity: float
    humidity: float
    aerosol_loading: float



class AtmosphericPrecipitationDynamics:


    def __init__(self):
        self.name = "Atmospheric Precipitation Dynamics"
        self.version = "9.21"



    def precipitation_formation(
        self,
        state: PrecipitationState
    ) -> float:
        """
        Formation des précipitations.
        """

        result = (
            state.cloud_water
            +
            state.ice_content
            -
            state.aerosol_loading
            / 3
        )

        return round(result, 1)



    def rainfall_rate(
        self,
        state: PrecipitationState
    ) -> float:
        """
        Taux de pluie.
        """

        if state.temperature > 0:

            result = (
                state.cloud_water
                *
                state.humidity
                *
                0.001
            )

            return round(result, 1)

        return 0.0



    def snowfall_rate(
        self,
        state: PrecipitationState
    ) -> float:
        """
        Taux de neige.
        """

        if state.temperature <= 0:

            return round(
                state.ice_content,
                1
            )

        return 0.0



    def hail_probability(
        self,
        state: PrecipitationState
    ) -> float:
        """
        Probabilité de grêle.
        """

        result = (
            state.vertical_velocity
            *
            state.ice_content
            *
            0.01
        )

        return round(result, 1)



    def phase_transition(
        self,
        state: PrecipitationState
    ) -> int:
        """
        Transition de phase eau/glace.
        """

        result = int(
            state.ice_content
        )

        return result



    def precipitation_accumulation(
        self,
        state: PrecipitationState
    ) -> int:
        """
        Accumulation totale.
        """

        result = (
            state.cloud_water
            +
            state.ice_content
        )

        return int(result)



    def cloud_precipitation_interaction(
        self,
        state: PrecipitationState
    ) -> float:
        """
        Interaction nuage-précipitation.
        """

        result = (
            state.aerosol_loading
            *
            0.12
        )

        return round(result, 1)
