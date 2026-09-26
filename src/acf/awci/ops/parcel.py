"""
Surface-based parcel ascent on pressure levels (vectorized, NumPy only).

- LCL temperature: Bolton (1980) eq. 15; LCL pressure by Poisson p_L = p0 (T_L / T0)^(1/kappa)
- below the LCL: dry adiabat T = T0 (p / p0)^kappa, specific humidity conserved
- above the LCL: pseudo-adiabat by conservation of theta_e (Bolton 1980, thermo.theta_e_bolton_k);
  T solved by bisection on theta_e(T, q_s(T, p), p) = theta_e(parcel), which increases with T
- buoyancy on virtual temperature; EL = highest level above the LCL where Tv_parcel > Tv_env
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from acf.awci.ops.thermo import (
    EPSILON,
    lcl_temperature_bolton_k,
    saturation_specific_humidity,
    saturation_vapor_pressure_hpa,
    theta_e_bolton_k,
    virtual_temperature_k,
)
from acf.science.constants import KAPPA

T_MIN_K = 150.0
T_MAX_K = 330.0
BISECTION_ITERATIONS = 40  # (T_MAX - T_MIN) / 2**40 < 1e-9 K


@dataclass(frozen=True)
class ParcelResult:
    p_lcl_hpa: np.ndarray
    el_index: np.ndarray  # level index of the EL, -1 = no buoyant level above the LCL
    el_gh_m: np.ndarray
    el_temp_k: np.ndarray


def _upper_bound_k(p_hpa: np.ndarray) -> np.ndarray:
    """Warmest temperature with e_s <= p/2 (exact inverse of Bolton e_s): keeps q_s finite and monotonic."""
    ln = np.log(0.5 * np.asarray(p_hpa, dtype=float) / 6.112)
    return np.minimum(T_MAX_K, 243.5 * ln / (17.67 - ln) + 273.15)


def saturated_parcel_temperature_k(theta_e: np.ndarray, p_hpa: np.ndarray) -> np.ndarray:
    theta_e = np.asarray(theta_e, dtype=float)
    p = np.broadcast_to(np.asarray(p_hpa, dtype=float), theta_e.shape)
    lo = np.full(theta_e.shape, T_MIN_K)
    hi = np.broadcast_to(_upper_bound_k(p), theta_e.shape).copy()
    for _ in range(BISECTION_ITERATIONS):
        mid = 0.5 * (lo + hi)
        too_warm = theta_e_bolton_k(mid, saturation_specific_humidity(mid, p), p) > theta_e
        hi = np.where(too_warm, mid, hi)
        lo = np.where(too_warm, lo, mid)
    return 0.5 * (lo + hi)


def surface_parcel(
    t2m: np.ndarray, d2m: np.ndarray, sp_hpa: np.ndarray, levels_hpa: np.ndarray,
    t_env: np.ndarray, q_env: np.ndarray, gh: np.ndarray, underground: np.ndarray,
) -> ParcelResult:
    t0 = np.asarray(t2m, dtype=float)
    td0 = np.minimum(np.asarray(d2m, dtype=float), t0)
    p0 = np.asarray(sp_hpa, dtype=float)
    e0 = saturation_vapor_pressure_hpa(td0)
    q0 = EPSILON * e0 / (p0 - (1.0 - EPSILON) * e0)
    p_lcl = p0 * (lcl_temperature_bolton_k(t0, td0) / t0) ** (1.0 / KAPPA)
    p3 = np.asarray(levels_hpa, dtype=float)[:, None, None] * np.ones_like(t_env, dtype=float)
    above_lcl = p3 < p_lcl[None]
    moist_t = saturated_parcel_temperature_k(np.broadcast_to(theta_e_bolton_k(t0, q0, p0), p3.shape), p3)
    t_parcel = np.where(above_lcl, moist_t, t0[None] * (p3 / p0[None]) ** KAPPA)
    q_parcel = np.where(above_lcl, saturation_specific_humidity(moist_t, p3), q0[None])
    buoyant = (above_lcl & ~np.asarray(underground, dtype=bool)
               & (virtual_temperature_k(t_parcel, q_parcel) > virtual_temperature_k(t_env, q_env)))
    has_el = buoyant.any(axis=0)
    n = p3.shape[0]
    el = np.where(has_el, n - 1 - np.argmax(buoyant[::-1], axis=0), -1)
    idx = np.clip(el, 0, None)[None]
    el_gh = np.where(has_el, np.take_along_axis(np.asarray(gh, dtype=float), idx, 0)[0], np.nan)
    el_t = np.where(has_el, np.take_along_axis(np.asarray(t_env, dtype=float), idx, 0)[0], np.nan)
    return ParcelResult(p_lcl, el.astype(np.int16), el_gh, el_t)
