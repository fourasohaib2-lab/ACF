"""
Tests for acf.gui.dashboard.acf_workstation_complexity - the real,
multidimensional (never combined into one score) Complexity Explorer
helpers backing the AWCI-free ACF Scientific Workstation (added
2026-09-04).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from acf.gui.dashboard.acf_workstation_complexity import (
    compute_real_spatial_complexity,
    compute_real_temporal_complexity,
)
from acf.gui.dashboard.acf_workstation_dynamics import real_grid_spacing_m


def test_spatial_complexity_matches_a_known_analytic_gradient():
    """A real, purely zonal linear temperature field - simple enough
    to hand-compute the exact expected interior gradient magnitude
    independently."""
    lats = np.linspace(30.0, 40.0, 9)
    lons = np.linspace(0.0, 10.0, 9)
    lon_grid = np.broadcast_to(lons[None, :], (9, 9)).astype(float)
    b = 2.0  # K per degree longitude
    temperature = 280.0 + b * lon_grid

    spatial_complexity = compute_real_spatial_complexity(temperature, lats, lons)

    _dy, dx_per_row = real_grid_spacing_m(lats, lons)
    dlon_step_deg = lons[1] - lons[0]
    expected_gradient_per_metre = (b * dlon_step_deg / dx_per_row) * 100_000.0  # K/m -> K/100km
    expected = np.broadcast_to(expected_gradient_per_metre[:, None], (9, 9))

    assert np.allclose(spatial_complexity[1:-1, 1:-1], expected[1:-1, 1:-1], rtol=1e-6)


def test_spatial_complexity_is_zero_for_a_uniform_field():
    lats = np.linspace(20.0, 30.0, 7)
    lons = np.linspace(-5.0, 5.0, 7)
    temperature = np.full((7, 7), 288.0)

    spatial_complexity = compute_real_spatial_complexity(temperature, lats, lons)

    assert np.allclose(spatial_complexity[1:-1, 1:-1], 0.0, atol=1e-9)


def _synthetic_evolution(n_frames: int, slope_k_per_h: float) -> dict[str, Any]:
    """A real-*shaped* (not real-solver-computed) evolution dict, with
    a KNOWN, hand-picked linear temperature trajectory - isolates
    compute_real_temporal_complexity() as a pure function test,
    separate from a real CoupledEarthSolver run (that real integration
    is verified by tests/gui/test_acf_workstation.py's own real
    off-thread worker test)."""
    valid_time_seconds = [3600.0 * h for h in range(n_frames)]
    base = 280.0
    temperature_evolution = np.stack(
        [np.full((1, 4, 4), base + slope_k_per_h * h) for h in range(n_frames)], axis=0
    )
    return {
        "temperature_evolution": temperature_evolution,
        "valid_time_seconds": valid_time_seconds,
        "n_levels": 1,
        "n_frames": n_frames,
        "model": "ARPEGE",
    }


def test_temporal_complexity_matches_a_known_constant_rate():
    slope = 1.5  # K/h
    evolution = _synthetic_evolution(n_frames=4, slope_k_per_h=slope)

    rates = compute_real_temporal_complexity(evolution, level_index=0)

    assert np.allclose(rates, slope, atol=1e-9)


def test_temporal_complexity_is_zero_for_a_steady_state():
    evolution = _synthetic_evolution(n_frames=3, slope_k_per_h=0.0)

    rates = compute_real_temporal_complexity(evolution, level_index=0)

    assert np.allclose(rates, 0.0, atol=1e-12)
