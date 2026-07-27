"""
ACF - Atmospheric Complexity Framework
Polar Vortex Dynamics Physics Module

Simulation simplifiée de la dynamique du vortex polaire :
- vitesse du vortex
- intensité du vortex
- gradient thermique polaire
- stabilité stratosphérique
- déplacement du vortex
- énergie cinétique
"""

import math


class PolarVortexDynamicsPhysics:
    """
    Physics engine for polar vortex dynamics.
    """

    @staticmethod
    def vortex_speed(radius, angular_velocity):
        """
        Tangential vortex wind speed.

        v = r * omega
        """
        return radius * angular_velocity


    @staticmethod
    def vortex_intensity(wind_speed):
        """
        Estimate vortex intensity.

        proportional to wind speed squared.
        """
        return round(wind_speed ** 2, 3)


    @staticmethod
    def thermal_gradient(polar_temperature, midlatitude_temperature):
        """
        Temperature gradient between polar region and mid-latitudes.
        """
        return abs(midlatitude_temperature - polar_temperature)


    @staticmethod
    def stratospheric_stability(temperature_gradient):
        """
        Simple stability index.
        """
        return round(temperature_gradient / 10, 3)


    @staticmethod
    def vortex_displacement(initial_position, final_position):
        """
        Vortex movement distance.
        """
        return abs(final_position - initial_position)


    @staticmethod
    def kinetic_energy(mass, velocity):
        """
        KE = 1/2 m v²
        """
        return 0.5 * mass * velocity ** 2


    @staticmethod
    def angular_momentum(mass, radius, velocity):
        """
        L = m r v
        """
        return mass * radius * velocity


    @staticmethod
    def polar_warming_effect(stratospheric_temperature_change):
        """
        Sudden stratospheric warming indicator.
        """
        return round(stratospheric_temperature_change * 2, 3)


    @staticmethod
    def vortex_decay(initial_strength, decay_rate):
        """
        Exponential vortex weakening.

        S = S0 * (1-rate)
        """
        return round(initial_strength * (1 - decay_rate), 3)


    @staticmethod
    def vortex_energy(mass, velocity):
        """
        Total simplified vortex kinetic energy.
        """
        return round(0.5 * mass * velocity ** 2, 3)
