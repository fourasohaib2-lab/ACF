"""
Atmospheric Complexity Framework (ACF)

AWCI Provenance & Audit - Reproducibility

Two real, honest, narrowly-scoped checks - never a claim that a run
"is reproducible" without either (a) a real second computation to
compare against, or (b) a real, complete provenance record that would
in principle let one be re-run. This module does not itself re-run
`AWCICalculator` - the caller supplies both the original and the
recomputed `AWCIResult`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from acf.core.contracts.provenance import Provenance
    from awci.complexity.result import AWCIResult


@dataclass(frozen=True)
class ReproducibilityCheck:
    """Real, exact comparison of two already-computed AWCI scores -
    ``matches`` is a plain, real floating-point tolerance check, never
    a fabricated or estimated judgment."""

    matches: bool
    original_score: float
    recomputed_score: float
    absolute_difference: float
    tolerance: float


def verify_reproducibility(
    original: "AWCIResult", recomputed: "AWCIResult", tolerance: float = 1e-6
) -> ReproducibilityCheck:
    """
    Real reproducibility check between two already-computed
    ``AWCIResult``s (e.g. one from a prior run, one from a fresh
    recompute under the same, or a claimed-identical, real
    ``LockedModel``/config/input data) - a plain real
    ``abs(original.awci - recomputed.awci) <= tolerance`` comparison.
    This function never re-runs the calculation itself; the caller is
    responsible for actually recomputing ``recomputed`` from real,
    matching inputs.
    """
    difference = abs(original.awci - recomputed.awci)
    return ReproducibilityCheck(
        matches=difference <= tolerance,
        original_score=original.awci,
        recomputed_score=recomputed.awci,
        absolute_difference=difference,
        tolerance=tolerance,
    )


def is_reproducible_run(provenance: "Provenance | None") -> bool:
    """
    Real, honest signal for "is there enough real, recorded metadata
    to even ATTEMPT a reproduction of this run" - exactly
    ``Provenance.is_fully_specified()`` (already real, already tested),
    reused here rather than re-derived, and honestly ``False`` when no
    real ``provenance`` was ever attached at all. This is necessary,
    not sufficient, for reproducibility: a fully-specified provenance
    means every real version/source field was recorded, not that the
    real underlying model/data is still available to actually re-run
    against.
    """
    return provenance is not None and provenance.is_fully_specified()
