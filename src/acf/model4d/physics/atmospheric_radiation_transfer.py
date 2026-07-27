from dataclasses import dataclass


@dataclass
class RadiationState:
    solar_input: float
    infrared_output: float
    atmospheric_absorption: float
    greenhouse_gas_effect: float
    aerosol_loading: float
    surface_temperature: float


class AtmosphericRadiationTransfer:
    """
    Simplified atmospheric radiation transfer model
    for ACF Model 4D physics engine.
    """

    def solar_radiation_absorption(self, state: RadiationState) -> float:
        """
        Incoming solar radiation absorbed by atmosphere.
        """

        return round(
            state.solar_input
            * state.atmospheric_absorption,
            2
        )

    def infrared_trapping(self, state: RadiationState) -> float:
        """
        Greenhouse infrared trapping effect.
        """

        return round(
            state.infrared_output
            * state.greenhouse_gas_effect,
            2
        )

    def rayleigh_scattering(self, state: RadiationState) -> float:
        """
        Simplified Rayleigh scattering.
        """

        return round(
            state.solar_input
            * 0.1
            *
            (1 + state.aerosol_loading),
            2
        )

    def outgoing_longwave_radiation(self, state: RadiationState) -> float:
        """
        Surface longwave emission.
        """

        return round(
            state.infrared_output
            *
            (state.surface_temperature / 300),
            2
        )

    def greenhouse_feedback(self, state: RadiationState) -> float:
        """
        Positive greenhouse radiative feedback.
        """

        return round(
            state.greenhouse_gas_effect
            *
            state.surface_temperature
            /
            100,
            2
        )

    def radiative_energy_balance(self, state: RadiationState) -> float:
        """
        Global atmospheric radiative balance.

        Positive value:
        warming tendency.

        Negative value:
        cooling tendency.
        """

        absorbed = (
            state.solar_input
            * state.atmospheric_absorption
        )

        trapped = (
            state.infrared_output
            * state.greenhouse_gas_effect
        )

        return round(
            absorbed
            - state.infrared_output
            + trapped,
            2
        )

