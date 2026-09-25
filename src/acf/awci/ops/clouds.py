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

from dataclasses import dataclass

import numpy as np

from acf.awci.ops.cloud_profile import CloudProfile
from acf.awci.ops.isa import flight_level
from acf.awci.ops.kinematics import horizontal_gradients
from acf.awci.ops.parcel import ParcelResult
from acf.awci.ops.thermo import saturation_specific_humidity, theta_e_bolton_k
from acf.science.constants import G, KAPPA

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


CLOUD_LEVEL_LAYERS: tuple[str, ...] = ("cloud_fraction", "cloud_genus", "cloud_species", "potential_instability")
CLOUD_SURFACE_LAYERS: tuple[str, ...] = (
    "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "cloud_cover_total_diag", "ceiling_m",
    "lowest_cloud_base_m", "highest_cloud_top_m", "genus_low", "genus_mid", "genus_high", "convective_class",
    "convective_top_m", "convective_top_temp_k", "species_flags",
)
_CELLULAR = (GENUS_CODES["Ac"], GENUS_CODES["Sc"], GENUS_CODES["Cc"])


@dataclass
class CloudInputs:
    levels_hpa: np.ndarray
    lats: np.ndarray
    lons: np.ndarray
    r_pct: np.ndarray
    t_k: np.ndarray
    q: np.ndarray
    gh: np.ndarray
    u: np.ndarray
    v: np.ndarray
    theta_e: np.ndarray
    underground: np.ndarray
    sp_hpa: np.ndarray
    elevation: np.ndarray
    precip_rate_mm_h: np.ndarray
    ptype: np.ndarray
    wind10_m_s: np.ndarray
    mucape: np.ndarray
    column_condensate: np.ndarray
    lcl_agl_m: np.ndarray
    parcel: ParcelResult


def _take(a: np.ndarray, idx: np.ndarray) -> np.ndarray:
    return np.take_along_axis(a, idx[None], axis=0)[0]


def _neighbourhood(f: np.ndarray, reduce: str, radius: int = 1) -> np.ndarray:
    """max, min or std over a (2r+1)^2 window, edges replicated."""
    pad = np.pad(np.asarray(f, dtype=float), radius, mode="edge")
    ny, nx = f.shape
    stack = np.stack([pad[dy:dy + ny, dx:dx + nx] for dy in range(2 * radius + 1) for dx in range(2 * radius + 1)])
    return {"max": stack.max(0), "min": stack.min(0), "std": stack.std(0)}[reduce]


def convective_diagnosis(inp: CloudInputs, profile: CloudProfile) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    c = profile.convection
    top, top_t = inp.parcel.el_gh_m, inp.parcel.el_temp_k
    with np.errstate(invalid="ignore"):
        depth = top - (inp.elevation + inp.lcl_agl_m)
        ok = ((inp.mucape >= c["cape_min_j_kg"]) & np.isfinite(depth) & (depth > 0.0)
              & (inp.column_condensate >= c["condensate_min_kg_m2"]))
        # Cb = deep convection with a glaciated top; rain at the ground is not required (high-based dry Cb, virga)
        cb = ok & (depth >= c["cb_min_depth_m"]) & (top_t <= c["glaciation_temp_k"])
        cls = np.select([cb & (top_t <= c["capillatus_temp_k"]), cb, ok & (depth >= c["tcu_min_depth_m"]), ok],
                        [4, 3, 2, 1], 0)
    return cls, np.where(cls > 0, top, np.nan), np.where(cls > 0, top_t, np.nan)


def _genus(etage: np.ndarray, depth: np.ndarray, n_oktas: np.ndarray, base_agl: np.ndarray, unstable: np.ndarray,
           precip: np.ndarray, g: dict[str, float]) -> np.ndarray:
    low, mid, high = etage == ETAGE_LOW, etage == ETAGE_MID, etage == ETAGE_HIGH
    stable = ~unstable
    return np.select(
        [(low | mid) & (depth >= g["ns_min_depth_m"]) & precip & stable,
         low & (base_agl <= g["st_max_base_m"]) & stable, low,
         mid & stable & (depth >= g["as_min_depth_m"]), mid,
         high & unstable & (depth < g["cc_max_depth_m"]), high & stable & (n_oktas >= g["cs_min_oktas"]), high],
        [GENUS_CODES[n] for n in ("Ns", "St", "Sc", "As", "Ac", "Cc", "Cs", "Ci")], CLEAR,
    )


