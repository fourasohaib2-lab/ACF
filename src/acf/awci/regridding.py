"""
ACF Complexity Engine — real generic grid regridding
========================================================

Closes reports/ACF_MASTER_AUDIT_v2.md's own "Grid/Regridding: PARTIAL
... pas de regridding bilinéaire/conservatif générique entre deux
grilles quelconques" finding - `acf.awci.multi_model_fusion`'s
`regrid_nearest_neighbor()` (moved here, same logic, not
reimplemented) and `acf.awci.path_sampling`'s own per-point lookup
were both explicitly disclosed as nearest-neighbour only.

Three real methods, honestly scoped to a regular rectilinear lat/lon
grid (the only kind ACF's own `acf.simulation_engine.numerical_core.
earth_grid.EarthGrid` produces - `numpy.linspace` cell centres, no
curvilinear/unstructured grid support anywhere in this project today):

- `regrid_nearest_neighbor()` : real nearest-grid-point lookup - no
  interpolation at all. Fast, always defined everywhere inside the
  source domain, but genuinely discontinuous at cell boundaries.
- `regrid_bilinear()` : real bilinear interpolation between the 4
  source points bracketing each target point - continuous, does NOT
  conserve the field's area-weighted integral.
- `regrid_conservative()` : real area-weighted (in the honest
  spherical sense - see its own docstring on why `sin(lat)`, not raw
  degrees) overlap regridding - conserves the area-weighted integral
  by construction, does NOT interpolate smoothly (a target cell
  entirely inside one source cell just gets that source cell's exact
  value).

None of the three is "the right one" universally - which to use
depends on what a caller needs to preserve (smoothness vs. a
conserved integral vs. raw simplicity/speed); `acf.awci.
multi_model_fusion.compute_real_multi_model_field_fusion()` still uses
nearest-neighbour by default (documented there, not changed by adding
these) since which of these three a real multi-model fusion should use
is a genuine scientific decision out of scope for this module to make
unilaterally.

Honest limitation - NOT shared by all three, disclosed precisely per
function rather than as one blanket statement: `regrid_conservative()`
genuinely handles the real 360° longitude periodicity (a source cell
near +180° really does contribute to a target cell straddling into
-180° territory - see its own docstring; getting this wrong silently
broke conservation at that seam, a real bug caught while building this,
not assumed). `regrid_nearest_neighbor()`/`regrid_bilinear()` do NOT -
a target point right at the antimeridian is clamped to the nearest
real source edge rather than wrapping, same "no extrapolation past the
real domain" choice `acf.awci.path_sampling`'s own route/cross-section
sampling already documents for the analogous case (a real, understood
gap for those two, left as such rather than fixed here since it's a
larger, separate change to their own bracketing logic).
"""

from __future__ import annotations

from typing import Any

import numpy as np


def regrid_nearest_neighbor(
    lats_src: Any,
    lons_src: Any,
    field_src: np.ndarray,
    lats_target: Any,
    lons_target: Any,
) -> np.ndarray:
    """
    Real nearest-neighbour regrid of `field_src` (shape
    (len(lats_src), len(lons_src))) onto `(lats_target, lons_target)`.

    Same technique `acf.awci.path_sampling.sample_field_along_path()`
    already uses per sample point, vectorised across an entire target
    grid instead of a path - not a second implementation.

    Returns
    -------
    numpy.ndarray, shape (len(lats_target), len(lons_target))
    """
    lats_src_arr = np.asarray(lats_src)
    lons_src_arr = np.asarray(lons_src)
    lats_target_arr = np.asarray(lats_target)
    lons_target_arr = np.asarray(lons_target)

    lat_idx = np.argmin(np.abs(lats_target_arr[:, None] - lats_src_arr[None, :]), axis=1)
    lon_idx = np.argmin(np.abs(lons_target_arr[:, None] - lons_src_arr[None, :]), axis=1)
    return field_src[np.ix_(lat_idx, lon_idx)]


