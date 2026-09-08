# AWCI UI Audit

**Date:** 2026-09-03
**Context:** requested by the user's "AWCI — Master Engineering Prompt V3.0"
(§4). This document is real, based on direct source inspection and two
Explore-agent passes performed before any code in this closure — not
assumed. It documents the ACTUAL architecture of this project (Python /
PySide6 / matplotlib desktop application), not the generic React/web
architecture the master prompt's own template language describes — see
the note in §0 below.

## 0. A note on the master prompt's own tech-stack language

The master prompt is written for a generic web/React stack: `npm build`,
hooks, WebGL, ARIA. **This project has none of those** — it is a Python
desktop application (`PySide6`/Qt widgets, `matplotlib`/`cartopy` for maps
and charts). Every section below is answered against the real stack, not
against an imagined one. Where the prompt asks for something with no real
analog here (e.g. "npm build passes"), the real equivalent is named
instead (e.g. `ruff check` + `mypy` + `pytest -q`).

## 1. Architecture actuelle (real, current)

- **Language/runtime:** Python 3.12, PySide6 (Qt6 bindings), matplotlib
  (`FigureCanvasQTAgg`) + Cartopy for maps, NumPy/SciPy for the science
  layer.
- **Package root:** `src/acf/` — a single installable package (`acf`), no
  separate frontend/backend repo split. `pyproject.toml` at the repo root.
- **GUI entry points:** `src/acf/gui/` — `esoc/` (the main "ESOC" desktop
  shell), `dashboard/` (AWCI + the general ACF dashboard), `map/` (shared
  Cartopy map widgets/camera/layers).
