"""
ACF - Atmospheric Complexity Framework
Model 4D Physics Module

Mesoscale Convective Systems (MCS) Dynamics
Sprint 8.84

Description:
    Simulation simplifiée des systèmes convectifs de méso-échelle :
    - organisation convective
    - durée de vie
    - intensité précipitationnelle
    - énergie convective
    - propagation du système
"""

from dataclasses import dataclass
from math import sqrt


@dataclass
class MCSState:
    """
    Etat physique d'un système convectif de méso-échelle.
    """

    cape: float
    wind_shear: float
    moisture: float
    temperature: float
    precipitation_rate: float
    organization: float


class MesoscaleConvectiveSystem:
    """
    Modèle simplifié d'un MCS atmosphérique.
    """

    def __init__(self, state: MCSState):
        self.state = state

    def convective_energy(self) -> float:
        """
        Energie convective disponible.

        CAPE × humidité normalisée
        """

        return self.state.cape * (self.state.moisture / 100)

    def organization_index(self) -> float:
        """
        Organisation du système convectif.

        Combine cisaillement et organisation interne.
        """

        return self.state.wind_shear * 0.5 + self.state.organization * 0.5

    def precipitation_intensity(self) -> float:
        """
        Intensité potentielle des précipitations.
        """

        energy = self.convective_energy()

        return sqrt(max(energy, 0)) + self.state.moisture * 0.05

    def propagation_speed(self) -> float:
        """
        Vitesse de propagation du MCS.

        Influence du cisaillement et de l'énergie.
        """

        return self.state.wind_shear + sqrt(max(self.convective_energy(), 0))

    def stability_index(self) -> float:
        """
        Indice de stabilité atmosphérique.
        """

        return self.state.temperature - self.state.cape * 0.01

    def simulate(self) -> dict:
        """
        Retourne l'état simulé.
        """

        return {
            "convective_energy": self.convective_energy(),
            "organization": self.organization_index(),
            "precipitation": self.precipitation_intensity(),
            "propagation_speed": self.propagation_speed(),
            "stability": self.stability_index(),
        }


def create_example_mcs():
    """
    Exemple réaliste d'un système convectif.
    """

    state = MCSState(
        cape=1800,
        wind_shear=25,
        moisture=75,
        temperature=290,
        precipitation_rate=20,
        organization=80,
    )

    return MesoscaleConvectiveSystem(state)
