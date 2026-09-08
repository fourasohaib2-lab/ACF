"""
Ensemble Uncertainty
=====================

Standard ensemble-forecast statistics: spread, percentiles,
exceedance probability, and a simple consensus/agreement metric.
These are standard statistical operations (not physical laws needing
external verification) applied to a set of ensemble member forecasts.

Reference:
    Standard ensemble forecast verification practice, e.g. Wilks
    (2011), "Statistical Methods in the Atmospheric Sciences", Ch. 8.
"""

from dataclasses import dataclass, field

from acf.science.climatology import Climatology


@dataclass
class EnsembleMember:
    """One ensemble member's forecast value for a single variable/time/location."""

    member_id: str
    value: float


@dataclass
class EnsembleRun:
    """A full ensemble forecast (all members) for one variable/time/location."""

    variable: str
    members: list[EnsembleMember] = field(default_factory=list)

    def values(self) -> list[float]:
        return [m.value for m in self.members]

    def mean(self) -> float:
        """Ensemble mean."""
        vals = self.values()
        if not vals:
            raise ValueError("ensemble has no members.")
        return sum(vals) / len(vals)

    def spread(self) -> float:
        """
        Ensemble spread: population standard deviation across members
        — the standard measure of ensemble forecast uncertainty.
        """
        vals = self.values()
        if len(vals) < 2:
            raise ValueError("spread requires at least 2 members.")
        m = self.mean()
        variance = sum((v - m) ** 2 for v in vals) / len(vals)
        return variance**0.5

    def percentile(self, percentile: float) -> float:
        """Value at a given percentile across members. See Climatology.percentile_value()."""
        return Climatology.percentile_value(self.values(), percentile)

    def probability_exceeding(self, threshold: float) -> float:
        """
        Empirical probability (fraction of members) exceeding a
        threshold — the standard ensemble-based probabilistic
        forecast for a threshold event.

        Parameters
        ----------
        threshold : float
            The threshold value.

        Returns
        -------
        float
            Fraction of members with value > threshold, in [0, 1].
        """
        vals = self.values()
        if not vals:
            raise ValueError("ensemble has no members.")
        return sum(1 for v in vals if v > threshold) / len(vals)


@dataclass
class UncertaintyEstimate:
    """Summary uncertainty estimate for one ensemble run."""

    mean: float
    spread: float
    p10: float
    p50: float
    p90: float

    @staticmethod
    def from_ensemble(run: EnsembleRun) -> "UncertaintyEstimate":
        return UncertaintyEstimate(
            mean=run.mean(),
            spread=run.spread(),
            p10=run.percentile(10.0),
            p50=run.percentile(50.0),
            p90=run.percentile(90.0),
        )


@dataclass
class ConsensusResult:
    """Agreement-based consensus summary across ensemble members."""

    consensus_value: float
    agreement_fraction: float
    recommendation: str

    @staticmethod
    def from_ensemble(run: EnsembleRun, agreement_tolerance: float) -> "ConsensusResult":
        """
        Build a consensus summary: the ensemble median as the
        consensus value, and the fraction of members within
        agreement_tolerance of that median as the agreement score.

        Parameters
        ----------
        run : EnsembleRun
        agreement_tolerance : float
            Members within +/- this amount of the median count as
            "in agreement" (same units as the variable).

        Returns
        -------
        ConsensusResult
            recommendation is "High confidence" (agreement >= 0.8),
            "Moderate confidence" (>= 0.5), or "Low confidence /
            divergent" (< 0.5) — a simple, documented ACF convention,
            not an external published standard.
        """
        if agreement_tolerance < 0:
            raise ValueError("agreement_tolerance must be non-negative.")

        median = run.percentile(50.0)
        vals = run.values()
        if not vals:
            raise ValueError("ensemble has no members.")

        agreeing = sum(1 for v in vals if abs(v - median) <= agreement_tolerance)
        agreement_fraction = agreeing / len(vals)

        if agreement_fraction >= 0.8:
            recommendation = "High confidence"
        elif agreement_fraction >= 0.5:
            recommendation = "Moderate confidence"
        else:
            recommendation = "Low confidence / divergent"

        return ConsensusResult(
            consensus_value=median, agreement_fraction=agreement_fraction, recommendation=recommendation
        )
