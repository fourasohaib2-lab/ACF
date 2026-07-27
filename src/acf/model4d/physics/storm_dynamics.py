"""
ACF - Atmospheric Complexity Framework
Storm Dynamics Physics Module

Module physique dédié aux systèmes convectifs sévères,
orages, supercellules et dynamique convective.
"""


class StormDynamicsPhysics:
    """
    Advanced storm dynamics calculations.
    """

    @staticmethod
    def cape(parcel_energy, environment_energy):
        """
        Convective Available Potential Energy

        CAPE = parcel energy - environment energy
        """
        return parcel_energy - environment_energy


    @staticmethod
    def cin(inhibition, reference):
        """
        Convective Inhibition

        CIN = reference - inhibition
        """
        return reference - inhibition


    @staticmethod
    def updraft_velocity(energy):
        """
        Approximate updraft velocity.

        Simplified model:
        w = energy / 10
        """
        return energy / 10


    @staticmethod
    def wind_shear(upper_wind, lower_wind):
        """
        Vertical wind shear.
        """
        return upper_wind - lower_wind


    @staticmethod
    def storm_intensity(wind_speed, duration):
        """
        Storm intensity index.
        """
        return wind_speed * duration


    @staticmethod
    def supercell_potential(vorticity, shear):
        """
        Supercell potential index.
        """
        return vorticity * shear


    @staticmethod
    def storm_lifetime(distance, speed):
        """
        Storm lifetime.

        lifetime = distance / speed
        """
        return distance / speed


    @staticmethod
    def precipitation_efficiency(rainfall, moisture):
        """
        Precipitation efficiency.
        """
        return rainfall / moisture


    @staticmethod
    def vorticity(rotation, scale):
        """
        Relative vorticity approximation.
        """
        return rotation / scale


    @staticmethod
    def convective_index(surface_temperature, upper_temperature):
        """
        Thermal convective index.
        """
        return surface_temperature - upper_temperature
