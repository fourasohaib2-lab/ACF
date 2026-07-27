"""
ACF - Atmospheric Complexity Framework

Cryosphere Climate Dynamics Physics Module

Sprint 9.08
"""

from dataclasses import dataclass


@dataclass
class CryosphereState:
    """
    Cryosphere parameters.

    Attributes:
        ice_cover: fraction of ice coverage (0-1)
        snow_cover: fraction of snow coverage (0-1)
        temperature_anomaly: temperature increase/decrease
        melting_rate: melting coefficient
    """

    ice_cover: float
    snow_cover: float
    temperature_anomaly: float
    melting_rate: float


class CryosphereClimateDynamics:
    """
    Simplified cryosphere-climate interaction model.

    Physical chain:

        temperature increase
                ↓
          ice melting
                ↓
        albedo reduction
                ↓
        climate warming feedback
    """


    def albedo_effect(
        self,
        state: CryosphereState
    ) -> float:
        """
        Calculate cryosphere reflectivity effect.

        Higher ice and snow coverage means
        stronger albedo cooling effect.
        """

        return round(
            state.ice_cover + state.snow_cover,
            6
        )


    def ice_loss(
        self,
        state: CryosphereState
    ) -> float:
        """
        Calculate ice loss rate.

        Formula:

            ice_loss = temperature_anomaly × melting_rate
        """

        return round(
            state.temperature_anomaly
            * state.melting_rate,
            6
        )


    def climate_feedback(
        self,
        state: CryosphereState
    ) -> float:
        """
        Calculate cryosphere warming feedback.

        Formula:

            feedback =
            ice_loss × (1 - albedo)

        """

        loss = self.ice_loss(state)

        albedo = self.albedo_effect(state)

        feedback = loss * (1 - albedo)

        return round(feedback, 6)


    def cryosphere_state(
        self,
        state: CryosphereState
    ) -> str:
        """
        Determine cryosphere condition.
        """

        loss = self.ice_loss(state)

        if loss > 0:
            return "melting"

        return "stable"
