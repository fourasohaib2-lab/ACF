"""
ACF - Atmospheric Complexity Framework
Model4D Atmospheric Radiation Physics

Sprint 8.45
"""

import math


class AtmosphericRadiationPhysics:
    """
    Atmospheric radiation calculations.
    """

    STEFAN_BOLTZMANN = 5.670374419e-8

    @staticmethod
    def stefan_boltzmann_flux(
        temperature
    ):
        """
        Stefan-Boltzmann radiation flux.

        F = sigma T^4

        temperature: Kelvin
        returns W/m2
        """

        return (
            AtmosphericRadiationPhysics.STEFAN_BOLTZMANN
            * temperature ** 4
        )


    @staticmethod
    def net_radiative_flux(
        incoming,
        outgoing
    ):
        """
        Net radiation balance.

        Rn = incoming - outgoing
        """

        return incoming - outgoing


    @staticmethod
    def effective_temperature(
        flux
    ):
        """
        Effective radiative temperature.

        T = (F/sigma)^0.25
        """

        return (
            flux /
            AtmosphericRadiationPhysics.STEFAN_BOLTZMANN
        ) ** 0.25


    @staticmethod
    def greenhouse_forcing(
        incoming,
        outgoing
    ):
        """
        Simplified greenhouse forcing.

        G = incoming - outgoing
        """

        return incoming - outgoing


    @staticmethod
    def blackbody_emission(
        temperature,
        emissivity=1.0
    ):
        """
        Black body emission.

        F = e sigma T^4
        """

        return (
            emissivity *
            AtmosphericRadiationPhysics.STEFAN_BOLTZMANN *
            temperature ** 4
        )


    @staticmethod
    def atmospheric_absorption(
        radiation,
        coefficient
    ):
        """
        Radiation absorbed by atmosphere.

        A = R * k
        """

        return radiation * coefficient


    @staticmethod
    def optical_depth(
        absorption,
        path
    ):
        """
        Optical depth.

        tau = absorption * path
        """

        return absorption * path


    @staticmethod
    def radiative_equilibrium(
        absorbed,
        emitted
    ):
        """
        Equilibrium difference.
        """

        return absorbed - emitted


    @staticmethod
    def outgoing_longwave_radiation(
        temperature
    ):
        """
        OLR simplified.

        sigma T^4
        """

        return AtmosphericRadiationPhysics.stefan_boltzmann_flux(
            temperature
        )
