"""
ACF Model4D Physics Module

Polar Vortex Dynamics
=====================

Simulation simplifiée de la dynamique des vortex polaires
dans la stratosphère.

Concepts :
- vitesse des vents stratosphériques
- gradient thermique polaire
- stabilité atmosphérique
- hémisphère nord/sud
- intensité du vortex
"""

from dataclasses import dataclass


@dataclass
class PolarVortexState:
    """
    Etat physique du vortex polaire.
    """

    wind_speed: float
    temperature_gradient: float
    stability_index: float = 1.0
    hemisphere: str = "north"


class PolarVortexDynamics:
    """
    Modèle dynamique simplifié du vortex polaire.
    """

    def __init__(self):
        self.name = "Polar Vortex Dynamics"
        self.version = "1.0"

    def calculate_intensity(self, state: PolarVortexState) -> float:
        """
        Calcule une intensité normalisée du vortex.

        Plus :
        - le vent est fort
        - le gradient thermique est élevé
        - la stabilité est importante

        plus le vortex est intense.
        """

        intensity = state.wind_speed * state.temperature_gradient * state.stability_index

        return round(intensity, 3)

    def simulate(self, state: PolarVortexState) -> dict:
        """
        Simulation complète du vortex.
        """

        intensity = self.calculate_intensity(state)

        if intensity >= 500:
            status = "strong"
        elif intensity >= 200:
            status = "moderate"
        else:
            status = "weak"

        return {
            "name": self.name,
            "hemisphere": state.hemisphere,
            "wind_speed": state.wind_speed,
            "temperature_gradient": state.temperature_gradient,
            "stability_index": state.stability_index,
            "intensity": intensity,
            "status": status,
        }

    def hemisphere_effect(self, state: PolarVortexState) -> str:
        """
        Effet saisonnier simplifié selon l'hémisphère.
        """

        if state.hemisphere.lower() == "north":
            return "Arctic polar vortex"

        if state.hemisphere.lower() == "south":
            return "Antarctic polar vortex"

        return "unknown hemisphere"
