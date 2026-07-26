"""
ACF - Atmospheric Complexity Framework
Model4D Physics Engine

Radiative Transfer Physics Module
Sprint 8.22

Handles:
- Stefan-Boltzmann radiation
- solar radiation flux
- atmospheric absorption
- emission
- optical depth
- radiative equilibrium
"""

import math


class RadiativeTransferPhysics:
    """
    Atmospheric radiative transfer calculations.
    """

    STEFAN_BOLTZMANN = 5.670374419e-8

    SOLAR_CONSTANT = 1361.0


    @staticmethod
    def stefan_boltzmann_flux(
        temperature: float
    ) -> float:
        """
        Thermal emission flux.

        F = sigma * T^4
        """

        if temperature <= 0:
            raise ValueError(
                "Temperature must be positive"
            )

        return (
            RadiativeTransferPhysics.STEFAN_BOLTZMANN
            * temperature ** 4
        )


    @staticmethod
    def absorbed_solar_flux(
        solar_flux: float,
        albedo: float
    ) -> float:
        """
        Absorbed solar radiation.

        Q = S(1-alpha)
        """

        if solar_flux < 0:
            raise ValueError(
                "Solar flux cannot be negative"
            )

        if not 0 <= albedo <= 1:
            raise ValueError(
                "Albedo must be between 0 and 1"
            )

        return solar_flux * (1 - albedo)


    @staticmethod
    def atmospheric_transmission(
        optical_depth: float
    ) -> float:
        """
        Beer-Lambert transmission.

        T = exp(-tau)
        """

        if optical_depth < 0:
            raise ValueError(
                "Optical depth cannot be negative"
            )

        return math.exp(
            -optical_depth
        )


    @staticmethod
    def emitted_radiation(
        emissivity: float,
        temperature: float
    ) -> float:
        """
        Grey-body emission.

        F = epsilon sigma T^4
        """

        if not 0 <= emissivity <= 1:
            raise ValueError(
                "Emissivity must be between 0 and 1"
            )

        if temperature <= 0:
            raise ValueError(
                "Temperature must be positive"
            )

        return (
            emissivity
            *
            RadiativeTransferPhysics.STEFAN_BOLTZMANN
            *
            temperature ** 4
        )


    @staticmethod
    def radiative_equilibrium(
        incoming_flux: float,
        emissivity: float = 1.0
    ) -> float:
        """
        Equilibrium temperature.

        T = (F/(epsilon sigma))^(1/4)
        """

        if incoming_flux <= 0:
            raise ValueError(
                "Incoming flux must be positive"
            )

        if not 0 < emissivity <= 1:
            raise ValueError(
                "Invalid emissivity"
            )

        return (
            incoming_flux /
            (
                emissivity
                *
                RadiativeTransferPhysics.STEFAN_BOLTZMANN
            )
        ) ** 0.25


    @staticmethod
    def classify_radiative_state(
        net_flux: float
    ) -> str:
        """
        Classify atmospheric radiative balance.
        """

        if net_flux > 0:
            return "warming"

        if net_flux < 0:
            return "cooling"

        return "equilibrium"

