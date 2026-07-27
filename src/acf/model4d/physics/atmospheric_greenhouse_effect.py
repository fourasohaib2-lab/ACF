"""
ACF - Atmospheric Complexity Framework

Atmospheric Greenhouse Effect Physics Module

Sprint 9.05
"""

from dataclasses import dataclass


@dataclass
class GreenhouseState:
    """
    Atmospheric greenhouse parameters.
    """

    infrared_emission: float
    greenhouse_gas_factor: float
    atmospheric_reemission: float = 0.0


class AtmosphericGreenhouseEffect:
    """
    Simplified greenhouse effect model.

    Represents:

    absorbed infrared energy +
    atmospheric re-emission
    """

    def absorbed_infrared(
        self,
        state: GreenhouseState
    ) -> float:
        """
        Calculate absorbed terrestrial infrared radiation.
        """

        return (
            state.infrared_emission
            * state.greenhouse_gas_factor
        )


    def total_greenhouse_forcing(
        self,
        state: GreenhouseState
    ) -> float:
        """
        Calculate total greenhouse forcing.
        """

        absorbed = self.absorbed_infrared(state)

        return (
            absorbed
            + state.atmospheric_reemission
        )


    def climate_response(
        self,
        state: GreenhouseState
    ) -> str:
        """
        Determine thermal tendency.
        """

        forcing = self.total_greenhouse_forcing(state)

        if forcing > 0:
            return "warming"

        return "neutral"
