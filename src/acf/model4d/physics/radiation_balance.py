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
        Calculate normalized outgoing longwave radiation.
        """

        if temperature <= 0:
            raise ValueError(
                "Temperature must be positive"
            )

        radiation = (
            RadiationBalancePhysics.STEFAN_BOLTZMANN
            * temperature ** 4
        )

        return radiation / 10.01


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
            raise ValueError(
                "Emission cannot be zero"
            )

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
            raise ValueError(
                "Surface flux must be positive"
            )

        return (
            surface_flux - outgoing_flux
        ) / surface_flux
