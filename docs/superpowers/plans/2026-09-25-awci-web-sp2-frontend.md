# AWCI Web SP2 — Front 2D : plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** un tableau de bord web opérationnel (`web/awci`) qui reprend la structure de la maquette et n'affiche que des grandeurs calculées (cube SP1/SP1C) ou observées (EUMETView relayé), avec source, heure et statut scientifique ; plus les petites routes serveur qu'il consomme.

**Architecture:** Vite + React 19 + TypeScript strict dans `web/awci/`, servi en statique par `acf-awci-web` (même origine que l'API). MapLibre GL pour la carte (fond Natural Earth embarqué, champ raster rééchantillonné en Mercator, lignes de courant, tuiles WMS relayées), TanStack Query pour les données, l'URL comme source de vérité de la vue. Côté serveur : `/summary`, `/summary/series`, `/clouds/series`, `/wms`, `/wms/times`, point de rosée dans `/profile`, `ingested_at` dans le manifest, service du build statique.

**Tech Stack:** Python 3.12 / FastAPI / NumPy (serveur) ; Node 22, Vite, React 19, TypeScript, MapLibre GL 6, @tanstack/react-query 5, lucide-react, @fontsource (Fira Sans / Fira Code), Vitest + Testing Library, Playwright + @axe-core/playwright.

**Spec:** `docs/superpowers/specs/2026-09-25-awci-web-sp2-frontend-design.md` (+ SP1C pour les couches nuageuses).

## Global Constraints

- Aucune valeur fictive : un indicateur sans donnée affiche « — » ou un état explicite ; une cellule `NaN` est hachurée, jamais colorée comme un risque faible.
- Toute observation porte son heure d'observation (« Observé HH:MM UTC, il y a N min ») et « © EUMETSAT » ; toute prévision porte run, échéance, validité et « © ECMWF, CC-BY-4.0 ».
- Palette AWCI (sombre, validée) : `#854494 #b94c90 #e45d84 #ff7f6c #ffa85d #ffd368` sur surface `#0b1220`. Séquentielle : bleu du skill dataviz (`#0d366b … #cde2fb`, sombre → clair sur fond sombre). Catégorielle carte : 3 premiers créneaux sombres seulement (`#3987e5 #d95926 #199e70`, seuls valides « toutes paires »). Statuts : `#0ca30c #fab219 #ec835a #d03b3b`, toujours icône + texte.
- Polices, icônes et fond de carte embarqués (réseau interne) ; aucune requête navigateur hors de la même origine.
- Libellés en français, regroupés dans `src/i18n/fr.ts`.
- Accessibilité : contraste texte ≥ 4,5:1, focus visible, ARIA sur les boutons-icônes, `prefers-reduced-motion` respecté, aucune information par la couleur seule.
- Serveur : aucun import d'eccodes dans `acf/web/*` et `acf/awci/ops/summary.py` ; entrées externes validées (liste blanche WMS, bornes, motifs).
- Tests : `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q -p no:warnings tests/test_awci_ops_*.py tests/test_web_awci_*.py` ; front `npm test`, `npm run lint`, `npm run build`, `npm run e2e` dans `web/awci`.
- Commits : trailers `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` et `Claude-Session: https://claude.ai/code/session_017rtRvi8FETpCKyneMvVvBM`.

## Review Focus

1. **Run partiel** (échéances manquantes) : le curseur et les flèches sautent les échéances manquantes, jamais de 404 visible ni de champ de l'échéance voisine présenté à la place. → Task 7 (test Vitest `nextStep`) + Task 13 (e2e run partiel).
2. **Clic sur une cellule sous le relief ou hors domaine** : inspecteur « sous le sol » / message « hors domaine », jamais de valeur 0. → Task 9 + Task 13.
3. **Run ingéré avant SP1C** : couches nuageuses absentes du sélecteur, panneau Nuages « non disponible pour ce run », aucune erreur. → Task 5 (`availableLayers`) + Task 10.
4. **EUMETView indisponible ou lent** : overlay marqué indisponible, la prévision reste utilisable. → Task 2 (502) + Task 11 (état d'erreur) + Task 13.
5. **Petit écran (< 1024 px)** : mise en page carte + inspecteur sans défilement horizontal ; 2560 px sans étirement illisible. → Task 7 (CSS) + Task 13 (captures 900 / 1440 / 2560).

---

### Task 1: Routes de synthèse et compléments d'API (`/summary`, `/summary/series`, `/clouds/series`, point de rosée, `ingested_at`, bornes d'étage)

**Files:**
- Create: `src/acf/awci/ops/summary.py`, `tests/test_awci_ops_summary.py`, `tests/test_web_awci_summary_api.py`
- Modify: `src/acf/web/awci_router.py`, `src/acf/awci/ops/store.py` (`ingested_at`), `src/acf/awci/ops/clouds.py` (`base_fl` dans `column_layers`)

**Interfaces:**
- Produces: `summary.area_weights(lats, nx)`, `summary.area_pct(condition, valid, weights) -> float | None`, `summary.weighted_percentile(values, weights, q) -> float | None`, `summary.badge(value, bounds) -> str | None`, `summary.summarize(layers, lats, profile) -> dict`, `summary.SUMMARY_THRESHOLDS`.
- Routes : `GET /awci/summary?domain&run&step&level` ; `GET /awci/summary/series?domain&run&level` ; `GET /awci/clouds/series?domain&run&lat&lon` ; `/profile` : `dewpoint_k` par niveau ; `/runs` : `ingested_at` ; `/clouds` : `etage_bounds_fl` et `layers[].base_fl`.

- [ ] **Step 1: tests unitaires (échouent)** — `tests/test_awci_ops_summary.py`

```python
"""Area-weighted domain indicators for the KPI row."""

import numpy as np

from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.summary import area_pct, area_weights, badge, summarize, weighted_percentile

PROFILE = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)


def test_area_weights_follow_cos_latitude() -> None:
    w = area_weights(np.array([0.0, 60.0]), 3)
    assert w.shape == (2, 3) and np.allclose(w[1] / w[0], 0.5)


def test_area_pct_is_weighted_and_ignores_nan() -> None:
    w = area_weights(np.array([0.0, 60.0]), 1)
    cond = np.array([[False], [True]])
    assert np.isclose(area_pct(cond, np.ones((2, 1), bool), w), 100 * 0.5 / 1.5)
    assert area_pct(cond, np.zeros((2, 1), bool), w) is None


def test_weighted_percentile_inverted_cdf() -> None:
    v = np.array([1.0, 2.0, 3.0, 4.0, np.nan])
    w = np.ones(5)
    assert weighted_percentile(v, w, 50) == 2.0 and weighted_percentile(v, w, 95) == 4.0
    assert weighted_percentile(np.array([np.nan]), np.ones(1), 95) is None


def test_badges() -> None:
    assert badge(None, (5, 15, 30)) is None
    assert [badge(x, (5, 15, 30)) for x in (1, 5, 20, 31)] == ["ok", "attention", "serious", "critical"]
    assert [badge(x, (5e-3, 8e-3)) for x in (1e-3, 6e-3, 9e-3)] == ["ok", "attention", "serious"]


def test_summarize_on_synthetic_fields() -> None:
    lats = np.array([30.0, 30.25])
    ones = np.ones((2, 2))
    layers = {
        "awci": np.array([[10.0, 70.0], [np.nan, 40.0]]), "cat_category": np.array([[0.0, 2.0], [np.nan, 3.0]]),
        "icing_potential": np.array([[0.0, 1.0], [np.nan, 0.0]]), "vertical_shear": ones * 4e-3,
        "mucape": np.array([[0.0, 1500.0], [200.0, 1000.0]]), "precip_class": np.array([[0.0, 3.0], [1.0, 0.0]]),
        "ceiling_m": np.array([[np.nan, 200.0], [500.0, np.nan]]), "convective_class": np.array([[0, 4], [0, 2.0]]),
        "cloud_cover_bias": np.array([[0.1, -0.1], [0.2, 0.0]]),
    }
    s = summarize(layers, lats, PROFILE)
    assert s["valid_cells_pct"] is not None and 74 < s["valid_cells_pct"] < 76
    assert 66 < s["turbulence_area_pct"] < 67 and s["mucape_max"] == 1500.0
    assert 49 < s["convection_area_pct"] < 51 and 24 < s["cb_area_pct"] < 26
    assert s["awci_class"] == "High" and s["badges"]["turbulence_area_pct"] == "critical"


def test_summarize_without_sp1c_layers() -> None:
    lats = np.array([30.0, 30.25])
    base = {k: np.zeros((2, 2)) for k in ("awci", "cat_category", "icing_potential", "vertical_shear", "mucape",
                                          "precip_class")}
    s = summarize(base | {"ceiling_m": None, "convective_class": None, "cloud_cover_bias": None}, lats, PROFILE)
    assert s["low_ceiling_area_pct"] is None and s["cb_area_pct"] is None and s["cloud_cover_bias_mean"] is None
```

- [ ] **Step 2:** `pytest tests/test_awci_ops_summary.py -q` → FAIL (ImportError).
- [ ] **Step 3: implémentation** — `src/acf/awci/ops/summary.py`

```python
"""
Domain indicators of one (run, step, level) for the AWCI Web KPI row (SP2 spec §5.1).

Area percentages and percentiles are weighted by grid-cell area: on the regular lat/lon grid of a
spherical Earth a cell's area is proportional to cos(latitude), so a 0.25° cell at 45°N counts for
0.71 of one at the equator. Cells without data (NaN: below ground, missing input) are excluded from
numerator and denominator. Badge thresholds are ACF choices (status HYPOTHESIS), served by /registry.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from acf.awci.ops.engine import Profile, level_codes

AREA_BADGES_PCT = (5.0, 15.0, 30.0)
SHEAR_BADGES_PER_S = (5e-3, 8e-3)
CONVECTIVE_MUCAPE_J_KG = 1000.0
IFR_CEILING_M = 304.8  # 1000 ft (1 ft = 0.3048 m exactly)
SUMMARY_THRESHOLDS: dict[str, Any] = {
    "area_badges_pct": AREA_BADGES_PCT, "shear_badges_per_s": SHEAR_BADGES_PER_S,
    "convective_mucape_j_kg": CONVECTIVE_MUCAPE_J_KG, "low_ceiling_m": IFR_CEILING_M,
    "status": "HYPOTHESIS", "weighting": "cell area, cos(latitude)",
}
_NAMES = ("ok", "attention", "serious", "critical")


def area_weights(lats: np.ndarray, nx: int) -> np.ndarray:
    return np.cos(np.radians(np.asarray(lats, dtype=float)))[:, None] * np.ones((1, nx))


def area_pct(condition: np.ndarray, valid: np.ndarray, weights: np.ndarray) -> float | None:
    total = float(weights[valid].sum())
    return None if total <= 0.0 else 100.0 * float(weights[valid & condition].sum()) / total


def weighted_percentile(values: np.ndarray, weights: np.ndarray, q: float) -> float | None:
    ok = np.isfinite(values)
    if not ok.any():
        return None
    v, w = values[ok], weights[ok]
    order = np.argsort(v)
    cdf = np.cumsum(w[order])
    idx = min(int(np.searchsorted(cdf / cdf[-1], q / 100.0)), v.size - 1)
    return float(v[order][idx])


def badge(value: float | None, bounds: tuple[float, ...]) -> str | None:
    return None if value is None else _NAMES[sum(value >= b for b in bounds)]


def _pct(layer: np.ndarray | None, weights: np.ndarray, predicate: Any) -> float | None:
    if layer is None:
        return None
    valid = np.isfinite(layer)
    with np.errstate(invalid="ignore"):
        return area_pct(predicate(layer), valid, weights)


def summarize(layers: dict[str, np.ndarray | None], lats: np.ndarray, profile: Profile) -> dict[str, Any]:
    awci = layers["awci"]
    assert awci is not None
    w = area_weights(lats, awci.shape[1])
    p95 = weighted_percentile(awci, w, 95.0)
    code = None if p95 is None else int(level_codes(np.array([p95]), profile)[0])
    bias = layers["cloud_cover_bias"]
    mucape = layers["mucape"]
    out: dict[str, Any] = {
        "awci_p95": p95, "awci_class": None if code is None else profile.level_thresholds[code][1],
        "turbulence_area_pct": _pct(layers["cat_category"], w, lambda a: a >= 2),
        "convection_area_pct": _pct(mucape, w, lambda a: a >= CONVECTIVE_MUCAPE_J_KG),
        "mucape_max": None if mucape is None or not np.isfinite(mucape).any() else float(np.nanmax(mucape)),
        "icing_area_pct": _pct(layers["icing_potential"], w, lambda a: a >= 1),
        "shear_p95": None if layers["vertical_shear"] is None else weighted_percentile(layers["vertical_shear"], w, 95.0),
        "heavy_precip_area_pct": _pct(layers["precip_class"], w, lambda a: a >= 3),
        # every cell counts: no ceiling (NaN) means no low ceiling, not missing data
        "low_ceiling_area_pct": None if layers["ceiling_m"] is None else area_pct(
            np.nan_to_num(layers["ceiling_m"], nan=np.inf) < IFR_CEILING_M, np.ones(awci.shape, dtype=bool), w),
        "cb_area_pct": _pct(layers["convective_class"], w, lambda a: a >= 3),
        "cloud_cover_bias_mean": None if bias is None or not np.isfinite(bias).any() else float(np.nanmean(bias)),
        "valid_cells_pct": area_pct(np.isfinite(awci), np.ones(awci.shape, dtype=bool), w),
    }
    out["badges"] = {
        **{k: badge(out[k], AREA_BADGES_PCT) for k in ("turbulence_area_pct", "convection_area_pct", "icing_area_pct",
                                                       "heavy_precip_area_pct", "low_ceiling_area_pct", "cb_area_pct")},
        "shear_p95": badge(out["shear_p95"], SHEAR_BADGES_PER_S),
    }
    return out
```

- [ ] **Step 4:** PASS.
- [ ] **Step 5: tests d'API (échouent)** — `tests/test_web_awci_summary_api.py` (ingestion de la fixture sèche dans `tmp_path_factory`, même mise en place que `tests/test_web_awci_clouds_api.py`)

```python
def test_summary_route(client) -> None:
    body = client.get(f"{BASE}/summary", params=Q | {"step": 3, "level": 300}).json()
    for key in ("awci_p95", "awci_class", "turbulence_area_pct", "icing_area_pct", "shear_p95", "low_ceiling_area_pct",
                "cb_area_pct", "valid_cells_pct", "badges", "awci_p95_by_level", "provenance"):
        assert key in body
    assert len(body["awci_p95_by_level"]) == 12 and body["provenance"]["step"] == 3


def test_summary_series_route(client) -> None:
    body = client.get(f"{BASE}/summary/series", params=Q | {"level": 300}).json()
    assert [p["step"] for p in body["points"]] == [0, 3] and "awci_p95" in body["points"][0]


def test_clouds_series_route(client) -> None:
    body = client.get(f"{BASE}/clouds/series", params=Q | {"lat": 36, "lon": 3}).json()
    assert [p["step"] for p in body["points"]] == [0, 3]
    assert set(body["points"][0]["genus"]) == {"low", "mid", "high"}


def test_profile_has_dewpoint_not_above_temperature(client) -> None:
    levels = client.get(f"{BASE}/profile", params=Q | {"step": 3, "lat": 36, "lon": 3}).json()["levels"]
    for lev in levels:
        t, td = lev["level_layers"].get("t"), lev["dewpoint_k"]
        assert (t is None) == (td is None) and (td is None or td <= t + 1e-6)


def test_runs_expose_ingestion_time(client) -> None:
    assert client.get(f"{BASE}/runs", params={"domain": "fixture"}).json()[0]["ingested_at"]


def test_clouds_etage_bounds_and_base_fl(client) -> None:
    body = client.get(f"{BASE}/clouds", params=Q | {"step": 3, "lat": 36, "lon": 3}).json()
    b = body["etage_bounds_fl"]
    assert b["mid_high"] > b["low_mid"] > 0
    assert all("base_fl" in lay for lay in body["layers"] if lay["kind"] == "layer")
```

- [ ] **Step 6:** FAIL, puis implémenter dans `awci_router.py` :

```python
_SUMMARY_LEVEL = ("awci", "cat_category", "icing_potential", "vertical_shear")
_SUMMARY_SURFACE = ("mucape", "precip_class", "ceiling_m", "convective_class", "cloud_cover_bias")


def _summary_layers(ds: Any, m: dict[str, Any], si: int, li: int) -> dict[str, np.ndarray | None]:
    surface = _run_layers(m, "surface_layers")
    out: dict[str, np.ndarray | None] = {n: ds[n].isel(step=si, level=li).values for n in _SUMMARY_LEVEL}
    out |= {n: ds[n].isel(step=si).values if n in surface else None for n in _SUMMARY_SURFACE}
    return out


@router.get("/summary")
def summary(request: Request, domain: str, run: RunId, level: float,
            step: int = Query(ge=0, le=384)) -> dict[str, Any]:
    m = _manifest(request, domain, run)
    si, li = _step_index(m, step), _level_index(m, level)
    ds = _dataset(request, domain, run)
    lats = ds["lat"].values
    body = summarize(_summary_layers(ds, m, si, li), lats, request.app.state.awci_profile)
    awci_all = ds["awci"].isel(step=si).values
    w = area_weights(lats, awci_all.shape[2])
    body["awci_p95_by_level"] = [{"level_hpa": p, "flight_level": fl, "awci_p95": weighted_percentile(awci_all[k], w, 95.0)}
                                 for k, (p, fl) in enumerate(zip(m["levels_hpa"], m["flight_levels"]))]
    return body | {"level_hpa": level, "provenance": _provenance(m, step), "source_tier": "nwp_forecast"}


@router.get("/summary/series")
def summary_series(request: Request, domain: str, run: RunId, level: float) -> dict[str, Any]:
    m = _manifest(request, domain, run)
    li = _level_index(m, level)
    ds = _dataset(request, domain, run)
    lats, prof = ds["lat"].values, request.app.state.awci_profile
    points = []
    for si, (s, vt) in enumerate(zip(m["steps"], m["valid_times"])):
        if s in m["missing_steps"]:
            points.append({"step": s, "valid_time": vt, "missing": True})
            continue
        body = summarize(_summary_layers(ds, m, si, li), lats, prof)
        points.append({"step": s, "valid_time": vt, "missing": False,
                       **{k: body[k] for k in ("awci_p95", "turbulence_area_pct", "icing_area_pct",
                                               "convection_area_pct", "cb_area_pct")}})
    return {"level_hpa": level, "points": points, "provenance": _provenance(m, None), "source_tier": "nwp_forecast"}
```

  - `/clouds/series` : `_require_layer(m, "genus_low")` ; pour chaque échéance non manquante, `genus_low/mid/high` (via `_genus_name`), `convective_class`, `ceiling_m`, `cloud_cover_total_diag` lus en `isel(lat=i, lon=j)` sur la dimension `step` entière (une lecture par couche).
  - `/profile` : `dewpoint_k = _num(dewpoint_k_from_vapor_pressure(vapor_pressure_hpa(q, p)))` par niveau (`q = column["q"][li]`, `p = level_hpa`), `null` si `q` est `null`.
  - `store.CubeWriter.finalize` : `"ingested_at": datetime.now(UTC).isoformat(timespec="seconds")` ; `/runs` : `"ingested_at": m.get("ingested_at")`.
  - `/clouds` : `etage_bounds_fl = {"low_mid": flight_level(0.8 * sp_hpa), "mid_high": flight_level(0.45 * sp_hpa)}` (bornes σ du profil nuageux : `cloud_profile.sigma_low_mid` / `sigma_mid_high`) ; `clouds.column_layers` ajoute `"base_fl": flight_level(float(levels_hpa[k]))`.
  - `/registry` : `"summary_thresholds": SUMMARY_THRESHOLDS`.
- [ ] **Step 7:** PASS + suite complète ; `ruff`, `mypy`. **Step 8:** commit `feat(awci-web): /summary, /summary/series, /clouds/series, dewpoint profile, ingestion time`.

---

### Task 2: Relais WMS EUMETView (`/wms`, `/wms/times`)

**Files:** Create `src/acf/web/awci_wms.py`, `tests/test_web_awci_wms.py`, `tests/data/wms/eumetview_capabilities_excerpt.xml` (+ `NOTICE.md`) ; Modify `src/acf/web/awci_router.py` (inclusion du sous-routeur), `src/acf/web/awci_app.py` (état `awci_wms`).

**Interfaces:**
- Produces: `WMS_LAYERS: dict[str, dict]` (nom → libellé, pas de temps), `parse_time_dimension(text, count) -> list[datetime]`, `capabilities_time_dimensions(xml) -> dict[str, str]`, `WmsFetcher` (protocole `get(url, timeout) -> tuple[str, bytes]`), `WmsRelay(fetcher, cache_dir, now=...)` avec `.times(layer, count)` et `.tile(layer, time, bbox, width, height) -> tuple[bytes, str]`, `WmsUpstreamError`.
- Routes : `GET /awci/wms?layer&bbox&width&height[&time]` → `image/png` + `X-AWCI-Observed-At`, `X-AWCI-Attribution: © EUMETSAT` ; `GET /awci/wms/times?layer&count=1..48` → `{layer, label, times: [...], attribution}` ; `GET /awci/wms/layers` → liste blanche.

- [ ] **Step 1:** Extraire l'extrait **réel** des capacités : `python - <<EOF` (scratchpad, non commité) qui télécharge `GetCapabilities` d'EUMETView, garde `<Service>` et les `<Layer>` de la liste blanche (nom, titre, `Dimension name="time"`) sous une racine `WMS_Capabilities` (espace de noms `http://www.opengis.net/wms`, version 1.3.0) et écrit `tests/data/wms/eumetview_capabilities_excerpt.xml` + `NOTICE.md` (source, date, « © EUMETSAT »).
- [ ] **Step 2: tests (échouent)**

```python
"""EUMETView WMS relay: allow-list, validation, latest time, disk cache, upstream failures."""

import struct
import zlib
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from acf.web.awci_app import create_awci_app
from acf.web.awci_wms import WMS_LAYERS, WmsRelay, capabilities_time_dimensions, parse_time_dimension

CAPS = (Path(__file__).parent / "data" / "wms" / "eumetview_capabilities_excerpt.xml").read_bytes()


def _png() -> bytes:
    raw = b"\x00\x00\x00\x00\x00"
    def chunk(t: bytes, d: bytes) -> bytes:
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


class FakeFetcher:
    def __init__(self, fail: bool = False, xml_error: bool = False) -> None:
        self.calls: list[str] = []
        self.fail, self.xml_error = fail, xml_error

    def get(self, url: str, timeout: float) -> tuple[str, bytes]:
        self.calls.append(url)
        if self.fail:
            raise OSError("upstream down")
        if "GetCapabilities" in url:
            return "text/xml", CAPS
        return ("text/xml", b"<ServiceExceptionReport/>") if self.xml_error else ("image/png", _png())


def _client(tmp_path: Path, fetcher: FakeFetcher) -> TestClient:
    app = create_awci_app(data_dir=tmp_path)
    app.state.awci_wms = WmsRelay(fetcher, tmp_path / "wms-cache")
    return TestClient(app)


BBOX = "0,4000000,500000,4500000"


def test_time_dimension_interval_and_list() -> None:
    times = parse_time_dimension("2026-09-25T18:00:00.000Z/2026-09-25T18:30:00.000Z/PT10M", 3)
    assert times == [datetime(2026, 9, 25, 18, m, tzinfo=UTC) for m in (10, 20, 30)]
    assert parse_time_dimension("2026-09-25T18:00:00Z,2026-09-25T18:15:00Z", 5)[-1].minute == 15


def test_real_capabilities_excerpt_covers_the_allow_list() -> None:
    dims = capabilities_time_dimensions(CAPS)
    assert set(WMS_LAYERS) <= set(dims)


def test_tile_uses_latest_time_and_is_cached(tmp_path: Path) -> None:
    f = FakeFetcher()
    c = _client(tmp_path, f)
    r = c.get("/api/v1/awci/wms", params={"layer": "mtg_fd:ir105_hrfi", "bbox": BBOX, "width": 256, "height": 256})
    assert r.status_code == 200 and r.headers["content-type"] == "image/png"
    assert r.headers["x-awci-observed-at"].endswith("Z") and "EUMETSAT" in r.headers["x-awci-attribution"]
    n = len(f.calls)
    c.get("/api/v1/awci/wms", params={"layer": "mtg_fd:ir105_hrfi", "bbox": BBOX, "width": 256, "height": 256,
                                      "time": r.headers["x-awci-observed-at"]})
    assert len(f.calls) == n  # same explicit time -> disk cache


@pytest.mark.parametrize("params,status", [
    ({"layer": "evil:layer"}, 400),
    ({"bbox": "0,0,1"}, 400),
    ({"bbox": "0,0,99999999,1"}, 400),
    ({"width": 4096}, 422),
    ({"time": "yesterday"}, 400),
])
def test_invalid_requests_rejected(tmp_path: Path, params: dict, status: int) -> None:
    base = {"layer": "mtg_fd:ir105_hrfi", "bbox": BBOX, "width": 256, "height": 256}
    assert _client(tmp_path, FakeFetcher()).get("/api/v1/awci/wms", params=base | params).status_code == status


@pytest.mark.parametrize("fetcher", [FakeFetcher(fail=True), FakeFetcher(xml_error=True)])
def test_upstream_failure_is_502(tmp_path: Path, fetcher: FakeFetcher) -> None:
    r = _client(tmp_path, fetcher).get("/api/v1/awci/wms", params={"layer": "mtg_fd:ir105_hrfi", "bbox": BBOX,
                                                                  "width": 256, "height": 256})
    assert r.status_code == 502


def test_times_route(tmp_path: Path) -> None:
    body = _client(tmp_path, FakeFetcher()).get("/api/v1/awci/wms/times",
                                                params={"layer": "mtg_fd:li_afa", "count": 6}).json()
    assert len(body["times"]) == 6 and body["times"] == sorted(body["times"])
```

- [ ] **Step 3:** FAIL. **Step 4: implémentation** — `src/acf/web/awci_wms.py`

```python
"""
Read-only relay to the public EUMETSAT EUMETView WMS for AWCI Web observation overlays.

Only allow-listed layers, EPSG:3857 bounding boxes inside the Web-Mercator extent, image sizes up to
2048 px and ISO-8601 UTC times are forwarded; nothing else reaches the upstream URL. The latest time
of a layer comes from GetCapabilities (cached 5 min) and is returned in X-AWCI-Observed-At, so the UI
never shows an observation as synchronous with a forecast step. Tiles are cached on disk per
normalised request. Imagery © EUMETSAT.
"""

from __future__ import annotations

import hashlib
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated, Any, Protocol

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import Response

UPSTREAM = "https://view.eumetsat.int/geoserver/wms"
ATTRIBUTION = "© EUMETSAT"
MERCATOR_MAX = 20037508.342789244
USER_AGENT = "ACF-AWCI-Web/1.0 (+https://github.com/fourasohaib2-lab/ACF)"
CAPABILITIES_TTL_S = 300.0
_NS = "{http://www.opengis.net/wms}"
_TIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d{1,3})?)?Z$")
_PERIOD_RE = re.compile(r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$")

WMS_LAYERS: dict[str, dict[str, Any]] = {
    "mtg_fd:ir105_hrfi": {"label": "MTG FCI IR 10,5 µm", "group": "satellite"},
    "mtg_fd:rgb_geocolour": {"label": "MTG GeoColour", "group": "satellite"},
    "mtg_fd:rgb_dust": {"label": "MTG Dust RGB", "group": "satellite"},
    "mtg_fd:rgb_fog": {"label": "MTG Fog RGB", "group": "satellite"},
    "mtg_fd:rgb_cloudtype": {"label": "MTG Cloud Type RGB", "group": "clouds"},
    "mtg_fd:rgb_cloudphase": {"label": "MTG Cloud Phase RGB", "group": "clouds"},
    "msg_fes:cth": {"label": "MSG hauteur du sommet des nuages", "group": "clouds"},
    "msg_fes:clm": {"label": "MSG masque nuageux", "group": "clouds"},
    "msg_fes:rgb_convection": {"label": "MSG Convection RGB", "group": "convection"},
    "msg_fes:rdt": {"label": "MSG orages à développement rapide (RDT)", "group": "convection"},
    "mtg_fd:li_afa": {"label": "MTG LI aire des éclairs cumulée", "group": "convection"},
    "msg_fes:rgb_ash": {"label": "MSG Ash RGB (cendres)", "group": "ash"},
}


class WmsUpstreamError(RuntimeError):
    """EUMETView did not return a usable answer."""


class WmsFetcher(Protocol):
    def get(self, url: str, timeout: float) -> tuple[str, bytes]: ...


class UrllibWmsFetcher:
    def get(self, url: str, timeout: float) -> tuple[str, bytes]:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.headers.get_content_type(), response.read()


def _iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def _period(text: str) -> timedelta:
    match = _PERIOD_RE.match(text)
    if not match or not any(match.groups()):
        raise ValueError(f"unsupported WMS time period {text!r}")
    h, m, s = (int(g or 0) for g in match.groups())
    return timedelta(hours=h, minutes=m, seconds=s)


def parse_time_dimension(text: str, count: int) -> list[datetime]:
    """Latest `count` instants of a WMS 1.3 time dimension ("start/end/period" intervals and/or instants)."""
    found: set[datetime] = set()
    for part in (p.strip() for p in text.split(",")):
        if "/" in part:
            start, end, period = part.split("/")
            t, first, step = _iso(end), _iso(start), _period(period)
            while t >= first and len(found) < 4 * count:
                found.add(t)
                t -= step
        elif part:
            found.add(_iso(part))
    return sorted(found)[-count:]


def capabilities_time_dimensions(xml: bytes) -> dict[str, str]:
    root = ET.fromstring(xml)
    out: dict[str, str] = {}
    for layer in root.iter(f"{_NS}Layer"):
        name = layer.findtext(f"{_NS}Name")
        dim = next((d for d in layer.findall(f"{_NS}Dimension") if d.get("name") == "time"), None)
        if name and dim is not None and dim.text:
            out[name] = dim.text.strip()
    return out


def _fmt(t: datetime) -> str:
    return t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class WmsRelay:
    def __init__(self, fetcher: WmsFetcher, cache_dir: Path, timeout_s: float = 20.0,
                 clock: Callable[[], float] = time.monotonic) -> None:
        self.fetcher, self.cache_dir, self.timeout_s, self.clock = fetcher, Path(cache_dir), timeout_s, clock
        self._caps: tuple[float, dict[str, str]] | None = None

    def _dimensions(self) -> dict[str, str]:
        if self._caps is None or self.clock() - self._caps[0] > CAPABILITIES_TTL_S:
            url = f"{UPSTREAM}?service=WMS&version=1.3.0&request=GetCapabilities"
            try:
                _, body = self.fetcher.get(url, self.timeout_s)
                self._caps = (self.clock(), capabilities_time_dimensions(body))
            except (OSError, ET.ParseError) as exc:
                raise WmsUpstreamError(f"EUMETView capabilities unavailable: {exc}") from exc
        return self._caps[1]

    def times(self, layer: str, count: int) -> list[str]:
        dim = self._dimensions().get(layer)
        if dim is None:
            raise WmsUpstreamError(f"layer {layer} has no time dimension upstream")
        return [_fmt(t) for t in parse_time_dimension(dim, count)]

    def tile(self, layer: str, when: str | None, bbox: tuple[float, float, float, float], width: int,
             height: int) -> tuple[bytes, str]:
        observed = when or self.times(layer, 1)[-1]
        params = {"service": "WMS", "version": "1.3.0", "request": "GetMap", "layers": layer, "styles": "",
                  "crs": "EPSG:3857", "bbox": ",".join(f"{v:.3f}" for v in bbox), "width": str(width),
                  "height": str(height), "format": "image/png", "transparent": "true", "time": observed}
        query = urllib.parse.urlencode(params)
        path = self.cache_dir / f"{hashlib.sha256(query.encode()).hexdigest()}.png"
        if path.exists():
            return path.read_bytes(), observed
        try:
            content_type, body = self.fetcher.get(f"{UPSTREAM}?{query}", self.timeout_s)
        except OSError as exc:
            raise WmsUpstreamError(f"EUMETView GetMap failed: {exc}") from exc
        if content_type != "image/png":
            raise WmsUpstreamError(f"EUMETView answered {content_type} instead of a PNG")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_bytes(body)
        tmp.replace(path)
        return body, observed


router = APIRouter()


def _relay(request: Request) -> WmsRelay:
    return request.app.state.awci_wms


def _layer(name: str) -> str:
    if name not in WMS_LAYERS:
        raise HTTPException(400, f"layer {name!r} is not relayed")
    return name


def _bbox(text: str) -> tuple[float, float, float, float]:
    try:
        values = tuple(float(v) for v in text.split(","))
    except ValueError as exc:
        raise HTTPException(400, "bbox must be 4 numbers") from exc
    if len(values) != 4 or not all(abs(v) <= MERCATOR_MAX for v in values) or values[0] >= values[2] \
            or values[1] >= values[3]:
        raise HTTPException(400, "bbox must be minx,miny,maxx,maxy inside the EPSG:3857 extent")
    return values[0], values[1], values[2], values[3]


@router.get("/wms/layers")
def wms_layers() -> list[dict[str, Any]]:
    return [{"layer": name, **meta, "attribution": ATTRIBUTION} for name, meta in WMS_LAYERS.items()]


@router.get("/wms/times")
def wms_times(request: Request, layer: str, count: Annotated[int, Query(ge=1, le=48)] = 1) -> dict[str, Any]:
    try:
        times = _relay(request).times(_layer(layer), count)
    except WmsUpstreamError as exc:
        raise HTTPException(502, str(exc)) from exc
    return {"layer": layer, "label": WMS_LAYERS[layer]["label"], "times": times, "attribution": ATTRIBUTION}


@router.get("/wms", response_model=None)
def wms_tile(request: Request, layer: str, bbox: str, width: Annotated[int, Query(ge=1, le=2048)] = 256,
             height: Annotated[int, Query(ge=1, le=2048)] = 256, time: str | None = None) -> Response:
    if time is not None and not _TIME_RE.match(time):
        raise HTTPException(400, "time must be ISO-8601 UTC, e.g. 2026-09-25T18:50:00Z")
    try:
        body, observed = _relay(request).tile(_layer(layer), time, _bbox(bbox), width, height)
    except WmsUpstreamError as exc:
        raise HTTPException(502, str(exc)) from exc
    return Response(content=body, media_type="image/png", headers={
        "X-AWCI-Observed-At": observed, "X-AWCI-Attribution": ATTRIBUTION,
        "Cache-Control": "public, max-age=86400" if time else "public, max-age=300"})
```

  - `awci_router.py` (fin du module) : `from acf.web.awci_wms import router as _wms_router` puis `router.include_router(_wms_router)`.
  - `awci_app.attach_awci_state` : `app.state.awci_wms = WmsRelay(UrllibWmsFetcher(), Path(os.environ.get("ACF_AWCI_WMS_CACHE", data_root() / ".wms-cache")))`; en-têtes CORS exposés : `X-AWCI-Observed-At`.
  - Test réseau réel opt-in (`ACF_AWCI_NETWORK_TESTS=1`) : `/wms/times?layer=mtg_fd:ir105_hrfi` sur la vraie EUMETView renvoie une heure de moins de 2 h.
- [ ] **Step 5:** PASS + suite ; ruff, mypy. **Step 6:** commit `feat(awci-web): read-only EUMETView WMS relay with allow-list, observed time and disk cache`.

---

### Task 3: Service du front et serveur d'e2e

**Files:** Modify `src/acf/web/awci_app.py` ; Create `tools/awci/e2e_server.py`, `tests/test_web_awci_static.py`.

**Interfaces:** `create_awci_app(..., web_dist: Path | None = None)` monte `StaticFiles(directory=web_dist, html=True)` sur `/` **après** l'API si `web_dist/index.html` existe (défaut `ACF_AWCI_WEB_DIST` ou `<repo>/web/awci/dist`) ; `ACF_AWCI_DOMAINS_FILE` pris en compte. `tools/awci/e2e_server.py --port 8099 --data-dir DIR` ingère les deux fixtures réelles (domaines `fixture` et `fixture_wet`), écrit `domains.json`, remplace le relais WMS par un relais hors ligne (capacités = extrait réel, tuiles = PNG transparent) et lance uvicorn.

- [ ] **Step 1: tests (échouent)**

```python
def test_serves_index_and_keeps_api(tmp_path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<!doctype html><title>AWCI</title>")
    c = TestClient(create_awci_app(data_dir=tmp_path, web_dist=dist))
    assert "AWCI" in c.get("/").text
    assert c.get("/api/v1/awci/registry").status_code == 200


def test_no_dist_no_static_mount(tmp_path) -> None:
    c = TestClient(create_awci_app(data_dir=tmp_path, web_dist=tmp_path / "absent"))
    assert c.get("/").status_code == 404
```

- [ ] **Step 2:** FAIL. **Step 3:** implémenter (`from fastapi.staticfiles import StaticFiles`). **Step 4:** PASS. **Step 5:** commit `feat(awci-web): serve the built front from acf-awci-web; e2e server over real fixtures`.

---

### Task 4: Squelette du front, thème, formats, palettes, définitions de couches

**Files:** Create `web/awci/{package.json,package-lock.json,tsconfig.json,vite.config.ts,eslint.config.js,index.html,.gitignore}`, `web/awci/src/{main.tsx,App.tsx}`, `src/theme/{tokens.css,palette.ts}`, `src/lib/format.ts`, `src/i18n/fr.ts`, `src/map/layers.ts`, `src/test/setup.ts`, tests `src/lib/format.test.ts`, `src/theme/palette.test.ts`, `src/map/layers.test.ts`.

**Interfaces:**
- `format.ts` : `FT_PER_M`, `fmt(value, digits?, unit?)`, `utcLabel(iso)`, `flLabel(fl)`, `ageLabel(iso, now)`, `stepLabel(step)`.
- `palette.ts` : `AWCI_CLASS_COLORS`, `SEQ_BLUE` (13 pas, sombre→clair), `CATEGORICAL` (3), `STATUS`, `HATCH`, `hexToRgb`, `rampColor(stops, t)`.
- `layers.ts` : `Rgba`, `Render`, `LayerDef`, `Group`, `GROUP_LABELS`, `LAYER_DEFS`, `layerDef(id)`, `colorFn(def, awciBounds) -> (v) => Rgba | null`, `GENUS_FAMILY`.

- [ ] **Step 1:** `npm create vite@latest web/awci -- --template react-ts` n'est **pas** utilisé (modèle générique) ; créer les fichiers à la main, puis `cd web/awci && npm install react react-dom maplibre-gl @tanstack/react-query lucide-react @fontsource/fira-sans @fontsource/fira-code && npm install -D vite @vitejs/plugin-react typescript vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event @playwright/test @axe-core/playwright eslint @eslint/js typescript-eslint eslint-plugin-react-hooks globals`.
  - `package.json` scripts : `"dev": "vite"`, `"build": "tsc -b && vite build"`, `"test": "vitest run"`, `"lint": "eslint ."`, `"e2e": "playwright test"`.
  - `vite.config.ts` : plugin React ; `server.proxy["/api"] = "http://127.0.0.1:8091"` ; `test: { environment: "jsdom", setupFiles: "./src/test/setup.ts", include: ["src/**/*.test.{ts,tsx}"] }`.
  - `tsconfig.json` : `strict`, `noUncheckedIndexedAccess`, `noUnusedLocals`, `jsx: "react-jsx"`, `moduleResolution: "bundler"`, `types: ["vitest/globals"]`.
- [ ] **Step 2: tests (échouent)**

```ts
// src/lib/format.test.ts
import { ageLabel, flLabel, fmt, stepLabel, utcLabel } from "./format";

test("fmt uses French separators and an em dash for missing values", () => {
  expect(fmt(1234.5, 1, "J/kg")).toBe(`1${" "}234,5 J/kg`);
  expect(fmt(null)).toBe("—");
  expect(fmt(Number.NaN, 0, "m")).toBe("—");
});
test("labels", () => {
  expect(utcLabel("2026-09-25T12:00:00+00:00")).toBe("25/09 12:00 UTC");
  expect(flLabel(50)).toBe("FL050");
  expect(stepLabel(24)).toBe("+24 h");
  expect(ageLabel("2026-09-25T10:40:00Z", new Date("2026-09-25T12:00:00Z"))).toBe("il y a 1 h 20");
  expect(ageLabel("2026-09-25T11:55:00Z", new Date("2026-09-25T12:00:00Z"))).toBe("il y a 5 min");
});
```

```ts
// src/theme/palette.test.ts
import { AWCI_CLASS_COLORS, CATEGORICAL, SEQ_BLUE, hexToRgb, rampColor } from "./palette";

test("validated palettes are exactly the documented ones", () => {
  expect(AWCI_CLASS_COLORS).toEqual(["#854494", "#b94c90", "#e45d84", "#ff7f6c", "#ffa85d", "#ffd368"]);
  expect(CATEGORICAL).toEqual(["#3987e5", "#d95926", "#199e70"]);
  expect(SEQ_BLUE[0]).toBe("#0d366b");
  expect(SEQ_BLUE[SEQ_BLUE.length - 1]).toBe("#cde2fb");
});
test("rampColor clamps and hits the end stops", () => {
  expect(rampColor(SEQ_BLUE, -1)).toEqual(hexToRgb("#0d366b"));
  expect(rampColor(SEQ_BLUE, 2)).toEqual(hexToRgb("#cde2fb"));
});
```

```ts
// src/map/layers.test.ts
import { colorFn, layerDef } from "./layers";
import { AWCI_CLASS_COLORS, CATEGORICAL, hexToRgb } from "../theme/palette";

const BOUNDS = [20, 35, 50, 65, 85];
test("AWCI colours follow the profile class bounds (value >= bound goes up)", () => {
  const c = colorFn(layerDef("awci"), BOUNDS);
  expect(c(19.9)?.slice(0, 3)).toEqual(hexToRgb(AWCI_CLASS_COLORS[0]));
  expect(c(20)?.slice(0, 3)).toEqual(hexToRgb(AWCI_CLASS_COLORS[1]));
  expect(c(99)?.slice(0, 3)).toEqual(hexToRgb(AWCI_CLASS_COLORS[5]));
});
test("genus map folds genera into three validated families", () => {
  const c = colorFn(layerDef("genus_low"), BOUNDS);
  expect(c(9)?.slice(0, 3)).toEqual(hexToRgb(CATEGORICAL[1])); // Cb
  expect(c(8)?.slice(0, 3)).toEqual(hexToRgb(CATEGORICAL[2])); // Cu / TCU
  expect(c(6)?.slice(0, 3)).toEqual(hexToRgb(CATEGORICAL[0])); // stratiform (Sc)
  expect(c(-1)).toBeNull(); // clear: transparent, not a colour
});
test("no-hazard codes are transparent", () => {
  expect(colorFn(layerDef("icing_potential"), BOUNDS)(0)).toBeNull();
  expect(colorFn(layerDef("icing_potential"), BOUNDS)(1)).not.toBeNull();
});
```

- [ ] **Step 3:** FAIL. **Step 4: implémentation**

```ts
// src/lib/format.ts
export const FT_PER_M = 1 / 0.3048;

export function fmt(value: number | null | undefined, digits = 0, unit = ""): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return "—";
  const s = value.toLocaleString("fr-FR", { minimumFractionDigits: digits, maximumFractionDigits: digits });
  return unit ? `${s} ${unit}` : s;
}

const p2 = (n: number) => String(n).padStart(2, "0");

export function utcLabel(iso: string): string {
  const d = new Date(iso);
  return `${p2(d.getUTCDate())}/${p2(d.getUTCMonth() + 1)} ${p2(d.getUTCHours())}:${p2(d.getUTCMinutes())} UTC`;
}

export const flLabel = (fl: number) => `FL${String(Math.round(fl)).padStart(3, "0")}`;
export const stepLabel = (step: number) => `+${step} h`;

export function ageLabel(iso: string, now: Date): string {
  const minutes = Math.max(0, Math.round((now.getTime() - new Date(iso).getTime()) / 60000));
  if (minutes < 60) return `il y a ${minutes} min`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m ? `il y a ${h} h ${p2(m)}` : `il y a ${h} h`;
}
```

```ts
// src/theme/palette.ts
/** AWCI ordinal classes, dark theme, validated with dataviz validate_palette --ordinal --mode dark --surface #0b1220. */
export const AWCI_CLASS_COLORS = ["#854494", "#b94c90", "#e45d84", "#ff7f6c", "#ffa85d", "#ffd368"] as const;
/** dataviz reference sequential blue, darkest -> lightest (low values recede into the dark surface). */
export const SEQ_BLUE = ["#0d366b", "#104281", "#184f95", "#1c5cab", "#256abf", "#2a78d6", "#3987e5", "#5598e7",
  "#6da7ec", "#86b6ef", "#9ec5f4", "#b7d3f6", "#cde2fb"] as const;
/** dataviz dark categorical slots 1-3: the only ones valid for all pairs (maps). */
export const CATEGORICAL = ["#3987e5", "#d95926", "#199e70"] as const;
export const STATUS = { ok: "#0ca30c", attention: "#fab219", serious: "#ec835a", critical: "#d03b3b" } as const;
export type Rgb = [number, number, number];
export const HATCH: [number, number, number, number] = [137, 135, 129, 150];

export function hexToRgb(hex: string): Rgb {
  const n = Number.parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

export function rampColor(stops: readonly string[], t: number): Rgb {
  const x = Math.min(1, Math.max(0, t)) * (stops.length - 1);
  const i = Math.min(stops.length - 2, Math.floor(x));
  const a = hexToRgb(stops[i]!);
  const b = hexToRgb(stops[i + 1]!);
  const f = x - i;
  return [0, 1, 2].map((k) => Math.round(a[k]! + (b[k]! - a[k]!) * f)) as Rgb;
}
```

```ts
// src/map/layers.ts
import { AWCI_CLASS_COLORS, CATEGORICAL, SEQ_BLUE, hexToRgb, rampColor } from "../theme/palette";

export type Rgba = [number, number, number, number];
export type Group = "awci" | "hazards" | "clouds" | "surface";
export type Render =
  | { kind: "awci" }
  | { kind: "codes"; colors: (string | null)[]; labels: string[] }
  | { kind: "continuous"; min: number; max: number; invert?: boolean; scale?: number; unitLabel?: string }
  | { kind: "genus" };
export interface LayerDef { id: string; label: string; group: Group; perLevel: boolean; unit: string; render: Render }

export const GROUP_LABELS: Record<Group, string> = {
  awci: "AWCI", hazards: "Dangers", clouds: "Nuages", surface: "Surface et précipitations",
};
const S = SEQ_BLUE;
const cont = (min: number, max: number, extra: Partial<Extract<Render, { kind: "continuous" }>> = {}): Render =>
  ({ kind: "continuous", min, max, ...extra });

export const LAYER_DEFS: LayerDef[] = [
  { id: "awci", label: "AWCI", group: "awci", perLevel: true, unit: "0–100", render: { kind: "awci" } },
  { id: "cat_category", label: "Turbulence en air clair", group: "hazards", perLevel: true, unit: "classe",
    render: { kind: "codes", colors: [null, S[6], S[9], S[12]], labels: ["Nulle", "Légère", "Modérée", "Modérée à sévère"] } },
  { id: "icing_potential", label: "Givrage potentiel", group: "hazards", perLevel: true, unit: "oui/non",
    render: { kind: "codes", colors: [null, S[10]], labels: ["Non", "Oui"] } },
  { id: "vertical_shear", label: "Cisaillement vertical", group: "hazards", perLevel: true, unit: "10⁻³ s⁻¹",
    render: cont(0, 0.012, { scale: 1000 }) },
  { id: "wind_speed", label: "Vent", group: "hazards", perLevel: true, unit: "m/s", render: cont(0, 80) },
  { id: "mucape", label: "Instabilité (MUCAPE)", group: "hazards", perLevel: false, unit: "J/kg", render: cont(0, 3000) },
  { id: "convective_class", label: "Convection (Cu, TCU, Cb)", group: "clouds", perLevel: false, unit: "classe",
    render: { kind: "codes", colors: [null, S[5], CATEGORICAL[2], CATEGORICAL[1], CATEGORICAL[1]],
      labels: ["Aucune", "Cu humilis/mediocris", "TCU", "Cb calvus", "Cb capillatus"] } },
  { id: "genus_low", label: "Genre, étage bas", group: "clouds", perLevel: false, unit: "", render: { kind: "genus" } },
  { id: "genus_mid", label: "Genre, étage moyen", group: "clouds", perLevel: false, unit: "", render: { kind: "genus" } },
  { id: "genus_high", label: "Genre, étage haut", group: "clouds", perLevel: false, unit: "", render: { kind: "genus" } },
  { id: "cloud_cover_low", label: "Couverture basse", group: "clouds", perLevel: false, unit: "octas", render: cont(0, 1, { scale: 8 }) },
  { id: "cloud_cover_mid", label: "Couverture moyenne", group: "clouds", perLevel: false, unit: "octas", render: cont(0, 1, { scale: 8 }) },
  { id: "cloud_cover_high", label: "Couverture haute", group: "clouds", perLevel: false, unit: "octas", render: cont(0, 1, { scale: 8 }) },
  { id: "cloud_fraction", label: "Fraction nuageuse au niveau", group: "clouds", perLevel: true, unit: "octas", render: cont(0, 1, { scale: 8 }) },
  { id: "ceiling_m", label: "Plafond (OACI)", group: "clouds", perLevel: false, unit: "ft", render: cont(0, 3048, { invert: true, scale: 1 / 0.3048 }) },
  { id: "cloud_top_teff_k", label: "Température des sommets (OLR)", group: "clouds", perLevel: false, unit: "°C",
    render: cont(200, 300, { invert: true }) },
  { id: "column_condensate", label: "Condensat colonne", group: "clouds", perLevel: false, unit: "kg/m²", render: cont(0, 5) },
  { id: "precip_class", label: "Précipitations (OMM)", group: "surface", perLevel: false, unit: "classe",
    render: { kind: "codes", colors: [null, S[4], S[7], S[10], S[12]], labels: ["Nulles", "Faibles", "Modérées", "Fortes", "Violentes"] } },
  { id: "snowfall_mm", label: "Chute de neige (3 h)", group: "surface", perLevel: false, unit: "mm eau", render: cont(0, 20) },
  { id: "snow_depth_cm", label: "Épaisseur de neige", group: "surface", perLevel: false, unit: "cm", render: cont(0, 100) },
  { id: "freezing_precip_mm", label: "Précipitations verglaçantes (3 h)", group: "surface", perLevel: false, unit: "mm", render: cont(0, 10) },
  { id: "gust_10m", label: "Rafales à 10 m", group: "surface", perLevel: false, unit: "m/s", render: cont(0, 40) },
  { id: "dust_proxy", label: "Soulèvement de poussière (proxy)", group: "surface", perLevel: false, unit: "0–1", render: cont(0, 1) },
];

export function layerDef(id: string): LayerDef {
  const def = LAYER_DEFS.find((d) => d.id === id);
  if (!def) throw new Error(`unknown layer ${id}`);
  return def;
}

/** WMO 0500 codes folded into the three map-valid categorical slots; exact genus in the inspector. */
export const GENUS_FAMILY = [
  { label: "Stratiformes et en nappes (Ci, Cc, Cs, Ac, As, Ns, Sc, St)", color: CATEGORICAL[0] },
  { label: "Cumulus, TCU", color: CATEGORICAL[2] },
  { label: "Cumulonimbus", color: CATEGORICAL[1] },
] as const;

const rgba = (hex: string): Rgba => [...hexToRgb(hex), 255];

export function colorFn(def: LayerDef, awciBounds: number[]): (v: number) => Rgba | null {
  const r = def.render;
  switch (r.kind) {
    case "awci":
      return (v) => rgba(AWCI_CLASS_COLORS[awciBounds.filter((b) => v >= b).length]!);
    case "codes":
      return (v) => { const c = r.colors[Math.round(v)]; return c ? rgba(c) : null; };
    case "genus":
      return (v) => {
        if (v === 9) return rgba(CATEGORICAL[1]);
        if (v === 8) return rgba(CATEGORICAL[2]);
        return v >= 0 && v <= 7 ? rgba(CATEGORICAL[0]) : null;
      };
    case "continuous":
      return (v) => {
        const t = (v - r.min) / (r.max - r.min);
        return [...rampColor(SEQ_BLUE, r.invert ? 1 - t : t), 255];
      };
  }
}
```

> `genus` = −2 (indéterminé) est converti en `NaN` avant rendu (hachures), dans `MapView` (Task 6).

  - `tokens.css` : variables de la surface `#0b1220`, panneaux `#111a2e`/`#16213a`, bordure `rgba(255,255,255,.10)`, texte `#ffffff`/`#c3c2b7`, atténué `#9a988f`, accent `#3987e5`, statuts ; `font-family: "Fira Sans", system-ui, sans-serif` ; chiffres `"Fira Code"` + `tabular-nums` pour tableaux et axes ; tailles 12/14/16/20/28 px ; `:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }` ; `@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }`.
  - `index.html` : `<html lang="fr">`, `<title>AWCI — Complexité météorologique aéronautique</title>`.
  - `App.tsx` provisoire : titre + « Chargement… » (remplacé en Task 7).
- [ ] **Step 5:** `npm test`, `npm run lint`, `npm run build` → OK. **Step 6:** `.gitignore` (`node_modules`, `dist`, `test-results`, `playwright-report`) ; commit `feat(awci-web): front scaffold, theme tokens, validated palettes, layer definitions`.

---

### Task 5: Client d'API, types, état de vue dans l'URL

**Files:** Create `src/api/{types.ts,client.ts,hooks.ts}`, `src/state/view.ts`, tests `src/api/client.test.ts`, `src/state/view.test.ts`.

**Interfaces:**
- `client.ts` : `ApiError(status, message)`, `getJson<T>(path, params?, signal?)`, `parseField(headers, buf) -> FieldData`, `getField(params, signal?)`.
- `types.ts` : `Domain`, `RunInfo`, `Meta`, `Provenance`, `FieldData`, `PointPayload`, `ProfilePayload`, `TimeseriesPayload`, `Summary`, `SummarySeries`, `CloudsPayload`, `CloudsSeries`, `Registry`, `WmsLayer`, `WmsTimes`.
- `view.ts` : `ViewState`, `parseView(search)`, `serializeView(v)`, `resolveView(v, domains, runs, meta, now) -> Resolved | null`, `nextStep(meta, step, dir)`, `nextLevel(meta, level, dir)`, `availableLayers(meta) -> LayerDef[]`, `useViewState()`.
- `hooks.ts` : `useDomains`, `useRuns(domain)`, `useMeta(domain, run)`, `useField(domain, run, layer, step, level?)`, `useSummary`, `useSummarySeries`, `usePoint`, `useProfile`, `useTimeseries`, `useClouds`, `useCloudsSeries`, `useRegistry`, `useWmsLayers`, `useWmsTimes(layer, count)`.

- [ ] **Step 1: tests (échouent)**

```ts
// src/api/client.test.ts
import { parseField } from "./client";

test("parseField decodes little-endian float32 and grid headers", () => {
  const values = new Float32Array([1, Number.NaN, 3, 4, 5, 6]);
  const headers = new Headers({ "X-AWCI-Shape": "2,3", "X-AWCI-Lats": "35,35.25", "X-AWCI-Lons": "2,2.5", "X-AWCI-Unit": "m/s" });
  const f = parseField(headers, values.buffer);
  expect([f.ny, f.nx, f.lat0, f.lat1, f.lon0, f.lon1, f.unit]).toEqual([2, 3, 35, 35.25, 2, 2.5, "m/s"]);
  expect(Number.isNaN(f.values[1]!)).toBe(true);
});
test("parseField rejects a size mismatch", () => {
  const headers = new Headers({ "X-AWCI-Shape": "3,3", "X-AWCI-Lats": "0,1", "X-AWCI-Lons": "0,1" });
  expect(() => parseField(headers, new Float32Array(4).buffer)).toThrow();
});
```

```ts
// src/state/view.test.ts
import { availableLayers, nextLevel, nextStep, parseView, resolveView, serializeView } from "./view";

const meta = { steps: [0, 3, 6, 9], missing_steps: [6], valid_times: ["2026-09-25T12:00:00+00:00",
  "2026-09-25T15:00:00+00:00", "2026-09-25T18:00:00+00:00", "2026-09-25T21:00:00+00:00"],
  levels_hpa: [1000, 850, 500, 300, 200], level_layers: ["awci", "t"], surface_layers: ["mucape"] } as never;

test("URL round trip keeps every field and drops invalid ones", () => {
  const v = parseView("?domain=north_africa&run=2026092512&step=9&level=300&layer=awci&lat=36.7&lon=3.2&ov=mtg_fd:ir105_hrfi");
  expect(parseView(serializeView(v))).toEqual(v);
  expect(parseView("?run=../../etc&step=abc&layer=<x>").run).toBeUndefined();
  expect(parseView("?step=abc").step).toBeUndefined();
});
test("missing steps are skipped both ways", () => {
  expect(nextStep(meta, 3, 1)).toBe(9);
  expect(nextStep(meta, 9, -1)).toBe(3);
  expect(nextStep(meta, 9, 1)).toBe(9);
});
test("levels move up (lower pressure) and down", () => {
  expect(nextLevel(meta, 500, 1)).toBe(300);
  expect(nextLevel(meta, 1000, -1)).toBe(1000);
});
test("resolveView picks the step nearest to now, never a missing one", () => {
  const r = resolveView(parseView(""), [{ name: "d", default: true }] as never,
    [{ run: "2026092512", status: "partial" }] as never, meta, new Date("2026-09-25T18:40:00Z"));
  // 18:40: +6 h (18:00) is missing; among available steps +9 h (21:00, 2 h 20 away) beats +3 h (15:00, 3 h 40)
  expect(r).toMatchObject({ domain: "d", run: "2026092512", step: 9, level: 300, layer: "awci" });
});
test("layers absent from the run are not offered", () => {
  expect(availableLayers(meta).map((d) => d.id)).toEqual(["awci", "mucape"]);
});
```

- [ ] **Step 2:** FAIL. **Step 3: implémentation**

```ts
// src/api/client.ts
import type { FieldData } from "./types";

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) { super(message); }
}
export const API_BASE = "/api/v1/awci";
type Params = Record<string, string | number | undefined>;

function query(params: Params): string {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) if (v !== undefined) q.set(k, String(v));
  const s = q.toString();
  return s ? `?${s}` : "";
}

async function fail(r: Response): Promise<never> {
  let detail = r.statusText;
  try { const body = (await r.json()) as { detail?: unknown }; if (body.detail) detail = String(body.detail); } catch { /* not JSON */ }
  throw new ApiError(r.status, detail);
}

export async function getJson<T>(path: string, params: Params = {}, signal?: AbortSignal): Promise<T> {
  const r = await fetch(`${API_BASE}${path}${query(params)}`, { signal });
  if (!r.ok) return fail(r);
  return (await r.json()) as T;
}

const pair = (h: Headers, name: string): [number, number] => {
  const raw = h.get(name);
  const parts = (raw ?? "").split(",").map(Number);
  if (parts.length !== 2 || parts.some((x) => !Number.isFinite(x))) throw new Error(`bad header ${name}: ${raw}`);
  return [parts[0]!, parts[1]!];
};

export function parseField(headers: Headers, buf: ArrayBuffer): FieldData {
  const [ny, nx] = pair(headers, "X-AWCI-Shape");
  const [lat0, lat1] = pair(headers, "X-AWCI-Lats");
  const [lon0, lon1] = pair(headers, "X-AWCI-Lons");
  const values = new Float32Array(buf); // little-endian on every supported browser platform
  if (values.length !== ny * nx) throw new Error(`field size ${values.length} != ${ny}x${nx}`);
  return { values, ny, nx, lat0, lat1, lon0, lon1, unit: headers.get("X-AWCI-Unit") ?? "" };
}

export async function getField(params: Params, signal?: AbortSignal): Promise<FieldData> {
  const r = await fetch(`${API_BASE}/field${query({ ...params, format: "f32" })}`, { signal });
  if (!r.ok) return fail(r);
  return parseField(r.headers, await r.arrayBuffer());
}
```

```ts
// src/state/view.ts
import { useCallback, useEffect, useState } from "react";
import type { Domain, Meta, RunInfo } from "../api/types";
import { LAYER_DEFS, type LayerDef } from "../map/layers";

export interface ViewState {
  domain?: string; run?: string; step?: number; level?: number; layer: string;
  lat?: number; lon?: number; ov: string[]; panel?: string;
}
export interface Resolved { domain: string; run: string; step: number; level: number; layer: string }

const NAME = /^[a-z0-9_]{1,64}$/;
const OVERLAY = /^[a-z0-9_]+:[a-z0-9_]+$/;
const num = (s: string | null) => (s !== null && s.trim() !== "" && Number.isFinite(Number(s)) ? Number(s) : undefined);

export function parseView(search: string): ViewState {
  const q = new URLSearchParams(search);
  const text = (k: string, re: RegExp) => { const v = q.get(k); return v && re.test(v) ? v : undefined; };
  const lat = num(q.get("lat"));
  const lon = num(q.get("lon"));
  return {
    domain: text("domain", NAME), run: text("run", /^\d{10}$/), step: num(q.get("step")), level: num(q.get("level")),
    layer: text("layer", NAME) ?? "awci",
    lat: lat !== undefined && Math.abs(lat) <= 90 ? lat : undefined,
    lon: lon !== undefined && Math.abs(lon) <= 180 ? lon : undefined,
    ov: (q.get("ov") ?? "").split(",").filter((o) => OVERLAY.test(o)), panel: text("panel", NAME),
  };
}

export function serializeView(v: ViewState): string {
  const q = new URLSearchParams();
  const set = (k: string, val: string | number | undefined) => { if (val !== undefined && val !== "") q.set(k, String(val)); };
  set("domain", v.domain); set("run", v.run); set("step", v.step); set("level", v.level); set("layer", v.layer);
  set("lat", v.lat); set("lon", v.lon); set("ov", v.ov.join(",")); set("panel", v.panel);
  return `?${q.toString()}`;
}

const validSteps = (m: Meta) => m.steps.filter((s) => !m.missing_steps.includes(s));

export function nextStep(m: Meta, step: number, dir: 1 | -1): number {
  const ok = validSteps(m);
  const candidates = dir > 0 ? ok.filter((s) => s > step) : ok.filter((s) => s < step).reverse();
  return candidates[0] ?? step;
}

/** dir = +1 moves up (lower pressure). */
export function nextLevel(m: Meta, level: number, dir: 1 | -1): number {
  const sorted = [...m.levels_hpa].sort((a, b) => b - a);
  const i = sorted.indexOf(level);
  return sorted[Math.min(sorted.length - 1, Math.max(0, i + dir))] ?? level;
}

export function availableLayers(m: Meta): LayerDef[] {
  const present = new Set([...m.level_layers, ...m.surface_layers]);
  return LAYER_DEFS.filter((d) => present.has(d.id));
}

export function resolveView(v: ViewState, domains: Domain[], runs: RunInfo[], meta: Meta | undefined,
                            now: Date): Resolved | null {
  const domain = domains.find((d) => d.name === v.domain)?.name ?? domains.find((d) => d.default)?.name ?? domains[0]?.name;
  const usable = runs.filter((r) => r.status !== "failed");
  const run = usable.find((r) => r.run === v.run)?.run ?? usable[0]?.run;
  if (!domain || !run || !meta) return null;
  const ok = validSteps(meta);
  let step = v.step !== undefined && ok.includes(v.step) ? v.step : undefined;
  if (step === undefined) {
    const t = now.getTime();
    step = ok.reduce((best, s) => {
      const d = (x: number) => Math.abs(new Date(meta.valid_times[meta.steps.indexOf(x)]!).getTime() - t);
      return d(s) < d(best) ? s : best;
    }, ok[0]!);
  }
  const level = v.level !== undefined && meta.levels_hpa.includes(v.level) ? v.level
    : meta.levels_hpa.includes(300) ? 300 : meta.levels_hpa[0]!;
  const layer = availableLayers(meta).some((d) => d.id === v.layer) ? v.layer : "awci";
  return { domain, run, step, level, layer };
}

export function useViewState(): [ViewState, (patch: Partial<ViewState>) => void] {
  const [view, setView] = useState<ViewState>(() => parseView(window.location.search));
  useEffect(() => {
    const onPop = () => setView(parseView(window.location.search));
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);
  const update = useCallback((patch: Partial<ViewState>) => {
    setView((old) => {
      const next = { ...old, ...patch };
      window.history.replaceState(null, "", serializeView(next));
      return next;
    });
  }, []);
  return [view, update];
}
```

  - `hooks.ts` : un `useQuery` par route, clé `[route, …params]`, `enabled` quand les paramètres sont connus ; `staleTime: Infinity` pour tout ce qui dépend d'un run (cubes immuables), `refetchInterval: 300_000` pour `/runs`, `staleTime: 60_000` pour `/wms/times` ; `useField` utilise `getField` et `placeholderData: keepPreviousData` (pas de clignotement), plus un préchargement `queryClient.prefetchQuery` des échéances voisines (±1 valide).
  - `types.ts` : interfaces calquées sur les réponses réelles (vérifiées contre le cube de la fixture en Task 13).
- [ ] **Step 4:** PASS ; lint, build. **Step 5:** commit `feat(awci-web): typed API client, f32 field decoding, URL view state`.

---

### Task 6: Carte — fond Natural Earth, champ rééchantillonné en Mercator, hachures, lignes de courant, légende

**Files:** Create `tools/awci/make_basemap.py`, `web/awci/public/basemap/{land,coastline,borders}.geojson` + `NOTICE.md`, `src/map/{fieldRaster.ts,streamlines.ts,style.ts,MapView.tsx,Legend.tsx}`, tests `src/map/fieldRaster.test.ts`, `src/map/streamlines.test.ts`, `src/map/style.test.ts`.

**Interfaces:**
- `fieldRaster.ts` : `Grid`, `mercY(lat)`, `invMercY(y)`, `gridEdges(g)`, `mercatorRowIndex(g, outRows)`, `renderField(g, color, cellPx?) -> RasterImage` (`data`, `width`, `height`, `coordinates` coins NO, NE, SE, SO).
- `streamlines.ts` : `WindGrid`, `sampleWind(g, lat, lon)`, `traceStreamline(g, lat, lon, dtS, maxSteps)`, `streamlineFeatures(g, spacingDeg, dtS?, maxSteps?)`.
- `style.ts` : `baseStyle(bounds) -> StyleSpecification` (fond, terres, côtes, frontières, graticule 5°), `graticule(bounds, stepDeg)`, `wmsTileUrl(layer, time)`.
- `MapView` props : `field`, `def`, `awciBounds`, `wind`, `overlays: { layer, time, opacity }[]`, `point`, `onPick(lat, lon)`, `domain`, `opacity`.

- [ ] **Step 1:** `tools/awci/make_basemap.py` : télécharge les GeoJSON Natural Earth 1:50m (`ne_50m_land`, `ne_50m_coastline`, `ne_50m_admin_0_boundary_lines_land`, dépôt `nvkelso/natural-earth-vector`), les découpe à l'emprise de **tous** les domaines configurés + 10° (shapely `clip_by_rect`), arrondit les coordonnées à 3 décimales, écrit `web/awci/public/basemap/*.geojson` et `NOTICE.md` (domaine public, source, date). Taille cible < 1,5 Mo au total.
- [ ] **Step 2: tests (échouent)**

```ts
// src/map/fieldRaster.test.ts
import { gridEdges, invMercY, mercY, mercatorRowIndex, renderField, type Grid } from "./fieldRaster";

const ny = 121, nx = 3;
const grid: Grid = { values: new Float32Array(ny * nx).fill(1), ny, nx, lat0: 15, lat1: 45, lon0: 0, lon1: 0.5 };

test("rows are resampled uniformly in Mercator y, not in latitude", () => {
  const rows = mercatorRowIndex(grid, 400);
  expect(rows[0]).toBe(ny - 1);
  expect(rows[399]).toBe(0);
  const e = gridEdges(grid);
  const midLat = invMercY((mercY(e.north) + mercY(e.south)) / 2);
  expect(rows[200]).toBe(Math.round((midLat - grid.lat0) / e.dy));
  expect(midLat).toBeLessThan(30); // Mercator mid-y lies south of the arithmetic mid-latitude
  expect(midLat).toBeGreaterThan(29);
});
test("NaN cells are hatched, null colours transparent, values coloured", () => {
  const g: Grid = { values: new Float32Array([Number.NaN, 0, 1, 1]), ny: 2, nx: 2, lat0: 0, lat1: 1, lon0: 0, lon1: 1 };
  const img = renderField(g, (v) => (v > 0 ? [255, 0, 0, 255] : null), 6);
  const alpha = (x: number, y: number) => img.data[(y * img.width + x) * 4 + 3];
  const bottom = img.height - 1; // southern row = lat index 0: [NaN, 0]
  const nanAlphas = Array.from({ length: 6 }, (_, x) => alpha(x, bottom));
  expect(nanAlphas.some((a) => a! > 0) && nanAlphas.some((a) => a === 0)).toBe(true);
  expect(alpha(8, bottom)).toBe(0);
  expect(alpha(8, 0)).toBe(255);
  expect(img.coordinates[0]).toEqual([-0.5, 1.5]);
});
```

```ts
// src/map/streamlines.test.ts
import { traceStreamline, type WindGrid } from "./streamlines";

const ny = 11, nx = 11;
const wind = (u: number, v: number): WindGrid => ({ u: new Float32Array(ny * nx).fill(u), v: new Float32Array(ny * nx).fill(v),
  ny, nx, lat0: 30, lat1: 40, lon0: 0, lon1: 10 });

test("uniform westerly: constant latitude, spherical metric step", () => {
  const pts = traceStreamline(wind(10, 0), 35, 2, 3600, 5);
  expect(pts.length).toBe(6);
  for (const [, lat] of pts) expect(lat).toBeCloseTo(35, 9);
  const dlon = (10 * 3600) / (6371000 * Math.cos((35 * Math.PI) / 180)) * (180 / Math.PI);
  expect(pts[1]![0] - pts[0]![0]).toBeCloseTo(dlon, 6);
});
test("stops at the domain edge and in calm air", () => {
  expect(traceStreamline(wind(10, 0), 35, 9.9, 3600, 50).length).toBeLessThan(5);
  expect(traceStreamline(wind(0.1, 0), 35, 5, 3600, 50).length).toBe(1);
});
```

```ts
// src/map/style.test.ts
import { graticule, wmsTileUrl } from "./style";

test("graticule every 5 degrees inside the bounds", () => {
  const lines = graticule({ west: -20, south: 15, east: 40, north: 45 }, 5).features;
  expect(lines.length).toBe(13 + 7);
});
test("WMS tile URL uses the relay, an explicit time and the MapLibre bbox token", () => {
  expect(wmsTileUrl("mtg_fd:ir105_hrfi", "2026-09-25T18:50:00Z")).toBe(
    "/api/v1/awci/wms?layer=mtg_fd%3Air105_hrfi&time=2026-09-25T18%3A50%3A00Z&width=256&height=256&bbox={bbox-epsg-3857}");
});
```

- [ ] **Step 3:** FAIL. **Step 4: implémentation**

```ts
// src/map/fieldRaster.ts
import type { Rgba } from "./layers";
import { HATCH } from "../theme/palette";

export interface Grid { values: Float32Array; ny: number; nx: number; lat0: number; lat1: number; lon0: number; lon1: number }
export interface RasterImage {
  data: Uint8ClampedArray; width: number; height: number;
  coordinates: [[number, number], [number, number], [number, number], [number, number]];
}
const RAD = Math.PI / 180;
export const mercY = (lat: number) => Math.log(Math.tan(Math.PI / 4 + (lat * RAD) / 2));
export const invMercY = (y: number) => (2 * Math.atan(Math.exp(y)) - Math.PI / 2) / RAD;

export function gridEdges(g: Grid) {
  if (g.ny < 2 || g.nx < 2) throw new Error("grid needs at least 2x2 cells");
  const dy = (g.lat1 - g.lat0) / (g.ny - 1);
  const dx = (g.lon1 - g.lon0) / (g.nx - 1);
  return { dy, dx, south: g.lat0 - dy / 2, north: g.lat1 + dy / 2, west: g.lon0 - dx / 2, east: g.lon1 + dx / 2 };
}

/** Nearest grid row (latitude-ascending index) of each output row, rows uniform in Mercator y from north to south. */
export function mercatorRowIndex(g: Grid, outRows: number): Int32Array {
  const e = gridEdges(g);
  const yN = mercY(e.north);
  const yS = mercY(e.south);
  const idx = new Int32Array(outRows);
  for (let r = 0; r < outRows; r++) {
    const lat = invMercY(yN + ((r + 0.5) / outRows) * (yS - yN));
    idx[r] = Math.min(g.ny - 1, Math.max(0, Math.round((lat - g.lat0) / e.dy)));
  }
  return idx;
}

/** Nearest-cell raster (no value invented between grid points), NaN hatched, in the map's Mercator geometry. */
export function renderField(g: Grid, color: (v: number) => Rgba | null, cellPx = 4): RasterImage {
  const e = gridEdges(g);
  const width = g.nx * cellPx;
  const height = Math.max(1, Math.round(((mercY(e.north) - mercY(e.south)) / (e.dx * RAD)) * cellPx));
  const cells = new Uint8ClampedArray(g.ny * g.nx * 4);
  const nan = new Uint8Array(g.ny * g.nx);
  for (let i = 0; i < g.values.length; i++) {
    const v = g.values[i]!;
    if (Number.isNaN(v)) { nan[i] = 1; continue; }
    const c = color(v);
    if (c) cells.set(c, i * 4);
  }
  const rows = mercatorRowIndex(g, height);
  const data = new Uint8ClampedArray(width * height * 4);
  for (let r = 0; r < height; r++) {
    const base = rows[r]! * g.nx;
    for (let x = 0; x < width; x++) {
      const cell = base + Math.floor(x / cellPx);
      const o = (r * width + x) * 4;
      if (nan[cell]) { if ((x + r) % 6 < 2) data.set(HATCH, o); } else data.set(cells.subarray(cell * 4, cell * 4 + 4), o);
    }
  }
  return { data, width, height, coordinates: [[e.west, e.north], [e.east, e.north], [e.east, e.south], [e.west, e.south]] };
}
```

```ts
// src/map/streamlines.ts
/** Streamlines of the real level wind: RK2 (midpoint) on a spherical Earth, bilinear sampling of the grid wind. */
export interface WindGrid { u: Float32Array; v: Float32Array; ny: number; nx: number; lat0: number; lat1: number; lon0: number; lon1: number }
export interface LineFeature { type: "Feature"; properties: { speed: number }; geometry: { type: "LineString"; coordinates: [number, number][] } }
const R = 6371000;
const RAD = Math.PI / 180;

export function sampleWind(g: WindGrid, lat: number, lon: number): [number, number] | null {
  const fy = ((lat - g.lat0) / (g.lat1 - g.lat0)) * (g.ny - 1);
  const fx = ((lon - g.lon0) / (g.lon1 - g.lon0)) * (g.nx - 1);
  if (!(fy >= 0 && fx >= 0 && fy <= g.ny - 1 && fx <= g.nx - 1)) return null;
  const y0 = Math.min(Math.floor(fy), g.ny - 2);
  const x0 = Math.min(Math.floor(fx), g.nx - 2);
  const ty = fy - y0;
  const tx = fx - x0;
  const bil = (a: Float32Array) => {
    const at = (y: number, x: number) => a[y * g.nx + x]!;
    return (1 - ty) * ((1 - tx) * at(y0, x0) + tx * at(y0, x0 + 1)) + ty * ((1 - tx) * at(y0 + 1, x0) + tx * at(y0 + 1, x0 + 1));
  };
  const u = bil(g.u);
  const v = bil(g.v);
  return Number.isFinite(u) && Number.isFinite(v) ? [u, v] : null;
}

function rate(g: WindGrid, lat: number, lon: number): [number, number] | null {
  const w = sampleWind(g, lat, lon);
  return w ? [w[1] / R / RAD, w[0] / (R * Math.cos(lat * RAD)) / RAD] : null; // dlat/dt, dlon/dt in deg/s
}

export function traceStreamline(g: WindGrid, lat: number, lon: number, dtS: number, maxSteps: number,
                                minSpeed = 0.5): [number, number][] {
  const pts: [number, number][] = [[lon, lat]];
  for (let i = 0; i < maxSteps; i++) {
    const w = sampleWind(g, lat, lon);
    if (!w || Math.hypot(w[0], w[1]) < minSpeed) break;
    const k1 = rate(g, lat, lon)!;
    const mid = rate(g, lat + (k1[0] * dtS) / 2, lon + (k1[1] * dtS) / 2);
    if (!mid) break;
    lat += mid[0] * dtS;
    lon += mid[1] * dtS;
    pts.push([lon, lat]);
  }
  return pts;
}

export function streamlineFeatures(g: WindGrid, spacingDeg: number, dtS = 1800, maxSteps = 24) {
  const features: LineFeature[] = [];
  for (let lat = g.lat0 + spacingDeg / 2; lat < g.lat1; lat += spacingDeg) {
    for (let lon = g.lon0 + spacingDeg / 2; lon < g.lon1; lon += spacingDeg) {
      const pts = traceStreamline(g, lat, lon, dtS, maxSteps);
      const w = sampleWind(g, lat, lon);
      if (pts.length >= 3 && w) features.push({ type: "Feature", properties: { speed: Math.hypot(w[0], w[1]) },
        geometry: { type: "LineString", coordinates: pts } });
    }
  }
  return { type: "FeatureCollection" as const, features };
}
```

  - `style.ts` : `baseStyle` renvoie un style MapLibre v8 sans tuiles externes : `background` `#0b1220` (mer) ; sources GeoJSON `/basemap/land.geojson` (remplissage `#141d31`), `coastline` (ligne `#3a4a6b`, 0,8 px), `borders` (ligne `#56617a`, 0,6 px, pointillée) ; source `graticule` (générée, ligne `rgba(255,255,255,0.06)`). `wmsTileUrl(layer, time)` construit `…/wms?layer=…&time=…&width=256&height=256&bbox={bbox-epsg-3857}` (le jeton `{bbox-epsg-3857}` n'est pas encodé).
  - `MapView.tsx` :
    - carte créée une fois (`maplibregl.Map`, `bounds` = domaine, `attributionControl` compact avec « © ECMWF CC-BY-4.0 · Natural Earth » et « © EUMETSAT » quand un overlay est actif) ;
    - source `field` de type `image` (canevas via `renderField` → `ImageData` → `canvas.toDataURL()` → `updateImage({ url, coordinates })`), couche raster `raster-resampling: "nearest"`, `raster-opacity` = `opacity` ; genre −2 → `NaN` avant rendu ;
    - source `streamlines` (GeoJSON, recalculée à `moveend` avec un espacement 3° / 1,5° / 0,75° selon le zoom) couche ligne blanche 60 % ;
    - overlays : une source raster par couche WMS (`tiles: [wmsTileUrl(layer, time)]`, `tileSize: 256`), insérées sous `field` ;
    - point choisi : source GeoJSON + cercle ; `click` → `onPick(lat, lon)` ;
    - clavier : la carte reste focalisable (`tabIndex=0`, `aria-label`).
  - `Legend.tsx` : classes AWCI (libellés du registre), codes (libellés), continue (dégradé + min/max dans l'unité affichée), genre (3 familles + « clair : transparent »), et **toujours** une entrée hachurée « sans donnée / sous le relief / indéterminé ».
- [ ] **Step 5:** PASS ; lint, build. **Step 6:** commit `feat(awci-web): map with embedded Natural Earth basemap, Mercator-resampled field, hatching, streamlines, legend`.

---

### Task 7: Coque — barre haute, navigation, échéances et niveaux, états, clavier, mise en page

**Files:** Create `src/panels/{TopBar.tsx,SideNav.tsx,TimeBar.tsx,DataStatus.tsx,StateViews.tsx}`, `src/App.tsx` (remplacé), `src/App.css`, tests `src/panels/TimeBar.test.tsx`, `src/panels/DataStatus.test.tsx`, `src/App.test.tsx`.

**Interfaces:** `App` assemble : `useViewState` + `resolveView` ; `TopBar` (domaine, run, validité ± pas, « Maintenant », niveau, `DataStatus`, horloge UTC) ; `SideNav` (groupes de couches filtrés par `availableLayers`, overlays, sections SP3–SP6 **absentes**) ; `TimeBar` (curseur des échéances, manquantes grisées et non focalisables, ▶/⏸ 1 pas/s, `aria-valuetext` = validité) ; raccourcis ←/→, ↑/↓, `L`, Espace, Échap ; `StateViews` (squelettes, « Aucun run ingéré » + commande d'ingestion, erreurs par zone, bandeau run partiel, badge « Run ancien » > 18 h).

- [ ] **Step 1: tests (échouent)**

```tsx
// src/panels/TimeBar.test.tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TimeBar } from "./TimeBar";

const meta = { steps: [0, 3, 6], missing_steps: [3], valid_times: ["2026-09-25T12:00:00+00:00",
  "2026-09-25T15:00:00+00:00", "2026-09-25T18:00:00+00:00"] } as never;

test("missing steps are disabled and announced", async () => {
  const onStep = vi.fn();
  render(<TimeBar meta={meta} step={0} onStep={onStep} />);
  const missing = screen.getByRole("button", { name: /\+3 h.*manquante/i });
  expect(missing).toBeDisabled();
  await userEvent.click(screen.getByRole("button", { name: /\+6 h/ }));
  expect(onStep).toHaveBeenCalledWith(6);
});
```

```tsx
// src/panels/DataStatus.test.tsx
import { render, screen } from "@testing-library/react";
import { DataStatus } from "./DataStatus";

test("partial and stale runs are flagged with text, not colour only", () => {
  render(<DataStatus run={{ run: "2026092500", run_time: "2026-09-25T00:00:00+00:00", status: "partial",
    steps: [0, 3], missing_steps: [3], ingested_at: "2026-09-25T08:10:00+00:00" } as never}
    cloudStatus="degraded" now={new Date("2026-09-25T20:00:00Z")} />);
  expect(screen.getByText(/partiel/i)).toBeInTheDocument();
  expect(screen.getByText(/run ancien/i)).toBeInTheDocument();
  expect(screen.getByText(/nuages : cohérence dégradée/i)).toBeInTheDocument();
});
```

```tsx
// src/App.test.tsx : fetch simulé (réponses JSON des routes) -> état « Aucun run ingéré » quand /runs renvoie []
```

- [ ] **Step 2:** FAIL. **Step 3:** implémenter (grille CSS : `grid-template-areas: "top top" "nav main"` ; `main` = KPI / (carte | colonne droite) / rangée basse ; `@media (max-width: 1023px)` : navigation repliée en tiroir, carte + inspecteur empilés, rangée basse repliée ; `@media (min-width: 2200px)` : largeur de colonne droite plafonnée, textes non agrandis). **Step 4:** PASS ; lint, build. **Step 5:** commit `feat(awci-web): app shell, time bar with missing steps, data status, keyboard, states, responsive layout`.

---

### Task 8: Rangée KPI, situation actuelle, accord des modèles

**Files:** Create `src/panels/{KpiRow.tsx,Situation.tsx,ModelAgreement.tsx}`, `src/charts/Gauge.tsx`, test `src/panels/KpiRow.test.tsx`.

**Interfaces:** `KpiRow({ summary, onSelectLayer })` : jauge AWCI P95 + classe (texte + couleur) ; cartes Turbulence (`turbulence_area_pct`), Convection (`convection_area_pct` + `mucape_max`), Givrage, Cisaillement (`shear_p95` ×10⁻³ s⁻¹), Plafond < 1000 ft (`low_ceiling_area_pct`), **Cb** (`cb_area_pct`) ; chaque carte : valeur, unité, badge statut (icône Lucide + texte), cliquable → `onSelectLayer(id)` ; valeur `null` → « — » + « non disponible pour ce run ». `Situation` : classe du P95, dangers triés par badge, altitude principale (niveau au P95 max de `awci_p95_by_level`, en FL), validité. `ModelAgreement` : « Non disponible — mono-modèle (ECMWF IFS). Ensemble ECMWF prévu en SP5, GFS en SP6. »

- [ ] **Step 1: test (échoue)**

```tsx
test("KPI cards show value, unit, text badge and select their layer", async () => {
  const onSelect = vi.fn();
  render(<KpiRow summary={{ awci_p95: 57.2, awci_class: "Moderate", turbulence_area_pct: 18.4, convection_area_pct: 2,
    mucape_max: 1800, icing_area_pct: null, shear_p95: 0.006, heavy_precip_area_pct: 0, low_ceiling_area_pct: 1.2,
    cb_area_pct: 13, valid_cells_pct: 99, badges: { turbulence_area_pct: "serious", shear_p95: "attention",
    icing_area_pct: null, convection_area_pct: "ok", cb_area_pct: "attention", low_ceiling_area_pct: "ok",
    heavy_precip_area_pct: "ok" }, awci_p95_by_level: [] } as never} onSelectLayer={onSelect} />);
  expect(screen.getByText("18,4 %")).toBeInTheDocument();
  expect(screen.getAllByText(/sérieux/i).length).toBeGreaterThan(0);
  expect(screen.getByText(/givrage/i).closest("button")).toHaveTextContent("—");
  await userEvent.click(screen.getByRole("button", { name: /turbulence/i }));
  expect(onSelect).toHaveBeenCalledWith("cat_category");
});
```

- [ ] **Step 2–4:** FAIL → implémenter → PASS. **Step 5:** commit `feat(awci-web): KPI row, current situation, explicit single-model agreement`.

---

### Task 9: Inspecteur de point et graphiques (évolution, profil AWCI, profil atmosphérique)

**Files:** Create `src/panels/{Inspector.tsx,TimeEvolution.tsx,AwciProfile.tsx,AtmoProfile.tsx}`, `src/charts/{LineChart.tsx,DataTable.tsx}`, tests `src/panels/Inspector.test.tsx`, `src/charts/LineChart.test.tsx`.

**Interfaces:**
- `Inspector({ point, layerDefs, registry })` : AWCI + classe ; décomposition en barres horizontales triées (points AWCI) ; « calculé sur N % des poids » (`present_weight`) ; `missing_inputs` listés ; valeurs des couches du niveau et de surface avec unités ; statut scientifique de chaque grandeur ; provenance (run, échéance, validité, © ECMWF) ; niveau sous le relief (`awci` `null` et `level_layers.gh` `null`) → « Sous le relief à ce niveau : pas de donnée ».
- `LineChart({ series, xCurrent, yLabel, format })` : SVG, un seul axe Y, traits fins, légende dès 2 séries, survol → réticule + infobulle (valeurs de toutes les séries), `<details>` « Voir les données » avec `DataTable`.
- `TimeEvolution` : AWCI au point (`/timeseries`) et P95 domaine (`/summary/series`), échéance courante marquée.
- `AwciProfile` : barres AWCI par niveau (FL + hPa), classe en texte, « sous le sol ».
- `AtmoProfile` : T et Td (°C) en fonction de l'altitude géopotentielle (km), flèches de vent par niveau (direction météorologique), bande de fraction nuageuse (octas) en marge, niveaux sous le relief omis.

- [ ] **Step 1: tests (échouent)**

```tsx
test("inspector explains the composite and flags missing inputs", () => {
  render(<Inspector point={{ lat: 36.75, lon: 3, level_hpa: 300, flight_level: 301, awci: 42.1, awci_level: "Moderate",
    modules: { dynamic: 0.5, thermodynamic: 0.4, convective: null, microphysical: 0.1, topographic: 0.2 },
    missing_inputs: ["convective", "temporal", "confidence"], present_weight: 0.7,
    decomposition: { dynamic: 12.5, thermodynamic: 14.3, microphysical: 2.1, topographic: 2.9 },
    level_layers: { t: 230.1, gh: 9400 }, surface_layers: { mucape: 0 }, scientific_status: { awci: "HYPOTHESIS" },
    provenance: { run: "2026092512", step: 24, valid_time: "2026-09-26T12:00:00+00:00", attribution: "© ECMWF, CC-BY-4.0" } } as never}
    registry={undefined} />);
  expect(screen.getByText(/calculé sur 70 % des poids/i)).toBeInTheDocument();
  expect(screen.getByText(/convective/i)).toBeInTheDocument();
  expect(screen.getByText(/HYPOTHESIS/)).toBeInTheDocument();
  expect(screen.getByText(/© ECMWF/)).toBeInTheDocument();
});

test("line chart exposes its data as a table", () => {
  render(<LineChart yLabel="AWCI" series={[{ id: "p", label: "Point", color: "#3987e5",
    points: [{ x: 0, y: 10 }, { x: 3600000, y: null }] }]} format={(v) => String(v)} />);
  expect(screen.getByRole("table")).toBeInTheDocument();
  expect(screen.getByText("—")).toBeInTheDocument(); // missing value stays visible as missing
});
```

- [ ] **Step 2–4:** FAIL → implémenter → PASS. **Step 5:** commit `feat(awci-web): point inspector, time evolution, AWCI and atmospheric profiles`.

---

### Task 10: Panneau Nuages

**Files:** Create `src/panels/{CloudsPanel.tsx,GenusTimeline.tsx}`, test `src/panels/CloudsPanel.test.tsx`.

**Interfaces:** `CloudsPanel({ clouds, series, currentStep })` :
- colonne verticale en FL (0 → FL450) : une bande par couche (base FL → sommet FL, ± demi-intervalle en trait fin), texte « genre + espèces + octas (FEW/SCT/BKN/OVC) » ; couche convective en hachures avec « Cb/TCU, sommet m et ft » ; ligne du plafond OACI ; repères d'étage `etage_bounds_fl` (σ ECMWF) ; étages OMM de référence en texte discret ;
- ligne « MODEL BKN030 OVC080 CB » en police à chasse fixe ;
- T_e (°C), condensat colonne, `tcc` IFS vs couverture diagnostiquée, biais, statut nuageux du run ;
- `GenusTimeline` : une rangée par étage, une case par échéance (famille de couleur + abréviation du genre en texte), échéance courante marquée ;
- libellé permanent « Genre probable — diagnostic modèle, statut HYPOTHESIS » ;
- run antérieur à SP1C (`/clouds` 404) → « Diagnostic nuageux non disponible pour ce run (ingéré avant SP1C). »

- [ ] **Step 1: test (échoue)**

```tsx
test("clouds panel lists layers with genus, oktas and the model METAR line", () => {
  render(<CloudsPanel currentStep={24} series={undefined} clouds={{ lat: 36.75, lon: 3, elevation_m: 20,
    layers: [{ kind: "layer", genus: "Sc", etage: "low", species: ["castellanus"], base_agl_m: 900, base_ft: 2952,
      base_fl: 30, base_uncertainty_m: 300, top_amsl_m: 1500, top_fl: 50, oktas: 6, amount: "BKN" },
      { kind: "convective", genus: "Cb", etage: null, species: ["capillatus"], base_agl_m: 800, base_ft: 2624,
        base_uncertainty_m: null, top_amsl_m: 12000, top_fl: null, oktas: null, amount: null }],
    metar: "MODEL ///026CB BKN029", ceiling_m: 900, ceiling_ft: 2952,
    convective: { class: 4, label: "Cb capillatus", top_m: 12000, top_temp_k: 216 }, cloud_top_teff_k: 212,
    column_condensate: 1.2, tcc: 0.9, cloud_cover_bias: -0.05, etage_bounds_fl: { low_mid: 62, mid_high: 216 },
    run_cloud_status: "ok", scientific_status: { cloud_genus: "HYPOTHESIS" } } as never} />);
  expect(screen.getByText("MODEL ///026CB BKN029")).toBeInTheDocument();
  expect(screen.getByText(/Sc castellanus/)).toBeInTheDocument();
  expect(screen.getByText(/BKN/)).toBeInTheDocument();
  expect(screen.getByText(/diagnostic modèle/i)).toBeInTheDocument();
});
```

- [ ] **Step 2–4:** FAIL → implémenter → PASS. **Step 5:** commit `feat(awci-web): clouds panel (layers by etage, genus timeline, model METAR line)`.

---

### Task 11: Overlays d'observation et comparaison modèle / observation

**Files:** Create `src/panels/{OverlayPanel.tsx,ObservedBadge.tsx,CompareControl.tsx}`, test `src/panels/OverlayPanel.test.tsx`.

**Interfaces:** `OverlayPanel({ layers (useWmsLayers), active, onToggle, opacity })` : couches groupées (satellite, nuages, convection, cendres) ; à l'activation, `useWmsTimes(layer, 1)` → heure explicite ; `ObservedBadge` « Observé HH:MM UTC · il y a N min · © EUMETSAT » sur la carte ; erreur 502 → « EUMETView indisponible » et overlay désactivé, prévision intacte. `CompareControl` : fondu (curseur 0–100 %) entre `cloud_top_teff_k` (prévision, validité affichée) et `mtg_fd:ir105_hrfi` (observé, heure affichée), les deux heures côte à côte.

- [ ] **Step 1: test (échoue)** — overlay en erreur : `useWmsTimes` simulé en échec → texte « EUMETView indisponible », case décochée, bouton de nouvel essai.
- [ ] **Step 2–4:** FAIL → implémenter → PASS. **Step 5:** commit `feat(awci-web): EUMETView overlays with observed time, model/observation fade compare`.

---

### Task 12: Page API et registre, vues enregistrées, derniers runs, thème clair

**Files:** Create `src/panels/{RegistryPage.tsx,SavedViews.tsx,LatestRuns.tsx}`, `src/state/savedViews.ts`, tests `src/state/savedViews.test.ts`, `src/panels/RegistryPage.test.tsx`.

**Interfaces:** `RegistryPage` (panneau `panel=api`) : tableau des couches (`/registry` : nom, unité, équation, source, statut), classes AWCI, seuils de synthèse et profil nuageux, lien vers `/docs` (OpenAPI de FastAPI) ; `savedViews.ts` : `loadViews()`, `saveView(name, search)`, `deleteView(name)` sur `localStorage` (`awci.savedViews`), **chaque accès dans try/catch** (navigation privée) ; `LatestRuns` : `/runs` (run, statut, échéances manquantes, `ingested_at`) ; thème clair : `[data-theme="light"]` dans `tokens.css`, palettes vérifiées avec `validate_palette.js --mode light --surface <surface claire>` (résultat consigné dans le fichier), bascule dans la barre haute.

- [ ] **Step 1: tests (échouent)** — `saveView` puis `loadViews` restitue la vue ; `localStorage` qui lève une exception → `loadViews()` renvoie `[]` sans erreur ; `RegistryPage` affiche une ligne par couche et le statut en texte.
- [ ] **Step 2–4:** FAIL → implémenter → PASS. **Step 5:** commit `feat(awci-web): registry/API page, saved views, latest runs, validated light theme`.

---

### Task 13: Bout en bout, accessibilité, captures, mesures, documentation

**Files:** Create `web/awci/playwright.config.ts`, `web/awci/e2e/{flows.spec.ts,a11y.spec.ts,layout.spec.ts}` ; Modify `docs/awci/AWCI_WEB_SP1.md` (section SP2), `CHANGELOG.md`, spec SP2 (écarts).

**Interfaces:** `playwright.config.ts` : `webServer` = `../../.venv/bin/python ../../tools/awci/e2e_server.py --port 8099 --data-dir <tmp>` (build préalable `npm run build`), `use.baseURL = http://127.0.0.1:8099`, Chromium de `/opt/pw-browsers` (`launchOptions.executablePath` si la version ne correspond pas).

- [ ] **Step 1: e2e (échouent avant la mise en place)**
  - parcours : chargement → carte, KPI et état des données visibles ; changement d'échéance (flèche), de niveau, de couche (AWCI → Givrage → Genre bas) ; clic au centre du domaine → inspecteur rempli, panneau Nuages rempli ; l'URL reproduit la vue (recharger = même état) ;
  - run partiel : ingestion avec l'échéance 3 manquante → bouton +3 h désactivé, → saute de 0 à la suivante disponible ;
  - clic hors domaine → message ; cellule sous le relief (fixture sèche, 1000 hPa sur l'Atlas) → « sous le relief » ;
  - overlay satellite : badge « Observé … · © EUMETSAT » ; serveur WMS hors ligne en échec → « EUMETView indisponible » ;
  - clavier : ←/→, ↑/↓, Espace, Échap ; `prefers-reduced-motion: reduce` → pas de transition ;
  - `@axe-core/playwright` : aucune violation « serious » ou « critical » ;
  - captures 900, 1440, 1920 et 2560 px : pas de défilement horizontal (`scrollWidth <= clientWidth`), zones de la maquette présentes (KPI, carte, colonne droite, rangée basse) ; captures conservées comme référence de non-régression.
- [ ] **Step 2:** faire passer ; mesurer sur le cube réel `north_africa` (run 12Z) servi par `acf-awci-web` : premier affichage complet, changement d'échéance (p95 sur 20 changements), taille du bundle (gz). Critères spec : < 3 s, < 300 ms, < 600 Ko gz.
- [ ] **Step 3:** documentation (lancement : `cd web/awci && npm ci && npm run build`, puis `acf-awci-web` sert `/` ; développement : `npm run dev` avec proxy), mesures, limites ; CHANGELOG ; écarts à la spec consignés.
- [ ] **Step 4:** suites Python + front complètes ; commit `test(awci-web): end-to-end flows, accessibility and layout checks; SP2 docs and measurements` ; push.
