"""
GUI wiring tests for the imported-model vertical cross-section (added
2026-09-09) - closes the import tier's disclosed "no vertical product"
gap at the dashboard level: a file with a real pressure-level coordinate
drives AWCICrossSection through
acf.awci.model_import_cross_section.compute_awci_cross_section_from_imported_dataset()
(the same real path_sampling/ACF alias machinery as the other tiers);
a surface-only file is refused honestly.
"""

from __future__ import annotations

import numpy as np
import pytest

from acf.data.dataset import Dataset
from acf.gui.dashboard.awci_dashboard import AWCIDashboard


def _pressure_level_dataset() -> Dataset:
    """A real CF-style pressure-level dataset (small grid, fast worker)."""
    ds = Dataset(name="pl-gui-test", filetype="NetCDF", source="xarray")
    lats = np.linspace(40.0, 50.0, 4)
    lons = np.linspace(0.0, 10.0, 8)
    levels = np.asarray([1000.0, 850.0, 500.0])
    li = np.arange(3)[:, None, None]
    ia = np.arange(4)[None, :, None]
    shape = (3, 4, 8)
    ds.add_variable("latitude", lats)
    ds.add_variable("longitude", lons)
    ds.add_variable("level", levels)
    ds.add_variable("t", 288.0 - 6.0 * li + 0.1 * ia + np.zeros(shape))
    ds.add_variable("q", np.clip(0.012 - 0.003 * li + np.zeros(shape), 1e-6, None))
    ds.add_variable("pres", np.broadcast_to(levels[:, None, None], shape).copy())
    ds.add_variable("u", 5.0 + 9.0 * li + np.zeros(shape))
    ds.add_variable("v", 2.0 - 1.0 * li + np.zeros(shape))
    for name, unit in (("t", "K"), ("q", "kg kg-1"), ("pres", "hPa"), ("u", "m s-1"), ("v", "m s-1")):
        ds.set_metadata(f"{name}_units", unit)
    return ds


def _surface_only_dataset() -> Dataset:
    ds = Dataset(name="surface-gui-test", filetype="NetCDF", source="xarray")
    lats = np.linspace(40.0, 50.0, 4)
    lons = np.linspace(0.0, 10.0, 8)
    LAT, LON = np.meshgrid(lats, lons, indexing="ij")
    ds.add_variable("latitude", lats)
    ds.add_variable("longitude", lons)
    ds.add_variable("T2", 288.0 + 0.1 * LAT)
    ds.add_variable("U10", 5.0 + 0.05 * LON)
    ds.add_variable("V10", 2.0 + 0.02 * LAT)
    ds.set_metadata("T2_units", "K")
    return ds


@pytest.fixture
def dashboard(qtbot) -> AWCIDashboard:
    widget = AWCIDashboard()
    qtbot.addWidget(widget)
    return widget


def test_pressure_level_import_drives_the_cross_section_panel(
    dashboard: AWCIDashboard, qtbot
) -> None:
    dashboard._imported_dataset = _pressure_level_dataset()
    dashboard._refresh_imported_model()
    dashboard._maybe_show_imported_cross_section()

    # The worker computes off-thread; wait for the GUI-thread handler.
    qtbot.waitUntil(lambda: dashboard._imported_cross_section is not None, timeout=15000)

    result = dashboard._imported_cross_section
    assert result["status"] == "REAL_IMPORTED_MODEL_CROSS_SECTION"
    # The panel shows the real computed transect (the exact same arrays
    # the adapter returned - not a synthetic pattern).
    distances, levels_hpa, grid = dashboard.cross_section._external_cross_section
    assert levels_hpa == pytest.approx([1000.0, 850.0, 500.0])
    np.testing.assert_allclose(np.asarray(grid), np.asarray(result["awci_grid"]))
    assert list(distances) == list(result["distances_km"])
    assert "IMPORTED MODEL" in dashboard.cross_section._title
    # The status line honestly reports the vertical product.
    assert "cross-section" in dashboard.real_physics_status.text()
    assert "1000" in dashboard.real_physics_status.text()


def test_surface_only_file_is_refused_honestly_without_crashing(
    dashboard: AWCIDashboard,
) -> None:
    dashboard._imported_dataset = _surface_only_dataset()
    dashboard._refresh_imported_model()  # the per-point path still works
    assert dashboard._last_point_mode == "imported_model"

    dashboard._maybe_show_imported_cross_section()  # must not raise
    assert dashboard._imported_cross_section is None
    assert "no pressure-level coordinate" in dashboard.real_physics_status.text()
    # The panel keeps its previous (demo) content - never a fake transect.
    assert dashboard.cross_section._external_cross_section is None


def test_stale_file_result_is_never_drawn(
    dashboard: AWCIDashboard, qtbot
) -> None:
    dashboard._imported_dataset = _pressure_level_dataset()
    stale_dataset = _pressure_level_dataset()  # a different object with the same data
    stale_payload = {
        "dataset": stale_dataset,
        "cross_section": {
            "status": "REAL_IMPORTED_MODEL_CROSS_SECTION",
            "distances_km": [0.0, 1.0],
            "levels_hpa": np.asarray([1000.0]),
            "awci_grid": np.zeros((1, 2)),
            "matched_variables": {"temperature": "t"},
            "source_file": "stale",
            "notes": [],
            "hazard_overlay": None,
        },
    }
    dashboard._on_imported_cross_section_ready(stale_payload)
    assert dashboard._imported_cross_section is None
    assert dashboard.cross_section._external_cross_section is None


def test_imported_cross_section_survives_revert_to_demo(
    dashboard: AWCIDashboard, qtbot
) -> None:
    dashboard._imported_dataset = _pressure_level_dataset()
    dashboard._refresh_imported_model()
    dashboard._maybe_show_imported_cross_section()
    qtbot.waitUntil(lambda: dashboard._imported_cross_section is not None, timeout=15000)

    dashboard._revert_to_demo()

    # The import tier survives the demo revert (like its per-point
    # panels) - the cached real transect is redrawn, not dropped.
    distances, levels_hpa, grid = dashboard.cross_section._external_cross_section
    assert levels_hpa == pytest.approx([1000.0, 850.0, 500.0])
    assert "IMPORTED MODEL" in dashboard.cross_section._title
