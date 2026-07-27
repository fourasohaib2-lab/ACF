"""
ACF - Atmospheric Complexity Framework
Magnetosphere Dynamics Physics Module

Simulation simplifiée des interactions :
- vent solaire
- champ magnétique terrestre
- pression magnétique
- confinement des particules
- activité géomagnétique
"""


class MagnetosphereDynamicsPhysics:
    """
    Module physique magnétosphérique 4D.
    """

    @staticmethod
    def solar_wind_pressure(density, velocity):
        """
        Pression dynamique du vent solaire.

        P = rho * V²

        density : densité plasma
        velocity : vitesse vent solaire
        """
        return density * velocity ** 2

    @staticmethod
    def magnetic_pressure(field_strength):
        """
        Pression magnétique.

        P = B² / 2

        field_strength : intensité champ magnétique
        """
        return (field_strength ** 2) / 2

    @staticmethod
    def magnetopause_distance(solar_pressure):
        """
        Distance simplifiée de la magnétopause.

        Plus la pression solaire augmente,
        plus la magnétopause se rapproche.
        """
        return 100 / (solar_pressure ** 0.5)

    @staticmethod
    def geomagnetic_activity(index):
        """
        Classification activité géomagnétique.

        index : 0-100
        """
        if index < 20:
            return "quiet"

        if index < 50:
            return "moderate"

        if index < 80:
            return "storm"

        return "extreme"

    @staticmethod
    def particle_trapping(efficiency, particles):
        """
        Nombre de particules confinées.
        """
        return particles * efficiency

    @staticmethod
    def aurora_intensity(particle_flux, magnetic_activity):
        """
        Intensité simplifiée des aurores.

        augmente avec flux particulaire
        et activité magnétique
        """
        return particle_flux * magnetic_activity

    @staticmethod
    def radiation_belt_energy(particles, energy):
        """
        Energie totale ceinture radiative.
        """
        return particles * energy

    @staticmethod
    def magnetic_reconnection(rate, energy):
        """
        Libération énergie reconnexion magnétique.
        """
        return rate * energy

    @staticmethod
    def storm_energy(solar_flux, duration):
        """
        Energie d'une tempête géomagnétique.
        """
        return solar_flux * duration

    @staticmethod
    def field_variation(initial_field, variation):
        """
        Variation champ magnétique.
        """
        return initial_field + variation
