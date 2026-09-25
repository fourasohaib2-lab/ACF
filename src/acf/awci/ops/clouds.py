"""
Cloud diagnostics from IFS pressure-level fields (NumPy only, vectorized over the grid).

Per-level arrays are (level, lat, lon), levels by decreasing pressure (1000 hPa first).
- level cloud fraction: Sundqvist, Berge & Kristjansson (1989), Mon. Wea. Rev. 117,
  C = 1 - sqrt((1 - RH) / (1 - RHc)) for RH >= RHc else 0, RH = IFS r (water above 0 degC, ice below -23 degC)
- etages: sigma = p / p_s, low > 0.8 >= mid > 0.45 >= high (ECMWF low/medium/high cloud cover definitions)
- overlap: maximum-random, Geleyn & Hollingsworth (1979), form of Raisanen (1998), from the top down
  C_tot = 1 - prod_k (1 - max(C_k, C_k-1)) / (1 - C_k-1)
- oktas: WMO code table 2700 (8 only when overcast, 7 for 7/8 or more but not 8, 1 for a trace);
  FEW 1-2, SCT 3-4, BKN 5-7, OVC 8 (ICAO Annex 3)
- ceiling: ICAO Annex 2, base (AGL) of the lowest layer below 6000 m covering more than half the sky
- genus / species: rule tables of the SP1C spec (thresholds in the cloud profile, status HYPOTHESIS)
"""

from __future__ import annotations

import numpy as np

from acf.awci.ops.cloud_profile import CloudProfile

ETAGE_LOW, ETAGE_MID, ETAGE_HIGH = 0, 1, 2
ETAGE_NAMES = ("low", "mid", "high")
#: WMO code table 0500 (genus of cloud).
GENUS_CODES: dict[str, int] = {"Ci": 0, "Cc": 1, "Cs": 2, "Ac": 3, "As": 4, "Ns": 5, "Sc": 6, "St": 7, "Cu": 8, "Cb": 9}
GENUS_NAMES: dict[int, str] = {code: name for name, code in GENUS_CODES.items()}
CLEAR, INDETERMINATE = -1, -2
SPECIES_BITS: dict[str, int] = {"castellanus": 1, "lenticularis": 2, "fractus": 4, "nebulosus": 8, "spissatus": 16}
CONVECTIVE_CLASSES: dict[int, str] = {0: "none", 1: "Cu humilis/mediocris", 2: "Cu congestus (TCU)",
                                      3: "Cb calvus", 4: "Cb capillatus"}


def sigma_etage(sigma: np.ndarray, profile: CloudProfile) -> np.ndarray:
    s = np.asarray(sigma, dtype=float)
    return np.where(s > profile.sigma_low_mid, ETAGE_LOW,
                    np.where(s > profile.sigma_mid_high, ETAGE_MID, ETAGE_HIGH)).astype(np.int8)


def etage_codes(levels_hpa: np.ndarray, sp_hpa: np.ndarray, profile: CloudProfile) -> np.ndarray:
    return sigma_etage(np.asarray(levels_hpa, dtype=float)[:, None, None] / np.asarray(sp_hpa, dtype=float)[None],
                       profile)


def sundqvist_fraction(rh_pct: np.ndarray, rh_critical: np.ndarray | float) -> np.ndarray:
    raw = np.asarray(rh_pct, dtype=float)
    rh = np.clip(raw / 100.0, 0.0, 1.0)
    rhc = np.asarray(rh_critical, dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        c = 1.0 - np.sqrt((1.0 - rh) / (1.0 - rhc))
    return np.where(np.isnan(raw), np.nan, np.where(rh >= rhc, np.clip(c, 0.0, 1.0), 0.0))


def level_cloud_fraction(r_pct: np.ndarray, etage: np.ndarray, profile: CloudProfile) -> np.ndarray:
    rhc = np.choose(etage, [profile.rh_critical[name] for name in ETAGE_NAMES])
    return sundqvist_fraction(r_pct, rhc)


def max_random_cover(fraction: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
    c = np.nan_to_num(np.asarray(fraction, dtype=float), nan=0.0)
    if mask is not None:
        c = np.where(mask, c, 0.0)
    clear = np.ones(c.shape[1:])
    above = np.zeros(c.shape[1:])
    for k in range(c.shape[0] - 1, -1, -1):
        with np.errstate(invalid="ignore", divide="ignore"):
            factor = np.where(above < 1.0, (1.0 - np.maximum(c[k], above)) / (1.0 - above), 0.0)
        clear = clear * factor
        above = c[k]
    return 1.0 - clear


def oktas(cover: np.ndarray) -> np.ndarray:
    c = np.asarray(cover, dtype=float)
    n = np.clip(np.rint(8.0 * np.nan_to_num(c)), 1, 7)
    n = np.where(c >= 1.0, 8, np.where(c <= 0.0, 0, n))
    return np.where(np.isnan(c), np.nan, n)


def amount_code(n_oktas: float) -> str | None:
    if not n_oktas or np.isnan(n_oktas):
        return None
    return "FEW" if n_oktas <= 2 else "SCT" if n_oktas <= 4 else "BKN" if n_oktas <= 7 else "OVC"


def level_interfaces(gh: np.ndarray, elevation: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Lower/upper interfaces (m AMSL): midpoints between neighbouring gh, half the neighbouring
    spacing at both ends, never below the terrain."""
    gh = np.asarray(gh, dtype=float)
    mid = 0.5 * (gh[1:] + gh[:-1])
    lower = np.concatenate([(gh[0] - 0.5 * (gh[1] - gh[0]))[None], mid])
    upper = np.concatenate([mid, (gh[-1] + 0.5 * (gh[-1] - gh[-2]))[None]])
    floor = np.asarray(elevation, dtype=float)[None]
    return np.maximum(lower, floor), np.maximum(upper, floor)


def vertical_gradient_per_km(f: np.ndarray, gh: np.ndarray) -> np.ndarray:
    """df/dz (per km) between each level and its upper neighbour (lower one for the top level)."""
    f, gh = np.asarray(f, dtype=float), np.asarray(gh, dtype=float)
    n = f.shape[0]
    upper = np.r_[np.arange(1, n), n - 1]
    lower = np.r_[np.arange(0, n - 1), n - 2]
    dz = gh[upper] - gh[lower]
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(np.abs(dz) >= 1.0, (f[upper] - f[lower]) / dz * 1000.0, np.nan)
