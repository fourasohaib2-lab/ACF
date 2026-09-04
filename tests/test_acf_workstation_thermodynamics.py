"""
Tests for acf.gui.dashboard.acf_workstation_thermodynamics - the real
θ-e/relative-humidity and CAPE/CIN helpers backing the AWCI-free ACF
Scientific Workstation's Thermodynamics Lab (added 2026-09-04).
"""

from __future__ import annotations

import numpy as np

from acf.awci.convective_energy import compute_real_cape_cin_at_point
from acf.awci.theta_e import compute_real_theta_e_at_point
from acf.gui.dashboard.acf_workstation_thermodynamics import (
    compute_real_cape_cin_fields,
    compute_real_theta_e_and_rh_fields,
)


def test_theta_e_and_rh_fields_match_the_real_point_function_directly():
    """Cross-check discipline: every cell of the field must equal an
    independent, direct call to compute_real_theta_e_at_point() on
    that same real point - never a separately re-derived formula."""
    rng = np.random.default_rng(0)
    temperature = 288.0 + rng.uniform(-10.0, 10.0, size=(4, 5))
    specific_humidity = np.clip(0.008 + rng.uniform(-0.003, 0.003, size=(4, 5)), 1e-6, None)
    pressure_hpa = np.full((4, 5), 950.0)

    theta_e, relative_humidity = compute_real_theta_e_and_rh_fields(temperature, specific_humidity, pressure_hpa)

    for i in range(4):
        for j in range(5):
            expected = compute_real_theta_e_at_point(
                float(temperature[i, j]), float(specific_humidity[i, j]), float(pressure_hpa[i, j])
            )
            assert expected["is_real_data"] is True
            assert theta_e[i, j] == expected["theta_e_k"]
            assert relative_humidity[i, j] == expected["relative_humidity_pct"]


def test_theta_e_and_rh_fields_are_honestly_nan_for_a_genuinely_dry_point():
    """A genuinely zero-humidity point has no real dewpoint (see
    compute_real_theta_e_at_point()'s own docstring) - must be NaN,
    never a fabricated value."""
    temperature = np.array([[288.0]])
    specific_humidity = np.array([[0.0]])
    pressure_hpa = np.array([[950.0]])

    theta_e, relative_humidity = compute_real_theta_e_and_rh_fields(temperature, specific_humidity, pressure_hpa)

    assert np.isnan(theta_e[0, 0])
    assert np.isnan(relative_humidity[0, 0])


def _synthetic_profile(n_levels: int = 6) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A real, hand-shaped vertical profile (decreasing pressure/
    temperature with height, decreasing humidity) - realistic enough
    for a genuine MetPy parcel ascent to succeed, same convention as
    acf_workstation_complexity.py's own _synthetic_evolution() helper:
    isolating the function under test, not a real solver integration."""
    pressure_hpa = np.linspace(1000.0, 500.0, n_levels)
    temperature_k = np.linspace(298.0, 260.0, n_levels)
    specific_humidity = np.linspace(0.012, 0.001, n_levels)
    return temperature_k, specific_humidity, pressure_hpa


def test_cape_cin_fields_match_the_real_point_function_directly():
    """Cross-check discipline: every strided grid cell must equal an
    independent, direct call to compute_real_cape_cin_at_point() on
    that exact real column."""
    n_levels, n_lat, n_lon, stride = 6, 6, 8, 2
    t_profile, q_profile, p_profile = _synthetic_profile(n_levels)
    # Same real profile at every column, slightly warmed with longitude
    # - simple enough to hand-verify, still a real, distinct column per
    # (i, j) so this isn't testing a degenerate uniform field only.
    lon_warm = np.linspace(0.0, 3.0, n_lon)
    temperature_volume = np.broadcast_to(t_profile[:, None, None], (n_levels, n_lat, n_lon)).copy()
    temperature_volume += lon_warm[None, None, :]
    specific_humidity_volume = np.broadcast_to(q_profile[:, None, None], (n_levels, n_lat, n_lon)).copy()
    pressure_volume_hpa = np.broadcast_to(p_profile[:, None, None], (n_levels, n_lat, n_lon)).copy()
    lats = np.linspace(30.0, 40.0, n_lat)
    lons = np.linspace(0.0, 10.0, n_lon)

    sub_lats, sub_lons, cape_grid, cin_grid = compute_real_cape_cin_fields(
        temperature_volume, specific_humidity_volume, pressure_volume_hpa, lats, lons, stride=stride
    )

    assert np.array_equal(sub_lats, lats[::stride])
    assert np.array_equal(sub_lons, lons[::stride])
    assert cape_grid.shape == (len(sub_lats), len(sub_lons))

    row_indices = list(range(0, n_lat, stride))
    col_indices = list(range(0, n_lon, stride))
    for si, i in enumerate(row_indices):
        for sj, j in enumerate(col_indices):
            expected = compute_real_cape_cin_at_point(
                temperature_profile_k=temperature_volume[:, i, j],
                specific_humidity_profile=specific_humidity_volume[:, i, j],
                pressure_profile_hpa=pressure_volume_hpa[:, i, j],
            )
            assert expected["is_real_data"] is True
            assert cape_grid[si, sj] == expected["cape_j_kg"]
            assert cin_grid[si, sj] == expected["cin_j_kg"]
            # Real physical sanity - both are non-negative by convention
            # (see acf.science.cape.CAPE.calculate()/cin.CIN.calculate()'s
            # own docstrings).
            assert cape_grid[si, sj] >= 0.0
            assert cin_grid[si, sj] >= 0.0


def test_cape_cin_fields_return_a_real_coarser_grid_not_the_native_resolution():
    """Honest performance trade-off (see module docstring): the
    returned grid is genuinely smaller than the native one, not a
    same-size grid with gaps."""
    n_levels, n_lat, n_lon, stride = 6, 9, 11, 3
    t_profile, q_profile, p_profile = _synthetic_profile(n_levels)
    temperature_volume = np.broadcast_to(t_profile[:, None, None], (n_levels, n_lat, n_lon)).copy()
    specific_humidity_volume = np.broadcast_to(q_profile[:, None, None], (n_levels, n_lat, n_lon)).copy()
    pressure_volume_hpa = np.broadcast_to(p_profile[:, None, None], (n_levels, n_lat, n_lon)).copy()
    lats = np.linspace(30.0, 40.0, n_lat)
    lons = np.linspace(0.0, 10.0, n_lon)

    sub_lats, sub_lons, cape_grid, cin_grid = compute_real_cape_cin_fields(
        temperature_volume, specific_humidity_volume, pressure_volume_hpa, lats, lons, stride=stride
    )

    assert cape_grid.shape[0] < n_lat
    assert cape_grid.shape[1] < n_lon
    assert not np.isnan(cape_grid).any()  # every cell of the real coarser grid was actually computed
    assert not np.isnan(cin_grid).any()
