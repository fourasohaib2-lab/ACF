"""
Tests for ACFWorkstation's real Research Mode toggle (added
2026-09-04) and the 2 Lab panels that support it
(ACFThermodynamicsLabPanel/ACFMicrophysicsLabPanel).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation import ACFWorkstation
from acf.gui.dashboard.acf_workstation_microphysics import ACFMicrophysicsLabPanel
from acf.gui.dashboard.acf_workstation_thermodynamics import ACFThermodynamicsLabPanel


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


# --------------------------------------------------------------- chrome


def test_research_mode_button_starts_unchecked(qapp):
    ws = ACFWorkstation()
    assert ws.research_mode_button.isChecked() is False


def test_toggling_research_mode_propagates_to_both_supporting_panels(qapp):
    ws = ACFWorkstation()

    ws.research_mode_button.setChecked(True)

    assert ws.thermodynamics_panel._research_mode_enabled is True
    assert ws.microphysics_panel._research_mode_enabled is True
    assert "Research Mode ON" in ws.status_label.text()

    ws.research_mode_button.setChecked(False)

    assert ws.thermodynamics_panel._research_mode_enabled is False
    assert ws.microphysics_panel._research_mode_enabled is False


def test_toggle_research_mode_reachable_from_the_command_palette(qapp):
    ws = ACFWorkstation()
    commands = dict(ws._build_palette_commands())

    commands["Toggle Research Mode"]()

    assert ws.research_mode_button.isChecked() is True


# --------------------------------------------------------- Thermodynamics


def test_thermodynamics_click_is_a_no_op_when_research_mode_is_off(qapp, monkeypatch):
    panel = ACFThermodynamicsLabPanel()
    panel.update_from_volume(_real_small_volume(), level_index=0)
    called = {"n": 0}
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *a, **k: called.__setitem__("n", called["n"] + 1)))

    panel.map_panel.pointClicked.emit(30.0, 10.0)

    assert called["n"] == 0


def test_thermodynamics_click_shows_the_real_full_diagnostic_when_enabled(qapp, monkeypatch):
    panel = ACFThermodynamicsLabPanel()
    volume = _real_small_volume()
    panel.update_from_volume(volume, level_index=0)
    panel.set_research_mode(True)
    shown: list[tuple] = []
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *a, **k: shown.append(a)))

    real_lat, real_lon = float(volume["lats"][2]), float(volume["lons"][3])
    panel.map_panel.pointClicked.emit(real_lat, real_lon)

    assert len(shown) == 1
    title, text = shown[0][1], shown[0][2]
    assert "Research Detail" in title
    assert "θ-e" in text or "Status" in text  # real content, either branch


def test_thermodynamics_set_research_mode_toggles_the_real_flag(qapp):
    panel = ACFThermodynamicsLabPanel()
    assert panel._research_mode_enabled is False
    panel.set_research_mode(True)
    assert panel._research_mode_enabled is True


# ----------------------------------------------------------- Microphysics


def test_microphysics_click_is_a_no_op_when_research_mode_is_off(qapp, monkeypatch):
    panel = ACFMicrophysicsLabPanel()
    panel.update_from_volume(_real_small_volume(), level_index=0)
    called = {"n": 0}
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *a, **k: called.__setitem__("n", called["n"] + 1)))

    panel.map_panel.pointClicked.emit(30.0, 10.0)

    assert called["n"] == 0


def test_microphysics_click_shows_the_real_full_diagnostic_when_enabled(qapp, monkeypatch):
    panel = ACFMicrophysicsLabPanel()
    volume = _real_small_volume()
    panel.update_from_volume(volume, level_index=0)
    panel.set_research_mode(True)
    shown: list[tuple] = []
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *a, **k: shown.append(a)))

    real_lat, real_lon = float(volume["lats"][1]), float(volume["lons"][4])
    panel.map_panel.pointClicked.emit(real_lat, real_lon)

    assert len(shown) == 1
    title, text = shown[0][1], shown[0][2]
    assert "Research Detail" in title
    assert "Phase" in text
    assert "Wet-bulb" in text


def test_microphysics_click_without_a_volume_does_not_crash(qapp, monkeypatch):
    panel = ACFMicrophysicsLabPanel()
    panel.set_research_mode(True)
    called = {"n": 0}
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *a, **k: called.__setitem__("n", called["n"] + 1)))

    panel.map_panel.pointClicked.emit(30.0, 10.0)  # no volume yet - must not raise

    assert called["n"] == 0
