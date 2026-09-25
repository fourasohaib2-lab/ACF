"""
Atmospheric Complexity Framework (ACF)

AWCI Provenance & Audit - Lineage

Real, structured assembly of the reference architecture's own full
traceability chain (section 22): "AWCI → Which model? → Which data? →
Which time? → Which variables? → Which formula? → Which factors? →
Which code version?" - the structured, programmatically usable
counterpart to ``AWCIResult.trace_chain()``'s already-real string
rendering, composed entirely from ``source.py``/``version.py``/
``calculation.py`` plus the real drill-down fields ``AWCIResult``
already carries (``dominant_factors``, ``lead_time_hours``,
``vertical_level``) - nothing new computed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from awci.provenance.calculation import CalculationStep, describe_calculation
from awci.provenance.source import DataSource, describe_source
from awci.provenance.version import VersionInfo, describe_version

if TYPE_CHECKING:
    from awci.complexity.calculator import AWCICalculator
    from awci.complexity.result import AWCIResult


@dataclass(frozen=True)
class LineageRecord:
    """Real, structured lineage for one ``AWCIResult`` - every field
    either copied directly from that result/its provenance, or honestly
    ``None`` when the real underlying value was never supplied (never
    a fabricated placeholder)."""

    source: DataSource | None
    version: VersionInfo | None
    calculation: tuple[CalculationStep, ...]
    dominant_factors: tuple[str, ...]
    model: str | None
    lead_time_hours: float | None
    vertical_level: int | None


def build_lineage(result: "AWCIResult", calculator: "AWCICalculator | None" = None) -> LineageRecord:
    """
    Real lineage record for ``result`` - ``source``/``version`` are
    ``None`` (never fabricated) when ``result.provenance`` itself is
    ``None``; ``calculation``/``dominant_factors``/``lead_time_hours``/
    ``vertical_level`` are read directly from ``result``'s own real
    fields, exactly matching what ``result.trace_chain()`` already
    renders as text.
    """
    provenance = result.provenance
    source = describe_source(provenance) if provenance is not None else None
    version = describe_version(provenance, calculator) if provenance is not None else None
    model = provenance.algorithm_version if provenance is not None else None
    return LineageRecord(
        source=source,
        version=version,
        calculation=describe_calculation(result),
        dominant_factors=tuple(result.dominant_factors),
        model=model,
        lead_time_hours=result.lead_time_hours,
        vertical_level=result.vertical_level,
    )
