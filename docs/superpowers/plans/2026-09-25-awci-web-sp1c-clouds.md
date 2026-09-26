# AWCI Web SP1C — Nuages et champs étendus : plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** diagnostiquer, à partir des vrais champs IFS, la fraction nuageuse par niveau, les couvertures par étage, les couches (base/sommet/octas), le plafond OACI, la convection (Cu/TCU/Cb, sommet), le genre OMM probable par couche et par étage, les espèces diagnosticables, la température d'émission des sommets, le condensat colonne, la neige et la pluie verglaçante ; les stocker dans le cube SP1 et les servir par `/clouds`, `/volume`, `/terrain`.

**Architecture:** trois modules NumPy purs sans eccodes (`parcel.py`, `accum.py`, `clouds.py`) et un profil versionné (`cloud_profile.py` + `config/awci/clouds/cloud-v1.json`), appelés par `pipeline.compute_step` ; l'ingestion garde l'échéance précédente pour les cumuls ; le routeur lit le cube et réutilise `clouds.column_layers` (aucune science dupliquée côté API).

**Tech Stack:** Python 3.12, NumPy, eccodes (ingestion seulement), netCDF4/xarray, FastAPI, pytest.

**Spec:** `docs/superpowers/specs/2026-09-25-awci-web-sp1c-clouds-design.md`

## Global Constraints

- Aucun import d'eccodes dans `parcel.py`, `accum.py`, `clouds.py`, `cloud_profile.py`, `registry.py`, `acf/web/awci_router.py` (test existant `test_router_imports_without_eccodes`).
- Valeur manquante = `NaN` dans le cube / `null` en JSON, jamais 0 ; cumul sans échéance précédente = `NaN`.
- Codes de genre = table OMM 0500 (Ci 0, Cc 1, Cs 2, Ac 3, As 4, Ns 5, Sc 6, St 7, Cu 8, Cb 9) ; `-1` = clair, `-2` = indéterminé ; `NaN` = sous le relief.
- Seuils non normatifs dans `cloud-v1.json` uniquement, statut HYPOTHESIS dans `/registry`.
- σ Stefan–Boltzmann = 5.670374419e-8 W m⁻² K⁻⁴ (CODATA 2018, exact) ; 1 ft = 0,3048 m (exact) ; g = `acf.science.constants.G`.
- L'AWCI `operational-v1` n'est pas modifié (les tests de parité SP1 doivent rester verts).
- Commits : trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` + `Claude-Session: https://claude.ai/code/session_017rtRvi8FETpCKyneMvVvBM`.
- Tests : `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_*.py tests/test_web_awci_api.py` ; `ruff check` et `mypy` propres sur les fichiers touchés.

## Review Focus

1. **Cube SP1 sans couches nuageuses** (runs ingérés avant SP1C, encore sur disque) : `/field`, `/point`, `/profile` doivent continuer à répondre et `/clouds`, `/volume` renvoyer 404 explicite (« run antérieur à SP1C »), jamais 500 (`KeyError`). → Task 8.
2. **Échéance précédente manquante** (échec de téléchargement au milieu du run) : les cumuls de l'échéance suivante sont `NaN`, pas une différence sur 6 h présentée comme 3 h. → Task 7.
3. **Colonne entièrement sous le relief ou sans nuage** : `diagnose_clouds` ne lève aucun avertissement NumPy et renvoie clair/`NaN` cohérents. → Task 5.
4. **Relief plat** (pente nulle, Froude indéfini) : pas de *lenticularis*, pas de division par zéro visible. → Task 5.
5. **Point au bord du domaine** (voisinage 3×3 tronqué) : écart-type calculé avec bord répliqué, pas d'erreur d'indice. → Task 5.

---

### Task 1: Thermodynamique de la particule (`thermo.py` + `parcel.py`)

**Files:**
- Modify: `src/acf/awci/ops/thermo.py`
- Create: `src/acf/awci/ops/parcel.py`
- Test: `tests/test_awci_ops_parcel.py`

**Interfaces:**
- Produces: `thermo.saturation_specific_humidity(t_k, p_hpa)`, `thermo.virtual_temperature_k(t_k, q)`, `thermo.lcl_temperature_bolton_k(t_k, td_k)`, `parcel.ParcelResult(p_lcl_hpa, el_index, el_gh_m, el_temp_k)`, `parcel.saturated_parcel_temperature_k(theta_e, p_hpa)`, `parcel.surface_parcel(t2m, d2m, sp_hpa, levels_hpa, t_env, q_env, gh, underground) -> ParcelResult`.

- [ ] **Step 1: tests (échouent)**

```python
"""Surface parcel ascent: Bolton LCL, theta-e conserving pseudo-adiabat, virtual-temperature EL."""

import numpy as np

from acf.awci.ops.parcel import saturated_parcel_temperature_k, surface_parcel
from acf.awci.ops.thermo import (
    lcl_temperature_bolton_k,
    saturation_specific_humidity,
    saturation_vapor_pressure_hpa,
    theta_e_bolton_k,
    virtual_temperature_k,
)
LEVELS = np.array([1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100], dtype=float)


def test_saturation_specific_humidity_matches_definition() -> None:
    es = saturation_vapor_pressure_hpa(np.array(293.15))
    assert np.isclose(saturation_specific_humidity(np.array(293.15), np.array(1000.0)),
                      0.622 * es / (1000.0 - 0.378 * es))


def test_virtual_temperature() -> None:
    assert np.isclose(virtual_temperature_k(np.array(300.0), np.array(0.01)), 300.0 * (1 + (1 / 0.622 - 1) * 0.01))


def test_lcl_temperature_bolton_eq15_saturated_and_dry() -> None:
    assert np.isclose(lcl_temperature_bolton_k(np.array(290.0), np.array(290.0)), 290.0)
    t_l = lcl_temperature_bolton_k(np.array(303.15), np.array(283.15))
    assert np.isclose(t_l, 1.0 / (1.0 / (283.15 - 56.0) + np.log(303.15 / 283.15) / 800.0) + 56.0)
    assert 270.0 < t_l < 283.15


def test_saturated_parcel_conserves_theta_e() -> None:
    p = np.array([850.0, 500.0, 200.0])
    theta_e = np.full(3, 340.0)
    t = saturated_parcel_temperature_k(theta_e, p)
    back = theta_e_bolton_k(t, saturation_specific_humidity(t, p), p)
    np.testing.assert_allclose(back, 340.0, atol=0.05)
    assert np.all(np.diff(t) < 0)  # colder aloft


def _column(t_env_c: np.ndarray, q_env: np.ndarray) -> tuple:
    shape = (len(LEVELS), 1, 1)
    gh = (44330.8 * (1 - (LEVELS / 1013.25) ** 0.190263)).reshape(shape)  # ISA heights, monotonic
    return (t_env_c + 273.15).reshape(shape), q_env.reshape(shape), gh


def test_unstable_column_has_el_high_and_stable_column_has_none() -> None:
    t_env_c = np.array([30, 24, 18, 6, -2, -11, -22, -37, -46, -55, -60, -65], dtype=float)
    q = np.full(len(LEVELS), 1e-4)
    t_env, q_env, gh = _column(t_env_c, q)
    under = np.zeros_like(t_env, dtype=bool)
    moist = surface_parcel(np.array([[305.0]]), np.array([[297.0]]), np.array([[1005.0]]), LEVELS,
                           t_env, q_env, gh, under)
    assert moist.el_index[0, 0] >= 7 and moist.el_temp_k[0, 0] < 253.15  # deep convection, top colder than -20 C
    assert moist.p_lcl_hpa[0, 0] < 1005.0
    warm_aloft = t_env + 25.0  # strong inversion everywhere: no buoyancy
    dry = surface_parcel(np.array([[290.0]]), np.array([[270.0]]), np.array([[1005.0]]), LEVELS,
                         warm_aloft, q_env, gh, under)
    assert dry.el_index[0, 0] == -1 and np.isnan(dry.el_gh_m[0, 0]) and np.isnan(dry.el_temp_k[0, 0])


def test_underground_levels_never_buoyant() -> None:
    t_env_c = np.array([30, 24, 18, 6, -2, -11, -22, -37, -46, -55, -60, -65], dtype=float)
    t_env, q_env, gh = _column(t_env_c, np.full(len(LEVELS), 1e-4))
    under = np.ones_like(t_env, dtype=bool)
    res = surface_parcel(np.array([[305.0]]), np.array([[297.0]]), np.array([[1005.0]]), LEVELS, t_env, q_env,
                         gh, under)
    assert res.el_index[0, 0] == -1


def test_parcel_below_lcl_is_not_buoyant_when_colder_than_dry_adiabat_env() -> None:
    # very dry surface air: LCL above 700 hPa, so 925/850 hPa are on the dry adiabat and never count for the EL
    t_env_c = np.array([30, 24, 18, 6, -2, -11, -22, -37, -46, -55, -60, -65], dtype=float)
    t_env, q_env, gh = _column(t_env_c, np.full(len(LEVELS), 1e-4))
    res = surface_parcel(np.array([[305.0]]), np.array([[260.0]]), np.array([[1005.0]]), LEVELS, t_env, q_env, gh,
                         np.zeros_like(t_env, dtype=bool))
    assert res.p_lcl_hpa[0, 0] < 700.0
    assert res.el_index[0, 0] == -1 or LEVELS[res.el_index[0, 0]] < res.p_lcl_hpa[0, 0]
```