- **Science/domain layer:** `src/acf/awci/` (the AWCI composite-index
  engine itself — `calculator.py`, `normalizer.py`, and per-diagnostic
  modules like `wind_shear.py`/`theta_e.py`/`hydrometeor_phase.py`/
  `orographic_froude.py`), `src/acf/science/` (the much larger general
  meteorological formula library AWCI draws a subset of formulas from),
  `src/acf/simulation_engine/` (`CoupledEarthSolver`, the real numerical
  model AWCI's "🔬 Real Physics" mode runs).
  Also relevant to this closure: `src/acf/models/` (real per-NWP-model
  ingestion adapters), `src/acf/core/contracts/` (the real `Dataset`/
  `Provenance`/`QualityInfo`/`VariableContract` data contract),
  `src/acf/physics_guard/` (real range/consistency/quality validation),
  `src/acf/normalization/` (real CF standard-name/unit conversion).
- **A separate FastAPI web layer also exists** (`src/acf/web/`,
  `complexity_router.py`/`datasets_router.py`) exposing some of the same
  real science over HTTP — not the UI this closure targets, mentioned
  here only because it is a second, independent real consumer of
  `AWCICalculator`/`Dataset`.
- **Tests:** `pytest` + `pytest-qt` (`qtbot` fixture) for GUI widgets,
  `ruff` for linting, `mypy` for typing — run via `.venv/bin/...`, no
  `npm`/`node` anywhere in this repository.
- **Package manager:** none in the npm sense — Python dependencies via
  `pyproject.toml`/`.venv`.
- **Build system:** none in the compiled-bundle sense — the application
  runs directly from source (`python -m acf...` / the ESOC entry point);
  "build" for verification purposes means `ruff check` + `mypy` + `pytest`.
- **Routes:** N/A (desktop app, not a router-driven SPA) — navigation is
  Qt widget/window management (`show()`/`raise_()`/dialogs), not URL
  routes.
- **State management:** plain Python instance attributes on
  `AWCIDashboard` (a `QWidget` subclass) — no Redux/Context/hooks
  equivalent exists or is needed at this scale; see
  `AWCI_INTERACTION_MATRIX.md` for the real shared-state fields.
- **Hooks:** N/A (no React) — the closest real analog is Qt's own
  signal/slot connections (`widget.clicked.connect(self._handler)`),
  used throughout.

## 2. Frontend (the real AWCI dashboard)

`src/acf/gui/dashboard/awci_dashboard.py` — `AWCIDashboard(QWidget)`, ~1250
lines. Composes ~14 sub-widgets from the same package (`awci_map_panel.py`,
`awci_cross_section.py`, `awci_radar.py`, `awci_risk_summary.py`,
`awci_route_chart.py`, `awci_stats_bar.py`, `awci_footer.py`,
`awci_component_detail.py`, `awci_alerts_panel.py`, `awci_messages_panel.py`,
`awci_volume_3d.py`, `awci_gauge.py`, `awci_timeline.py`,
`awci_vertical_profile.py`), plus `awci_synthetic_field.py` (the demo-mode
data generator) and `awci_colors.py`/`acf/gui/theme_tokens.py` (the shared
visual design system). Full component-by-component detail:
`AWCI_COMPONENT_INVENTORY.md`.

## 3. Backend / data layer

There is no separate "backend service" the desktop dashboard talks to over
a network for its own science — `AWCICalculator`/`CoupledEarthSolver` run
in-process. The real "backend" for this dashboard's purposes is:
- `acf.awci.calculator.AWCICalculator` — the composite AWCI score/module
  engine, a plain-dict input contract (see `AWCI_UI_AUDIT.md` §7 below).
- `acf.simulation_engine.coupled_solver.CoupledEarthSolver` — the real
  numerical atmosphere/ocean/land model "🔬 Real Physics" mode runs.
- `acf.awci.spatial_field` / `vertical_field` / `temporal_field` /
  `path_sampling` — real post-processing that samples one solver run
  into the map/cross-section/route views without re-running the solver
  per panel.
- A genuinely separate real backend does exist for live aviation data:
  `acf.aviation.icao.live_source` fetches real METAR/TAF/SIGMET from the
  public NOAA Aviation Weather Center API (`📨 Message` button).

## 4. ACF (the science/data-contract layer)

- **Real Data Contract** (`acf.core.contracts`): `Dataset` (id, source,
  model, run, forecast_reference_time, valid_time, lead_time, variable,
  unit, dimensions, coordinates, values, quality, uncertainty,
  provenance), `Provenance`, `QualityInfo` (`NOT_ASSESSED`/`PASS`/
  `WARNING`/`FAIL`), `UncertaintyInfo`, `VariableContract`
  (`from_registry()` pulls unit/valid_range from the real CF-name/
  operational-range tables below). `Dataset.from_real_field()`/
  `from_real_volume()` already bridge `compute_real_complexity_field()`/
  `compute_real_complexity_volume()` into this contract, used today by
  the certification engine (`acf.certification.engine.CertificationEngine`)
  and the FastAPI dataset router — **not yet by the AWCI dashboard**.
- **Real Model Adapter Protocol** (`acf.models.base_model.BaseWeatherModel`):
  shared `read()`/`normalize()`/`metadata()`/`coordinates()`/
  `capabilities()` methods; real adapters exist for all 6 named models —
  AROME, ALADIN, ARPEGE, WRF, ICON, OpenIFS (`src/acf/models/<model>/
  ingestion_adapter.py`).
- **Real normalization** (`acf.normalization`): `convert_unit()` (real
  MetPy/pint conversion), `cf_canonical_unit()`/`to_cf_standard_name()`
  (backed by `resources/standards/cf/cf_standard_names.json` — 9 real CF
  names — and `resources/standards/ecmwf/parameters.json` — 4 real ECMWF
  short-name mappings; a real, narrow, disclosed coverage, not a
  fabricated complete table).
- **Real validation** (`acf.physics_guard`): `PhysicsGuard.validate()`/
  `check_range()`/`check_consistency()`, `OPERATIONAL_RANGES` (9 real CF
  standard names with documented min/max bounds),
  `acf.physics_guard.variable_quality.assess_variable_quality()` — a
  real, formal per-variable status vocabulary (`VALID`/`SUSPECT`/
  `MISSING`/`INVALID`/`OUT_OF_RANGE`/`UNIT_ERROR`/`GRID_ERROR`/
  `TIME_ERROR`/`PHYSICAL_INCONSISTENCY`), already able to represent
  "missing" honestly rather than via a bare `None`.
- **The real, confirmed gap**: no code anywhere constructs a `Dataset`/
  `VariableContract` and hands it to `AWCICalculator` — every real
  caller (the dashboard included) builds `AWCICalculator`'s plain
  `dict[str, Any]` by hand. This closure adds
  `acf.awci.input_adapter` to bridge that gap (see
  `AWCI_IMPLEMENTATION_STATUS.md`).

## 5. Composants existants (résumé — détail complet dans AWCI_COMPONENT_INVENTORY.md)

Real and already built: global/regional map (heatmap, legend, layers
panel, zoom/pan, aircraft glyphs, city labels, point-information card),
vertical cross-section (heatmap + colorbar + hazard icon overlay), AWCI
components radar + clickable value list + detail dialog (formula/status/
diagnostic-registry docs/drill-down trace), stats bar (5 KPIs incl. a
half-circle confidence gauge), regional-trend sparkline, route-planning
chart (single-series + FL280/FL320 comparison), risk summary, static
recommendation banner, footer, alerts dialog, live-METAR dialog, 3D
volume view, VIEW MODE radios, header status badge.

## 6. Composants manquants (real, confirmed by this closure's own audit)

- Click-to-select a new point of interest on the map (today a hardcoded
  constant) — **built this closure**.
- Clickable risk-summary badges — **built this closure**.
- A demo-mode flight-level selector acting as a real single source of
  truth (today ~7 independent hardcoded pressure constants across
  panels in demo mode) — **built this closure**.
- A calendar/date picker beyond the existing hour slider — **not built**,
  documented in `future-improvements.md` (the mockup itself shows a
  static date string, not an interactive picker; `time_slider` already
  provides the real interactive time axis the mockup's own trend/route
  panels consume).
- A flight-level-recommendation "route optimization engine" —
  **deliberately not built** — see `AWCI_UI_AUDIT.md` §8.
- Repo-wide accessibility (ARIA-equivalent) attributes — **not built at
  scale**, documented in `future-improvements.md`.

## 7. Routes / APIs

N/A for the desktop UI (see §1). The separate FastAPI layer
(`acf.web.routers.complexity_router`/`datasets_router`) exposes
`AWCICalculator`/`Dataset.from_real_field()` over HTTP already — real,
pre-existing, unrelated to this closure's own dashboard work.

## 8. Données / moteurs scientifiques — the RouteOptimizationEngine question

The master prompt (§30) asks for a `RouteOptimizationEngine` producing a
`preferredFlightLevel`/`alternativeFlightLevel` recommendation. Before
building this, per the prompt's own §50 rule ("vérifier s'il existe déjà
dans ACF"), the codebase was searched. **Two real, deliberate stubs
already exist** and both were explicitly gutted of a fabricated
recommendation:
- `src/acf/science/query_engine.py` — the "best flight level" query
  branch returns `"recommended_flight_level": None, "is_real_data":
  False`, with a code comment recording that it used to return a
  fabricated `"FL360"` and was corrected.
- `src/acf/ai_expert/aviation_reasoning.py` —
  `AviationReasoningEngine.analyze_flight_hazards()` likewise returns
  `None`/`"NOT_ANALYZED_NO_TURBULENCE_ICING_DATA_CONNECTED"`, same real
  history.

Building a new engine that outputs a flight-level "recommendation" from
AWCI scores alone would resurrect exactly the kind of fabrication this
project's own history explicitly removed twice. **Decision: not built.**
The dashboard's existing recommendation banner (real template text from
real elevated risks + a real high-AWCI route segment, built in the
previous closure) already satisfies what the reference mockup itself
shows (a short recommendation sentence, not a scored multi-level
optimizer) — see `future-improvements.md` for how a real one could be
built later if a real scientific basis for scoring flight levels is
established.

