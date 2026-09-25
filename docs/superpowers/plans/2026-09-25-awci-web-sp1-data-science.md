# AWCI Web SP1 — Data & Science Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ingest real ECMWF IFS 0.25° Open Data per run and per configured domain, compute vectorized aviation hazard diagnostics and an honest AWCI composite, store them as reproducible NetCDF cubes, and serve them through a typed read-only FastAPI API.

**Architecture:** A Qt-free sub-package `acf.awci.ops` holds pure NumPy diagnostics (`isa`, `thermo`, `kinematics`, `hazards`), the vectorized engine (`engine`), the ECMWF source (`source_ecmwf`), GRIB decoding (`decode`), per-step computation (`pipeline`), storage (`store`) and the ingestion CLI (`ingest`). A new router `acf.web.routers.awci_router` reads the cubes only; a light app factory `acf.web.awci_app` serves it without HPC/torch imports.

**Tech Stack:** Python 3.12, NumPy, eccodes (GRIB decoding), netCDF4 + xarray (storage/reading), FastAPI + Pydantic, loguru, pytest.

**Spec:** `docs/superpowers/specs/2026-09-25-awci-web-sp1-data-science-design.md`

## Global Constraints

- Python ≥ 3.12; line length 120 (ruff); type hints on every public function.
- No new third-party dependency (network via `urllib`; decoding via `eccodes`, already in extra `formats`).
- Never modify `AWCICalculator`, `Normalizer`, `WeightsManager`, the desktop GUI, or existing `/api/v1/*` routes.
- A missing value is `NaN` in arrays and `null` in JSON — never `0`.
- Every API response carries `provenance` (model `"ECMWF IFS 0.25° Open Data"`, run, step, valid_time, domain, profile, profile_version, license `"CC-BY-4.0"`, attribution `"© ECMWF, CC-BY-4.0"`) and `source_tier: "nwp_forecast"`.
- Pressure levels ingested: `1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100` hPa. Steps: `0..72` every 3 h.
- Pressure-level params: `t, q, r, u, v, w, gh, d`. Surface params: `2t, 2d, 10u, 10v, 10fg, sp, msl, mucape, tprate, ptype, tcc, lsm`.
- Storage root: env `ACF_AWCI_DATA_DIR`, default `<repo>/data/awci/` (already git-ignored via `/data/`).
- Operational composite: `awci = null` when the summed weight of present modules < 0.5.
- Run the tests with: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q <files>`.

## Review Focus

1. A point request outside the domain bbox must return HTTP 400, never the nearest-edge value → test in Task 10.
2. A step absent from a `partial` run must return HTTP 404 naming the missing step → test in Task 10.
3. A cell with zero humidity (q = 0) must give `theta_e = NaN`, a `null` thermodynamic module and a renormalized AWCI, never 0 → test in Task 5.
4. When the newest run's last requested step is not yet published, `latest` must fall back to the previous run → test in Task 9.
5. A domain config with `west >= east` (antimeridian crossing) or `south >= north` must be rejected at load time → test in Task 6.

---

## File Structure

| File | Responsibility |
|---|---|
| `src/acf/awci/ops/__init__.py` | package docstring only |
| `src/acf/awci/ops/isa.py` | ICAO standard atmosphere (Doc 7488) pressure ↔ altitude, flight level labels |
| `src/acf/awci/ops/thermo.py` | vectorized vapour pressure, dewpoint, RH, θe (Bolton 1980), LCL cloud base |
| `src/acf/awci/ops/kinematics.py` | wind speed, layer/vertical shear on real Δgh, horizontal gradients, Ellrod TI2 |
| `src/acf/awci/ops/hazards.py` | icing potential, precip rate/class, ptype severity, 2 m RH, dust proxy |
| `src/acf/awci/ops/registry.py` | metadata of every served layer (unit, equation, source, status) |
| `src/acf/awci/ops/engine.py` | profiles (legacy/operational), vectorized module scores, composite with missing-module rule |
| `src/acf/awci/ops/domains.py` | domain config loading/validation, cropping indices |
| `src/acf/awci/ops/source_ecmwf.py` | URLs, index parsing, fetcher (urllib, retries), message selection, latest run |
| `src/acf/awci/ops/decode.py` | GRIB message bytes → cropped arrays per domain (`StepFields`) |
| `src/acf/awci/ops/pipeline.py` | `StepFields` → all layers + AWCI arrays for one step |
| `src/acf/awci/ops/store.py` | NetCDF cube writer (atomic), manifest, retention, reader `CubeStore` |
| `src/acf/awci/ops/ingest.py` | `ingest_run()` orchestration + CLI `acf-awci-ingest` |
| `src/acf/web/routers/awci_router.py` | `/api/v1/awci/*` read-only endpoints + Pydantic models |
| `src/acf/web/awci_app.py` | light FastAPI factory + `acf-awci-web` entry point |
| `config/awci/domains.json` | domain definitions |
| `config/awci/profiles/operational-v1.json` | operational profile |
| `tools/awci/make_ops_fixture.py` | one-off generator of the real cropped GRIB fixture |
| `tests/data/awci_ops/` | cropped real GRIB2 + index for 2 steps, `NOTICE.md` |
| `docs/awci/AWCI_WEB_SP1.md` | operator documentation (install, schedule, API) |

---

### Task 1: ICAO standard atmosphere (`isa.py`)

**Files:**
- Create: `src/acf/awci/ops/__init__.py`, `src/acf/awci/ops/isa.py`
- Test: `tests/test_awci_ops_isa.py`

**Interfaces:**
- Produces: `pressure_altitude_m(pressure_hpa: float | np.ndarray) -> float | np.ndarray`, `flight_level(pressure_hpa: float) -> int`, constants `ISA_P0_HPA=1013.25`, `ISA_P11_HPA`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_awci_ops_isa.py
import numpy as np
import pytest

from acf.awci.ops.isa import ISA_P11_HPA, flight_level, pressure_altitude_m

# ICAO Doc 7488 tabulated pressure altitudes (m)
@pytest.mark.parametrize(
    ("p_hpa", "h_m"),
    [(1013.25, 0.0), (850.0, 1457.3), (500.0, 5574.4), (300.0, 9164.0), (200.0, 11784.0), (100.0, 16179.7)],
)
def test_pressure_altitude_matches_doc7488(p_hpa: float, h_m: float) -> None:
    assert pressure_altitude_m(p_hpa) == pytest.approx(h_m, abs=1.0)


def test_tropopause_pressure_is_22632_pa() -> None:
    assert ISA_P11_HPA == pytest.approx(226.32, abs=0.01)


def test_vectorized_and_continuous_at_tropopause() -> None:
    p = np.array([ISA_P11_HPA + 1e-9, ISA_P11_HPA - 1e-9])
    h = pressure_altitude_m(p)
    assert h[0] == pytest.approx(11000.0, abs=0.01)
    assert h[1] == pytest.approx(11000.0, abs=0.01)


@pytest.mark.parametrize(("p_hpa", "fl"), [(300.0, 301), (250.0, 340), (200.0, 387), (100.0, 531)])
def test_flight_level_labels(p_hpa: float, fl: int) -> None:
    assert flight_level(p_hpa) == fl


def test_rejects_pressure_above_20km() -> None:
    with pytest.raises(ValueError):
        pressure_altitude_m(40.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_isa.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'acf.awci.ops'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/acf/awci/ops/__init__.py
"""
AWCI operational pipeline (AWCI Web, SP1).

Qt-free: ingestion of ECMWF IFS Open Data, vectorized hazard
diagnostics, AWCI composite, NetCDF cube storage. See
docs/superpowers/specs/2026-09-25-awci-web-sp1-data-science-design.md.
"""
```

```python
# src/acf/awci/ops/isa.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_isa.py`
Expected: PASS (13 tests)

- [ ] **Step 5: Commit**

```bash
git add src/acf/awci/ops/__init__.py src/acf/awci/ops/isa.py tests/test_awci_ops_isa.py
git commit -m "feat(awci-ops): ICAO Doc 7488 standard atmosphere incl. stratosphere"
```

---

### Task 2: Vectorized thermodynamics (`thermo.py`)

**Files:**
- Create: `src/acf/awci/ops/thermo.py`
- Test: `tests/test_awci_ops_thermo.py`

**Interfaces:**
- Produces: `vapor_pressure_hpa(q, p_hpa)`, `saturation_vapor_pressure_hpa(t_k)`, `dewpoint_k_from_vapor_pressure(e_hpa)`, `relative_humidity_pct(t_k, q, p_hpa)`, `theta_e_bolton_k(t_k, q, p_hpa)`, `cloud_base_lcl_m(t2m_k, d2m_k)` — all take/return `np.ndarray`, NaN for undefined.

Scientific note: dewpoint is obtained by exactly inverting the Bolton (1980) saturation vapour pressure formula that `acf.science.SaturationVaporPressure` uses, so `es(Td) == e` holds exactly. (The scalar chain `compute_real_theta_e_at_point` mixes Bolton `es` with Magnus–Tetens dewpoint coefficients; the vectorized path deliberately does not.)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_awci_ops_thermo.py
import numpy as np
import pytest

from acf.awci.ops.thermo import (
    cloud_base_lcl_m,
    dewpoint_k_from_vapor_pressure,
    relative_humidity_pct,
    saturation_vapor_pressure_hpa,
    theta_e_bolton_k,
    vapor_pressure_hpa,
)
from acf.science.equivalent_potential_temperature import EquivalentPotentialTemperature
from acf.science.saturation_vapor_pressure import SaturationVaporPressure
from acf.science.vapor_pressure import VaporPressure

RNG = np.random.default_rng(42)
T = RNG.uniform(210.0, 310.0, 500)
P = RNG.uniform(100.0, 1030.0, 500)
RH = RNG.uniform(0.05, 1.0, 500)
Q = np.array([0.622 * r * SaturationVaporPressure.calculate(t) / p for t, p, r in zip(T, P, RH)])


def test_vapor_pressure_matches_scalar() -> None:
    expected = np.array([VaporPressure.calculate(q, p) for q, p in zip(Q, P)])
    np.testing.assert_allclose(vapor_pressure_hpa(Q, P), expected, rtol=1e-12)


def test_saturation_vapor_pressure_matches_scalar() -> None:
    expected = np.array([SaturationVaporPressure.calculate(t) for t in T])
    np.testing.assert_allclose(saturation_vapor_pressure_hpa(T), expected, rtol=1e-12)


def test_dewpoint_inverts_bolton_es_exactly() -> None:
    e = vapor_pressure_hpa(Q, P)
    np.testing.assert_allclose(saturation_vapor_pressure_hpa(dewpoint_k_from_vapor_pressure(e)), e, rtol=1e-10)


def test_theta_e_matches_scalar_bolton_given_same_dewpoint() -> None:
    td = np.minimum(dewpoint_k_from_vapor_pressure(vapor_pressure_hpa(Q, P)), T)
    expected = np.array([EquivalentPotentialTemperature.calculate_bolton_1980(t, d, p) for t, d, p in zip(T, td, P)])
    np.testing.assert_allclose(theta_e_bolton_k(T, Q, P), expected, rtol=1e-10)


def test_zero_humidity_gives_nan_theta_e() -> None:
    out = theta_e_bolton_k(np.array([290.0]), np.array([0.0]), np.array([1000.0]))
    assert np.isnan(out[0])


def test_relative_humidity_capped_at_100() -> None:
    q_super = 1.2 * 0.622 * SaturationVaporPressure.calculate(280.0) / 900.0
    assert relative_humidity_pct(np.array([280.0]), np.array([q_super]), np.array([900.0]))[0] == 100.0


def test_cloud_base_lcl_espy_125m_per_kelvin() -> None:
    out = cloud_base_lcl_m(np.array([300.0, 290.0, 285.0]), np.array([290.0, 290.0, 286.0]))
    np.testing.assert_allclose(out, [1250.0, 0.0, 0.0])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_thermo.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'acf.awci.ops.thermo'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/acf/awci/ops/thermo.py
"""
Vectorized moist thermodynamics (NumPy), consistent with acf.science.

- e  = q p / (eps + q (1 - eps)),  eps = 0.622          (VaporPressure)
- es = 6.112 exp(17.67 Tc / (Tc + 243.5))  [hPa]       (Bolton 1980, SaturationVaporPressure)
- Td = exact inverse of es: Tc = 243.5 ln(e/6.112) / (17.67 - ln(e/6.112))
- theta_e: Bolton (1980) eq. 43 as in EquivalentPotentialTemperature.calculate_bolton_1980
- LCL height (Espy): 125 m per K of dewpoint depression.
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_thermo.py`
Expected: PASS (7 tests)

- [ ] **Step 5: Commit**

```bash
git add src/acf/awci/ops/thermo.py tests/test_awci_ops_thermo.py
git commit -m "feat(awci-ops): vectorized thermodynamics (Bolton theta-e, dewpoint, LCL)"
```

---

### Task 3: Kinematics and Ellrod TI2 (`kinematics.py`)

**Files:**
- Create: `src/acf/awci/ops/kinematics.py`
- Test: `tests/test_awci_ops_kinematics.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `wind_speed(u, v) -> ndarray`
  - `layer_shear(u, v, gh) -> tuple[ndarray, ndarray]` — inputs `(level, lat, lon)` with levels ordered by **decreasing pressure** (1000→100); returns `(layer_shear_ms, vertical_shear_s1)` same shape.
  - `grid_spacing_m(lats, lons) -> tuple[float, ndarray]` — `dy`, `dx_per_row` (lats ascending).
  - `horizontal_gradients(f, lats, lons) -> tuple[ndarray, ndarray]` — `(df_dx, df_dy)` on the last two axes.
  - `ellrod_ti2(u, v, gh, divergence, lats, lons) -> ndarray` (s⁻²).
  - `cat_category_codes(ti2) -> ndarray[int8]` — 0 Smooth-Light, 1 Light-Moderate, 2 Moderate, 3 Moderate-Severe, −1 undefined.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_awci_ops_kinematics.py
import numpy as np
import pytest

from acf.awci.ops.kinematics import (
    cat_category_codes,
    ellrod_ti2,
    grid_spacing_m,
    horizontal_gradients,
    layer_shear,
    wind_speed,
)
from acf.science.wind_turbulence import CATIndex

LATS = np.linspace(30.0, 32.0, 9)
LONS = np.linspace(0.0, 2.0, 9)


def test_wind_speed() -> None:
    np.testing.assert_allclose(wind_speed(np.array([3.0]), np.array([4.0])), [5.0])


def test_layer_shear_uses_real_gh_and_upper_neighbour() -> None:
    u = np.stack([np.full((2, 2), 10.0), np.full((2, 2), 20.0), np.full((2, 2), 20.0)])
    v = np.zeros_like(u)
    gh = np.stack([np.full((2, 2), 100.0), np.full((2, 2), 1100.0), np.full((2, 2), 3100.0)])
    shear, vws = layer_shear(u, v, gh)
    assert shear[0, 0, 0] == pytest.approx(10.0)
    assert vws[0, 0, 0] == pytest.approx(10.0 / 1000.0)
    # top level uses the lower neighbour: |20-20| / 2000
    assert vws[2, 0, 0] == pytest.approx(0.0)
    assert shear[1, 0, 0] == pytest.approx(0.0)


def test_layer_shear_degenerate_dz_is_nan() -> None:
    u = np.stack([np.ones((1, 1)), 2 * np.ones((1, 1))])
    gh = np.stack([np.full((1, 1), 500.0), np.full((1, 1), 500.2)])
    _, vws = layer_shear(u, np.zeros_like(u), gh)
    assert np.isnan(vws[0, 0, 0])


def test_horizontal_gradient_of_linear_field() -> None:
    dy, dx = grid_spacing_m(LATS, LONS)
    lat_m = (LATS - LATS[0])[:, None] * (dy / (LATS[1] - LATS[0])) * np.ones((1, LONS.size))
    df_dx, df_dy = horizontal_gradients(2.0e-5 * lat_m, LATS, LONS)
    np.testing.assert_allclose(df_dy, 2.0e-5, rtol=1e-9)
    np.testing.assert_allclose(df_dx, 0.0, atol=1e-15)


def test_ti2_matches_scalar_cat_index() -> None:
    rng = np.random.default_rng(1)
    u = rng.normal(20.0, 8.0, (3, 9, 9))
    v = rng.normal(0.0, 8.0, (3, 9, 9))
    gh = np.stack([np.full((9, 9), h) for h in (1500.0, 3000.0, 5600.0)])
    div = rng.normal(0.0, 1e-5, (3, 9, 9))
    ti2 = ellrod_ti2(u, v, gh, div, LATS, LONS)
    du_dx, du_dy = horizontal_gradients(u, LATS, LONS)
    dv_dx, dv_dy = horizontal_gradients(v, LATS, LONS)
    _, vws = layer_shear(u, v, gh)
    k, i, j = 1, 4, 4
    expected = CATIndex.ti2(
        vws[k, i, j],
        CATIndex.deformation(du_dx[k, i, j], dv_dy[k, i, j], dv_dx[k, i, j], du_dy[k, i, j]),
        -div[k, i, j],
    )
    assert ti2[k, i, j] == pytest.approx(expected, rel=1e-12)


def test_cat_categories_match_scalar_thresholds() -> None:
    values = np.array([1e-7, 5e-7, 9e-7, 13e-7, np.nan])
    np.testing.assert_array_equal(cat_category_codes(values), [0, 1, 2, 3, -1])
    names = ["Smooth to Light", "Light-Moderate", "Moderate", "Moderate-Severe"]
    for code, value in zip(cat_category_codes(values[:4]), values[:4]):
        assert names[code] == CATIndex.category(float(value))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_kinematics.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'acf.awci.ops.kinematics'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/acf/awci/ops/kinematics.py
"""
Vectorized kinematics and Ellrod-Knapp (1992) TI2.

VWS = |dV|/dz (dz from real geopotential height gh), DEF = sqrt(DST^2 + DSH^2),
DST = du/dx - dv/dy, DSH = dv/dx + du/dy, CVG = -divergence (IFS field d),
TI2 = VWS * (DEF + CVG)  [s^-2]; categories use CATIndex's x1e7 thresholds 4/8/12.
Horizontal derivatives: centred differences on a regular lat/lon grid with real
metric spacing (spherical Earth, R = 6371 km).
"""

from __future__ import annotations

import numpy as np

EARTH_RADIUS_M = 6371000.0
MIN_DZ_M = 1.0
_CAT_BOUNDS_S2 = (4e-7, 8e-7, 12e-7)


def wind_speed(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    return np.hypot(np.asarray(u, dtype=float), np.asarray(v, dtype=float))


def layer_shear(u: np.ndarray, v: np.ndarray, gh: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """|dV| (m/s) and |dV|/dz (1/s) between each level and its upper neighbour (lower one for the top level)."""
    u, v, gh = (np.asarray(a, dtype=float) for a in (u, v, gh))
    n = u.shape[0]
    upper = np.r_[np.arange(1, n), n - 1]
    lower = np.r_[np.arange(0, n - 1), n - 2]
    dv = np.hypot(u[upper] - u[lower], v[upper] - v[lower])
    dz = np.abs(gh[upper] - gh[lower])
    with np.errstate(divide="ignore", invalid="ignore"):
        vws = np.where(dz >= MIN_DZ_M, dv / dz, np.nan)
    return dv, vws


def grid_spacing_m(lats: np.ndarray, lons: np.ndarray) -> tuple[float, np.ndarray]:
    lats = np.asarray(lats, dtype=float)
    dlat = np.radians(float(np.mean(np.diff(lats))))
    dlon = np.radians(float(np.mean(np.diff(np.asarray(lons, dtype=float)))))
    return float(EARTH_RADIUS_M * dlat), EARTH_RADIUS_M * np.cos(np.radians(lats)) * dlon


def horizontal_gradients(f: np.ndarray, lats: np.ndarray, lons: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    dy, dx_row = grid_spacing_m(lats, lons)
    f = np.asarray(f, dtype=float)
    df_dy = np.gradient(f, axis=-2) / dy
    df_dx = np.gradient(f, axis=-1) / dx_row[:, None]
    return df_dx, df_dy


def ellrod_ti2(
    u: np.ndarray, v: np.ndarray, gh: np.ndarray, divergence: np.ndarray, lats: np.ndarray, lons: np.ndarray
) -> np.ndarray:
    _, vws = layer_shear(u, v, gh)
    du_dx, du_dy = horizontal_gradients(u, lats, lons)
    dv_dx, dv_dy = horizontal_gradients(v, lats, lons)
    deformation = np.hypot(dv_dx + du_dy, du_dx - dv_dy)
    return vws * (deformation - np.asarray(divergence, dtype=float))


def cat_category_codes(ti2: np.ndarray) -> np.ndarray:
    ti2 = np.asarray(ti2, dtype=float)
    codes = np.searchsorted(np.asarray(_CAT_BOUNDS_S2), np.nan_to_num(ti2, nan=0.0), side="right").astype(np.int8)
    return np.where(np.isfinite(ti2), codes, np.int8(-1)).astype(np.int8)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_kinematics.py`
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add src/acf/awci/ops/kinematics.py tests/test_awci_ops_kinematics.py
git commit -m "feat(awci-ops): vectorized shear and Ellrod-Knapp TI2 on real gh/divergence"
```

---

### Task 4: Hazard diagnostics and layer registry (`hazards.py`, `registry.py`)

**Files:**
- Create: `src/acf/awci/ops/hazards.py`, `src/acf/awci/ops/registry.py`
- Test: `tests/test_awci_ops_hazards.py`

**Interfaces:**
- Consumes: `thermo.saturation_vapor_pressure_hpa`.
- Produces:
  - `icing_potential(t_k, r_pct) -> ndarray` (1.0/0.0, NaN if input NaN); constants `ICING_T_MIN_C=-20.0`, `ICING_T_MAX_C=0.0`, `ICING_RH_MIN_PCT=70.0`.
  - `precip_rate_mm_h(tprate) -> ndarray`; `precip_class_codes(rate_mm_h) -> ndarray[int8]` (0 none, 1 light <2.5, 2 moderate <10, 3 heavy <50, 4 violent, −1 NaN).
  - `ECMWF_PTYPE_SEVERITY: dict[int, float]`; `ptype_severity(ptype) -> ndarray` (NaN for unknown code).
  - `relative_humidity_2m_pct(t2m_k, d2m_k) -> ndarray`.
  - `dust_proxy(gust_ms, rh2m_pct) -> ndarray`.
  - `registry.LAYERS: dict[str, LayerSpec]`; `LayerSpec(name, label, unit, per_level, equation, source, status)`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_awci_ops_hazards.py
import numpy as np

from acf.awci.hydrometeor_phase import PHASE_SEVERITY
from acf.awci.ops.hazards import (
    ECMWF_PTYPE_SEVERITY,
    dust_proxy,
    icing_potential,
    precip_class_codes,
    precip_rate_mm_h,
    ptype_severity,
    relative_humidity_2m_pct,
)
from acf.awci.ops.registry import LAYERS


def test_icing_potential_temperature_and_humidity_window() -> None:
    t = np.array([273.15, 263.15, 253.15, 252.0, 274.0, 263.15, np.nan])
    r = np.array([80.0, 70.0, 90.0, 90.0, 90.0, 69.9, 80.0])
    out = icing_potential(t, r)
    np.testing.assert_array_equal(out[:6], [1.0, 1.0, 1.0, 0.0, 0.0, 0.0])
    assert np.isnan(out[6])


def test_precip_rate_and_wmo_classes() -> None:
    rate = precip_rate_mm_h(np.array([0.0, 1e-4, 2e-3, 5e-3, 2e-2, np.nan]))
    np.testing.assert_allclose(rate[:5], [0.0, 0.36, 7.2, 18.0, 72.0])
    np.testing.assert_array_equal(precip_class_codes(rate), [0, 1, 2, 3, 4, -1])


def test_ptype_severity_reuses_phase_severity_and_rejects_unknown() -> None:
    assert ECMWF_PTYPE_SEVERITY[1] == PHASE_SEVERITY["Rain"]
    assert ECMWF_PTYPE_SEVERITY[5] == PHASE_SEVERITY["Snow"]
    assert ECMWF_PTYPE_SEVERITY[3] == PHASE_SEVERITY["Freezing Rain / Ice Pellets"]
    out = ptype_severity(np.array([0.0, 1.0, 12.0, 42.0, np.nan]))
    np.testing.assert_allclose(out[:3], [0.0, 0.2, 1.0])
    assert np.isnan(out[3]) and np.isnan(out[4])


def test_rh2m_and_dust_proxy() -> None:
    rh = relative_humidity_2m_pct(np.array([300.0, 300.0]), np.array([300.0, 280.0]))
    assert rh[0] == 100.0 and 25.0 < rh[1] < 35.0
    out = dust_proxy(np.array([8.0, 18.0, 18.0, 13.0]), np.array([10.0, 10.0, 80.0, 45.0]))
    np.testing.assert_allclose(out, [0.0, 1.0, 0.0, 0.25])


def test_registry_declares_every_layer_with_status() -> None:
    for name in ("wind_speed", "layer_shear", "vertical_shear", "cat_ti2", "cat_category", "icing_potential",
                 "theta_e", "mucape", "cloud_base_lcl", "precip_rate", "precip_class", "precip_type",
                 "gust_10m", "dust_proxy", "awci"):
        spec = LAYERS[name]
        assert spec.unit and spec.equation and spec.source and spec.status
```

- [ ] **Step 2: Run test to verify it fails**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_hazards.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'acf.awci.ops.hazards'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/acf/awci/ops/hazards.py
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
```

```python
# src/acf/awci/ops/registry.py
"""Single source of truth for every layer served by /api/v1/awci (unit, equation, source, status)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class LayerSpec:
    name: str
    label: str
    unit: str
    per_level: bool
    equation: str
    source: str
    status: str  # ScientificStatus value from acf.awci.scientific_status

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_SPECS = (
    LayerSpec("wind_speed", "Wind speed", "m/s", True, "sqrt(u^2 + v^2)", "IFS u, v", "CONFIRMED"),
    LayerSpec("layer_shear", "Layer wind shear", "m/s", True, "|V(k+1) - V(k)|", "IFS u, v", "CONFIRMED"),
    LayerSpec("vertical_shear", "Vertical wind shear", "1/s", True, "|dV| / dgh", "IFS u, v, gh", "CONFIRMED"),
    LayerSpec("cat_ti2", "Clear-air turbulence (Ellrod TI2)", "1/s^2", True, "VWS * (DEF - div)",
              "Ellrod & Knapp (1992), Wea. Forecasting 7, 150-165", "HYPOTHESIS"),
    LayerSpec("cat_category", "CAT category", "code 0-3", True, "TI2 x1e7 thresholds 4/8/12",
              "Ellrod & Knapp (1992)", "HYPOTHESIS"),
    LayerSpec("icing_potential", "Icing potential", "0/1", True, "-20 <= T <= 0 degC and RH >= 70 %",
              "T+RH approach of Schultz & Politovich (1992); thresholds ACF choice", "HYPOTHESIS"),
    LayerSpec("theta_e", "Equivalent potential temperature", "K", True, "Bolton (1980) eq. 43",
              "Bolton (1980), Mon. Wea. Rev. 108, 1046-1053", "CONFIRMED"),
    LayerSpec("mucape", "Most-unstable CAPE", "J/kg", False, "IFS field", "ECMWF IFS", "CONFIRMED"),
    LayerSpec("cloud_base_lcl", "Estimated cloud base (LCL) - not a ceiling", "m AGL", False,
              "125 m x (T2m - Td2m)", "Espy approximation", "HYPOTHESIS"),
    LayerSpec("precip_rate", "Precipitation rate", "mm/h", False, "tprate x 3600", "ECMWF IFS", "CONFIRMED"),
    LayerSpec("precip_class", "Precipitation intensity", "code 0-4", False, "WMO bounds 2.5/10/50 mm/h",
              "WMO-No. 8", "CONFIRMED"),
    LayerSpec("precip_type", "Precipitation type", "ECMWF code", False, "IFS ptype", "ECMWF IFS", "CONFIRMED"),
    LayerSpec("gust_10m", "10 m wind gust", "m/s", False, "IFS 10fg", "ECMWF IFS", "CONFIRMED"),
    LayerSpec("dust_proxy", "Dust-raising proxy (not a concentration)", "0-1", False,
              "ramp(gust, 8, 18) x (1 - ramp(RH2m, 20, 70))", "ACF proxy", "HYPOTHESIS"),
    LayerSpec("awci", "AWCI (operational-v1)", "0-100", True, "weighted modules, missing ones renormalized",
              "ACF composite index", "HYPOTHESIS"),
)

LAYERS: dict[str, LayerSpec] = {spec.name: spec for spec in _SPECS}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_hazards.py`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add src/acf/awci/ops/hazards.py src/acf/awci/ops/registry.py tests/test_awci_ops_hazards.py
git commit -m "feat(awci-ops): icing, WMO precipitation, ptype, dust diagnostics + layer registry"
```

---

### Task 5: Vectorized AWCI engine and profiles (`engine.py`)

**Files:**
- Create: `src/acf/awci/ops/engine.py`, `config/awci/profiles/operational-v1.json`
- Test: `tests/test_awci_ops_engine.py`

**Interfaces:**
- Consumes: `AWCICalculator`, `WeightsManager`, `Normalizer` constants (read, never modified).
- Produces:
  - `@dataclass(frozen=True) Profile(name, version, weights, interaction_terms, interaction_weights, level_thresholds, min_present_weight)`
  - `legacy_profile() -> Profile`; `load_profile(path) -> Profile`; `DEFAULT_OPERATIONAL_PROFILE_PATH`
  - `legacy_module_scores(inputs: dict[str, np.ndarray]) -> dict[str, np.ndarray]` (all 14 modules, [0,1])
  - `operational_module_scores(*, wind_speed, layer_shear, theta_e, mucape, precip_rate, ptype_severity, elevation) -> dict[str, np.ndarray | None]`
  - `@dataclass CompositeResult(awci, decomposition, present_weight)`; `combine(module_scores, profile) -> CompositeResult`
  - `level_codes(awci, profile) -> ndarray[int8]` (index into `profile.level_thresholds`, −1 NaN)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_awci_ops_engine.py
import numpy as np
import pytest

from acf.awci.calculator import AWCICalculator
from acf.awci.ops.engine import (
    DEFAULT_OPERATIONAL_PROFILE_PATH,
    combine,
    legacy_module_scores,
    legacy_profile,
    level_codes,
    load_profile,
    operational_module_scores,
)

RNG = np.random.default_rng(7)
N = 10_000
INPUTS = {
    "temperature": RNG.uniform(220.0, 320.0, N),
    "specific_humidity": RNG.uniform(0.0, 0.03, N),
    "wind_speed": RNG.uniform(0.0, 70.0, N),
    "cape": RNG.uniform(0.0, 6000.0, N),
    "cin": RNG.uniform(-600.0, 0.0, N),
    "precipitation": RNG.uniform(0.0, 60.0, N),
    "pressure": RNG.uniform(100.0, 1030.0, N),
    "altitude": RNG.uniform(-100.0, 4000.0, N),
    "confidence": RNG.uniform(0.0, 100.0, N),
    "temporal_change": RNG.uniform(0.0, 25.0, N),
}


def test_legacy_module_scores_match_calculator() -> None:
    calc = AWCICalculator()
    scores = legacy_module_scores(INPUTS)
    for idx in range(0, N, 97):
        point = {key: float(values[idx]) for key, values in INPUTS.items()}
        expected = calc.calculate_module_scores(point)
        for module, value in expected.items():
            assert scores[module][idx] == pytest.approx(value, abs=1e-12)


def test_legacy_composite_matches_calculator_after_its_rounding() -> None:
    calc = AWCICalculator()
    result = combine(legacy_module_scores(INPUTS), legacy_profile())
    for idx in range(0, N, 97):
        point = {key: float(values[idx]) for key, values in INPUTS.items()}
        assert abs(result.awci[idx] - calc.calculate(point)["awci"]) <= 0.05 + 1e-9


def test_operational_profile_file_is_valid() -> None:
    profile = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
    assert profile.name == "operational-v1"
    assert sum(profile.weights.values()) == pytest.approx(1.0)
    assert profile.min_present_weight == 0.5


def _op_scores(theta_e: float) -> dict:
    one = lambda x: np.array([x])  # noqa: E731
    return operational_module_scores(
        wind_speed=one(25.0), layer_shear=one(10.0), theta_e=one(theta_e), mucape=one(1000.0),
        precip_rate=one(5.0), ptype_severity=one(0.2), elevation=one(300.0),
    )


def test_missing_module_is_renormalized_never_zero() -> None:
    profile = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
    full = combine(_op_scores(330.0), profile)
    missing = combine(_op_scores(np.nan), profile)
    assert np.isnan(missing.decomposition["thermodynamic"][0])
    assert missing.present_weight[0] == pytest.approx(full.present_weight[0] - 0.25)
    assert missing.awci[0] > 0.0 and np.isfinite(missing.awci[0])
    assert _op_scores(330.0)["temporal"] is None and _op_scores(330.0)["confidence"] is None


def test_insufficient_data_gives_null_awci() -> None:
    profile = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
    nan = np.array([np.nan])
    scores = operational_module_scores(
        wind_speed=nan, layer_shear=nan, theta_e=nan, mucape=nan,
        precip_rate=np.array([1.0]), ptype_severity=np.array([0.2]), elevation=np.array([10.0]),
    )
    assert np.isnan(combine(scores, profile).awci[0])


def test_level_codes_use_calculator_thresholds() -> None:
    codes = level_codes(np.array([10.0, 20.0, 49.9, 90.0, np.nan]), legacy_profile())
    np.testing.assert_array_equal(codes, [0, 1, 2, 5, -1])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_engine.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'acf.awci.ops.engine'`

- [ ] **Step 3: Write minimal implementation**

```json
// config/awci/profiles/operational-v1.json  (write WITHOUT this comment line - JSON has no comments)
{
  "name": "operational-v1",
  "version": "1.0.0",
  "min_present_weight": 0.5,
  "weights": {
    "dynamic": 0.20, "thermodynamic": 0.25, "convective": 0.20, "microphysical": 0.15,
    "topographic": 0.10, "temporal": 0.05, "confidence": 0.05,
    "ensemble_spread": 0.0, "model_disagreement": 0.0, "ceiling": 0.0, "visibility": 0.0,
    "dust": 0.0, "ash": 0.0, "microburst": 0.0
  },
  "interaction_terms": {
    "wind_topo_interaction": ["dynamic", "topographic"],
    "conv_thermo_interaction": ["convective", "thermodynamic"]
  },
  "interaction_weights": {"wind_topo_interaction": 0.05, "conv_thermo_interaction": 0.05},
  "level_thresholds": [[20.0, "Very Low"], [35.0, "Low"], [50.0, "Moderate"], [65.0, "High"], [85.0, "Very High"], [null, "Extreme"]]
}
```

```python
# src/acf/awci/ops/engine.py
"""
Vectorized AWCI engine.

Profile "legacy": exactly the mechanism and constants of AWCICalculator
(read from that class, not copied) - parity-tested.
Profile "operational-v1" (config/awci/profiles/operational-v1.json):
- dynamic       = 0.5 norm_wind(wind_speed) + 0.5 norm_wind_shear(layer_shear)
- thermodynamic = norm_theta_e(theta_e)          (replaces raw temperature)
- convective    = norm_cape(mucape)              (CIN no longer adds complexity)
- microphysical = 0.5 norm_precip(rate) + 0.5 ptype severity
- topographic   = norm_topographic(elevation)
- temporal, confidence: not fed in V1 -> None
Composite: awci = 100 * (sum w_m s_m + sum w_i prod s) / (sum present w_m + sum present w_i);
an interaction is present only if all its modules are; awci = NaN when sum present w_m < min_present_weight.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from acf.awci.calculator import AWCICalculator
from acf.awci.weights import WeightsManager

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OPERATIONAL_PROFILE_PATH = REPO_ROOT / "config" / "awci" / "profiles" / "operational-v1.json"


@dataclass(frozen=True)
class Profile:
    name: str
    version: str
    weights: dict[str, float]
    interaction_terms: dict[str, tuple[str, ...]]
    interaction_weights: dict[str, float]
    level_thresholds: tuple[tuple[float, str], ...]
    min_present_weight: float


def legacy_profile() -> Profile:
    return Profile(
        name="legacy",
        version="calculator",
        weights=dict(WeightsManager.DEFAULT_WEIGHTS),
        interaction_terms=dict(AWCICalculator.INTERACTION_TERMS),
        interaction_weights=dict(AWCICalculator.INTERACTION_WEIGHTS),
        level_thresholds=AWCICalculator.LEVEL_THRESHOLDS,
        min_present_weight=0.0,
    )


def load_profile(path: Path | str) -> Profile:
    payload: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
    profile = Profile(
        name=payload["name"],
        version=payload["version"],
        weights={k: float(v) for k, v in payload["weights"].items()},
        interaction_terms={k: tuple(v) for k, v in payload["interaction_terms"].items()},
        interaction_weights={k: float(v) for k, v in payload["interaction_weights"].items()},
        level_thresholds=tuple(
            (float("inf") if bound is None else float(bound), label) for bound, label in payload["level_thresholds"]
        ),
        min_present_weight=float(payload["min_present_weight"]),
    )
    AWCICalculator(  # reuse the calculator's own validation, never reimplemented
        weights=profile.weights,
        interaction_terms=profile.interaction_terms,
        interaction_weights=profile.interaction_weights,
        level_thresholds=profile.level_thresholds,
    )
    return profile


def _clip01(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return (np.clip(np.asarray(x, dtype=float), lo, hi) - lo) / (hi - lo)


def legacy_module_scores(inputs: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    shape = np.shape(next(iter(inputs.values())))

    def get(key: str, default: float) -> np.ndarray:
        return np.asarray(inputs.get(key, np.full(shape, default)), dtype=float)

    zeros = np.zeros(shape)
    scores = {
        "dynamic": _clip01(get("wind_speed", 0.0), 0.0, 50.0),
        "thermodynamic": 0.5 * _clip01(get("temperature", 273.15) - 273.15, -30.0, 50.0)
        + 0.5 * _clip01(get("specific_humidity", 0.001), 0.0, 0.03),
        "convective": 0.7 * _clip01(get("cape", 0.0), 0.0, 5000.0) + 0.3 * _clip01(np.abs(get("cin", 0.0)), 0.0, 500.0),
        "microphysical": _clip01(get("precipitation", 0.0), 0.0, 50.0),
        "topographic": _clip01(get("altitude", 0.0), 0.0, 3000.0),
        "temporal": _clip01(get("temporal_change", 0.0), 0.0, 20.0),
        "confidence": 1.0 - _clip01(get("confidence", 100.0), 0.0, 100.0),
    }
    for module in ("ensemble_spread", "model_disagreement", "ceiling", "visibility", "dust", "ash", "microburst"):
        scores[module] = zeros.copy()
    return scores


def operational_module_scores(
    *,
    wind_speed: np.ndarray,
    layer_shear: np.ndarray,
    theta_e: np.ndarray,
    mucape: np.ndarray,
    precip_rate: np.ndarray,
    ptype_severity: np.ndarray,
    elevation: np.ndarray,
) -> dict[str, np.ndarray | None]:
    return {
        "dynamic": 0.5 * _clip01(wind_speed, 0.0, 50.0) + 0.5 * _clip01(layer_shear, 0.0, 50.0),
        "thermodynamic": _clip01(theta_e, 250.0, 380.0),
        "convective": _clip01(mucape, 0.0, 5000.0),
        "microphysical": 0.5 * _clip01(precip_rate, 0.0, 50.0) + 0.5 * np.clip(np.asarray(ptype_severity, dtype=float), 0.0, 1.0),
        "topographic": _clip01(elevation, 0.0, 3000.0),
        "temporal": None,
        "confidence": None,
    }


@dataclass
class CompositeResult:
    awci: np.ndarray
    decomposition: dict[str, np.ndarray]
    present_weight: np.ndarray


def combine(module_scores: dict[str, np.ndarray | None], profile: Profile) -> CompositeResult:
    arrays = [a for a in module_scores.values() if a is not None]
    shape = np.broadcast_shapes(*(np.shape(a) for a in arrays))
    weighted: dict[str, np.ndarray] = {}
    budget = np.zeros(shape)
    present_weight = np.zeros(shape)
    total = np.zeros(shape)
    for module, weight in profile.weights.items():
        score = module_scores.get(module)
        if score is None or weight == 0.0:
            weighted[module] = np.full(shape, np.nan if score is None else 0.0)
            continue
        score = np.broadcast_to(np.asarray(score, dtype=float), shape)
        present = np.isfinite(score)
        contrib = np.where(present, weight * score, np.nan)
        weighted[module] = contrib
        total += np.nan_to_num(contrib)
        budget += present * weight
        present_weight += present * weight
    for term, modules in profile.interaction_terms.items():
        weight = profile.interaction_weights[term]
        parts = [module_scores.get(m) for m in modules]
        if any(p is None for p in parts):
            weighted[term] = np.full(shape, np.nan)
            continue
        product = np.ones(shape)
        for part in parts:
            product = product * np.broadcast_to(np.asarray(part, dtype=float), shape)
        present = np.isfinite(product)
        contrib = np.where(present, weight * product, np.nan)
        weighted[term] = contrib
        total += np.nan_to_num(contrib)
        budget += present * weight
    with np.errstate(divide="ignore", invalid="ignore"):
        awci = np.where((budget > 0) & (present_weight >= profile.min_present_weight), 100.0 * total / budget, np.nan)
        decomposition = {k: 100.0 * v / budget for k, v in weighted.items()}
    return CompositeResult(awci=awci, decomposition=decomposition, present_weight=present_weight)


def level_codes(awci: np.ndarray, profile: Profile) -> np.ndarray:
    bounds = np.asarray([b for b, _ in profile.level_thresholds[:-1]])
    awci = np.asarray(awci, dtype=float)
    codes = np.searchsorted(bounds, np.nan_to_num(awci), side="right").astype(np.int8)
    return np.where(np.isfinite(awci), codes, np.int8(-1)).astype(np.int8)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_engine.py`
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add src/acf/awci/ops/engine.py config/awci/profiles/operational-v1.json tests/test_awci_ops_engine.py
git commit -m "feat(awci-ops): vectorized AWCI engine, legacy parity + operational-v1 profile"
```

---

### Task 6: Domains and ECMWF source (`domains.py`, `source_ecmwf.py`)

**Files:**
- Create: `src/acf/awci/ops/domains.py`, `src/acf/awci/ops/source_ecmwf.py`, `config/awci/domains.json`
- Test: `tests/test_awci_ops_source.py`

**Interfaces:**
- Produces:
  - `Domain(name, label, south, north, west, east, default)`; `load_domains(path=DEFAULT_DOMAINS_PATH) -> dict[str, Domain]` (raises `ValueError` on invalid bbox / no or several defaults); `Domain.crop_indices(lats, lons) -> tuple[ndarray, ndarray]`.
  - `PL_PARAMS`, `PL_LEVELS`, `SFC_PARAMS`, `IndexEntry(param, levtype, level, offset, length)`, `parse_index(text) -> list[IndexEntry]`, `select_entries(entries) -> list[IndexEntry]` (raises `MissingFieldsError` listing absent `(param, level)`), `step_urls(run: datetime, step: int) -> tuple[str, str]`, `Fetcher` protocol (`get_text(url)`, `get_range(url, offset, length)`), `UrllibFetcher(retries=4, backoff_s=(2,4,8,16), sleep=time.sleep)`, `fetch_step_messages(fetcher, run, step, max_workers=8) -> list[bytes]`, `find_latest_run(fetcher, now, last_step) -> datetime`, `FetchError`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_awci_ops_source.py
import json
from datetime import UTC, datetime

import numpy as np
import pytest

from acf.awci.ops.domains import DEFAULT_DOMAINS_PATH, load_domains
from acf.awci.ops.source_ecmwf import (
    PL_LEVELS,
    PL_PARAMS,
    SFC_PARAMS,
    FetchError,
    MissingFieldsError,
    UrllibFetcher,
    find_latest_run,
    parse_index,
    select_entries,
    step_urls,
)


def _index_text(drop: tuple[str, int | None] | None = None) -> str:
    lines, offset = [], 0
    for p in PL_PARAMS:
        for lev in PL_LEVELS:
            if drop != (p, lev):
                lines.append(json.dumps({"param": p, "levtype": "pl", "levelist": str(lev), "_offset": offset, "_length": 10}))
            offset += 10
    for p in SFC_PARAMS:
        if drop != (p, None):
            lines.append(json.dumps({"param": p, "levtype": "sfc", "_offset": offset, "_length": 10}))
        offset += 10
    lines.append(json.dumps({"param": "vo", "levtype": "pl", "levelist": "500", "_offset": offset, "_length": 10}))
    return "\n".join(lines)


def test_default_domain_config() -> None:
    domains = load_domains(DEFAULT_DOMAINS_PATH)
    default = [d for d in domains.values() if d.default]
    assert len(default) == 1 and default[0].name == "north_africa"


@pytest.mark.parametrize("bbox", [(15, 45, 40, -20), (45, 15, -20, 40)])
def test_invalid_domain_bbox_rejected(tmp_path, bbox) -> None:
    south, north, west, east = bbox
    path = tmp_path / "d.json"
    path.write_text(json.dumps({"domains": [{"name": "x", "label": "x", "south": south, "north": north,
                                             "west": west, "east": east, "default": True}]}))
    with pytest.raises(ValueError):
        load_domains(path)


def test_crop_indices() -> None:
    domain = load_domains(DEFAULT_DOMAINS_PATH)["north_africa"]
    lats = np.arange(-90.0, 90.25, 0.25)
    lons = np.arange(-180.0, 180.0, 0.25)
    iy, ix = domain.crop_indices(lats, lons)
    assert lats[iy].min() == 15.0 and lats[iy].max() == 45.0
    assert lons[ix].min() == -20.0 and lons[ix].max() == 40.0


def test_parse_and_select_index() -> None:
    selected = select_entries(parse_index(_index_text()))
    assert len(selected) == len(PL_PARAMS) * len(PL_LEVELS) + len(SFC_PARAMS)
    assert all(e.param != "vo" for e in selected)


def test_missing_field_is_reported() -> None:
    with pytest.raises(MissingFieldsError, match="mucape"):
        select_entries(parse_index(_index_text(drop=("mucape", None))))


def test_step_urls() -> None:
    grib, index = step_urls(datetime(2026, 9, 25, 6, tzinfo=UTC), 3)
    assert grib == "https://data.ecmwf.int/forecasts/20260925/06z/ifs/0p25/oper/20260925060000-3h-oper-fc.grib2"
    assert index.endswith("-3h-oper-fc.index")


class _FakeFetcher:
    def __init__(self, available: set[str]) -> None:
        self.available = available

    def get_text(self, url: str) -> str:
        if url not in self.available:
            raise FetchError(url)
        return ""

    def get_range(self, url: str, offset: int, length: int) -> bytes:
        raise NotImplementedError


def test_latest_run_falls_back_when_last_step_not_published() -> None:
    now = datetime(2026, 9, 25, 14, 0, tzinfo=UTC)
    newest_last = step_urls(datetime(2026, 9, 25, 6, tzinfo=UTC), 72)[1]
    previous_last = step_urls(datetime(2026, 9, 25, 0, tzinfo=UTC), 72)[1]
    fetcher = _FakeFetcher({previous_last})
    assert newest_last not in fetcher.available
    assert find_latest_run(fetcher, now, last_step=72) == datetime(2026, 9, 25, 0, tzinfo=UTC)


def test_urllib_fetcher_retries_then_fails(monkeypatch) -> None:
    calls: list[str] = []
    sleeps: list[float] = []

    def boom(*args, **kwargs):
        calls.append("x")
        raise OSError("down")

    monkeypatch.setattr("acf.awci.ops.source_ecmwf.urllib.request.urlopen", boom)
    fetcher = UrllibFetcher(sleep=sleeps.append)
    with pytest.raises(FetchError):
        fetcher.get_text("https://example.invalid/x")
    assert len(calls) == 5 and sleeps == [2, 4, 8, 16]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_source.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'acf.awci.ops.domains'`

- [ ] **Step 3: Write minimal implementation**

```json
{
  "domains": [
    {"name": "north_africa", "label": "Afrique du Nord / Méditerranée", "south": 15.0, "north": 45.0,
     "west": -20.0, "east": 40.0, "default": true}
  ]
}
```
(save as `config/awci/domains.json`)

```python
# src/acf/awci/ops/domains.py
"""Configured AWCI Web domains (config/awci/domains.json). Antimeridian-crossing boxes are not supported in V1."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

DEFAULT_DOMAINS_PATH = Path(__file__).resolve().parents[4] / "config" / "awci" / "domains.json"


@dataclass(frozen=True)
class Domain:
    name: str
    label: str
    south: float
    north: float
    west: float
    east: float
    default: bool = False

    def crop_indices(self, lats: np.ndarray, lons: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        lats, lons = np.asarray(lats), np.asarray(lons)
        iy = np.where((lats >= self.south - 1e-9) & (lats <= self.north + 1e-9))[0]
        ix = np.where((lons >= self.west - 1e-9) & (lons <= self.east + 1e-9))[0]
        return iy, ix

    def contains(self, lat: float, lon: float) -> bool:
        return self.south <= lat <= self.north and self.west <= lon <= self.east


def load_domains(path: Path | str = DEFAULT_DOMAINS_PATH) -> dict[str, Domain]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    domains: dict[str, Domain] = {}
    for raw in payload["domains"]:
        domain = Domain(
            name=str(raw["name"]), label=str(raw["label"]),
            south=float(raw["south"]), north=float(raw["north"]),
            west=float(raw["west"]), east=float(raw["east"]), default=bool(raw.get("default", False)),
        )
        if not (-90.0 <= domain.south < domain.north <= 90.0):
            raise ValueError(f"domain {domain.name!r}: need -90 <= south < north <= 90")
        if not (-180.0 <= domain.west < domain.east < 180.0):
            raise ValueError(f"domain {domain.name!r}: need -180 <= west < east < 180 (no antimeridian crossing)")
        if domain.name in domains:
            raise ValueError(f"duplicate domain name {domain.name!r}")
        domains[domain.name] = domain
    if sum(d.default for d in domains.values()) != 1:
        raise ValueError("exactly one domain must have default: true")
    return domains
```

```python
# src/acf/awci/ops/source_ecmwf.py
"""
ECMWF IFS 0.25 deg Open Data source (CC-BY-4.0, attribution "© ECMWF, CC-BY-4.0").

Layout: {BASE_URL}/{YYYYMMDD}/{HH}z/ifs/0p25/oper/{YYYYMMDDHH0000}-{step}h-oper-fc.{grib2,index}
The .index file is JSON-lines with param/levtype/levelist/_offset/_length; only the
needed messages are downloaded with HTTP Range requests (stdlib urllib, no new dependency).
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

BASE_URL = "https://data.ecmwf.int/forecasts"
PL_PARAMS: tuple[str, ...] = ("t", "q", "r", "u", "v", "w", "gh", "d")
PL_LEVELS: tuple[int, ...] = (1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100)
SFC_PARAMS: tuple[str, ...] = ("2t", "2d", "10u", "10v", "10fg", "sp", "msl", "mucape", "tprate", "ptype", "tcc", "lsm")
RUN_HOURS = (0, 6, 12, 18)
USER_AGENT = "ACF-AWCI-Web/1.0 (+https://github.com/fourasohaib2-lab/ACF)"


class FetchError(RuntimeError):
    """A URL could not be fetched after all retries."""


class MissingFieldsError(RuntimeError):
    """The index lacks required (param, level) messages."""


@dataclass(frozen=True)
class IndexEntry:
    param: str
    levtype: str
    level: int | None
    offset: int
    length: int


class Fetcher(Protocol):
    def get_text(self, url: str) -> str: ...

    def get_range(self, url: str, offset: int, length: int) -> bytes: ...


class UrllibFetcher:
    def __init__(
        self,
        timeout_s: float = 60.0,
        backoff_s: Sequence[float] = (2, 4, 8, 16),
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.timeout_s = timeout_s
        self.backoff_s = tuple(backoff_s)
        self.sleep = sleep

    def _get(self, url: str, headers: dict[str, str], expected_length: int | None = None) -> bytes:
        last_error: Exception | None = None
        for attempt in range(len(self.backoff_s) + 1):
            try:
                request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **headers})
                with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                    data = response.read()
                if expected_length is not None and len(data) != expected_length:
                    raise FetchError(f"{url}: got {len(data)} bytes, index announced {expected_length}")
                return data
            except (OSError, urllib.error.URLError, FetchError) as exc:
                last_error = exc
                if attempt < len(self.backoff_s):
                    self.sleep(self.backoff_s[attempt])
        raise FetchError(f"{url}: {last_error}")

    def get_text(self, url: str) -> str:
        return self._get(url, {}).decode("utf-8")

    def get_range(self, url: str, offset: int, length: int) -> bytes:
        return self._get(url, {"Range": f"bytes={offset}-{offset + length - 1}"}, expected_length=length)


def step_urls(run: datetime, step: int) -> tuple[str, str]:
    stem = f"{BASE_URL}/{run:%Y%m%d}/{run:%H}z/ifs/0p25/oper/{run:%Y%m%d%H}0000-{step}h-oper-fc"
    return f"{stem}.grib2", f"{stem}.index"


def parse_index(text: str) -> list[IndexEntry]:
    entries = []
    for line in text.splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        level = raw.get("levelist")
        entries.append(IndexEntry(raw["param"], raw.get("levtype", ""), int(level) if level is not None else None,
                                  int(raw["_offset"]), int(raw["_length"])))
    return entries


def select_entries(entries: list[IndexEntry]) -> list[IndexEntry]:
    wanted = {(p, lev) for p in PL_PARAMS for lev in PL_LEVELS} | {(p, None) for p in SFC_PARAMS}
    chosen = {}
    for entry in entries:
        key = (entry.param, entry.level if entry.levtype == "pl" else None)
        if key in wanted and key not in chosen:
            chosen[key] = entry
    missing = sorted(wanted - chosen.keys(), key=str)
    if missing:
        raise MissingFieldsError(f"index lacks {missing}")
    return sorted(chosen.values(), key=lambda e: e.offset)


def fetch_step_messages(fetcher: Fetcher, run: datetime, step: int, max_workers: int = 8) -> list[bytes]:
    grib_url, index_url = step_urls(run, step)
    entries = select_entries(parse_index(fetcher.get_text(index_url)))
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return list(pool.map(lambda e: fetcher.get_range(grib_url, e.offset, e.length), entries))


def find_latest_run(fetcher: Fetcher, now: datetime, last_step: int, max_lookback_runs: int = 8) -> datetime:
    run = now.replace(minute=0, second=0, microsecond=0)
    run = run.replace(hour=max(h for h in RUN_HOURS if h <= run.hour))
    for _ in range(max_lookback_runs):
        try:
            fetcher.get_text(step_urls(run, last_step)[1])
            return run
        except FetchError:
            run -= timedelta(hours=6)
    raise FetchError(f"no run with step {last_step} published in the last {max_lookback_runs} runs")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_source.py`
Expected: PASS (10 tests)

- [ ] **Step 5: Commit**

```bash
git add src/acf/awci/ops/domains.py src/acf/awci/ops/source_ecmwf.py config/awci/domains.json tests/test_awci_ops_source.py
git commit -m "feat(awci-ops): domain config and ECMWF open-data index/range source"
```

---

### Task 7: Real GRIB fixture and decoding (`decode.py`)

**Files:**
- Create: `tools/awci/make_ops_fixture.py`, `tests/data/awci_ops/NOTICE.md`, `tests/data/awci_ops/*.grib2|*.index` (generated), `src/acf/awci/ops/decode.py`
- Test: `tests/test_awci_ops_decode.py`

**Interfaces:**
- Consumes: `PL_PARAMS`, `PL_LEVELS`, `SFC_PARAMS`, `Domain`.
- Produces:
  - `@dataclass StepFields(lats: ndarray, lons: ndarray, levels_hpa: ndarray, pl: dict[str, ndarray], sfc: dict[str, ndarray])` — `lats` ascending, `pl[param]` shape `(level, lat, lon)` in `PL_LEVELS` order, `sfc[param]` shape `(lat, lon)`.
  - `decode_messages(messages: list[bytes], domains: list[Domain]) -> dict[str, StepFields]`.
  - `FIXTURE_DIR = tests/data/awci_ops`, fixture run `2026-09-25 00Z`, steps `0, 3`, box 35–37°N, 2–4°E (9×9).

- [ ] **Step 1: Generate the real fixture (network, one-off)**

```python
# tools/awci/make_ops_fixture.py
"""
Regenerate tests/data/awci_ops: download the real ECMWF IFS Open Data messages
AWCI Web needs for run 2026-09-25 00Z, steps 0 and 3, crop them to 35-37N / 2-4E
with eccodes, and write a matching .index. Data: © ECMWF, CC-BY-4.0.
Usage: .venv/bin/python tools/awci/make_ops_fixture.py
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import eccodes
import numpy as np

from acf.awci.ops.source_ecmwf import UrllibFetcher, parse_index, select_entries, step_urls

OUT = Path(__file__).resolve().parents[2] / "tests" / "data" / "awci_ops"
RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)
BOX = (35.0, 37.0, 2.0, 4.0)  # south, north, west, east


def crop(message: bytes) -> bytes:
    handle = eccodes.codes_new_from_message(message)
    try:
        ni, nj = eccodes.codes_get(handle, "Ni"), eccodes.codes_get(handle, "Nj")
        values = eccodes.codes_get_values(handle).reshape(nj, ni)
        lats = 90.0 - 0.25 * np.arange(nj)
        lons = -180.0 + 0.25 * np.arange(ni)
        iy = np.where((lats >= BOX[0]) & (lats <= BOX[1]))[0]
        ix = np.where((lons >= BOX[2]) & (lons <= BOX[3]))[0]
        clone = eccodes.codes_clone(handle)
        for key, value in (("Ni", len(ix)), ("Nj", len(iy)),
                           ("latitudeOfFirstGridPointInDegrees", float(lats[iy[0]])),
                           ("latitudeOfLastGridPointInDegrees", float(lats[iy[-1]])),
                           ("longitudeOfFirstGridPointInDegrees", float(lons[ix[0]])),
                           ("longitudeOfLastGridPointInDegrees", float(lons[ix[-1]]))):
            eccodes.codes_set(clone, key, value)
        eccodes.codes_set_values(clone, values[np.ix_(iy, ix)].ravel())
        data = eccodes.codes_get_message(clone)
        eccodes.codes_release(clone)
        return data
    finally:
        eccodes.codes_release(handle)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fetcher = UrllibFetcher()
    for step in (0, 3):
        grib_url, index_url = step_urls(RUN, step)
        entries = select_entries(parse_index(fetcher.get_text(index_url)))
        stem = Path(grib_url).name.removesuffix(".grib2")
        offset, blobs, index_lines = 0, [], []
        for entry in entries:
            blob = crop(fetcher.get_range(grib_url, entry.offset, entry.length))
            line = {"param": entry.param, "levtype": entry.levtype, "_offset": offset, "_length": len(blob)}
            if entry.level is not None:
                line["levelist"] = str(entry.level)
            index_lines.append(json.dumps(line))
            blobs.append(blob)
            offset += len(blob)
        (OUT / f"{stem}.grib2").write_bytes(b"".join(blobs))
        (OUT / f"{stem}.index").write_text("\n".join(index_lines) + "\n")
        print(f"step {step}: {len(entries)} messages, {offset} bytes")


if __name__ == "__main__":
    main()
```

Run: `.venv/bin/python tools/awci/make_ops_fixture.py`
Expected: `step 0: 108 messages, …` and `step 3: 108 messages, …` (a few tens of kB each).

Write `tests/data/awci_ops/NOTICE.md`:

```markdown
# AWCI ops test fixture

Real ECMWF IFS 0.25° Open Data (run 2026-09-25 00Z, steps 0 h and 3 h), the
108 messages AWCI Web ingests, cropped with eccodes to 35–37°N / 2–4°E (9×9).
Regenerate with `tools/awci/make_ops_fixture.py`.

Source: https://data.ecmwf.int/forecasts/ — © ECMWF, licensed CC-BY-4.0
(https://creativecommons.org/licenses/by/4.0/). Values are unmodified apart
from the spatial crop.
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_awci_ops_decode.py
from pathlib import Path

import numpy as np
import pytest

from acf.awci.ops.decode import decode_messages
from acf.awci.ops.domains import Domain
from acf.awci.ops.hazards import ECMWF_PTYPE_SEVERITY
from acf.awci.ops.source_ecmwf import PL_LEVELS, PL_PARAMS, SFC_PARAMS, parse_index

FIXTURE = Path(__file__).parent / "data" / "awci_ops"
STEM = "20260925000000-3h-oper-fc"


def _messages() -> list[bytes]:
    data = (FIXTURE / f"{STEM}.grib2").read_bytes()
    return [data[e.offset : e.offset + e.length] for e in parse_index((FIXTURE / f"{STEM}.index").read_text())]


FULL = Domain("fixture", "fixture", 35.0, 37.0, 2.0, 4.0, True)
SUB = Domain("sub", "sub", 35.5, 36.5, 2.5, 3.5, False)


def test_decode_full_fixture_domain() -> None:
    fields = decode_messages(_messages(), [FULL])["fixture"]
    assert fields.lats[0] == 35.0 and fields.lats[-1] == 37.0 and np.all(np.diff(fields.lats) > 0)
    assert fields.lons[0] == 2.0 and fields.lons[-1] == 4.0
    np.testing.assert_array_equal(fields.levels_hpa, PL_LEVELS)
    for p in PL_PARAMS:
        assert fields.pl[p].shape == (len(PL_LEVELS), 9, 9)
    for p in SFC_PARAMS:
        assert fields.sfc[p].shape == (9, 9)


def test_physical_plausibility_and_level_order() -> None:
    f = decode_messages(_messages(), [FULL])["fixture"]
    t = f.pl["t"]
    assert 180.0 < t.min() and t.max() < 330.0
    assert np.all(np.diff(f.pl["gh"].mean(axis=(1, 2))) > 0)  # 1000 -> 100 hPa: height increases
    assert 0.0 <= f.pl["q"].min() and f.pl["q"].max() < 0.04
    assert set(np.unique(f.sfc["ptype"])) <= set(ECMWF_PTYPE_SEVERITY)


def test_sub_domain_crop_is_consistent() -> None:
    both = decode_messages(_messages(), [FULL, SUB])
    full, sub = both["fixture"], both["sub"]
    assert sub.pl["t"].shape == (len(PL_LEVELS), 5, 5)
    iy = np.searchsorted(full.lats, sub.lats)
    ix = np.searchsorted(full.lons, sub.lons)
    np.testing.assert_array_equal(sub.pl["t"], full.pl["t"][:, iy][:, :, ix])


def test_missing_message_is_an_error() -> None:
    with pytest.raises(ValueError, match="missing"):
        decode_messages(_messages()[1:], [FULL])
```

- [ ] **Step 3: Run test to verify it fails**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_decode.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'acf.awci.ops.decode'`

- [ ] **Step 4: Write minimal implementation**

```python
# src/acf/awci/ops/decode.py
"""
GRIB2 message bytes -> cropped NumPy arrays per domain (eccodes, no cfgrib).

Grid geometry is read from each message (Ni, Nj, first-point lat/lon, increments,
jScansPositively), longitudes are wrapped to [-180, 180) and latitudes returned
ascending. Missing values (bitmap) become NaN.
"""

from __future__ import annotations

from dataclasses import dataclass

import eccodes
import numpy as np

from acf.awci.ops.domains import Domain
from acf.awci.ops.source_ecmwf import PL_LEVELS, PL_PARAMS, SFC_PARAMS


@dataclass
class StepFields:
    lats: np.ndarray
    lons: np.ndarray
    levels_hpa: np.ndarray
    pl: dict[str, np.ndarray]
    sfc: dict[str, np.ndarray]


def _read(message: bytes) -> tuple[str, int | None, np.ndarray, np.ndarray, np.ndarray]:
    handle = eccodes.codes_new_from_message(message)
    try:
        get = lambda key: eccodes.codes_get(handle, key)  # noqa: E731
        ni, nj = get("Ni"), get("Nj")
        di, dj = get("iDirectionIncrementInDegrees"), get("jDirectionIncrementInDegrees")
        lat0, lon0 = get("latitudeOfFirstGridPointInDegrees"), get("longitudeOfFirstGridPointInDegrees")
        lats = lat0 + (dj if get("jScansPositively") else -dj) * np.arange(nj)
        lons = (lon0 + di * np.arange(ni) + 180.0) % 360.0 - 180.0
        values = eccodes.codes_get_values(handle).astype(float).reshape(nj, ni)
        if get("bitmapPresent"):
            values[values == get("missingValue")] = np.nan
        level = int(get("level")) if get("typeOfLevel") == "isobaricInhPa" else None
        return str(get("shortName")), level, lats, lons, values
    finally:
        eccodes.codes_release(handle)


def decode_messages(messages: list[bytes], domains: list[Domain]) -> dict[str, StepFields]:
    decoded: dict[tuple[str, int | None], np.ndarray] = {}
    lats = lons = None
    for message in messages:
        name, level, m_lats, m_lons, values = _read(message)
        lat_order = np.argsort(m_lats)
        lon_order = np.argsort(m_lons)
        if lats is None:
            lats, lons = m_lats[lat_order], m_lons[lon_order]
        decoded[(name, level)] = values[np.ix_(lat_order, lon_order)]
    wanted = [(p, lev) for p in PL_PARAMS for lev in PL_LEVELS] + [(p, None) for p in SFC_PARAMS]
    missing = [key for key in wanted if key not in decoded]
    if missing or lats is None or lons is None:
        raise ValueError(f"missing GRIB messages: {missing}")
    out: dict[str, StepFields] = {}
    for domain in domains:
        iy, ix = domain.crop_indices(lats, lons)
        sub = lambda arr: arr[np.ix_(iy, ix)]  # noqa: E731
        out[domain.name] = StepFields(
            lats=lats[iy],
            lons=lons[ix],
            levels_hpa=np.asarray(PL_LEVELS, dtype=float),
            pl={p: np.stack([sub(decoded[(p, lev)]) for lev in PL_LEVELS]) for p in PL_PARAMS},
            sfc={p: sub(decoded[(p, None)]) for p in SFC_PARAMS},
        )
    return out
```

Note: messages are keyed by eccodes `shortName`, which matches the index `param` for every requested field (checked on real IFS messages: `t`, `2t`, `mucape`, `tprate`, `ptype`). If a future IFS change breaks that, `decode_messages` raises `missing GRIB messages: [...]` naming the key — never a silent gap.

- [ ] **Step 5: Run test to verify it passes**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_decode.py`
Expected: PASS (4 tests)

- [ ] **Step 6: Commit**

```bash
git add tools/awci/make_ops_fixture.py tests/data/awci_ops src/acf/awci/ops/decode.py tests/test_awci_ops_decode.py
git commit -m "feat(awci-ops): eccodes GRIB decoding + real cropped IFS fixture (CC-BY-4.0)"
```

---

### Task 8: Step pipeline and cube storage (`pipeline.py`, `store.py`)

**Files:**
- Create: `src/acf/awci/ops/pipeline.py`, `src/acf/awci/ops/store.py`
- Test: `tests/test_awci_ops_pipeline_store.py`

**Interfaces:**
- Consumes: Tasks 2–5, 7 (`StepFields`, all diagnostics, `operational_module_scores`, `combine`, `level_codes`, `Profile`), `acf.awci.terrain_elevation.interpolate_real_terrain_elevation`.
- Produces:
  - `LEVEL_LAYERS: tuple[str, ...]` = `("t","q","r","u","v","w","gh","wind_speed","layer_shear","vertical_shear","cat_ti2","cat_category","icing_potential","theta_e","awci","awci_level","module_dynamic","module_thermodynamic","module_convective","module_microphysical","module_topographic")`
  - `SURFACE_LAYERS: tuple[str, ...]` = `("t2m","d2m","rh2m","mucape","cloud_base_lcl","precip_rate","precip_class","precip_type","ptype_severity","gust_10m","dust_proxy","tcc","sp_hpa")`
  - `compute_step(fields: StepFields, elevation: ndarray, profile: Profile) -> dict[str, ndarray]`
  - `CubeWriter(root, domain, run, lats, lons, levels_hpa, steps, profile)` with `.write_step(step_index, layers, elevation)`, `.finalize(status, missing_steps, extra) -> dict` (manifest), `.abort()`
  - `run_id(run: datetime) -> str` (`YYYYMMDDHH`), `apply_retention(root, domain, keep) -> list[str]`
  - `CubeStore(root)` with `.runs(domain) -> list[dict]`, `.manifest(domain, run_id) -> dict`, `.dataset(domain, run_id) -> xarray.Dataset`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_awci_ops_pipeline_store.py
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pytest

from acf.awci.ops.decode import decode_messages
from acf.awci.ops.domains import Domain
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.pipeline import LEVEL_LAYERS, SURFACE_LAYERS, compute_step
from acf.awci.ops.source_ecmwf import parse_index
from acf.awci.ops.store import CubeStore, CubeWriter, apply_retention, run_id
from acf.awci.terrain_elevation import interpolate_real_terrain_elevation

FIXTURE = Path(__file__).parent / "data" / "awci_ops"
DOMAIN = Domain("fixture", "fixture", 35.0, 37.0, 2.0, 4.0, True)
PROFILE = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)


def _fields(step: int):
    stem = f"20260925000000-{step}h-oper-fc"
    data = (FIXTURE / f"{stem}.grib2").read_bytes()
    msgs = [data[e.offset : e.offset + e.length] for e in parse_index((FIXTURE / f"{stem}.index").read_text())]
    return decode_messages(msgs, [DOMAIN])["fixture"]


def _write_cube(root: Path, steps=(0, 3), fail_step: int | None = None) -> dict:
    f0 = _fields(0)
    elevation = interpolate_real_terrain_elevation(f0.lats, f0.lons)
    writer = CubeWriter(root, DOMAIN, RUN, f0.lats, f0.lons, f0.levels_hpa, list(steps), PROFILE)
    missing = []
    for i, step in enumerate(steps):
        if step == fail_step:
            missing.append(step)
            continue
        writer.write_step(i, compute_step(_fields(step), elevation, PROFILE), elevation)
    return writer.finalize("partial" if missing else "complete", missing, {})


def test_compute_step_shapes_and_ranges() -> None:
    f = _fields(3)
    layers = compute_step(f, interpolate_real_terrain_elevation(f.lats, f.lons), PROFILE)
    for name in LEVEL_LAYERS:
        assert layers[name].shape == (12, 9, 9), name
    for name in SURFACE_LAYERS:
        assert layers[name].shape == (9, 9), name
    awci = layers["awci"]
    assert np.all((awci[np.isfinite(awci)] >= 0) & (awci[np.isfinite(awci)] <= 100))
    assert np.isfinite(awci).mean() > 0.9


def test_cube_roundtrip_manifest_and_nan_not_zero(tmp_path: Path) -> None:
    manifest = _write_cube(tmp_path)
    assert manifest["status"] == "complete" and manifest["steps"] == [0, 3]
    assert manifest["license"] == "CC-BY-4.0" and manifest["profile"] == "operational-v1"
    store = CubeStore(tmp_path)
    assert [r["run"] for r in store.runs("fixture")] == ["2026092500"]
    ds = store.dataset("fixture", "2026092500")
    assert ds["awci"].shape == (2, 12, 9, 9)
    assert ds["elevation"].shape == (9, 9)
    assert not (tmp_path / "fixture" / "2026092500.tmp").exists()


def test_partial_run_is_marked(tmp_path: Path) -> None:
    manifest = _write_cube(tmp_path, fail_step=3)
    assert manifest["status"] == "partial" and manifest["missing_steps"] == [3]
    ds = CubeStore(tmp_path).dataset("fixture", "2026092500")
    assert np.isnan(ds["awci"].isel(step=1)).all()


def test_two_ingestions_are_identical(tmp_path: Path) -> None:
    _write_cube(tmp_path / "a")
    _write_cube(tmp_path / "b")
    a = CubeStore(tmp_path / "a").dataset("fixture", "2026092500")
    b = CubeStore(tmp_path / "b").dataset("fixture", "2026092500")
    for name in a.data_vars:
        np.testing.assert_array_equal(a[name].values, b[name].values)


def test_retention_keeps_newest(tmp_path: Path) -> None:
    for rid in ("2026092400", "2026092406", "2026092412"):
        d = tmp_path / "fixture" / rid
        d.mkdir(parents=True)
        (d / "manifest.json").write_text(json.dumps({"run": rid}))
    assert apply_retention(tmp_path, "fixture", keep=2) == ["2026092400"]
    assert sorted(p.name for p in (tmp_path / "fixture").iterdir()) == ["2026092406", "2026092412"]


def test_run_id() -> None:
    assert run_id(RUN) == "2026092500"


def test_unknown_run_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        CubeStore(tmp_path).manifest("fixture", "2026010100")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_pipeline_store.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'acf.awci.ops.pipeline'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/acf/awci/ops/pipeline.py
"""One forecast step: decoded IFS fields -> every served layer + operational AWCI."""

from __future__ import annotations

import numpy as np

from acf.awci.ops.decode import StepFields
from acf.awci.ops.engine import Profile, combine, level_codes, operational_module_scores
from acf.awci.ops.hazards import (
    dust_proxy,
    icing_potential,
    precip_class_codes,
    precip_rate_mm_h,
    ptype_severity,
    relative_humidity_2m_pct,
)
from acf.awci.ops.kinematics import cat_category_codes, ellrod_ti2, layer_shear, wind_speed
from acf.awci.ops.thermo import cloud_base_lcl_m, theta_e_bolton_k

_MODULES = ("dynamic", "thermodynamic", "convective", "microphysical", "topographic")
LEVEL_LAYERS: tuple[str, ...] = (
    "t", "q", "r", "u", "v", "w", "gh", "wind_speed", "layer_shear", "vertical_shear", "cat_ti2",
    "cat_category", "icing_potential", "theta_e", "awci", "awci_level", *(f"module_{m}" for m in _MODULES),
)
SURFACE_LAYERS: tuple[str, ...] = (
    "t2m", "d2m", "rh2m", "mucape", "cloud_base_lcl", "precip_rate", "precip_class", "precip_type",
    "ptype_severity", "gust_10m", "dust_proxy", "tcc", "sp_hpa",
)


def compute_step(fields: StepFields, elevation: np.ndarray, profile: Profile) -> dict[str, np.ndarray]:
    pl, sfc = fields.pl, fields.sfc
    p3d = fields.levels_hpa[:, None, None] * np.ones_like(pl["t"])
    ws = wind_speed(pl["u"], pl["v"])
    shear, vws = layer_shear(pl["u"], pl["v"], pl["gh"])
    ti2 = ellrod_ti2(pl["u"], pl["v"], pl["gh"], pl["d"], fields.lats, fields.lons)
    theta_e = theta_e_bolton_k(pl["t"], pl["q"], p3d)
    rate = precip_rate_mm_h(sfc["tprate"])
    severity = ptype_severity(sfc["ptype"])
    rh2m = relative_humidity_2m_pct(sfc["2t"], sfc["2d"])

    scores = operational_module_scores(
        wind_speed=ws, layer_shear=shear, theta_e=theta_e, mucape=sfc["mucape"][None],
        precip_rate=rate[None], ptype_severity=severity[None], elevation=np.asarray(elevation, dtype=float)[None],
    )
    composite = combine(scores, profile)
    shape = pl["t"].shape
    layers: dict[str, np.ndarray] = {p: pl[p] for p in ("t", "q", "r", "u", "v", "w", "gh")}
    layers.update(
        wind_speed=ws, layer_shear=shear, vertical_shear=vws, cat_ti2=ti2,
        cat_category=cat_category_codes(ti2).astype(float), icing_potential=icing_potential(pl["t"], pl["r"]),
        theta_e=theta_e, awci=composite.awci, awci_level=level_codes(composite.awci, profile).astype(float),
    )
    for module in _MODULES:
        layers[f"module_{module}"] = np.broadcast_to(np.asarray(scores[module], dtype=float), shape).copy()
    layers.update(
        t2m=sfc["2t"], d2m=sfc["2d"], rh2m=rh2m, mucape=sfc["mucape"],
        cloud_base_lcl=cloud_base_lcl_m(sfc["2t"], sfc["2d"]), precip_rate=rate,
        precip_class=precip_class_codes(rate).astype(float), precip_type=sfc["ptype"], ptype_severity=severity,
        gust_10m=sfc["10fg"], dust_proxy=dust_proxy(sfc["10fg"], rh2m), tcc=sfc["tcc"], sp_hpa=sfc["sp"] / 100.0,
    )
    for name in ("cat_category", "awci_level", "precip_class"):
        layers[name] = np.where(layers[name] < 0, np.nan, layers[name])
    return layers
```

```python
# src/acf/awci/ops/store.py
"""
NetCDF4 cube per (domain, run): data/awci/{domain}/{YYYYMMDDHH}/{cube.nc, manifest.json}.
Written into {run}.tmp/ then renamed atomically. Float32, zlib level 4, NaN = missing.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

import netCDF4
import numpy as np
import xarray as xr

from acf.awci.ops.domains import Domain
from acf.awci.ops.engine import Profile
from acf.awci.ops.isa import flight_level
from acf.awci.ops.pipeline import LEVEL_LAYERS, SURFACE_LAYERS

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[4] / "data" / "awci"
LICENSE = "CC-BY-4.0"
ATTRIBUTION = "© ECMWF, CC-BY-4.0"
MODEL = "ECMWF IFS 0.25° Open Data"


def data_root() -> Path:
    return Path(os.environ.get("ACF_AWCI_DATA_DIR", DEFAULT_DATA_DIR))


def run_id(run: datetime) -> str:
    return f"{run:%Y%m%d%H}"


def _git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              check=True, cwd=Path(__file__).parent).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


class CubeWriter:
    def __init__(self, root: Path, domain: Domain, run: datetime, lats: np.ndarray, lons: np.ndarray,
                 levels_hpa: np.ndarray, steps: list[int], profile: Profile) -> None:
        self.final_dir = Path(root) / domain.name / run_id(run)
        self.tmp_dir = self.final_dir.with_name(self.final_dir.name + ".tmp")
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        self.tmp_dir.mkdir(parents=True)
        self.domain, self.run, self.steps, self.profile = domain, run, steps, profile
        self.levels_hpa = np.asarray(levels_hpa, dtype=float)
        self.nc = netCDF4.Dataset(self.tmp_dir / "cube.nc", "w", format="NETCDF4")
        self.nc.createDimension("step", len(steps))
        self.nc.createDimension("level", len(levels_hpa))
        self.nc.createDimension("lat", len(lats))
        self.nc.createDimension("lon", len(lons))
        for name, dims, values in (("step", ("step",), steps), ("level", ("level",), levels_hpa),
                                   ("lat", ("lat",), lats), ("lon", ("lon",), lons)):
            self.nc.createVariable(name, "f8", dims)[:] = np.asarray(values, dtype=float)
        comp = {"zlib": True, "complevel": 4, "fill_value": np.float32(np.nan)}
        for name in LEVEL_LAYERS:
            var = self.nc.createVariable(name, "f4", ("step", "level", "lat", "lon"),
                                         chunksizes=(1, 1, len(lats), len(lons)), **comp)
            var[:] = np.nan
        for name in SURFACE_LAYERS:
            var = self.nc.createVariable(name, "f4", ("step", "lat", "lon"), chunksizes=(1, len(lats), len(lons)), **comp)
            var[:] = np.nan
        self.nc.createVariable("elevation", "f4", ("lat", "lon"), **comp)

    def write_step(self, step_index: int, layers: dict[str, np.ndarray], elevation: np.ndarray) -> None:
        for name in LEVEL_LAYERS:
            self.nc[name][step_index] = layers[name].astype(np.float32)
        for name in SURFACE_LAYERS:
            self.nc[name][step_index] = layers[name].astype(np.float32)
        self.nc["elevation"][:] = np.asarray(elevation, dtype=np.float32)

    def finalize(self, status: str, missing_steps: list[int], extra: dict[str, Any]) -> dict[str, Any]:
        self.nc.close()
        manifest = {
            "run": run_id(self.run), "run_time": self.run.isoformat(), "domain": self.domain.name,
            "status": status, "steps": self.steps, "missing_steps": missing_steps,
            "valid_times": [(self.run + timedelta(hours=s)).isoformat() for s in self.steps],
            "levels_hpa": self.levels_hpa.tolist(),
            "flight_levels": [flight_level(p) for p in self.levels_hpa],
            "level_layers": list(LEVEL_LAYERS), "surface_layers": list(SURFACE_LAYERS),
            "profile": self.profile.name, "profile_version": self.profile.version,
            "model": MODEL, "license": LICENSE, "attribution": ATTRIBUTION, "acf_git_sha": _git_sha(), **extra,
        }
        (self.tmp_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
        shutil.rmtree(self.final_dir, ignore_errors=True)
        os.replace(self.tmp_dir, self.final_dir)
        return manifest

    def abort(self) -> None:
        if self.nc.isopen():
            self.nc.close()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)


def apply_retention(root: Path, domain: str, keep: int) -> list[str]:
    domain_dir = Path(root) / domain
    runs = sorted(p.name for p in domain_dir.iterdir() if p.is_dir() and p.name.isdigit()) if domain_dir.exists() else []
    removed = runs[: max(0, len(runs) - keep)]
    for name in removed:
        shutil.rmtree(domain_dir / name)
    return removed


@lru_cache(maxsize=16)
def _open(path: str, mtime: float) -> xr.Dataset:
    return xr.open_dataset(path, engine="netcdf4", cache=False)


class CubeStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else data_root()

    def runs(self, domain: str) -> list[dict[str, Any]]:
        domain_dir = self.root / domain
        if not domain_dir.exists():
            return []
        manifests = [json.loads((d / "manifest.json").read_text()) for d in domain_dir.iterdir()
                     if d.is_dir() and d.name.isdigit() and (d / "manifest.json").exists()]
        return sorted(manifests, key=lambda m: m["run"], reverse=True)

    def manifest(self, domain: str, run: str) -> dict[str, Any]:
        path = self.root / domain / run / "manifest.json"
        if not path.exists():
            raise FileNotFoundError(f"no run {run!r} for domain {domain!r}")
        return json.loads(path.read_text())

    def dataset(self, domain: str, run: str) -> xr.Dataset:
        path = self.root / domain / run / "cube.nc"
        if not path.exists():
            raise FileNotFoundError(f"no cube for {domain!r}/{run!r}")
        return _open(str(path), path.stat().st_mtime)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_pipeline_store.py`
Expected: PASS (7 tests)

- [ ] **Step 5: Commit**

```bash
git add src/acf/awci/ops/pipeline.py src/acf/awci/ops/store.py tests/test_awci_ops_pipeline_store.py
git commit -m "feat(awci-ops): per-step pipeline and atomic NetCDF cube store"
```

---

### Task 9: Ingestion orchestration and CLI (`ingest.py`)

**Files:**
- Create: `src/acf/awci/ops/ingest.py`
- Modify: `pyproject.toml` (`[project.scripts]`: add `acf-awci-ingest = "acf.awci.ops.ingest:main"`)
- Test: `tests/test_awci_ops_ingest.py`, helper `tests/awci_ops_support.py`

**Interfaces:**
- Consumes: `Fetcher`, `fetch_step_messages`, `find_latest_run`, `FetchError`, `MissingFieldsError`, `decode_messages`, `compute_step`, `CubeWriter`, `apply_retention`, `load_domains`, `load_profile`, `interpolate_real_terrain_elevation`.
- Produces: `ingest_run(run, domains, profile, fetcher, root, steps, keep=8) -> dict[str, dict]` (manifest per domain), `parse_steps(spec: str) -> list[int]` (`"0-72/3"`), `main(argv: list[str] | None = None) -> int` (0 complete/partial, 1 failed).

Create the shared test helper first (reused by Task 10):

```python
# tests/awci_ops_support.py
"""Shared helpers for AWCI ops tests: serve the real cropped fixture as if it were data.ecmwf.int."""

from pathlib import Path

from acf.awci.ops.domains import Domain
from acf.awci.ops.source_ecmwf import FetchError

FIXTURE = Path(__file__).parent / "data" / "awci_ops"
DOMAIN = Domain("fixture", "fixture", 35.0, 37.0, 2.0, 4.0, True)


class FixtureFetcher:
    def __init__(self, fail_steps: tuple[int, ...] = ()) -> None:
        self.fail_steps = fail_steps

    def _path(self, url: str) -> Path:
        name = url.rsplit("/", 1)[1]
        step = int(name.split("-")[1].removesuffix("h"))
        if step in self.fail_steps or not (FIXTURE / name).exists():
            raise FetchError(url)
        return FIXTURE / name

    def get_text(self, url: str) -> str:
        return self._path(url).read_text()

    def get_range(self, url: str, offset: int, length: int) -> bytes:
        return self._path(url).read_bytes()[offset : offset + length]
```

- [ ] **Step 1: Write the failing test**

```python
# tests/test_awci_ops_ingest.py
from datetime import UTC, datetime
from pathlib import Path

import pytest

from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ingest import ingest_run, main, parse_steps
from acf.awci.ops.store import CubeStore
from tests.awci_ops_support import DOMAIN, FixtureFetcher

RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)
PROFILE = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)


def test_parse_steps() -> None:
    assert parse_steps("0-72/3")[:3] == [0, 3, 6] and parse_steps("0-72/3")[-1] == 72
    assert parse_steps("0,3") == [0, 3]
    with pytest.raises(ValueError):
        parse_steps("0-10/0")


def test_ingest_complete(tmp_path: Path) -> None:
    manifests = ingest_run(RUN, [DOMAIN], PROFILE, FixtureFetcher(), tmp_path, [0, 3])
    assert manifests["fixture"]["status"] == "complete"
    assert CubeStore(tmp_path).dataset("fixture", "2026092500")["awci"].shape == (2, 12, 9, 9)


def test_ingest_partial_when_a_step_fails(tmp_path: Path) -> None:
    manifests = ingest_run(RUN, [DOMAIN], PROFILE, FixtureFetcher(fail_steps=(3,)), tmp_path, [0, 3])
    assert manifests["fixture"]["status"] == "partial" and manifests["fixture"]["missing_steps"] == [3]


def test_ingest_failed_when_every_step_fails(tmp_path: Path) -> None:
    manifests = ingest_run(RUN, [DOMAIN], PROFILE, FixtureFetcher(fail_steps=(0, 3)), tmp_path, [0, 3])
    assert manifests["fixture"]["status"] == "failed"
    assert CubeStore(tmp_path).runs("fixture") == []


def test_cli_exit_codes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("acf.awci.ops.ingest.UrllibFetcher", lambda: FixtureFetcher())
    domains = tmp_path / "domains.json"
    domains.write_text('{"domains": [{"name": "fixture", "label": "f", "south": 35, "north": 37, '
                       '"west": 2, "east": 4, "default": true}]}')
    code = main(["--run", "2026092500", "--steps", "0,3", "--domains-file", str(domains),
                 "--data-dir", str(tmp_path / "data")])
    assert code == 0
    assert (tmp_path / "data" / "fixture" / "2026092500" / "manifest.json").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_ingest.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'acf.awci.ops.ingest'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/acf/awci/ops/ingest.py
"""
acf-awci-ingest: download one ECMWF IFS run, compute AWCI layers, store cubes.

    acf-awci-ingest [--run latest|YYYYMMDDHH] [--domain NAME|all] [--steps 0-72/3]
                    [--profile PATH] [--domains-file PATH] [--data-dir PATH] [--keep N]

Exit code 0 when every domain is complete or partial, 1 when any failed.
A failed step never aborts the run; a run with no step at all is 'failed' and not stored.
"""

from __future__ import annotations

import argparse
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from loguru import logger

from acf.awci.ops.decode import decode_messages
from acf.awci.ops.domains import DEFAULT_DOMAINS_PATH, Domain, load_domains
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, Profile, load_profile
from acf.awci.ops.pipeline import compute_step
from acf.awci.ops.source_ecmwf import (
    Fetcher,
    FetchError,
    MissingFieldsError,
    UrllibFetcher,
    fetch_step_messages,
    find_latest_run,
)
from acf.awci.ops.store import CubeWriter, apply_retention, data_root
from acf.awci.terrain_elevation import interpolate_real_terrain_elevation


def parse_steps(spec: str) -> list[int]:
    if "-" in spec:
        span, _, stride = spec.partition("/")
        start, end = (int(x) for x in span.split("-"))
        step = int(stride or 3)
        if step <= 0 or start > end:
            raise ValueError(f"invalid steps spec {spec!r}")
        return list(range(start, end + 1, step))
    return [int(x) for x in spec.split(",")]


def ingest_run(
    run: datetime, domains: list[Domain], profile: Profile, fetcher: Fetcher, root: Path,
    steps: list[int], keep: int = 8,
) -> dict[str, dict[str, Any]]:
    started = time.monotonic()
    writers: dict[str, CubeWriter] = {}
    elevations: dict[str, Any] = {}
    missing: list[int] = []
    for index, step in enumerate(steps):
        try:
            per_domain = decode_messages(fetch_step_messages(fetcher, run, step), domains)
        except (FetchError, MissingFieldsError, ValueError) as exc:
            logger.warning("AWCI ingest {} step {}h skipped: {}", run, step, exc)
            missing.append(step)
            continue
        for domain in domains:
            fields = per_domain[domain.name]
            if domain.name not in writers:
                elevations[domain.name] = interpolate_real_terrain_elevation(fields.lats, fields.lons)
                writers[domain.name] = CubeWriter(root, domain, run, fields.lats, fields.lons, fields.levels_hpa,
                                                  steps, profile)
            writers[domain.name].write_step(index, compute_step(fields, elevations[domain.name], profile),
                                            elevations[domain.name])
        logger.info("AWCI ingest {} step {}h done", run, step)
    manifests: dict[str, dict[str, Any]] = {}
    status = "failed" if len(missing) == len(steps) else ("partial" if missing else "complete")
    for domain in domains:
        writer = writers.get(domain.name)
        if writer is None:
            manifests[domain.name] = {"status": "failed", "domain": domain.name, "missing_steps": missing}
            continue
        manifests[domain.name] = writer.finalize(status, missing, {"duration_s": round(time.monotonic() - started, 1)})
        apply_retention(root, domain.name, keep)
    return manifests


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="acf-awci-ingest", description=__doc__.splitlines()[1])
    parser.add_argument("--run", default="latest")
    parser.add_argument("--domain", default="all")
    parser.add_argument("--steps", default="0-72/3")
    parser.add_argument("--profile", default=str(DEFAULT_OPERATIONAL_PROFILE_PATH))
    parser.add_argument("--domains-file", default=str(DEFAULT_DOMAINS_PATH))
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--keep", type=int, default=8)
    args = parser.parse_args(argv)

    steps = parse_steps(args.steps)
    all_domains = load_domains(args.domains_file)
    domains = list(all_domains.values()) if args.domain == "all" else [all_domains[args.domain]]
    fetcher = UrllibFetcher()
    run = (find_latest_run(fetcher, datetime.now(UTC), steps[-1]) if args.run == "latest"
           else datetime.strptime(args.run, "%Y%m%d%H").replace(tzinfo=UTC))
    root = Path(args.data_dir) if args.data_dir else data_root()
    manifests = ingest_run(run, domains, load_profile(args.profile), fetcher, root, steps, args.keep)
    for name, manifest in manifests.items():
        logger.info("AWCI ingest {} {}: {}", run, name, manifest["status"])
    return 1 if any(m["status"] == "failed" for m in manifests.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Also fix `CubeWriter` for the failed case: nothing to add — a writer is only created once a step succeeds, so a fully failed run leaves no directory (`test_ingest_failed_when_every_step_fails`).

Add to `pyproject.toml` under `[project.scripts]`:

```toml
acf-awci-ingest = "acf.awci.ops.ingest:main"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_ingest.py`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add src/acf/awci/ops/ingest.py pyproject.toml tests/test_awci_ops_ingest.py tests/awci_ops_support.py
git commit -m "feat(awci-ops): acf-awci-ingest CLI with partial/failed run handling and retention"
```

---

### Task 10: Read-only API (`awci_router.py`, `awci_app.py`)

**Files:**
- Create: `src/acf/web/routers/awci_router.py`, `src/acf/web/awci_app.py`
- Modify: `src/acf/web/hpc_dashboard_server.py` (include the router), `pyproject.toml` (`acf-awci-web = "acf.web.awci_app:run"`)
- Test: `tests/test_web_awci_api.py`

**Interfaces:**
- Consumes: `CubeStore`, `load_domains`, `load_profile`, `DEFAULT_OPERATIONAL_PROFILE_PATH`, `LAYERS`, `LEVEL_LAYERS`, `SURFACE_LAYERS`, `ATTRIBUTION`, `LICENSE`, `MODEL`.
- Produces: `router` (prefix `/awci`); `create_awci_app(data_dir: Path | None = None, domains_file: Path | None = None, cors_origins: list[str] | None = None) -> FastAPI` (mounts under `/api/v1`); `run(host="127.0.0.1", port=8091)`.
  App state: `app.state.awci_store: CubeStore`, `app.state.awci_domains: dict[str, Domain]`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_web_awci_api.py
import struct
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ingest import ingest_run
from acf.web.awci_app import create_awci_app
from tests.awci_ops_support import DOMAIN, FixtureFetcher

RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)


@pytest.fixture(scope="module")
def client(tmp_path_factory) -> TestClient:
    root = tmp_path_factory.mktemp("awci")
    ingest_run(RUN, [DOMAIN], load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH), FixtureFetcher(fail_steps=(3,)),
               root, [0, 3])
    domains = root / "domains.json"
    domains.write_text('{"domains": [{"name": "fixture", "label": "f", "south": 35, "north": 37, '
                       '"west": 2, "east": 4, "default": true}]}')
    return TestClient(create_awci_app(data_dir=root, domains_file=domains))


BASE = "/api/v1/awci"
Q = "domain=fixture&run=2026092500"


def test_domains_and_runs(client: TestClient) -> None:
    assert client.get(f"{BASE}/domains").json()[0]["name"] == "fixture"
    runs = client.get(f"{BASE}/runs?domain=fixture").json()
    assert runs[0]["run"] == "2026092500" and runs[0]["status"] == "partial"


def test_meta_has_flight_levels_and_provenance(client: TestClient) -> None:
    meta = client.get(f"{BASE}/meta?{Q}").json()
    assert meta["flight_levels"][meta["levels_hpa"].index(300.0)] == 301
    assert meta["provenance"]["license"] == "CC-BY-4.0" and meta["source_tier"] == "nwp_forecast"


def test_field_json_uses_null_for_missing(client: TestClient) -> None:
    body = client.get(f"{BASE}/field?{Q}&layer=awci&step=0&level=300").json()
    assert len(body["values"]) == 9 and len(body["values"][0]) == 9
    assert body["provenance"]["step"] == 0 and body["unit"] == "0-100"
    flat = [v for row in body["values"] for v in row]
    assert all(v is None or 0 <= v <= 100 for v in flat)


def test_field_binary_f32(client: TestClient) -> None:
    r = client.get(f"{BASE}/field?{Q}&layer=mucape&step=0&format=f32")
    assert r.headers["content-type"] == "application/octet-stream"
    assert r.headers["x-awci-shape"] == "9,9"
    values = struct.unpack("<81f", r.content)
    assert all(np.isnan(v) or v >= 0 for v in values)


def test_point_breakdown(client: TestClient) -> None:
    body = client.get(f"{BASE}/point?{Q}&step=0&level=300&lat=36.0&lon=3.0").json()
    assert body["lat"] == 36.0 and body["lon"] == 3.0
    assert set(body["modules"]) >= {"dynamic", "thermodynamic", "convective", "microphysical", "topographic"}
    assert body["excluded_modules"] == ["temporal", "confidence"]
    assert body["awci_level"] in {"Very Low", "Low", "Moderate", "High", "Very High", "Extreme", None}


def test_profile_and_timeseries(client: TestClient) -> None:
    prof = client.get(f"{BASE}/profile?{Q}&step=0&lat=36&lon=3").json()
    assert len(prof["levels"]) == 12
    ts = client.get(f"{BASE}/timeseries?{Q}&level=300&lat=36&lon=3").json()
    assert [p["step"] for p in ts["points"]] == [0, 3] and ts["points"][1]["awci"] is None


def test_registry(client: TestClient) -> None:
    body = client.get(f"{BASE}/registry").json()
    assert body["layers"]["cat_ti2"]["status"] == "HYPOTHESIS"
    assert body["classes"][0] == {"upper_bound": 20.0, "label": "Very Low"}
    assert body["profile"]["name"] == "operational-v1"


# Review Focus 1 and 2
def test_point_outside_domain_is_400(client: TestClient) -> None:
    assert client.get(f"{BASE}/point?{Q}&step=0&level=300&lat=50&lon=3").status_code == 400


def test_missing_step_of_partial_run_is_404(client: TestClient) -> None:
    r = client.get(f"{BASE}/field?{Q}&layer=awci&step=3&level=300")
    assert r.status_code == 404 and "3" in r.json()["detail"]


@pytest.mark.parametrize("query", ["layer=nope&step=0", "layer=awci&step=5&level=300", "layer=awci&step=0&level=333",
                                   "layer=awci&step=0"])
def test_invalid_parameters_are_400(client: TestClient, query: str) -> None:
    assert client.get(f"{BASE}/field?{Q}&{query}").status_code == 400


def test_unknown_run_is_404(client: TestClient) -> None:
    assert client.get(f"{BASE}/meta?domain=fixture&run=2026010100").status_code == 404


def test_router_mounted_in_main_app() -> None:
    from acf.web.hpc_dashboard_server import create_app

    paths = {route.path for route in create_app(hpc=object(), fno_checkpoint_path=None,
                                                event_db_path=":memory:", dataset_db_path=":memory:").routes}
    assert "/api/v1/awci/runs" in paths
```

- [ ] **Step 2: Run test to verify it fails**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_web_awci_api.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'acf.web.awci_app'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/acf/web/routers/awci_router.py
"""
/api/v1/awci - read-only AWCI Web API over the stored cubes (acf.awci.ops.store).

Handlers are plain `def` (FastAPI runs them in its thread pool) and only read
NetCDF slices - no heavy computation per request. Missing values are JSON null.
Every response carries provenance and source_tier "nwp_forecast".
"""

from __future__ import annotations

import math
from typing import Any, Literal

import numpy as np
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import Response
from pydantic import BaseModel

from acf.awci.ops.domains import Domain
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.pipeline import LEVEL_LAYERS, SURFACE_LAYERS
from acf.awci.ops.registry import LAYERS
from acf.awci.ops.store import ATTRIBUTION, LICENSE, MODEL, CubeStore

router = APIRouter(prefix="/awci", tags=["awci"])
_MODULES = ("dynamic", "thermodynamic", "convective", "microphysical", "topographic")
_EXCLUDED = ["temporal", "confidence"]


class Provenance(BaseModel):
    model: str
    run: str
    step: int | None
    valid_time: str | None
    domain: str
    profile: str
    profile_version: str
    license: str
    attribution: str


def _num(value: Any) -> float | None:
    value = float(value)
    return None if math.isnan(value) else value


def _store(request: Request) -> CubeStore:
    return request.app.state.awci_store


def _domain(request: Request, name: str) -> Domain:
    domains: dict[str, Domain] = request.app.state.awci_domains
    if name not in domains:
        raise HTTPException(404, f"unknown domain {name!r}")
    return domains[name]


def _manifest(request: Request, domain: str, run: str) -> dict[str, Any]:
    _domain(request, domain)
    try:
        return _store(request).manifest(domain, run)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc


def _step_index(manifest: dict[str, Any], step: int) -> int:
    if step not in manifest["steps"]:
        raise HTTPException(400, f"step {step} not in this run's steps {manifest['steps']}")
    if step in manifest["missing_steps"]:
        raise HTTPException(404, f"step {step} is missing from this {manifest['status']} run")
    return manifest["steps"].index(step)


def _level_index(manifest: dict[str, Any], level: float) -> int:
    if level not in manifest["levels_hpa"]:
        raise HTTPException(400, f"level {level} hPa not in {manifest['levels_hpa']}")
    return manifest["levels_hpa"].index(level)


def _provenance(manifest: dict[str, Any], step: int | None) -> dict[str, Any]:
    valid = manifest["valid_times"][manifest["steps"].index(step)] if step is not None else None
    return Provenance(model=MODEL, run=manifest["run"], step=step, valid_time=valid, domain=manifest["domain"],
                      profile=manifest["profile"], profile_version=manifest["profile_version"],
                      license=LICENSE, attribution=ATTRIBUTION).model_dump()


def _nearest(ds: Any, domain: Domain, lat: float, lon: float) -> tuple[int, int]:
    if not domain.contains(lat, lon):
        raise HTTPException(400, f"point ({lat}, {lon}) is outside domain {domain.name!r}")
    return int(np.abs(ds["lat"].values - lat).argmin()), int(np.abs(ds["lon"].values - lon).argmin())


def _level_label(profile_thresholds: tuple[tuple[float, str], ...], code: float) -> str | None:
    return None if math.isnan(code) else profile_thresholds[int(code)][1]


@router.get("/domains")
def domains(request: Request) -> list[dict[str, Any]]:
    return [{"name": d.name, "label": d.label, "south": d.south, "north": d.north, "west": d.west, "east": d.east,
             "default": d.default, "resolution_deg": 0.25} for d in request.app.state.awci_domains.values()]


@router.get("/runs")
def runs(request: Request, domain: str) -> list[dict[str, Any]]:
    _domain(request, domain)
    return [{"run": m["run"], "run_time": m["run_time"], "status": m["status"], "steps": m["steps"],
             "missing_steps": m["missing_steps"]} for m in _store(request).runs(domain)]


@router.get("/meta")
def meta(request: Request, domain: str, run: str) -> dict[str, Any]:
    m = _manifest(request, domain, run)
    return {"levels_hpa": m["levels_hpa"], "flight_levels": m["flight_levels"], "steps": m["steps"],
            "valid_times": m["valid_times"], "missing_steps": m["missing_steps"], "status": m["status"],
            "level_layers": m["level_layers"], "surface_layers": m["surface_layers"],
            "provenance": _provenance(m, None), "source_tier": "nwp_forecast"}


@router.get("/field", response_model=None)
def field(
    request: Request, domain: str, run: str, layer: str, step: int = Query(ge=0, le=384),
    level: float | None = None, format: Literal["json", "f32"] = "json",
) -> dict[str, Any] | Response:
    m = _manifest(request, domain, run)
    if layer not in LEVEL_LAYERS and layer not in SURFACE_LAYERS:
        raise HTTPException(400, f"unknown layer {layer!r}")
    si = _step_index(m, step)
    ds = _store(request).dataset(domain, run)
    if layer in LEVEL_LAYERS:
        if level is None:
            raise HTTPException(400, f"layer {layer!r} is per-level: 'level' (hPa) is required")
        values = ds[layer].isel(step=si, level=_level_index(m, level)).values
    else:
        values = ds[layer].isel(step=si).values
    lats, lons = ds["lat"].values, ds["lon"].values
    unit = LAYERS[layer].unit if layer in LAYERS else ""
    if format == "f32":
        return Response(
            content=np.ascontiguousarray(values, dtype="<f4").tobytes(), media_type="application/octet-stream",
            headers={"X-AWCI-Shape": f"{values.shape[0]},{values.shape[1]}",
                     "X-AWCI-Lats": f"{lats[0]},{lats[-1]}", "X-AWCI-Lons": f"{lons[0]},{lons[-1]}",
                     "X-AWCI-Nodata": "NaN", "X-AWCI-Unit": unit, "X-AWCI-Attribution": "ECMWF CC-BY-4.0"},
        )
    return {"layer": layer, "unit": unit, "level_hpa": level, "lats": lats.tolist(), "lons": lons.tolist(),
            "values": [[_num(v) for v in row] for row in values],
            "provenance": _provenance(m, step), "source_tier": "nwp_forecast"}


def _point_payload(ds: Any, si: int, li: int, i: int, j: int, thresholds: Any) -> dict[str, Any]:
    level_values = {name: _num(ds[name].values[si, li, i, j]) for name in LEVEL_LAYERS
                    if not name.startswith("module_") and name not in ("awci", "awci_level")}
    return {
        "awci": _num(ds["awci"].values[si, li, i, j]),
        "awci_level": _level_label(thresholds, float(ds["awci_level"].values[si, li, i, j])),
        "modules": {m: _num(ds[f"module_{m}"].values[si, li, i, j]) for m in _MODULES},
        "excluded_modules": list(_EXCLUDED),
        "level_layers": level_values,
    }


@router.get("/point")
def point(request: Request, domain: str, run: str, step: int, level: float, lat: float, lon: float) -> dict[str, Any]:
    m = _manifest(request, domain, run)
    si, li = _step_index(m, step), _level_index(m, level)
    ds = _store(request).dataset(domain, run)
    i, j = _nearest(ds, _domain(request, domain), lat, lon)
    thresholds = request.app.state.awci_profile.level_thresholds
    return {"lat": float(ds["lat"].values[i]), "lon": float(ds["lon"].values[j]), "level_hpa": level,
            "flight_level": m["flight_levels"][li], **_point_payload(ds, si, li, i, j, thresholds),
            "surface_layers": {name: _num(ds[name].values[si, i, j]) for name in SURFACE_LAYERS},
            "elevation_m": _num(ds["elevation"].values[i, j]),
            "provenance": _provenance(m, step), "source_tier": "nwp_forecast"}


@router.get("/profile")
def profile(request: Request, domain: str, run: str, step: int, lat: float, lon: float) -> dict[str, Any]:
    m = _manifest(request, domain, run)
    si = _step_index(m, step)
    ds = _store(request).dataset(domain, run)
    i, j = _nearest(ds, _domain(request, domain), lat, lon)
    thresholds = request.app.state.awci_profile.level_thresholds
    levels = [{"level_hpa": p, "flight_level": fl, **_point_payload(ds, si, li, i, j, thresholds)}
              for li, (p, fl) in enumerate(zip(m["levels_hpa"], m["flight_levels"]))]
    return {"lat": float(ds["lat"].values[i]), "lon": float(ds["lon"].values[j]), "levels": levels,
            "provenance": _provenance(m, step), "source_tier": "nwp_forecast"}


@router.get("/timeseries")
def timeseries(request: Request, domain: str, run: str, level: float, lat: float, lon: float) -> dict[str, Any]:
    m = _manifest(request, domain, run)
    li = _level_index(m, level)
    ds = _store(request).dataset(domain, run)
    i, j = _nearest(ds, _domain(request, domain), lat, lon)
    points = [{"step": s, "valid_time": vt, "awci": _num(ds["awci"].values[si, li, i, j])}
              for si, (s, vt) in enumerate(zip(m["steps"], m["valid_times"]))]
    return {"lat": float(ds["lat"].values[i]), "lon": float(ds["lon"].values[j]), "level_hpa": level,
            "points": points, "provenance": _provenance(m, None), "source_tier": "nwp_forecast"}


@router.get("/registry")
def registry(request: Request) -> dict[str, Any]:
    prof = request.app.state.awci_profile
    classes = [{"upper_bound": None if math.isinf(b) else b, "label": label} for b, label in prof.level_thresholds]
    return {"layers": {name: spec.to_dict() for name, spec in LAYERS.items()}, "classes": classes,
            "profile": {"name": prof.name, "version": prof.version, "weights": prof.weights,
                        "interaction_weights": prof.interaction_weights, "min_present_weight": prof.min_present_weight,
                        "excluded_modules": list(_EXCLUDED)},
            "attribution": ATTRIBUTION, "license": LICENSE}


def default_profile() -> Any:
    return load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
```

```python
# src/acf/web/awci_app.py
"""
Light FastAPI app serving only /api/v1/awci (no HPC/torch imports).

    acf-awci-web            # uvicorn on 127.0.0.1:8091
Data directory: ACF_AWCI_DATA_DIR (default <repo>/data/awci).
CORS: ACF_AWCI_CORS_ORIGINS (comma-separated), default none (same origin).
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from acf.awci.ops.domains import DEFAULT_DOMAINS_PATH, load_domains
from acf.awci.ops.store import CubeStore
from acf.web.routers.awci_router import default_profile, router


def attach_awci_state(app: FastAPI, data_dir: Path | None = None, domains_file: Path | None = None) -> None:
    app.state.awci_store = CubeStore(data_dir)
    app.state.awci_domains = load_domains(domains_file or DEFAULT_DOMAINS_PATH)
    app.state.awci_profile = default_profile()


def create_awci_app(
    data_dir: Path | None = None, domains_file: Path | None = None, cors_origins: list[str] | None = None
) -> FastAPI:
    app = FastAPI(title="AWCI Web API", version="1.0.0")
    attach_awci_state(app, data_dir, domains_file)
    origins = cors_origins if cors_origins is not None else [
        o for o in os.environ.get("ACF_AWCI_CORS_ORIGINS", "").split(",") if o
    ]
    if origins:
        app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET"], allow_headers=["*"],
                           expose_headers=["X-AWCI-Shape", "X-AWCI-Lats", "X-AWCI-Lons", "X-AWCI-Nodata",
                                           "X-AWCI-Unit", "X-AWCI-Attribution"])
    app.include_router(router, prefix="/api/v1")
    return app


def run(host: str = "127.0.0.1", port: int = 8091) -> None:
    import uvicorn

    uvicorn.run(create_awci_app(), host=host, port=port)
```

Modify `src/acf/web/hpc_dashboard_server.py` inside `create_app()` right after the `workstation_router` include:

```python
    from acf.web.awci_app import attach_awci_state
    from acf.web.routers.awci_router import router as awci_router

    attach_awci_state(app)
    app.include_router(awci_router, prefix="/api/v1")
```

Add to `pyproject.toml` `[project.scripts]`:

```toml
acf-awci-web = "acf.web.awci_app:run"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_web_awci_api.py tests/test_web_api_v1.py tests/test_web_hpc_dashboard.py`
Expected: PASS (all; existing web tests unchanged)

- [ ] **Step 5: Commit**

```bash
git add src/acf/web/routers/awci_router.py src/acf/web/awci_app.py src/acf/web/hpc_dashboard_server.py pyproject.toml tests/test_web_awci_api.py
git commit -m "feat(awci-web): read-only /api/v1/awci API with provenance and null-for-missing"
```

---

### Task 11: Real network check, operator documentation, full verification

**Files:**
- Create: `tests/test_awci_ops_network.py`, `docs/awci/AWCI_WEB_SP1.md`
- Modify: `docs/superpowers/specs/2026-09-25-awci-web-sp1-data-science-design.md` (success criterion 6 wording), `CHANGELOG.md`

- [ ] **Step 1: Write the opt-in real network test**

```python
# tests/test_awci_ops_network.py
"""Real ECMWF Open Data check - opt-in: ACF_AWCI_NETWORK_TESTS=1."""

import os
from datetime import UTC, datetime

import numpy as np
import pytest

from acf.awci.ops.decode import decode_messages
from acf.awci.ops.domains import Domain
from acf.awci.ops.source_ecmwf import UrllibFetcher, fetch_step_messages, find_latest_run

pytestmark = pytest.mark.skipif(os.environ.get("ACF_AWCI_NETWORK_TESTS") != "1", reason="network test (opt-in)")


@pytest.mark.timeout(600)
def test_latest_real_step_decodes() -> None:
    fetcher = UrllibFetcher()
    run = find_latest_run(fetcher, datetime.now(UTC), last_step=0)
    fields = decode_messages(fetch_step_messages(fetcher, run, 0), [Domain("na", "na", 15, 45, -20, 40, True)])["na"]
    assert fields.pl["t"].shape == (12, 121, 241)
    assert 180.0 < np.nanmin(fields.pl["t"]) and np.nanmax(fields.pl["t"]) < 330.0
```

Run: `ACF_AWCI_NETWORK_TESTS=1 QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_network.py`
Expected: PASS (downloads ~75 MB). Without the variable: 1 skipped.

- [ ] **Step 2: Measure a real full ingestion (criterion 1)**

Run: `.venv/bin/acf-awci-ingest --run latest --domain north_africa --data-dir /tmp/awci-real` (or `.venv/bin/python -m acf.awci.ops.ingest …`)
Expected: exit 0, manifest `status: complete`, `duration_s` < 1800. Record the measured duration and cube size in `docs/awci/AWCI_WEB_SP1.md`.

Then time the API (criterion 5):

```bash
ACF_AWCI_DATA_DIR=/tmp/awci-real .venv/bin/python -c "
import time; from fastapi.testclient import TestClient; from acf.web.awci_app import create_awci_app
c = TestClient(create_awci_app()); run = c.get('/api/v1/awci/runs?domain=north_africa').json()[0]['run']
t = []
for _ in range(50):
    s = time.perf_counter(); c.get(f'/api/v1/awci/field?domain=north_africa&run={run}&layer=awci&step=24&level=300&format=f32'); t.append(time.perf_counter() - s)
t.sort(); print('p95 ms', round(t[int(0.95 * len(t))] * 1000, 1))"
```
Expected: `p95 ms` < 300. Record it in the doc.

- [ ] **Step 3: Write the operator documentation**

`docs/awci/AWCI_WEB_SP1.md` must contain, with the measured numbers from Step 2:

```markdown
# AWCI Web — SP1 (données & science) : guide d'exploitation

## Installation
pip install -e ".[formats,web,science]"   # eccodes, netCDF4/xarray, fastapi/uvicorn

## Ingestion
acf-awci-ingest --run latest --domain all          # 0-72 h / 3 h, profil operational-v1
Variables : ACF_AWCI_DATA_DIR (défaut <repo>/data/awci). Rétention : --keep 8.
Mesures (run <run>, domaine north_africa) : durée <X> min, cube <Y> Mo.

### systemd
# /etc/systemd/system/acf-awci-ingest.service
[Service]
Type=oneshot
Environment=ACF_AWCI_DATA_DIR=/srv/awci
ExecStart=/opt/acf/.venv/bin/acf-awci-ingest --run latest --domain all
# /etc/systemd/system/acf-awci-ingest.timer
[Timer]
OnCalendar=*-*-* 02,08,14,20:15:00 UTC
Persistent=true
[Install]
WantedBy=timers.target

### cron (alternative)
15 2,8,14,20 * * * ACF_AWCI_DATA_DIR=/srv/awci /opt/acf/.venv/bin/acf-awci-ingest --run latest --domain all

## API
acf-awci-web   # http://127.0.0.1:8091/api/v1/awci/…  (ACF_AWCI_CORS_ORIGINS pour le front)
Routes : /domains, /runs, /meta, /field (json|f32), /point, /profile, /timeseries, /registry.
Latence mesurée /field f32 : p95 <Z> ms.

## Garanties
- Données : ECMWF IFS 0,25° Open Data, © ECMWF, CC-BY-4.0 (attribution obligatoire côté front).
- Valeur manquante = null (JSON) / NaN (f32), jamais 0 ; modules exclus listés.
- Statuts scientifiques exposés par /registry (HYPOTHESIS pour givrage, CAT, poussière, AWCI composite).
```

- [ ] **Step 4: Align the spec's parity criterion with the implemented check**

In the spec, replace success criterion 6 with:
`6. Le moteur vectorisé reproduit les scores de module d'AWCICalculator à 1e-12 près et son awci à l'arrondi 0,1 près (|Δ| ≤ 0,05) sur le profil legacy.`
And add a CHANGELOG entry under the unreleased section: `AWCI Web SP1: ECMWF IFS ingestion (acf-awci-ingest), vectorized hazards + operational-v1 AWCI, /api/v1/awci (acf-awci-web).`

- [ ] **Step 5: Full verification**

Run:
```bash
.venv/bin/ruff check src/acf/awci/ops src/acf/web/routers/awci_router.py src/acf/web/awci_app.py tools/awci tests/test_awci_ops_*.py tests/test_web_awci_api.py
.venv/bin/mypy src/acf/awci/ops src/acf/web/routers/awci_router.py src/acf/web/awci_app.py
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/test_awci_ops_*.py tests/test_web_*.py
```
Expected: ruff clean, mypy clean, all tests pass (network test skipped).

- [ ] **Step 6: Commit**

```bash
git add tests/test_awci_ops_network.py docs/awci/AWCI_WEB_SP1.md docs/superpowers/specs/2026-09-25-awci-web-sp1-data-science-design.md CHANGELOG.md
git commit -m "docs(awci-web): SP1 operator guide, measured performance, opt-in network test"
```