- [ ] **Step 2:** `pytest tests/test_awci_ops_parcel.py -q` → FAIL (ImportError).

- [ ] **Step 3: implémentation**

Ajouter à `thermo.py` (docstring de module : trois lignes décrivant ces formules) :

```python
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
```

Créer `parcel.py` :

```python
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
```

- [ ] **Step 4:** `pytest tests/test_awci_ops_parcel.py tests/test_awci_ops_thermo.py -q` → PASS.
- [ ] **Step 5:** commit `feat(awci-ops): surface parcel ascent (Bolton LCL, theta-e pseudo-adiabat, Tv EL)`.

---

### Task 2: Cumuls, OLR, neige, condensat (`accum.py`)

**Files:** Create `src/acf/awci/ops/accum.py` ; Test `tests/test_awci_ops_accum.py`

**Interfaces:**
- Produces: `STEFAN_BOLTZMANN`, `olr_w_m2(ttr_now, ttr_prev, interval_h)`, `effective_emission_temperature_k(olr)`, `interval_amount_mm(acc_now_m, acc_prev_m)`, `snow_depth_cm(sd_m_we, rsn_kg_m3)`, `freezing_precip_mm(tp_now_m, tp_prev_m, ptype_now, ptype_prev)`, `column_condensate(tcw, tcwv)`, `accumulated_layers(sfc_now, sfc_prev, interval_h) -> dict[str, ndarray]` (clés `cloud_top_teff_k`, `snowfall_mm`, `freezing_precip_mm`).

- [ ] **Step 1: tests**

```python
"""Accumulated IFS fields differenced between steps; OLR effective temperature; snow; condensate."""

import numpy as np

from acf.awci.ops.accum import (
    STEFAN_BOLTZMANN,
    accumulated_layers,
    column_condensate,
    effective_emission_temperature_k,
    freezing_precip_mm,
    interval_amount_mm,
    olr_w_m2,
    snow_depth_cm,
)


def test_olr_from_ttr_difference() -> None:
    olr = olr_w_m2(np.array(-240.0 * 3 * 3600 * 2), np.array(-240.0 * 3 * 3600), 3.0)
    assert np.isclose(olr, 240.0)
    assert np.isnan(olr_w_m2(np.array(0.0), np.array(0.0), 3.0))  # no emission = no data, not 0 K


def test_effective_temperature_255k_for_240_w_m2() -> None:
    assert STEFAN_BOLTZMANN == 5.670374419e-8
    assert np.isclose(effective_emission_temperature_k(np.array(240.0)), 255.064, atol=1e-3)


def test_interval_amount_clips_packing_noise() -> None:
    assert np.isclose(interval_amount_mm(np.array(0.0035), np.array(0.0010)), 2.5)
    assert interval_amount_mm(np.array(0.0010), np.array(0.0010000001)) == 0.0


def test_snow_depth_from_water_equivalent_and_density() -> None:
    assert np.isclose(snow_depth_cm(np.array(0.03), np.array(300.0)), 10.0)
    assert snow_depth_cm(np.array(0.0), np.array(100.0)) == 0.0
    assert np.isnan(snow_depth_cm(np.array(0.01), np.array(0.0)))


def test_freezing_precip_requires_freezing_type_at_both_ends() -> None:
    now, prev = np.array([0.004, 0.004, 0.004]), np.array([0.001, 0.001, 0.001])
    out = freezing_precip_mm(now, prev, np.array([3.0, 12.0, 1.0]), np.array([3.0, 3.0, 3.0]))
    np.testing.assert_allclose(out, [3.0, 3.0, 0.0])


def test_column_condensate_non_negative() -> None:
    np.testing.assert_allclose(column_condensate(np.array([30.5, 20.0]), np.array([30.0, 20.1])), [0.5, 0.0])


def test_accumulated_layers_nan_without_previous_step() -> None:
    sfc = {k: np.ones((2, 2)) for k in ("ttr", "sf", "tp", "ptype")}
    out = accumulated_layers(sfc, None, None)
    assert set(out) == {"cloud_top_teff_k", "snowfall_mm", "freezing_precip_mm"}
    assert all(np.isnan(v).all() for v in out.values())
```

- [ ] **Step 2:** FAIL (ImportError).
- [ ] **Step 3: implémentation**

```python
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
```

- [ ] **Step 4:** PASS. **Step 5:** commit `feat(awci-ops): OLR effective temperature, snow and freezing precipitation from IFS accumulations`.

---

### Task 3: Profil nuageux versionné

**Files:** Create `src/acf/awci/ops/cloud_profile.py`, `config/awci/clouds/cloud-v1.json` ; Test `tests/test_awci_ops_cloud_profile.py`

**Interfaces:** Produces `CloudProfile` (champs ci-dessous, `to_dict()`), `DEFAULT_CLOUD_PROFILE_PATH`, `load_cloud_profile(path=DEFAULT_CLOUD_PROFILE_PATH) -> CloudProfile` (ValueError sur clé manquante / borne invalide).

- [ ] **Step 1: tests**

```python
import json
from pathlib import Path

import pytest

from acf.awci.ops.cloud_profile import DEFAULT_CLOUD_PROFILE_PATH, load_cloud_profile


def test_default_profile_loads_with_documented_values() -> None:
    p = load_cloud_profile()
    assert p.name == "cloud-v1" and p.sigma_low_mid == 0.8 and p.sigma_mid_high == 0.45
    assert p.layer_min_fraction == 0.125 and p.ceiling_max_base_m == 6000.0
    assert p.convection["capillatus_temp_k"] == 235.15 and p.convection["glaciation_temp_k"] == 253.15
    assert set(p.references) >= {"rh_critical", "sigma_bounds", "layer_min_fraction", "ceiling_max_base_m"}


@pytest.mark.parametrize("patch", [
    {"rh_critical": {"low": 1.2, "mid": 0.7, "high": 0.7}},
    {"sigma_bounds": {"low_mid": 0.4, "mid_high": 0.45}},
    {"convection": {}},
])
def test_invalid_profiles_rejected(tmp_path: Path, patch: dict) -> None:
    raw = json.loads(DEFAULT_CLOUD_PROFILE_PATH.read_text()) | patch
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError):
        load_cloud_profile(path)
```

