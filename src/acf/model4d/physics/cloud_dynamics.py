"""
ACF - Atmospheric Complexity Framework
Cloud Dynamics Physics Module

Contains simplified cloud dynamic parameterizations:
- updraft velocity
- downdraft velocity
- cloud thickness
- entrainment rate
- detrainment rate
- cloud growth
- precipitation efficiency
"""

import math


class CloudDynamicsPhysics:
    """
    Cloud dynamics parameterization engine.
    """

    @staticmethod
    def updraft_velocity(buoyancy: float, height: float) -> float:
        """
        Estimate cloud updraft velocity.

        Parameters:
            buoyancy : m/s²
            height : m

        Returns:
            velocity m/s
        """
        if buoyancy < 0 or height <= 0:
            raise ValueError("Invalid cloud parameters")

        return math.sqrt(2 * buoyancy * height) / 10


    @staticmethod
    def downdraft_velocity(cooling: float, height: float) -> float:
        """
        Estimate downdraft velocity.
        """
        if cooling < 0 or height <= 0:
            raise ValueError("Invalid downdraft parameters")

        return -math.sqrt(2 * cooling * height) / 10


    @staticmethod
    def cloud_thickness(top: float, base: float) -> float:
        """
        Cloud vertical thickness.
        """
        if top < base:
            raise ValueError("Cloud top must exceed base")

        return top - base


    @staticmethod
    def entrainment_rate(environment: float, cloud: float) -> float:
        """
        Mixing of environmental air into cloud.
        """
        if cloud <= 0:
            raise ValueError("Invalid cloud value")

        return (environment - cloud) / cloud


    @staticmethod
    def detrainment_rate(cloud_mass: float, loss: float) -> float:
        """
        Cloud mass loss rate.
        """
        if cloud_mass <= 0:
            raise ValueError("Invalid cloud mass")

        return loss / cloud_mass


    @staticmethod
    def cloud_growth(initial: float, forcing: float) -> float:
        """
        Cloud growth factor.
        """
        if initial < 0:
            raise ValueError("Invalid initial cloud size")

        return initial * (1 + forcing / 100)


    @staticmethod
    def precipitation_efficiency(rainfall: float, condensate: float) -> float:
        """
        Ratio of precipitation production.
        """
        if condensate <= 0:
            raise ValueError("Invalid condensate")

        return rainfall / condensate


    @staticmethod
    def cloud_mass_flux(density: float, velocity: float, area: float) -> float:
        """
        Cloud mass flux.
        """
        if density <= 0 or area <= 0:
            raise ValueError("Invalid mass flux parameters")

        return density * velocity * area
