"""
ACF - Atmospheric Complexity Framework
Radiative Transfer Model Physics Module

Sprint 8.76

Simulates simplified radiative transfer processes:
- Atmospheric absorption
- Emission
- Transmission
- Optical depth
- Radiative balance
"""

import math


class RadiativeTransferModelPhysics:
    """
    Physics model for atmospheric radiative transfer.
    """

    STEFAN_BOLTZMANN = 5.670374419e-8

    @staticmethod
    def absorbed_radiation(incoming_flux: float, absorptivity: float) -> float:
        """
        Calculate absorbed radiation.

        Q_abs = Q_in * alpha
        """
        if incoming_flux < 0:
            raise ValueError("Incoming flux must be positive")

        if not 0 <= absorptivity <= 1:
            raise ValueError("Absorptivity must be between 0 and 1")

        return round(incoming_flux * absorptivity, 10)

    @staticmethod
    def transmitted_radiation(
        incoming_flux: float,
        absorptivity: float
    ) -> float:
        """
        Calculate transmitted radiation.

        Q_trans = Q_in * (1-alpha)
        """
        if incoming_flux < 0:
            raise ValueError("Incoming flux must be positive")

        if not 0 <= absorptivity <= 1:
            raise ValueError("Absorptivity must be between 0 and 1")

        return round(incoming_flux * (1 - absorptivity), 10)

    @staticmethod
    def emitted_radiation(
        temperature: float,
        emissivity: float = 1.0
    ) -> float:
        """
        Stefan-Boltzmann radiation emission.

        E = epsilon * sigma * T^4
        """
        if temperature < 0:
            raise ValueError("Temperature must be positive")

        if not 0 <= emissivity <= 1:
            raise ValueError("Emissivity must be between 0 and 1")

        return round(
            emissivity *
            RadiativeTransferModelPhysics.STEFAN_BOLTZMANN *
            temperature ** 4,
            10
        )

    @staticmethod
    def optical_depth(
        absorption_coefficient: float,
        path_length: float
    ) -> float:
        """
        Calculate optical depth.

        tau = k * L
        """
        if absorption_coefficient < 0:
            raise ValueError(
                "Absorption coefficient must be positive"
            )

        if path_length < 0:
            raise ValueError(
                "Path length must be positive"
            )

        return round(
            absorption_coefficient * path_length,
            10
        )

    @staticmethod
    def transmission_from_optical_depth(
        optical_depth: float
    ) -> float:
        """
        Beer-Lambert transmission.

        T = exp(-tau)
        """
        if optical_depth < 0:
            raise ValueError(
                "Optical depth must be positive"
            )

        return round(
            math.exp(-optical_depth),
            10
        )

    @staticmethod
    def radiative_balance(
        absorbed: float,
        emitted: float
    ) -> float:
        """
        Net radiative balance.

        Balance = absorbed - emitted
        """
        return round(
            absorbed - emitted,
            10
        )

    @staticmethod
    def greenhouse_effect(
        surface_temperature: float,
        atmospheric_emissivity: float
    ) -> float:
        """
        Simplified greenhouse outgoing reduction.

        Reduced emission = sigma*T^4*(1-epsilon)
        """
        if surface_temperature < 0:
            raise ValueError(
                "Temperature must be positive"
            )

        if not 0 <= atmospheric_emissivity <= 1:
            raise ValueError(
                "Atmospheric emissivity must be between 0 and 1"
            )

        return round(
            RadiativeTransferModelPhysics.STEFAN_BOLTZMANN *
            surface_temperature ** 4 *
            (1 - atmospheric_emissivity),
            10
        )
