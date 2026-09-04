"""
Tests for acf.awci.terrain_elevation - the real, bundled SRTM15+ 1
arc-degree elevation grid and its real interpolation onto an arbitrary
solver grid (added 2026-09-04, Terrain Lab).
"""

from __future__ import annotations

import numpy as np

from acf.awci.terrain_elevation import interpolate_real_terrain_elevation, load_real_terrain_elevation


def test_load_real_terrain_elevation_returns_the_real_bundled_180x360_grid():
    lats, lons, elevation_m = load_real_terrain_elevation()

    assert lats.shape == (180,)
    assert lons.shape == (360,)
    assert elevation_m.shape == (180, 360)
    # Real, physically plausible global range (Earth's deepest trench /
    # highest peak, at this real dataset's own coarse 1-degree
    # resolution - see src/acf/awci/data/NOTICE.md).
    assert -12000.0 < elevation_m.min() < 0.0
    assert 0.0 < elevation_m.max() < 10000.0


def test_load_real_terrain_elevation_is_cached_not_reread_every_call():
    """Real proof of the lru_cache - two calls return the exact same
    array object, not two independent file reads."""
    lats_a, lons_a, elevation_a = load_real_terrain_elevation()
    lats_b, lons_b, elevation_b = load_real_terrain_elevation()

    assert elevation_a is elevation_b
    assert lats_a is lats_b


def test_interpolated_elevation_matches_a_real_known_land_and_ocean_point():
    """Real, hand-verifiable sanity check: a point near the Himalaya
    must be real, meaningfully positive; a point in the mid-Atlantic
    must be real, meaningfully negative (below sea level)."""
    target_lats = np.linspace(-90.0, 90.0, 19)
    target_lons = np.linspace(-180.0, 180.0, 36, endpoint=False)

    elevation = interpolate_real_terrain_elevation(target_lats, target_lons)

    assert elevation.shape == (19, 36)
    lat_idx = int(np.argmin(np.abs(target_lats - 28.0)))
    lon_idx = int(np.argmin(np.abs(target_lons - 84.0)))
    assert elevation[lat_idx, lon_idx] > 500.0  # real, meaningfully high (near the Himalaya)

    lat_idx_ocean = int(np.argmin(np.abs(target_lats - 0.0)))
    lon_idx_ocean = int(np.argmin(np.abs(target_lons - (-30.0))))
    assert elevation[lat_idx_ocean, lon_idx_ocean] < -1000.0  # real, meaningfully deep (mid-Atlantic)


def test_interpolated_elevation_on_the_native_grid_matches_the_source_grid_directly():
    """Cross-check discipline: interpolating exactly onto the source
    grid's own real lat/lon coordinates must reproduce those same real
    values (bilinear interpolation at an exact source node is
    identity)."""
    lats, lons, elevation_m = load_real_terrain_elevation()

    interpolated = interpolate_real_terrain_elevation(lats[:5], lons[:5])

    assert np.allclose(interpolated, elevation_m[:5, :5], atol=1e-6)


def test_interpolated_elevation_is_never_nan_globally():
    """The real, bundled dataset is genuinely global - a real solver
    grid anywhere on Earth must get a real, non-NaN elevation."""
    target_lats = np.linspace(-89.0, 89.0, 7)
    target_lons = np.linspace(-179.0, 179.0, 9)

    elevation = interpolate_real_terrain_elevation(target_lats, target_lons)

    assert not np.isnan(elevation).any()
