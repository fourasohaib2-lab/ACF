"""
ACF - Atmospheric Complexity Framework
Model4D Physics Module

Mesoscale Convective Systems Physics
Sprint 8.55
"""


class MesoscaleConvectiveSystemsPhysics:
    """
    Physics approximations for Mesoscale Convective Systems (MCS).
    """

    @staticmethod
    def convective_cluster_size(area, cells):
        """
        Size index of convective cluster.
        """
        return area * cells


    @staticmethod
    def life_cycle_stage(age):
        """
        MCS life cycle classification.
        """
        if age < 2:
            return "formation"
        elif age < 8:
            return "mature"
        else:
            return "dissipation"


    @staticmethod
    def formation_probability(cape, moisture):
        """
        Formation probability index.
        """
        return cape * moisture / 100


    @staticmethod
    def updraft_strength(cape):
        """
        Convective updraft strength.

        Simplified:
        W = CAPE / 10
        """
        return cape / 10


    @staticmethod
    def downdraft_strength(precipitation, cold_pool):
        """
        Downdraft intensity.
        """
        return precipitation * cold_pool


    @staticmethod
    def outflow_boundary_speed(temperature_difference):
        """
        Cold pool outflow speed.
        """
        return temperature_difference * 2


    @staticmethod
    def convective_organization_index(cells, area):
        """
        Organization index.
        """
        return cells / area


    @staticmethod
    def precipitation_core_intensity(rate, duration):
        """
        Precipitation core intensity.
        """
        return rate * duration


    @staticmethod
    def system_velocity(distance, time):
        """
        MCS propagation speed.
        """
        return distance / time


    @staticmethod
    def mcs_energy(mass, velocity):
        """
        Simplified MCS dynamic energy.

        E = mass × velocity
        """
        return mass * velocity