def _lenticular_levels(inp: CloudInputs, s: dict[str, float]) -> np.ndarray:
    """Mountain-wave conditions per level: stable (N^2 > 0), cross-barrier wind, relief, Froude U/(N h)."""
    theta = inp.t_k * (1000.0 / inp.levels_hpa[:, None, None]) ** KAPPA
    n2 = G / theta * vertical_gradient_per_km(theta, inp.gh) / 1000.0
    dhdx, dhdy = horizontal_gradients(inp.elevation, inp.lats, inp.lons)
    slope = np.hypot(dhdx, dhdy)
    relief = _neighbourhood(inp.elevation, "max") - _neighbourhood(inp.elevation, "min")
    with np.errstate(invalid="ignore", divide="ignore"):
        u_cross = np.abs(inp.u * dhdx + inp.v * dhdy) / slope
        froude = u_cross / (np.sqrt(np.where(n2 > 0.0, n2, np.nan)) * relief)
        return ((n2 > 0.0) & (u_cross >= s["lenticularis_min_wind_m_s"]) & (relief >= s["lenticularis_min_relief_m"])
                & (froude >= s["lenticularis_froude_min"]) & (froude <= s["lenticularis_froude_max"]))


def diagnose_clouds(inp: CloudInputs, profile: CloudProfile) -> dict[str, np.ndarray]:
    g, s = profile.genus, profile.species
    n, shape2 = inp.gh.shape[0], inp.gh.shape[1:]
    p3 = inp.levels_hpa[:, None, None] * np.ones_like(inp.t_k)
    etage = etage_codes(inp.levels_hpa, inp.sp_hpa, profile)
    frac = np.where(inp.underground, np.nan, level_cloud_fraction(inp.r_pct, etage, profile))
    instability = np.where(inp.underground, np.nan, vertical_gradient_per_km(inp.theta_e, inp.gh))
    theta_es = theta_e_bolton_k(inp.t_k, saturation_specific_humidity(inp.t_k, p3), p3)
    conditional = vertical_gradient_per_km(theta_es, inp.gh)
    lenticular = _lenticular_levels(inp, s)
    lower_if, upper_if = level_interfaces(inp.gh, inp.elevation)
    precip = (inp.precip_rate_mm_h >= g["continuous_precip_mm_h"]) & (inp.ptype > 0)

    cloudy = np.nan_to_num(frac) >= profile.layer_min_fraction
    start = cloudy & ~np.concatenate([np.zeros((1, *shape2), dtype=bool), cloudy[:-1]])
    layer_id = np.where(cloudy, np.cumsum(start, axis=0), 0)

    genus_level = np.full(inp.gh.shape, float(CLEAR))
    genus_etage = [np.full(shape2, float(CLEAR)) for _ in ETAGE_NAMES]
    best_cover = [np.zeros(shape2) for _ in ETAGE_NAMES]
    ceiling = np.full(shape2, np.nan)
    lowest, highest = np.full(shape2, np.nan), np.full(shape2, np.nan)
    species = np.zeros(inp.gh.shape, dtype=np.int32)  # per level: the species of the layer it belongs to
    layer_oktas = np.zeros(inp.gh.shape)

    for j in range(1, int(layer_id.max(initial=0)) + 1):
        mask = layer_id == j
        present = mask.any(axis=0)
        base = np.argmax(mask, axis=0)
        top = n - 1 - np.argmax(mask[::-1], axis=0)
        cover = np.where(mask, np.nan_to_num(frac), 0.0).max(axis=0)
        n_ok = np.nan_to_num(oktas(cover))
        depth = _take(upper_if, top) - _take(lower_if, base)
        base_agl = np.maximum(_take(inp.gh, base) - inp.elevation, 0.0)
        e_base = _take(etage, base)
        count = mask.sum(axis=0)
        total = np.where(mask, np.nan_to_num(instability), 0.0).sum(axis=0)
        valid = np.where(mask, np.isfinite(instability), True).all(axis=0)
        mean_pi = np.where(present & valid, total / np.maximum(count, 1), np.nan)
        code = _genus(e_base, depth, n_ok, base_agl, mean_pi < 0.0, precip, g)
        code = np.where(present, np.where(np.isfinite(mean_pi), code, INDETERMINATE), CLEAR)
        genus_level = np.where(mask, code, genus_level)
        for e in range(len(ETAGE_NAMES)):  # the cloud present in the etage, wherever its base is
            in_etage = mask & (etage == e)
            cover_e = np.where(in_etage, np.nan_to_num(frac), 0.0).max(axis=0)
            better = in_etage.any(axis=0) & (cover_e > best_cover[e])
            genus_etage[e] = np.where(better, code, genus_etage[e])
            best_cover[e] = np.where(better, cover_e, best_cover[e])
        qualifies = present & (n_ok >= 5) & (base_agl < profile.ceiling_max_base_m)
        ceiling = np.where(qualifies, np.fmin(ceiling, base_agl), ceiling)
        lowest = np.where(present, np.fmin(lowest, base_agl), lowest)
        highest = np.where(present, np.fmax(highest, _take(inp.gh, top)), highest)
        cellular = present & np.isin(code, _CELLULAR)
        bits = np.where(cellular & (_take(conditional, base) < 0.0), SPECIES_BITS["castellanus"], 0)
        bits |= np.where(cellular & _take(lenticular, base), SPECIES_BITS["lenticularis"], 0)
        bits |= np.where(present & (code == GENUS_CODES["St"]) & precip  # WMO-No. 407: fractus only with St, Cu
                         & (inp.wind10_m_s >= s["fractus_min_wind_m_s"]), SPECIES_BITS["fractus"], 0)
        species = np.where(mask, bits[None], species)
        layer_oktas = np.where(mask, n_ok[None], layer_oktas)

    covers = {e: max_random_cover(frac, etage == code) for code, e in enumerate(ETAGE_NAMES)}
    smooth_low = _neighbourhood(covers["low"], "std") <= s["nebulosus_max_std"]
    smooth_high = _neighbourhood(covers["high"], "std") <= s["nebulosus_max_std"]
    dense = layer_oktas >= s["nebulosus_min_oktas"]
    nebulosus = dense & (((genus_level == GENUS_CODES["St"]) & smooth_low[None])
                         | ((genus_level == GENUS_CODES["Cs"]) & smooth_high[None]))
    species |= np.where(nebulosus, SPECIES_BITS["nebulosus"], 0)

    cls, conv_top, conv_top_t = convective_diagnosis(inp, profile)
    conv_code = np.where(cls >= 3, GENUS_CODES["Cb"], GENUS_CODES["Cu"])
    with np.errstate(invalid="ignore"):
        in_conv = (cls > 0)[None] & (inp.gh >= (inp.elevation + inp.lcl_agl_m)[None]) & (inp.gh <= conv_top[None])
    genus_level = np.where(in_conv & (cls >= 2)[None], conv_code[None], genus_level)
    species = np.where(in_conv & (cls >= 2)[None], 0, species)  # the layer's species no longer describe TCU/Cb
    genus_level = np.where(in_conv & (cls == 1)[None] & (genus_level == CLEAR), GENUS_CODES["Cu"], genus_level)
    conv_etage = sigma_etage(inp.parcel.p_lcl_hpa / inp.sp_hpa, profile)
    for e in range(len(ETAGE_NAMES)):  # every etage the convective column crosses, base etage at least
        here = (in_conv & (etage == e)).any(axis=0) | (conv_etage == e)
        genus_etage[e] = np.where(here & (cls >= 2), conv_code, genus_etage[e])
        genus_etage[e] = np.where(here & (cls == 1) & (genus_etage[e] == CLEAR), GENUS_CODES["Cu"], genus_etage[e])
    lowest = np.where(cls > 0, np.fmin(lowest, inp.lcl_agl_m), lowest)
    highest = np.where(cls > 0, np.fmax(highest, conv_top), highest)

    only_high = (genus_etage[ETAGE_LOW] == CLEAR) & (genus_etage[ETAGE_MID] == CLEAR) & (cls == 0)
    spissatus = (genus_level == GENUS_CODES["Ci"]) & (
        only_high & (inp.column_condensate >= s["spissatus_min_condensate_kg_m2"]))[None]
    species |= np.where(spissatus, SPECIES_BITS["spissatus"], 0)
    species = np.where(inp.underground, 0, species)
    flags = np.bitwise_or.reduce(species, axis=0)

    return {
        "cloud_fraction": frac,
        "cloud_genus": np.where(inp.underground, np.nan, genus_level),
        "potential_instability": instability,
        "cloud_cover_low": covers["low"], "cloud_cover_mid": covers["mid"], "cloud_cover_high": covers["high"],
        "cloud_cover_total_diag": max_random_cover(frac),
        "ceiling_m": ceiling, "lowest_cloud_base_m": lowest, "highest_cloud_top_m": highest,
        "genus_low": genus_etage[ETAGE_LOW], "genus_mid": genus_etage[ETAGE_MID], "genus_high": genus_etage[ETAGE_HIGH],
        "convective_class": cls.astype(float), "convective_top_m": conv_top, "convective_top_temp_k": conv_top_t,
        "species_flags": flags.astype(float),
        "cloud_species": np.where(inp.underground, np.nan, species.astype(float)),
    }


