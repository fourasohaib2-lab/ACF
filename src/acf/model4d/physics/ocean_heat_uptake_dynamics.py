"""
ACF - Atmospheric Complexity Framework

Ocean Heat Uptake Dynamics Physics Module

Sprint 9.07
"""

from dataclasses import dataclass


@dataclass
class OceanHeatState:
    """
    Ocean thermal state.
    """

    heat_flux: float
    ocean_capacity: float
    initial_temperature: float
    mixing_efficiency: float = 1.0


class OceanHeatUptakeDynamics:
    """
    Simplified ocean heat uptake model.

    Represents:

        temperature change =
        absorbed heat / thermal capacity
    """

    def absorbed_heat(
        self,
        state: OceanHeatState
    ) -> float:
        """
        Calculate effective ocean heat absorption.
        """

        return (
            state.heat_flux
            * state.mixing_efficiency
        )


    def temperature_change(
        self,
        state: OceanHeatState
    ) -> float:
        """
        Calculate ocean temperature response.
        """

        absorbed = self.absorbed_heat(state)

        return absorbed / state.ocean_capacity


    def future_temperature(
        self,
        state: OceanHeatState
    ) -> float:
        """
        Estimate future ocean temperature.
        """

        return (
            state.initial_temperature
            + self.temperature_change(state)
        )


    def climate_memory(
        self,
        state: OceanHeatState
    ) -> str:
        """
        Classify ocean thermal inertia.
        """

        change = self.temperature_change(state)

        if change < 1:
            return "high_memory"

        return "low_memory"
