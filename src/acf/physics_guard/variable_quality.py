"""
Per-variable data quality status (docs/ACF_MASTER_PROMPT.md section 32)
==========================================================================

Section 32: "Chaque variable doit avoir un statut : VALID, SUSPECT,
MISSING, INVALID, OUT_OF_RANGE, UNIT_ERROR, GRID_ERROR, TIME_ERROR,
PHYSICAL_INCONSISTENCY. Le moteur ne doit pas silencieusement continuer
avec des données douteuses." This session's first conformance audit
(reports/ACF_MASTER_AUDIT_v2.md) found this a real gap: this
codebase's existing `acf.core.contracts.quality.QualityInfo` is real
and honest (defaults to NOT_ASSESSED, never PASS) but is a single
DATASET-level summary status (NOT_ASSESSED/PASS/WARNING/FAIL) - not the
distinct, more granular per-VARIABLE failure-mode taxonomy section 32
asks for. This module is additive, not a replacement: QualityInfo is
untouched.

Reuses real, already-built acf.physics_guard infrastructure rather
than reimplementing validation logic: acf.physics_guard.range_check.
OPERATIONAL_RANGES/check_range() for OUT_OF_RANGE, and acf.
physics_guard.consistency_check.check_dewpoint_not_above_temperature()
for PHYSICAL_INCONSISTENCY. classify_guard_exception() maps every real
acf.core.exceptions.PhysicsError subclass PhysicsGuard can raise
(UnitError/RangeError/CoordinateError/DimensionError/VerticalError/
TimeError/ScientificConsistencyError) onto section 32's exact
vocabulary, so any caller already wrapping a PhysicsGuard check in
try/except can get a real section-32 status instead of just letting
the exception propagate.

Honest scope - what this does NOT do
--------------------------------------
- SUSPECT is never produced. No real "plausible but doubtful" heuristic
  exists anywhere in this codebase (that would need a real statistical
  or climatological basis - e.g. an unusual-but-not-impossible z-score
  against real climatology - which does not exist yet); fabricating a
  threshold here would be exactly the kind of ungrounded rule the
  master prompt's own section 78 warns against. It stays in
  VARIABLE_QUALITY_STATUSES because it is real, valid section-32
  vocabulary a caller may assign directly - just never produced by the
  functions in this module.
- GRID_ERROR/TIME_ERROR are only ever produced when the caller runs
  the corresponding real PhysicsGuard check
  (check_coordinates()/check_coordinate_arrays()/check_vertical()/
  check_time()) and passes the resulting exception to
  classify_guard_exception() - assess_variable_quality() below only
  covers the two checks that are genuinely PER-VARIABLE in a
  meaningful sense (range, and the dew point/temperature relationship)
  today; grid/time errors are properties of a whole field/axis, not
  one named physical variable, so wiring them into this function's
  automatic loop would force an artificial choice of which variable to
  blame.
- acf.physics_guard.consistency_check.check_relative_humidity_bounds()
  (0-110%, a real supersaturation margin) is deliberately NOT
  additionally applied here: OPERATIONAL_RANGES already has its own,
  stricter (0-100%) bound for "relative_humidity" via the range check
  below, and running both would produce two different verdicts for the
  same 100-110% band depending on check order - a real ambiguity this
  module resolves by relying on the range check alone for this
  variable, not by silently picking a winner.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from math import isfinite
from typing import Any

from acf.core.exceptions import (
    CoordinateError,
    DimensionError,
    PhysicsError,
    RangeError,
    ScientificConsistencyError,
    TimeError,
    UnitError,
    VerticalError,
)
from acf.physics_guard.consistency_check import check_dewpoint_not_above_temperature
from acf.physics_guard.range_check import OPERATIONAL_RANGES, check_range

#: Exact vocabulary from docs/ACF_MASTER_PROMPT.md section 32 - not
#: reordered, not renamed, not extended.
VARIABLE_QUALITY_STATUSES = (
    "VALID",
    "SUSPECT",
    "MISSING",
    "INVALID",
    "OUT_OF_RANGE",
    "UNIT_ERROR",
    "GRID_ERROR",
    "TIME_ERROR",
    "PHYSICAL_INCONSISTENCY",
)

# Real mapping from each of PhysicsGuard's own exception classes to
# section 32's vocabulary - every entry justified by what the
# exception actually means, never guessed. DimensionError and
# VerticalError both map to GRID_ERROR: DimensionError is literally a
# grid/shape mismatch, and VerticalError (pressure not decreasing with
# altitude) is a violation of the vertical grid's own required
# ordering - the closest section-32 category for either is GRID_ERROR,
# there being no separate "VERTICAL_ERROR" in the prompt's list.
_EXCEPTION_STATUS_MAP: dict[type[PhysicsError], str] = {
    RangeError: "OUT_OF_RANGE",
    UnitError: "UNIT_ERROR",
    CoordinateError: "GRID_ERROR",
    DimensionError: "GRID_ERROR",
    VerticalError: "GRID_ERROR",
    TimeError: "TIME_ERROR",
    ScientificConsistencyError: "PHYSICAL_INCONSISTENCY",
}


@dataclass
class VariableQualityStatus:
    """Real per-variable quality outcome (docs/ACF_MASTER_PROMPT.md section 32)."""

    variable: str
    status: str
    detail: str = ""

    def __post_init__(self) -> None:
        if self.status not in VARIABLE_QUALITY_STATUSES:
            raise ValueError(f"status must be one of {VARIABLE_QUALITY_STATUSES}, got {self.status!r}")


def classify_guard_exception(exc: PhysicsError) -> str:
    """
    Real mapping from one of PhysicsGuard's own exception classes to
    docs/ACF_MASTER_PROMPT.md section 32's exact per-variable status
    vocabulary - see this module's own docstring for each mapping's
    justification.

    Raises
    ------
    ValueError
        If `exc` is not an instance of any mapped exception type - a
        new PhysicsError subclass added later needs a real, deliberate
        entry added to _EXCEPTION_STATUS_MAP, never a silent guess here.
    """
    for exc_type, status in _EXCEPTION_STATUS_MAP.items():
        if isinstance(exc, exc_type):
            return status
    raise ValueError(f"No section-32 status mapping for {type(exc).__name__} - add one to _EXCEPTION_STATUS_MAP with a real justification.")


def _finite_number_or_none(value: Any) -> float | None:
    """Real, honest number check: None/non-numeric/NaN/Inf all return
    None (caller decides MISSING vs. INVALID from context - see
    assess_variable_quality())."""
    if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = float(value)
    return value if isfinite(value) else None


def assess_variable_quality(
    data: dict[str, Any], expected_variables: Iterable[str] | None = None
) -> dict[str, VariableQualityStatus]:
    """
    Real per-variable quality status for a data dict keyed by real CF
    standard_name (the same names acf.physics_guard.range_check.
    OPERATIONAL_RANGES/acf.physics_guard.consistency_check use, e.g.
    "air_temperature", "eastward_wind", "relative_humidity" - NOT
    AWCICalculator's simplified variable names like "wind_speed").

    Parameters
    ----------
    data : dict
        Real values to assess, keyed by CF standard_name.
    expected_variables : iterable of str, optional
        The variables this caller actually expects `data` to carry -
        any of these absent from `data` (or present as None) is real
        MISSING evidence, not silently skipped. Defaults to whichever
        OPERATIONAL_RANGES-covered variables are actually present in
        `data` - i.e. without an explicit expectation, a variable
        `data` never claims to have is never marked MISSING (this
        module never guesses what a caller expected).

    Returns
    -------
    dict[str, VariableQualityStatus]
        One entry per variable in `expected_variables` (or, when that
        is omitted, per OPERATIONAL_RANGES-covered variable actually
        present in `data`), plus - always, regardless of
        `expected_variables` - real PHYSICAL_INCONSISTENCY entries for
        "air_temperature"/"dewpoint_temperature" when both are present
        as real finite numbers and violate
        check_dewpoint_not_above_temperature() (this overrides
        whatever range-check status either variable already got - a
        real relational violation between two variables is real
        additional evidence, not suppressed by an `expected_variables`
        filter that didn't happen to name both of them).
    """
    variables = list(expected_variables) if expected_variables is not None else [v for v in OPERATIONAL_RANGES if v in data]

    statuses: dict[str, VariableQualityStatus] = {}
    for variable in variables:
        if variable not in data:
            statuses[variable] = VariableQualityStatus(variable, "MISSING", "Variable absent from data.")
            continue

        numeric_value = _finite_number_or_none(data[variable])
        if numeric_value is None:
            if data[variable] is None:
                statuses[variable] = VariableQualityStatus(variable, "MISSING", "Value is None.")
            else:
                statuses[variable] = VariableQualityStatus(
                    variable, "INVALID", f"Non-finite or non-numeric value: {data[variable]!r}."
                )
            continue

        if variable not in OPERATIONAL_RANGES:
            statuses[variable] = VariableQualityStatus(
                variable, "VALID", "No documented OPERATIONAL_RANGES bound for this variable - presence/finiteness verified only, physical plausibility not checked."
            )
            continue

        try:
            check_range(numeric_value, variable)
        except RangeError as exc:
            statuses[variable] = VariableQualityStatus(variable, classify_guard_exception(exc), str(exc))
        else:
            statuses[variable] = VariableQualityStatus(variable, "VALID", "")

    temperature = _finite_number_or_none(data.get("air_temperature"))
    dewpoint = _finite_number_or_none(data.get("dewpoint_temperature"))
    if temperature is not None and dewpoint is not None:
        try:
            check_dewpoint_not_above_temperature(temperature, dewpoint)
        except ScientificConsistencyError as exc:
            detail = str(exc)
            statuses["air_temperature"] = VariableQualityStatus("air_temperature", "PHYSICAL_INCONSISTENCY", detail)
            statuses["dewpoint_temperature"] = VariableQualityStatus("dewpoint_temperature", "PHYSICAL_INCONSISTENCY", detail)

    return statuses
