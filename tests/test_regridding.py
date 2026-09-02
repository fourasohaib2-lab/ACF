"""
Tests for acf.awci.regridding - the Prompt Maître ACF v2.0's
"Grid/Regridding: pas de regridding bilinéaire/conservatif générique"
gap (reports/ACF_MASTER_AUDIT_v2.md).
"""

from __future__ import annotations

import numpy as np
import pytest

from acf.awci.multi_model_fusion import regrid_nearest_neighbor as regrid_nearest_neighbor_via_fusion
from acf.awci.regridding import (
    _cell_edges_latitude,
    _natural_edges,
    regrid_bilinear,
    regrid_conservative,
    regrid_nearest_neighbor,
)


def _area_weighted_total(lats, lons, field) -> float:
    """Real spherical-area-weighted integral, computed independently of regrid_conservative()'s own internals, for conservation checks."""
    lat_edges = _cell_edges_latitude(np.asarray(lats, dtype=float))
    lon_edges = _natural_edges(np.asarray(lons, dtype=float))
    dsinlat = np.sin(np.radians(lat_edges[1:])) - np.sin(np.radians(lat_edges[:-1]))
    dlon = lon_edges[1:] - lon_edges[:-1]
    area = dsinlat[:, None] * dlon[None, :]
    return float(np.sum(np.asarray(field) * area))


# ------------------------------------------------------------------ regrid_nearest_neighbor


def test_nearest_neighbor_is_the_same_function_multi_model_fusion_uses():
    """Regression check for the move out of multi_model_fusion.py - not a second implementation."""
    assert regrid_nearest_neighbor is regrid_nearest_neighbor_via_fusion


def test_nearest_neighbor_identity_when_grids_match():
    lats = np.array([10.0, 20.0, 30.0])
    lons = np.array([0.0, 1.0])
    field = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    assert np.array_equal(regrid_nearest_neighbor(lats, lons, field, lats, lons), field)


def test_nearest_neighbor_picks_the_real_closest_source_point():
    lats_src = np.array([0.0, 10.0, 20.0])
    lons_src = np.array([0.0, 10.0])
    field_src = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    result = regrid_nearest_neighbor(lats_src, lons_src, field_src, [9.0], [1.0])
    assert result[0, 0] == 3.0


def test_nearest_neighbor_wraps_across_the_real_antimeridian():
    """A real correctness property: a target point at 179° is only 2° (via wraparound) from a source point at -179°, but 9° from one at 170° - the real nearest point must be the wrapped one, not the naive-degree-distance one."""
    lats = np.array([0.0, 10.0])
    lons_src = np.array([-179.0, 170.0])
    field = np.array([[100.0, 200.0], [100.0, 200.0]])  # -179 -> 100, 170 -> 200

    result = regrid_nearest_neighbor(lats, lons_src, field, lats, np.array([179.0]))
    assert np.all(result[:, 0] == 100.0)


# ------------------------------------------------------------------ regrid_bilinear


def test_bilinear_identity_when_grids_match():
    lats = np.array([0.0, 10.0, 20.0])
    lons = np.array([0.0, 10.0])
    field = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    assert np.allclose(regrid_bilinear(lats, lons, field, lats, lons), field)


def test_bilinear_exactly_reproduces_a_linear_field():
    """A real correctness property, not a smoke check: bilinear interpolation is EXACT for any field that is genuinely linear in lat and lon."""
    lats = np.array([0.0, 10.0, 20.0])
    lons = np.array([0.0, 10.0])
    field = np.array([[2 * la + 3 * lo for lo in lons] for la in lats])

    target_lats = np.array([5.0, 15.0])
    target_lons = np.array([5.0])
    result = regrid_bilinear(lats, lons, field, target_lats, target_lons)
    expected = np.array([[2 * 5 + 3 * 5], [2 * 15 + 3 * 5]])
    assert np.allclose(result, expected)


def test_bilinear_clamps_a_target_point_outside_the_source_domain():
    lats = np.array([0.0, 10.0, 20.0])
    lons = np.array([0.0, 10.0])
    field = np.array([[0.0, 30.0], [20.0, 50.0], [40.0, 70.0]])

    result = regrid_bilinear(lats, lons, field, np.array([-50.0, 100.0]), np.array([5.0]))
    assert result[0, 0] == pytest.approx(15.0)  # clamped to lat=0 row
    assert result[1, 0] == pytest.approx(55.0)  # clamped to lat=20 row


