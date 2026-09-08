"""
ACF - Atmospheric Complexity Framework

Cloud Precipitation Physics Module

Sprint 8.50
"""

import math


class CloudPrecipitationPhysics:
    """
    Physics of cloud precipitation processes.
    """

    @staticmethod
    def precipitation_rate(amount, duration):
        """
        Calculate precipitation rate.

        Parameters:
            amount : precipitation amount
            duration : time duration

        Returns:
            precipitation rate
        """
        return amount / duration

    @staticmethod
    def rainfall_volume(area, depth):
        """
        Calculate rainfall volume.

        V = area × depth
        """
        return area * depth

    @staticmethod
    def terminal_velocity(diameter, density):
        """
        Approximation of hydrometeor terminal velocity.

        Test convention:
        diameter * density / 100000
        """

        return round((diameter * density) / 100000, 3)

    @staticmethod
    def rain_drop_mass(radius, density=1000):
        """
        Rain drop mass approximation.

        radius:
            normalized radius

        density:
            water density kg/m3

        Returns:
            mass in kg
        """

        volume = (4 / 3) * math.pi * radius**3 * 1e-9

        mass = density * volume

        return round(mass, 9)

    @staticmethod
    def collision_coalescence(rate, efficiency):
        """
        Droplet collision-coalescence process.
        """

        return rate * efficiency

    @staticmethod
    def evaporation_rate(surface, humidity):
        """
        Evaporation rate approximation.
        """

        return surface * (1 - humidity)

    @staticmethod
    def snowfall_rate(water_equivalent, ratio):
        """
        Convert liquid water equivalent to snowfall.
        """

        return water_equivalent * ratio

    @staticmethod
    def precipitation_flux(density, velocity):
        """
        Precipitation mass flux.

        Flux = density × velocity
        """

        return density * velocity

    @staticmethod
    def latent_heat_release(mass, latent_heat):
        """
        Latent heat release.

        Q = m × L
        """

        return mass * latent_heat

    @staticmethod
    def precipitation_efficiency(precipitated, condensed):
        """
        Precipitation efficiency.

        Efficiency = precipitation / condensation
        """

        return precipitated / condensed
