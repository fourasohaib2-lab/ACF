"""
ACF - Atmospheric Complexity Framework

Aerosol Radiative Interaction Physics Module

Represents simplified interactions between:
- aerosol optical depth
- solar radiation
- scattering
- absorption
- radiative forcing
- atmospheric cooling/heating effects
"""


class AerosolRadiativeInteractionPhysics:
    """
    Physics engine for aerosol-radiation coupling.
    """

    MODULE_NAME = "Aerosol Radiative Interaction Physics"

    @staticmethod
    def transmitted_solar_radiation(incoming_radiation, optical_depth):
        """
        Beer-Lambert simplified transmission.

        T = I0 * exp(-tau)
        """
        import math

        if incoming_radiation < 0:
            raise ValueError("Incoming radiation must be positive")

        if optical_depth < 0:
            raise ValueError("Optical depth must be positive")

        return incoming_radiation * math.exp(-optical_depth)


    @staticmethod
    def aerosol_scattering_fraction(optical_depth, scattering_ratio):
        """
        Fraction of radiation scattered by aerosols.
        """

        if optical_depth < 0:
            raise ValueError("Optical depth must be positive")

        if not 0 <= scattering_ratio <= 1:
            raise ValueError("Scattering ratio must be between 0 and 1")

        return optical_depth * scattering_ratio


    @staticmethod
    def aerosol_absorption_fraction(optical_depth, absorption_ratio):
        """
        Aerosol absorption contribution.
        """

        if optical_depth < 0:
            raise ValueError("Optical depth must be positive")

        if not 0 <= absorption_ratio <= 1:
            raise ValueError("Absorption ratio must be between 0 and 1")

        return optical_depth * absorption_ratio


    @staticmethod
    def radiative_forcing(aerosol_effect, surface_albedo):
        """
        Simplified aerosol radiative forcing.

        Negative value:
        cooling effect

        Positive value:
        warming effect
        """

        if not 0 <= surface_albedo <= 1:
            raise ValueError("Albedo must be between 0 and 1")

        return -aerosol_effect * (1 - surface_albedo)


    @staticmethod
    def aerosol_cloud_interaction(aerosol_number, cloud_response_factor):
        """
        Aerosol indirect effect on clouds.
        """

        if aerosol_number < 0:
            raise ValueError("Aerosol concentration must be positive")

        if cloud_response_factor < 0:
            raise ValueError("Cloud response factor must be positive")

        return aerosol_number * cloud_response_factor


    @staticmethod
    def module_status():
        return {
            "module": AerosolRadiativeInteractionPhysics.MODULE_NAME,
            "status": "active",
            "domain": "atmospheric radiation",
        }
