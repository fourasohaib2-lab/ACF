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
        return 0.5 * mass * velocity**2

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
    def buoyancy(temperature_difference, gravity=9.81, reference_temperature=288.15):
        """
        Simplified buoyancy acceleration:

        B = g * ΔT / T

        simplified normalized form

        NOTE (correction — Physics Guard): the docstring's own stated
        formula divides by a reference temperature T, but the
        implementation used to just return `gravity * temperature_difference`
        - completely omitting that division. Dimensionally, g*ΔT alone
        has units of m/s^2*K (meaningless as an acceleration); g*ΔT/T
        is the correct, dimensionless-ratio-scaled acceleration (the
        same form correctly used elsewhere in this codebase, e.g.
        simulation_engine/atmosphere_solver/convection_engine.py's
        buoyancy = g*(t_parcel-t_env)/t_env). Added
        reference_temperature as a new optional parameter (default
        288.15 K, the standard-atmosphere reference temperature also
        used in model4d/constants.py's STANDARD_TEMPERATURE) so the
        formula now matches its own documented equation; existing
        2-argument call sites keep working with this default. Not
        fabricated.
        """
        if reference_temperature == 0:
            raise ValueError("Reference temperature cannot be zero")

        return gravity * temperature_difference / reference_temperature

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
