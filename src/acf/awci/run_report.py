"""
AWCI Run Report (§75)
========================

docs/ACF_MASTER_PROMPT.md section 75:

    "Le pipeline doit produire : logs, metrics, warnings, errors,
    quality reports, runtime statistics.

    Exemple :
    Input files: 48
    Valid: 46
    Rejected: 2
    Diagnostics: 123
    AWCI generated: YES
    Quality: GOOD
    Model spread: HIGH"

Found during this session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md): `acf.monitoring` is real and large
(realtime_monitor/telemetry_engine/anomaly_monitor/alert_dispatcher)
but generic - nothing produces this specific real per-run summary tied
to one real AWCI computation.

Honest scope
-------------
`build_run_report()` is a real ASSEMBLER, not a new computation - same
discipline as `acf.awci.result.build_awci_result()` (section 81): it
never invents input_files_count/valid_count/rejected_count/
diagnostics_count from nothing - the caller supplies real counts (or
real lists, when supplying a count directly is inconvenient) from its
own real run.

`quality_status` is real but deliberately BINARY (PASS/FAIL), not the
3-tier PASS/WARNING/FAIL section 75's own "GOOD" example might suggest
- introducing a WARNING tier would require a real percentage-of-
failures threshold this project has no scientific basis for (the same
kind of invented cutoff sections 78-79 warn against). PASS only when
every real supplied acf.physics_guard.variable_quality.
VariableQualityStatus is VALID; FAIL if at least one real entry is not
VALID; the real, honest acf.core.contracts.quality.QualityInfo
vocabulary is reused directly (NOT_ASSESSED/PASS/WARNING/FAIL - WARNING
kept in the vocabulary for a future real caller who has a genuine basis
to use it, just never produced by this function itself) rather than
inventing "GOOD" as a new, separate word.

`model_spread` is kept as the real numeric value (e.g. a real
ModelConsensusEngine.compute_real_multi_model_disagreement()'s own
`disagreement_spread`), not binned into LOW/MODERATE/HIGH - those
categories would need real percentile/threshold boundaries this
project does not have (same reasoning as quality_status above).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from acf.physics_guard.variable_quality import VariableQualityStatus


@dataclass(frozen=True)
class AWCIRunReport:
    """Real, structured per-run summary (docs/ACF_MASTER_PROMPT.md
    section 75's own worked example format) - built by
    `build_run_report()` below, never constructed by hand."""

    input_files_count: int
    valid_count: int
    rejected_count: int
    diagnostics_count: int
    awci_generated: bool
    #: One of acf.core.contracts.quality.QualityInfo's own real
    #: vocabulary (NOT_ASSESSED/PASS/FAIL here - WARNING never produced
    #: by build_run_report(), see module docstring).
    quality_status: str
    #: Real numeric multi-model/ensemble disagreement spread, in its
    #: native units - None when no real spread was computed for this
    #: run. Deliberately not binned into LOW/MODERATE/HIGH (see module
    #: docstring).
    model_spread: float | None = None

    def format_text(self) -> str:
        """Real text rendering matching section 75's own example format."""
        lines = [
            f"Input files: {self.input_files_count}",
            f"Valid: {self.valid_count}",
            f"Rejected: {self.rejected_count}",
            f"Diagnostics: {self.diagnostics_count}",
            f"AWCI generated: {'YES' if self.awci_generated else 'NO'}",
            f"Quality: {self.quality_status}",
        ]
        if self.model_spread is not None:
            lines.append(f"Model spread: {self.model_spread}")
        return "\n".join(lines)


def build_run_report(
    *,
    input_files_count: int = 0,
    valid_count: int = 0,
    rejected_count: int = 0,
    diagnostics_count: int = 0,
    awci_generated: bool = False,
    quality_results: dict[str, VariableQualityStatus] | None = None,
    model_spread: float | None = None,
) -> AWCIRunReport:
    """
    Real assembler for one AWCIRunReport (docs/ACF_MASTER_PROMPT.md
    section 75).

    Parameters
    ----------
    input_files_count, valid_count, rejected_count, diagnostics_count : int
        Real counts from the caller's own real run - never computed or
        guessed here.
    awci_generated : bool
        Whether a real AWCI score was actually produced for this run.
    quality_results : dict[str, VariableQualityStatus], optional
        Real per-variable quality results (e.g. from
        acf.physics_guard.variable_quality.assess_variable_quality())
        for this run - used to derive `quality_status`:
        - None or empty -> "NOT_ASSESSED" (no real assessment ran).
        - every real entry VALID -> "PASS".
        - at least one real entry not VALID -> "FAIL".
    model_spread : float, optional
        A real numeric disagreement/ensemble spread value for this run
        - kept as-is (see AWCIRunReport's own field docstring for why
        this is never binned into a category).

    Returns
    -------
    AWCIRunReport
    """
    if not quality_results:
        quality_status = "NOT_ASSESSED"
    elif all(status.status == "VALID" for status in quality_results.values()):
        quality_status = "PASS"
    else:
        quality_status = "FAIL"

    return AWCIRunReport(
        input_files_count=input_files_count,
        valid_count=valid_count,
        rejected_count=rejected_count,
        diagnostics_count=diagnostics_count,
        awci_generated=awci_generated,
        quality_status=quality_status,
        model_spread=model_spread,
    )
