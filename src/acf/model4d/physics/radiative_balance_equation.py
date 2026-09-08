"""
ACF - Atmospheric Complexity Framework

Radiative Balance Equation Physics Module

Sprint 9.04
"""

from dataclasses import dataclass


@dataclass
class RadiativeBalanceState:
    """
    Planetary radiation state.
    """

    solar_input: float
    albedo: float
    outgoing_longwave: float


class RadiativeBalanceEquation:
    """
    Simplified planetary energy balance model.

    Net balance:

        absorbed solar energy - outgoing radiation
    """

    def absorbed_solar_energy(self, state: RadiativeBalanceState) -> float:
        """
        Calculate absorbed solar radiation.
        """

        return state.solar_input * (1 - state.albedo)

    def energy_balance(self, state: RadiativeBalanceState) -> float:
        """
        Calculate planetary energy imbalance.
        """

        absorbed = self.absorbed_solar_energy(state)

        return absorbed - state.outgoing_longwave

    def climate_state(self, state: RadiativeBalanceState) -> str:
        """
        Classify climate equilibrium.
        """

        balance = self.energy_balance(state)

        if balance > 0:
            return "warming"

        if balance < 0:
            return "cooling"

        return "equilibrium"
