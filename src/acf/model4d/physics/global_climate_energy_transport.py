"""
ACF Model4D Physics
Global Climate Energy Transport Module

Sprint 9.01

Purpose:
    Simulate simplified planetary climate energy transport.
"""

from dataclasses import dataclass


@dataclass
class ClimateEnergyState:
    """
    Global climate energy state.
    """

    solar_input: float
    outgoing_longwave: float
    ocean_transport: float
    atmospheric_transport: float
    albedo: float = 0.3


class GlobalClimateEnergyTransport:
    """
    Simplified Earth energy transport model.

    Represents:
        - incoming solar radiation
        - reflected radiation
        - atmospheric heat transport
        - ocean heat transport
        - planetary balance
    """

    SOLAR_CONSTANT = 1361.0

    def absorbed_solar_energy(self, state: ClimateEnergyState) -> float:
        """
        Calculate absorbed solar energy.
        """
        return state.solar_input * (1 - state.albedo)

    def total_heat_transport(self, state: ClimateEnergyState) -> float:
        """
        Atmospheric + ocean heat transport.
        """
        return (
            state.ocean_transport
            + state.atmospheric_transport
        )

    def energy_balance(self, state: ClimateEnergyState) -> float:
        """
        Planetary energy imbalance.

        Positive:
            warming tendency

        Negative:
            cooling tendency
        """

        absorbed = self.absorbed_solar_energy(state)

        loss = (
            state.outgoing_longwave
            + self.total_heat_transport(state)
        )

        return absorbed - loss

    def climate_trend(self, state: ClimateEnergyState) -> str:
        """
        Determine climate tendency.
        """

        balance = self.energy_balance(state)

        if balance > 0:
            return "warming"

        if balance < 0:
            return "cooling"

        return "balanced"
