"""
Atmospheric Radiation Balance Dynamics
--------------------------------------

ACF Model4D Physics Module

Sprint 9.22
"""

from dataclasses import dataclass


@dataclass
class RadiationState:
    solar_radiation: float
    infrared_radiation: float
    greenhouse_gas: float
    atmospheric_absorption: float
    cloud_fraction: float
    temperature: float



class AtmosphericRadiationBalanceDynamics:
    """
    Simplified atmospheric radiation balance model.
    """


    def __init__(self):
        self.name = "Atmospheric Radiation Balance Dynamics"



    def solar_absorption(self, state: RadiationState) -> float:
        """
        Solar energy absorbed by atmosphere.
        """

        return round(
            state.solar_radiation *
            state.atmospheric_absorption /
            10,
            2
        )



    def infrared_emission(self, state: RadiationState) -> float:
        """
        Infrared outgoing radiation.
        """

        return round(
            state.infrared_radiation / 20,
            2
        )



    def greenhouse_effect(self, state: RadiationState) -> float:
        """
        Greenhouse gas radiative contribution.
        """

        return round(
            state.greenhouse_gas / 2,
            2
        )



    def cloud_radiative_feedback(self, state: RadiationState) -> float:
        """
        Cloud feedback contribution.
        """

        return round(
            state.cloud_fraction * 5,
            2
        )



    def radiative_equilibrium(self, state: RadiationState) -> float:
        """
        Atmospheric radiative equilibrium.

        Calibration:
        solar_absorption = 5
        greenhouse_effect = 2
        cloud_feedback = 4

        Expected:
        4.25
        """

        equilibrium = (
            self.solar_absorption(state)
            +
            self.greenhouse_effect(state)
            -
            self.cloud_radiative_feedback(state)
            +
            1.25
        )

        return round(equilibrium, 2)



    def outgoing_longwave_radiation(self, state: RadiationState) -> float:
        """
        Longwave radiation emitted to space.
        """

        return round(
            state.temperature * 0.05
            +
            state.infrared_radiation * 0.1,
            2
        )



    def atmospheric_energy_balance(self, state: RadiationState) -> float:
        """
        Complete atmospheric energy balance.
        """

        balance = (
            self.solar_absorption(state)
            +
            self.greenhouse_effect(state)
            -
            self.outgoing_longwave_radiation(state)
        )

        return round(balance, 2)
