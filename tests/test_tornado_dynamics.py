"""
ACF - Atmospheric Complexity Framework
Model4D Physics

Sprint 8.52
Tornado Dynamics Physics Module
"""

import math


class TornadoDynamicsPhysics:
    """
    Physical models for tornado dynamics.
    """

    @staticmethod
    def pressure_deficit(environment_pressure, tornado_pressure):
        """
        Pressure deficit:
        ΔP = P_environment - P_tornado
        """
        return environment_pressure - tornado_pressure

    @staticmethod
    def wind_speed_from_pressure_drop(delta_pressure):
        """
        Simplified wind speed from pressure deficit.

        V = sqrt(2ΔP / ρ)

        ACF reference air density:
        ρ = 1.2245 kg/m³
        """
        air_density = 1.2245
        return round(
            math.sqrt((2 * delta_pressure) / air_density),
            3
        )

    @staticmethod
    def rotational_velocity(radius, angular_velocity):
        """
        Tangential velocity:
        V = rω
        """
        return radius * angular_velocity

    @staticmethod
    def angular_velocity(tangential_velocity, radius):
        """
        Angular velocity:
        ω = V/r
        """
        return tangential_velocity / radius

    @staticmethod
    def tornado_energy(mass, velocity):
        """
        Kinetic energy:
        E = 1/2 mv²
        """
        return 0.5 * mass * velocity ** 2

    @staticmethod
    def vortex_strength(vorticity, radius):
        """
        Simplified vortex circulation indicator.
        """
        return vorticity * radius

    @staticmethod
    def tornado_intensity(wind_speed, pressure_drop):
        """
        Tornado intensity index.
        """
        return wind_speed * pressure_drop

    @staticmethod
    def inflow_rate(surface_velocity, area):
        """
        Air inflow rate:
        Q = V × A
        """
        return surface_velocity * area

    @staticmethod
    def tornado_lifetime(distance, propagation_speed):
        """
        Tornado lifetime:
        T = distance / speed
        """
        return distance / propagation_speed

    @staticmethod
    def enhanced_fujita_index(wind_speed):
        """
        Simplified Enhanced Fujita scale.
        """
        if wind_speed < 38:
            return "EF0"

        elif wind_speed < 50:
            return "EF1"

        elif wind_speed < 70:
            return "EF2"

        elif wind_speed < 90:
            return "EF3"

        elif wind_speed < 110:
            return "EF4"

        else:
            return "EF5"