- [ ] **Step 2:** FAIL.
- [ ] **Step 3:** `config/awci/clouds/cloud-v1.json` :

```json
{
  "name": "cloud-v1",
  "version": "1.0.0",
  "rh_critical": {"low": 0.80, "mid": 0.70, "high": 0.70},
  "sigma_bounds": {"low_mid": 0.8, "mid_high": 0.45},
  "layer_min_fraction": 0.125,
  "ceiling_max_base_m": 6000.0,
  "bias_degraded_threshold": 0.15,
  "convection": {
    "cape_min_j_kg": 100.0, "precip_min_mm_h": 0.1, "cb_min_depth_m": 6000.0, "tcu_min_depth_m": 3000.0,
    "humilis_max_depth_m": 1000.0, "glaciation_temp_k": 253.15, "capillatus_temp_k": 235.15
  },
  "genus": {
    "st_max_base_m": 600.0, "ns_min_depth_m": 3000.0, "as_min_depth_m": 1500.0, "cc_max_depth_m": 1500.0,
    "cs_min_oktas": 5, "continuous_precip_mm_h": 0.1
  },
  "species": {
    "lenticularis_min_wind_m_s": 10.0, "lenticularis_min_relief_m": 300.0, "lenticularis_froude_min": 0.5,
    "lenticularis_froude_max": 1.5, "fractus_min_wind_m_s": 10.0, "nebulosus_min_oktas": 7,
    "nebulosus_max_std": 0.1, "spissatus_min_condensate_kg_m2": 0.05
  },
  "references": {
    "rh_critical": "Sundqvist, Berge & Kristjansson (1989), Mon. Wea. Rev. 117; initial values ACF choice (HYPOTHESIS), calibrated against IFS tcc by tools/awci/calibrate_cloud_rhc.py",
    "sigma_bounds": "ECMWF parameter database, low/medium/high cloud cover (params 186-188)",
    "layer_min_fraction": "1 okta, smallest reportable amount (FEW): ICAO Annex 3 App. 3, WMO code table 2700",
    "ceiling_max_base_m": "ICAO Annex 2, definition of ceiling (below 6000 m / 20000 ft, more than half the sky)",
    "glaciation_temp_k": "-20 degC: glaciation of convective tops observed near -20 to -25 degC, Rosenfeld & Lensky (1998), BAMS 79",
    "capillatus_temp_k": "-38 degC: homogeneous freezing of supercooled droplets, Pruppacher & Klett (1997)",
    "lenticularis_froude": "mountain-wave regime Fr = U/(N h) of order 1, Durran (1990), Meteor. Monogr. 23; bounds ACF choice",
    "other": "ACF choices, status HYPOTHESIS, to be validated against METAR cloud groups (SP3)"
  },
  "calibration": null
}
```

`cloud_profile.py` :

```python
"""
Versioned thresholds of the cloud diagnostics (config/awci/clouds/<name>.json).

Normative values (ICAO ceiling, 1 okta, ECMWF etage bounds) and ACF choices (status HYPOTHESIS)
live side by side; every group carries a reference in ``references``.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_CLOUD_PROFILE_PATH = REPO_ROOT / "config" / "awci" / "clouds" / "cloud-v1.json"

_CONVECTION = ("cape_min_j_kg", "precip_min_mm_h", "cb_min_depth_m", "tcu_min_depth_m", "humilis_max_depth_m",
               "glaciation_temp_k", "capillatus_temp_k")
_GENUS = ("st_max_base_m", "ns_min_depth_m", "as_min_depth_m", "cc_max_depth_m", "cs_min_oktas",
          "continuous_precip_mm_h")
_SPECIES = ("lenticularis_min_wind_m_s", "lenticularis_min_relief_m", "lenticularis_froude_min",
            "lenticularis_froude_max", "fractus_min_wind_m_s", "nebulosus_min_oktas", "nebulosus_max_std",
            "spissatus_min_condensate_kg_m2")


@dataclass(frozen=True)
class CloudProfile:
    name: str
    version: str
    rh_critical: dict[str, float]
    sigma_low_mid: float
    sigma_mid_high: float
    layer_min_fraction: float
    ceiling_max_base_m: float
    bias_degraded_threshold: float
    convection: dict[str, float]
    genus: dict[str, float]
    species: dict[str, float]
    references: dict[str, str]
    calibration: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _group(raw: dict[str, Any], key: str, names: tuple[str, ...]) -> dict[str, float]:
    group = raw.get(key, {})
    missing = [n for n in names if n not in group]
    if missing:
        raise ValueError(f"cloud profile: {key} lacks {missing}")
    return {n: float(group[n]) for n in names}


def load_cloud_profile(path: Path | str = DEFAULT_CLOUD_PROFILE_PATH) -> CloudProfile:
    raw: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
    rhc = _group(raw, "rh_critical", ("low", "mid", "high"))
    if not all(0.0 < v < 1.0 for v in rhc.values()):
        raise ValueError(f"cloud profile: rh_critical must lie in (0, 1), got {rhc}")
    bounds = _group(raw, "sigma_bounds", ("low_mid", "mid_high"))
    if not 0.0 < bounds["mid_high"] < bounds["low_mid"] < 1.0:
        raise ValueError(f"cloud profile: need 0 < mid_high < low_mid < 1, got {bounds}")
    min_fraction = float(raw["layer_min_fraction"])
    if not 0.0 < min_fraction < 1.0:
        raise ValueError("cloud profile: layer_min_fraction must lie in (0, 1)")
    return CloudProfile(
        name=str(raw["name"]), version=str(raw["version"]), rh_critical=rhc,
        sigma_low_mid=bounds["low_mid"], sigma_mid_high=bounds["mid_high"], layer_min_fraction=min_fraction,
        ceiling_max_base_m=float(raw["ceiling_max_base_m"]),
        bias_degraded_threshold=float(raw["bias_degraded_threshold"]),
        convection=_group(raw, "convection", _CONVECTION), genus=_group(raw, "genus", _GENUS),
        species=_group(raw, "species", _SPECIES), references=dict(raw.get("references", {})),
        calibration=raw.get("calibration"),
    )
```

- [ ] **Step 4:** PASS. **Step 5:** commit `feat(awci-ops): versioned cloud diagnostics profile cloud-v1`.

---

### Task 4: Nébulosité par niveau, étages, recouvrement, octas (`clouds.py`, partie 1)

**Files:** Create `src/acf/awci/ops/clouds.py` ; Test `tests/test_awci_ops_clouds_core.py`

**Interfaces:**
- Produces: constantes `ETAGE_LOW/MID/HIGH`, `ETAGE_NAMES`, `GENUS_CODES`, `GENUS_NAMES`, `CLEAR=-1`, `INDETERMINATE=-2`, `SPECIES_BITS`, `CONVECTIVE_CLASSES` ; fonctions `sigma_etage(sigma, profile)`, `etage_codes(levels_hpa, sp_hpa, profile)`, `sundqvist_fraction(rh_pct, rh_critical)`, `level_cloud_fraction(r_pct, etage, profile)`, `max_random_cover(fraction, mask=None)`, `oktas(cover)`, `amount_code(n_oktas)`, `level_interfaces(gh, elevation)`, `vertical_gradient_per_km(f, gh)`.

- [ ] **Step 1: tests**

