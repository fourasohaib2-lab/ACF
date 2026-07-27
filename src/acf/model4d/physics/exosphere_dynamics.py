"""
ACF - Atmospheric Complexity Framework
Model4D Physics Module

Exosphere Dynamics Physics
Sprint 8.71

Simulates simplified upper-atmosphere exosphere processes:
- particle escape
- atmospheric loss
- solar wind interaction
- exospheric density
- thermal escape
"""


class ExosphereDynamicsPhysics:
    """
    Physics engine for exospheric processes.
    """

    @staticmethod
    def exosphere_density(base_density, altitude_factor):
        """
        Estimate exospheric density.

        Parameters:
            base_density: reference density
            altitude_factor: reduction coefficient

        Returns:
            reduced density
        """
        return base_density * altitude_factor


    @staticmethod
    def atmospheric_escape_rate(particle_flux, escape_fraction):
        """
        Atmospheric particle escape rate.

        Returns:
            escaping particles
        """
        return particle_flux * escape_fraction


    @staticmethod
    def solar_wind_interaction(solar_pressure, magnetic_protection):
        """
        Solar wind impact after magnetic shielding.

        Returns:
            effective interaction energy
        """
        return solar_pressure * (1 - magnetic_protection)


    @staticmethod
    def exosphere_temperature(base_temperature, solar_heating):
        """
        Exospheric temperature response.
        """
        return base_temperature + solar_heating


    @staticmethod
    def thermal_escape_velocity(initial_velocity, thermal_factor):
        """
        Thermal escape contribution.
        """
        return initial_velocity * thermal_factor


    @staticmethod
    def atmospheric_loss(initial_mass, escaped_mass):
        """
        Remaining atmosphere mass.
        """
        return initial_mass - escaped_mass


    @staticmethod
    def particle_escape_fraction(total_particles, escaped_particles):
        """
        Fraction of escaped particles.
        """
        return escaped_particles / total_particles


    @staticmethod
    def exosphere_energy_balance(input_energy, lost_energy):
        """
        Energy balance.
        """
        return input_energy - lost_energy


    @staticmethod
    def solar_activity_effect(activity_level, sensitivity):
        """
        Solar cycle effect.
        """
        return activity_level * sensitivity


    @staticmethod
    def upper_atmosphere_expansion(temperature, expansion_factor):
        """
        Atmospheric expansion due to heating.
        """
        return temperature * expansion_factor
