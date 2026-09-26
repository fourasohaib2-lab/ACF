"""
Vectorized moist thermodynamics (NumPy), consistent with acf.science.

- e  = q p / (eps + q (1 - eps)),  eps = 0.622          (VaporPressure)
- es = 6.112 exp(17.67 Tc / (Tc + 243.5))  [hPa]       (Bolton 1980, SaturationVaporPressure)
- Td = exact inverse of es: Tc = 243.5 ln(e/6.112) / (17.67 - ln(e/6.112))
- theta_e: Bolton (1980) eq. 43 as in EquivalentPotentialTemperature.calculate_bolton_1980
- LCL height (Espy): 125 m per K of dewpoint depression.
- q_s = eps e_s / (p - (1 - eps) e_s); Tv = T (1 + (1/eps - 1) q), condensate loading neglected
- LCL temperature: Bolton (1980) eq. 15, T_L = 1 / (1/(Td - 56) + ln(T/Td)/800) + 56
- IFS mixed-phase saturation (ECMWF IFS Documentation, Part IV "Physical processes"; Tetens formula with the
  Buck (1981) constants): e_sat = alpha e_w + (1 - alpha) e_i, e = a1 exp(a3 (T - T0) / (T - a4)),
  a1 = 611.21 Pa, T0 = 273.16 K; water a3 = 17.502, a4 = 32.19 K; ice a3 = 22.587, a4 = -0.7 K;
  alpha = 1 above T0, 0 below T_ice = 250.16 K, ((T - T_ice) / (T0 - T_ice))^2 in between. The relative
  humidity of IFS pressure-level `r` uses it; ifs_relative_humidity_pct gives the same quantity from q, T, p
  for another model (SP6), so that the IFS-calibrated cloud profile receives what it was calibrated on.
- model surface height (hypsometric equation): z_s = gh_k - (Rd Tv_mean / g) ln(p_s / p_k),
  k = lowest level above ground, Tv_mean = mean of surface (2t, 2d) and level-k virtual temperatures
"""

from __future__ import annotations

import numpy as np

from acf.science.constants import KAPPA, RD, G

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


IFS_A1_PA = 611.21
IFS_T0_K = 273.16
IFS_TICE_K = 250.16
IFS_WATER = (17.502, 32.19)
IFS_ICE = (22.587, -0.7)


def ifs_saturation_vapor_pressure_hpa(t_k: np.ndarray) -> np.ndarray:
    """Mixed-phase saturation vapour pressure of the IFS (see module doc), hPa."""
    t = np.asarray(t_k, dtype=float)
    tetens = lambda a3, a4: IFS_A1_PA * np.exp(a3 * (t - IFS_T0_K) / (t - a4))  # noqa: E731
    alpha = np.clip((t - IFS_TICE_K) / (IFS_T0_K - IFS_TICE_K), 0.0, 1.0) ** 2
    return (alpha * tetens(*IFS_WATER) + (1.0 - alpha) * tetens(*IFS_ICE)) / 100.0


def ifs_relative_humidity_pct(t_k: np.ndarray, q: np.ndarray, p_hpa: np.ndarray) -> np.ndarray:
    """Relative humidity with respect to the IFS mixed-phase saturation, from q, T, p (not capped: the IFS `r`
    exceeds 100 % in ice-supersaturated air)."""
    return vapor_pressure_hpa(q, p_hpa) / ifs_saturation_vapor_pressure_hpa(t_k) * 100.0


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


def model_surface_height_m(sp_hpa: np.ndarray, t2m_k: np.ndarray, d2m_k: np.ndarray, levels_hpa: np.ndarray,
                           gh: np.ndarray, t_k: np.ndarray, q: np.ndarray) -> np.ndarray:
    """Height (m AMSL) of the IFS model surface, consistent with sp: hypsometric equation from the lowest
    pressure level above ground (levels ordered by decreasing pressure). NaN if no level is above ground."""
    sp = np.asarray(sp_hpa, dtype=float)
    levels = np.asarray(levels_hpa, dtype=float)
    above = levels[:, None, None] < sp[None]
    k = np.argmax(above, axis=0)[None]
    p_k = levels[k[0]]
    take = lambda a: np.take_along_axis(np.asarray(a, dtype=float), k, axis=0)[0]  # noqa: E731
    e_s = saturation_vapor_pressure_hpa(np.minimum(d2m_k, t2m_k))
    q_s = EPSILON * e_s / (sp - (1.0 - EPSILON) * e_s)
    tv_mean = 0.5 * (virtual_temperature_k(t2m_k, q_s) + virtual_temperature_k(take(t_k), take(q)))
    z = take(gh) - RD * tv_mean / G * np.log(sp / p_k)
    return np.where(above.any(axis=0), z, np.nan)
