"""
ACF - Atmospheric Complexity Framework

Sprint 8.62
Snow Ice Atmosphere Interaction Physics Module

Processes:
- snow accumulation
- snow melt energy
- snow water equivalent
- ice albedo feedback
- solar absorption
- freezing potential
- surface cooling
- ice insulation
- freeze-thaw cycles
- snow cover effects
"""


class SnowIceAtmosphereInteractionPhysics:
    """
    Physics calculations for snow, ice and atmosphere coupling.
    """

    @staticmethod
    def snow_accumulation(precipitation, snow_fraction):
        """
        Calculate snow accumulation.

        Formula:
        Snow = precipitation × snow fraction
        """
        return precipitation * snow_fraction


    @staticmethod
    def snow_melt_energy(mass, latent_heat=334):
        """
        Energy required to melt snow/ice.

        Formula:
        Q = m × L
        """
        return mass * latent_heat


    @staticmethod
    def snow_water_equivalent(snow_depth, density=100):
        """
        Convert snow depth into water equivalent.

        """
        return snow_depth * density / 1000


    @staticmethod
    def ice_albedo_effect(solar_flux, albedo):
        """
        Reflected solar radiation.

        """
        return solar_flux * albedo


    @staticmethod
    def absorbed_solar_energy(solar_flux, albedo):
        """
        Absorbed solar radiation.

        Formula:
        Absorbed = Solar × (1 - albedo)

        Rounded to avoid floating point errors.
        """
        return round(solar_flux * (1 - albedo), 10)


    @staticmethod
    def freezing_potential(temperature, threshold=273):
        """
        Freezing potential.

        """
        return threshold - temperature


    @staticmethod
    def surface_cooling(temperature, snow_temperature):
        """
        Temperature difference between atmosphere and snow surface.
        """
        return temperature - snow_temperature


    @staticmethod
    def ice_insulation(thickness, conductivity=2.2):
        """
        Thermal insulation effect of ice.

        """
        return thickness / conductivity


    @staticmethod
    def freeze_thaw_cycle(freezing_days, thaw_days):
        """
        Freeze-thaw cycle intensity.

        """
        return freezing_days + thaw_days


    @staticmethod
    def snow_cover_effect(area, fraction):
        """
        Snow covered surface area.

        """
        return area * fraction
