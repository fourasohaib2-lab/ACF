"""
ACF Model4D Physics

Cloud Feedback Dynamics Module

Sprint 9.14

Simplified cloud-climate interaction model:
- cloud cover
- albedo effect
- greenhouse cloud effect
- radiative feedback
"""

from dataclasses import dataclass


@dataclass
class CloudState:
    """
    Cloud system parameters.
    """

    humidity: float
    convection_strength: float
    cloud_fraction: float
    solar_reflection: float
    infrared_trapping: float


class CloudFeedbackDynamics:
    """
    Simplified cloud feedback engine.
    """

    def cloud_formation(self, state: CloudState) -> float:
        """
        Estimate cloud formation potential.
        """

        value = state.humidity * state.convection_strength

        return round(value, 6)

    def albedo_effect(self, state: CloudState) -> float:
        """
        Cooling effect from reflected solar radiation.
        """

        value = state.cloud_fraction * state.solar_reflection

        return round(value, 6)

    def greenhouse_cloud_effect(self, state: CloudState) -> float:
        """
        Warming effect from infrared trapping.
        """

        value = state.cloud_fraction * state.infrared_trapping

        return round(value, 6)

    def cloud_feedback_balance(self, state: CloudState) -> float:
        """
        Net cloud climate feedback.

        Positive:
        warming

        Negative:
        cooling
        """

        value = self.greenhouse_cloud_effect(state) - self.albedo_effect(state)

        return round(value, 6)

    def feedback_state(self, state: CloudState) -> str:
        """
        Classify cloud feedback.
        """

        balance = self.cloud_feedback_balance(state)

        if balance > 0:
            return "positive_cloud_feedback"

        if balance < 0:
            return "negative_cloud_feedback"

        return "neutral_cloud_feedback"
