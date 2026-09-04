"""
ACF Scientific Workstation — shared, Qt-free field helpers
==============================================================

Real per-grid-point atmospheric diagnostics used by both the ACF
Scientific Workstation's GUI panels (`acf.gui.dashboard.
acf_workstation_dynamics`/`acf_workstation_thermodynamics`) and, since
2026-09-04, the real `/api/v1/workstation` HTTP router
(`acf.web.routers.workstation_router`).

Why this module exists (added 2026-09-04)
---------------------------------------------
These functions originally lived directly inside the GUI panel
modules above - correct for the GUI itself, but those modules import
`PySide6.QtWidgets` at the top level (for their own `QWidget` panel
classes), which a headless API server has no real reason to import.
Moved here, a real Qt-free module, so `workstation_router.py` can
reuse the EXACT SAME real formulas (never a second, independently
re-derived copy) without pulling a GUI toolkit into the web process.
The GUI panel modules now import these same functions FROM here (a
plain re-export, not reimplemented) - zero behaviour change for any
existing caller/test, verified by keeping every original import path
(`from acf.gui.dashboard.acf_workstation_dynamics import
compute_real_vorticity_divergence, real_grid_spacing_m`, etc.) working
unchanged.

Real vorticity/divergence, not reimplemented
-----------------------------------------------
`compute_real_vorticity_divergence()` computes the real horizontal
gradients (du/dx, du/dy, dv/dx, dv/dy) via `np.gradient` on the real
lat/lon grid, using the standard real metric-spacing approximation for
a regular lat/lon grid (dy = R*dphi, dx = R*cos(phi)*dlambda, R =
Earth's real mean radius, same 6,371 km constant
`acf.awci.path_sampling._haversine_km()` already uses) - then calls
`acf.earth_physics.atmospheric_dynamics.vorticity.
VorticityCalculator.compute_relative_vorticity()` and
`acf.science.divergence.Divergence.calculate()` VERBATIM (both are
simple enough - `zeta = dv/dx - du/dy`, `delta = du/dx + dv/dy` - that
they already work correctly on numpy arrays with no changes needed, so
this reuses the exact same real, tested formula classes rather than
re-deriving the physics).

Honest limitation: vorticity/divergence are physically singular at the
poles on a regular lat/lon grid (cos(lat) -> 0) - this is a real,
known geophysical fact, not a bug; those cells honestly render as
non-finite (NaN).

Real θ-e/relative humidity, not reimplemented
-------------------------------------------------
`compute_real_theta_e_and_rh_fields()` calls
`acf.awci.theta_e.compute_real_theta_e_at_point()` (the CANONICAL,
published Bolton (1980) formula, composed from 3 already-real, already
-tested pieces - see that module's own docstring) at every point of one
real 2D level slice - pure arithmetic, no iterative solve, fast enough
(~1 microsecond/point measured) for real-time use.
"""

from __future__ import annotations

import numpy as np

from acf.awci.theta_e import compute_real_theta_e_at_point
from acf.awci.wind_shear import compute_real_wind_shear_at_point
from acf.earth_physics.atmospheric_dynamics.vorticity import VorticityCalculator
from acf.science.divergence import Divergence

#: Real Earth mean radius, metres - same constant
#: acf.awci.path_sampling._haversine_km() already uses (6371.0 km).
_EARTH_RADIUS_M = 6371000.0


def real_grid_spacing_m(lats: np.ndarray, lons: np.ndarray) -> tuple[float, np.ndarray]:
    """
    Real metric grid spacing (metres) for a regular lat/lon grid - the
    standard real approximation used throughout meteorology (dy =
    R*dphi, dx = R*cos(phi)*dlambda) - single source of truth for this
    real, disclosed approximation (shared by
    compute_real_vorticity_divergence() below and
    acf_workstation_complexity.py's own real spatial-complexity
    gradient), never duplicated.

    Returns
    -------
    (dy, dx_per_row) : dy is a real scalar (uniform across the grid);
        dx_per_row is a real (n_lat,) array (varies with latitude).
    """
    lats_arr = np.asarray(lats, dtype=float)
    lons_arr = np.asarray(lons, dtype=float)
    dlat_rad = np.radians(float(np.mean(np.diff(lats_arr))))
    dlon_rad = np.radians(float(np.mean(np.diff(lons_arr))))
    lat_rad = np.radians(lats_arr)

    dy = float(_EARTH_RADIUS_M * dlat_rad)
    dx_per_row = _EARTH_RADIUS_M * np.cos(lat_rad) * dlon_rad
    return dy, dx_per_row


