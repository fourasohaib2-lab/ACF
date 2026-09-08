"""
ACF Scientific Workstation — real Pipeline Monitor checks
=============================================================

Real, honest per-stage checks for the Workstation's own "ACF Pipeline
Monitor" (Phase 32, 2026-09-05, matching the reference mockup's own
left-column pipeline status box - `docs/reference/
acf_scientific_workstation_reference.jpg` shows INGESTION/QC/
NORMALIZATION/MODULES/INTERACTIONS/ANALYSIS/VISUALIZATION, each with a
real [OK] tag).

Kept Qt-free and deliberately separate from
`acf_workstation_pipeline_monitor.ACFPipelineMonitorWidget` (the
display widget) so every check here is directly unit-testable against
a real `compute_real_complexity_volume()` output, with no GUI
dependency.

Honest scope - what each stage genuinely verifies
----------------------------------------------------
- QC (`run_real_range_qc`): the real min/max of every physical field
  this volume actually carries, checked against ACF's own documented
  `acf.physics_guard.range_check.OPERATIONAL_RANGES` via the same
  `check_range()` this codebase's other real QC paths already use -
  never a fabricated pass/fail.
- Normalization (`run_real_derivation_consistency_check`): a real
  self-consistency check on how `compute_real_complexity_volume()`
  itself derives `wind_speed_volume` (`sqrt(u_volume**2 +
  v_volume**2)`) and `pressure_volume_hpa` (a strictly-positive real
  Pa->hPa conversion) - catches a genuine regression in that
  derivation, never an independently-invented "normalization" concept.
The remaining stages (Ingestion/Modules/Interactions/Analysis/
Visualization) are reported directly by `ACFWorkstation` itself from
real, already-happening steps of its own pipeline (grid/model
validation, the real off-thread solver run, and each real panel's own
`update_from_volume()` call actually completing) - see
`acf_workstation.py`'s own `refresh()`/`_on_volume_ready()` for where.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from acf.core.exceptions import RangeError
from acf.physics_guard.range_check import check_range

#: (standard_name, volume dict key, unit override or None) for every
#: real physical field compute_real_complexity_volume() returns that
#: OPERATIONAL_RANGES has a documented bound for.
_QC_FIELDS: tuple[tuple[str, str, str | None], ...] = (
    ("air_temperature", "temperature_volume", None),
    ("wind_speed", "wind_speed_volume", None),
    ("specific_humidity", "specific_humidity_volume", None),
    ("air_pressure", "pressure_volume_hpa", "hPa"),
)


def run_real_range_qc(volume: dict[str, Any]) -> tuple[str, str]:
    """Real QC over a real volume's own physical fields.

    Returns
    -------
    (status, detail) : status is "OK" if every field's real min and
        max fall inside ACF's own documented operational range,
        "WARN" (with the real violation messages, never hidden)
        otherwise.
    """
    violations: list[str] = []
    for standard_name, key, unit in _QC_FIELDS:
        array = volume[key]
        for value in (float(np.min(array)), float(np.max(array))):
            try:
                check_range(value, standard_name, unit=unit)
            except RangeError as exc:
                violations.append(str(exc))
    if violations:
        return "WARN", f"{len(violations)} real range violation(s): " + " | ".join(violations[:3])
    return "OK", "Every real field's min/max is within ACF's documented operational ranges."


def run_real_derivation_consistency_check(volume: dict[str, Any]) -> tuple[str, str]:
    """Real self-consistency check on this volume's own real field
    derivations (see module docstring)."""
    u, v = volume["u_volume"], volume["v_volume"]
    recomputed_speed = np.sqrt(u**2 + v**2)
    speed_consistent = bool(np.allclose(recomputed_speed, volume["wind_speed_volume"], atol=1e-6))
    pressure_positive = bool(np.all(volume["pressure_volume_hpa"] > 0.0))
    if speed_consistent and pressure_positive:
        return "OK", "wind_speed_volume == sqrt(u_volume^2+v_volume^2) holds; pressure_volume_hpa is strictly positive."
    problems = []
    if not speed_consistent:
        problems.append("wind_speed_volume no longer matches sqrt(u_volume^2+v_volume^2)")
    if not pressure_positive:
        problems.append("pressure_volume_hpa contains a non-positive value")
    return "FAIL", "; ".join(problems)
