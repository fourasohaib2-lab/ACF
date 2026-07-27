"""
ACF Model4D Physics
Planetary Climate Feedback Loops Module

Sprint 9.02

Purpose:
    Simulate major planetary climate feedback mechanisms.
"""

from dataclasses import dataclass


@dataclass
class ClimateFeedbackState:
    """
    Planetary climate feedback state.
    """

    temperature_anomaly: float
    ice_cover: float
    water_vapor: float
    cloud_effect: float
    co2_forcing: float
    ocean_memory: float


class PlanetaryClimateFeedbackLoops:
    """
    Simplified Earth climate feedback model.

    Includes:
        - ice albedo feedback
        - water vapor feedback
        - cloud feedback
        - CO2 forcing
        - ocean thermal memory
    """

    def ice_albedo_feedback(
        self,
        state: ClimateFeedbackState
    ) -> float:
        """
        Ice-albedo amplification.

        More ice:
            cooling

        Less ice:
            warming
        """

        return (1 - state.ice_cover) * state.temperature_anomaly


    def water_vapor_feedback(
        self,
        state: ClimateFeedbackState
    ) -> float:
        """
        Water vapor greenhouse amplification.
        """

        return (
            state.water_vapor
            * state.temperature_anomaly
        )


    def cloud_feedback(
        self,
        state: ClimateFeedbackState
    ) -> float:
        """
        Cloud radiative effect.
        """

        return state.cloud_effect


    def total_feedback(
        self,
        state: ClimateFeedbackState
    ) -> float:
        """
        Total climate feedback response.
        """

        return (
            self.ice_albedo_feedback(state)
            + self.water_vapor_feedback(state)
            + self.cloud_feedback(state)
            + state.co2_forcing
            + state.ocean_memory
        )


    def climate_response(
        self,
        state: ClimateFeedbackState
    ) -> str:
        """
        Determine climate evolution.
        """

        feedback = self.total_feedback(state)

        if feedback > 0:
            return "amplifying warming"

        if feedback < 0:
            return "cooling tendency"

        return "neutral feedback"
