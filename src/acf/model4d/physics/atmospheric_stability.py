"""
ACF - Atmospheric Complexity Framework
Atmospheric Stability Physics Module

Contains atmospheric stability calculations:
- Brunt-Väisälä frequency
- Richardson number
- Potential temperature gradient
- Static stability
- Convective instability
- Stability classification
"""

import math


class AtmosphericStabilityPhysics:
    """
    Atmospheric stability physical calculations.
    """

    @staticmethod
    def brunt_vaisala_frequency(potential_temperature_gradient, temperature=300):
        """
        Calculate Brunt-Väisälä frequency.

        N² = (g / θ) * dθ/dz

        Returns frequency in s^-1.
        """

        g = 9.81

        if temperature <= 0:
            raise ValueError("Temperature must be positive")

        if potential_temperature_gradient < 0:
            raise ValueError("Gradient cannot be negative")

        return math.sqrt((g / temperature) * potential_temperature_gradient)

    @staticmethod
    def richardson_number(static_stability, wind_shear):
        """
        Gradient Richardson number.

        Ri = N² / (du/dz)²
        """

        if wind_shear <= 0:
            raise ValueError("Wind shear must be positive")

        return round(static_stability / (wind_shear**2), 3)

    @staticmethod
    def stability_parameter(temperature_gradient, lapse_rate=9.8):
        """
        Atmospheric stability parameter.

        Positive -> stable
        Zero -> neutral
        Negative -> unstable
        """

        return round(lapse_rate - temperature_gradient, 2)

    @staticmethod
    def classify_stability(parameter):
        """
        Stability classification.
        """

        if parameter > 0:
            return "stable"

        elif parameter == 0:
            return "neutral"

        else:
            return "unstable"

    @staticmethod
    def convective_available_energy(temperature_difference, height):
        """
        Simplified CAPE estimation.

        CAPE = g * ΔT/T * z
        """

        g = 9.81
        reference_temperature = 300

        if height < 0:
            raise ValueError("Height cannot be negative")

        return round(g * (temperature_difference / reference_temperature) * height, 2)

    @staticmethod
    def convective_inhibition(temperature_difference, height):
        """
        Simplified CIN estimation.
        """

        if temperature_difference >= 0:
            return 0

        return round(abs(temperature_difference) * height * 0.01, 2)

    @staticmethod
    def stability_index(temperature_difference):
        """
        Stability index.

        Positive:
        stable atmosphere

        Negative:
        unstable atmosphere
        """

        return round(temperature_difference, 2)
