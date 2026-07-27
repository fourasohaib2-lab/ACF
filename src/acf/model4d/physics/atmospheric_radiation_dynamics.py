"""
Atmospheric Radiation Dynamics
ACF Model4D Physics Module

Handles atmospheric radiative processes:
- Solar radiation
- Infrared emission
- Radiative balance
- Greenhouse effect
- Radiative cooling
"""


from dataclasses import dataclass


@dataclass
class RadiationState:
    solar_flux: float
    infrared_flux: float
    atmospheric_absorption: float
    greenhouse_factor: float
    surface_temperature: float
    atmospheric_temperature: float
    emissivity: float


class AtmosphericRadiationDynamics:
    """
    Atmospheric radiation physics engine.
    """


    STEFAN_BOLTZMANN = 5.67e-8


    def solar_radiation(self, state):
        """
        Incoming solar radiation.
        """

        return round(state.solar_flux, 2)



    def absorbed_radiation(self, state):
        """
        Radiation absorbed by atmosphere.
        """

        result = (
            state.solar_flux *
            state.atmospheric_absorption
        )

        return round(result, 2)



    def infrared_emission(self, state):
        """
        Infrared thermal emission.
        """

        result = (
            self.STEFAN_BOLTZMANN *
            state.surface_temperature ** 4 *
            state.emissivity
        )

        return round(result, 2)



    def outgoing_longwave_radiation(self, state):
        """
        Outgoing infrared radiation.
        """

        result = (
            state.infrared_flux *
            (1 - state.greenhouse_factor)
        )

        return round(result, 2)



    def greenhouse_effect(self, state):
        """
        Simplified greenhouse warming effect.
        """

        result = (
            state.infrared_flux *
            state.greenhouse_factor
        )

        return round(result, 2)



    def radiative_balance(self, state):
        """
        Net atmospheric radiative balance.
        """

        incoming = (
            state.solar_flux *
            state.atmospheric_absorption
        )

        outgoing = (
            state.infrared_flux *
            (1 - state.greenhouse_factor)
        )

        return round(incoming - outgoing, 2)



    def radiative_cooling(self, state):
        """
        Atmospheric cooling rate.
        """

        result = (
            state.atmospheric_temperature *
            state.emissivity *
            0.01
        )

        return round(result, 2)



    def radiative_equilibrium(self, state):
        """
        Radiative equilibrium temperature index.
        """

        result = (
            state.surface_temperature -
            state.greenhouse_factor * 10
        )

        return round(result, 2)
