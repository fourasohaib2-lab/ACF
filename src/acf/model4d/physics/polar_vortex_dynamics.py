"""
ACF Model4D Physics
Polar Vortex Dynamics Module

Sprint 8.88

Simulation conceptuelle :
- vortex polaire stratosphérique
- circulation zonale
- stabilité du vortex
- réchauffement stratosphérique soudain
- transport polaire d'énergie
"""


from dataclasses import dataclass
from math import exp


@dataclass
class PolarVortexState:
    """
    Etat du vortex polaire.
    """

    wind_speed: float
    temperature_gradient: float
    stability_index: float
    hemisphere: str = "north"


class PolarVortexDynamics:
    """
    Modèle dynamique simplifié du vortex polaire.
    """

    def __init__(self):
        self.name = "Polar Vortex Dynamics"
        self.version = "8.88"

    def calculate_vortex_strength(
        self,
        wind_speed: float,
        temperature_gradient: float
    ) -> float:
        """
        Calcule une intensité normalisée du vortex.

        Plus le gradient thermique et le vent zonal
        sont élevés, plus le vortex est fort.
        """

        strength = (
            wind_speed *
            temperature_gradient
        ) / 100.0

        return round(strength, 4)


    def diagnose_stability(
        self,
        strength: float
    ) -> str:
        """
        Classification stabilité vortex.
        """

        if strength >= 5:
            return "stable"

        if strength >= 2:
            return "moderate"

        return "weak"


    def sudden_stratospheric_warming_effect(
        self,
        temperature_increase: float
    ) -> float:
        """
        Impact simplifié d'un SSW.

        Une augmentation de température
        réduit la force du vortex.
        """

        reduction = exp(
            -temperature_increase / 10
        )

        return round(reduction, 4)


    def simulate(
        self,
        state: PolarVortexState
    ) -> dict:
        """
        Simulation complète.
        """

        strength = self.calculate_vortex_strength(
            state.wind_speed,
            state.temperature_gradient
        )

        return {
            "module": self.name,
            "version": self.version,
            "hemisphere": state.hemisphere,
            "strength": strength,
            "stability": self.diagnose_stability(
                strength
            )
        }


def create_polar_vortex_model():
    """
    Factory ACF.
    """

    return PolarVortexDynamics()
