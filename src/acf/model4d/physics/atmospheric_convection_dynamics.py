"""
ACF Model4D Physics

Atmospheric Convection Dynamics Module

Sprint 9.12

Simplified atmospheric convection model:
- buoyancy
- thermal instability
- vertical heat transport
- convection classification
"""

from dataclasses import dataclass


@dataclass
class ConvectionState:
    """
    Atmospheric convection parameters.
    """

    temperature_difference: float
    lapse_rate: float
    stability_threshold: float
    vertical_velocity: float
    moisture_content: float


class AtmosphericConvectionDynamics:
    """
    Simplified convection dynamics engine.
    """


    def calculate_buoyancy(
        self,
        state: ConvectionState
    ) -> float:
        """
        Estimate atmospheric buoyancy.
        """

        value = (
            state.temperature_difference
            * 0.1
        )

        return round(value, 6)


    def convection_intensity(
        self,
        state: ConvectionState
    ) -> float:
        """
        Estimate convection strength.

        Depends on:
        - vertical velocity
        - moisture
        - instability
        """

        value = (
            state.vertical_velocity
            * state.moisture_content
            * abs(state.lapse_rate)
        )

        return round(value, 6)


    def vertical_heat_transport(
        self,
        state: ConvectionState
    ) -> float:
        """
        Estimate vertical energy transport.
        """

        value = (
            self.convection_intensity(state)
            * 0.5
        )

        return round(value, 6)


    def convection_state(
        self,
        state: ConvectionState
    ) -> str:
        """
        Classify convection regime.
        """

        buoyancy = self.calculate_buoyancy(state)

        if buoyancy > state.stability_threshold:
            return "unstable_convection"

        return "stable_atmosphere"