```python
import numpy as np
import pytest

from acf.awci.ops.cloud_profile import load_cloud_profile
from acf.awci.ops.clouds import (
    ETAGE_HIGH, ETAGE_LOW, ETAGE_MID, amount_code, etage_codes, level_interfaces, max_random_cover, oktas,
    sundqvist_fraction, vertical_gradient_per_km,
)

P = load_cloud_profile()


def test_sundqvist_bounds_and_monotonic() -> None:
    rh = np.array([50.0, 80.0, 90.0, 99.0, 100.0, 104.0, np.nan])
    c = sundqvist_fraction(rh, 0.8)
    assert c[0] == 0.0 and c[1] == 0.0 and c[4] == 1.0 and c[5] == 1.0 and np.isnan(c[6])
    assert np.isclose(c[2], 1 - np.sqrt(0.1 / 0.2))
    assert np.all(np.diff(c[:5]) >= 0)


def test_etages_follow_ecmwf_sigma_bounds() -> None:
    levels = np.array([1000.0, 850.0, 700.0, 500.0, 400.0])
    codes = etage_codes(levels, np.array([[1000.0]]), P)[:, 0, 0]
    assert codes.tolist() == [ETAGE_LOW, ETAGE_LOW, ETAGE_MID, ETAGE_MID, ETAGE_HIGH]  # 0.85 low, 0.8 mid, 0.45 high
    over_plateau = etage_codes(levels, np.array([[850.0]]), P)[:, 0, 0]  # sigma follows the terrain
    assert over_plateau[2] == ETAGE_LOW  # 700/850 = 0.82


@pytest.mark.parametrize("column,expected", [
    ([0.0, 0.5, 0.0], 0.5),                 # single layer
    ([0.3, 0.6, 0.0], 0.6),                 # adjacent: maximum overlap
    ([0.5, 0.0, 0.5], 0.75),                # separated: random overlap 1 - 0.5 * 0.5
    ([1.0, 0.0, 0.2], 1.0),
    ([np.nan, 0.4, 0.0], 0.4),              # below-ground NaN counts as clear
])
def test_max_random_overlap(column: list[float], expected: float) -> None:
    f = np.array(column)[:, None, None]
    assert np.isclose(max_random_cover(f)[0, 0], expected)


def test_overlap_restricted_to_an_etage_mask() -> None:
    f = np.array([0.5, 0.0, 0.5])[:, None, None]
    mask = np.array([True, True, False])[:, None, None]
    assert np.isclose(max_random_cover(f, mask)[0, 0], 0.5)


def test_oktas_follow_wmo_code_2700() -> None:
    out = oktas(np.array([0.0, 0.05, 0.3, 0.9, 0.999, 1.0, np.nan]))
    assert out[:6].tolist() == [0, 1, 2, 7, 7, 8] and np.isnan(out[6])
    assert [amount_code(n) for n in (1, 2, 3, 4, 5, 7, 8)] == ["FEW", "FEW", "SCT", "SCT", "BKN", "BKN", "OVC"]


def test_interfaces_midpoints_and_terrain_floor() -> None:
    gh = np.array([100.0, 800.0, 1500.0])[:, None, None]
    lower, upper = level_interfaces(gh, np.array([[300.0]]))
    assert lower[:, 0, 0].tolist() == [300.0, 450.0, 1150.0]
    assert upper[:, 0, 0].tolist() == [450.0, 1150.0, 1850.0]


def test_vertical_gradient_forward_then_backward_at_top() -> None:
    f = np.array([300.0, 305.0, 306.0])[:, None, None]
    gh = np.array([0.0, 1000.0, 2000.0])[:, None, None]
    assert vertical_gradient_per_km(f, gh)[:, 0, 0].tolist() == [5.0, 1.0, 1.0]
```

- [ ] **Step 2:** FAIL.
- [ ] **Step 3: implémentation** (début de `clouds.py`)

```python
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
```

- [ ] **Step 4:** PASS. **Step 5:** commit `feat(awci-ops): level cloud fraction, ECMWF etages, max-random overlap, oktas`.

---

### Task 5: Couches, genres, espèces, plafond, convection (`clouds.py`, partie 2)

**Files:** Modify `src/acf/awci/ops/clouds.py` ; Test `tests/test_awci_ops_clouds_diagnose.py`

**Interfaces:**
- Consumes: Task 1 `ParcelResult`, `thermo.saturation_specific_humidity`, `thermo.theta_e_bolton_k`, `kinematics.horizontal_gradients`, `acf.science.constants.G, KAPPA`.
- Produces: `CloudInputs` (dataclass : `levels_hpa, lats, lons, r_pct, t_k, q, gh, u, v, theta_e, underground` (3D) ; `sp_hpa, elevation, precip_rate_mm_h, ptype, wind10_m_s, mucape, column_condensate, lcl_agl_m` (2D) ; `parcel: ParcelResult`), `convective_diagnosis(inputs, profile) -> (cls, top_m, top_t_k)`, `diagnose_clouds(inputs, profile) -> dict[str, np.ndarray]` avec exactement les clés `CLOUD_LEVEL_LAYERS = ("cloud_fraction", "cloud_genus", "potential_instability")` et `CLOUD_SURFACE_LAYERS = ("cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "cloud_cover_total_diag", "ceiling_m", "lowest_cloud_base_m", "highest_cloud_top_m", "genus_low", "genus_mid", "genus_high", "convective_class", "convective_top_m", "convective_top_temp_k", "species_flags")`.

- [ ] **Step 1: tests** (colonnes synthétiques 12 niveaux, grille 3×3 identique ; helper `_inputs(**overrides)` construisant un `CloudInputs` sec et stable par défaut : T ISA, q faible, r = 20 %, vent nul, relief plat 0 m, sp 1013 hPa, pas de précipitation, `ParcelResult` sans EL)

```python
import warnings

import numpy as np

from acf.awci.ops.cloud_profile import load_cloud_profile
from acf.awci.ops.clouds import (
    CLEAR, CLOUD_LEVEL_LAYERS, CLOUD_SURFACE_LAYERS, GENUS_CODES, SPECIES_BITS, CloudInputs, diagnose_clouds,
)
from acf.awci.ops.parcel import ParcelResult

P = load_cloud_profile()
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
    out = diagnose_clouds(_inputs(el=9, mucape=1500.0, precip=5.0, ptype=1.0, lcl=800.0), P)  # EL 200 hPa ~ -57 C
    assert out["convective_class"][1, 1] == 4 and out["genus_low"][1, 1] == GENUS_CODES["Cb"]
    assert np.isclose(out["convective_top_m"][1, 1], ISA_GH[9])
    assert np.isclose(out["lowest_cloud_base_m"][1, 1], 800.0)
    assert np.isnan(out["ceiling_m"][1, 1])  # convective cover unknown: never used as a ceiling


def test_moderate_convection_is_tcu_and_shallow_is_cu() -> None:
    tcu = diagnose_clouds(_inputs(el=5, mucape=600.0, lcl=800.0), P)  # EL 500 hPa, ~4.8 km deep, no precip
    assert tcu["convective_class"][1, 1] == 2
    cu = diagnose_clouds(_inputs(el=2, mucape=200.0, lcl=800.0), P)  # EL 850 hPa
    assert cu["convective_class"][1, 1] == 1
    capped = diagnose_clouds(_inputs(el=5, mucape=20.0, lcl=800.0), P)  # CAPE below the profile minimum
    assert capped["convective_class"][1, 1] == 0


def test_castellanus_flag_on_conditionally_unstable_mid_layer() -> None:
    inp = _inputs(r=_r_with({4: 100.0}))
    inp.t_k[5] = inp.t_k[4] - 12.0  # steep lapse above the 600 hPa base: theta_e* decreases upward
    out = diagnose_clouds(inp, P)
    assert out["species_flags"][1, 1] & SPECIES_BITS["castellanus"]


def test_no_lenticularis_over_flat_terrain_and_edges_are_safe() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        out = diagnose_clouds(_inputs(r=_r_with({4: 100.0}), u=_cube(np.full(NL, 20.0))), P)
    assert not (out["species_flags"] & SPECIES_BITS["lenticularis"]).any()


def test_fractus_under_precipitation_with_wind() -> None:
    out = diagnose_clouds(_inputs(r=_r_with({0: 100.0}), precip=1.0, ptype=1.0, wind10=12.0), P)
    assert out["species_flags"][1, 1] & SPECIES_BITS["fractus"]


def test_underground_levels_are_nan() -> None:
    inp = _inputs(r=_r_with({0: 100.0}))
    inp.underground[0] = True
    out = diagnose_clouds(inp, P)
    assert np.isnan(out["cloud_fraction"][0]).all() and np.isnan(out["cloud_genus"][0]).all()
```

