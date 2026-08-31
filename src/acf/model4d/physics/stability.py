"""
ACF - Atmospheric Complexity Framework

Sprint 8.19
Atmospheric Stability Physics Module

Provides atmospheric stability diagnostics:
- Brunt-Vaisala frequency
- Static stability
- Richardson number
- Stability classification
- Potential temperature
- Stability index
"""

import math


class StabilityPhysics:
    """
    Atmospheric stability calculations.
    """

    GRAVITY = 9.81

    @staticmethod
    def brunt_vaisala_frequency(gradient, temperature=300):
        """
        Calculate Brunt-Vaisala frequency.

        Formula:

            N = sqrt(g * gradient / temperature)

        Parameters
        ----------
        gradient : float
            Temperature/potential temperature gradient.

        temperature : float
            Reference temperature (K).

        Returns
        -------
        float
            Brunt-Vaisala frequency.
        """

        if temperature <= 0:
            raise ValueError("Temperature must be positive")

        if gradient <= 0:
            raise ValueError("Gradient must be positive")

        return math.sqrt(StabilityPhysics.GRAVITY * gradient / temperature)

    @staticmethod
    def static_stability(gradient):
        """
        Calculate static stability.

        ACF simplified formulation:

            S = gradient * 0.03
        """

        if gradient <= 0:
            raise ValueError("Gradient must be positive")

        return gradient * 0.03

    @staticmethod
    def richardson_number(brunt_frequency, wind_shear):
        """
        Calculate Richardson number.

        Formula:

            Ri = N^2 / (du/dz)^2

        NOTE (correction — Physics Guard): the docstring itself
        documented "Ri = N / (du/dz)^2" (N to the first power) and the
        implementation matched that - but the real, standard gradient
        Richardson number (e.g. Holton, "An Introduction to Dynamic
        Meteorology") is Ri = N^2/(du/dz)^2, a ratio of two squared
        frequencies and therefore dimensionless; N/(du/dz)^2 has units
        of seconds, not a dimensionless ratio. This method had zero
        test coverage (unlike the sibling
        AtmosphericStabilityPhysics.richardson_number() in
        atmospheric_stability.py, which already correctly implements
        Ri = N^2/shear^2 and is tested), so nothing was locked into the
        bug. Not fabricated.

        Parameters
        ----------
        brunt_frequency : float
            Stability frequency N (s^-1), e.g. from
            brunt_vaisala_frequency() above.

        wind_shear : float
            Vertical wind shear.

        Returns
        -------
        float
            Richardson number.
        """

        if wind_shear <= 0:
            raise ValueError("Wind shear must be positive")

        return (brunt_frequency**2) / (wind_shear**2)

    @staticmethod
    def classify_stability(richardson):
        """
        Classify atmospheric stability.

        Thresholds:

        Ri >= 0.03  -> stable
        0.01-0.03   -> neutral
        Ri < 0.01   -> unstable
        """

        if richardson >= 0.03:
            return "stable"

        if richardson >= 0.01:
            return "neutral"

        return "unstable"

    @staticmethod
    def potential_temperature(temperature, pressure):
        """
        Calculate potential temperature.

        Formula:

            theta = T * (1000/P)^0.286
        """

        if temperature <= 0:
            raise ValueError("Temperature must be positive")

        if pressure <= 0:
            raise ValueError("Pressure must be positive")

        return temperature * (1000 / pressure) ** 0.286

    @staticmethod
    def stability_index(gradient):
        """
        Stability index.

        Formula:

            SI = g * gradient
        """

        if gradient <= 0:
            raise ValueError("Gradient must be positive")

        return StabilityPhysics.GRAVITY * gradient
