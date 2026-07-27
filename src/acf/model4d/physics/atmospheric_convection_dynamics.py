"""
ACF Model4D Physics

Atmospheric Convection Dynamics Module

Sprint 9.12

Simplified atmospheric convection physics:
- buoyancy
- instability
- convective available energy
- vertical heat transport
- convection classification
"""

from dataclasses import dataclass


@dataclass
class ConvectionState:
    """
    Atmospheric convection state.
    """

    temperature_anomaly: float
    lapse_rate: float
    environmental_lapse_rate: float
    moisture_content: float
    vertical_velocity: float



class AtmosphericConvectionDynamics:
    """
    Simplified convection dynamics engine.
    """


    def calculate_buoyancy(
        self,
        state: ConvectionState
    ) -> float:
        """
        Calculate thermal buoyancy.

        Positive value:
        rising air

        Negative value:
        sinking air
        """

        value = (
            state.temperature_anomaly
            * 0.1
        )

        return round(value, 6)



    def instability_index(
        self,
        state: ConvectionState
    ) -> float:
        """
        Estimate atmospheric instability.

        Difference between:
        - environmental lapse rate
        - parcel lapse rate
        """

        value = (
            state.environmental_lapse_rate
            -
            state.lapse_rate
        )

        return round(value, 6)



    def convective_energy(
        self,
        state: ConvectionState
    ) -> float:
        """
        Estimate convective available energy.

        Simplified CAPE representation.
        """

        buoyancy = self.calculate_buoyancy(state)

        value = (
            max(buoyancy, 0)
            *
            state.moisture_content
        )

        return round(value, 6)



    def vertical_heat_transport(
        self,
        state: ConvectionState
    ) -> float:
        """
        Estimate vertical heat transport.
        """

        value = (
            state.vertical_velocity
            *
            state.moisture_content
            *
            0.5
        )

        return round(value, 6)



    def convection_state(
        self,
        state: ConvectionState
    ) -> str:
        """
        Atmospheric convection regime.
        """

        instability = self.instability_index(state)

        if instability > 0:
            return "unstable_convection"

        return "stable_atmosphere"
