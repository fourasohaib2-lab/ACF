"""Probabilistic hazard risk and threshold engine."""

from typing import List, Dict
import numpy as np


class ProbabilityEngine:
    """Calculates probabilistic hazard metrics from ensemble predictions.

    Example outputs:
        P(Rainfall > 100mm) = 42%
        P(Wind Speed > 33 m/s) = 15%
        90th percentile heat wave temperature
    """

    def __init__(self) -> None:
        pass

    def compute_exceedance_probability(
        self, member_fields: List[np.ndarray], threshold: float
    ) -> np.ndarray:
        """Calculate probability P(X >= threshold) = count(X >= threshold) / N_members.

        Args:
            member_fields (List[np.ndarray]): List of 2D/3D arrays from each member.
            threshold (float): Numeric threshold value.

        Returns:
            np.ndarray: Probability array in range [0.0, 1.0].
        """
        stack = np.stack(member_fields, axis=0)
        exceed_mask = stack >= threshold
        prob = np.mean(exceed_mask.astype(np.float64), axis=0)
        return prob

    def compute_percentiles(
        self, member_fields: List[np.ndarray], percentiles: List[float] = [10.0, 50.0, 90.0]
    ) -> Dict[float, np.ndarray]:
        """Compute array quantiles across ensemble members.

        Args:
            member_fields (List[np.ndarray]): List of member arrays.
            percentiles (List[float]): List of percentiles (e.g. 10th, 50th, 90th).

        Returns:
            Dict[float, np.ndarray]: Map of percentile value to field array.
        """
        stack = np.stack(member_fields, axis=0)
        results = {}
        for p in percentiles:
            results[p] = np.percentile(stack, p, axis=0)
        return results
