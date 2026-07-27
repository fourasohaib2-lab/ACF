"""
ACF - Atmospheric Complexity Framework

Atmospheric Moisture Feedback Dynamics Physics Module

Sprint 9.09
"""

from dataclasses import dataclass


@dataclass
class MoistureFeedbackState:
    """
    Atmospheric moisture parameters.
    """

    temperature_anomaly: float
    ocean_evaporation: float
    humidity_level: float
    cloud_response: float
    greenhouse_effect: float = 1.0


class AtmosphericMoistureFeedbackDynamics:
    """
    Simplified atmospheric moisture feedback model.

    Physical chain:

        temperature rise
              ↓
        evaporation increase
              ↓
        humidity increase
              ↓
        greenhouse amplification
    """


    def evaporation_feedback(
        self,
        state: MoistureFeedbackState
    ) -> float:
        """
        Calculate evaporation response.

        Formula:

            evaporation =
            temperature anomaly × ocean evaporation
        """

        return round(
            state.temperature_anomaly
            * state.ocean_evaporation,
            6
        )


    def humidity_amplification(
        self,
        state: MoistureFeedbackState
    ) -> float:
        """
        Calculate atmospheric humidity amplification.
        """

        evaporation = self.evaporation_feedback(state)

        return round(
            evaporation
            * state.humidity_level,
            6
        )


    def greenhouse_feedback(
        self,
        state: MoistureFeedbackState
    ) -> float:
        """
        Calculate water vapor greenhouse feedback.

        Formula:

            feedback =
            humidity amplification
            × cloud response
            × greenhouse effect
        """

        humidity = self.humidity_amplification(state)

        return round(
            humidity
            * state.cloud_response
            * state.greenhouse_effect,
            6
        )


    def moisture_state(
        self,
        state: MoistureFeedbackState
    ) -> str:
        """
        Classify atmospheric moisture condition.
        """

        feedback = self.greenhouse_feedback(state)

        if feedback > 0:
            return "humidifying_feedback"

        return "stable"
