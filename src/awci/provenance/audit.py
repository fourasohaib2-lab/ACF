"""
Atmospheric Complexity Framework (ACF)

AWCI Provenance & Audit - Audit

Real, top-level entry point of this package - builds one
``AuditRecord`` combining the real lineage (``lineage.py``) with a real,
honest completeness assessment of the ``Provenance`` a result was built
with (``acf.core.contracts.provenance.Provenance.is_fully_specified()``,
already real and already tested - never a second, independently
invented completeness check). "Audit" here means exactly what
``docs/architecture/awci_reference_architecture.md`` section 22 asks
for: gathering the real, already-recorded trail into one inspectable
record - it never re-runs or re-validates the underlying AWCI
calculation itself (see ``reproducibility.py`` for the one real,
separate check that does compare two calculations).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from awci.provenance.lineage import LineageRecord, build_lineage

if TYPE_CHECKING:
    from awci.complexity.calculator import AWCICalculator
    from awci.complexity.result import AWCIResult

#: Real Provenance field names is_fully_specified() checks - mirrored
#: here (not re-derived) purely to report WHICH fields are still at
#: their honest "unknown" default, since Provenance.is_fully_specified()
#: itself only returns a single real bool, not the individual reasons.
_VERSION_FIELDS = (
    "algorithm_version",
    "science_version",
    "config_version",
    "run_identifier",
    "calibration_version",
    "dataset_version",
    "software_environment",
)


@dataclass(frozen=True)
class AuditRecord:
    """Real, complete audit record for one ``AWCIResult`` - the real
    lineage plus a real, honest disclosure of exactly which real
    provenance fields were never supplied."""

    lineage: LineageRecord
    is_fully_specified: bool
    missing_fields: tuple[str, ...]
    generated_at: datetime


def build_audit_record(result: "AWCIResult", calculator: "AWCICalculator | None" = None) -> AuditRecord:
    """
    Real audit record for ``result``. ``missing_fields`` lists exactly
    which of ``Provenance``'s own version-ish fields are still at their
    honest "unknown" default (or, honestly, every one of them, plus a
    single ``"provenance"`` entry, when ``result.provenance`` itself is
    ``None``) - never silently hidden, matching this whole package's
    "prefer a disclosed gap to a fabricated value" discipline.
    """
    lineage = build_lineage(result, calculator)
    provenance = result.provenance
    if provenance is None:
        missing_fields: tuple[str, ...] = ("provenance", *_VERSION_FIELDS)
        is_fully_specified = False
    else:
        missing_fields = tuple(field for field in _VERSION_FIELDS if getattr(provenance, field) == "unknown")
        is_fully_specified = provenance.is_fully_specified()
    return AuditRecord(
        lineage=lineage,
        is_fully_specified=is_fully_specified,
        missing_fields=missing_fields,
        generated_at=datetime.now(UTC),
    )


def format_audit_report(record: AuditRecord) -> str:
    """
    Real, human-readable audit report - one line per real lineage link
    (mirroring ``AWCIResult.trace_chain()``'s own real "not available"
    convention for a link that was never supplied), plus an explicit
    completeness disclosure naming every real missing field.
    """
    lineage = record.lineage
    lines = [
        f"Model: {lineage.model if lineage.model is not None else 'not available'}",
        f"Data source: {lineage.source.input_files if lineage.source is not None else 'not available'}",
        f"Dataset version: {lineage.source.dataset_version if lineage.source is not None else 'not available'}",
        f"Run identifier: {lineage.source.run_identifier if lineage.source is not None else 'not available'}",
        f"Code version: {lineage.version.algorithm_version if lineage.version is not None else 'not available'}",
        f"Config version: {lineage.version.config_version if lineage.version is not None else 'not available'}",
        f"Calibration version: {lineage.version.calibration_version if lineage.version is not None else 'not available'}",
        f"Dominant factors: {', '.join(lineage.dominant_factors) if lineage.dominant_factors else 'none above threshold'}",
        f"Lead time: {f'{lineage.lead_time_hours:.2f}h' if lineage.lead_time_hours is not None else 'not available'}",
        f"Vertical level: {lineage.vertical_level if lineage.vertical_level is not None else 'not available'}",
        f"Fully specified provenance: {record.is_fully_specified}",
        f"Missing fields: {', '.join(record.missing_fields) if record.missing_fields else 'none'}",
    ]
    return "\n".join(lines)
