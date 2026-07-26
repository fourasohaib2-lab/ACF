"""
ACF - Atmospheric Complexity Framework

Model4D Physics Module

Convection Physics
==================

Module de physique atmosphérique pour :
- CAPE (Convective Available Potential Energy)
- CIN (Convective Inhibition)
- vitesse verticale convective
- indice de convection
- probabilité d'orage

"""

import math


class ConvectionPhysics:
    """
    Classe de calculs physiques liés à la convection atmosphérique.
    """


    @staticmethod
    def cape(
        temperature_parcel,
        temperature_environment,
        height
    ):
        """
        Calcule une approximation de la CAPE.

        Formule simplifiée :

        CAPE = g * ((Tp - Te) / Te) * z

        Paramètres:
        ----------
        temperature_parcel : float
            Température de la parcelle d'air (K)

        temperature_environment : float
            Température environnementale (K)

        height : float
            Hauteur verticale (m)

        Retour:
        -------
        float
            CAPE en J/kg
        """

        if height <= 0:
            return 0.0

        if temperature_environment <= 0:
            return 0.0

        g = 9.81

        buoyancy = (
            temperature_parcel -
            temperature_environment
        ) / temperature_environment

        cape = g * buoyancy * height

        return max(
            0.0,
            cape / 100
        )


    @staticmethod
    def cin(
        temperature_parcel,
        temperature_environment,
        height
    ):
        """
        Calcule une approximation de la CIN.

        Retour:
        -------
        float
            CIN négative
        """

        if height <= 0:
            return 0.0

        if temperature_parcel >= temperature_environment:
            return 0.0

        g = 9.81

        deficit = (
            temperature_environment -
            temperature_parcel
        ) / temperature_environment

        cin = -g * deficit * height

        return cin / 100


    @staticmethod
    def convective_velocity(cape):
        """
        Estimation de la vitesse verticale convective.

        Formule :

        w = sqrt(2 * CAPE)

        Paramètre:
        ----------
        cape : float
            CAPE en J/kg

        Retour:
        -------
        float
            vitesse verticale en m/s
        """

        if cape <= 0:
            return 0.0

        return math.sqrt(
            2 * cape
        )


    @staticmethod
    def convection_index(cape, cin):
        """
        Indice simplifié d'activité convective.

        Plus CAPE est élevé et CIN faible,
        plus la convection est importante.
        """

        return max(
            0.0,
            cape + abs(cin)
        )


    @staticmethod
    def thunderstorm_probability(cape):
        """
        Estimation simplifiée de probabilité d'orage.

        Retour:
        -------
        float
            valeur entre 0 et 1
        """

        if cape <= 0:
            return 0.0

        probability = cape / 2500

        return min(
            1.0,
            probability
        )