## 9. Visualisations

All real matplotlib/Cartopy — no image placeholders anywhere for a
scientific plot. See `AWCI_COMPONENT_INVENTORY.md`.

## 10. Tests

7 dashboard-level test files under `tests/gui/test_awci_dashboard_*.py`
plus per-widget test files under `tests/test_awci_*.py` — full suite
3852/3852 green before this closure's own new work, **3883/3883 green
after** (31 new tests: 12 `test_awci_input_adapter.py`, 4
`test_awci_map_panel_point_click.py`, 15
`tests/gui/test_awci_dashboard_synchronization.py`). See
`AWCI_IMPLEMENTATION_STATUS.md` for exact coverage per component.

## 11. Problèmes (real findings from this audit — resolution noted per item)

- Flight-level state was a real single source of truth only while Real
  Physics mode was active — **resolved this closure** for demo mode via
  `flight_level_selector`/`_current_flight_level_hpa` (see
  `AWCI_INTERACTION_MATRIX.md`); Real Physics mode's own `level_slider`
  is untouched and still its own real source of truth, now kept in sync
  by the same selector rather than duplicated.
- Map clicks (aircraft, any point) and risk badges were currently inert
  — **resolved this closure** (`AWCIMapPanel.pointClicked`, `AWCIRiskSummary.rowClicked`).
- CF standard-name/unit coverage in `acf.normalization` is real but
  narrow (9 CF names, 4 ECMWF short names) — a real, disclosed limit on
  how much of a real `Dataset` the new input adapter can translate today
  (**not addressed this closure** — widening `acf.normalization`'s own
  coverage is a separate, larger task, not an AWCI-dashboard task).

## 12. Risques

- The new input adapter must never silently substitute a fabricated
  value for a variable `Dataset` doesn't carry — it must return a real
  `MISSING`/`INVALID` quality entry instead (see
  `acf.physics_guard.variable_quality`).
- Unifying flight-level state must stay bit-identical for any caller
  that doesn't touch the new selector (existing tests must keep passing
  unchanged).

## 13. Dépendances

No new third-party dependency is needed for this closure — everything
reused (`Dataset`, `PhysicsGuard`, `assess_variable_quality`,
`AWCICalculator`) already exists and is already a real dependency of
this package.

## 14. Plan de travail

See the approved plan (session plan file) and `AWCI_IMPLEMENTATION_STATUS.md`.
