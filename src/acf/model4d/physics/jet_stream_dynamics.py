"""
ACF Model4D Physics Module
Jet Stream Dynamics

Simulation simplifiée des courants-jets atmosphériques :
- vitesse du jet
- gradient thermique
- cisaillement vertical
- stabilité dynamique
- influence sur circulation générale
"""

import math
from dataclasses import dataclass


@dataclass
class JetStreamState:
    """
    Etat dynamique d'un courant-jet.
    """

    wind_speed: float
    temperature_gradient: float
    vertical_shear: float
    latitude: float


class JetStreamDynamics:
    """
    Modèle simplifié de dynamique des courants-jets.
    """

    def __init__(self, state: JetStreamState):
        self.state = state

    def coriolis_parameter(self):
        """
        Paramètre de Coriolis simplifié.
        """

        omega = 7.2921e-5

        latitude_rad = math.radians(self.state.latitude)

        return 2 * omega * math.sin(latitude_rad)

    def thermal_wind_balance(self):
        """
        Approximation équilibre vent thermique.
        """

        return self.state.temperature_gradient * self.state.vertical_shear

    def jet_intensity(self):
        """
        Intensité dynamique du courant-jet.
        """

        coriolis = abs(self.coriolis_parameter())

        return self.state.wind_speed * coriolis * (1 + self.state.vertical_shear)

    def blocking_risk(self):
        """
        Risque de blocage atmosphérique.
        """

        instability = self.state.vertical_shear - self.state.temperature_gradient

        return max(0.0, min(1.0, instability))

    def diagnostic(self):
        """
        Diagnostic complet.
        """

        return {
            "wind_speed": self.state.wind_speed,
            "coriolis": self.coriolis_parameter(),
            "thermal_balance": self.thermal_wind_balance(),
            "jet_intensity": self.jet_intensity(),
            "blocking_risk": self.blocking_risk(),
        }
