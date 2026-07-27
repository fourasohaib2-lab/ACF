"""
ACF - Atmospheric Complexity Framework

Atmospheric Convection Dynamics Physics Module

Sprint 9.12
"""

from dataclasses import dataclass


@dataclass
class ConvectionState:
    """
    Atmospheric convection parameters.
    """

    surface_temperature_anomaly: float
    lapse_rate: float
    stability_index: float
    moisture_content: float
    convection_efficiency: float = 1.0


class AtmosphericConvectionDynamics:
    """
    Simplified atmospheric convection model.

    Physical chain:

        surface heating
              ↓
        instability
              ↓
        vertical motion
              ↓
        convection feedback
    """


    def buoyancy_force(
        self,
        state: ConvectionState
    ) -> float:
        """
        Calculate atmospheric buoyancy.

        Formula:

            buoyancy =
            temperature anomaly × lapse rate
        """

        return round(
            state.surface_temperature_anomaly
            * state.lapse_rate,
            6
        )


    def vertical_velocity(
        self,
        state: ConvectionState
    ) -> float:
        """
        Calculate vertical atmospheric motion.

        Formula:

            velocity =
            buoyancy × instability
        """

        buoyancy = self.buoyancy_force(state)

        return round(
            buoyancy
            * state.stability_index,
            6
        )


    def convection_feedback(
        self,
        state: ConvectionState
    ) -> float:
        """
        Calculate convective energy transport.

        Formula:

            feedback =
            vertical velocity
            × moisture
            × efficiency
        """

        velocity = self.vertical_velocity(state)

        return round(
            velocity
            * state.moisture_content
            * state.convection_efficiency,
            6
        )


    def convection_state(
        self,
        state: ConvectionState
    ) -> str:
        """
        Classify atmospheric convection.
        """

        velocity = self.vertical_velocity(state)

        if velocity > 0:
            return "active_convection"

        return "stable_atmosphere"
