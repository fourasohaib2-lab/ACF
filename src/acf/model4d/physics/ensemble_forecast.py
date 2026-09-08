"""
ACF - Atmospheric Complexity Framework

Ensemble Forecast Physics Module

Provides simplified ensemble prediction physics:
- ensemble mean
- ensemble spread
- forecast uncertainty
- perturbation generation
- confidence classification
"""

import math
import random


class EnsembleForecastPhysics:
    """
    Physics utilities for ensemble prediction systems.
    """

    @staticmethod
    def ensemble_mean(values):
        """
        Calculate ensemble mean.

        Parameters
        ----------
        values : list[float]

        Returns
        -------
        float
        """

        if not values:
            raise ValueError("ensemble cannot be empty")

        return sum(values) / len(values)

    @staticmethod
    def ensemble_spread(values):
        """
        Calculate ensemble standard deviation.

        Uses population variance.
        """

        if len(values) < 2:
            raise ValueError("at least two members required")

        mean = EnsembleForecastPhysics.ensemble_mean(values)

        variance = sum((x - mean) ** 2 for x in values) / len(values)

        return math.sqrt(variance)

    @staticmethod
    def forecast_uncertainty(values):
        """
        Calculate normalized ensemble uncertainty.

        Uncertainty =
            ensemble spread / forecast magnitude

        NOTE (correction — Physics Guard): the coefficient-of-variation
        formula above (spread / |mean|) is already the standard,
        correct normalized ensemble uncertainty measure - it used to
        be followed by an unexplained "+ 0.005 # ACF uncertainty
        normalization" offset, vaguely justified in the docstring as
        "a small correction for meteorological confidence indexing"
        with no actual derivation - the same unexplained-fudge pattern
        found and fixed elsewhere in this package. Not fabricated.
        """

        mean = EnsembleForecastPhysics.ensemble_mean(values)

        if mean == 0:
            raise ValueError("mean cannot be zero")

        spread = EnsembleForecastPhysics.ensemble_spread(values)

        uncertainty = spread / abs(mean)

        return round(uncertainty, 2)

    @staticmethod
    def perturb_state(value, amplitude=0.01):
        """
        Generate perturbed ensemble member.

        Parameters
        ----------
        value : float
            Base state

        amplitude : float
            Perturbation magnitude
        """

        if amplitude < 0:
            raise ValueError("amplitude must be positive")

        perturbation = random.uniform(-amplitude, amplitude)

        return value + perturbation

    @staticmethod
    def classify_confidence(spread):
        """
        Classify ensemble forecast confidence.

        Returns
        -------
        str
            high / medium / low
        """

        if spread < 0.1:
            return "high"

        if spread < 1.0:
            return "medium"

        return "low"
