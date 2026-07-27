"""
ACF - Atmospheric Complexity Framework
Solar Wind Interaction Physics Module

Sprint 8.74

Simulation simplifiée des interactions entre :
- vent solaire
- magnétosphère terrestre
- pression dynamique solaire
- flux énergétique
- perturbations spatiales
"""

from math import sqrt


class SolarWindInteractionPhysics:
    """
    Modèle physique simplifié des interactions vent solaire-espace.
    """

    @staticmethod
    def solar_wind_pressure(density, velocity):
        """
        Calcule la pression dynamique du vent solaire.

        P = rho * v² / 2

        Parameters
        ----------
        density : float
            densité du plasma solaire
        velocity : float
            vitesse du vent solaire

        Returns
        -------
        float
            pression dynamique
        """
        return round(0.5 * density * velocity ** 2, 6)

    @staticmethod
    def solar_wind_energy_flux(density, velocity):
        """
        Flux énergétique du vent solaire.

        F = 0.5 * rho * v³
        """
        return round(0.5 * density * velocity ** 3, 6)

    @staticmethod
    def magnetopause_distance(solar_pressure, magnetic_pressure):
        """
        Distance approximative de la magnétopause.

        Relation simplifiée :
        R ∝ sqrt(B_pressure / Solar_pressure)
        """
        if solar_pressure == 0:
            return 0

        return round(
            sqrt(magnetic_pressure / solar_pressure),
            6
        )

    @staticmethod
    def solar_wind_speed_change(initial_speed, final_speed):
        """
        Variation de vitesse du vent solaire.
        """
        return final_speed - initial_speed

    @staticmethod
    def plasma_density_variation(initial_density, final_density):
        """
        Variation de densité du plasma solaire.
        """
        return final_density - initial_density

    @staticmethod
    def magnetic_field_effect(field_strength, solar_pressure):
        """
        Effet simplifié du champ magnétique.

        Protection magnétique proportionnelle :
        B / P
        """
        if solar_pressure == 0:
            return 0

        return round(field_strength / solar_pressure, 6)

    @staticmethod
    def geomagnetic_activity_index(solar_flux, magnetic_field):
        """
        Indice simplifié d'activité géomagnétique.
        """
        return round(
            solar_flux * magnetic_field,
            6
        )

    @staticmethod
    def solar_storm_intensity(particle_flux, velocity):
        """
        Intensité simplifiée d'une tempête solaire.
        """
        return round(
            particle_flux * velocity,
            6
        )

    @staticmethod
    def aurora_probability(particle_flux, magnetic_activity):
        """
        Probabilité simplifiée d'aurore polaire.

        Limitation entre 0 et 1.
        """
        value = particle_flux * magnetic_activity

        return min(
            max(round(value, 6), 0),
            1
        )

    @staticmethod
    def interaction_strength(solar_wind, magnetosphere):
        """
        Force globale d'interaction vent solaire-magnétosphère.
        """
        return round(
            solar_wind * magnetosphere,
            6
        )
