"""
ACF - Atmospheric Complexity Framework

Atmospheric Gravity Waves Dynamics
Sprint 8.85

Modèle simplifié des ondes de gravité atmosphériques :
- génération par perturbations verticales
- fréquence de Brunt-Väisälä
- vitesse de propagation
- énergie ondulatoire
- dissipation
"""

from dataclasses import dataclass
from math import pi


@dataclass
class GravityWaveState:
    """
    Etat physique d'une onde de gravité atmosphérique.
    """

    stability_frequency: float
    amplitude: float
    wavelength: float
    wind_speed: float
    density: float
    dissipation_rate: float


class AtmosphericGravityWave:
    """
    Modèle dynamique d'une onde de gravité atmosphérique.
    """

    def __init__(self, state: GravityWaveState):
        self.state = state

    def phase_speed(self) -> float:
        """
        Vitesse de phase de l'onde.
        """

        if self.state.wavelength <= 0:
            return 0.0

        return self.state.stability_frequency * self.state.wavelength / (2 * pi)

    def energy(self) -> float:
        """
        Energie simplifiée de l'onde.
        """

        return 0.5 * self.state.density * self.state.amplitude**2

    def propagation_speed(self) -> float:
        """
        Vitesse totale de propagation.
        """

        return self.phase_speed() + self.state.wind_speed

    def vertical_displacement(self) -> float:
        """
        Déplacement vertical maximal.
        """

        return self.state.amplitude

    def dissipation(self) -> float:
        """
        Perte énergétique.
        """

        return self.energy() * self.state.dissipation_rate

    def simulate(self) -> dict:
        """
        Simulation complète.
        """

        return {
            "phase_speed": self.phase_speed(),
            "energy": self.energy(),
            "propagation_speed": self.propagation_speed(),
            "vertical_displacement": self.vertical_displacement(),
            "dissipation": self.dissipation(),
        }


def create_example_wave():
    """
    Exemple réaliste d'onde de gravité.
    """

    state = GravityWaveState(
        stability_frequency=0.02,
        amplitude=120,
        wavelength=50000,
        wind_speed=15,
        density=1.2,
        dissipation_rate=0.05,
    )

    return AtmosphericGravityWave(state)
