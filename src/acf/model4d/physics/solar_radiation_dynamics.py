"""
ACF - Atmospheric Complexity Framework
Model4D Physics Module

Solar Radiation Dynamics

Simulation simplifiée des interactions :
- rayonnement solaire entrant
- absorption atmosphérique
- réflexion de surface
- énergie nette reçue
- équilibre radiatif

Sprint 8.75
"""

from dataclasses import dataclass


@dataclass
class SolarRadiationDynamics:
    """
    Modèle physique du rayonnement solaire.
    """

    solar_constant: float = 1361.0  # W/m²
    atmosphere_absorption: float = 0.2
    surface_albedo: float = 0.3

    @staticmethod
    def validate_fraction(value: float) -> float:
        """
        Vérifie un coefficient compris entre 0 et 1.
        """
        if not 0 <= value <= 1:
            raise ValueError("Fraction must be between 0 and 1")

        return value

    @classmethod
    def absorbed_by_atmosphere(cls, incoming_radiation: float, absorption_fraction: float) -> float:
        """
        Calcule l'énergie absorbée par l'atmosphère.

        Q = R * A
        """

        cls.validate_fraction(absorption_fraction)

        return round(incoming_radiation * absorption_fraction, 6)

    @classmethod
    def reflected_by_surface(cls, incoming_radiation: float, albedo: float) -> float:
        """
        Calcule le rayonnement réfléchi par la surface.

        R = Q * albedo
        """

        cls.validate_fraction(albedo)

        return round(incoming_radiation * albedo, 6)

    @classmethod
    def absorbed_by_surface(cls, incoming_radiation: float, albedo: float) -> float:
        """
        Energie absorbée par la surface.

        Q = R * (1 - albedo)
        """

        cls.validate_fraction(albedo)

        return round(incoming_radiation * (1 - albedo), 6)

    @classmethod
    def net_radiation(cls, incoming_radiation: float, atmospheric_absorption: float, albedo: float) -> float:
        """
        Radiation nette disponible.

        RN = R - absorption_atm - reflection
        """

        cls.validate_fraction(atmospheric_absorption)
        cls.validate_fraction(albedo)

        absorbed_atm = incoming_radiation * atmospheric_absorption

        reflected = incoming_radiation * albedo

        return round(incoming_radiation - absorbed_atm - reflected, 6)

    @classmethod
    def greenhouse_radiative_effect(cls, infrared_trapping: float, outgoing_radiation: float) -> float:
        """
        Effet simplifié des gaz à effet de serre.

        G = IR * trapping
        """

        cls.validate_fraction(infrared_trapping)

        return round(outgoing_radiation * infrared_trapping, 6)

    def simulate(self, incoming_radiation: float) -> dict:
        """
        Simulation complète.
        """

        atmosphere_energy = self.absorbed_by_atmosphere(incoming_radiation, self.atmosphere_absorption)

        reflected = self.reflected_by_surface(incoming_radiation, self.surface_albedo)

        surface_energy = self.absorbed_by_surface(incoming_radiation, self.surface_albedo)

        net = self.net_radiation(incoming_radiation, self.atmosphere_absorption, self.surface_albedo)

        return {
            "incoming_radiation": incoming_radiation,
            "atmosphere_absorption": atmosphere_energy,
            "surface_reflection": reflected,
            "surface_absorption": surface_energy,
            "net_radiation": net,
        }
