"""
ACF - Atmospheric Complexity Framework

Cloud Microphysics Climate Dynamics Physics Module

Sprint 9.10
"""

from dataclasses import dataclass


@dataclass
class CloudMicrophysicsState:
    """
    Cloud physical parameters.
    """

    temperature_anomaly: float
    humidity: float
    condensation_rate: float
    cloud_fraction: float
    radiative_effect: float = 1.0


class CloudMicrophysicsClimateDynamics:
    """
    Simplified cloud-climate interaction model.

    Physical chain:

        temperature
              ↓
        condensation
              ↓
        cloud formation
              ↓
        radiative feedback
    """


    def condensation(
        self,
        state: CloudMicrophysicsState
    ) -> float:
        """
        Calculate condensation production.

        Formula:

            condensation =
            humidity × condensation_rate
        """

        return round(
            state.humidity
            * state.condensation_rate,
            6
        )


    def cloud_formation(
        self,
        state: CloudMicrophysicsState
    ) -> float:
        """
        Calculate cloud formation intensity.
        """

        condensation = self.condensation(state)

        return round(
            condensation
            * state.cloud_fraction,
            6
        )


    def radiative_feedback(
        self,
        state: CloudMicrophysicsState
    ) -> float:
        """
        Calculate cloud radiative forcing.

        Formula:

            feedback =
            cloud formation × radiative effect
        """

        clouds = self.cloud_formation(state)

        return round(
            clouds
            * state.radiative_effect,
            6
        )


    def cloud_state(
        self,
        state: CloudMicrophysicsState
    ) -> str:
        """
        Classify cloud activity.
        """

        feedback = self.radiative_feedback(state)

        if feedback > 0:
            return "active_cloud_feedback"

        return "stable_cloud_state"
