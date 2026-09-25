"""
Vectorized moist thermodynamics (NumPy), consistent with acf.science.

- e  = q p / (eps + q (1 - eps)),  eps = 0.622          (VaporPressure)
- es = 6.112 exp(17.67 Tc / (Tc + 243.5))  [hPa]       (Bolton 1980, SaturationVaporPressure)
- Td = exact inverse of es: Tc = 243.5 ln(e/6.112) / (17.67 - ln(e/6.112))
- theta_e: Bolton (1980) eq. 43 as in EquivalentPotentialTemperature.calculate_bolton_1980
- LCL height (Espy): 125 m per K of dewpoint depression.
- q_s = eps e_s / (p - (1 - eps) e_s); Tv = T (1 + (1/eps - 1) q), condensate loading neglected
- LCL temperature: Bolton (1980) eq. 15, T_L = 1 / (1/(Td - 56) + ln(T/Td)/800) + 56
"""

from __future__ import annotations

import numpy as np

from acf.science.constants import KAPPA

EPSILON = 0.622
ESPY_M_PER_K = 125.0


def vapor_pressure_hpa(q: np.ndarray, p_hpa: np.ndarray) -> np.ndarray:
    q = np.asarray(q, dtype=float)
    return q * np.asarray(p_hpa, dtype=float) / (EPSILON + q * (1.0 - EPSILON))


def saturation_vapor_pressure_hpa(t_k: np.ndarray) -> np.ndarray:
    tc = np.asarray(t_k, dtype=float) - 273.15
    return 6.112 * np.exp(17.67 * tc / (tc + 243.5))


def dewpoint_k_from_vapor_pressure(e_hpa: np.ndarray) -> np.ndarray:
    e = np.asarray(e_hpa, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        ln = np.log(e / 6.112)
        td_c = 243.5 * ln / (17.67 - ln)
    return np.where(e > 0.0, td_c + 273.15, np.nan)


def relative_humidity_pct(t_k: np.ndarray, q: np.ndarray, p_hpa: np.ndarray) -> np.ndarray:
    return np.minimum(100.0, vapor_pressure_hpa(q, p_hpa) / saturation_vapor_pressure_hpa(t_k) * 100.0)


def theta_e_bolton_k(t_k: np.ndarray, q: np.ndarray, p_hpa: np.ndarray) -> np.ndarray:
    t = np.asarray(t_k, dtype=float)
    p = np.asarray(p_hpa, dtype=float)
    td = np.minimum(dewpoint_k_from_vapor_pressure(vapor_pressure_hpa(q, p)), t)  # cap supersaturation
    with np.errstate(divide="ignore", invalid="ignore"):
        t_l = 56.0 + 1.0 / (1.0 / (td - 56.0) + np.log(t / td) / 800.0)
        e = saturation_vapor_pressure_hpa(td)
        r = EPSILON * e / (p - e)
        theta_l = t * (1000.0 / (p - e)) ** KAPPA * (t / t_l) ** (0.28 * r)
        return theta_l * np.exp(r * (1.0 + 0.448 * r) * (3036.0 / t_l - 1.78))


def cloud_base_lcl_m(t2m_k: np.ndarray, d2m_k: np.ndarray) -> np.ndarray:
    depression = np.asarray(t2m_k, dtype=float) - np.asarray(d2m_k, dtype=float)
    return ESPY_M_PER_K * np.maximum(depression, 0.0)


def saturation_specific_humidity(t_k: np.ndarray, p_hpa: np.ndarray) -> np.ndarray:
    """q_s = eps e_s / (p - (1 - eps) e_s), e_s from Bolton (1980)."""
    es = saturation_vapor_pressure_hpa(t_k)
    return EPSILON * es / (np.asarray(p_hpa, dtype=float) - (1.0 - EPSILON) * es)


def virtual_temperature_k(t_k: np.ndarray, q: np.ndarray) -> np.ndarray:
    """Tv = T (1 + (1/eps - 1) q), condensate loading neglected."""
    return np.asarray(t_k, dtype=float) * (1.0 + (1.0 / EPSILON - 1.0) * np.asarray(q, dtype=float))


def lcl_temperature_bolton_k(t_k: np.ndarray, td_k: np.ndarray) -> np.ndarray:
    """Bolton (1980) eq. 15: T_L = 1 / (1/(Td - 56) + ln(T/Td)/800) + 56."""
    t = np.asarray(t_k, dtype=float)
    td = np.minimum(np.asarray(td_k, dtype=float), t)
    return 1.0 / (1.0 / (td - 56.0) + np.log(t / td) / 800.0) + 56.0
