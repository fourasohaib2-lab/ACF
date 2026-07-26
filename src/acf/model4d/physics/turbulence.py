"""
ACF - Atmospheric Complexity Framework
Model4D Turbulence Physics Module

Provides simplified atmospheric turbulence calculations:
- Turbulent kinetic energy (TKE)
- Dissipation rate
- Mixing coefficient
- Turbulence intensity
"""


class Turbulence:
    """
    Atmospheric turbulence parameterizations.
    """

    @staticmethod
    def tke(u_prime, v_prime, w_prime):
        """
        Turbulent kinetic energy.

        TKE = 0.5 * (u'² + v'² + w'²)

        Parameters:
            u_prime: zonal turbulent velocity
            v_prime: meridional turbulent velocity
            w_prime: vertical turbulent velocity
        """
        return 0.5 * (
            u_prime ** 2
            + v_prime ** 2
            + w_prime ** 2
        )

    @staticmethod
    def dissipation(tke_value, timescale):
        """
        Turbulent energy dissipation rate.

        epsilon = TKE / timescale
        """
        if timescale <= 0:
            raise ValueError("Timescale must be positive")

        return tke_value / timescale

    @staticmethod
    def mixing_length_coefficient(length_scale, velocity_scale):
        """
        Eddy diffusion coefficient.

        K = L * V
        """
        return length_scale * velocity_scale

    @staticmethod
    def intensity(tke_value, mean_velocity):
        """
        Turbulence intensity.

        I = sqrt(2*TKE/3) / U
        """
        if mean_velocity <= 0:
            raise ValueError("Mean velocity must be positive")

        return ((2 * tke_value / 3) ** 0.5) / mean_velocity
