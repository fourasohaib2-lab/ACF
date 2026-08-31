"""
ACF - Atmospheric Complexity Framework
Mountain Physics Module

Simulation des effets orographiques :
- soulèvement orographique
- refroidissement adiabatique
- gradient thermique montagneux
- précipitations orographiques
- effet foehn
"""

import math


class MountainPhysics:
    """
    Physique atmosphérique des régions montagneuses.
    """

    G = 9.81
    RD = 287.05
    CP = 1004.0
    LAPSE_RATE = 0.0065  # K/m

    @staticmethod
    def orographic_lifting(wind_speed, slope):
        """
        Calcul du soulèvement orographique.

        wind_speed : vitesse vent (m/s)
        slope      : pente montagne (rad)

        retourne vitesse verticale (m/s)
        """

        if wind_speed < 0:
            raise ValueError("Wind speed must be positive")

        if slope < 0:
            raise ValueError("Slope must be positive")

        return wind_speed * math.sin(slope)

    @staticmethod
    def adiabatic_cooling(height):
        """
        Refroidissement adiabatique avec altitude.

        height : altitude en mètres

        retourne température perdue en Kelvin
        """

        if height < 0:
            raise ValueError("Height cannot be negative")

        return height * MountainPhysics.LAPSE_RATE

    @staticmethod
    def mountain_temperature(surface_temperature, height):
        """
        Température à une altitude donnée.

        T = T0 - Γz
        """

        if surface_temperature <= 0:
            raise ValueError("Invalid temperature")

        if height < 0:
            raise ValueError("Invalid height")

        return surface_temperature - MountainPhysics.LAPSE_RATE * height

    @staticmethod
    def orographic_precipitation(moisture, uplift):
        """
        Estimation simple précipitation orographique.

        moisture : contenu humidité
        uplift   : soulèvement vertical
        """

        if moisture < 0:
            raise ValueError("Invalid moisture")

        if uplift < 0:
            raise ValueError("Invalid uplift")

        return moisture * uplift

    @staticmethod
    def foehn_temperature(windward_temperature, descent_height):
        """
        Réchauffement effet foehn.

        Air descendant se réchauffe.
        """

        if descent_height < 0:
            raise ValueError("Invalid descent height")

        return windward_temperature + MountainPhysics.LAPSE_RATE * descent_height

    @staticmethod
    def classify_orography(slope):
        """
        Classification terrain montagneux.
        """

        if slope < 0:
            raise ValueError("Invalid slope")

        if slope < 0.05:
            return "flat"

        elif slope < 0.2:
            return "hill"

        else:
            return "mountain"
