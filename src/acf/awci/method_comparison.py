"""
AWCI Prediction Method Comparison — Physics-First (§41-§42)
================================================================

docs/ACF_MASTER_PROMPT.md section 41:

    "L'IA peut être étudiée plus tard... une architecture sérieuse doit
    pouvoir comparer Physics-based contre Statistical contre Machine
    Learning contre Hybrid Physics + ML, et mesurer leurs performances."

...and section 42 (PHYSICS-FIRST), the principle this whole module is
built to respect:

    PHYSICS → DIAGNOSTICS → STATISTICS → ML   (correct order)
    ML → invented score → physical interpretation   (never do this)

Found during this session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md): no such comparison framework existed
anywhere in this codebase.

Honest scope - what this module IS and is NOT
-------------------------------------------------
This is the real, general COMPARISON INFRASTRUCTURE section 41 asks
for - a `PredictionMethod` abstraction any real method can implement,
plus `compare_methods()` which scores each one against real
observations using the already-real, already-tested
`acf.verification.nwp_metrics.NWPVerificationMetrics` (not
reimplemented here).

Two of the four categories section 41 names have a REAL implementation
today:
- `PHYSICS_BASED` (`PhysicsBasedMethod`) - a real, thin wrapper around
  `AWCICalculator` itself, ACF's own real physics-driven complexity
  engine.
- `STATISTICAL` (`ClimatologicalBaselineMethod`) - a real, genuinely
  non-physics baseline: the empirical percentile rank of one variable
  against a real climatological sample
  (`Normalizer.normalize_percentile()`, already real, built section
  20 of this same session) - a real statistical comparison point, not
  a second physics model in disguise.

The other two - `MACHINE_LEARNING` and `HYBRID` - have NO real
implementation anywhere in this codebase (confirmed by direct search
during the conformance audit that found this whole section absent).
`NotYetImplementedMethod` is an honest placeholder for them: its
`predict()` RAISES rather than returning a fabricated number. Building
a fake "ML model" here - one not actually trained on any real data,
producing numbers that look plausible but mean nothing - would be
exactly the ML→invented-score→physical-interpretation anti-pattern
section 42 explicitly forbids, and exactly the "réponse certaine mais
inventée" section 88 tells this project to refuse. A real ML/Hybrid
method belongs here the day a real trained model exists to wrap - this
module is that day's real integration point, not a premature
implementation of it.

`compare_methods()` needs real observed values to produce meaningful
metrics - this codebase has no real observed-AWCI dataset (sections 36
"validation des cas" / 37 "validation contre l'expertise humaine" of
the same audit both confirmed absent) - see this module's own test
suite for how it is exercised with clearly-disclosed synthetic
example data in the meantime, the same honest convention already used
throughout this project's own test suite.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from enum import Enum
from typing import Any

from acf.awci.calculator import AWCICalculator
from acf.awci.normalizer import Normalizer
from acf.verification.nwp_metrics import NWPVerificationMetrics


class MethodCategory(str, Enum):
    """The exact 4 categories docs/ACF_MASTER_PROMPT.md section 41 names."""

    PHYSICS_BASED = "physics_based"
    STATISTICAL = "statistical"
    MACHINE_LEARNING = "machine_learning"
    HYBRID = "hybrid"


class PredictionMethod(ABC):
    """A real, comparable AWCI-style prediction method (section 41)."""

    #: One of MethodCategory - set by every real subclass, never left unset.
    category: MethodCategory
    #: Human-readable name shown in compare_methods()'s own results.
    name: str

    @abstractmethod
    def predict(self, data: dict[str, Any]) -> float:
        """Real prediction for one case, a score in [0, 100] matching
        AWCICalculator.calculate()['awci']'s own real scale - so every
        method's output is directly comparable to the others' and to
        real observations on the same scale."""


class PhysicsBasedMethod(PredictionMethod):
    """Real physics-based method - a thin wrapper around
    AWCICalculator itself (section 42: PHYSICS first)."""

    category = MethodCategory.PHYSICS_BASED

    def __init__(self, calculator: AWCICalculator | None = None, name: str = "AWCICalculator (physics-based)") -> None:
        self.calculator = calculator if calculator is not None else AWCICalculator()
        self.name = name

    def predict(self, data: dict[str, Any]) -> float:
        return self.calculator.calculate(data)["awci"]


class ClimatologicalBaselineMethod(PredictionMethod):
    """
    Real, genuinely non-physics statistical baseline (section 41's
    "Statistical" category) - the real empirical percentile rank of
    one variable against a real climatological reference sample
    (Normalizer.normalize_percentile(), not reimplemented here),
    scaled to AWCICalculator's own 0-100 range. Deliberately ignores
    every other variable in `data` - a real, honest single-variable
    statistical baseline is a meaningful comparison point precisely
    BECAUSE it is simpler than the physics-based method, not a second
    attempt at the same thing.
    """

    category = MethodCategory.STATISTICAL

    def __init__(self, variable: str, climatology: list[float], name: str = "") -> None:
        self.variable = variable
        self.climatology = list(climatology)
        self.name = name or f"Climatological percentile baseline ({variable})"

    def predict(self, data: dict[str, Any]) -> float:
        if self.variable not in data:
            raise KeyError(
                f"{self.name}: required variable {self.variable!r} not present in this case's data - "
                "no real prediction possible, never silently fabricated."
            )
        return Normalizer.normalize_percentile(data[self.variable], self.climatology) * 100.0


class NotYetImplementedMethod(PredictionMethod):
    """
    Honest placeholder for MACHINE_LEARNING/HYBRID (section 41) - no
    real trained model exists anywhere in this codebase to wrap (see
    this module's own docstring). `predict()` raises rather than
    fabricating a number - a real ML/Hybrid method should replace this
    placeholder, not extend it, once a real trained model exists.
    """

    def __init__(self, category: MethodCategory, name: str) -> None:
        if category not in (MethodCategory.MACHINE_LEARNING, MethodCategory.HYBRID):
            raise ValueError(
                f"NotYetImplementedMethod is only a real, disclosed placeholder for "
                f"MACHINE_LEARNING/HYBRID - {category} has a real implementation "
                "(PhysicsBasedMethod/ClimatologicalBaselineMethod), use that instead."
            )
        self.category = category
        self.name = name

    def predict(self, data: dict[str, Any]) -> float:
        raise NotImplementedError(
            f"{self.name} ({self.category.value}): no real implementation exists yet - see "
            "acf.awci.method_comparison's own module docstring for why this is a disclosed, "
            "deliberate absence (section 42: never fabricate an ML prediction with no real "
            "trained model behind it), not a bug."
        )


def compare_methods(
    methods: Sequence[PredictionMethod],
    cases: Sequence[dict[str, Any]],
    observations: Sequence[float],
    threshold: float = 50.0,
) -> dict[str, dict[str, Any]]:
    """
    Real comparison (docs/ACF_MASTER_PROMPT.md section 41): each real
    method's real predict() over every case, scored against real
    `observations` via the already-real, already-tested
    acf.verification.nwp_metrics.NWPVerificationMetrics.evaluate_all()
    (RMSE/bias/MAE/ACC/POD/FAR/CSI/ETS - not reimplemented here).

    Parameters
    ----------
    methods : sequence of PredictionMethod
        Real methods to compare - each one's own real predict() runs,
        including NotYetImplementedMethod's real NotImplementedError
        if included (propagated, never silently caught/skipped - a
        caller who wants to compare only the real methods available
        today should simply not include a placeholder).
    cases : sequence of dict
        Real input data per case, one dict per case, aligned by index
        with `observations`.
    observations : sequence of float
        Real observed/reference AWCI-scale values, one per case,
        aligned by index with `cases`.
    threshold : float
        The categorical event threshold POD/FAR/CSI/ETS are computed
        against (NWPVerificationMetrics.evaluate_all()'s own
        `threshold` parameter) - defaults to 50.0, matching
        AWCICalculator.LEVEL_THRESHOLDS' own real "Moderate" complexity
        cutoff (a real, disclosed choice, not NWPVerificationMetrics'
        own generic default of 1.0, which would be nearly meaningless
        on AWCI's real 0-100 scale - almost every real score exceeds 1).

    Returns
    -------
    dict[str, dict]
        Keyed by each method's own `name`; each value is
        `{"category": ..., **NWPVerificationMetrics.evaluate_all(predictions, observations, threshold)}`.

    Raises
    ------
    ValueError
        If `cases` and `observations` have different lengths - a
        length mismatch would silently misalign predictions against
        the wrong real observations.
    """
    if len(cases) != len(observations):
        raise ValueError(f"cases and observations must have the same length, got {len(cases)} and {len(observations)}")

    results: dict[str, dict[str, Any]] = {}
    for method in methods:
        predictions = [method.predict(case) for case in cases]
        results[method.name] = {
            "category": method.category.value,
            **NWPVerificationMetrics.evaluate_all(predictions, list(observations), threshold),
        }
    return results
