"""
Tests for acf.gui.dashboard.acf_workstation_dynamics - the real
vorticity/divergence helper backing the AWCI-free ACF Scientific
Workstation's Dynamics Lab (added 2026-09-04, explicit user master
spec: "ACF CORE ONLY - NO AWCI").
"""

from __future__ import annotations

import numpy as np

from acf.earth_physics.atmospheric_dynamics.vorticity import VorticityCalculator
from acf.gui.dashboard.acf_workstation_dynamics import (
    compute_real_vorticity_divergence,
    real_grid_spacing_m,
)
from acf.science.divergence import Divergence

_EARTH_RADIUS_M = 6_371_000.0


def test_real_grid_spacing_matches_the_standard_real_formula():
    lats = np.linspace(30.0, 40.0, 11)
    lons = np.linspace(0.0, 10.0, 11)

    dy, dx_per_row = real_grid_spacing_m(lats, lons)

    dlat_step_deg = lats[1] - lats[0]
    dlon_step_deg = lons[1] - lons[0]
    expected_dy = _EARTH_RADIUS_M * np.radians(dlat_step_deg)
    expected_dx = _EARTH_RADIUS_M * np.cos(np.radians(lats)) * np.radians(dlon_step_deg)

    assert dy == expected_dy
    assert np.allclose(dx_per_row, expected_dx)
    # Real, physical: zonal spacing shrinks toward the poles (cos(lat) -> 0).
    assert dx_per_row[-1] < dx_per_row[0]


def test_vorticity_divergence_match_a_known_analytic_case():
    """u varies only with latitude (v=0 everywhere) - a real, simple
    enough field to hand-compute the exact expected interior values
    independently, without calling the function under test for its
    own inputs."""
    lats = np.linspace(30.0, 40.0, 11)
    lons = np.linspace(0.0, 10.0, 11)
    lat_grid = np.broadcast_to(lats[:, None], (11, 11)).astype(float)
    k = 0.5  # m/s per degree latitude
    u = k * lat_grid
    v = np.zeros_like(u)

    vorticity, divergence = compute_real_vorticity_divergence(u, v, lats, lons)

    dlat_step_deg = lats[1] - lats[0]
    dy = _EARTH_RADIUS_M * np.radians(dlat_step_deg)
    expected_du_dy = k * dlat_step_deg / dy  # central diff of a linear function is exact
    expected_vorticity = -expected_du_dy  # zeta = dv/dx - du/dy, dv/dx = 0 (v is 0 everywhere)
    expected_divergence = 0.0  # delta = du/dx + dv/dy; du/dx = 0 (u constant along each row), dv/dy = 0

    # Interior points only - np.gradient's one-sided edge differences
    # are real but not what this simple hand-derivation assumes.
    assert np.allclose(divergence[1:-1, 1:-1], expected_divergence, atol=1e-12)
    assert np.allclose(vorticity[1:-1, 1:-1], expected_vorticity, rtol=1e-6)


def test_vorticity_divergence_are_zero_for_uniform_flow():
    """A real, trivial sanity case: perfectly uniform wind has no real
    shear anywhere - both diagnostics must be exactly 0 (well within
    the interior, away from edge effects)."""
    lats = np.linspace(20.0, 30.0, 9)
    lons = np.linspace(-5.0, 5.0, 9)
    u = np.full((9, 9), 12.0)
    v = np.full((9, 9), -4.0)

    vorticity, divergence = compute_real_vorticity_divergence(u, v, lats, lons)

    assert np.allclose(vorticity[1:-1, 1:-1], 0.0, atol=1e-15)
    assert np.allclose(divergence[1:-1, 1:-1], 0.0, atol=1e-15)


def test_pole_rows_are_honestly_nan_not_a_huge_finite_blowup():
    """Real regression guard for a real bug found while smoke-testing
    against an actual solver grid (EarthGrid genuinely spans the full
    -90..90 pole-to-pole): `1/0` in numpy is +-inf, not NaN - a
    nonzero real gradient divided by an exactly-zero real dx_per_row
    at the pole row produced a real but absurd ~1e10 s^-1 value
    instead of the honestly-disclosed NaN this module's own docstring
    already promised. Interior rows must stay real and finite."""
    lats = np.linspace(-90.0, 90.0, 13)
    lons = np.linspace(-180.0, 180.0, 13)
    rng = np.random.default_rng(1)
    u = rng.uniform(-15.0, 15.0, size=(13, 13))
    v = rng.uniform(-15.0, 15.0, size=(13, 13))

    vorticity, divergence = compute_real_vorticity_divergence(u, v, lats, lons)

    assert not np.isfinite(vorticity[0]).any()  # real, honest NaN at the south pole row
    assert not np.isfinite(vorticity[-1]).any()  # real, honest NaN at the north pole row
    assert not np.isfinite(divergence[0]).any()
    assert not np.isfinite(divergence[-1]).any()
    # Interior rows (away from the real singularity) must stay real,
    # finite, and physically reasonable - never absurdly large.
    assert np.all(np.isfinite(vorticity[1:-1]))
    assert np.all(np.abs(vorticity[1:-1]) < 1.0)  # s^-1 - real synoptic-scale values are ~1e-4, not ~1e10
    assert np.all(np.isfinite(divergence[1:-1]))
    assert np.all(np.abs(divergence[1:-1]) < 1.0)


def test_vorticity_divergence_reuse_the_real_formula_classes_directly():
    """Cross-check discipline: pick one real interior grid point,
    independently recompute its own real du/dx, du/dy, dv/dx, dv/dy via
    the exact same np.gradient()/real spacing this module uses, and
    confirm the function's own output matches
    VorticityCalculator.compute_relative_vorticity()/Divergence.calculate()
    called directly on those - proving no independent/duplicated
    formula was written."""
    rng = np.random.default_rng(0)
    lats = np.linspace(10.0, 20.0, 7)
    lons = np.linspace(0.0, 10.0, 7)
    u = rng.uniform(-15.0, 15.0, size=(7, 7))
    v = rng.uniform(-15.0, 15.0, size=(7, 7))

    vorticity, divergence = compute_real_vorticity_divergence(u, v, lats, lons)

    dy, dx_per_row = real_grid_spacing_m(lats, lons)
    du_dy_full = np.gradient(u, axis=0) / dy
    dv_dy_full = np.gradient(v, axis=0) / dy
    du_dx_full = np.gradient(u, axis=1) / dx_per_row[:, None]
    dv_dx_full = np.gradient(v, axis=1) / dx_per_row[:, None]

    i, j = 3, 3
    expected_vorticity = VorticityCalculator.compute_relative_vorticity(dv_dx_full[i, j], du_dy_full[i, j])
    expected_divergence = Divergence.calculate(du_dx_full[i, j], dv_dy_full[i, j])

    assert vorticity[i, j] == expected_vorticity
    assert divergence[i, j] == expected_divergence
