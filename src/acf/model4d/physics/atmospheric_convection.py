"""
Atmospheric Convection Physics Module
Atmospheric Complexity Framework (ACF)

Contains simplified atmospheric convection equations:
- CAPE
- CIN
- convection velocity
- convective available energy
- thermal buoyancy
- parcel acceleration
- convective timescale
"""

import math


class AtmosphericConvectionPhysics:
    """
    Atmospheric convection physical calculations.
    """

    GRAVITY = 9.81
    CP_AIR = 1004.0

    @staticmethod
    def cape(temperature_parcel, temperature_environment, height):
        """
        Convective Available Potential Energy.

        CAPE = g * ΔT/T * z

        Parameters:
        temperature_parcel : K
        temperature_environment : K
        height : m
        """

        if temperature_environment == 0:
            return 0

        return (
            AtmosphericConvectionPhysics.GRAVITY
            * (temperature_parcel - temperature_environment)
            / temperature_environment
            * height
        )

    @staticmethod
    def cin(temperature_parcel, temperature_environment, height):
        """
        Convective Inhibition Energy.

        Simplified CIN representation.
        """

        if temperature_parcel >= temperature_environment:
            return 0

        return abs(
            AtmosphericConvectionPhysics.GRAVITY
            * (temperature_parcel - temperature_environment)
            / temperature_environment
            * height
        )

    @staticmethod
    def buoyancy(temperature_parcel, temperature_environment):
        """
        Thermal buoyancy.

        B = g * (Tp-Te)/Te
        """

        return (
            AtmosphericConvectionPhysics.GRAVITY
            * (temperature_parcel - temperature_environment)
            / temperature_environment
        )

    @staticmethod
    def convection_velocity(cape):
        """
        Maximum convective velocity.

        w = sqrt(2*CAPE)
        """

        if cape <= 0:
            return 0

        return math.sqrt(2 * cape)

    @staticmethod
    def parcel_acceleration(buoyancy):
        """
        Parcel acceleration.
        """

        return buoyancy

    @staticmethod
    def convective_timescale(height, velocity):
        """
        Convective overturning timescale.

        τ = z / w
        """

        if velocity == 0:
            return 0

        return height / velocity

    @staticmethod
    def lifting_condensation_level_height(temperature_surface, temperature_dewpoint):
        """
        LCL height approximation.

        z = 125 * (T - Td)
        """

        return 125 * (temperature_surface - temperature_dewpoint)

    @staticmethod
    def convective_flux(density, velocity, temperature_difference):
        """
        Simplified sensible heat flux.

        F = rho * Cp * w * ΔT
        """

        return density * AtmosphericConvectionPhysics.CP_AIR * velocity * temperature_difference

    @staticmethod
    def updraft_velocity(cape):
        """
        Atmospheric updraft velocity.
        """

        return AtmosphericConvectionPhysics.convection_velocity(cape)
