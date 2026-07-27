"""
ACF Model4D Physics
Atmospheric Radiative Balance Module

Sprint 9.05

Represents simplified atmospheric energy balance:
- incoming solar radiation
- outgoing longwave radiation
- greenhouse forcing
- atmospheric absorption
"""

from dataclasses import dataclass


@dataclass
class RadiativeState:
    solar_input: float
    infrared_output: float
    greenhouse_forcing: float
    atmospheric_absorption: float


class AtmosphericRadiativeBalance:
    """
    Simplified atmospheric radiative balance model.
    """

    def net_radiation(self, state: RadiativeState) -> float:
        """
        Net radiation balance.

        Positive:
        warming tendency

        Negative:
        cooling tendency
        """

        value = (
            state.solar_input
            - state.infrared_output
            + state.greenhouse_forcing
            + state.atmospheric_absorption
        )

        return round(value, 6)


    def greenhouse_effect(self, state: RadiativeState) -> float:
        """
        Estimates greenhouse contribution.
        """

        value = (
            state.greenhouse_forcing
            * (1 + state.atmospheric_absorption)
        )

        return round(value, 6)


    def energy_balance_status(self, state: RadiativeState) -> str:
        """
        Classifies climate energy state.
        """

        balance = self.net_radiation(state)

        if balance > 0:
            return "warming"

        if balance < 0:
            return "cooling"

        return "balanced"