- [ ] **Step 2:** FAIL.
- [ ] **Step 3: implémentation** (ajouts à `clouds.py`)

```python
from dataclasses import dataclass

from acf.awci.ops.kinematics import horizontal_gradients
from acf.awci.ops.parcel import ParcelResult
from acf.awci.ops.thermo import saturation_specific_humidity, theta_e_bolton_k
from acf.science.constants import G, KAPPA

CLOUD_LEVEL_LAYERS: tuple[str, ...] = ("cloud_fraction", "cloud_genus", "potential_instability")
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
        ok = (inp.mucape >= c["cape_min_j_kg"]) & np.isfinite(depth) & (depth > 0.0)
        cb = ok & (depth >= c["cb_min_depth_m"]) & (top_t <= c["glaciation_temp_k"]) & (
            inp.precip_rate_mm_h >= c["precip_min_mm_h"])
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
    flags = np.zeros(shape2, dtype=np.int32)
    neb_low, neb_high, has_ci = (np.zeros(shape2, dtype=bool) for _ in range(3))

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
        for e in range(len(ETAGE_NAMES)):
            better = present & (e_base == e) & (cover > best_cover[e])
            genus_etage[e] = np.where(better, code, genus_etage[e])
            best_cover[e] = np.where(better, cover, best_cover[e])
        qualifies = present & (n_ok >= 5) & (base_agl < profile.ceiling_max_base_m)
        ceiling = np.where(qualifies, np.fmin(ceiling, base_agl), ceiling)
        lowest = np.where(present, np.fmin(lowest, base_agl), lowest)
        highest = np.where(present, np.fmax(highest, _take(inp.gh, top)), highest)
        cellular = present & np.isin(code, _CELLULAR)
        flags |= np.where(cellular & (_take(conditional, base) < 0.0), SPECIES_BITS["castellanus"], 0)
        flags |= np.where(cellular & _take(lenticular, base), SPECIES_BITS["lenticularis"], 0)
        flags |= np.where(present & np.isin(code, (GENUS_CODES["St"], GENUS_CODES["Sc"])) & (e_base == ETAGE_LOW)
                          & precip & (inp.wind10_m_s >= s["fractus_min_wind_m_s"]), SPECIES_BITS["fractus"], 0)
        dense = n_ok >= s["nebulosus_min_oktas"]
        neb_low |= present & (code == GENUS_CODES["St"]) & dense
        neb_high |= present & (code == GENUS_CODES["Cs"]) & dense
        has_ci |= present & (code == GENUS_CODES["Ci"])

    covers = {e: max_random_cover(frac, etage == code) for code, e in enumerate(ETAGE_NAMES)}
    smooth_low = _neighbourhood(covers["low"], "std") <= s["nebulosus_max_std"]
    smooth_high = _neighbourhood(covers["high"], "std") <= s["nebulosus_max_std"]
    flags |= np.where((neb_low & smooth_low) | (neb_high & smooth_high), SPECIES_BITS["nebulosus"], 0)

    cls, conv_top, conv_top_t = convective_diagnosis(inp, profile)
    conv_code = np.where(cls >= 3, GENUS_CODES["Cb"], GENUS_CODES["Cu"])
    with np.errstate(invalid="ignore"):
        in_conv = (cls > 0)[None] & (inp.gh >= (inp.elevation + inp.lcl_agl_m)[None]) & (inp.gh <= conv_top[None])
    genus_level = np.where(in_conv & (cls >= 2)[None], conv_code[None], genus_level)
    genus_level = np.where(in_conv & (cls == 1)[None] & (genus_level == CLEAR), GENUS_CODES["Cu"], genus_level)
    conv_etage = sigma_etage(inp.parcel.p_lcl_hpa / inp.sp_hpa, profile)
    for e in range(len(ETAGE_NAMES)):
        here = conv_etage == e
        genus_etage[e] = np.where(here & (cls >= 2), conv_code, genus_etage[e])
        genus_etage[e] = np.where(here & (cls == 1) & (genus_etage[e] == CLEAR), GENUS_CODES["Cu"], genus_etage[e])
    lowest = np.where(cls > 0, np.fmin(lowest, inp.lcl_agl_m), lowest)
    highest = np.where(cls > 0, np.fmax(highest, conv_top), highest)

    only_high = has_ci & (genus_etage[ETAGE_LOW] == CLEAR) & (genus_etage[ETAGE_MID] == CLEAR) & (cls == 0)
    flags |= np.where(only_high & (inp.column_condensate >= s["spissatus_min_condensate_kg_m2"]),
                      SPECIES_BITS["spissatus"], 0)

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
    }
```

- [ ] **Step 4:** `pytest tests/test_awci_ops_clouds_diagnose.py -q` → PASS ; si un cas synthétique échoue, corriger la **règle** seulement si elle contredit la spec, sinon corriger le cas (et le noter).
- [ ] **Step 5:** commit `feat(awci-ops): cloud layers, WMO genus and diagnosable species, ICAO ceiling, convective class`.

---

### Task 6: Couches d'un point pour l'API (`column_layers`) et ligne METAR

**Files:** Modify `src/acf/awci/ops/clouds.py` ; Test `tests/test_awci_ops_clouds_column.py`

**Interfaces:**
- Consumes: `acf.awci.ops.isa.flight_level`.
- Produces: `column_layers(levels_hpa, fraction, genus, gh, elevation, sp_hpa, species_flags, convective_class, convective_top_m, lcl_agl_m, profile) -> list[dict]` (chaque dict : `kind` "layer"|"convective", `etage`, `genus`, `species`, `base_agl_m`, `base_uncertainty_m`, `base_ft`, `top_amsl_m`, `top_fl`, `oktas`, `amount`), `metar_cloud_group(layers) -> str`, `FT_PER_M = 1 / 0.3048`.

- [ ] **Step 1: tests**

