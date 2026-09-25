import warnings
from dataclasses import replace

import numpy as np

from acf.awci.ops.cloud_profile import load_cloud_profile
from acf.awci.ops.clouds import (
    CLEAR, CLOUD_LEVEL_LAYERS, CLOUD_SURFACE_LAYERS, GENUS_CODES, SPECIES_BITS, CloudInputs, diagnose_clouds,
)
from acf.awci.ops.parcel import ParcelResult

# Fixed RHc so that the rule tests do not depend on the calibrated values of the shipped profile.
P = replace(load_cloud_profile(), rh_critical={"low": 0.80, "mid": 0.70, "high": 0.70})
LEVELS = np.array([1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100], dtype=float)
NL, NY, NX = len(LEVELS), 3, 3
ISA_GH = 44330.8 * (1 - (LEVELS / 1013.25) ** 0.190263)
ISA_T = np.maximum(288.15 - 0.0065 * ISA_GH, 216.65)


def _cube(values: np.ndarray) -> np.ndarray:
    return np.broadcast_to(np.asarray(values, dtype=float)[:, None, None], (NL, NY, NX)).copy()


def _inputs(r=None, theta_e=None, precip=0.0, ptype=0.0, el=None, mucape=0.0, lcl=500.0, wind10=0.0,
            elevation=None, u=None, condensate=0.0) -> CloudInputs:
    flat = np.zeros((NY, NX))
    el_index = np.full((NY, NX), -1 if el is None else el, dtype=np.int16)
    el_gh = flat + (np.nan if el is None else ISA_GH[el])
    el_t = flat + (np.nan if el is None else ISA_T[el])
    return CloudInputs(
        levels_hpa=LEVELS, lats=np.array([35.0, 35.25, 35.5]), lons=np.array([2.0, 2.25, 2.5]),
        r_pct=_cube(np.full(NL, 20.0) if r is None else r), t_k=_cube(ISA_T), q=_cube(np.full(NL, 1e-3)),
        gh=_cube(ISA_GH), u=_cube(np.zeros(NL)) if u is None else u, v=_cube(np.zeros(NL)),
        theta_e=_cube(np.linspace(300, 360, NL) if theta_e is None else theta_e),
        underground=np.zeros((NL, NY, NX), dtype=bool), sp_hpa=flat + 1013.0,
        elevation=flat if elevation is None else elevation, precip_rate_mm_h=flat + precip, ptype=flat + ptype,
        wind10_m_s=flat + wind10, mucape=flat + mucape, column_condensate=flat + condensate, lcl_agl_m=flat + lcl,
        parcel=ParcelResult(flat + 950.0, el_index, el_gh, el_t),
    )


def _r_with(levels: dict[int, float]) -> np.ndarray:
    r = np.full(NL, 20.0)
    for k, v in levels.items():
        r[k] = v
    return r


def test_clear_dry_column() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # no NumPy RuntimeWarning on empty columns
        out = diagnose_clouds(_inputs(), P)
    assert set(out) == set(CLOUD_LEVEL_LAYERS) | set(CLOUD_SURFACE_LAYERS)
    assert (out["cloud_genus"] == CLEAR).all() and (out["genus_low"] == CLEAR).all()
    assert np.isnan(out["ceiling_m"]).all() and (out["convective_class"] == 0).all()
    assert (out["cloud_cover_total_diag"] == 0).all()


def test_low_stable_saturated_layer_is_stratus_with_icao_ceiling() -> None:
    out = diagnose_clouds(_inputs(r=_r_with({0: 100.0})), P)  # 1000 hPa saturated, ~110 m AGL, stable
    assert out["genus_low"][1, 1] == GENUS_CODES["St"] and out["cloud_genus"][0, 1, 1] == GENUS_CODES["St"]
    assert np.isclose(out["ceiling_m"][1, 1], ISA_GH[0])  # OVC based at the level gh above flat 0 m terrain


def test_potentially_unstable_low_layer_is_stratocumulus() -> None:
    theta_e = np.linspace(300, 360, NL)
    theta_e[1] = theta_e[0] - 3.0  # d(theta_e)/dz < 0 at 1000 hPa
    out = diagnose_clouds(_inputs(r=_r_with({0: 100.0}), theta_e=theta_e), P)
    assert out["genus_low"][1, 1] == GENUS_CODES["Sc"]


def test_deep_precipitating_layer_is_nimbostratus() -> None:
    r = _r_with({k: 100.0 for k in range(1, 6)})  # 925-500 hPa saturated, > 3 km deep
    out = diagnose_clouds(_inputs(r=r, precip=2.0, ptype=1.0), P)
    assert out["genus_low"][1, 1] == GENUS_CODES["Ns"]


