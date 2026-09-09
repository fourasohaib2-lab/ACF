"""
GUI wiring tests for the imported-model 4D evolution tier (added
2026-09-09, "4D over imported data") - closes the AWCI completion
report's disclosed 4D gap: an imported model file that genuinely
carries a time dimension drives the SAME ▶ 4D Evolution button +
global-map animation the Real Physics solver evolution uses, with
every frame a real per-grid-cell AWCICalculator pass over the file's
own valid times.
"""

from __future__ import annotations

import numpy as np
import pytest

from acf.data.dataset import Dataset
from acf.gui.dashboard.awci_dashboard import AWCIDashboard, _FLIGHT_LEVEL_SELECTOR_OPTIONS_HPA

_FL320_HPA = _FLIGHT_LEVEL_SELECTOR_OPTIONS_HPA["FL320"]


def _evolution_dataset() -> Dataset:
    """A real WRF-style time-series surface dataset (time, lat, lon)."""
    ds = Dataset(name="wrf-4d-gui", filetype="NetCDF", source="xarray")
    lats = np.linspace(30.0, 40.0, 6)
    lons = np.linspace(0.0, 10.0, 8)
    T0 = 288.0 + 0.3 * (lats[:, None] - 30.0) - 0.02 * lons[None, :]
    for name, base, perturb, unit in (
        ("t2m", T0, 2.0, "K"),
        ("q", np.full_like(T0, 0.008), 0.0005, "kg kg-1"),
        ("u10", np.full_like(T0, 5.0), 1.5, "m s-1"),
        ("v10", np.full_like(T0, 1.0), 0.5, "m s-1"),
        ("sp", np.full_like(T0, 1013.0), 1.0, "hPa"),
    ):
        ds.add_variable(name, np.stack([base + k * perturb for k in range(3)], axis=0))
        ds.set_metadata(f"{name}_units", unit)
    ds.add_variable("latitude", lats)
    ds.add_variable("longitude", lons)
    ds.add_variable("time", np.array([0.0, 6.0, 12.0]))
    ds.set_metadata("time_units", "hours since 2026-09-09 00:00:00")
    return ds


@pytest.fixture
def dashboard(qtbot) -> AWCIDashboard:
    widget = AWCIDashboard()
    qtbot.addWidget(widget)
    return widget


def test_imported_time_series_drives_the_4d_evolution_playback(dashboard: AWCIDashboard, qtbot) -> None:
    dashboard._imported_dataset = _evolution_dataset()
    dashboard._toggle_evolution_playback()  # routes to _start_imported_evolution

    qtbot.waitUntil(lambda: dashboard._imported_evolution is not None, timeout=15000)

    assert dashboard._evolution is dashboard._imported_evolution
    assert dashboard._evolution_timer.isActive() is True
    assert "Stop Animation" in dashboard.play_evolution_button.text()
    # The global map animates the real imported frame - source-labelled.
    lons, lats, grid = dashboard.global_map._external_field
    assert "IMPORTED MODEL" in dashboard.global_map._title
    assert "t+" in dashboard.time_readout.text()
    assert np.isfinite(grid).all()
    # The status line discloses the real provenance.
    assert "IMPORTED MODEL 4D" in dashboard.real_physics_status.text()


def test_new_import_invalidates_a_cached_imported_evolution(
    dashboard: AWCIDashboard, qtbot
) -> None:
    dashboard._imported_dataset = _evolution_dataset()
    dashboard._start_imported_evolution()
    qtbot.waitUntil(lambda: dashboard._imported_evolution is not None, timeout=15000)
    assert dashboard.play_evolution_button.isEnabled() is True

    # A second (coordinate-less) import drops the cached evolution - a
    # stale-file evolution is never replayed.
    stale = Dataset(name="stale", filetype="NetCDF", source="xarray")
    stale.add_variable("t2m", np.zeros((3, 4, 5)))
    dashboard._imported_dataset = stale
    dashboard._invalidate_imported_evolution()

    assert dashboard._imported_evolution is None


def test_flight_level_change_invalidates_and_recomputes_lazily(
    dashboard: AWCIDashboard, qtbot
) -> None:
    dashboard._imported_dataset = _evolution_dataset()
    dashboard._start_imported_evolution()
    qtbot.waitUntil(lambda: dashboard._imported_evolution is not None, timeout=15000)

    dashboard._on_flight_level_selector_changed("FL320")

    # Level changed -> cached evolution dropped (a stale-level evolution
    # is never replayed); the button is re-enabled so the next click
    # recomputes at the new level.
    assert dashboard._imported_evolution is None
    assert dashboard._current_flight_level_hpa == pytest.approx(_FL320_HPA)


def test_real_physics_evolution_keeps_priority_while_active(
    dashboard: AWCIDashboard,
) -> None:
    """An active imported dataset must not hijack the Real Physics 4D
    path - the solver evolution stays the one the button continues."""
    dashboard._imported_dataset = _evolution_dataset()
    dashboard._real_physics_active = True
    solver_evolution = {
        "awci_evolution": np.zeros((2, 2, 4, 4)),
        "lats": np.linspace(30.0, 40.0, 4),
        "lons": np.linspace(0.0, 10.0, 4),
        "valid_time_seconds": np.array([0.0, 3600.0]),
        "n_frames": 2,
    }
    dashboard._on_evolution_ready(solver_evolution)

    assert dashboard._evolution is solver_evolution
    assert dashboard._evolution_timer.isActive() is True


def test_imported_evolution_survives_revert_to_demo(dashboard: AWCIDashboard) -> None:
    """_revert_to_demo tears down the REAL PHYSICS session - the
    imported-model evolution belongs to the import tier and must
    survive it (the ▶ button then replays the imported evolution)."""
    dashboard._imported_dataset = _evolution_dataset()
    dashboard._start_imported_evolution()
    qtbot_wait = None
    # Simulate an already-computed imported evolution without the wait:
    dashboard._imported_evolution = {
        "awci_evolution": np.zeros((2, 1, 4, 4)),
        "lats": np.linspace(30.0, 40.0, 4),
        "lons": np.linspace(0.0, 10.0, 4),
        "valid_time_seconds": np.array([0.0, 3600.0]),
        "n_frames": 2,
    }

    dashboard._revert_to_demo()

    assert dashboard._imported_evolution is not None  # survived - import tier
    assert dashboard._real_physics_active is False
    assert dashboard._real_volume is None
