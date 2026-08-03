"""
ACF - Atmospheric Wave Coupling Physics Module

Sprint 8.91

Simulation simplified des interactions entre:
- ondes atmosphériques
- gravité
- convection
- turbulence
- transport d'énergie

Module destiné au modèle 4D Atmospheric Complexity Framework.
"""

from dataclasses import dataclass


@dataclass
class AtmosphericWaveState:
    """
    Etat d'une onde atmosphérique.
    """

    amplitude: float
    wavelength: float
    frequency: float
    wind_speed: float = 0.0
    altitude: float = 0.0


class AtmosphericWaveCoupling:
    """
    Modèle de couplage des ondes atmosphériques.
    """

    def __init__(self):
        self.gravity = 9.80665

    def phase_speed(self, state: AtmosphericWaveState):
        """
        Calcule la vitesse de phase simplifiée.

        c = wavelength * frequency
        """

        return state.wavelength * state.frequency


    def wave_energy(self, state: AtmosphericWaveState):
        """
        Energie relative de l'onde.
        """

        return 0.5 * state.amplitude ** 2


    def gravity_wave_effect(self, state: AtmosphericWaveState):
        """
        Influence gravitationnelle verticale.
        """

        return self.gravity * state.amplitude


    def wind_coupling(self, state: AtmosphericWaveState):
        """
        Interaction vent-onde.
        """

        return state.wind_speed * state.frequency


    def coupling_index(self, state: AtmosphericWaveState):
        """
        Indice global de couplage.
        """

        return (
            self.wave_energy(state)
            + self.wind_coupling(state)
            + self.gravity_wave_effect(state)
        )


    def simulate(self, state: AtmosphericWaveState):
        """
        Simulation complète.
        """

        return {
            "phase_speed": self.phase_speed(state),
            "energy": self.wave_energy(state),
            "gravity_effect": self.gravity_wave_effect(state),
            "wind_coupling": self.wind_coupling(state),
            "coupling_index": self.coupling_index(state),
        }
