"""
Cloud Microphysics Physics Module
Atmospheric Complexity Framework (ACF)

Cloud droplets, condensation, ice processes,
precipitation formation and cloud evolution.
"""

import math


class CloudMicrophysicsPhysics:
    """
    Cloud microphysics calculations.
    """

    @staticmethod
    def saturation_vapor_pressure(temperature):
        """
        Saturation vapor pressure.

        Tetens formula.
        Temperature in Celsius.
        """

        return round(6.112 * math.exp((17.67 * temperature) / (temperature + 243.5)), 2)

    @staticmethod
    def condensation_rate(vapor_pressure, saturation_pressure, coefficient):
        """
        Condensation rate.
        """

        return coefficient * (vapor_pressure - saturation_pressure)

    @staticmethod
    def cloud_water_content(liquid_water, air_volume):
        """
        Liquid water content.

        LWC = water mass / air volume
        """

        return liquid_water / air_volume

    @staticmethod
    def droplet_growth_rate(radius, supersaturation):
        """
        Droplet diffusional growth.

        Normalized ACF formulation.
        """

        return round(radius * supersaturation * 1e-6, 7)

    @staticmethod
    def autoconversion_rate(cloud_water, threshold):
        """
        Cloud water converted
        into precipitation.
        """

        if cloud_water <= threshold:
            return 0

        return round((cloud_water - threshold) * 1e-2, 5)

    @staticmethod
    def accretion_rate(rain_water, cloud_water, coefficient):
        """
        Collision-coalescence growth.
        """

        return coefficient * rain_water * cloud_water

    @staticmethod
    def ice_nucleation_rate(temperature, concentration):
        """
        Ice crystal nucleation.

        Active below 0 Celsius.
        """

        if temperature >= 0:
            return 0

        return round(abs(temperature) * concentration * 1e-4, 5)

    @staticmethod
    def deposition_growth(ice_mass, vapor_supply):
        """
        Ice deposition growth.
        """

        return round(ice_mass * vapor_supply * 1e-3, 5)

    @staticmethod
    def precipitation_efficiency(precipitation, available_water):
        """
        Precipitation efficiency.
        """

        if available_water == 0:
            return 0

        return precipitation / available_water

    @staticmethod
    def terminal_velocity_droplet(radius):
        """
        Droplet terminal velocity.

        Simplified power law.
        """

        return round(1300 * radius**2, 5)
