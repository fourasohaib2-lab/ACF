"""
Tests for acf.awci.workstation_fields.compute_real_terrain_field() -
the real terrain elevation + mountain-wave Froude number pipeline
backing the AWCI-free ACF Scientific Workstation's Terrain Lab (added
2026-09-04, closing the last remaining planned module).
"""

from __future__ import annotations

import numpy as np
import pytest

from acf.awci.orographic_froude import compute_real_mountain_wave_froude_number_at_point
from acf.awci.terrain_elevation import interpolate_real_terrain_elevation
from acf.awci.workstation_fields import compute_real_near_surface_static_stability_at_point, compute_real_terrain_field
from acf.science.constants import G, RD
from acf.science.cyclones import BruntVaisalaFrequency
from acf.science.potential_temperature import PotentialTemperature


def _build_volume(n_lat: int, n_lon: int, lat_start: float = 20.0, lon_start: float = 70.0):
    """A real, hand-shaped 2-level profile (only the 2 lowest levels
    matter to this function) centred near the Himalaya, so at least
    some real points have real, positive terrain."""
    n_levels = 2
    lats = np.linspace(lat_start, lat_start + 10.0, n_lat)
    lons = np.linspace(lon_start, lon_start + 20.0, n_lon)

    t_profile = np.array([295.0, 288.0])  # real, stable near-surface lapse
    p_profile = np.array([1000.0, 900.0])
    temperature_volume = np.broadcast_to(t_profile[:, None, None], (n_levels, n_lat, n_lon)).copy()
    pressure_volume_hpa = np.broadcast_to(p_profile[:, None, None], (n_levels, n_lat, n_lon)).copy()
    wind_speed_volume = np.full((n_levels, n_lat, n_lon), 15.0)
    return temperature_volume, pressure_volume_hpa, wind_speed_volume, lats, lons


def test_terrain_field_elevation_matches_the_real_interpolation_function_directly():
    """Cross-check discipline: elevation must equal an independent,
    direct call to interpolate_real_terrain_elevation() - never a
    separately re-derived value."""
    temperature_volume, pressure_volume_hpa, wind_speed_volume, lats, lons = _build_volume(4, 5)

    result = compute_real_terrain_field(temperature_volume, pressure_volume_hpa, wind_speed_volume, lats, lons)

    expected_elevation = interpolate_real_terrain_elevation(lats, lons)
    assert np.array_equal(result["elevation_m"], expected_elevation)
    assert not np.isnan(result["elevation_m"]).any()  # real, global dataset - never NaN


def test_terrain_field_brunt_vaisala_and_froude_match_the_real_formulas_directly():
    """Cross-check discipline: every real grid cell's N and Froude
    number must equal an independent, direct call to each real
    underlying formula on that exact real column."""
    n_lat, n_lon = 4, 5
    temperature_volume, pressure_volume_hpa, wind_speed_volume, lats, lons = _build_volume(n_lat, n_lon)

    result = compute_real_terrain_field(temperature_volume, pressure_volume_hpa, wind_speed_volume, lats, lons)

    theta0 = PotentialTemperature.calculate(295.0, 1000.0)
    theta1 = PotentialTemperature.calculate(288.0, 900.0)
    # Same real hypsometric-equation formula compute_real_terrain_field()
    # itself uses (see that function's own docstring) - not MetPy's
    # thickness_hydrostatic() directly, which agrees with it only to
    # within ~0.02 m (an independently-real but not bit-identical
    # computation of the same physics).
    dz = (RD / G) * ((295.0 + 288.0) / 2.0) * np.log(1000.0 / 900.0)
    dtheta_dz = (theta1 - theta0) / dz
    expected_n = BruntVaisalaFrequency.calculate(theta0, dtheta_dz)

    assert np.allclose(result["brunt_vaisala_n_s1"], expected_n)
    assert expected_n > 0.0  # a real, stable profile - sanity-check the test fixture itself

    for i in range(n_lat):
        for j in range(n_lon):
            elevation = result["elevation_m"][i, j]
            if elevation <= 0.0:
                assert np.isnan(result["froude_number"][i, j])
                continue
            expected = compute_real_mountain_wave_froude_number_at_point(15.0, expected_n, float(elevation))
            if expected["is_real_data"]:
                assert result["froude_number"][i, j] == expected["froude_number"]
            else:
                assert np.isnan(result["froude_number"][i, j])


