"""
ACF - Atmospheric Complexity Framework
Model 4D Physics Engine

Earth System Coupled Dynamics Module
Sprint 9.00

Couples:
- Atmosphere
- Ocean
- Cryosphere
- Biosphere
- Land surface
- Energy exchanges
"""


from dataclasses import dataclass


@dataclass
class EarthSystemState:
    """
    Global Earth system state representation.
    """

    atmospheric_energy: float
    ocean_energy: float
    ice_fraction: float
    greenhouse_forcing: float
    biosphere_activity: float = 1.0


class EarthSystemCoupledDynamics:
    """
    Earth system coupled dynamics engine.

    Represents simplified interactions between
    atmospheric, oceanic and climate components.
    """

    def __init__(self):
        self.name = "Earth System Coupled Dynamics"
        self.version = "1.0"

    def calculate_energy_balance(
        self,
        state: EarthSystemState
    ) -> float:
        """
        Calculate simplified planetary energy balance.
        """

        absorbed = (
            state.atmospheric_energy
            + state.ocean_energy
            + state.greenhouse_forcing
        )

        losses = (
            state.ice_fraction * 10
            + state.biosphere_activity
        )

        return absorbed - losses


    def simulate(
        self,
        state: EarthSystemState,
        timestep: float = 1.0
    ):
        """
        Perform one coupled Earth system step.
        """

        balance = self.calculate_energy_balance(state)

        new_atmosphere = (
            state.atmospheric_energy
            + balance * 0.1 * timestep
        )

        new_ocean = (
            state.ocean_energy
            + balance * 0.05 * timestep
        )

        new_ice = max(
            0.0,
            min(
                1.0,
                state.ice_fraction - balance * 0.001
            )
        )

        return EarthSystemState(
            atmospheric_energy=new_atmosphere,
            ocean_energy=new_ocean,
            ice_fraction=new_ice,
            greenhouse_forcing=state.greenhouse_forcing,
            biosphere_activity=state.biosphere_activity
        )


    def climate_feedback_index(
        self,
        state: EarthSystemState
    ) -> float:
        """
        Estimate coupled climate feedback strength.
        """

        return (
            state.greenhouse_forcing
            *
            (1 - state.ice_fraction)
            *
            state.biosphere_activity
        )
