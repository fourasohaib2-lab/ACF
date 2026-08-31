"""
ACF Model4D Physics
Planetary Climate Feedback Loops Module

Sprint 9.02
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
    Simplified planetary climate feedback model.

    Components:
        - Ice albedo feedback
        - Water vapor feedback
        - Cloud feedback
        - CO2 forcing
        - Ocean memory
    """

    def ice_albedo_feedback(self, state: ClimateFeedbackState) -> float:
        """
        Ice-albedo feedback.
        """

        return (1 - state.ice_cover) * state.temperature_anomaly

    def water_vapor_feedback(self, state: ClimateFeedbackState) -> float:
        """
        Water vapor greenhouse amplification.
        """

        return state.water_vapor * state.temperature_anomaly

    def cloud_feedback(self, state: ClimateFeedbackState) -> float:
        """
        Cloud radiative feedback.
        """

        return state.cloud_effect

    def total_feedback(self, state: ClimateFeedbackState) -> float:
        """
        Total climate feedback.

        Ocean memory is stored but
        not yet coupled in this sprint.
        """

        return (
            self.ice_albedo_feedback(state)
            + self.water_vapor_feedback(state)
            + self.cloud_feedback(state)
            + state.co2_forcing
        )

    def climate_response(self, state: ClimateFeedbackState) -> str:
        """
        Climate system response.
        """

        feedback = self.total_feedback(state)

        if feedback > 0:
            return "amplifying warming"

        if feedback < 0:
            return "cooling tendency"

        return "neutral feedback"
