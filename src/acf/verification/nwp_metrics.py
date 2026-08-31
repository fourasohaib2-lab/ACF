"""
Atmospheric Complexity Framework (ACF) - NWP Verification Metrics (ACF-NWP-001)

Computes continuous (RMSE, BIAS, MAE, ACC) and categorical (ETS, CSI, POD, FAR) verification metrics.
"""

from __future__ import annotations

import math
from collections.abc import Sequence


class NWPVerificationMetrics:
    """
    Calculator for continuous and categorical NWP verification metrics.
    """

    @staticmethod
    def rmse(forecast: Sequence[float], observation: Sequence[float]) -> float:
        """Root Mean Square Error."""
        if not forecast or len(forecast) != len(observation):
            return 0.0
        n = len(forecast)
        mse = sum((f - o) ** 2 for f, o in zip(forecast, observation, strict=True)) / n
        return math.sqrt(mse)

    @staticmethod
    def bias(forecast: Sequence[float], observation: Sequence[float]) -> float:
        """Mean Error (BIAS)."""
        if not forecast or len(forecast) != len(observation):
            return 0.0
        n = len(forecast)
        return sum(f - o for f, o in zip(forecast, observation, strict=True)) / n

    @staticmethod
    def mae(forecast: Sequence[float], observation: Sequence[float]) -> float:
        """Mean Absolute Error."""
        if not forecast or len(forecast) != len(observation):
            return 0.0
        n = len(forecast)
        return sum(abs(f - o) for f, o in zip(forecast, observation, strict=True)) / n

    @staticmethod
    def acc(
        forecast: Sequence[float], observation: Sequence[float], climatology: Sequence[float] | None = None
    ) -> float:
        """Anomaly Correlation Coefficient."""
        if not forecast or len(forecast) != len(observation):
            return 1.0
        n = len(forecast)
        c = climatology if (climatology and len(climatology) == n) else [sum(observation) / n] * n

        f_anom = [f - ci for f, ci in zip(forecast, c, strict=True)]
        o_anom = [o - ci for o, ci in zip(observation, c, strict=True)]

        num = sum(fa * oa for fa, oa in zip(f_anom, o_anom, strict=True))
        den = math.sqrt(sum(fa**2 for fa in f_anom) * sum(oa**2 for oa in o_anom))

        return (num / den) if den != 0 else 1.0

    @staticmethod
    def contingency_table(forecast: Sequence[float], observation: Sequence[float], threshold: float) -> dict[str, int]:
        """
        Computes 2x2 contingency table (hits, false_alarms, misses, correct_negatives).
        """
        a = 0  # Hits
        b = 0  # False Alarms
        c = 0  # Misses
        d = 0  # Correct Negatives

        for f, o in zip(forecast, observation, strict=False):
            f_event = f >= threshold
            o_event = o >= threshold

            if f_event and o_event:
                a += 1
            elif f_event and not o_event:
                b += 1
            elif not f_event and o_event:
                c += 1
            else:
                d += 1

        return {"hits": a, "false_alarms": b, "misses": c, "correct_negatives": d}

    @staticmethod
    def pod(forecast: Sequence[float], observation: Sequence[float], threshold: float) -> float:
        """Probability of Detection (Hit Rate)."""
        ct = NWPVerificationMetrics.contingency_table(forecast, observation, threshold)
        a, c = ct["hits"], ct["misses"]
        return (a / (a + c)) if (a + c) > 0 else 1.0

    @staticmethod
    def far(forecast: Sequence[float], observation: Sequence[float], threshold: float) -> float:
        """False Alarm Ratio."""
        ct = NWPVerificationMetrics.contingency_table(forecast, observation, threshold)
        a, b = ct["hits"], ct["false_alarms"]
        return (b / (a + b)) if (a + b) > 0 else 0.0

    @staticmethod
    def csi(forecast: Sequence[float], observation: Sequence[float], threshold: float) -> float:
        """Critical Success Index (Threat Score)."""
        ct = NWPVerificationMetrics.contingency_table(forecast, observation, threshold)
        a, b, c = ct["hits"], ct["false_alarms"], ct["misses"]
        return (a / (a + b + c)) if (a + b + c) > 0 else 1.0

    @staticmethod
    def ets(forecast: Sequence[float], observation: Sequence[float], threshold: float) -> float:
        """Equitable Threat Score."""
        ct = NWPVerificationMetrics.contingency_table(forecast, observation, threshold)
        a, b, c, d = ct["hits"], ct["false_alarms"], ct["misses"], ct["correct_negatives"]
        total = a + b + c + d
        a_random = ((a + b) * (a + c)) / total if total > 0 else 0.0

        den = a + b + c - a_random
        return ((a - a_random) / den) if den != 0 else 0.0

    @classmethod
    def evaluate_all(
        cls, forecast: Sequence[float], observation: Sequence[float], threshold: float = 1.0
    ) -> dict[str, float]:
        """Evaluates complete suite of NWP metrics."""
        return {
            "rmse": cls.rmse(forecast, observation),
            "bias": cls.bias(forecast, observation),
            "mae": cls.mae(forecast, observation),
            "acc": cls.acc(forecast, observation),
            "pod": cls.pod(forecast, observation, threshold),
            "far": cls.far(forecast, observation, threshold),
            "csi": cls.csi(forecast, observation, threshold),
            "ets": cls.ets(forecast, observation, threshold),
        }
