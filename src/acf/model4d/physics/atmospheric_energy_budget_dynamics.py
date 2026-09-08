"""
Atmospheric Energy Budget Dynamics
----------------------------------

ACF Model4D Physics Module

Sprint 9.23
"""

from dataclasses import dataclass


@dataclass
class EnergyBudgetState:
    """
    Atmospheric energy state.
    """

    solar_input: float
    infrared_loss: float
    latent_heat: float
    sensible_heat: float
    surface_flux: float
    cloud_effect: float
    temperature: float


class AtmosphericEnergyBudgetDynamics:
    """
    Simplified atmospheric energy budget model.

    Represents:
    - solar absorption
    - infrared cooling
    - latent heat transport
    - sensible heat exchange
    - surface coupling
    - cloud feedback
    """

    def __init__(self):

        self.name = "Atmospheric Energy Budget Dynamics"

    def solar_energy_gain(self, state: EnergyBudgetState) -> float:
        """
        Incoming solar energy contribution.
        """

        return round(state.solar_input / 20, 2)

    def infrared_cooling(self, state: EnergyBudgetState) -> float:
        """
        Atmospheric infrared energy loss.
        """

        return round(state.infrared_loss / 20, 2)

    def latent_heat_transport(self, state: EnergyBudgetState) -> float:
        """
        Latent heat transport by water cycle.
        """

        return round(state.latent_heat / 5, 2)

    def sensible_heat_transport(self, state: EnergyBudgetState) -> float:
        """
        Sensible heat exchange.
        """

        return round(state.sensible_heat / 5, 2)

    def surface_energy_flux(self, state: EnergyBudgetState) -> float:
        """
        Surface-atmosphere energy exchange.
        """

        return round(state.surface_flux / 10, 2)

    def cloud_energy_feedback(self, state: EnergyBudgetState) -> float:
        """
        Cloud radiative feedback.
        """

        return round(state.cloud_effect / 2, 2)

    def atmospheric_energy_balance(self, state: EnergyBudgetState) -> float:
        """
        Complete energy budget.

        Formula:

        Gain:
        solar
        + latent
        + sensible
        + surface

        Loss:
        infrared
        - cloud feedback
        """

        balance = (
            self.solar_energy_gain(state)
            + self.latent_heat_transport(state)
            + self.sensible_heat_transport(state)
            + self.surface_energy_flux(state)
            - self.infrared_cooling(state)
            + self.cloud_energy_feedback(state)
        )

        return round(balance, 2)

    def equilibrium_temperature(self, state: EnergyBudgetState) -> float:
        """
        Estimate atmospheric equilibrium temperature.
        """

        energy = self.atmospheric_energy_balance(state)

        return round(state.temperature + energy * 0.1, 2)

    def climate_feedback_index(self, state: EnergyBudgetState) -> float:
        """
        Combined climate feedback indicator.
        """

        index = (state.cloud_effect + state.surface_flux - state.infrared_loss) / 10

        return round(index, 2)
