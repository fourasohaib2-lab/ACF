"""
ACF - Atmospheric Complexity Framework
Model4D Physics
Cryosphere Physics Module

Gestion des processus glace/neige :
- température de congélation
- fonte de glace
- croissance de glace
- albédo cryosphérique
- flux thermique glace-atmosphère
- variation d'épaisseur
"""


class Cryosphere:
    """
    Module physique cryosphérique simplifié.
    """

    ICE_FREEZING_POINT = 273.15  # Kelvin

    @staticmethod
    def is_frozen(temperature):
        """
        Détermine si l'eau est sous forme de glace.
        """
        return temperature <= Cryosphere.ICE_FREEZING_POINT

    @staticmethod
    def melting_rate(temperature, ice_factor=1.0):
        """
        Calcule un taux simplifié de fonte.
        """
        if temperature <= Cryosphere.ICE_FREEZING_POINT:
            return 0.0

        return (temperature - Cryosphere.ICE_FREEZING_POINT) * ice_factor

    @staticmethod
    def freezing_rate(temperature, factor=1.0):
        """
        Calcule un taux simplifié de formation de glace.
        """
        if temperature >= Cryosphere.ICE_FREEZING_POINT:
            return 0.0

        return (Cryosphere.ICE_FREEZING_POINT - temperature) * factor

    @staticmethod
    def albedo(ice_fraction):
        """
        Albédo cryosphérique.
        
        ice_fraction:
        0 -> surface libre
        1 -> glace complète
        """
        ice_fraction = max(0.0, min(1.0, ice_fraction))

        ice_albedo = 0.85
        water_albedo = 0.10

        return (
            ice_fraction * ice_albedo
            + (1 - ice_fraction) * water_albedo
        )

    @staticmethod
    def heat_flux(temperature_difference, conductivity=2.2):
        """
        Flux thermique simplifié.
        """
        return conductivity * temperature_difference

    @staticmethod
    def thickness_change(melting, freezing):
        """
        Variation d'épaisseur de glace.
        """
        return freezing - melting

