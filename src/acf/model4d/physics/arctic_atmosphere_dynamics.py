"""
ACF - Atmospheric Complexity Framework
Sprint 8.66
Arctic Atmosphere Dynamics Physics Module

Physical representations:
- Arctic temperature gradients
- Polar vortex dynamics
- Sea ice feedback
- Arctic amplification
- Katabatic winds
- Polar boundary layer
- Albedo feedback
- Jet stream displacement
- Cold air outbreak index
- Arctic energy balance
"""


class ArcticAtmosphereDynamicsPhysics:
    """
    Physics engine for Arctic atmospheric processes.
    """

    @staticmethod
    def arctic_temperature_gradient(surface_temp, upper_temp):
        """
        Temperature gradient between surface and upper atmosphere.

        Example:
        surface=250K upper=240K => 10
        """
        return surface_temp - upper_temp


    @staticmethod
    def polar_vortex_strength(wind_speed, pressure_gradient):
        """
        Polar vortex intensity index.
        """
        return wind_speed * pressure_gradient


    @staticmethod
    def sea_ice_feedback(initial_albedo, final_albedo):
        """
        Ice-albedo feedback variation.
        """
        return initial_albedo - final_albedo


    @staticmethod
    def arctic_amplification(global_temperature_change,
                             arctic_temperature_change):
        """
        Arctic amplification ratio.
        """
        if global_temperature_change == 0:
            return 0

        return arctic_temperature_change / global_temperature_change


    @staticmethod
    def katabatic_wind_speed(height_difference, temperature_difference):
        """
        Simplified katabatic wind estimation.
        """
        return height_difference * temperature_difference


    @staticmethod
    def polar_boundary_layer(surface_wind, stability_factor):
        """
        Polar boundary layer index.
        """
        return surface_wind / stability_factor


    @staticmethod
    def albedo_feedback(incoming_radiation, albedo):
        """
        Reflected solar energy.
        """
        return incoming_radiation * albedo


    @staticmethod
    def jet_stream_shift(polar_temperature_gradient,
                         midlatitude_gradient):
        """
        Jet stream displacement index.
        """
        return polar_temperature_gradient - midlatitude_gradient


    @staticmethod
    def cold_air_outbreak_index(cold_air_mass,
                                temperature_anomaly):
        """
        Cold air outbreak intensity.
        """
        return cold_air_mass * temperature_anomaly


    @staticmethod
    def arctic_energy_balance(incoming_energy,
                              outgoing_energy):
        """
        Arctic surface energy balance.
        """
        return incoming_energy - outgoing_energy
