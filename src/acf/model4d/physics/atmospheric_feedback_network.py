"""
ACF Model4D
Atmospheric Feedback Network Engine

Sprint 9.28

Gestion des boucles de rétroaction atmosphériques :
- humidité
- radiation
- nuages
- température
- surface
- océan-atmosphère
"""

from dataclasses import dataclass


@dataclass
class FeedbackState:
    temperature: float
    humidity: float
    cloud_cover: float
    radiation: float
    surface_temperature: float
    ocean_temperature: float


class AtmosphericFeedbackNetwork:
    """
    Atmospheric feedback coupling system
    """

    def __init__(self):
        self.name = "Atmospheric Feedback Network Engine"
        self.version = "0.1.0"


    def moisture_feedback(self, state: FeedbackState):
        """
        Humidity-temperature feedback
        """

        feedback = (
            state.humidity * 0.02
            +
            state.temperature * 0.001
        )

        return round(feedback, 2)


    def radiative_feedback(self, state: FeedbackState):
        """
        Radiation feedback
        """

        feedback = (
            state.radiation * 0.01
            -
            state.cloud_cover * 0.005
        )

        return round(feedback, 2)


    def cloud_feedback(self, state: FeedbackState):
        """
        Cloud-radiation interaction
        """

        feedback = (
            state.cloud_cover * 0.03
        )

        return round(feedback, 2)


    def temperature_feedback(self, state: FeedbackState):
        """
        Temperature amplification loop
        """

        feedback = (
            state.temperature * 0.005
            +
            state.surface_temperature * 0.003
        )

        return round(feedback, 2)


    def surface_feedback(self, state: FeedbackState):
        """
        Land-atmosphere interaction
        """

        feedback = (
            state.surface_temperature
            -
            state.temperature
        )

        return round(feedback, 2)


    def ocean_atmosphere_feedback(self, state: FeedbackState):
        """
        Ocean atmosphere coupling
        """

        feedback = (
            state.ocean_temperature
            -
            state.temperature
        ) * 0.1

        return round(feedback, 2)


    def feedback_equilibrium(self, state: FeedbackState):
        """
        Total atmospheric feedback equilibrium
        """

        total = (
            self.moisture_feedback(state)
            +
            self.radiative_feedback(state)
            +
            self.cloud_feedback(state)
            +
            self.temperature_feedback(state)
            +
            self.surface_feedback(state)
            +
            self.ocean_atmosphere_feedback(state)
        )

        return round(total, 2)
