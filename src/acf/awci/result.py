"""
AWCI Complete Result (§81)
=============================

docs/ACF_MASTER_PROMPT.md section 81:

    "Toujours conserver au minimum : AWCI score, AWCI class, AWCI
    confidence, AWCI dominant factors, AWCI interactions, AWCI model
    spread, AWCI quality, AWCI provenance."

Found during this session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md): `AWCICalculator.calculate()` already
returns score/class/confidence/dominant-factors(via `explanation`)/
interactions - but `model spread`, `quality`, and `provenance` exist
only as separate, real systems elsewhere in this codebase
(`acf.visualization.ai_forecast_center.model_consensus_engine.
ModelConsensusEngine`, `acf.physics_guard.variable_quality.
assess_variable_quality()`, `acf.core.contracts.provenance.Provenance`)
- never attached to a `calculate()` result itself, so a caller wanting
all 8 real fields section 81 requires had to know to combine 4
separate systems by hand.

Honest scope
-------------
`build_awci_result()` is a real ASSEMBLER, not a new computation - it
NEVER computes model_spread/quality/provenance itself (that would mean
guessing which real climatology/model-comparison/generator string a
caller actually wants, or worse, silently defaulting them to a
fabricated placeholder). A caller supplies whatever real values it
already has from those 3 real systems (or the CF-standard-name-keyed
`data` this calculator's own AWCI-simplified variable names cannot be
mapped to automatically without guessing a specific unit/naming
convention - see AWCIResult's own field docstrings) - fields left
unsupplied stay honestly `None`, matching every other "prefer UNKNOWN
to a fabricated value" convention already used throughout this project
(section 61).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from acf.core.contracts.provenance import Provenance
    from acf.physics_guard.variable_quality import VariableQualityStatus


@dataclass
class AWCIResult:
    """
    The complete, real minimum result set docs/ACF_MASTER_PROMPT.md
    section 81 requires, assembled in one real, traceable object -
    built by `build_awci_result()` below, never constructed by hand
    from a `calculate()` output (risks silently drifting from what
    `calculate()` actually returned).
    """

    #: AWCI score - AWCICalculator.calculate()['awci'].
    awci: float
    #: AWCI class - calculate()['level'].
    level: str
    #: AWCI confidence - calculate()['confidence'].
    confidence: float
    #: AWCI dominant factors - the top real contributors from
    #: calculate()['explanation'] (already real, already sorted by
    #: contribution - not recomputed here), by label, largest first.
    dominant_factors: list[str]
    #: AWCI interactions - calculate()['interaction_scores'].
    interaction_scores: dict[str, float]
    #: The full real module + interaction decomposition (calculate()['decomposition']).
    decomposition: dict[str, float]
    module_scores: dict[str, float]
    explanation: list[str]
    physical_score: float | None
    forecast_score: float | None
    #: AWCI model spread - real, e.g. ModelConsensusEngine.
    #: compute_real_multi_model_disagreement()'s own return dict, or
    #: AWCICalculator.calculate_with_uncertainty()'s own uncertainty
    #: fields - supplied by the caller from whichever real computation
    #: it already ran. None (not a fabricated 0.0) when no real
    #: multi-model/ensemble comparison was run for this result.
    model_spread: dict[str, Any] | None = None
    #: AWCI quality - real, e.g.
    #: acf.physics_guard.variable_quality.assess_variable_quality()'s
    #: own return dict, supplied by the caller (this calculator's own
    #: `data` uses AWCI's simplified variable names, e.g. "wind_speed",
    #: not the CF standard names/units assess_variable_quality() itself
    #: expects - see acf.aviation.icao.metar_decoder.
    #: metar_report_quality() for a real, worked example of that
    #: bridge). None when no real quality assessment was run.
    quality: dict[str, VariableQualityStatus] | None = None
    #: AWCI provenance - real, e.g. a real
    #: acf.core.contracts.provenance.Provenance the caller already
    #: built (generator/algorithm_version/science_version/
    #: config_version/created_at). None when no real provenance was
    #: attached.
    provenance: Provenance | None = None


def build_awci_result(
    calculate_output: dict[str, Any],
    *,
    model_spread: dict[str, Any] | None = None,
    quality: dict[str, VariableQualityStatus] | None = None,
    provenance: Provenance | None = None,
    max_dominant_factors: int = 3,
) -> AWCIResult:
    """
    Real assembler: wraps an existing, already-computed
    `AWCICalculator.calculate()` output plus whatever real
    model_spread/quality/provenance the caller already has into one
    complete AWCIResult (docs/ACF_MASTER_PROMPT.md section 81) - never
    computes any of the 3 optional fields itself (see module docstring).

    Parameters
    ----------
    calculate_output : dict
        A real, already-computed `AWCICalculator.calculate()` return
        value - not recomputed or validated here beyond reading its
        own real keys.
    model_spread, quality, provenance : optional
        Real values from the caller's own real computation elsewhere -
        see AWCIResult's own field docstrings for what each expects.
        Left as None (never fabricated) when not supplied.
    max_dominant_factors : int
        How many of `calculate_output['explanation']`'s own real,
        already-contribution-sorted entries to surface as
        `dominant_factors` (default 3, matching section 49's own
        worked example of 3-4 "principaux facteurs").

    Returns
    -------
    AWCIResult
    """
    dominant_factors = [line.split(" : ")[0] for line in calculate_output["explanation"][:max_dominant_factors]]
    return AWCIResult(
        awci=calculate_output["awci"],
        level=calculate_output["level"],
        confidence=calculate_output["confidence"],
        dominant_factors=dominant_factors,
        interaction_scores=calculate_output["interaction_scores"],
        decomposition=calculate_output["decomposition"],
        module_scores=calculate_output["module_scores"],
        explanation=calculate_output["explanation"],
        physical_score=calculate_output["physical_score"],
        forecast_score=calculate_output["forecast_score"],
        model_spread=model_spread,
        quality=quality,
        provenance=provenance,
    )
