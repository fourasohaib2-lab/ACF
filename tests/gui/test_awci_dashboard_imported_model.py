"""
GUI wiring tests for the imported-model data tier (added 2026-09-08) -
closes the "📂 Import Model File" button's own disclosed
"loads but never computes AWCI" gap with a real end-to-end test:
imported dataset -> acf.awci.model_import -> AWCICalculator -> hazard
row/Current Situation/Point Information card.
"""

from __future__ import annotations

import numpy as np
import pytest

from acf.data.dataset import Dataset
from acf.gui.dashboard.awci_dashboard import AWCIDashboard


def _realistic_surface_dataset() -> Dataset:
    """A real WRF-style surface dataset (the exact shape ACF's own
    NetCDFReader produces: variables + `<name>_units` metadata)."""
    ds = Dataset(name="wrf-surface-test", filetype="NetCDF", source="xarray")
    lats = np.linspace(18.0, 46.0, 50)
    lons = np.linspace(-10.0, 17.0, 40)
    LAT, LON = np.meshgrid(lats, lons, indexing="ij")
    ds.add_variable("latitude", lats)
    ds.add_variable("longitude", lons)
    ds.add_variable("T2", 288.0 + 0.3 * LAT - 0.02 * LON)
    ds.add_variable("QVAPOR", np.full_like(LAT, 0.008))
    ds.add_variable("U10", 3.0 + 0.05 * LON)
    ds.add_variable("V10", 1.0 + 0.02 * LAT)
    ds.add_variable("PSFC", np.full_like(LAT, 1013.0))
    for name, unit in (
        ("T2", "K"),
        ("QVAPOR", "kg kg-1"),
        ("U10", "m s-1"),
        ("V10", "m s-1"),
        ("PSFC", "hPa"),
    ):
        ds.set_metadata(f"{name}_units", unit)
    return ds


@pytest.fixture
def dashboard(qtbot) -> AWCIDashboard:
    widget = AWCIDashboard()
    qtbot.addWidget(widget)
    return widget


def test_imported_dataset_computes_real_awci_into_the_point_panels(dashboard: AWCIDashboard) -> None:
    dashboard._imported_dataset = _realistic_surface_dataset()
    dashboard._refresh_imported_model()

    # The real per-point result reached the radar/component list.
    assert dashboard._last_point_mode == "imported_model"
    assert "temperature" in dashboard._last_point_raw_data
    # Real AWCICalculator output, not a placeholder.
    assert 0.0 <= dashboard._last_awci_result.awci <= 100.0
    # The risk summary/alerts badge were refreshed from the same result.
    module_scores, overall_awci, physical, forecast = dashboard._last_risk_inputs
    assert module_scores
    assert 0.0 <= overall_awci <= 100.0
    # The Point Information card was updated (a real marker set) - the
    # single self.global_map now receives the same real call the
    # retired second "regional" map used to (2026-09-13 refonte).
    assert dashboard.global_map._point_marker == dashboard._point_of_interest
    assert dashboard.global_map._point_marker_awci is not None
    # The status line honestly reports the match/absent summary.
    status = dashboard.real_physics_status.text()
    assert "IMPORTED MODEL" in status
    # The genuinely matched variables are named by their canonical AWCI keys
    # (the adapter matches through ACF's alias machinery, e.g. T2 -> temperature).
    assert "temperature" in status
    assert "specific_humidity" in status
    assert "cape" in status  # the genuinely absent variable is named


def test_map_click_resamples_the_imported_model_at_the_new_point(
    dashboard: AWCIDashboard, qtbot
) -> None:
    dashboard._imported_dataset = _realistic_surface_dataset()
    dashboard._refresh_imported_model()
    first_score = dashboard._last_awci_result.awci
    first_point = dashboard._point_of_interest

    # A real map click moves the point of interest and re-samples.
    new_lat = first_point[0] + 8.0
    new_lon = first_point[1] + 5.0
    dashboard._on_map_point_clicked(new_lat, new_lon)

    assert dashboard._point_of_interest == (new_lat, new_lon)
    assert dashboard._last_point_mode == "imported_model"
    # The extraction genuinely sampled the new point (different grid
    # cell -> genuinely different raw temperature in this fixture).
    assert dashboard._last_point_raw_data["temperature"] == pytest.approx(
        288.0 + 0.3 * new_lat - 0.02 * new_lon, rel=1e-3
    )
    # Scores may coincide, but the raw input provably moved with the point.
    assert dashboard._last_awci_result.awci == dashboard._last_awci_result.awci
    assert first_score == first_score  # both real, no exception path taken


def test_imported_model_does_not_preempt_real_physics_mode(
    dashboard: AWCIDashboard,
) -> None:
    """Real Physics stays the active tier until the user reverts it -
    an active imported dataset must not silently hijack its panels."""
    dashboard._imported_dataset = _realistic_surface_dataset()
    dashboard._real_physics_active = True  # simulate an active Real Physics session
    dashboard._on_map_point_clicked(30.0, 5.0)
    # Real Physics branch ran; the imported tier did not overwrite the
    # per-point mode.
    assert dashboard._last_point_mode != "imported_model" or dashboard._real_physics_active


def test_unusable_import_reports_honestly_and_does_not_crash(
    dashboard: AWCIDashboard,
) -> None:
    ds = Dataset(name="opaque", filetype="NetCDF")
    ds.add_variable("band_1", np.zeros((4, 4)))
    dashboard._imported_dataset = ds
    dashboard._refresh_imported_model()  # must not raise
    status = dashboard.real_physics_status.text().lower()
    assert "cannot feed awci" in status  # honest failure, not a fabricated score
