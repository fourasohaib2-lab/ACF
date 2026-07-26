"""
ACF - Atmospheric Complexity Framework

Model4D Physics Module

Aerosol Physics Module

Handles simplified atmospheric aerosol processes:
- concentration
- PM2.5 / PM10
- dry deposition
- wet deposition
- aerosol-cloud interaction
- radiative forcing
"""


class Aerosols:
    """
    Atmospheric aerosol physical processes.
    """

    @staticmethod
    def concentration(mass, volume):
        """
        Aerosol concentration.

        C = mass / volume
        """
        if volume <= 0:
            raise ValueError("Volume must be positive")

        return mass / volume


    @staticmethod
    def pm25_fraction(pm25, total_particles):
        """
        PM2.5 fraction.
        """
        if total_particles <= 0:
            raise ValueError("Particle count must be positive")

        return pm25 / total_particles


    @staticmethod
    def dry_deposition(concentration, velocity, area):
        """
        Dry deposition flux.

        F = C * Vd * A
        """
        if velocity < 0:
            raise ValueError("Deposition velocity must be positive")

        if area < 0:
            raise ValueError("Area must be positive")

        return concentration * velocity * area


    @staticmethod
    def wet_deposition(concentration, precipitation_rate):
        """
        Wet scavenging.

        W = C * precipitation
        """
        if precipitation_rate < 0:
            raise ValueError("Precipitation rate must be positive")

        return concentration * precipitation_rate


    @staticmethod
    def cloud_interaction(aerosol_number, cloud_water):
        """
        Aerosol-cloud interaction index.
        """
        if cloud_water < 0:
            raise ValueError("Cloud water must be positive")

        return aerosol_number * cloud_water


    @staticmethod
    def radiative_forcing(aerosol_optical_depth):
        """
        Simplified aerosol radiative forcing.

        Negative forcing represents cooling effect.
        """
        return -130 * aerosol_optical_depth
