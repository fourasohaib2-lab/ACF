"""
ACF - Atmospheric Complexity Framework
Model4D Physics - Dynamics Module

Basic atmospheric dynamics operators:
- acceleration
- momentum
- kinetic energy
- pressure force
- buoyancy force
"""

from math import isclose


class Dynamics:
    """
    Atmospheric dynamics calculations.
    """

    @staticmethod
    def acceleration(force, mass):
        """
        Newton second law:

        a = F / m
        """
        if mass == 0:
            raise ValueError("Mass cannot be zero")

        return force / mass

    @staticmethod
    def momentum(mass, velocity):
        """
        Momentum:

        p = m * v
        """
        return mass * velocity

    @staticmethod
    def kinetic_energy(mass, velocity):
        """
        Kinetic energy:

        KE = 1/2 m v²
        """
        return 0.5 * mass * velocity ** 2

    @staticmethod
    def pressure_force(pressure_gradient, density):
        """
        Pressure gradient force approximation:

        F = -grad(P) / rho
        """
        if density == 0:
            raise ValueError("Density cannot be zero")

        return -pressure_gradient / density

    @staticmethod
    def buoyancy(temperature_difference, gravity=9.81):
        """
        Simplified buoyancy acceleration:

        B = g * ΔT / T

        simplified normalized form
        """
        return gravity * temperature_difference

    @staticmethod
    def category(value):
        """
        Classify dynamic intensity.
        """

        if abs(value) < 1e-6:
            return "Weak"

        if abs(value) < 1e-4:
            return "Moderate"

        return "Strong"
