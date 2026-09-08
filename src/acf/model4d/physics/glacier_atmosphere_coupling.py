"""
ACF - Atmospheric Complexity Framework
Glacier Atmosphere Coupling Physics Module

Sprint 8.64

Physical representations of glacier-atmosphere interactions:
- glacier melt
- albedo feedback
- sublimation
- glacier energy balance
- ice temperature response
- meltwater production
- atmospheric feedback
"""


class GlacierAtmosphereCouplingPhysics:
    """
    Glacier-atmosphere coupling physical parameterizations.
    """

    @staticmethod
    def glacier_melt_energy(energy, latent_heat):
        """
        Calculate glacier melt mass.

        energy : available energy (J)
        latent_heat : latent heat of fusion (J/kg)

        m = Q / L
        """
        if latent_heat == 0:
            return 0

        return energy / latent_heat

    @staticmethod
    def albedo_feedback(incoming_radiation, albedo):
        """
        Calculate absorbed solar energy.

        absorbed = radiation * (1 - albedo)
        """
        value = incoming_radiation * (1 - albedo)

        return round(value, 10)

    @staticmethod
    def glacier_temperature_change(energy, heat_capacity):
        """
        Temperature variation.

        ΔT = Q / C
        """
        if heat_capacity == 0:
            return 0

        return energy / heat_capacity

    @staticmethod
    def sublimation_rate(ice_loss, time):
        """
        Sublimation rate.

        rate = ice_loss / time
        """
        if time == 0:
            return 0

        return ice_loss / time

    @staticmethod
    def meltwater_generation(ice_mass, melt_fraction):
        """
        Meltwater production.

        water = ice_mass * melt_fraction
        """
        return ice_mass * melt_fraction

    @staticmethod
    def glacier_energy_balance(shortwave, longwave):
        """
        Glacier surface energy balance.

        net = shortwave - longwave
        """
        return shortwave - longwave

    @staticmethod
    def glacier_retreat(distance, years):
        """
        Glacier retreat speed.

        speed = distance / years
        """
        if years == 0:
            return 0

        return distance / years

    @staticmethod
    def atmospheric_warming_effect(glacier_loss, factor):
        """
        Atmospheric response due to glacier loss.
        """
        return glacier_loss * factor

    @staticmethod
    def ice_surface_temperature(surface_energy, thermal_capacity):
        """
        Ice surface temperature response.
        """
        if thermal_capacity == 0:
            return 0

        return surface_energy / thermal_capacity

    @staticmethod
    def glacier_mass_balance(accumulation, ablation):
        """
        Glacier mass balance.

        balance = accumulation - ablation
        """
        return accumulation - ablation
