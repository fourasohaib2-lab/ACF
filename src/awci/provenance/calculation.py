"""
Atmospheric Complexity Framework (ACF)

AWCI Provenance & Audit - Calculation

Real, structured drill-down of the already-computed numbers on an
``AWCIResult`` - "Which variables? → Which factors?" in the reference
architecture's own traceability chain (section 22). This is a
STRUCTURED (programmatically usable) counterpart to
``AWCIResult.trace_chain()``'s already-real, already-tested string
rendering - built from the exact same real fields, nothing
recomputed, nothing invented.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from awci.complexity.result import AWCIResult


@dataclass(frozen=True)
class CalculationStep:
    """One real step of the real AWCI calculation chain - a module
    score, an interaction term, or the final composite score, each
    already computed and stored on the ``AWCIResult`` this was built
    from."""

    kind: str  # "module_score" | "interaction_term" | "final_score"
    name: str
    value: float


def describe_calculation(result: "AWCIResult") -> tuple[CalculationStep, ...]:
    """
    Real, ordered calculation trail - every real module score
    (``result.module_scores``), every real interaction term
    (``result.interaction_scores``), then the real final composite
    score (``result.awci``) - in that order, matching the real
    contribution → composition → result flow
    ``AWCICalculator.calculate()`` itself follows. Every value here is
    read directly from ``result``'s own already-computed fields; this
    function performs no arithmetic of its own.
    """
    steps: list[CalculationStep] = [
        CalculationStep(kind="module_score", name=name, value=value)
        for name, value in sorted(result.module_scores.items())
    ]
    steps.extend(
        CalculationStep(kind="interaction_term", name=name, value=value)
        for name, value in sorted(result.interaction_scores.items())
    )
    steps.append(CalculationStep(kind="final_score", name="awci", value=result.awci))
    return tuple(steps)
