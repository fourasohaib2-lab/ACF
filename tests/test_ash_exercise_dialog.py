"""Tests for acf.gui.esoc.ash_exercise_dialog.AshExerciseDialog - the
real "Volcanic Ash Exercise" input form (Master Prompt V3 §28-29,
closed 2026-09-20)."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.esoc.ash_exercise_dialog import AshExerciseDialog


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_defaults_never_pretend_a_real_eruption_is_already_entered(qapp):
    """Every field must default to a genuinely honest starting point -
    volumetric_eruption_rate_m3_s=0 (no real eruption assessed unless
    the operator actively enters one), never a plausible-looking
    placeholder value that could be submitted unnoticed."""
    dialog = AshExerciseDialog()
    values = dialog.get_values()
    assert values["volumetric_eruption_rate_m3_s"] == 0.0
    assert values["hours_since_eruption"] == 0.0


def test_get_values_returns_every_real_field_compute_real_ash_exposure_risk_field_needs(qapp):
    from acf.awci.volcanic_ash import compute_real_ash_exposure_risk_field

    dialog = AshExerciseDialog()
    values = dialog.get_values()
    # Every key here must be a real, accepted keyword of the real
    # function this dialog's own values are meant to feed - a real
    # regression guard against the dialog and the function silently
    # drifting apart.
    compute_real_ash_exposure_risk_field(lats=[0.0], lons=[0.0], **values)


def test_operator_entered_values_round_trip_exactly(qapp):
    dialog = AshExerciseDialog()
    dialog.eruption_lat_spin.setValue(36.7)
    dialog.eruption_lon_spin.setValue(3.0)
    dialog.eruption_rate_spin.setValue(500.0)
    dialog.hours_since_spin.setValue(2.5)
    dialog.wind_speed_spin.setValue(12.0)
    dialog.wind_direction_spin.setValue(90.0)
    dialog.altitude_spin.setValue(9000.0)

    values = dialog.get_values()

    assert values == {
        "eruption_lat": 36.7,
        "eruption_lon": 3.0,
        "volumetric_eruption_rate_m3_s": 500.0,
        "hours_since_eruption": 2.5,
        "wind_speed_m_s": 12.0,
        "wind_direction_deg": 90.0,
        "point_altitude_m": 9000.0,
    }


def test_latitude_and_longitude_ranges_are_real_geographic_bounds(qapp):
    dialog = AshExerciseDialog()
    assert dialog.eruption_lat_spin.minimum() == -90.0
    assert dialog.eruption_lat_spin.maximum() == 90.0
    assert dialog.eruption_lon_spin.minimum() == -180.0
    assert dialog.eruption_lon_spin.maximum() == 180.0
    assert dialog.wind_direction_spin.minimum() == 0.0
    assert dialog.wind_direction_spin.maximum() == 360.0
