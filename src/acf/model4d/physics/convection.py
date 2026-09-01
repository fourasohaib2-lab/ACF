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
    def cape(temperature_parcel, temperature_environment, height):
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

        NOTE (correction - Physics Guard): g*buoyancy*height already
        has correct J/kg units (m/s^2 * dimensionless * m = m^2/s^2 =
        J/kg) - this used to be followed by an unexplained "/ 100"
        with no unit-conversion justification, making cape() report
        values ~100x too small (e.g. 3.38 J/kg instead of the correct
        338.28 J/kg for T_parcel=300K/T_env=290K/z=1000m - a physically
        negligible-looking number for what is actually a real,
        moderate-instability CAPE value). This broke internal
        consistency with this class's own sibling functions:
        convective_velocity(cape) = sqrt(2*CAPE) and
        thunderstorm_probability(cape) = CAPE/2500 both assume a
        real-unit CAPE input - chaining cape()'s output into either
        would have silently produced values orders of magnitude too
        small. Removed.
        """

        if height <= 0:
            return 0.0

        if temperature_environment <= 0:
            return 0.0

        g = 9.81

        buoyancy = (temperature_parcel - temperature_environment) / temperature_environment

        cape = g * buoyancy * height

        return max(0.0, cape)

    @staticmethod
    def cin(temperature_parcel, temperature_environment, height):
        """
        Calcule une approximation de la CIN.

        Retour:
        -------
        float
            CIN négative

        NOTE (correction - Physics Guard): same unexplained "/ 100"
        bug as cape() above, with the same units already correct
        without it - removed.
        """

        if height <= 0:
            return 0.0

        if temperature_parcel >= temperature_environment:
            return 0.0

        g = 9.81

        deficit = (temperature_environment - temperature_parcel) / temperature_environment

        cin = -g * deficit * height

        return cin

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

        return math.sqrt(2 * cape)

    @staticmethod
    def convection_index(cape, cin):
        """
        Indice simplifié d'activité convective.

        Plus CAPE est élevé et CIN faible,
        plus la convection est importante.
        """

        return max(0.0, cape + abs(cin))

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

        return min(1.0, probability)
