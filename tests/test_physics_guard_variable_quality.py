"""
Tests for acf.physics_guard.variable_quality - real per-variable data
quality status (docs/ACF_MASTER_PROMPT.md section 32: "Chaque variable
doit avoir un statut : VALID, SUSPECT, MISSING, INVALID, OUT_OF_RANGE,
UNIT_ERROR, GRID_ERROR, TIME_ERROR, PHYSICAL_INCONSISTENCY"). This
session's conformance audit (reports/ACF_MASTER_AUDIT_v2.md) found this
vocabulary genuinely absent from the codebase before this module.
"""

from __future__ import annotations

import pytest

from acf.core.exceptions import (
    CoordinateError,
    DimensionError,
    RangeError,
    ScientificConsistencyError,
    TimeError,
    UnitError,
    VerticalError,
)
from acf.physics_guard import VariableQualityStatus, assess_variable_quality, classify_guard_exception
from acf.physics_guard.range_check import OPERATIONAL_RANGES


# ------------------------------------------------------- classify_guard_exception


def test_classify_guard_exception_maps_every_real_physics_error_type():
    assert classify_guard_exception(RangeError("x")) == "OUT_OF_RANGE"
    assert classify_guard_exception(UnitError("x")) == "UNIT_ERROR"
    assert classify_guard_exception(CoordinateError("x")) == "GRID_ERROR"
    assert classify_guard_exception(DimensionError("x")) == "GRID_ERROR"
    assert classify_guard_exception(VerticalError("x")) == "GRID_ERROR"
    assert classify_guard_exception(TimeError("x")) == "TIME_ERROR"
    assert classify_guard_exception(ScientificConsistencyError("x")) == "PHYSICAL_INCONSISTENCY"


def test_classify_guard_exception_raises_for_an_unmapped_exception_type():
    from acf.core.exceptions import ConfigurationError

    with pytest.raises(ValueError, match="No section-32 status mapping"):
        classify_guard_exception(ConfigurationError("x"))  # type: ignore[arg-type]


# ------------------------------------------------------- VariableQualityStatus


def test_variable_quality_status_rejects_a_vocabulary_outside_section_32():
    with pytest.raises(ValueError, match="status must be one of"):
        VariableQualityStatus("air_temperature", "FABRICATED_STATUS")


def test_variable_quality_status_accepts_every_real_section_32_value():
    from acf.physics_guard import VARIABLE_QUALITY_STATUSES

    for status in VARIABLE_QUALITY_STATUSES:
        VariableQualityStatus("air_temperature", status)  # must not raise


# ------------------------------------------------------- assess_variable_quality


def test_valid_value_within_the_real_operational_range():
    result = assess_variable_quality({"air_temperature": 288.0})
    assert result["air_temperature"].status == "VALID"


def test_out_of_range_value_matches_a_real_independent_check_range_call():
    from acf.physics_guard.range_check import check_range

    with pytest.raises(RangeError) as excinfo:
        check_range(500.0, "air_temperature")
    result = assess_variable_quality({"air_temperature": 500.0})
    assert result["air_temperature"].status == "OUT_OF_RANGE"
    assert result["air_temperature"].detail == str(excinfo.value)


def test_none_value_for_an_expected_variable_is_missing():
    result = assess_variable_quality({"air_temperature": None}, expected_variables=["air_temperature"])
    assert result["air_temperature"].status == "MISSING"


def test_absent_expected_variable_is_missing():
    result = assess_variable_quality({}, expected_variables=["air_temperature"])
    assert result["air_temperature"].status == "MISSING"


def test_absent_variable_not_in_expected_variables_is_never_silently_assumed():
    """Without an explicit expectation, a variable data never claims to
    have must not appear in the result at all - never guessed MISSING."""
    result = assess_variable_quality({"air_temperature": 288.0})
    assert "eastward_wind" not in result


def test_nan_value_is_invalid_not_out_of_range():
    result = assess_variable_quality({"air_temperature": float("nan")}, expected_variables=["air_temperature"])
    assert result["air_temperature"].status == "INVALID"


def test_infinite_value_is_invalid():
    result = assess_variable_quality({"air_temperature": float("inf")}, expected_variables=["air_temperature"])
    assert result["air_temperature"].status == "INVALID"


def test_non_numeric_value_is_invalid():
    result = assess_variable_quality({"air_temperature": "warm"}, expected_variables=["air_temperature"])
    assert result["air_temperature"].status == "INVALID"


def test_variable_with_no_documented_range_is_valid_but_only_presence_checked():
    result = assess_variable_quality({"not_a_real_cf_name": 42.0}, expected_variables=["not_a_real_cf_name"])
    assert result["not_a_real_cf_name"].status == "VALID"
    assert "no documented" in result["not_a_real_cf_name"].detail.lower()


def test_default_expected_variables_covers_every_operational_range_key_present():
    data = {name: (lo + hi) / 2.0 for name, (lo, hi) in OPERATIONAL_RANGES.items()}
    result = assess_variable_quality(data)
    assert set(result.keys()) == set(OPERATIONAL_RANGES.keys())
    assert all(s.status == "VALID" for s in result.values())


