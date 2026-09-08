"""
ACF - Atmospheric Complexity Framework
Model4D Physics Engine

Atmospheric Dynamics Physics Module
Sprint 8.42

Contains:
- Coriolis force
- Pressure gradient force
- Geostrophic wind
- Horizontal advection
- Divergence
- Vorticity
- Potential vorticity
- Relative flow dynamics
"""

import math


class AtmosphericDynamicsPhysics:
    """
    Atmospheric dynamics calculations.
    """

    EARTH_ROTATION = 7.2921159e-5
    GRAVITY = 9.80665
    EARTH_RADIUS = 6.371e6

    @staticmethod
    def coriolis_parameter(latitude):
        """
        Coriolis parameter.

        f = 2 Ω sin(latitude)

        latitude degrees
        """
        if latitude < -90 or latitude > 90:
            raise ValueError("Invalid latitude")

        return 2 * AtmosphericDynamicsPhysics.EARTH_ROTATION * math.sin(math.radians(latitude))

    @staticmethod
    def coriolis_force(velocity, latitude, mass=1):
        """
        Coriolis force.

        Fc = m f v
        """
        if velocity < 0:
            raise ValueError("Velocity must be positive")

        f = AtmosphericDynamicsPhysics.coriolis_parameter(latitude)

        return round(mass * f * velocity, 6)

    @staticmethod
    def pressure_gradient_force(pressure_difference, density, distance):
        """
        Pressure gradient force.

        PGF = -1/rho * dp/dx
        """

        if density <= 0:
            raise ValueError("Density must be positive")

        if distance <= 0:
            raise ValueError("Distance must be positive")

        return round(pressure_difference / (density * distance), 6)

    @staticmethod
    def geostrophic_wind(pressure_gradient, latitude, density=1.225):
        """
        Geostrophic wind.

        Vg = PGF / f
        """

        f = abs(AtmosphericDynamicsPhysics.coriolis_parameter(latitude))

        if f == 0:
            raise ValueError("Geostrophic wind undefined at equator")

        return round(pressure_gradient / (density * f), 3)

    @staticmethod
    def horizontal_advection(wind_speed, gradient):
        """
        Horizontal scalar advection.

        A = -V.grad(phi)
        """

        return round(-wind_speed * gradient, 6)

    @staticmethod
    def divergence(du_dx, dv_dy):
        """
        Horizontal divergence.

        div(V)=du/dx+dv/dy
        """

        return round(du_dx + dv_dy, 6)

    @staticmethod
    def vorticity(dv_dx, du_dy):
        """
        Relative vorticity.

        ζ=dv/dx-du/dy
        """

        return round(dv_dx - du_dy, 6)

    @staticmethod
    def potential_vorticity(absolute_vorticity, static_stability):
        """
        Simplified potential vorticity.

        PV = ζ / stability
        """

        if static_stability <= 0:
            raise ValueError("Static stability must be positive")

        return round(absolute_vorticity / static_stability, 6)

    @staticmethod
    def rossby_number(velocity, latitude, length_scale):
        """
        Rossby number.

        Ro = U/(fL)
        """

        if length_scale <= 0:
            raise ValueError("Length scale must be positive")

        f = abs(AtmosphericDynamicsPhysics.coriolis_parameter(latitude))

        if f == 0:
            raise ValueError("Rossby number undefined at equator")

        return round(velocity / (f * length_scale), 6)
