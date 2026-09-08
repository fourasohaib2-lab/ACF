"""
ACF - Atmospheric Complexity Framework

Radiation Balance Physics Module
"""


class RadiationBalancePhysics:
    """
    Simplified atmospheric radiation balance model.
    """

    STEFAN_BOLTZMANN = 5.670374419e-8

    @staticmethod
    def outgoing_longwave_radiation(
        temperature: float,
    ) -> float:
        """
        Calculate outgoing longwave radiation via the Stefan-Boltzmann law (W/m^2).

        NOTE (correction — Physics Guard): this used to divide the
        correct sigma*T^4 by an unexplained "10.01" - no physical
        justification, no comment, and not a clean unit-conversion
        factor. At T=288.15K (global mean surface temperature) the
        real Stefan-Boltzmann emission is ~391 W/m^2 (the standard,
        widely-cited figure for Earth's surface longwave emission,
        e.g. in global energy budget diagrams) - dividing by 10.01
        corrupted this to ~39 W/m^2, an order of magnitude off. The
        existing test asserted directly on the corrupted ~39 value,
        locking it in as if verified.
        """

        if temperature <= 0:
            raise ValueError("Temperature must be positive")

        return RadiationBalancePhysics.STEFAN_BOLTZMANN * temperature**4

    @staticmethod
    def net_radiation(
        incoming: float,
        outgoing: float,
    ) -> float:
        """
        Compute net radiation balance.
        """

        return incoming - outgoing

    @staticmethod
    def radiative_equilibrium(
        absorbed: float,
        emitted: float,
    ) -> float:
        """
        Compute radiation equilibrium ratio.

        absorbed / emitted
        """

        if emitted == 0:
            raise ValueError("Emission cannot be zero")

        return absorbed / emitted

    @staticmethod
    def greenhouse_effect(
        surface_flux: float,
        outgoing_flux: float,
    ) -> float:
        """
        Estimate simplified greenhouse trapping factor.
        """

        if surface_flux <= 0:
            raise ValueError("Surface flux must be positive")

        return (surface_flux - outgoing_flux) / surface_flux
