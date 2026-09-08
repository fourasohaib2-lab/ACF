"""
ACF - Atmospheric Complexity Framework

Model4D Physics

Turbulence Physics Module
Sprint 8.30
"""

import math


class TurbulencePhysics:
    """
    Atmospheric turbulence parameterization.
    """

    @staticmethod
    def turbulent_kinetic_energy(u_prime, v_prime, w_prime):
        """
        Compute turbulent kinetic energy.

        TKE = 0.5 * (u'^2 + v'^2 + w'^2)
        """

        if not all(isinstance(value, (int, float)) for value in (u_prime, v_prime, w_prime)):
            raise ValueError("Velocity fluctuations must be numeric")

        return 0.5 * (u_prime**2 + v_prime**2 + w_prime**2)

    @staticmethod
    def eddy_viscosity(mixing_length, velocity_gradient):
        """
        Eddy viscosity coefficient.

        Km = l² × du/dz
        """

        if mixing_length <= 0:
            raise ValueError("Mixing length must be positive")

        if velocity_gradient < 0:
            raise ValueError("Velocity gradient must be positive")

        return mixing_length**2 * velocity_gradient

    @staticmethod
    def mixing_length(height, surface_roughness):
        """
        Atmospheric mixing length.

        l = k(z + z0)
        """

        if height <= 0:
            raise ValueError("Height must be positive")

        if surface_roughness < 0:
            raise ValueError("Surface roughness invalid")

        von_karman = 0.4

        return von_karman * (height + surface_roughness)

    @staticmethod
    def turbulence_intensity(tke, mean_velocity):
        """
        Turbulence intensity.

        ACF formulation:

        I = sqrt(TKE / (0.15 × U²))

        Example:
        TKE = 1.5
        U = 10

        I = 0.316
        """

        if tke < 0:
            raise ValueError("TKE must be positive")

        if mean_velocity <= 0:
            raise ValueError("Mean velocity must be positive")

        return math.sqrt(tke / (0.15 * mean_velocity**2))

    @staticmethod
    def stability_correction(richardson_number):
        """
        Stability correction using Richardson number.

        Ri > 0.25  -> stable
        Ri < 0     -> unstable
        otherwise  -> neutral
        """

        if richardson_number > 0.25:
            return "stable"

        if richardson_number < 0:
            return "unstable"

        return "neutral"
