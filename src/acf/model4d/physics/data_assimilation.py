"""
ACF - Atmospheric Complexity Framework
Model4D Physics Engine

Data Assimilation Physics Module
Sprint 8.23

Fusion modèle atmosphérique + observations
Satellite / Radar / Stations / Profils
"""

from dataclasses import dataclass
from math import sqrt


@dataclass
class Observation:
    """
    Observation météorologique.
    """

    value: float
    error: float


class DataAssimilationPhysics:
    """
    Core physics for atmospheric data assimilation.
    """

    @staticmethod
    def innovation(observation, model_value):
        """
        Innovation:
        observation - model prediction
        """

        if observation is None:
            raise ValueError("Observation required")

        return observation - model_value


    @staticmethod
    def observation_weight(error):
        """
        Observation confidence weight.

        w = 1 / error²
        """

        if error <= 0:
            raise ValueError("Error must be positive")

        return 1 / (error ** 2)


    @staticmethod
    def kalman_gain(background_error, observation_error):
        """
        Simplified Kalman gain.

        K = B / (B + R)
        """

        if background_error <= 0:
            raise ValueError("Background error must be positive")

        if observation_error <= 0:
            raise ValueError("Observation error must be positive")

        return background_error / (
            background_error + observation_error
        )


    @staticmethod
    def analysis_update(
        background,
        observation,
        gain
    ):
        """
        Analysis state update.

        Xa = Xb + K(Y-Xb)
        """

        if gain < 0 or gain > 1:
            raise ValueError(
                "Gain must be between 0 and 1"
            )

        return (
            background
            +
            gain * (observation - background)
        )


    @staticmethod
    def four_d_var_cost(
        model_error,
        observation_error
    ):
        """
        Simplified 4D-Var cost function.

        J = background_error²
          + observation_error²
        """

        return (
            model_error ** 2
            +
            observation_error ** 2
        )


    @staticmethod
    def quality_index(error):
        """
        Observation quality index.

        0 = bad
        1 = perfect
        """

        if error < 0:
            raise ValueError(
                "Error cannot be negative"
            )

        return 1 / (1 + error)


    @staticmethod
    def spread(error):
        """
        Ensemble spread approximation.
        """

        if error < 0:
            raise ValueError(
                "Error cannot be negative"
            )

        return sqrt(error)