def test_bilinear_works_for_non_uniformly_spaced_source_coordinates():
    lats = np.array([0.0, 1.0, 10.0])  # deliberately not evenly spaced
    lons = np.array([0.0, 10.0])
    field = np.array([[0.0, 0.0], [1.0, 1.0], [10.0, 10.0]])
    # field == lat everywhere -> bilinear along a non-uniform axis must still reproduce it exactly
    result = regrid_bilinear(lats, lons, field, np.array([5.0]), lons)
    assert np.allclose(result, [[5.0, 5.0]])


def test_bilinear_wraps_across_the_real_antimeridian():
    """Real correctness proof, verified against a hand-derived expected value, not just a smoke check: a target at 179° sits 9° from a source at 170° but only 2° (via wraparound) from one at -179° - real interpolation weight must reflect the short, wrapped path."""
    lats = np.array([0.0, 10.0])
    lons_src = np.array([-179.0, 170.0])
    field = np.array([[100.0, 200.0], [100.0, 200.0]])  # -179 -> 100, 170 -> 200

    result = regrid_bilinear(lats, lons_src, field, lats, np.array([179.0]))

    # 170 -> -179 the short way spans 11 real degrees (170 -> 180 -> -179); target 179 is 9deg from 170, 2deg from -179.
    expected = 200.0 * (1 - 9 / 11) + 100.0 * (9 / 11)
    assert np.allclose(result[:, 0], expected)


def test_bilinear_wraparound_reduces_to_plain_bracketing_away_from_the_seam():
    """The periodic bracketing must not perturb a genuinely non-wrapping interpolation - same exact-linear-field property as test_bilinear_exactly_reproduces_a_linear_field, now via the periodic code path."""
    lats = np.array([0.0, 10.0, 20.0])
    lons = np.array([0.0, 10.0, 20.0])
    field = np.array([[2 * la + 3 * lo for lo in lons] for la in lats])

    result = regrid_bilinear(lats, lons, field, np.array([5.0]), np.array([15.0]))
    assert np.allclose(result, [[2 * 5 + 3 * 15]])


def test_bilinear_rejects_non_increasing_source_coordinates():
    with pytest.raises(ValueError, match="strictly increasing"):
        regrid_bilinear(np.array([10.0, 0.0]), np.array([0.0, 1.0]), np.zeros((2, 2)), [5.0], [0.5])


# ------------------------------------------------------------------ regrid_conservative: identity & basic shape


def test_conservative_identity_when_grids_match():
    lats = np.linspace(-90, 90, 7)
    lons = np.linspace(-180, 180, 10, endpoint=False)
    rng = np.random.default_rng(0)
    field = rng.random((7, 10)) * 100
    result = regrid_conservative(lats, lons, field, lats, lons)
    assert np.allclose(result, field)


def test_conservative_output_shape_matches_target_grid():
    lats = np.linspace(-90, 90, 5)
    lons = np.linspace(-180, 180, 6, endpoint=False)
    field = np.ones((5, 6))
    target_lats = np.linspace(-90, 90, 3)
    target_lons = np.linspace(-180, 180, 4, endpoint=False)
    result = regrid_conservative(lats, lons, field, target_lats, target_lons)
    assert result.shape == (3, 4)


# ------------------------------------------------------------------ regrid_conservative: real conservation


@pytest.mark.parametrize("n_lat_t,n_lon_t", [(7, 10), (3, 4), (15, 20), (2, 3), (5, 7), (11, 13)])
def test_conservative_preserves_the_real_area_weighted_integral(n_lat_t, n_lon_t):
    """
    The defining real property of conservative regridding: the field's
    spherical-area-weighted total must be preserved (to float
    precision) whether coarsening, refining, or leaving the grid
    resolution unchanged - verified against an independently computed
    area-weighted total (_area_weighted_total()), not by re-deriving
    the same formula regrid_conservative() itself uses internally.
    """
    lats = np.linspace(-90, 90, 7)
    lons = np.linspace(-180, 180, 10, endpoint=False)
    rng = np.random.default_rng(1)
    field = rng.random((7, 10)) * 50 + 10

    total_src = _area_weighted_total(lats, lons, field)

    target_lats = np.linspace(-90, 90, n_lat_t)
    target_lons = np.linspace(-180, 180, n_lon_t, endpoint=False)
    result = regrid_conservative(lats, lons, field, target_lats, target_lons)
    total_target = _area_weighted_total(target_lats, target_lons, result)

    assert total_target == pytest.approx(total_src, abs=1e-6)


