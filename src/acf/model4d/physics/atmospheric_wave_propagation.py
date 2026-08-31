"""
ACF - Atmospheric Complexity Framework
Model4D Physics Module

Sprint 8.92
Atmospheric Wave Propagation Physics Module

Simulation simplifiée de la propagation des ondes atmosphériques:
- ondes de gravité
- ondes de Rossby
- propagation verticale/horizontale
- vitesse de phase
- longueur d'onde
- fréquence
"""

from dataclasses import dataclass


@dataclass
class AtmosphericWaveState:
    wavelength: float
    frequency: float
    wind_speed: float
    stability: float
    altitude: float = 0.0
    wave_type: str = "gravity"


class AtmosphericWavePropagation:
    """
    Modèle de propagation des ondes atmosphériques.
    """

    def __init__(self):
        self.name = "Atmospheric Wave Propagation"
        self.version = "8.92"

    def phase_speed(self, state: AtmosphericWaveState) -> float:
        """
        Calcule la vitesse de phase simplifiée.
        """
        if state.frequency <= 0:
            return 0.0

        return state.wavelength * state.frequency

    def intrinsic_frequency(self, state: AtmosphericWaveState) -> float:
        """
        Fréquence intrinsèque corrigée par le vent.
        """

        doppler_shift = state.wind_speed / max(state.wavelength, 1e-6)

        return max(state.frequency - doppler_shift, 0.0)

    def vertical_propagation_factor(self, state: AtmosphericWaveState) -> float:
        """
        Facteur de propagation verticale.
        """

        return state.stability * (1 + state.altitude / 10000)

    def classify_wave(self, state: AtmosphericWaveState) -> str:
        """
        Classification physique.
        """

        if state.wave_type == "rossby":
            return "Rossby wave"

        if state.stability > 5:
            return "Strong gravity wave"

        return "Atmospheric wave"

    def simulate(self, state: AtmosphericWaveState) -> dict:
        """
        Simulation complète.
        """

        return {
            "module": self.name,
            "version": self.version,
            "wave_type": self.classify_wave(state),
            "phase_speed": self.phase_speed(state),
            "intrinsic_frequency": self.intrinsic_frequency(state),
            "vertical_factor": self.vertical_propagation_factor(state),
        }
