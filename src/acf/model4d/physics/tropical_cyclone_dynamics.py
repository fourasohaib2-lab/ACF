"""
ACF - Atmospheric Complexity Framework
Model4D Physics Module

Tropical Cyclone Dynamics Physics

Module:
    tropical_cyclone_dynamics.py

Purpose:
    Physical calculations related to tropical cyclone
    structure, intensity, pressure, rotation and evolution.
"""

import math


class TropicalCycloneDynamicsPhysics:
    """
    Tropical cyclone physics engine.
    """

    @staticmethod
    def pressure_gradient_force(pressure_difference, distance):
        """
        Pressure gradient force approximation.

        PGF = ΔP / Δx
        """
        return pressure_difference / distance

    @staticmethod
    def cyclone_intensity(wind_speed, radius):
        """
        Simple cyclone intensity index.

        I = V² / R
        """
        return (wind_speed**2) / radius

    @staticmethod
    def coriolis_effect(latitude, wind_speed):
        """
        Simplified Coriolis parameter effect.

        f = 2 Ω sin(latitude)
        """
        omega = 7.2921e-5

        latitude_rad = math.radians(latitude)

        return 2 * omega * math.sin(latitude_rad) * wind_speed

    @staticmethod
    def gradient_wind_balance(pressure_gradient, coriolis):
        """
        Gradient wind approximation.
        """
        return pressure_gradient + coriolis

    @staticmethod
    def cyclone_energy(mass, velocity):
        """
        Kinetic energy of cyclone circulation.

        KE = 1/2 m v²
        """
        return 0.5 * mass * velocity**2

    @staticmethod
    def eyewall_radius_change(initial_radius, contraction):
        """
        Eyewall contraction model.
        """
        return initial_radius - contraction

    @staticmethod
    def moisture_energy(mass_water, latent_heat):
        """
        Moisture latent energy.

        E = mL
        """
        return mass_water * latent_heat

    @staticmethod
    def cyclone_lifetime(distance, translation_speed):
        """
        Cyclone lifetime estimate.
        """
        return distance / translation_speed

    @staticmethod
    def rapid_intensification(wind_before, wind_after):
        """
        Wind increase rate.
        """
        return wind_after - wind_before

    @staticmethod
    def storm_surge_height(wind_speed, coefficient):
        """
        Simplified storm surge model.
        """
        return coefficient * wind_speed**2