def test_mid_etage_genera_and_high_etage_genera() -> None:
    thin_mid = diagnose_clouds(_inputs(r=_r_with({4: 100.0})), P)  # 600 hPa only
    assert thin_mid["genus_mid"][1, 1] == GENUS_CODES["Ac"]
    thick_mid = diagnose_clouds(_inputs(r=_r_with({3: 100.0, 4: 100.0, 5: 100.0})), P)
    assert thick_mid["genus_mid"][1, 1] == GENUS_CODES["As"]
    cs = diagnose_clouds(_inputs(r=_r_with({8: 100.0})), P)  # 250 hPa overcast, stable
    assert cs["genus_high"][1, 1] == GENUS_CODES["Cs"]
    ci = diagnose_clouds(_inputs(r=_r_with({8: 80.0})), P)  # partial cover
    assert ci["genus_high"][1, 1] == GENUS_CODES["Ci"]


def test_deep_cold_topped_precipitating_convection_is_cb_capillatus() -> None:
    out = diagnose_clouds(_inputs(el=9, mucape=1500.0, precip=5.0, ptype=1.0, lcl=800.0, condensate=2.0), P)  # EL 200 hPa ~ -57 C
    assert out["convective_class"][1, 1] == 4 and out["genus_low"][1, 1] == GENUS_CODES["Cb"]
    assert np.isclose(out["convective_top_m"][1, 1], ISA_GH[9])
    assert np.isclose(out["lowest_cloud_base_m"][1, 1], 800.0)
    assert np.isnan(out["ceiling_m"][1, 1])  # convective cover unknown: never used as a ceiling


def test_moderate_convection_is_tcu_and_shallow_is_cu() -> None:
    tcu = diagnose_clouds(_inputs(el=5, mucape=600.0, lcl=800.0, condensate=0.3), P)  # EL 500 hPa, ~4.8 km deep, no precip
    assert tcu["convective_class"][1, 1] == 2
    cu = diagnose_clouds(_inputs(el=2, mucape=200.0, lcl=800.0, condensate=0.05), P)  # EL 850 hPa
    assert cu["convective_class"][1, 1] == 1
    capped = diagnose_clouds(_inputs(el=5, mucape=20.0, lcl=800.0, condensate=0.3), P)  # CAPE below the profile minimum
    assert capped["convective_class"][1, 1] == 0
    no_condensate = diagnose_clouds(_inputs(el=5, mucape=600.0, lcl=800.0, condensate=0.0), P)  # no model cloud
    assert no_condensate["convective_class"][1, 1] == 0


def test_castellanus_flag_on_conditionally_unstable_mid_layer() -> None:
    inp = _inputs(r=_r_with({4: 100.0}))
    inp.t_k[5] = inp.t_k[4] - 12.0  # steep lapse above the 600 hPa base: theta_e* decreases upward
    out = diagnose_clouds(inp, P)
    assert int(out["species_flags"][1, 1]) & SPECIES_BITS["castellanus"]


def test_no_lenticularis_over_flat_terrain_and_edges_are_safe() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        out = diagnose_clouds(_inputs(r=_r_with({4: 100.0}), u=_cube(np.full(NL, 20.0))), P)
    assert not (out["species_flags"].astype(int) & SPECIES_BITS["lenticularis"]).any()


def test_fractus_under_precipitation_with_wind() -> None:
    out = diagnose_clouds(_inputs(r=_r_with({0: 100.0}), precip=1.0, ptype=1.0, wind10=12.0), P)
    assert int(out["species_flags"][1, 1]) & SPECIES_BITS["fractus"]


def test_underground_levels_are_nan() -> None:
    inp = _inputs(r=_r_with({0: 100.0}))
    inp.underground[0] = True
    out = diagnose_clouds(inp, P)
    assert np.isnan(out["cloud_fraction"][0]).all() and np.isnan(out["cloud_genus"][0]).all()


def test_etage_genus_describes_the_cloud_present_in_the_etage() -> None:
    deep = diagnose_clouds(_inputs(r=_r_with({k: 100.0 for k in range(4, 11)})), P)  # 600-150 hPa, based mid
    assert deep["genus_mid"][1, 1] == GENUS_CODES["As"] and deep["genus_high"][1, 1] == GENUS_CODES["As"]
    assert deep["genus_low"][1, 1] == CLEAR
    cb = diagnose_clouds(_inputs(el=9, mucape=1500.0, precip=5.0, ptype=1.0, lcl=800.0, condensate=2.0), P)
    assert cb["genus_low"][1, 1] == cb["genus_mid"][1, 1] == cb["genus_high"][1, 1] == GENUS_CODES["Cb"]
    tcu = diagnose_clouds(_inputs(el=5, mucape=600.0, lcl=800.0, condensate=0.3), P)  # top 500 hPa (mid etage)
    assert tcu["genus_mid"][1, 1] == GENUS_CODES["Cu"] and tcu["genus_high"][1, 1] == CLEAR


def test_dry_high_based_deep_cold_convection_is_still_cb() -> None:
    # Sahel/Sahara high-based Cb: no rain at the ground (virga), glaciated top: pilots need "CB", not "TCU"
    out = diagnose_clouds(_inputs(el=9, mucape=1500.0, precip=0.0, lcl=2500.0, condensate=0.5), P)
    assert out["convective_class"][1, 1] == 4
