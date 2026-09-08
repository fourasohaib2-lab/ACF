"""
ACF - Atmospheric Complexity Framework

Sprint 8.94
Atmospheric Wave Source Generation Physics Module

Modèle simplifié de génération des sources
d'ondes atmosphériques dans Model4D.
"""

from dataclasses import dataclass


@dataclass
class WaveSourceState:
    convection_index: float
    mountain_height: float
    jet_speed: float
    frontal_gradient: float
    instability: float
    source_type: str = "convection"


class AtmosphericWaveSourceGeneration:
    """
    Générateur de sources d'ondes atmosphériques.
    """

    def __init__(self):
        self.name = "Atmospheric Wave Source Generation"
        self.version = "8.94"

    def convection_source(self, state: WaveSourceState) -> float:
        """
        Génération d'onde par convection.
        """

        return state.convection_index * state.instability

    def orographic_source(self, state: WaveSourceState) -> float:
        """
        Génération d'ondes par relief montagneux.
        """

        return state.mountain_height * state.jet_speed / 1000

    def frontal_source(self, state: WaveSourceState) -> float:
        """
        Génération par gradient frontal.
        """

        return state.frontal_gradient * state.instability

    def jet_source(self, state: WaveSourceState) -> float:
        """
        Génération par jet stream.
        """

        return state.jet_speed**2 / 100

    def total_source_energy(self, state: WaveSourceState) -> float:
        """
        Energie totale générée.
        """

        if state.source_type == "mountain":
            return self.orographic_source(state)

        if state.source_type == "front":
            return self.frontal_source(state)

        if state.source_type == "jet":
            return self.jet_source(state)

        return self.convection_source(state)

    def classify_source(self, state: WaveSourceState) -> str:
        """
        Classification de la source.
        """

        energy = self.total_source_energy(state)

        if energy > 500:
            return "Strong wave source"

        if energy > 100:
            return "Moderate wave source"

        return "Weak wave source"

    def simulate(self, state: WaveSourceState) -> dict:
        """
        Simulation complète.
        """

        return {
            "module": self.name,
            "version": self.version,
            "source_type": state.source_type,
            "energy": self.total_source_energy(state),
            "classification": self.classify_source(state),
        }
