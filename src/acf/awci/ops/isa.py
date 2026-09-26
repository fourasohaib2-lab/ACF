"""
ICAO Standard Atmosphere (Doc 7488/3), troposphere and lower stratosphere.

Troposphere (0-11 km):  h = T0/L * (1 - (p/p0)^(R*L/g0))
Stratosphere (11-20 km, isothermal T11 = 216.65 K):
                        h = 11000 + R*T11/g0 * ln(p11/p)
Constants are the ICAO values: T0 = 288.15 K, p0 = 1013.25 hPa,
L = 0.0065 K/m, g0 = 9.80665 m/s2, R = 287.05287 J/(kg K).
"""

from __future__ import annotations

import numpy as np

ISA_T0_K = 288.15
ISA_P0_HPA = 1013.25
ISA_LAPSE_K_PER_M = 0.0065
ISA_G0 = 9.80665
ISA_R = 287.05287
ISA_T11_K = 216.65
ISA_H11_M = 11000.0
ISA_H20_M = 20000.0
ISA_P11_HPA = ISA_P0_HPA * (1.0 - ISA_LAPSE_K_PER_M * ISA_H11_M / ISA_T0_K) ** (ISA_G0 / (ISA_R * ISA_LAPSE_K_PER_M))
ISA_P20_HPA = ISA_P11_HPA * float(np.exp(-ISA_G0 * (ISA_H20_M - ISA_H11_M) / (ISA_R * ISA_T11_K)))
_FT_PER_M = 1.0 / 0.3048


def pressure_altitude_m(pressure_hpa: float | np.ndarray) -> float | np.ndarray:
    """ISA pressure altitude (m) for a pressure (hPa), valid from 20 km up to the surface."""
    p = np.asarray(pressure_hpa, dtype=float)
    if np.any(p < ISA_P20_HPA) or np.any(p <= 0):
        raise ValueError(f"pressure below {ISA_P20_HPA:.2f} hPa (above 20 km) is outside this ISA implementation")
    tropo = ISA_T0_K / ISA_LAPSE_K_PER_M * (1.0 - (p / ISA_P0_HPA) ** (ISA_R * ISA_LAPSE_K_PER_M / ISA_G0))
    strato = ISA_H11_M + ISA_R * ISA_T11_K / ISA_G0 * np.log(ISA_P11_HPA / p)
    h = np.where(p >= ISA_P11_HPA, tropo, strato)
    return float(h) if h.ndim == 0 else h


def flight_level(pressure_hpa: float) -> int:
    """Nearest flight level (hundreds of feet of ISA pressure altitude)."""
    return int(round(float(pressure_altitude_m(pressure_hpa)) * _FT_PER_M / 100.0))
