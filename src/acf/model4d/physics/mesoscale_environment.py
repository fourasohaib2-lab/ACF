"""
ACF - Atmospheric Complexity Framework
Model4D Physics Module

Mesoscale Environment Dynamics

Sprint 8.55
"""


class MesoscaleEnvironmentPhysics:
    """
    Physics calculations for mesoscale atmospheric environments.
    """

    @staticmethod
    def temperature_gradient(surface_temperature, upper_temperature):
        """
        Temperature difference between two atmospheric levels.

        Example:
        300K - 280K = 20K
        """
        return surface_temperature - upper_temperature

    @staticmethod
    def pressure_gradient(high_pressure, low_pressure):
        """
        Horizontal pressure gradient magnitude.
        """
        return high_pressure - low_pressure

    @staticmethod
    def moisture_flux(mixing_ratio, wind_speed):
        """
        Simplified moisture transport.
        """
        return mixing_ratio * wind_speed

    @staticmethod
    def boundary_layer_height(surface_temp, lapse_rate):
        """
        Estimate boundary layer height.

        height = temperature difference / lapse rate
        """
        return surface_temp / lapse_rate

    @staticmethod
    def mesoscale_convection_index(cape, moisture):
        """
        Simple convection potential index.
        """
        return cape * moisture

    @staticmethod
    def convergence(surface_wind, upper_wind):
        """
        Wind convergence indicator.
        """
        return surface_wind - upper_wind

    @staticmethod
    def vertical_velocity(temperature_difference):
        """
        Approximate vertical motion.
        """
        return temperature_difference / 10

    @staticmethod
    def stability_index(environment_temp, parcel_temp):
        """
        Atmospheric stability difference.
        """
        return environment_temp - parcel_temp

    @staticmethod
    def mesoscale_energy(mass, velocity):
        """
        Simplified kinetic energy.

        E = 0.5*m*v²
        """
        return 0.5 * mass * velocity**2

    @staticmethod
    def turbulence_factor(wind_difference, height_difference):
        """
        Simplified turbulence indicator.
        """
        return wind_difference / height_difference
