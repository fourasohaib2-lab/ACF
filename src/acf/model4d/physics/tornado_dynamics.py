"""
ACF - Atmospheric Complexity Framework
Model4D Physics
Tornado Dynamics Physics Module
Sprint 8.52
"""

import math


class TornadoDynamicsPhysics:
    """
    Physical calculations related to tornado dynamics.
    """

    @staticmethod
    def pressure_deficit(environment_pressure, tornado_pressure):
        """
        Pressure drop inside tornado (Pa).
        """
        return environment_pressure - tornado_pressure

    @staticmethod
    def wind_speed_from_pressure_drop(delta_pressure):
        """
        Approximate tornado wind speed from pressure deficit.
        """
        return round(math.sqrt(2 * delta_pressure / 1.225), 3)

    @staticmethod
    def rotational_velocity(radius, angular_velocity):
        """
        Tangential velocity:
        v = r * omega
        """
        return radius * angular_velocity

    @staticmethod
    def angular_velocity(tangential_velocity, radius):
        """
        omega = v / r
        """
        return tangential_velocity / radius

    @staticmethod
    def tornado_energy(mass, velocity):
        """
        Kinetic energy:
        E = 1/2 m v²
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
        Combined tornado intensity index.
        """
        return wind_speed * pressure_drop

    @staticmethod
    def inflow_rate(surface_velocity, area):
        """
        Air inflow volume rate.
        """
        return surface_velocity * area

    @staticmethod
    def tornado_lifetime(distance, propagation_speed):
        """
        Lifetime estimation.
        """
        return distance / propagation_speed

    @staticmethod
    def enhanced_fujita_index(wind_speed):
        """
        Simplified EF scale indicator.
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