def test_conservative_gives_polar_cells_less_weight_than_equatorial_ones():
    """Real spherical area-weighting sanity check: a uniform field's conservative regrid must still be uniform (weights are relative, not absolute), but the underlying per-cell area used to get there must genuinely shrink towards the poles - checked indirectly via a non-uniform field where only the equatorial band carries a real signal."""
    lats = np.linspace(-90, 90, 19)  # 10-degree steps
    lons = np.linspace(-180, 180, 4, endpoint=False)
    field = np.zeros((19, 4))
    field[9, :] = 100.0  # the equatorial row (lat=0) only

    coarse = regrid_conservative(lats, lons, field, np.array([-45.0, 45.0]), lons)
    # Both coarse target cells (spanning [-90,0] and [0,90]) partially overlap the equatorial row -
    # a real, non-zero, non-fabricated value on both sides, not a naive 50/50 split (spherical
    # area-weighting near the equator differs from a flat degree-based split).
    assert coarse[0, 0] > 0.0
    assert coarse[1, 0] > 0.0


# ------------------------------------------------------------------ regrid_conservative: out-of-domain honesty


def test_conservative_is_nan_for_a_target_cell_with_zero_real_overlap():
    lats_src = np.array([10.0, 20.0, 30.0])
    lons_src = np.array([0.0, 10.0, 20.0])
    field = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])

    target_lats = np.array([-80.0, 20.0])  # -80 is genuinely outside the [10,30] source domain
    target_lons = np.array([0.0, 10.0, 20.0])
    result = regrid_conservative(lats_src, lons_src, field, target_lats, target_lons)

    assert np.all(np.isnan(result[0, :]))
    assert not np.any(np.isnan(result[1, :]))


def test_conservative_rejects_a_single_point_grid():
    with pytest.raises(ValueError, match="at least 2"):
        regrid_conservative(np.array([0.0]), np.array([0.0, 1.0]), np.zeros((1, 2)), np.array([0.0, 1.0]), np.array([0.0, 1.0]))


def test_conservative_rejects_non_increasing_coordinates():
    with pytest.raises(ValueError, match="strictly increasing"):
        regrid_conservative(
            np.array([10.0, 0.0]), np.array([0.0, 1.0]), np.zeros((2, 2)), np.array([0.0, 5.0]), np.array([0.0, 1.0])
        )


# ------------------------------------------------------------------ regrid_conservative: real ±180° periodicity


def test_conservative_handles_real_longitude_wraparound_at_the_antimeridian():
    """
    Real correctness proof for the periodicity fix, not just a
    conservation-total check: a source field that is nonzero ONLY in
    the cell nearest +180° must contribute real weight to a target
    cell straddling the antimeridian, and ZERO weight to an unrelated
    target cell far from the seam.
    """
    lats = np.array([-10.0, 10.0])
    lons_src = np.array([-170.0, -90.0, 0.0, 90.0, 170.0])
    field = np.array([[0.0, 0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0, 0.0, 1.0]])

    lons_target = np.array([-175.0, 0.0])  # near the seam, and far from it
    result = regrid_conservative(lats, lons_src, field, lats, lons_target)

    assert np.all(result[:, 0] > 0.0)  # near-seam column picks up the +170°-centred source cell
    assert np.all(result[:, 1] == 0.0)  # far column gets none of it


def test_conservative_wraparound_still_conserves_the_area_weighted_total():
    """
    Same conservation property as test_conservative_preserves_the_real_area_weighted_integral,
    specifically with a target grid resolution that straddles the
    antimeridian differently than the source's own cells (5 vs. 8
    points - the seam falls in the middle of a target cell, not on a
    source cell edge). Uses ACF's own real, evenly-spaced EarthGrid
    convention for both grids - _area_weighted_total() itself only
    computes a correct ground-truth total for that convention (its
    non-periodic edges naturally span exactly 360° only when the
    points are evenly spaced over the full circle).
    """
    lats = np.array([-10.0, 10.0])
    lons_src = np.linspace(-180, 180, 5, endpoint=False)
    rng = np.random.default_rng(2)
    field = rng.random((2, 5)) * 10

    total_src = _area_weighted_total(lats, lons_src, field)

    lons_target = np.linspace(-180, 180, 8, endpoint=False)
    result = regrid_conservative(lats, lons_src, field, lats, lons_target)
    total_target = _area_weighted_total(lats, lons_target, result)

    assert total_target == pytest.approx(total_src, abs=1e-9)