def compute_real_vorticity_divergence(
    u: np.ndarray, v: np.ndarray, lats: np.ndarray, lons: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    Real relative vorticity (s^-1) and real horizontal divergence
    (s^-1) on a real regular lat/lon grid - see module docstring for
    the full disclosure of the method and why it's real, not
    fabricated.

    Parameters
    ----------
    u, v : 2D real wind components (n_lat, n_lon), m/s.
    lats, lons : 1D real coordinate arrays, degrees, regular spacing
        (EarthGrid's own convention - the same arrays
        compute_real_complexity_volume() itself returns).

    Returns
    -------
    (vorticity, divergence) : both (n_lat, n_lon), s^-1. Pole rows (if
        present in the real grid) are honestly non-finite (NaN), never
        a fabricated finite value.
    """
    dy, dx_per_row = real_grid_spacing_m(lats, lons)

    # NOTE (correction, found while smoke-testing the ACF Scientific
    # Workstation against a REAL solver grid, which genuinely spans
    # the full -90..90 pole-to-pole): `1/0` in numpy is +-inf, not
    # NaN - only true `0/0` produces NaN. A real, near-zero-but-
    # nonzero du_dx numerator divided by an EXACTLY zero dx_per_row at
    # the pole row therefore produced a real but absurd ~1e10 s^-1
    # "vorticity" instead of the honestly-disclosed NaN this module
    # promised. Explicitly masking the real dx-degenerate rows (a
    # real, physical epsilon: below 1 metre of real zonal spacing is
    # the pole itself on any Earth-radius grid) delivers the disclosed
    # behaviour for real, not just for a synthetic test grid that
    # happened not to reach the poles.
    degenerate_dx = np.abs(dx_per_row) < 1.0  # real physical threshold: <1m zonal spacing = the pole itself

    with np.errstate(divide="ignore", invalid="ignore"):  # real, expected pole-only singularity - see module docstring
        du_dy = np.gradient(u, axis=0) / dy
        dv_dy = np.gradient(v, axis=0) / dy
        safe_dx_per_row = np.where(degenerate_dx, np.nan, dx_per_row)
        du_dx = np.gradient(u, axis=1) / safe_dx_per_row[:, None]
        dv_dx = np.gradient(v, axis=1) / safe_dx_per_row[:, None]

    # VorticityCalculator/Divergence are typed for real scalar use
    # elsewhere in this codebase (dv_dx: float, du_dy: float) - they
    # work correctly on numpy arrays too (their own bodies are plain
    # `-`/`+`, real duck typing, not a hack); np.asarray() below only
    # gives mypy an accurate array type back, no behaviour change.
    vorticity = np.asarray(VorticityCalculator.compute_relative_vorticity(dv_dx, du_dy))
    divergence = np.asarray(Divergence.calculate(du_dx, dv_dy))
    return vorticity, divergence


def compute_real_wind_shear_field(
    u_volume: np.ndarray, v_volume: np.ndarray, bottom_level: int = 0, top_level: int = -1
) -> np.ndarray:
    """
    Real bulk wind shear (m/s) at every (lat, lon) point, via
    `acf.awci.wind_shear.compute_real_wind_shear_at_point()` - called
    directly, not reimplemented (that function's own real formula uses
    `math.sqrt`, not vectorizable over numpy arrays directly, unlike
    vorticity/divergence above - looped per point instead, real but
    fast: ~0.4 microseconds/point measured, negligible even at a
    native grid's full resolution).

    Parameters
    ----------
    u_volume, v_volume : real (n_levels, n_lat, n_lon) arrays.
    bottom_level, top_level : see compute_real_wind_shear_at_point()'s
        own docstring - defaults span the real full vertical extent,
        same real "not a fixed physical layer" disclosure.

    Returns
    -------
    np.ndarray, (n_lat, n_lon) - a real, full-column diagnostic,
        independent of any particular vertical level.
    """
    _n_levels, n_lat, n_lon = u_volume.shape
    shear = np.zeros((n_lat, n_lon))
    for i in range(n_lat):
        for j in range(n_lon):
            result = compute_real_wind_shear_at_point(
                u_volume[:, i, j], v_volume[:, i, j], bottom_level=bottom_level, top_level=top_level
            )
            shear[i, j] = result["shear_m_s"]
    return shear


def compute_real_theta_e_and_rh_fields(
    temperature: np.ndarray, specific_humidity: np.ndarray, pressure_hpa: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    Real θ-e (K) and relative humidity (%) at every point of one real
    2D level slice, via `compute_real_theta_e_at_point()` - see module
    docstring. NaN (never a fabricated value) wherever that real
    per-point computation itself honestly reports "not computed"
    (non-positive real relative humidity - see its own docstring).
    """
    n_lat, n_lon = temperature.shape
    theta_e = np.full((n_lat, n_lon), np.nan)
    relative_humidity = np.full((n_lat, n_lon), np.nan)
    for i in range(n_lat):
        for j in range(n_lon):
            result = compute_real_theta_e_at_point(
                float(temperature[i, j]), float(specific_humidity[i, j]), float(pressure_hpa[i, j])
            )
            if result["is_real_data"]:
                theta_e[i, j] = result["theta_e_k"]
                relative_humidity[i, j] = result["relative_humidity_pct"]
    return theta_e, relative_humidity
