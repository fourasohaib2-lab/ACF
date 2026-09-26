"""
IFS accumulated fields differenced over the preceding interval, and column diagnostics.

- OLR = -(ttr(t) - ttr(t - dt)) / dt   [W m-2]; ttr accumulated, J m-2, negative upward (ECMWF)
- T_e = (OLR / sigma)^(1/4), sigma = 5.670374419e-8 W m-2 K-4 (CODATA 2018, exact); broadband, not a
  window-channel brightness temperature
- amounts: (acc(t) - acc(t - dt)) x 1000 mm; negative GRIB-packing noise clipped to 0
- snow depth = sd x rho_water / rsn (sd in m water equivalent, rsn snow density kg m-3)
- freezing precipitation: tp increment when ptype is freezing rain (3) or freezing drizzle (12) at both ends
- column condensate = tcw - tcwv (cloud liquid + ice + rain + snow, kg m-2)
Without the previous step every accumulated layer is NaN (never 0).
"""

from __future__ import annotations

import numpy as np

STEFAN_BOLTZMANN = 5.670374419e-8
RHO_WATER = 1000.0
FREEZING_PTYPES = (3.0, 12.0)


def olr_w_m2(ttr_now: np.ndarray, ttr_prev: np.ndarray, interval_h: float) -> np.ndarray:
    olr = -(np.asarray(ttr_now, dtype=float) - np.asarray(ttr_prev, dtype=float)) / (interval_h * 3600.0)
    return np.where(olr > 0.0, olr, np.nan)


def effective_emission_temperature_k(olr: np.ndarray) -> np.ndarray:
    return (np.asarray(olr, dtype=float) / STEFAN_BOLTZMANN) ** 0.25


def interval_amount_mm(acc_now_m: np.ndarray, acc_prev_m: np.ndarray) -> np.ndarray:
    return np.maximum(np.asarray(acc_now_m, dtype=float) - np.asarray(acc_prev_m, dtype=float), 0.0) * 1000.0


def snow_depth_cm(sd_m_we: np.ndarray, rsn_kg_m3: np.ndarray) -> np.ndarray:
    sd, rsn = np.asarray(sd_m_we, dtype=float), np.asarray(rsn_kg_m3, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        depth = np.where(rsn > 0.0, sd * RHO_WATER / rsn * 100.0, np.nan)
    return np.where(sd == 0.0, 0.0, depth)


def freezing_precip_mm(tp_now_m: np.ndarray, tp_prev_m: np.ndarray, ptype_now: np.ndarray,
                       ptype_prev: np.ndarray) -> np.ndarray:
    freezing = np.isin(ptype_now, FREEZING_PTYPES) & np.isin(ptype_prev, FREEZING_PTYPES)
    return np.where(freezing, interval_amount_mm(tp_now_m, tp_prev_m), 0.0)


def column_condensate(tcw: np.ndarray, tcwv: np.ndarray) -> np.ndarray:
    return np.maximum(np.asarray(tcw, dtype=float) - np.asarray(tcwv, dtype=float), 0.0)


def accumulated_layers(sfc_now: dict[str, np.ndarray], sfc_prev: dict[str, np.ndarray] | None,
                       interval_h: float | None) -> dict[str, np.ndarray]:
    shape = np.shape(sfc_now["ttr"])
    if sfc_prev is None or not interval_h:
        nan = np.full(shape, np.nan)
        return {"cloud_top_teff_k": nan, "snowfall_mm": nan.copy(), "freezing_precip_mm": nan.copy()}
    return {
        "cloud_top_teff_k": effective_emission_temperature_k(olr_w_m2(sfc_now["ttr"], sfc_prev["ttr"], interval_h)),
        "snowfall_mm": interval_amount_mm(sfc_now["sf"], sfc_prev["sf"]),
        "freezing_precip_mm": freezing_precip_mm(sfc_now["tp"], sfc_prev["tp"], sfc_now["ptype"], sfc_prev["ptype"]),
    }
