"""
ACF - Atmospheric Complexity Framework

Sprint 8.93
Atmospheric Wave Energy Transfer Physics Module

Simulation simplifiée du transfert énergétique
des ondes atmosphériques dans le modèle 4D.
"""

from dataclasses import dataclass


@dataclass
class WaveEnergyState:
    amplitude: float
    frequency: float
    density: float
    propagation_distance: float
    damping: float = 0.0


class AtmosphericWaveEnergyTransfer:
    """
    Modèle de transfert énergétique des ondes.
    """

    def __init__(self):
        self.name = "Atmospheric Wave Energy Transfer"
        self.version = "8.93"

    def energy_density(self, state: WaveEnergyState) -> float:
        """
        Energie simplifiée proportionnelle
        à l'amplitude et densité.
        """

        return 0.5 * state.density * state.amplitude**2

    def attenuation(self, state: WaveEnergyState) -> float:
        """
        Atténuation linéaire simplifiée (avec seuil à zéro).

        NOTE (correction - Physics Guard, docs only): the docstring
        used to say "Atténuation exponentielle" (exponential
        attenuation) but the formula below is linear
        (1 - damping*distance, floored at 0), not exponential
        (exp(-damping*distance)) - real wave/radiative attenuation is
        typically exponential, but this is a deliberately simplified
        heuristic (the explicit floor-at-zero clamp is itself a
        linear-model idiom; a true exponential decay never reaches
        exactly zero and would need no such clamp). Not changing the
        formula itself (3 existing tests lock in specific linear-model
        values, e.g. damping*distance=0.5 -> attenuation=0.5, which
        would not hold for an exponential model) - just correcting the
        docstring to describe what is actually computed.
        """

        return max(0.0, 1 - state.damping * state.propagation_distance)

    def transferred_energy(self, state: WaveEnergyState) -> float:
        """
        Energie restante après propagation.
        """

        return self.energy_density(state) * self.attenuation(state)

    def classify_transfer(self, state: WaveEnergyState) -> str:
        """
        Classification du transfert.
        """

        energy = self.transferred_energy(state)

        if energy > 100:
            return "Strong transfer"

        if energy > 10:
            return "Moderate transfer"

        return "Weak transfer"

    def simulate(self, state: WaveEnergyState) -> dict:

        return {
            "module": self.name,
            "version": self.version,
            "energy_density": self.energy_density(state),
            "attenuation": self.attenuation(state),
            "transferred_energy": self.transferred_energy(state),
            "classification": self.classify_transfer(state),
        }