FT_PER_M = 1.0 / 0.3048


def _convective_species(cls: int, depth_m: float, profile: CloudProfile) -> list[str]:
    if cls >= 3:
        return ["capillatus" if cls == 4 else "calvus"]
    if cls == 2:
        return ["congestus"]
    return ["humilis" if depth_m < profile.convection["humilis_max_depth_m"] else "mediocris"]


def column_layers(levels_hpa: np.ndarray, fraction: np.ndarray, genus: np.ndarray, gh: np.ndarray, elevation: float,
                  sp_hpa: float, species: np.ndarray, convective_class: float, convective_top_m: float, lcl_agl_m: float,
                  profile: CloudProfile) -> list[dict[str, object]]:
    """Cloud layers of one column (1-D arrays over levels), same layer rule as diagnose_clouds; `species` is the
    per-level cloud_species bit field (the species of the layer each level belongs to)."""
    frac = np.nan_to_num(np.asarray(fraction, dtype=float))
    cloudy = frac >= profile.layer_min_fraction
    lower, _ = level_interfaces(np.asarray(gh, dtype=float)[:, None, None], np.array([[elevation]]))
    out: list[dict[str, object]] = []
    k = 0
    while k < len(frac):
        if not cloudy[k]:
            k += 1
            continue
        top = k
        while top + 1 < len(frac) and cloudy[top + 1]:
            top += 1
        code = int(genus[k]) if np.isfinite(genus[k]) else INDETERMINATE
        n_ok = float(oktas(np.array(frac[k:top + 1].max())))
        base_agl = max(float(gh[k]) - elevation, 0.0)
        out.append({
            "kind": "layer", "genus": GENUS_NAMES.get(code, "indeterminate"),
            "etage": ETAGE_NAMES[int(sigma_etage(np.array(levels_hpa[k] / sp_hpa), profile))],
            "species": [name for name, bit in SPECIES_BITS.items()
                        if np.isfinite(species[k]) and int(species[k]) & bit],
            "base_agl_m": base_agl, "base_uncertainty_m": float(gh[k] - lower[k, 0, 0]),
            "base_ft": int(base_agl * FT_PER_M), "top_amsl_m": float(gh[top]),
            "top_fl": flight_level(float(levels_hpa[top])), "oktas": int(n_ok), "amount": amount_code(n_ok),
        })
        k = top + 1
    cls = 0 if np.isnan(convective_class) else int(convective_class)
    if cls > 0:
        depth = float(convective_top_m) - (elevation + float(lcl_agl_m))
        out.append({
            "kind": "convective", "genus": "Cb" if cls >= 3 else "Cu", "etage": None,
            "species": _convective_species(cls, depth, profile), "base_agl_m": float(lcl_agl_m),
            "base_uncertainty_m": None, "base_ft": int(float(lcl_agl_m) * FT_PER_M),
            "top_amsl_m": float(convective_top_m), "top_fl": None, "oktas": None, "amount": None,
        })
    return sorted(out, key=lambda lay: lay["base_agl_m"])  # type: ignore[arg-type, return-value]


def metar_cloud_group(layers: list[dict[str, object]]) -> str:
    """Model cloud line in METAR form (ICAO Annex 3): amount + base in hundreds of feet (floor), CB/TCU suffix;
    '///' when the amount is unknown (sub-grid convection)."""
    if not layers:
        return "NSC"
    parts = []
    for lay in layers:
        hundreds = int(lay["base_ft"]) // 100  # type: ignore[call-overload]
        if lay["kind"] == "convective":
            suffix = "CB" if lay["genus"] == "Cb" else ("TCU" if lay["species"] == ["congestus"] else "")
            parts.append(f"///{hundreds:03d}{suffix}")
        else:
            parts.append(f"{lay['amount']}{hundreds:03d}")
    return " ".join(parts)