```python
import numpy as np

from acf.awci.ops.cloud_profile import load_cloud_profile
from acf.awci.ops.clouds import GENUS_CODES, SPECIES_BITS, column_layers, metar_cloud_group

P = load_cloud_profile()
LEVELS = np.array([1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100], dtype=float)
GH = 44330.8 * (1 - (LEVELS / 1013.25) ** 0.190263)


def test_two_layers_and_metar_line() -> None:
    frac = np.zeros(12)
    frac[1], frac[4] = 0.7, 1.0
    genus = np.full(12, -1.0)
    genus[1], genus[4] = GENUS_CODES["St"], GENUS_CODES["Ac"]  # castellanus applies to Ac, never to St
    layers = column_layers(LEVELS, frac, genus, GH, 0.0, 1013.0, float(SPECIES_BITS["castellanus"]), 0.0, np.nan, 500.0, P)
    assert [lay["genus"] for lay in layers] == ["St", "Ac"]
    assert [lay["etage"] for lay in layers] == ["low", "mid"]
    assert layers[0]["amount"] == "BKN" and layers[1]["amount"] == "OVC"
    assert layers[1]["species"] == ["castellanus"] and layers[0]["species"] == []
    assert layers[0]["base_ft"] == int(GH[1] / 0.3048)
    assert metar_cloud_group(layers) == f"BKN{int(GH[1] / 0.3048) // 100:03d} OVC{int(GH[4] / 0.3048) // 100:03d}"


def test_convective_layer_has_unknown_amount_and_cb_suffix() -> None:
    layers = column_layers(LEVELS, np.zeros(12), np.full(12, -1.0), GH, 200.0, 990.0, 0.0, 4.0, GH[9], 900.0, P)
    assert layers == [layers[0]] and layers[0]["kind"] == "convective" and layers[0]["genus"] == "Cb"
    assert layers[0]["species"] == ["capillatus"] and layers[0]["oktas"] is None
    assert metar_cloud_group(layers) == f"///{int(900.0 / 0.3048) // 100:03d}CB"


def test_clear_column_is_nsc() -> None:
    assert column_layers(LEVELS, np.zeros(12), np.full(12, -1.0), GH, 0.0, 1013.0, 0.0, 0.0, np.nan, 500.0, P) == []
    assert metar_cloud_group([]) == "NSC"
```

- [ ] **Step 2:** FAIL.
- [ ] **Step 3: implémentation**

```python
FT_PER_M = 1.0 / 0.3048
_LAYER_SPECIES = {"castellanus": _CELLULAR, "lenticularis": _CELLULAR,
                  "fractus": (GENUS_CODES["St"], GENUS_CODES["Sc"]),
                  "nebulosus": (GENUS_CODES["St"], GENUS_CODES["Cs"]), "spissatus": (GENUS_CODES["Ci"],)}


def _convective_species(cls: int, depth_m: float, profile: CloudProfile) -> list[str]:
    if cls >= 3:
        return ["capillatus" if cls == 4 else "calvus"]
    if cls == 2:
        return ["congestus"]
    return ["humilis" if depth_m < profile.convection["humilis_max_depth_m"] else "mediocris"]


def column_layers(levels_hpa: np.ndarray, fraction: np.ndarray, genus: np.ndarray, gh: np.ndarray, elevation: float,
                  sp_hpa: float, species_flags: float, convective_class: float, convective_top_m: float, lcl_agl_m: float,
                  profile: CloudProfile) -> list[dict[str, object]]:
    """Cloud layers of one column (1-D arrays over levels), same layer rule as diagnose_clouds."""
    from acf.awci.ops.isa import flight_level

    frac = np.nan_to_num(np.asarray(fraction, dtype=float))
    cloudy = frac >= profile.layer_min_fraction
    lower, _ = level_interfaces(np.asarray(gh, dtype=float)[:, None, None], np.array([[elevation]]))
    flags = 0 if np.isnan(species_flags) else int(species_flags)
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
                        if flags & bit and code in _LAYER_SPECIES[name]],
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
```

- [ ] **Step 4:** PASS. **Step 5:** commit `feat(awci-ops): per-column cloud layers and model METAR cloud group`.

---

### Task 7: Ingestion, registre, pipeline, manifest, fixtures réelles

**Files:**
- Modify: `src/acf/awci/ops/source_ecmwf.py` (`SFC_PARAMS` + `tcw tcwv ttr sf sd rsn tp`), `src/acf/awci/ops/registry.py`, `src/acf/awci/ops/pipeline.py`, `src/acf/awci/ops/ingest.py`, `tools/awci/make_ops_fixture.py` (arguments `--run --box --steps --out`), `tests/awci_ops_support.py` (`FixtureFetcher(root=FIXTURE)`, `WET_FIXTURE`, `WET_DOMAIN`)
- Regenerate: `tests/data/awci_ops/*` ; Create: `tests/data/awci_ops_wet/*` + `NOTICE.md`
- Test: `tests/test_awci_ops_pipeline_clouds.py` ; update `tests/test_awci_ops_source.py` si un compte est codé en dur (il utilise `len(SFC_PARAMS)` : rien à changer).

