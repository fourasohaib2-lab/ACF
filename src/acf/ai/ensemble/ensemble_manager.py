"""
Atmospheric Complexity Framework (ACF)

AI & NWP Ensemble Forecasting & Probabilistic Verification Module
(Ensemble Statistics, Spread, Probability Exceedance, CRPS, Brier Score)
"""

import math
from typing import Any, Dict, List


class EnsembleManager:
    """
    Gestionnaire et analyseur statistique d'ensembles de prévision numérique et stochastique d'IA.
    """

    def __init__(self, member_values: List[float]):
        self.members = sorted(member_values)
        self.n_members = len(member_values)

    @property
    def mean(self) -> float:
        """Moyenne d'ensemble (Ensemble Mean)."""
        if not self.members:
            return 0.0
        return sum(self.members) / self.n_members

    @property
    def median(self) -> float:
        """Médiane d'ensemble."""
        if not self.members:
            return 0.0
        mid = self.n_members // 2
        if self.n_members % 2 == 1:
            return self.members[mid]
        return (self.members[mid - 1] + self.members[mid]) / 2.0

    @property
    def spread(self) -> float:
        """Écart-type d'ensemble (Ensemble Spread / Standard Deviation)."""
        if self.n_members < 2:
            return 0.0
        m = self.mean
        variance = sum((x - m) ** 2 for x in self.members) / (self.n_members - 1)
        return math.sqrt(variance)

    def percentile(self, p: float) -> float:
        """Calcule le p-ième percentile (0.0 <= p <= 100.0)."""
        if not self.members:
            return 0.0
        if p <= 0:
            return self.members[0]
        if p >= 100:
            return self.members[-1]
        k = (self.n_members - 1) * (p / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return self.members[int(k)]
        d0 = self.members[int(f)] * (c - k)
        d1 = self.members[int(c)] * (k - f)
        return d0 + d1

    def probability_exceedance(self, threshold: float) -> float:
        """
        Calcule la probabilité de dépassement d'un seuil P(X >= threshold).
        """
        if not self.members:
            return 0.0
        exceed_count = sum(1 for x in self.members if x >= threshold)
        return exceed_count / float(self.n_members)

    def brier_score(self, threshold: float, observed_event: bool) -> float:
        """Score de Brier pour la prévision probabiliste d'un événement binaire."""
        prob = self.probability_exceedance(threshold)
        obs_val = 1.0 if observed_event else 0.0
        return (prob - obs_val) ** 2

    def crps(self, observation: float) -> float:
        """Continuous Ranked Probability Score (CRPS)."""
        if not self.members:
            return 0.0
        term1 = sum(abs(x - observation) for x in self.members) / self.n_members
        term2 = sum(abs(x - y) for x in self.members for y in self.members) / (2.0 * (self.n_members ** 2))
        return term1 - term2

    def summary(self) -> Dict[str, Any]:
        """Résumé statistique complet de l'ensemble."""
        return {
            "n_members": self.n_members,
            "mean": self.mean,
            "median": self.median,
            "spread": self.spread,
            "min": self.members[0] if self.members else 0.0,
            "max": self.members[-1] if self.members else 0.0,
            "p10": self.percentile(10.0),
            "p90": self.percentile(90.0),
        }
