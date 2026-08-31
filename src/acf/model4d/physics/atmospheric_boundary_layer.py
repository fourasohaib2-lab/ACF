"""
ACF Model4D Physics
Atmospheric Boundary Layer Physics Module

Sprint 8.81

Simulation des échanges surface-atmosphère :
- Flux de chaleur sensible
- Flux de chaleur latente
- Flux de quantité de mouvement
- Hauteur couche limite
- Stabilité atmosphérique
- Longueur de Monin-Obukhov

"""

import math


class AtmosphericBoundaryLayerPhysics:
    """
    Atmospheric Boundary Layer (ABL/PBL) physics engine.
    """

    AIR_DENSITY = 1.225  # kg/m3
    AIR_HEAT_CAPACITY = 1005  # J/kg/K
    LATENT_HEAT_VAPORIZATION = 2.5e6  # J/kg
    VON_KARMAN = 0.4

    @staticmethod
    def calculate_sensible_heat_flux(
        air_density, heat_capacity, wind_speed, surface_temperature, air_temperature, transfer_coefficient=0.001
    ):
        """
        Flux de chaleur sensible :

        H = rho * Cp * Cd * U * (Ts - Ta)

        W/m2
        """

        return air_density * heat_capacity * transfer_coefficient * wind_speed * (surface_temperature - air_temperature)

    @staticmethod
    def calculate_latent_heat_flux(evaporation_rate, latent_heat=LATENT_HEAT_VAPORIZATION):
        """
        Flux chaleur latente :

        LE = evaporation * Lv

        W/m2
        """

        return evaporation_rate * latent_heat

    @staticmethod
    def calculate_momentum_flux(air_density, wind_speed, drag_coefficient=0.001):
        """
        Flux quantité de mouvement :

        tau = rho * Cd * U²
        """

        return air_density * drag_coefficient * wind_speed**2

    @staticmethod
    def calculate_mixing_height(surface_temperature, air_temperature, wind_speed, base_height=100):
        """
        Estimation hauteur couche limite.

        Une atmosphère plus instable
        augmente le mélange vertical.
        """

        temperature_difference = surface_temperature - air_temperature

        stability_factor = max(0, temperature_difference)

        return base_height + stability_factor * wind_speed * 50

    @staticmethod
    def calculate_monin_obukhov_length(
        temperature,
        friction_velocity,
        sensible_heat_flux,
        air_density=AIR_DENSITY,
        heat_capacity=AIR_HEAT_CAPACITY,
        gravity=9.81,
    ):
        """
        Longueur de Monin-Obukhov :

        L = -rho Cp T u*³ / (k g H)

        """

        if sensible_heat_flux == 0:
            return float("inf")

        return (
            -air_density
            * heat_capacity
            * temperature
            * friction_velocity**3
            / (AtmosphericBoundaryLayerPhysics.VON_KARMAN * gravity * sensible_heat_flux)
        )

    @staticmethod
    def calculate_stability(monin_obukhov_length, height):
        """
        Classification stabilité :

        L > 0  : stable
        L < 0  : instable
        L inf : neutre
        """

        if math.isinf(monin_obukhov_length):
            return "neutral"

        z_over_l = height / monin_obukhov_length

        if z_over_l > 0:
            return "stable"

        elif z_over_l < 0:
            return "unstable"

        return "neutral"

    @staticmethod
    def boundary_layer_status(surface_temperature, air_temperature, wind_speed):
        """
        Etat général couche limite.
        """

        if surface_temperature > air_temperature:
            regime = "convective"

        elif surface_temperature < air_temperature:
            regime = "stable"

        else:
            regime = "neutral"

        height = AtmosphericBoundaryLayerPhysics.calculate_mixing_height(
            surface_temperature, air_temperature, wind_speed
        )

        return {"regime": regime, "mixing_height_m": height, "wind_speed_ms": wind_speed}
