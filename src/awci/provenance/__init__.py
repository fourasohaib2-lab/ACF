"""
Atmospheric Complexity Framework (ACF)

AWCI Provenance & Audit (``src/awci/provenance/``)

Real implementation of the package specified in
``docs/architecture/awci_reference_architecture.md`` section 22:
"For every result, must be traceable: AWCI → Which model? → Which
data? → Which time? → Which variables? → Which formula? → Which
factors? → Which code version?" - previously identified as a
genuinely absent piece in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` (section
3, point 3, and its own table row: "Provenance discipline is a strong,
repeatedly-enforced convention throughout this codebase... but not a
dedicated provenance/lineage.py/audit.py module").

This package is a real ASSEMBLER, never a new computation - matching
the same discipline already established by
``awci.complexity.result.build_awci_result()`` (whose own module
docstring states this explicitly). Every field this package can return
is read directly from one of the following, already-real, already-
tested sources, never invented or recomputed here:

- ``acf.core.contracts.provenance.Provenance`` - the real, generic
  reproducibility-metadata contract already attached to
  ``AWCIResult.provenance``.
- ``awci.complexity.result.AWCIResult`` - already carries
  ``module_scores``/``interaction_scores``/``decomposition``/
  ``dominant_factors``/``raw_variables``/``lead_time_hours``/
  ``vertical_level`` and its own ``trace_chain()`` string rendering,
  which this package's ``lineage.py``/``audit.py`` provide a
  structured, programmatically usable counterpart to.
- ``awci.complexity.scientific_status`` - the real, already-existing
  per-weight/threshold evidentiary status registry (nothing here is
  ever CONFIRMED today - see that module's own docstring).
- ``awci.complexity.calibration.LockedModel`` - the real calibration-
  version/case-ID lineage, when a caller built one.

Deliberately NOT a persisted, append-only audit log/database - real,
disclosed scope limit: ``Provenance``/``AWCIResult`` are per-object
snapshots attached at construction time, and this package only ever
assembles a real, structured view of one such snapshot at a time
(``AuditRecord``). Building a real persisted audit trail across many
runs (a database, a file-based log) would be new, separate
infrastructure this phase does not build.
"""

from __future__ import annotations

from awci.provenance.audit import AuditRecord, build_audit_record, format_audit_report
from awci.provenance.calculation import CalculationStep, describe_calculation
from awci.provenance.lineage import LineageRecord, build_lineage
from awci.provenance.reproducibility import ReproducibilityCheck, is_reproducible_run, verify_reproducibility
from awci.provenance.source import DataSource, describe_source
from awci.provenance.version import VersionInfo, WeightVersionEntry, describe_version

__all__ = [
    "AuditRecord",
    "CalculationStep",
    "DataSource",
    "LineageRecord",
    "ReproducibilityCheck",
    "VersionInfo",
    "WeightVersionEntry",
    "build_audit_record",
    "build_lineage",
    "describe_calculation",
    "describe_source",
    "describe_version",
    "format_audit_report",
    "is_reproducible_run",
    "verify_reproducibility",
]
