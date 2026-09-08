"""
AWCI Execution Report (docs/ACF_MASTER_PROMPT.md §75)
=======================================================

    "Le pipeline doit produire : logs, metrics, warnings, errors,
    quality reports, runtime statistics."

    Exemple ::

        Input files: 48
        Valid: 46
        Rejected: 2
        Diagnostics: 123
        AWCI generated: YES
        Quality: GOOD
        Model spread: HIGH

Honest scope
-------------
`summarize_execution()` is a real ASSEMBLER over an already-built
`acf.awci.result.AWCIResult` - it never computes anything itself
(same discipline as `build_awci_result()`). Two honest reinterpretations
of the prompt's own literal wording, disclosed here rather than
guessed silently:

- "Input files" - `AWCICalculator.calculate()` never reads files; it
  consumes a real `data` dict of named variables. This report counts
  real INPUT VARIABLES instead (from `AWCIResult.quality`, section 32's
  own per-variable quality vocabulary) - the closest real, honest
  analog to the prompt's own "how many inputs, how many were usable"
  intent.
- "Model spread: HIGH" - `ModelConsensusEngine.
  compute_real_multi_model_disagreement()`'s own real
  `disagreement_spread` has no universal scale (its unit depends on
  which field was compared - Kelvin for temperature, m/s for wind,
  kg/kg for humidity...), so a single global LOW/MEDIUM/HIGH threshold
  would be exactly the kind of unvalidated, field-blind classification
  section 79 warns against ("threshold = hypothesis until validated" -
  and worse, arbitrary across units here). This report never invents
  one: it shows the real numeric spread/field/mean, and only reports a
  categorical bucket when the caller supplies one explicitly
  (`model_spread_level` - the caller's own real, disclosed
  classification, e.g. from a domain-appropriate threshold it already
  validated) - "not available" otherwise, never a guessed word.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from acf.awci.result import AWCIResult

#: Real, disclosed ACF design choice (not derived from a published
#: standard) for the aggregate "Quality" bucket below - matches this
#: project's own established convention of disclosing every threshold
#: as an ACF choice rather than presenting it as literature-established
#: (section 78/79). Fractions of a result's own real per-variable
#: quality statuses (section 32's 9-value vocabulary) that are NOT
#: "VALID" (rejected) or "SUSPECT".
_DEGRADED_MAX_REJECTED_FRACTION = 0.5


@dataclass
class AWCIExecutionReport:
    """Real per-execution report, section 75's own worked example
    format - built by `summarize_execution()` below, never constructed
    by hand from an `AWCIResult` (risks silently drifting)."""

    #: Whether AWCIResult.quality was supplied at all - when False,
    #: every *_variables_* count below is honestly 0 (not fabricated),
    #: and quality/render() show "not available", not "GOOD"/"0".
    quality_available: bool
    #: Real count of real input variables AWCIResult.quality assessed
    #: (section 32's own per-variable statuses) - the honest analog of
    #: the prompt's own "Input files" (see module docstring).
    input_variables_total: int
    #: Real count with status == "VALID".
    input_variables_valid: int
    #: Real count with status == "SUSPECT" (tracked separately - not
    #: conflated with "rejected", matching section 32's own 9-value
    #: vocabulary rather than a binary valid/invalid collapse).
    input_variables_suspect: int
    #: Real count with any other real status (MISSING/INVALID/
    #: OUT_OF_RANGE/UNIT_ERROR/GRID_ERROR/TIME_ERROR/
    #: PHYSICAL_INCONSISTENCY) - the honest analog of "Rejected".
    input_variables_rejected: int
    #: Real count of this execution's own module + interaction scores
    #: (AWCIResult.module_scores/interaction_scores - the real,
    #: already-computed per-execution diagnostic breakdown, not the
    #: static acf.awci.diagnostic_registry.DIAGNOSTIC_REGISTRY catalog,
    #: which lists every POSSIBLE diagnostic, not this run's own).
    diagnostics_count: int
    #: Always True when this report was built from a real AWCIResult
    #: (calculate() ran to completion) - section 75's own "AWCI
    #: generated: YES/NO". A caller building a report for a run that
    #: genuinely failed before producing an AWCIResult should not call
    #: summarize_execution() at all (there is no real result to
    #: summarize) - see that function's own docstring.
    awci_generated: bool
    #: "GOOD" (quality assessed, nothing rejected), "DEGRADED" (quality
    #: assessed, some but under _DEGRADED_MAX_REJECTED_FRACTION
    #: rejected), "BAD" (quality assessed, at or above that fraction
    #: rejected), or "UNKNOWN" (quality_available is False - never
    #: fabricated as GOOD by omission).
    quality: str
    #: Real numeric model-spread context, when AWCIResult.model_spread
    #: was supplied - never a fabricated categorical bucket (see module
    #: docstring). None when AWCIResult.model_spread is None.
    model_spread_value: float | None
    model_spread_field: str | None
    #: The caller's own real, disclosed categorical bucket for
    #: model_spread_value, if it supplied one to summarize_execution()
    #: - "not available" otherwise (rendered, not stored as this
    #: literal string, to keep this field's real value distinguishable
    #: from a genuine caller-supplied string that happened to match).
    model_spread_level: str | None

    def render(self) -> list[str]:
        """Section 75's own literal example format, one real line per
        field - "not available" wherever this report's own real data
        genuinely does not cover a line, never a fabricated value."""
        if self.quality_available:
            valid_line = f"Valid: {self.input_variables_valid}"
            rejected_line = f"Rejected: {self.input_variables_rejected}"
            if self.input_variables_suspect:
                rejected_line += f" (+ {self.input_variables_suspect} suspect)"
        else:
            valid_line = "Valid: not available (no real quality assessment attached to this result)"
            rejected_line = "Rejected: not available (no real quality assessment attached to this result)"
        return [
            f"Input variables: {self.input_variables_total if self.quality_available else 'not available'}",
            valid_line,
            rejected_line,
            f"Diagnostics: {self.diagnostics_count}",
            f"AWCI generated: {'YES' if self.awci_generated else 'NO'}",
            f"Quality: {self.quality}",
            f"Model spread: {self._render_model_spread()}",
        ]

    def _render_model_spread(self) -> str:
        if self.model_spread_value is None:
            return "not available (no real multi-model comparison attached to this result)"
        field = f" ({self.model_spread_field})" if self.model_spread_field else ""
        level = self.model_spread_level if self.model_spread_level is not None else "not classified"
        return f"{level} - real spread {self.model_spread_value:.4g}{field}"


def summarize_execution(result: AWCIResult, *, model_spread_level: str | None = None) -> AWCIExecutionReport:
    """
    Real assembler: build a section-75 execution report from an
    already-built `AWCIResult` - never recomputes `calculate()`,
    `assess_variable_quality()`, or `compute_real_multi_model_disagreement()`
    itself (same "real assembler, not a new computation" discipline as
    `acf.awci.result.build_awci_result()`).

    Parameters
    ----------
    result : AWCIResult
        A real, already-built result (calculate() ran to completion -
        this function assumes AWCI generation succeeded, matching
        section 75's own "AWCI generated: YES" example; there is
        nothing to summarize for a run that failed before producing
        one).
    model_spread_level : str, optional
        The caller's own real, disclosed categorical bucket for
        `result.model_spread`'s numeric spread (e.g. "LOW"/"MEDIUM"/
        "HIGH", using whatever real, domain-appropriate threshold the
        caller has validated for the specific field compared) - never
        guessed here (see module docstring). Ignored (has no effect)
        when `result.model_spread` is None.

    Returns
    -------
    AWCIExecutionReport
    """
    quality = result.quality
    quality_available = quality is not None
    if quality_available:
        assert quality is not None  # for mypy - quality_available already proves this
        statuses = [entry.status for entry in quality.values()]
        input_variables_total = len(statuses)
        input_variables_valid = statuses.count("VALID")
        input_variables_suspect = statuses.count("SUSPECT")
        input_variables_rejected = input_variables_total - input_variables_valid - input_variables_suspect
    else:
        input_variables_total = 0
        input_variables_valid = 0
        input_variables_suspect = 0
        input_variables_rejected = 0

    if not quality_available:
        quality_bucket = "UNKNOWN"
    elif input_variables_total == 0:
        quality_bucket = "UNKNOWN"
    elif input_variables_rejected == 0:
        quality_bucket = "GOOD"
    elif input_variables_rejected / input_variables_total < _DEGRADED_MAX_REJECTED_FRACTION:
        quality_bucket = "DEGRADED"
    else:
        quality_bucket = "BAD"

    model_spread = result.model_spread
    model_spread_value = None
    model_spread_field = None
    if model_spread is not None:
        model_spread_value = model_spread.get("disagreement_spread")
        model_spread_field = model_spread.get("field")

    return AWCIExecutionReport(
        quality_available=quality_available,
        input_variables_total=input_variables_total,
        input_variables_valid=input_variables_valid,
        input_variables_suspect=input_variables_suspect,
        input_variables_rejected=input_variables_rejected,
        diagnostics_count=len(result.module_scores) + len(result.interaction_scores),
        awci_generated=True,
        quality=quality_bucket,
        model_spread_value=model_spread_value,
        model_spread_field=model_spread_field,
        model_spread_level=model_spread_level if model_spread_value is not None else None,
    )