def test_dewpoint_above_temperature_is_physical_inconsistency_for_both_variables():
    result = assess_variable_quality(
        {"air_temperature": 280.0, "dewpoint_temperature": 285.0},
        expected_variables=["air_temperature"],
    )
    assert result["air_temperature"].status == "PHYSICAL_INCONSISTENCY"
    assert result["dewpoint_temperature"].status == "PHYSICAL_INCONSISTENCY"


def test_physical_inconsistency_overrides_an_otherwise_valid_range_status():
    result = assess_variable_quality({"air_temperature": 280.0, "dewpoint_temperature": 285.0})
    # 280K/285K both individually pass the real range check - only the
    # cross-variable relationship is violated.
    assert result["air_temperature"].status == "PHYSICAL_INCONSISTENCY"


def test_valid_dewpoint_relationship_does_not_override_a_real_out_of_range_temperature():
    result = assess_variable_quality(
        {"air_temperature": 500.0, "dewpoint_temperature": 280.0}, expected_variables=["air_temperature"]
    )
    assert result["air_temperature"].status == "OUT_OF_RANGE"


def test_dewpoint_check_runs_even_when_not_in_expected_variables():
    """Real relational evidence between two present variables is never
    suppressed just because the caller's expectation list didn't name
    both of them."""
    result = assess_variable_quality(
        {"air_temperature": 280.0, "dewpoint_temperature": 285.0, "eastward_wind": 5.0},
        expected_variables=["eastward_wind"],
    )
    assert result["air_temperature"].status == "PHYSICAL_INCONSISTENCY"
    assert result["dewpoint_temperature"].status == "PHYSICAL_INCONSISTENCY"
    assert result["eastward_wind"].status == "VALID"


def test_missing_dewpoint_partner_means_no_consistency_check_runs():
    result = assess_variable_quality({"air_temperature": 280.0})
    assert "dewpoint_temperature" not in result
    assert result["air_temperature"].status == "VALID"


# ------------------------------------------------------- units (real conversion)


def test_units_parameter_converts_before_the_range_check():
    """15 degC is comfortably within the real air_temperature range in
    Kelvin (288.15K) - omitting the real unit would silently compare
    the raw 15 against the Kelvin bound and wrongly flag it."""
    result = assess_variable_quality(
        {"air_temperature": 15.0}, expected_variables=["air_temperature"], units={"air_temperature": "degC"}
    )
    assert result["air_temperature"].status == "VALID"


def test_units_parameter_still_catches_a_real_out_of_range_value():
    # 200 degC is a real, genuine out-of-range surface air temperature.
    result = assess_variable_quality(
        {"air_temperature": 200.0}, expected_variables=["air_temperature"], units={"air_temperature": "degC"}
    )
    assert result["air_temperature"].status == "OUT_OF_RANGE"


def test_units_parameter_default_none_is_bit_identical_to_before():
    without_units = assess_variable_quality({"air_temperature": 288.0}, expected_variables=["air_temperature"])
    with_units_none = assess_variable_quality({"air_temperature": 288.0}, expected_variables=["air_temperature"], units=None)
    assert without_units == with_units_none


def test_units_parameter_a_variable_without_a_units_entry_is_assumed_native_cf_unit():
    result = assess_variable_quality(
        {"air_temperature": 288.0, "eastward_wind": 10.0},
        expected_variables=["air_temperature", "eastward_wind"],
        units={"air_temperature": "degC"},
    )
    # eastward_wind has no units entry - assumed already m/s (its real
    # CF canonical unit), 10.0 m/s is real and valid.
    assert result["eastward_wind"].status == "VALID"


def test_units_parameter_converts_the_dewpoint_consistency_check_too():
    """15 degC / 20 degC in Celsius is the same real physical
    inconsistency as 288.15K / 293.15K - the consistency check must
    apply the real unit conversion, not compare raw Celsius against an
    implicit Kelvin assumption (they'd disagree by the same margin
    either way here, but the real conversion is what makes the check
    correct in general, not a coincidence of this example)."""
    result = assess_variable_quality(
        {"air_temperature": 15.0, "dewpoint_temperature": 20.0},
        units={"air_temperature": "degC", "dewpoint_temperature": "degC"},
    )
    assert result["air_temperature"].status == "PHYSICAL_INCONSISTENCY"
    assert result["dewpoint_temperature"].status == "PHYSICAL_INCONSISTENCY"


def test_new_wind_speed_and_dewpoint_temperature_range_entries_are_real_and_documented():
    from acf.physics_guard.range_check import OPERATIONAL_RANGES

    assert OPERATIONAL_RANGES["wind_speed"] == (0.0, 150.0)
    assert OPERATIONAL_RANGES["dewpoint_temperature"] == (173.15, 333.15)


def test_wind_speed_out_of_range_is_caught():
    result = assess_variable_quality({"wind_speed": 200.0}, expected_variables=["wind_speed"])
    assert result["wind_speed"].status == "OUT_OF_RANGE"


def test_wind_speed_negative_is_out_of_range_unlike_the_signed_vector_components():
    result = assess_variable_quality({"wind_speed": -5.0}, expected_variables=["wind_speed"])
    assert result["wind_speed"].status == "OUT_OF_RANGE"
