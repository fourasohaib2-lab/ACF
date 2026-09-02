"""
PhysicsGuard: orchestrates the individual real checks into one pass.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from acf.core.exceptions import (
    CoordinateError,
    RangeError,
    ScientificConsistencyError,
    TimeError,
    UnitError,
    VerticalError,
)
from acf.physics_guard.consistency_check import check_dewpoint_not_above_temperature, check_relative_humidity_bounds
from acf.physics_guard.coordinate_check import check_coordinate_arrays, check_coordinates
from acf.physics_guard.range_check import OPERATIONAL_RANGES, check_range, check_ranges
from acf.physics_guard.time_check import check_forecast_time_ordering
from acf.physics_guard.unit_check import check_unit
from acf.physics_guard.vertical_check import check_pressure_decreases_with_altitude


@dataclass
class PhysicsGuardReport:
    """Result of PhysicsGuard.validate() - every violation found, not just the first."""

    passed: bool
    violations: list[str] = field(default_factory=list)
    checks_run: list[str] = field(default_factory=list)


class PhysicsGuard:
    """
    Real transversal validation pipeline (see package docstring for the
    full disclosure on scope and what motivated each check).

    Two ways to use it:
    - Fail-fast, one check at a time: PhysicsGuard().check_range(...),
      .check_coordinates(...), etc. - each raises immediately (real
      exceptions from acf.core.exceptions), for a caller that wants to
      stop at the first problem.
    - Aggregate: PhysicsGuard().validate(data) - runs whichever checks
      apply to the keys present in `data`, collecting every violation
      into a PhysicsGuardReport instead of stopping at the first one.
    """

    # ------------------------------------------------------------ fail-fast

    def check_unit(self, value: float, unit: str, expected_unit: str) -> float:
        return check_unit(value, unit, expected_unit)

    def check_range(self, value: float, standard_name: str, unit: str | None = None) -> None:
        check_range(value, standard_name, unit)

    def check_coordinates(self, lat: float, lon: float) -> None:
        check_coordinates(lat, lon)

    def check_coordinate_arrays(self, lats: list[float], lons: list[float]) -> None:
        """See acf.physics_guard.coordinate_check.check_coordinate_arrays() - directly motivated by the real swapped-lons-lats bug found this session."""
        check_coordinate_arrays(lats, lons)

    def check_vertical(self, pressure_by_level: list[float]) -> None:
        check_pressure_decreases_with_altitude(pressure_by_level)

    def check_time(
        self, forecast_reference_time: datetime, valid_time: datetime, max_lead_time: timedelta | None = None
    ) -> None:
        check_forecast_time_ordering(forecast_reference_time, valid_time, max_lead_time)

    def check_consistency(self, data: dict[str, Any]) -> None:
        """Fail-fast scientific-consistency check - raises on the first violation found. See validate() to collect all of them instead."""
        if "air_temperature" in data and "dewpoint_temperature" in data:
            check_dewpoint_not_above_temperature(data["air_temperature"], data["dewpoint_temperature"])
        if "relative_humidity" in data:
            check_relative_humidity_bounds(data["relative_humidity"])

    # ------------------------------------------------------------- aggregate

    def validate(self, data: dict[str, Any]) -> PhysicsGuardReport:
        """
        Run whichever checks apply to the keys present in `data`,
        collecting every violation found instead of stopping at the
        first one.

        Recognized keys (all optional - only checks whose required
        keys are present actually run):
        - Any acf.physics_guard.range_check.OPERATIONAL_RANGES key
          (e.g. "air_temperature", "relative_humidity") -> range check,
          value assumed to already be in that variable's native CF unit.
        - "lat", "lon" -> coordinate check.
        - "pressure_by_level" -> vertical monotonicity check.
        - "forecast_reference_time", "valid_time" -> time ordering check.
        - "air_temperature" + "dewpoint_temperature" -> dew point <= temperature check.
        - "relative_humidity" -> relative humidity bounds check.

        Returns
        -------
        PhysicsGuardReport
            passed=True only if every applicable check found zero
            violations. checks_run lists which checks actually ran
            (for a caller/test to confirm the intended checks fired,
            not just that the report happened to pass).
        """
        violations: list[str] = []
        checks_run: list[str] = []

        range_inputs = {k: v for k, v in data.items() if k in OPERATIONAL_RANGES}
        if range_inputs:
            checks_run.append("range")
            violations.extend(check_ranges(range_inputs))

        if "lat" in data and "lon" in data:
            checks_run.append("coordinate")
            try:
                check_coordinates(data["lat"], data["lon"])
            except CoordinateError as exc:
                violations.append(str(exc))

        if "pressure_by_level" in data:
            checks_run.append("vertical")
            try:
                check_pressure_decreases_with_altitude(data["pressure_by_level"])
            except VerticalError as exc:
                violations.append(str(exc))

        if "forecast_reference_time" in data and "valid_time" in data:
            checks_run.append("time")
            try:
                check_forecast_time_ordering(data["forecast_reference_time"], data["valid_time"])
            except TimeError as exc:
                violations.append(str(exc))

        if "air_temperature" in data and "dewpoint_temperature" in data:
            checks_run.append("consistency:dewpoint")
            try:
                check_dewpoint_not_above_temperature(data["air_temperature"], data["dewpoint_temperature"])
            except ScientificConsistencyError as exc:
                violations.append(str(exc))

        if "relative_humidity" in data:
            checks_run.append("consistency:relative_humidity")
            try:
                check_relative_humidity_bounds(data["relative_humidity"])
            except ScientificConsistencyError as exc:
                violations.append(str(exc))

        return PhysicsGuardReport(passed=(len(violations) == 0), violations=violations, checks_run=checks_run)


__all__ = [
    "PhysicsGuard",
    "PhysicsGuardReport",
    "UnitError",
    "RangeError",
    "CoordinateError",
    "VerticalError",
    "TimeError",
    "ScientificConsistencyError",
]
