"""
Vectorized aviation hazard diagnostics.

- icing_potential: T+RH approach of Schultz & Politovich (1992); thresholds
  (-20..0 degC, RH >= 70 %) are an ACF choice, status HYPOTHESIS.
- precipitation classes: WMO-No. 8 (light < 2.5, moderate < 10, heavy < 50,
  violent >= 50 mm/h); tprate [kg m-2 s-1] x 3600 = mm/h.
- ptype: ECMWF parameter 260015 codes mapped onto acf.awci.hydrometeor_phase
  PHASE_SEVERITY (0 no precipitation, 1 rain, 3 freezing rain, 5 snow,
  6 wet snow, 7 rain/snow mix, 8 ice pellets, 12 freezing drizzle).
- dust_proxy: ramp(10 m gust; 8->18 m/s) x (1 - ramp(RH2m; 20->70 %)),
  status HYPOTHESIS (not a concentration).
"""

from __future__ import annotations

import numpy as np

from acf.awci.dust import DUST_DRY_RH_CEILING_PCT, DUST_DRY_RH_FLOOR_PCT, DUST_WIND_CEILING_M_S, DUST_WIND_FLOOR_M_S
from acf.awci.hydrometeor_phase import PHASE_SEVERITY
from acf.awci.ops.thermo import saturation_vapor_pressure_hpa

ICING_T_MIN_C = -20.0
ICING_T_MAX_C = 0.0
ICING_RH_MIN_PCT = 70.0
WMO_PRECIP_BOUNDS_MM_H = (2.5, 10.0, 50.0)

_FREEZING = PHASE_SEVERITY["Freezing Rain / Ice Pellets"]
ECMWF_PTYPE_SEVERITY: dict[int, float] = {
    0: 0.0,
    1: PHASE_SEVERITY["Rain"],
    3: _FREEZING,
    5: PHASE_SEVERITY["Snow"],
    6: PHASE_SEVERITY["Wet Snow/Mix"],
    7: PHASE_SEVERITY["Wet Snow/Mix"],
    8: _FREEZING,
    12: _FREEZING,
}


def _ramp(x: np.ndarray, floor: float, ceiling: float) -> np.ndarray:
    return np.clip((np.asarray(x, dtype=float) - floor) / (ceiling - floor), 0.0, 1.0)


def icing_potential(t_k: np.ndarray, r_pct: np.ndarray) -> np.ndarray:
    tc = np.asarray(t_k, dtype=float) - 273.15
    r = np.asarray(r_pct, dtype=float)
    hit = (tc >= ICING_T_MIN_C) & (tc <= ICING_T_MAX_C) & (r >= ICING_RH_MIN_PCT)
    return np.where(np.isfinite(tc) & np.isfinite(r), hit.astype(float), np.nan)


def precip_rate_mm_h(tprate: np.ndarray) -> np.ndarray:
    return np.maximum(np.asarray(tprate, dtype=float) * 3600.0, 0.0)


def precip_class_codes(rate_mm_h: np.ndarray) -> np.ndarray:
    rate = np.asarray(rate_mm_h, dtype=float)
    codes = 1 + np.searchsorted(np.asarray(WMO_PRECIP_BOUNDS_MM_H), np.nan_to_num(rate), side="right")
    codes = np.where(rate > 0.0, codes, 0)
    return np.where(np.isfinite(rate), codes, -1).astype(np.int8)


def ptype_severity(ptype: np.ndarray) -> np.ndarray:
    codes = np.asarray(ptype, dtype=float)
    out = np.full(codes.shape, np.nan)
    for code, severity in ECMWF_PTYPE_SEVERITY.items():
        out[codes == code] = severity
    return out


def relative_humidity_2m_pct(t2m_k: np.ndarray, d2m_k: np.ndarray) -> np.ndarray:
    return np.minimum(100.0, saturation_vapor_pressure_hpa(d2m_k) / saturation_vapor_pressure_hpa(t2m_k) * 100.0)


def dust_proxy(gust_ms: np.ndarray, rh2m_pct: np.ndarray) -> np.ndarray:
    wind = _ramp(gust_ms, DUST_WIND_FLOOR_M_S, DUST_WIND_CEILING_M_S)
    dry = 1.0 - _ramp(rh2m_pct, DUST_DRY_RH_FLOOR_PCT, DUST_DRY_RH_CEILING_PCT)
    return wind * dry
