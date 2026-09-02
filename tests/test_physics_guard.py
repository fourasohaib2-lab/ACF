"""
Tests for acf.physics_guard - the transversal validation infrastructure
requested by the user's "Prompt Maître ACF v2.0" (reports/
ACF_MASTER_AUDIT_v2.md found this genuinely absent before this work).
"""

from datetime import datetime, timedelta

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
from acf.physics_guard import PhysicsGuard
from acf.physics_guard.dimension_check import check_field_shape


# --------------------------------------------------------------- unit_check


def test_check_unit_real_conversion():
    guard = PhysicsGuard()
    assert guard.check_unit(15.0, "degC", "K") == pytest.approx(288.15, abs=1e-2)


def test_check_unit_raises_on_dimensional_mismatch():
    guard = PhysicsGuard()
    with pytest.raises(UnitError):
        guard.check_unit(1.0, "K", "m s-1")


# -------------------------------------------------------------- range_check


def test_check_range_accepts_normal_value():
    guard = PhysicsGuard()
    guard.check_range(288.15, "air_temperature")  # does not raise


def test_check_range_rejects_absurd_value():
    """A Celsius value (15.0) mistaken for Kelvin would be far outside the real operational range - exactly the unit-mixup bug class this exists to catch."""
    guard = PhysicsGuard()
    with pytest.raises(RangeError):
        guard.check_range(15.0, "air_temperature")


def test_check_range_converts_unit_before_checking():
    guard = PhysicsGuard()
    guard.check_range(15.0, "air_temperature", unit="degC")  # 288.15 K - within range, does not raise


def test_check_range_unknown_variable_raises_value_error_not_guess():
    guard = PhysicsGuard()
    with pytest.raises(ValueError, match="No documented operational range"):
        guard.check_range(1.0, "totally_made_up_variable")


# --------------------------------------------------------- coordinate_check


def test_check_coordinates_accepts_valid_pair():
    guard = PhysicsGuard()
    guard.check_coordinates(36.7, 3.0)  # Algiers - does not raise


def test_check_coordinates_catches_the_real_swapped_lat_lon_bug():
    """
    Directly reproduces the failure mode of the real swapped lons/lats
    bug found this session in gui/dashboard/awci_dashboard.py: a real
    longitude value (154.28) passed where a latitude was expected.
    """
    guard = PhysicsGuard()
    with pytest.raises(CoordinateError, match="Latitude"):
        guard.check_coordinates(154.28571429, 3.0)


def test_check_coordinates_rejects_out_of_range_longitude():
    guard = PhysicsGuard()
    with pytest.raises(CoordinateError, match="Longitude"):
        guard.check_coordinates(10.0, 200.0)


# ------------------------------------------------------------ vertical_check


def test_check_vertical_accepts_real_solver_pressure_profile():
    """The exact real pressure-by-level values measured against CoupledEarthSolver output earlier this session (surface -> top of atmosphere)."""
    guard = PhysicsGuard()
    real_pressure_by_level = [
        2013.2, 1907.3, 1801.4, 1695.5, 1589.6, 1483.7, 1377.8, 1271.9, 1166.0, 1060.1,
        954.2, 848.3, 742.4, 636.4, 530.5, 424.6, 318.7, 212.8, 106.9, 1.0,
    ]
    guard.check_vertical(real_pressure_by_level)  # does not raise


def test_check_vertical_rejects_non_monotonic_profile():
    guard = PhysicsGuard()
    with pytest.raises(VerticalError):
        guard.check_vertical([1000.0, 900.0, 950.0, 800.0])  # level 2 > level 1 - violates real physics


def test_check_vertical_rejects_reversed_profile():
    """A profile accidentally given top-of-atmosphere-first instead of surface-first must be caught, not silently accepted."""
    guard = PhysicsGuard()
    with pytest.raises(VerticalError):
        guard.check_vertical([100.0, 500.0, 1000.0])  # increasing, not decreasing


def test_check_vertical_single_level_is_trivially_valid():
    guard = PhysicsGuard()
    guard.check_vertical([1000.0])  # nothing to compare - does not raise


# ---------------------------------------------------------------- time_check


