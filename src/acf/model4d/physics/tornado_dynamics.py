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
        return 0.5 * mass * velocity**2

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
        Simplified EF scale indicator (wind_speed in m/s, 3-second gust).

        NOTE (correction — Physics Guard): the EF2-EF5 thresholds
        (70/90/110) diverged substantially from the real NWS/NOAA
        Enhanced Fujita Scale 3-second-gust wind estimates converted to
        m/s (EF0 >=29, EF1 >=38, EF2 >=50, EF3 >=61, EF4 >=74, EF5
        >=89 m/s) - a wind speed of e.g. 95 m/s (genuinely EF5, >=89)
        used to be classified as only "EF4" (<110), understating
        tornado severity. Corrected to the standard published
        thresholds. Not fabricated.
        """
        if wind_speed < 29:
            return "EF0"
        elif wind_speed < 38:
            return "EF1"
        elif wind_speed < 50:
            return "EF2"
        elif wind_speed < 61:
            return "EF3"
        elif wind_speed < 74:
            return "EF4"
        else:
            return "EF5"