def test_terrain_field_is_honestly_nan_over_a_real_ocean_point():
    """A genuinely below-sea-level point has no real terrain to block
    flow - froude_number must be honestly NaN there, never a
    fabricated value. elevation_m and brunt_vaisala_n_s1 stay real
    (they don't depend on there being positive terrain)."""
    n_levels = 2
    lats = np.array([0.0])
    lons = np.array([-30.0])  # real mid-Atlantic - genuinely below sea level
    temperature_volume = np.array([[[295.0]], [[288.0]]])
    pressure_volume_hpa = np.array([[[1000.0]], [[900.0]]])
    wind_speed_volume = np.full((n_levels, 1, 1), 15.0)

    result = compute_real_terrain_field(temperature_volume, pressure_volume_hpa, wind_speed_volume, lats, lons)

    assert result["elevation_m"][0, 0] < 0.0
    assert not np.isnan(result["brunt_vaisala_n_s1"][0, 0])
    assert np.isnan(result["froude_number"][0, 0])


def test_terrain_field_is_honestly_nan_for_a_genuinely_neutral_profile():
    """A genuinely neutral (isothermal-theta) profile has no real
    static stability (N=0) - froude_number must be honestly NaN there
    even over real, positive terrain, matching BruntVaisalaFrequency's
    own honest N=0 convention."""
    n_levels = 2
    lats = np.array([28.0])
    lons = np.array([84.0])  # real, high terrain (near the Himalaya)
    # Same potential temperature at both levels - dtheta/dz = 0, a
    # genuinely neutral profile. theta = T*(P0/P)^(R/Cp), so T at
    # 900 hPa matching theta=295K at the 1000 hPa (=P0) reference
    # level is T = 295 * (900/1000)^(R/Cp).
    t_level_1 = 295.0 * (900.0 / 1000.0) ** PotentialTemperature.RD_CP
    temperature_volume = np.array([[[295.0]], [[t_level_1]]])
    pressure_volume_hpa = np.array([[[1000.0]], [[900.0]]])
    wind_speed_volume = np.full((n_levels, 1, 1), 15.0)

    result = compute_real_terrain_field(temperature_volume, pressure_volume_hpa, wind_speed_volume, lats, lons)

    assert result["elevation_m"][0, 0] > 0.0
    assert result["brunt_vaisala_n_s1"][0, 0] == 0.0
    assert np.isnan(result["froude_number"][0, 0])


def test_terrain_field_runs_at_full_native_resolution_no_stride():
    """Unlike CAPE/CIN's real MetPy parcel ascent, this pipeline is
    cheap enough to run at the solver's own full grid - a real,
    disclosed design choice (see the function's own docstring) -
    proven here by checking the returned lats/lons are exactly the
    input ones, not a coarser strided subset."""
    temperature_volume, pressure_volume_hpa, wind_speed_volume, lats, lons = _build_volume(6, 7)

    result = compute_real_terrain_field(temperature_volume, pressure_volume_hpa, wind_speed_volume, lats, lons)

    assert np.array_equal(result["lats"], lats)
    assert np.array_equal(result["lons"], lons)
    assert result["elevation_m"].shape == (6, 7)


def test_static_stability_at_point_matches_the_real_grid_function_at_the_same_point():
    """Cross-check discipline: the real, scalar per-point function must
    agree exactly with compute_real_terrain_field()'s own vectorized N
    at the same real point - same formula, two real implementations
    kept for a real, disclosed performance reason (see the point
    function's own docstring), never allowed to silently drift apart."""
    temperature_volume, pressure_volume_hpa, wind_speed_volume, lats, lons = _build_volume(4, 5)

    grid_result = compute_real_terrain_field(temperature_volume, pressure_volume_hpa, wind_speed_volume, lats, lons)

    for i in range(4):
        for j in range(5):
            point_n = compute_real_near_surface_static_stability_at_point(
                float(temperature_volume[0, i, j]), float(temperature_volume[1, i, j]),
                float(pressure_volume_hpa[0, i, j]), float(pressure_volume_hpa[1, i, j]),
            )
            assert point_n == pytest.approx(float(grid_result["brunt_vaisala_n_s1"][i, j]))


def test_static_stability_at_point_is_zero_for_a_real_neutral_profile():
    """Same real neutral-profile construction as
    test_terrain_field_reports_a_real_neutral_stability_honestly above."""
    t_level_1 = 295.0 * (900.0 / 1000.0) ** PotentialTemperature.RD_CP

    n = compute_real_near_surface_static_stability_at_point(295.0, t_level_1, 1000.0, 900.0)

    assert n == 0.0


def test_static_stability_at_point_is_honestly_none_for_a_degenerate_profile():
    """Identical pressure at both real levels - a genuinely degenerate
    height spacing (dz undefined) - must be None, never a fabricated
    number or a crash."""
    n = compute_real_near_surface_static_stability_at_point(295.0, 288.0, 1000.0, 1000.0)

    assert n is None