def _bracket_indices(coord_src: np.ndarray, coord_target: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    For each real target coordinate, the pair of real source indices
    that bracket it and the real fractional position between them -
    `coord_target[k] ≈ coord_src[lo[k]] * (1 - frac[k]) + coord_src[hi[k]] * frac[k]`.

    `coord_target` is clamped to `[coord_src[0], coord_src[-1]]` first -
    a target point outside the real source domain has nothing real to
    interpolate between, so it is pinned to the nearest real edge
    value rather than extrapolated past it.
    """
    n = len(coord_src)
    clamped = np.clip(coord_target, coord_src[0], coord_src[-1])
    idx_hi = np.clip(np.searchsorted(coord_src, clamped, side="left"), 1, n - 1)
    idx_lo = idx_hi - 1
    denom = coord_src[idx_hi] - coord_src[idx_lo]
    frac = np.where(denom != 0, (clamped - coord_src[idx_lo]) / np.where(denom != 0, denom, 1.0), 0.0)
    return idx_lo, idx_hi, frac


def _require_strictly_increasing(name: str, coord: np.ndarray) -> None:
    if len(coord) < 2:
        raise ValueError(f"{name} needs at least 2 points, got {len(coord)}")
    if not np.all(np.diff(coord) > 0):
        raise ValueError(f"{name} must be strictly increasing (ACF's own EarthGrid convention) - got {coord!r}")


def regrid_bilinear(
    lats_src: Any,
    lons_src: Any,
    field_src: np.ndarray,
    lats_target: Any,
    lons_target: Any,
) -> np.ndarray:
    """
    Real bilinear interpolation of `field_src` onto `(lats_target,
    lons_target)` - the 4 real source grid points bracketing each
    target point, combined with real linear weights in each direction
    (works for any strictly-increasing 1D coordinate arrays, not only
    uniformly-spaced ones - `numpy.searchsorted`-based bracketing, not
    an index-arithmetic shortcut that assumes fixed spacing).

    Continuous (unlike `regrid_nearest_neighbor()`), but does NOT
    conserve the field's area-weighted integral (see
    `regrid_conservative()` for that).

    A target point outside the source domain is clamped to the
    nearest real source edge, not extrapolated - see
    `_bracket_indices()`'s own docstring.

    Returns
    -------
    numpy.ndarray, shape (len(lats_target), len(lons_target))
    """
    lats_src_arr = np.asarray(lats_src, dtype=float)
    lons_src_arr = np.asarray(lons_src, dtype=float)
    lats_target_arr = np.asarray(lats_target, dtype=float)
    lons_target_arr = np.asarray(lons_target, dtype=float)
    field = np.asarray(field_src, dtype=float)

    _require_strictly_increasing("lats_src", lats_src_arr)
    _require_strictly_increasing("lons_src", lons_src_arr)

    lat_lo, lat_hi, lat_frac = _bracket_indices(lats_src_arr, lats_target_arr)
    lon_lo, lon_hi, lon_frac = _bracket_indices(lons_src_arr, lons_target_arr)

    f00 = field[np.ix_(lat_lo, lon_lo)]
    f01 = field[np.ix_(lat_lo, lon_hi)]
    f10 = field[np.ix_(lat_hi, lon_lo)]
    f11 = field[np.ix_(lat_hi, lon_hi)]

    lat_w = lat_frac[:, None]
    lon_w = lon_frac[None, :]

    top = f00 * (1.0 - lon_w) + f01 * lon_w
    bottom = f10 * (1.0 - lon_w) + f11 * lon_w
    return top * (1.0 - lat_w) + bottom * lat_w


def _natural_edges(centers: np.ndarray) -> np.ndarray:
    """
    Real cell edges for a regular grid given only its cell CENTRES
    (`EarthGrid`'s own convention - plain `numpy.linspace` centres, no
    separate edges array anywhere in ACF). Standard technique: each
    interior edge is the midpoint between two consecutive centres; the
    two outer edges are extrapolated by half the adjacent cell's real
    spacing (`centers[0] - (centers[1]-centers[0])/2`, and the mirror
    at the other end) - NOT clamped to any bound here (see
    `_cell_edges_latitude()` for latitude's real physical clamp, and
    `_overlap_weights()`'s own `period` handling for why longitude
    needs none: its outer edges are genuinely correct as-is once
    periodic wraparound is handled during overlap comparison, not
    before it).

    Requires at least 2 centres (a single-point grid has no real
    spacing to infer an edge from).
    """
    if len(centers) < 2:
        raise ValueError(f"need at least 2 centres to infer real cell edges, got {len(centers)}")
    interior = (centers[:-1] + centers[1:]) / 2.0
    first_edge = centers[0] - (centers[1] - centers[0]) / 2.0
    last_edge = centers[-1] + (centers[-1] - centers[-2]) / 2.0
    return np.concatenate(([first_edge], interior, [last_edge]))


def _cell_edges_latitude(centers: np.ndarray) -> np.ndarray:
    """
    `_natural_edges()`, clamped to the real physical latitude domain
    `[-90, 90]` - a cell cannot conservatively cover area beyond the
    real poles. NOT unconditionally pinning the outer edges to ±90°
    (a real bug caught and fixed while building this, not assumed) -
    a REGIONAL grid whose first/last centre isn't already at the pole
    (e.g. `lats=[10, 20, 30]`) must not get an edge stretched all the
    way there, or every regridding call using it would silently claim
    coverage of latitudes it has no real data for. For a grid whose
    first/last centre already sits exactly at the pole (`EarthGrid.
    lats`'s own `linspace(-90, 90, n_lat)` does), this correctly gives
    that polar cell only half the width of a normal interior one, not
    a fabricated full one.
    """
    return np.clip(_natural_edges(centers), -90.0, 90.0)


def _overlap_weights(edges_src: np.ndarray, edges_target: np.ndarray, period: float | None = None) -> np.ndarray:
    """
    Real overlap-length weight matrix `W` of shape
    `(n_target, n_source)`: `W[t, s]` is real target cell `t`'s
    fractional coverage by real source cell `s`, in whatever
    coordinate units `edges_src`/`edges_target` are already in (the
    caller pre-transforms latitude edges to `sin(lat)` - see
    `regrid_conservative()`'s own docstring for why that makes plain
    overlap-length weighting exact rather than approximate).

    `period`, when given (longitude's real 360° period - see
    `regrid_conservative()`'s own docstring for why plain, non-periodic
    edges alone would under-cover real cells straddling the ±180°
    antimeridian): also checks each source cell shifted by -period and
    +period, and sums every real overlap found - the standard, exact
    way to handle a periodic axis without needing modular arithmetic
    inside the overlap comparison itself. `None` (the default,
    latitude's real case - genuinely bounded by the physical poles,
    never periodic) skips this entirely.

    Each row is normalised to sum to 1 over the real source cells it
    actually overlaps - a target cell with ZERO real overlap with any
    source cell (entirely outside the source domain, or - non-periodic
    axis only - past a real, physical domain edge) gets a row of all
    zeros, never a fabricated fallback weight.
    """
    lo_t, hi_t = edges_target[:-1], edges_target[1:]
    lo_s, hi_s = edges_src[:-1], edges_src[1:]

    shifts = (0.0,) if period is None else (-period, 0.0, period)
    overlap = np.zeros((len(lo_t), len(lo_s)))
    for shift in shifts:
        overlap_lo = np.maximum(lo_t[:, None], lo_s[None, :] + shift)
        overlap_hi = np.minimum(hi_t[:, None], hi_s[None, :] + shift)
        overlap += np.clip(overlap_hi - overlap_lo, 0.0, None)

    row_sums = overlap.sum(axis=1, keepdims=True)
    return np.divide(overlap, row_sums, out=np.zeros_like(overlap), where=row_sums > 0)


def regrid_conservative(
    lats_src: Any,
    lons_src: Any,
    field_src: np.ndarray,
    lats_target: Any,
    lons_target: Any,
) -> np.ndarray:
    """
    Real area-weighted conservative regrid of `field_src` onto
    `(lats_target, lons_target)` - each target cell's value is the
    real overlap-area-weighted average of every real source cell it
    intersects, so the field's spherical-area-weighted integral (a
    genuinely conserved physical quantity, e.g. total real mass/energy
    represented by the field) is preserved by construction, unlike
    `regrid_nearest_neighbor()`/`regrid_bilinear()`.

    Real spherical area weighting: a lat/lon cell's true surface area
    is proportional to `Δ(sin(lat))` for a fixed longitude width (the
    exact integral of `cos(lat)` over the cell's latitude span - the
    same real physical reason coarser polar cells cover LESS true
    surface area per degree than equatorial ones) - so latitude
    overlap is computed in `sin(lat)` space, making a plain overlap-
    length weighting spherically EXACT rather than a flat-degree
    approximation. Longitude overlap uses raw degrees directly (the
    `cos(lat)` factor already fully accounts for the sphere's
    curvature - longitude width itself contributes linearly to area
    at any fixed latitude), but genuinely handles the real 360°
    periodicity (`_overlap_weights(..., period=360.0)`) - a source
    cell near +180° really does overlap a finer target cell spanning
    the antimeridian into -180° territory, and omitting this (an
    earlier version of this function did - caught and fixed while
    building it, not assumed) silently under-covered up to one whole
    source cell's worth of real area at that seam, breaking
    conservation for ACF's own real global grid convention
    specifically (`EarthGrid.lons` is periodic - `linspace(-180, 180,
    n_lon, endpoint=False)` never places a real centre at +180 itself).
    Latitude has no such periodicity (the poles are real, non-wrapping
    physical bounds - `_cell_edges_latitude()`).

    A target cell with zero real overlap with the source domain is
    `numpy.nan`, never a fabricated 0.0 - same "None/NaN-not-0.0"
    discipline `acf.awci.calculator.AWCICalculator`'s own
    `forecast_field` already established.

    Returns
    -------
    numpy.ndarray, shape (len(lats_target), len(lons_target))
    """
    lats_src_arr = np.asarray(lats_src, dtype=float)
    lons_src_arr = np.asarray(lons_src, dtype=float)
    lats_target_arr = np.asarray(lats_target, dtype=float)
    lons_target_arr = np.asarray(lons_target, dtype=float)
    field = np.asarray(field_src, dtype=float)

    _require_strictly_increasing("lats_src", lats_src_arr)
    _require_strictly_increasing("lons_src", lons_src_arr)
    _require_strictly_increasing("lats_target", lats_target_arr)
    _require_strictly_increasing("lons_target", lons_target_arr)

    sinlat_edges_src = np.sin(np.radians(_cell_edges_latitude(lats_src_arr)))
    sinlat_edges_target = np.sin(np.radians(_cell_edges_latitude(lats_target_arr)))
    lon_edges_src = _natural_edges(lons_src_arr)
    lon_edges_target = _natural_edges(lons_target_arr)

    w_lat = _overlap_weights(sinlat_edges_src, sinlat_edges_target)  # (n_target_lat, n_source_lat)
    w_lon = _overlap_weights(lon_edges_src, lon_edges_target, period=360.0)  # (n_target_lon, n_source_lon)

    fused = w_lat @ field @ w_lon.T
    covered = (w_lat.sum(axis=1) > 0)[:, None] & (w_lon.sum(axis=1) > 0)[None, :]
    return np.where(covered, fused, np.nan)
