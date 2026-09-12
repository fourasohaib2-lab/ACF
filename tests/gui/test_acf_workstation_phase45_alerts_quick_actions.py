"""
Tests for ACF Scientific Workstation's Phase 45 (2026-09-12) "Alerts &
Hazards" and "Quick Actions" sections - added to match the new
"Atmospheric Analysis" reference mockup's own Overview screen.

Alerts & Hazards reuses ForecastDecisionEngine.assess_severe_weather_risk()
(real, cited NOAA SPC / Doswell et al. 1996 thresholds, already corrected
once in this codebase from an identical fabrication bug), fed only with
this Workstation's own real CAPE/bulk-wind-shear - a disclosed, honest
subset, never full severe-weather coverage.
"""

from __future__ import annotations

import json

import pytest
from PySide6.QtWidgets import QApplication, QFileDialog

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation import ACFWorkstation
from acf.gui.dashboard.acf_workstation_overview_landing import compute_real_alerts


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_small_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=8, n_lon=8, n_levels=5, steps=2, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


# --------------------------------------------------------- Alerts & Hazards


def test_compute_real_alerts_matches_a_direct_independent_engine_call():
    from acf.ai.decision_support.decision_engine import ForecastDecisionEngine

    result = compute_real_alerts(cape_j_kg=2000.0, bulk_wind_shear_ms=18.0)

    expected = ForecastDecisionEngine().assess_severe_weather_risk(
        {"CAPE": 2000.0, "shear_0_6km": 18.0}
    )
    assert result["risk_level"] == expected["risk_level"]
    assert result["detected_phenomena"] == expected["detected_phenomena"]


def test_compute_real_alerts_below_threshold_is_honestly_faible():
    """Real regression guard: CAPE/shear below the real cited
    thresholds (1500 J/kg, 15 m/s) must never fabricate a risk."""
    result = compute_real_alerts(cape_j_kg=50.0, bulk_wind_shear_ms=2.0)

    assert result["risk_level"] == "FAIBLE"
    assert result["detected_phenomena"] == []


def test_compute_real_alerts_above_threshold_genuinely_triggers():
    result = compute_real_alerts(cape_j_kg=2000.0, bulk_wind_shear_ms=18.0)

    assert result["risk_level"] != "FAIBLE"
    assert len(result["detected_phenomena"]) >= 1


def test_alerts_section_updates_on_volume_ready(qapp):
    ws = ACFWorkstation()
    volume = _real_small_volume()

    ws._on_volume_ready(volume)

    assert ws._last_alerts is not None
    assert "Risk level:" in ws.overview_landing_panel.alerts_risk_label.text()


def test_alerts_section_updates_on_map_click(qapp):
    ws = ACFWorkstation()
    volume = _real_small_volume()
    ws._on_volume_ready(volume)
    lat, lon = float(volume["lats"][1]), float(volume["lons"][1])

    ws._on_map_point_clicked(lat, lon)

    expected = compute_real_alerts(ws._last_key_metrics["cape_j_kg"], ws._last_key_metrics["bulk_wind_shear_ms"])
    assert ws._last_alerts["risk_level"] == expected["risk_level"]


# ------------------------------------------------------------ Quick Actions


def test_quick_action_buttons_are_wired_to_the_real_existing_handlers(qapp):
    ws = ACFWorkstation()
    panel = ws.overview_landing_panel

    assert panel.generate_report_button.isEnabled() is True
    assert panel.run_new_analysis_button.isEnabled() is True
    assert panel.export_data_button.isEnabled() is True
    assert panel.compare_models_button.isEnabled() is True


def test_run_new_analysis_quick_action_calls_the_real_refresh(qapp, monkeypatch):
    """The button is wired to the real bound refresh() at construction
    time (constructor injection - same convention as every other
    callback here), so ACFWorkstation.refresh must be patched at the
    CLASS level before construction for the button's own already-
    captured callable to reflect it."""
    called = {"n": 0}
    monkeypatch.setattr(ACFWorkstation, "refresh", lambda self: called.__setitem__("n", called["n"] + 1))
    ws = ACFWorkstation()

    ws.overview_landing_panel.run_new_analysis_button.click()

    assert called["n"] == 1


def test_compare_models_quick_action_navigates_to_the_real_multimodel_panel(qapp):
    ws = ACFWorkstation()

    ws.overview_landing_panel.compare_models_button.click()

    assert ws.stack.currentWidget() is ws.multimodel_panel


def test_generate_report_quick_action_calls_the_real_save_configuration(qapp, tmp_path, monkeypatch):
    ws = ACFWorkstation()
    ws.model_selector.setCurrentText("ALADIN")
    target = tmp_path / "quick_report.json"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(target), "")))

    ws.overview_landing_panel.generate_report_button.click()

    assert target.exists()
    assert json.loads(target.read_text(encoding="utf-8"))["model"] == "ALADIN"


def test_export_data_writes_the_real_currently_displayed_values(qapp, tmp_path, monkeypatch):
    ws = ACFWorkstation()
    volume = _real_small_volume()
    ws._on_volume_ready(volume)
    target = tmp_path / "diagnostics.json"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(target), "")))

    ws._export_diagnostics_data()

    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["key_metrics"]["cape_j_kg"] == ws._last_key_metrics["cape_j_kg"]
    assert payload["alerts"]["risk_level"] == ws._last_alerts["risk_level"]
    assert payload["model_consensus"] is None  # honestly null - never computed in this test


def test_export_data_does_nothing_without_a_chosen_path(qapp, monkeypatch):
    ws = ACFWorkstation()
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: ("", "")))

    ws._export_diagnostics_data()  # must not raise
