"""
ACF - Atmospheric Complexity Framework
Cryosphere Dynamics Physics Module

Simulation des interactions :
- neige
- glace
- glaciers
- permafrost
- bilan énergétique cryosphérique
"""


class CryosphereDynamicsPhysics:
    """
    Modèle physique simplifié de la cryosphère.
    """

    @staticmethod
    def snow_melt_rate(snow_energy, latent_heat):
        """
        Taux de fonte de neige.

        Args:
            snow_energy: énergie disponible (J)
            latent_heat: chaleur latente (J/kg)

        Returns:
            masse fondue (kg)
        """
        return snow_energy / latent_heat

    @staticmethod
    def ice_volume(thickness, area):
        """
        Volume de glace.

        V = épaisseur × surface
        """
        return thickness * area

    @staticmethod
    def glacier_mass(volume, density=900):
        """
        Masse d'un glacier.

        M = volume × densité
        """
        return volume * density

    @staticmethod
    def albedo_effect(solar_radiation, albedo):
        """
        Energie absorbée par une surface glacée.

        Q = radiation × (1 - albedo)
        """
        return round(solar_radiation * (1 - albedo), 10)

    @staticmethod
    def freezing_rate(temperature_difference, coefficient):
        """
        Taux de formation de glace.
        """
        return temperature_difference * coefficient

    @staticmethod
    def permafrost_stability(frozen_depth, thaw_depth):
        """
        Stabilité du pergélisol.
        """
        return frozen_depth - thaw_depth

    @staticmethod
    def glacier_retreat(initial_length, loss):
        """
        Retrait glaciaire.
        """
        return initial_length - loss

    @staticmethod
    def ice_energy(mass, latent_heat):
        """
        Energie nécessaire pour fondre la glace.
        """
        return mass * latent_heat

    @staticmethod
    def snow_water_equivalent(snow_depth, density_ratio):
        """
        Equivalent eau de neige.
        """
        return snow_depth * density_ratio

    @staticmethod
    def cryosphere_energy_balance(absorbed, emitted):
        """
        Bilan énergétique cryosphérique.
        """
        return absorbed - emitted
