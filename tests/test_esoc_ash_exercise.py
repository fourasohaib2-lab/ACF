"""
Tests for ESOCWindow's "🌋 Ash Exercise" toolbar action (Master Prompt
V3 §28-29's "ash" layer, closed 2026-09-20) - real
acf.awci.volcanic_ash.compute_real_ash_exposure_risk_field() overlaid
on ESOC's own central map, from real operator-supplied eruption data
(AshExerciseDialog), never an automatic/fabricated field.
"""

from __future__ import annotations

from unittest.mock import patch

from PySide6.QtWidgets import QDialog

from acf.gui.esoc.esoc_toolbar import ESOCToolbar
from acf.gui.esoc.esoc_window import ESOCWindow


def test_toolbar_has_the_real_ash_exercise_action(qtbot):
    toolbar = ESOCToolbar()
    qtbot.addWidget(toolbar)
    action_labels = [act.text() for act in toolbar.actions()]
    assert "🌋 Ash Exercise" in action_labels


def test_cancelling_the_dialog_computes_nothing(qtbot):
    win = ESOCWindow()
    qtbot.addWidget(win)
    map_canvas = win.layout_manager.view_manager.map_canvas

    with patch("acf.gui.esoc.esoc_window.AshExerciseDialog.exec", return_value=QDialog.DialogCode.Rejected):
        win._open_ash_exercise()

    assert map_canvas.layer_manager.available_layers["Volcanic Ash"].custom_data is None


def test_zero_eruption_rate_is_rejected_with_a_real_warning_not_computed(qtbot):
    from PySide6.QtWidgets import QMessageBox

    win = ESOCWindow()
    qtbot.addWidget(win)
    map_canvas = win.layout_manager.view_manager.map_canvas

    with (
        patch("acf.gui.esoc.esoc_window.AshExerciseDialog.exec", return_value=QDialog.DialogCode.Accepted),
        patch("acf.gui.esoc.esoc_window.AshExerciseDialog.get_values", return_value={
            "eruption_lat": 36.7, "eruption_lon": 3.0, "volumetric_eruption_rate_m3_s": 0.0,
            "hours_since_eruption": 0.0, "wind_speed_m_s": 0.0, "wind_direction_deg": 270.0,
            "point_altitude_m": 8000.0,
        }),
        patch.object(QMessageBox, "warning") as mock_warning,
    ):
        win._open_ash_exercise()

    mock_warning.assert_called_once()
    assert map_canvas.layer_manager.available_layers["Volcanic Ash"].custom_data is None


def test_a_real_exercise_scenario_genuinely_populates_the_map_layer(qtbot):
    win = ESOCWindow()
    qtbot.addWidget(win)
    map_canvas = win.layout_manager.view_manager.map_canvas

    real_values = {
        "eruption_lat": 36.7, "eruption_lon": 3.0, "volumetric_eruption_rate_m3_s": 500.0,
        "hours_since_eruption": 2.0, "wind_speed_m_s": 10.0, "wind_direction_deg": 270.0,
        "point_altitude_m": 8000.0,
    }
    with (
        patch("acf.gui.esoc.esoc_window.AshExerciseDialog.exec", return_value=QDialog.DialogCode.Accepted),
        patch("acf.gui.esoc.esoc_window.AshExerciseDialog.get_values", return_value=real_values),
    ):
        win._open_ash_exercise()

    qtbot.waitUntil(
        lambda: "Volcanic Ash" in map_canvas.layer_manager.active_layer_names,
        timeout=30000,
    )
    layer = map_canvas.layer_manager.available_layers["Volcanic Ash"]
    assert layer.custom_data is not None


def test_ash_exercise_does_not_appear_in_the_automatic_awci_field_sweep(qtbot):
    """Real regression guard: the "🌪️ AWCI Field" action's own generic
    per-module sweep must never auto-populate "Volcanic Ash" - see
    VolcanicAshLayer's own docstring for why."""
    win = ESOCWindow()
    qtbot.addWidget(win)
    map_canvas = win.layout_manager.view_manager.map_canvas

    win._show_awci_field_on_map()

    qtbot.waitUntil(
        lambda: "AWCI Complexity" in map_canvas.layer_manager.active_layer_names,
        timeout=60000,
    )

    assert map_canvas.layer_manager.available_layers["Volcanic Ash"].custom_data is None
    assert "Volcanic Ash" not in map_canvas.layer_manager.active_layer_names