def test_check_time_accepts_valid_ordering():
    guard = PhysicsGuard()
    run = datetime(2026, 9, 2, 0, 0)
    valid = datetime(2026, 9, 2, 6, 0)
    guard.check_time(run, valid)  # does not raise


def test_check_time_rejects_valid_time_before_run():
    guard = PhysicsGuard()
    run = datetime(2026, 9, 2, 6, 0)
    valid = datetime(2026, 9, 2, 0, 0)  # before the run - impossible
    with pytest.raises(TimeError):
        guard.check_time(run, valid)


def test_check_time_rejects_lead_time_beyond_max():
    guard = PhysicsGuard()
    run = datetime(2026, 9, 2, 0, 0)
    valid = datetime(2027, 9, 2, 0, 0)  # a year later - plausible unit mixup
    with pytest.raises(TimeError):
        guard.check_time(run, valid, max_lead_time=timedelta(days=10))


# ---------------------------------------------------------- consistency_check


def test_check_consistency_accepts_saturated_air():
    guard = PhysicsGuard()
    guard.check_consistency({"air_temperature": 288.15, "dewpoint_temperature": 288.15})  # does not raise


def test_check_consistency_rejects_dewpoint_above_temperature():
    guard = PhysicsGuard()
    with pytest.raises(ScientificConsistencyError):
        guard.check_consistency({"air_temperature": 280.0, "dewpoint_temperature": 285.0})


def test_check_consistency_rejects_negative_relative_humidity():
    guard = PhysicsGuard()
    with pytest.raises(ScientificConsistencyError):
        guard.check_consistency({"relative_humidity": -5.0})


# -------------------------------------------------------------- dimension_check


def test_check_field_shape_accepts_matching_2d_field():
    import numpy as np

    check_field_shape(np.zeros((3, 2)), lats=[0, 1, 2], lons=[0, 1])  # 3x2 - does not raise


def test_check_field_shape_rejects_mismatched_lats():
    import numpy as np

    field = np.zeros((3, 2))
    with pytest.raises(DimensionError, match="latitude"):
        check_field_shape(field, lats=[0, 1], lons=[0, 1])  # only 2 lats for 3 rows


def test_check_field_shape_requires_levels_for_3d_field():
    import numpy as np

    field = np.zeros((4, 3, 2))
    with pytest.raises(DimensionError, match="levels"):
        check_field_shape(field, lats=[0, 1, 2], lons=[0, 1], levels=None)


# ------------------------------------------------------------------- validate


def test_validate_aggregates_multiple_violations_not_just_the_first():
    """The whole point of the aggregate path: every violation is reported, not just the first one hit."""
    guard = PhysicsGuard()
    report = guard.validate(
        {
            "air_temperature": 15.0,  # looks like Celsius mistaken for Kelvin - out of range
            "relative_humidity": -10.0,  # invalid
            "lat": 200.0,  # invalid
            "lon": 3.0,
        }
    )

    assert report.passed is False
    assert len(report.violations) >= 3
    assert "range" in report.checks_run
    assert "coordinate" in report.checks_run
    assert "consistency:relative_humidity" in report.checks_run


def test_validate_passes_on_a_fully_real_and_valid_payload():
    guard = PhysicsGuard()
    report = guard.validate(
        {
            "air_temperature": 288.15,
            "relative_humidity": 65.0,
            "lat": 36.7,
            "lon": 3.0,
            "pressure_by_level": [1013.0, 850.0, 700.0, 500.0],
            "forecast_reference_time": datetime(2026, 9, 2, 0, 0),
            "valid_time": datetime(2026, 9, 2, 6, 0),
        }
    )

    assert report.passed is True
    assert report.violations == []
    assert set(report.checks_run) == {"range", "coordinate", "vertical", "time", "consistency:relative_humidity"}


def test_validate_only_runs_checks_whose_keys_are_present():
    guard = PhysicsGuard()
    report = guard.validate({"air_temperature": 288.15})
    assert report.checks_run == ["range"]
    assert report.passed is True


def test_validate_empty_payload_trivially_passes():
    guard = PhysicsGuard()
    report = guard.validate({})
    assert report.passed is True
    assert report.checks_run == []
