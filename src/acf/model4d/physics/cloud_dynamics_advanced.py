"""
Cloud Dynamics Advanced Physics Module
Atmospheric Complexity Framework (ACF)

Advanced cloud motion, convection, turbulence,
entrainment and convective energy processes.
"""

import math


class CloudDynamicsAdvancedPhysics:
    """
    Advanced cloud dynamics calculations.
    """


    @staticmethod
    def updraft_velocity(
        buoyancy,
        height
    ):
        """
        Vertical rising velocity.

        Simplified plume equation.
        """

        return round(
            math.sqrt(
                2 * buoyancy * height
            ),
            5
        )


    @staticmethod
    def downdraft_velocity(
        negative_buoyancy,
        height
    ):
        """
        Downward air velocity.
        """

        return round(
            math.sqrt(
                2 * abs(negative_buoyancy) * height
            ),
            5
        )


    @staticmethod
    def entrainment_rate(
        mixing_rate,
        cloud_radius
    ):
        """
        Environmental air mixing into cloud.
        """

        return round(
            mixing_rate / cloud_radius,
            5
        )


    @staticmethod
    def detrainment_rate(
        cloud_mass,
        lifetime
    ):
        """
        Cloud air leaving cloud system.
        """

        return round(
            cloud_mass / lifetime,
            5
        )


    @staticmethod
    def turbulence_mixing(
        turbulence_energy,
        mixing_length
    ):
        """
        Turbulent diffusion coefficient.
        """

        return round(
            turbulence_energy * mixing_length,
            5
        )


    @staticmethod
    def cloud_lifetime(
        cloud_water,
        precipitation_rate
    ):
        """
        Approximate cloud lifetime.
        """

        if precipitation_rate == 0:
            return 0

        return round(
            cloud_water / precipitation_rate,
            5
        )


    @staticmethod
    def convective_available_energy(
        temperature_difference,
        height
    ):
        """
        CAPE simplified formulation.
        """

        return round(
            9.81
            *
            temperature_difference
            *
            height,
            5
        )


    @staticmethod
    def convective_inhibition(
        temperature_deficit,
        height
    ):
        """
        CIN simplified formulation.
        """

        return round(
            9.81
            *
            temperature_deficit
            *
            height,
            5
        )


    @staticmethod
    def plume_temperature(
        surface_temperature,
        lapse_rate,
        height
    ):
        """
        Rising plume temperature.
        """

        return round(
            surface_temperature
            -
            lapse_rate * height,
            5
        )


    @staticmethod
    def cloud_top_height(
        temperature_difference,
        lapse_rate
    ):
        """
        Estimated cloud top altitude.
        """

        if lapse_rate == 0:
            return 0

        return round(
            temperature_difference / lapse_rate,
            5
        )
