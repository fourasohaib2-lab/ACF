"""
ACF - Atmospheric Complexity Framework

Model4D Physics
Atmospheric State Equations Module

Contains:
- Ideal gas law
- Density calculation
- Virtual temperature
- Speed of sound
- Atmospheric stability classification
"""

from math import sqrt


class StateEquations:
    """
    Atmospheric thermodynamic state equations.
    """

    R_DRY_AIR = 287.05  # J/(kg K)
    GAMMA = 1.4  # Air heat capacity ratio

    @staticmethod
    def pressure(density, temperature):
        """
        Ideal gas law:

        P = rho R T
        """
        return density * StateEquations.R_DRY_AIR * temperature

    @staticmethod
    def density(pressure, temperature):
        """
        Density:

        rho = P / (R T)
        """
        if temperature == 0:
            raise ValueError("Temperature cannot be zero")

        return pressure / (StateEquations.R_DRY_AIR * temperature)

    @staticmethod
    def virtual_temperature(temperature, humidity):
        """
        Virtual temperature:

        Tv = T(1 + 0.61q)
        """
        return temperature * (1 + 0.61 * humidity)

    @staticmethod
    def speed_of_sound(temperature):
        """
        Speed of sound:

        c = sqrt(gamma R T)
        """
        if temperature <= 0:
            raise ValueError("Temperature must be positive")

        return sqrt(StateEquations.GAMMA * StateEquations.R_DRY_AIR * temperature)

    @staticmethod
    def stability(value):
        """
        Atmospheric stability classification.
        """

        if value < -1e-3:
            return "Unstable"

        if value > 1e-3:
            return "Stable"

        return "Neutral"
