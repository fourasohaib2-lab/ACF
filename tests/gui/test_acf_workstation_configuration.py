"""
Tests for ACFWorkstation's real Configuration Management (added
2026-09-04) - _export_configuration()/_apply_configuration() and the
real "💾 Save Configuration…"/"📂 Load Configuration…" menu actions
behind the "⚙" button.
"""

from __future__ import annotations

import json

import pytest
from PySide6.QtWidgets import QApplication, QFileDialog

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation import ACFWorkstation


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_small_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=6, n_lon=6, n_levels=5, steps=2, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_settings_button_is_a_real_tool_button_with_a_real_menu(qapp):
    from PySide6.QtWidgets import QMenu, QToolButton

    ws = ACFWorkstation()

    assert isinstance(ws.settings_button, QToolButton)
    menu = ws.settings_button.menu()
    assert isinstance(menu, QMenu)
    action_texts = [a.text() for a in menu.actions()]
    assert action_texts == ["💾 Save Configuration…", "📂 Load Configuration…"]


def test_export_configuration_captures_the_real_current_selections(qapp):
    ws = ACFWorkstation()
    ws.model_selector.setCurrentText("ALADIN")
    ws.dynamics_panel.variable_selector.setCurrentText("Relative vorticity")

    config = ws._export_configuration()

    assert config["model"] == "ALADIN"
    assert config["dynamics_variable"] == "Relative vorticity"
    assert config["nav_row"] == ws.nav_list.currentRow()
    assert config["level_index"] == ws._level_index


def test_apply_configuration_restores_the_real_selections(qapp):
    ws = ACFWorkstation()
    config = {
        "model": "AROME",
        "dynamics_variable": "Divergence",
        "thermodynamics_variable": "Relative humidity",
        "nav_row": 2,
    }

    ws._apply_configuration(config)

    assert ws.model_selector.currentText() == "AROME"
    assert ws.dynamics_panel.variable_selector.currentText() == "Divergence"
    assert ws.thermodynamics_panel.variable_selector.currentText() == "Relative humidity"
    assert ws.nav_list.currentRow() == 2


def test_apply_configuration_ignores_unknown_or_malformed_fields(qapp):
    """Real, defensive parsing of a real external file - a malformed
    field must never crash the whole restore."""
    ws = ACFWorkstation()
    original_model = ws.model_selector.currentText()

    ws._apply_configuration({"model": "NOT_A_REAL_MODEL", "nav_row": "not an int", "unknown_key": 42})

    assert ws.model_selector.currentText() == original_model  # unchanged - invalid value ignored
    assert ws.nav_list.currentRow() == 0  # unchanged - non-int nav_row ignored


def test_export_then_apply_round_trips_every_real_configuration_selector(qapp):
    """Real, future-proof coverage: every entry _configuration_
    selectors() itself declares - not a hand-picked subset - must
    genuinely round-trip through export/apply. Iterates the same real
    dict the Workstation's own save/load logic uses, so a newly added
    Lab's own selector (e.g. Convection/Terrain, added Phases 18/22)
    is automatically covered without a separate test having to be
    remembered for it."""
    ws = ACFWorkstation()
    chosen: dict[str, str] = {}
    for key, selector in ws._configuration_selectors().items():
        assert selector.count() > 0, f"{key} has no real items to choose from"
        # Pick the LAST real item (rarely the selector's own default) -
        # a genuine, real proof this isn't just reading back the
        # selector's own unchanged starting value.
        chosen[key] = selector.itemText(selector.count() - 1)
        selector.setCurrentText(chosen[key])

    config = ws._export_configuration()
    for key, expected in chosen.items():
        assert config[key] == expected

    ws2 = ACFWorkstation()
    ws2._apply_configuration(config)
    for key, expected in chosen.items():
        assert ws2._configuration_selectors()[key].currentText() == expected


def test_export_then_apply_round_trips_the_real_configuration(qapp):
    ws = ACFWorkstation()
    ws.model_selector.setCurrentText("ARPEGE")
    ws.microphysics_panel.variable_selector.setCurrentText("Wet-bulb temperature")
    ws.quality_panel.variable_selector.setCurrentText("Pressure")
    config = ws._export_configuration()

    ws2 = ACFWorkstation()
    ws2._apply_configuration(config)

    assert ws2.model_selector.currentText() == "ARPEGE"
    assert ws2.microphysics_panel.variable_selector.currentText() == "Wet-bulb temperature"
    assert ws2.quality_panel.variable_selector.currentText() == "Pressure"


def test_level_index_restored_before_a_volume_exists_stays_pending_then_applies(qapp):
    ws = ACFWorkstation()
    assert ws._volume is None

    ws._apply_configuration({"level_index": 3})

    assert ws._pending_level_index == 3

    ws._on_volume_ready(_real_small_volume())

    assert ws._pending_level_index is None
    assert ws._level_index == 3
    assert ws.level_slider.value() == 3


def test_level_index_restored_after_a_volume_exists_applies_immediately_and_clamps(qapp):
    ws = ACFWorkstation()
    ws._on_volume_ready(_real_small_volume())  # n_levels=5 -> max real level index 4

    ws._apply_configuration({"level_index": 999})  # a real, deliberately out-of-range value

    assert ws._level_index == 4  # clamped to the real volume's own real max level


def test_save_configuration_writes_a_real_json_file(qapp, tmp_path, monkeypatch):
    ws = ACFWorkstation()
    ws.model_selector.setCurrentText("ALADIN")
    target = tmp_path / "config.json"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(target), "")))

    ws._save_configuration()

    assert target.exists()
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["model"] == "ALADIN"
    assert "✅" in ws.status_label.text()


def test_load_configuration_reads_a_real_json_file(qapp, tmp_path, monkeypatch):
    ws = ACFWorkstation()
    target = tmp_path / "config.json"
    target.write_text(json.dumps({"model": "AROME", "dynamics_variable": "Divergence"}), encoding="utf-8")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", staticmethod(lambda *a, **k: (str(target), "")))

    ws._load_configuration()

    assert ws.model_selector.currentText() == "AROME"
    assert ws.dynamics_panel.variable_selector.currentText() == "Divergence"
    assert "✅" in ws.status_label.text()


def test_load_configuration_reports_an_honest_error_for_invalid_json(qapp, tmp_path, monkeypatch):
    ws = ACFWorkstation()
    target = tmp_path / "broken.json"
    target.write_text("{ not valid json", encoding="utf-8")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", staticmethod(lambda *a, **k: (str(target), "")))

    ws._load_configuration()

    assert "⚠" in ws.status_label.text()
    assert "Could not load" in ws.status_label.text()


def test_save_and_load_are_reachable_from_the_command_palette(qapp):
    ws = ACFWorkstation()
    labels = [label for label, _callback in ws._build_palette_commands()]
    assert "Save Configuration…" in labels
    assert "Load Configuration…" in labels
