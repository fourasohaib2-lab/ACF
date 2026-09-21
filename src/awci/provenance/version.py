"""
Atmospheric Complexity Framework (ACF)

AWCI Provenance & Audit - Version

Real, thin view over an already-built ``Provenance``'s own version
fields, optionally enriched with the real, already-existing per-weight
evidentiary status registry (``awci.complexity.scientific_status`` -
"nothing here is CONFIRMED... this registry exists to make that
visible", see that module's own docstring) when a real
``AWCICalculator`` is supplied - "Which formula? → Which code version?"
in the reference architecture's own traceability chain (section 22).
Never invents a version string or a status this codebase does not
already record.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from acf.core.contracts.provenance import Provenance
from awci.complexity.scientific_status import WeightStatus, get_interaction_weight_status

if TYPE_CHECKING:
    from awci.complexity.calculator import AWCICalculator


@dataclass(frozen=True)
class WeightVersionEntry:
    """Real status of one module/interaction weight - key plus the
    real, already-assigned status/rationale from
    ``awci.complexity.scientific_status``."""

    key: str
    status: WeightStatus
    rationale: str


@dataclass(frozen=True)
class VersionInfo:
    """Real "which code version" view - the exact real values already
    recorded on the ``Provenance`` this was built from, plus (when a
    real ``AWCICalculator`` was supplied) the real, per-weight
    evidentiary status of every weight that calculator actually uses
    today."""

    algorithm_version: str
    science_version: str
    config_version: str
    calibration_version: str
    software_environment: str
    module_weight_statuses: tuple[WeightVersionEntry, ...]
    interaction_weight_statuses: tuple[WeightVersionEntry, ...]

    @property
    def has_calibrated_or_validated_weight(self) -> bool:
        """True only if at least one real weight has genuinely reached
        CALIBRATED/VALIDATED status - honestly False today for every
        weight this codebase ships (see scientific_status.py's own
        docstring: "No status here is CONFIRMED... nothing... has gone
        through the master prompt's own calibration/validation
        pipeline yet"), not fabricated as True."""
        return any(
            entry.status in (WeightStatus.CALIBRATED, WeightStatus.VALIDATED)
            for entry in (*self.module_weight_statuses, *self.interaction_weight_statuses)
        )


def describe_version(provenance: Provenance, calculator: "AWCICalculator | None" = None) -> VersionInfo:
    """
    Real version info - the exact real fields already on
    ``provenance``, plus, when ``calculator`` is supplied, the real
    per-weight status of exactly the weights that real calculator
    instance uses (via ``WeightsManager.get_weight_status()`` for
    module weights - already the real, established wrapper around
    ``scientific_status.get_module_weight_status()`` - and
    ``scientific_status.get_interaction_weight_status()`` directly for
    interaction weights, which have no calculator-level wrapper today).
    Empty tuples (never fabricated entries) when no calculator is
    supplied.
    """
    module_statuses: tuple[WeightVersionEntry, ...] = ()
    interaction_statuses: tuple[WeightVersionEntry, ...] = ()
    if calculator is not None:
        module_statuses = tuple(
            WeightVersionEntry(key=key, status=entry.status, rationale=entry.rationale)
            for key, entry in (
                (key, calculator.weights_manager.get_weight_status(key))
                for key in sorted(calculator.weights_manager.weights)
            )
        )
        interaction_statuses = tuple(
            WeightVersionEntry(key=key, status=entry.status, rationale=entry.rationale)
            for key, entry in (
                (key, get_interaction_weight_status(key)) for key in sorted(calculator.interaction_weights)
            )
        )
    return VersionInfo(
        algorithm_version=provenance.algorithm_version,
        science_version=provenance.science_version,
        config_version=provenance.config_version,
        calibration_version=provenance.calibration_version,
        software_environment=provenance.software_environment,
        module_weight_statuses=module_statuses,
        interaction_weight_statuses=interaction_statuses,
    )
