"""
Atmospheric Fronts Physics Module
Atmospheric Complexity Framework (ACF)

Provides physical calculations related to atmospheric fronts:
- temperature gradients
- frontal strength
- thermal advection
- front propagation
- frontogenesis
- frontal stability
"""


class AtmosphericFrontsPhysics:
    """
    Atmospheric front dynamics calculations.
    """

    @staticmethod
    def temperature_gradient(temperature_difference, distance):
        """
        Temperature gradient.

        Parameters
        ----------
        temperature_difference : float
            Temperature difference (K)
        distance : float
            Horizontal distance (km)

        Returns
        -------
        float
            Gradient K/km
        """

        return temperature_difference / distance

    @staticmethod
    def frontal_strength(gradient):
        """
        Front intensity index.

        Returns
        -------
        float
            Frontal strength
        """

        return abs(gradient) * 100

    @staticmethod
    def thermal_advection(wind_speed, temperature_gradient):
        """
        Thermal advection.

        Formula:
            A = -V * dT/dx

        Returns
        -------
        float
            Thermal advection
        """

        return -wind_speed * temperature_gradient

    @staticmethod
    def front_speed(pressure_gradient, density):
        """
        Simplified frontal propagation speed.

        Returns
        -------
        float
            m/s
        """

        return pressure_gradient / density

    @staticmethod
    def frontogenesis(temperature_gradient, deformation):
        """
        Frontogenesis function.

        Returns
        -------
        float
        """

        return temperature_gradient * deformation

    @staticmethod
    def frontal_zone_width(gradient, temperature_difference):
        """
        Width of frontal zone.

        Returns
        -------
        float
            km
        """

        return temperature_difference / gradient

    @staticmethod
    def baroclinic_instability(temperature_gradient, vertical_shear):
        """
        Simple baroclinic instability index.

        Returns
        -------
        float
        """

        return temperature_gradient * vertical_shear

    @staticmethod
    def warm_front_intensity(temperature_difference, speed):
        """
        Warm front intensity.

        Returns
        -------
        float
        """

        return temperature_difference * speed

    @staticmethod
    def cold_front_intensity(temperature_difference, speed):
        """
        Cold front intensity.

        Returns
        -------
        float
        """

        return temperature_difference * speed * 1.2

    @staticmethod
    def frontal_convergence(wind_change, distance):
        """
        Wind convergence near front.

        Returns
        -------
        float
        """

        return wind_change / distance
