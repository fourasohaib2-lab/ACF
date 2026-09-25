"""
Vectorized kinematics and Ellrod-Knapp (1992) TI2.

VWS = |dV|/dz (dz from real geopotential height gh), DEF = sqrt(DST^2 + DSH^2),
DST = du/dx - dv/dy, DSH = dv/dx + du/dy, CVG = -divergence (IFS field d),
TI2 = VWS * (DEF + CVG)  [s^-2]; categories use CATIndex's x1e7 thresholds 4/8/12.
Horizontal derivatives: centred differences on a regular lat/lon grid with real
metric spacing (spherical Earth, R = 6371 km).
"""

from __future__ import annotations

import numpy as np

EARTH_RADIUS_M = 6371000.0
MIN_DZ_M = 1.0
_CAT_BOUNDS_S2 = (4e-7, 8e-7, 12e-7)


def wind_speed(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    return np.hypot(np.asarray(u, dtype=float), np.asarray(v, dtype=float))


def layer_shear(u: np.ndarray, v: np.ndarray, gh: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """|dV| (m/s) and |dV|/dz (1/s) between each level and its upper neighbour (lower one for the top level)."""
    u, v, gh = (np.asarray(a, dtype=float) for a in (u, v, gh))
    n = u.shape[0]
    upper = np.r_[np.arange(1, n), n - 1]
    lower = np.r_[np.arange(0, n - 1), n - 2]
    dv = np.hypot(u[upper] - u[lower], v[upper] - v[lower])
    dz = np.abs(gh[upper] - gh[lower])
    with np.errstate(divide="ignore", invalid="ignore"):
        vws = np.where(dz >= MIN_DZ_M, dv / dz, np.nan)
    return dv, vws


def grid_spacing_m(lats: np.ndarray, lons: np.ndarray) -> tuple[float, np.ndarray]:
    lats = np.asarray(lats, dtype=float)
    dlat = np.radians(float(np.mean(np.diff(lats))))
    dlon = np.radians(float(np.mean(np.diff(np.asarray(lons, dtype=float)))))
    return float(EARTH_RADIUS_M * dlat), EARTH_RADIUS_M * np.cos(np.radians(lats)) * dlon


def horizontal_gradients(f: np.ndarray, lats: np.ndarray, lons: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    dy, dx_row = grid_spacing_m(lats, lons)
    f = np.asarray(f, dtype=float)
    df_dy = np.gradient(f, axis=-2) / dy
    df_dx = np.gradient(f, axis=-1) / dx_row[:, None]
    return df_dx, df_dy


def ellrod_ti2(
    u: np.ndarray, v: np.ndarray, gh: np.ndarray, divergence: np.ndarray, lats: np.ndarray, lons: np.ndarray
) -> np.ndarray:
    _, vws = layer_shear(u, v, gh)
    du_dx, du_dy = horizontal_gradients(u, lats, lons)
    dv_dx, dv_dy = horizontal_gradients(v, lats, lons)
    deformation = np.hypot(dv_dx + du_dy, du_dx - dv_dy)
    return vws * (deformation - np.asarray(divergence, dtype=float))


def cat_category_codes(ti2: np.ndarray) -> np.ndarray:
    ti2 = np.asarray(ti2, dtype=float)
    codes = np.searchsorted(np.asarray(_CAT_BOUNDS_S2), np.nan_to_num(ti2, nan=0.0), side="right").astype(np.int8)
    return np.where(np.isfinite(ti2), codes, np.int8(-1)).astype(np.int8)
