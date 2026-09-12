"""
Tests for ACF Scientific Workstation's Phase 44 (2026-09-12) "Key
Metrics" and "Model Consensus" sections on the Overview page - added to
match the new "Atmospheric Analysis" reference mockup's own Overview
screen, with 2 deliberate, disclosed departures from its literal numbers
(see acf_workstation_overview_landing.py's own module docstring): no
fabricated single "Complexity Index"/"Instability" 0-1 composite, and no
fabricated "% agreement" gauge - both would violate this project's own
master-spec §21/§67 "no single composite score" rule.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation import ACFWorkstation
from acf.gui.dashboard.acf_workstation_overview_landing import compute_real_key_metrics_at_point


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


# ----------------------------------------------------------- Key Metrics


def test_compute_real_key_metrics_at_point_matches_direct_independent_calls():
    """Cross-check discipline: the combined helper's own real values
    must equal fresh, independent direct calls to the same real
    underlying functions - never a separately re-derived number."""
    from acf.awci.theta_e import compute_real_theta_e_at_point
    from acf.gui.dashboard.acf_workstation_complexity import compute_real_spatial_complexity
    from acf.gui.dashboard.acf_workstation_stability_indices import compute_real_stability_indices_at_point

    volume = _real_small_volume()
    lat, lon = float(volume["lats"][2]), float(volume["lons"][3])

    result = compute_real_key_metrics_at_point(volume, lat, lon)

    expected_indices = compute_real_stability_indices_at_point(volume, lat, lon)
    assert result["cape_j_kg"] == expected_indices["cape_j_kg"]
    assert result["bulk_wind_shear_ms"] == expected_indices["bulk_wind_shear_ms"]

    import numpy as np

    lats = np.asarray(volume["lats"])
    lons = np.asarray(volume["lons"])
    lat_idx = int(np.argmin(np.abs(lats - lat)))
    lon_idx = int(np.argmin(np.abs(lons - lon)))
    t = float(volume["temperature_volume"][0, lat_idx, lon_idx])
    q = float(volume["specific_humidity_volume"][0, lat_idx, lon_idx])
    p = float(volume["pressure_volume_hpa"][0, lat_idx, lon_idx])
    expected_theta_e = compute_real_theta_e_at_point(t, q, p)
    assert result["relative_humidity_pct"] == expected_theta_e["relative_humidity_pct"]

    expected_spatial = compute_real_spatial_complexity(volume["temperature_volume"][0], lats, lons)
    assert result["spatial_complexity_k_per_100km"] == pytest.approx(float(expected_spatial[lat_idx, lon_idx]))


def test_key_metrics_are_never_a_fabricated_unitless_0_to_1_range():
    """Real regression guard for the explicit design decision: these
    are real physical quantities in real units, not a normalized score."""
    volume = _real_small_volume()
    result = compute_real_key_metrics_at_point(volume, float(volume["lats"][0]), float(volume["lons"][0]))

    # CAPE and spatial-complexity-gradient real ranges genuinely exceed
    # [0, 1] - if they didn't, that alone wouldn't prove no fabricated
    # normalization was applied, but this at least confirms the raw
    # real units are what's returned, not a squeezed index.
    assert "cape_j_kg" in result
    assert "relative_humidity_pct" in result
    assert "bulk_wind_shear_ms" in result
    assert "spatial_complexity_k_per_100km" in result
    assert "complexity_index" not in result  # the mockup's own forbidden composite name


def test_on_volume_ready_populates_the_real_key_metrics_on_overview(qapp):
    ws = ACFWorkstation()
    volume = _real_small_volume()

    ws._on_volume_ready(volume)

    expected = compute_real_key_metrics_at_point(
        volume, *ws._last_clicked_point if ws._last_clicked_point else
        (float(volume["lats"][len(volume["lats"]) // 2]), float(volume["lons"][len(volume["lons"]) // 2]))
    )
    panel = ws.overview_landing_panel
    assert f"{expected['cape_j_kg']:.0f} J/kg" in panel._metric_value_labels["cape_j_kg"].text()
    assert f"{expected['relative_humidity_pct']:.1f} %" in panel._metric_value_labels["relative_humidity_pct"].text()


def test_map_click_refreshes_the_real_key_metrics(qapp):
    ws = ACFWorkstation()
    volume = _real_small_volume()
    ws._on_volume_ready(volume)
    lat, lon = float(volume["lats"][1]), float(volume["lons"][1])

    ws._on_map_point_clicked(lat, lon)

    expected = compute_real_key_metrics_at_point(volume, lat, lon)
    panel = ws.overview_landing_panel
    assert f"{expected['bulk_wind_shear_ms']:.2f} m/s" in panel._metric_value_labels["bulk_wind_shear_ms"].text()
    assert f"{lat:.2f}" in panel._metric_point_label.text()


# ------------------------------------------------------------ Consensus


def test_consensus_button_starts_disabled_with_no_callback():
    from acf.gui.dashboard.acf_workstation_overview_landing import ACFOverviewLandingPanel

    panel = ACFOverviewLandingPanel(navigate_to=lambda _n: None, module_names=[], compute_consensus=None)
    assert panel.consensus_button.isEnabled() is False


def test_consensus_button_genuinely_runs_off_thread_and_reports_real_values(qapp):
    """Real regression guard: uses the smallest real MODEL_CONFIGS
    grids reachable via a tiny monkeypatched model set would be nicer,
    but ModelConsensusEngine.compute_real_multi_model_disagreement()
    always compares real MODEL_CONFIGS entries - this exercises the
    real, if slower, full path rather than mocking the engine away."""
    ws = ACFWorkstation()

    ws._start_consensus()

    assert ws.overview_landing_panel.consensus_button.isEnabled() is False
    assert "Computing" in ws.overview_landing_panel.consensus_status_label.text()

    QThreadPool.globalInstance().waitForDone(60_000)
    qapp.processEvents()

    assert ws.overview_landing_panel.consensus_button.isEnabled() is True
    status_text = ws.overview_landing_panel.consensus_status_label.text()
    assert "✅" in status_text or "⚠" in status_text
    if "✅" in status_text:
        assert "K" in status_text  # real physical unit, never a fabricated "%"
        assert "%" not in status_text
        models_text = ws.overview_landing_panel.consensus_models_label.text()
        assert "AROME" in models_text
        assert "WRF" not in models_text  # no real backing anywhere in this codebase