**Interfaces:**
- `compute_step(fields, elevation, profile, cloud_profile=None, previous=None, interval_h=None) -> dict[str, ndarray]` (`previous`: `StepFields` de l'échéance précédente ingérée) ; ajoute `CLOUD_LEVEL_LAYERS`, `CLOUD_SURFACE_LAYERS`, `cloud_top_teff_k`, `snowfall_mm`, `snow_depth_cm`, `freezing_precip_mm`, `column_condensate`, `cloud_cover_bias`.
- `registry.LEVEL_LAYERS` += `CLOUD_LEVEL_LAYERS` ; `SURFACE_LAYERS` += nuages + `cloud_cover_bias`, `cloud_top_teff_k`, `column_condensate`, `snowfall_mm`, `snow_depth_cm`, `freezing_precip_mm` ; `LayerSpec` pour chacune (unité, équation, source, statut : CONFIRMED pour `column_condensate`, `snowfall_mm`, `snow_depth_cm`, `tcc` ; HYPOTHESIS pour le reste). `registry.py` ne doit **pas** importer `clouds.py` (copie des deux tuples de noms + test d'égalité).
- Manifest : `cloud_profile`, `cloud_profile_version`, `accumulation_interval_h` (liste alignée sur `steps`, `null` si pas de précédente), `cloud_consistency` (liste `{step, bias_mean, bias_std, status}`), `cloud_status` (`ok`|`degraded`).

- [ ] **Step 1:** Choisir la boîte humide : `python tools/awci/find_wet_box.py` (script jetable du scratchpad, **non commité**) télécharge `tprate` et `mucape` de l'échéance 3 h du run 2026-09-25 00Z et imprime la boîte 2°×2° du domaine `north_africa` qui maximise `mean(tprate) × (mucape > 100)` ; reporter la boîte dans `WET_BOX` et le NOTICE.
- [ ] **Step 2:** Régénérer : `.venv/bin/python tools/awci/make_ops_fixture.py` (sec, 35–37N 2–4E, pas 0 et 3) et `… --box S N W E --out tests/data/awci_ops_wet --steps 0,3` ; vérifier 115 messages par échéance.
- [ ] **Step 3: tests (échouent)**

```python
"""SP1C pipeline integration on the real cropped IFS fixtures (dry and wet)."""

from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from acf.awci.ops.clouds import CLOUD_LEVEL_LAYERS, CLOUD_SURFACE_LAYERS
from acf.awci.ops.decode import decode_messages
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ingest import ingest_run
from acf.awci.ops.pipeline import compute_step
from acf.awci.ops.registry import LAYERS, LEVEL_LAYERS, SURFACE_LAYERS
from acf.awci.ops.source_ecmwf import parse_index
from acf.awci.ops.store import CubeStore
from acf.awci.terrain_elevation import interpolate_real_terrain_elevation
from tests.awci_ops_support import DOMAIN, FIXTURE, WET_DOMAIN, WET_FIXTURE, FixtureFetcher

PROFILE = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)


def _fields(root: Path, domain, step: int):
    stem = f"20260925000000-{step}h-oper-fc"
    data = (root / f"{stem}.grib2").read_bytes()
    msgs = [data[e.offset:e.offset + e.length] for e in parse_index((root / f"{stem}.index").read_text())]
    return decode_messages(msgs, [domain])[domain.name]


def test_registry_lists_every_cloud_layer() -> None:
    assert set(CLOUD_LEVEL_LAYERS) <= set(LEVEL_LAYERS) and set(CLOUD_SURFACE_LAYERS) <= set(SURFACE_LAYERS)
    for name in (*CLOUD_LEVEL_LAYERS, *CLOUD_SURFACE_LAYERS, "cloud_cover_bias", "cloud_top_teff_k",
                 "column_condensate", "snowfall_mm", "snow_depth_cm", "freezing_precip_mm"):
        assert name in LAYERS, name


def test_accumulations_need_the_previous_step() -> None:
    f0, f3 = _fields(FIXTURE, DOMAIN, 0), _fields(FIXTURE, DOMAIN, 3)
    elev = interpolate_real_terrain_elevation(f3.lats, f3.lons)
    alone = compute_step(f3, elev, PROFILE)
    assert np.isnan(alone["cloud_top_teff_k"]).all() and np.isnan(alone["snowfall_mm"]).all()
    chained = compute_step(f3, elev, PROFILE, previous=f0, interval_h=3.0)
    assert np.isfinite(chained["cloud_top_teff_k"]).all()
    assert (180.0 < chained["cloud_top_teff_k"]).all() and (chained["cloud_top_teff_k"] < 320.0).all()


def test_real_fields_give_consistent_cloud_diagnostics() -> None:
    for root, domain in ((FIXTURE, DOMAIN), (WET_FIXTURE, WET_DOMAIN)):
        f = _fields(root, domain, 3)
        out = compute_step(f, interpolate_real_terrain_elevation(f.lats, f.lons), PROFILE)
        tot = out["cloud_cover_total_diag"]
        assert ((0.0 <= tot) & (tot <= 1.0)).all()
        for e in ("low", "mid", "high"):
            assert (out[f"cloud_cover_{e}"] <= tot + 1e-12).all()
        np.testing.assert_allclose(out["cloud_cover_bias"], tot - f.sfc["tcc"])
        assert (out["column_condensate"] >= 0.0).all()


def test_wet_fixture_exercises_precipitating_genera() -> None:
    f = _fields(WET_FIXTURE, WET_DOMAIN, 3)
    out = compute_step(f, interpolate_real_terrain_elevation(f.lats, f.lons), PROFILE)
    assert (out["precip_rate"] > 0.1).any()
    assert (np.isin(out["genus_low"], (5, 8, 9)) | np.isin(out["genus_mid"], (5, 8, 9))).any()  # Ns, Cu or Cb


def test_manifest_records_cloud_consistency_and_intervals(tmp_path: Path) -> None:
    manifest = ingest_run(RUN, [DOMAIN], PROFILE, FixtureFetcher(), tmp_path, [0, 3])["fixture"]
    assert manifest["accumulation_interval_h"] == [None, 3]
    assert [c["step"] for c in manifest["cloud_consistency"]] == [0, 3]
    assert manifest["cloud_profile"] == "cloud-v1" and manifest["cloud_status"] in ("ok", "degraded")
    ds = CubeStore(tmp_path).dataset("fixture", "2026092500")
    assert np.isnan(ds["snowfall_mm"].isel(step=0)).all() and np.isfinite(ds["snowfall_mm"].isel(step=1)).all()


def test_failed_previous_step_nulls_next_accumulations(tmp_path: Path) -> None:
    manifest = ingest_run(RUN, [DOMAIN], PROFILE, FixtureFetcher(fail_steps=(0,)), tmp_path, [0, 3])["fixture"]
    assert manifest["accumulation_interval_h"] == [None, None]
    assert np.isnan(CubeStore(tmp_path).dataset("fixture", "2026092500")["cloud_top_teff_k"].isel(step=1)).all()
```

> Le test « genres précipitants » dépend de la boîte humide réelle : si la boîte retenue ne produit ni Ns ni Cu/Cb, en choisir une autre (Step 1) — **jamais** assouplir l'assertion.

- [ ] **Step 4:** FAIL, puis implémenter :
  - `pipeline.compute_step` : `cloud_profile = cloud_profile or _default_cloud_profile()` (fonction `lru_cache` qui charge `DEFAULT_CLOUD_PROFILE_PATH`) ; `lcl = cloud_base_lcl_m(...)` calculé une fois ; `parcel = surface_parcel(sfc["2t"], sfc["2d"], sfc["sp"] / 100, fields.levels_hpa, pl["t"], pl["q"], pl["gh"], underground)` ; `condensate = column_condensate(sfc["tcw"], sfc["tcwv"])` ; `CloudInputs(... wind10_m_s=wind_speed(sfc["10u"], sfc["10v"]), precip_rate_mm_h=rate, ...)` ; `layers.update(diagnose_clouds(...))`, `layers.update(accumulated_layers(sfc, previous.sfc if previous else None, interval_h))`, `snow_depth_cm`, `column_condensate`, `cloud_cover_bias = cloud_cover_total_diag − tcc`. Calculer `underground` **avant** et le réutiliser pour le masquage final.
  - `ingest_run` : `previous: dict[str, StepFields] = {}`, `prev_step: int | None` ; en cas d'échec d'une échéance, `previous.clear()` et `prev_step = None` ; `interval = step − prev_step` sinon `None` ; stats `bias_mean/std` sur `cloud_cover_bias` fini, `status = "degraded" if abs(mean) > cloud_profile.bias_degraded_threshold else "ok"` ; passer `extra` enrichi à `finalize`. Paramètre `cloud_profile: CloudProfile | None = None` et option CLI `--cloud-profile`.
- [ ] **Step 5:** `pytest -q tests/test_awci_ops_*.py tests/test_web_awci_api.py` → PASS (la parité SP1 et les tests existants inchangés).
- [ ] **Step 6:** commit `feat(awci-ops): ingest cloud inputs and store cloud, snow and OLR layers (real dry + wet fixtures)`.

---

### Task 8: API `/clouds`, `/volume`, `/terrain`, registre, compatibilité des anciens cubes

**Files:** Modify `src/acf/web/awci_router.py`, `src/acf/web/awci_app.py` (état `awci_cloud_profile`, en-têtes CORS exposés `X-AWCI-Levels`) ; Test `tests/test_web_awci_clouds_api.py`

**Interfaces:**
- `GET /awci/clouds?domain&run&step&lat&lon` → `{lat, lon, layers: column_layers(...), metar: "MODEL " + metar_cloud_group(...), ceiling_m, ceiling_ft, convective: {class, label, top_m, top_temp_k}, cloud_top_teff_k, column_condensate, tcc, cloud_cover_bias, cloud_covers: {low, mid, high, total_diag}, genus: {low, mid, high}, scientific_status, cloud_profile: {name, version}, provenance, source_tier}`.
- `GET /awci/volume?domain&run&step&layer&stride∈{1,2,4}` → octets `<f4` de `values` puis `gh`, en-têtes `X-AWCI-Shape: L,NY,NX`, `X-AWCI-Levels`, `X-AWCI-Lats`, `X-AWCI-Lons`, `X-AWCI-Parts: values,gh`, `X-AWCI-Unit`, `X-AWCI-Nodata: NaN`.
- `GET /awci/terrain?domain&run&stride` → `<f4` elevation, mêmes en-têtes 2D que `/field`.
- `/registry` : + `cloud_profile` (`to_dict()`), `codes` (`genus`, `clear`, `indeterminate`, `species_bits`, `convective_classes`).
- Toutes les routes lisent la **liste de couches du manifest** : couche absente du run → 404 `"layer {x!r} not in run {run} (ingested before SP1C?)"`.

- [ ] **Step 1: tests** (fixture : `ingest_run` sur la fixture sèche dans `tmp_path`, app `create_awci_app(tmp_path, domains_file)` comme `tests/test_web_awci_api.py` ; cube « ancien » simulé en retirant `cloud_fraction` des `level_layers` du manifest et la variable du NetCDF avec `netCDF4` → réécriture d'un cube sans ces variables via `xarray.Dataset.drop_vars(...).to_netcdf`)

```python
def test_clouds_point_payload(client, run_id) -> None:
    r = client.get("/api/v1/awci/clouds", params={"domain": "fixture", "run": run_id, "step": 3, "lat": 36, "lon": 3})
    assert r.status_code == 200
    body = r.json()
    assert body["metar"].startswith("MODEL ") and isinstance(body["layers"], list)
    assert set(body["cloud_covers"]) == {"low", "mid", "high", "total_diag"}
    assert body["scientific_status"]["cloud_genus"] == "HYPOTHESIS"
    assert body["provenance"]["attribution"] == "© ECMWF, CC-BY-4.0"


def test_volume_binary_layout(client, run_id) -> None:
    r = client.get("/api/v1/awci/volume", params={"domain": "fixture", "run": run_id, "step": 3,
                                                  "layer": "cloud_fraction", "stride": 2})
    assert r.status_code == 200
    nl, ny, nx = (int(x) for x in r.headers["X-AWCI-Shape"].split(","))
    assert (nl, ny, nx) == (12, 5, 5) and r.headers["X-AWCI-Parts"] == "values,gh"
    data = np.frombuffer(r.content, dtype="<f4")
    assert data.size == 2 * nl * ny * nx
    gh = data[nl * ny * nx:].reshape(nl, ny, nx)
    assert np.all(np.diff(gh, axis=0)[np.isfinite(np.diff(gh, axis=0))] > 0)


def test_volume_rejects_surface_layer_and_bad_stride(client, run_id) -> None:
    base = {"domain": "fixture", "run": run_id, "step": 3}
    assert client.get("/api/v1/awci/volume", params=base | {"layer": "tcc"}).status_code == 400
    assert client.get("/api/v1/awci/volume", params=base | {"layer": "cloud_fraction", "stride": 3}).status_code == 422


def test_terrain_f32(client, run_id) -> None:
    r = client.get("/api/v1/awci/terrain", params={"domain": "fixture", "run": run_id})
    assert r.status_code == 200 and len(r.content) == 9 * 9 * 4


def test_pre_sp1c_cube_still_served_and_clouds_404(old_client, run_id) -> None:
    ok = old_client.get("/api/v1/awci/point", params={"domain": "fixture", "run": run_id, "step": 3, "level": 850,
                                                      "lat": 36, "lon": 3})
    assert ok.status_code == 200 and "cloud_fraction" not in ok.json()["level_layers"]
    assert old_client.get("/api/v1/awci/clouds", params={"domain": "fixture", "run": run_id, "step": 3,
                                                         "lat": 36, "lon": 3}).status_code == 404
    assert old_client.get("/api/v1/awci/field", params={"domain": "fixture", "run": run_id, "step": 3,
                                                        "layer": "ceiling_m"}).status_code == 404


def test_registry_exposes_codes_and_cloud_profile(client) -> None:
    body = client.get("/api/v1/awci/registry").json()
    assert body["codes"]["genus"]["Cb"] == 9 and body["codes"]["clear"] == -1
    assert body["cloud_profile"]["name"] == "cloud-v1"
```

- [ ] **Step 2:** FAIL.
- [ ] **Step 3:** Implémenter :
  - `_available(m) = set(m["level_layers"]) | set(m["surface_layers"])` ; `_require_layer(m, name)` → 404 ; `_column(ds, si, i, j, names)` avec `names = [n for n in LEVEL_LAYERS if n in m["level_layers"]]` ; `/point` itère sur `m["surface_layers"]` ; `/field` appelle `_require_layer`.
  - `/clouds` : `_require_layer(m, "cloud_fraction")` ; lit la colonne `cloud_fraction`, `cloud_genus`, `gh` et les scalaires surface ; appelle `column_layers(..., sp_hpa=sfc["sp_hpa"], ...)` avec le profil `request.app.state.awci_cloud_profile` ; `ceiling_ft = int(ceiling_m / 0.3048)` ou `None`.
  - `/volume` : `stride: Literal[1, 2, 4] = 1` ; couche hors `LEVEL_LAYERS` → 400 ; `values = ds[layer].isel(step=si).values[:, ::stride, ::stride]`.
  - `/terrain` : `ds["elevation"].values[::stride, ::stride]`.
- [ ] **Step 4:** PASS + suite complète. **Step 5:** commit `feat(awci-web): /clouds, /volume, /terrain; manifest-aware layer guards for pre-SP1C cubes`.

---

### Task 9: Calibration reproductible de RHc

**Files:** Create `tools/awci/calibrate_cloud_rhc.py`, `src/acf/awci/ops/calibration.py` ; Test `tests/test_awci_ops_calibration.py`

**Interfaces:** `calibrate_rhc(r_pct, sp_hpa, levels_hpa, tcc, profile, grid=np.arange(0.50, 0.951, 0.025), passes=3) -> dict` (`rh_critical`, `rmse_before`, `rmse_after`, `bias_after`, `n_cells`) par descente coordonnée étage par étage (bas → moyen → haut, `passes` fois) sur l'erreur quadratique `max_random_cover(fraction) − tcc` des cellules finies. Le script lit un ou plusieurs cubes (`--domain --runs --steps`), imprime le JSON et, avec `--write`, met à jour `rh_critical`, incrémente la version mineure et remplit `calibration` (`runs`, `steps`, `n_cells`, `rmse_before`, `rmse_after`, `bias_after`, `date`, `acf_git_sha`).

- [ ] **Step 1: test** — champ synthétique généré avec RHc connus (0,78 / 0,66 / 0,72) et `tcc` = couverture exacte : la calibration retrouve chaque RHc à ±0,025 près et `rmse_after < rmse_before`.
- [ ] **Step 2:** FAIL. **Step 3:** implémenter (réutilise `etage_codes`, `level_cloud_fraction` avec un `CloudProfile` dérivé via `dataclasses.replace`). **Step 4:** PASS. **Step 5:** commit `feat(awci-ops): reproducible RHc calibration against IFS tcc`.

---

### Task 10: Run réel, calibration, mesures, documentation

- [ ] **Step 1:** Ingestion réelle `acf-awci-ingest --run latest --domain north_africa` (données dans le scratchpad) : noter durée, taille, `cloud_consistency` ; budget : durée ≤ 8,1 + 2 min, sinon profiler (`python -m cProfile`) avant toute optimisation.
- [ ] **Step 2:** `tools/awci/calibrate_cloud_rhc.py --domain north_africa --runs <run> --steps 0-72/6 --write` ; ré-ingérer ; noter RMSE avant/après et biais par échéance.
- [ ] **Step 3:** Contrôles de vraisemblance sur le cube réel, consignés dans le guide : répartition des genres par étage, part de Cb, plafond < 1000 ft, comparaison qualitative T_e / MTG IR 10,5 µm à la même heure (capture EUMETView).
- [ ] **Step 4:** Latences `/clouds` et `/volume` (TestClient, 50 requêtes, p95) ; critère < 300 ms (`/volume` stride 1 < 500 ms).
- [ ] **Step 5:** Docs : `docs/awci/AWCI_WEB_SP1.md` (section SP1C : couches, routes, mesures, statuts, limites), spec SP1C (écarts de mise en œuvre : `tp` au lieu de `skt`, bissection au lieu de Newton, `cloud_genus` au lieu de `cloud_layer_genus`, précip. continue = choix ACF), `CHANGELOG.md`.
- [ ] **Step 6:** Suite complète + `ruff` + `mypy` ; commit `docs(awci): SP1C operator guide, measured figures, calibration record` ; push.
