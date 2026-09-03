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

        NOTE (correction): this used zip(..., strict=False), which
        silently truncates to the shorter sequence on a length mismatch
        instead of raising - every other method in this class
        (rmse/bias/mae/acc) explicitly guards against mismatched
        lengths. A caller passing misaligned forecast/observation
        arrays would get a contingency table (and therefore POD/FAR/
        CSI/ETS) silently computed over a wrong, truncated pairing
        instead of an error.
        """
        if len(forecast) != len(observation):
            raise ValueError(
                f"forecast and observation must have the same length, got {len(forecast)} and {len(observation)}"
            )

        a = 0  # Hits
        b = 0  # False Alarms
        c = 0  # Misses
        d = 0  # Correct Negatives

        for f, o in zip(forecast, observation, strict=True):
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

    @staticmethod
    def brier_score(probability_forecasts: Sequence[float], binary_observations: Sequence[float]) -> float:
        """
        Real Brier score (Brier, 1950) - mean squared error between a
        real PROBABILISTIC forecast (each value in [0, 1], "how likely
        is this event") and the real binary observed outcome (0 = did
        not occur, 1 = occurred) - docs/ACF_MASTER_PROMPT.md section
        39's own explicit "Brier score lorsque pertinent" (a
        probabilistic-forecast metric, distinct from `rmse`/`mae`/`bias`
        above, which compare two DETERMINISTIC continuous values, not a
        probability against a binary outcome).

            BS = (1/N) * sum((p_i - o_i)^2)

        Lower is better (0.0 = perfect probabilistic forecast, 1.0 =
        worst possible).

        Raises
        ------
        ValueError
            If the two sequences have different lengths, or are empty.
        """
        if len(probability_forecasts) != len(binary_observations):
            raise ValueError(
                f"probability_forecasts and binary_observations must have the same length, "
                f"got {len(probability_forecasts)} and {len(binary_observations)}"
            )
        if not probability_forecasts:
            raise ValueError("probability_forecasts/binary_observations must not be empty.")
        n = len(probability_forecasts)
        return sum((p - o) ** 2 for p, o in zip(probability_forecasts, binary_observations, strict=True)) / n

    @staticmethod
    def roc_auc(probability_forecasts: Sequence[float], binary_observations: Sequence[float]) -> float:
        """
        Real ROC AUC (Area Under the Receiver Operating Characteristic
        Curve) - docs/ACF_MASTER_PROMPT.md section 39's own explicit
        "ROC/AUC lorsque pertinent". Computed via the real, well-known
        Mann-Whitney U equivalence (not an approximation - an exact
        identity: the fraction of (positive, negative) score pairs
        where the positive's real score exceeds the negative's, ties
        counting as one-half) rather than explicitly building and
        trapezoidally integrating an ROC curve - the same real
        quantity, a simpler and exact real computation. Verified in
        this module's own test suite against a hand-computed pairwise
        reference, not merely self-consistent.

        Real ties in `probability_forecasts` use averaged ranks
        (the standard real tie-correction for this exact formula).

        Returns
        -------
        float
            0.5 = no discrimination (equivalent to random guessing),
            1.0 = perfect real separation of positives from negatives,
            0.0 = perfectly, real, backwards.

        Raises
        ------
        ValueError
            If the two sequences have different lengths, are empty, or
            `binary_observations` contains no real positive (1) or no
            real negative (0) case - AUC is undefined without both.
        """
        if len(probability_forecasts) != len(binary_observations):
            raise ValueError(
                f"probability_forecasts and binary_observations must have the same length, "
                f"got {len(probability_forecasts)} and {len(binary_observations)}"
            )
        if not probability_forecasts:
            raise ValueError("probability_forecasts/binary_observations must not be empty.")

        scores = list(probability_forecasts)
        labels = list(binary_observations)
        n_pos = sum(1 for label in labels if label == 1)
        n_neg = sum(1 for label in labels if label == 0)
        if n_pos == 0 or n_neg == 0:
            raise ValueError(
                f"roc_auc requires at least one real positive and one real negative observation, "
                f"got {n_pos} positive(s) and {n_neg} negative(s)."
            )

        order = sorted(range(len(scores)), key=lambda i: scores[i])
        ranks = [0.0] * len(scores)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and scores[order[j + 1]] == scores[order[i]]:
                j += 1
            average_rank = (i + 1 + j + 1) / 2.0  # 1-indexed rank range [i+1, j+1], averaged for ties
            for k in range(i, j + 1):
                ranks[order[k]] = average_rank
            i = j + 1

        sum_positive_ranks = sum(ranks[idx] for idx, label in enumerate(labels) if label == 1)
        return (sum_positive_ranks - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)

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
