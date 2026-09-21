# ACF / AWCI Architecture Gap Analysis

**Compares the actual `src/acf/` tree (surveyed 2026-09-21) against the two
reference blueprints** — [`acf_reference_architecture.md`](acf_reference_architecture.md)
and [`awci_reference_architecture.md`](awci_reference_architecture.md) — so
that any future migration work is scoped from real findings, not
assumptions. No code was changed to produce this document; it is a survey
only.

Legend: ✅ real equivalent exists (possibly under a different name/location)
· 🟡 partially covered, organized differently than the blueprint ·
❌ genuinely absent from the codebase today.

## 1. ACF — layer by layer

### L0 — Foundation

| Blueprint | Current reality |
|---|---|
| `core/{application,configuration,context,exceptions,logging,lifecycle,registry,events,plugins,dependencies,environment,version}.py` | 🟡 `src/acf/core/` exists with `application.py`, `bootstrap.py`, `config.py`, `constants.py`, `environment.py`, `exceptions.py`, `logger.py`, `metadata.py`, `parameter.py`, `parameter_registry.py`, `plugin_manager.py`, `service_manager.py`, `version.py`, `default_parameters.py`, plus a `contracts/` subpackage. Real overlap on config/exceptions/logging/environment/version/plugins; no `lifecycle.py`, `registry.py` (a generic one — `parameter_registry.py` is science-specific), `events.py`, or `context.py`. `application.py` exists but is confirmed dead code (`docs/STATUS.md`'s own NOTE: nothing constructs it; `acf-gui` boots `ACFWorkstationWindow` directly). |
| `utils/{filesystem,paths,datetime,units,validation,serialization,hashing,caching,profiling,concurrency,numerical,decorators}.py` | 🟡 `src/acf/utils/` exists with `time.py`, `paths.py`, `system.py`, `validators.py`, `files.py`. Real overlap on paths/validation/time; no dedicated `units.py` (units live in `standards/`), `serialization.py`, `hashing.py`, `caching.py`, `profiling.py`, `concurrency.py`, `numerical.py`, `decorators.py` as standalone modules. |

### L1 — Scientific formulations & standards

| Blueprint | Current reality |
|---|---|
| `science/` with 19 subdomains (`thermodynamics/`, `dynamics/`, `stability/`, `convection/`, `radiation/`, `microphysics/`, `turbulence/`, `boundary_layer/`, `clouds/`, `precipitation/`, `atmospheric_composition/`, `ocean/`, `hydrology/`, `cryosphere/`, `land_surface/`, `carbon_cycle/`, `climate/`, `diagnostics/`, `constants/`) as subpackages | 🟡 `src/acf/science/` is real and large (~60 top-level modules: `thermodynamics.py`, `dynamics.py`, `stability.py`, `cape.py`, `cin.py`, `lcl.py`, `lfc.py`, `convection` concepts inline, `radiation.py`, `boundary_layer.py`, `precipitation.py`, `moisture.py`, `wind.py`, `cyclones.py`, `climatology.py`, `synoptic.py`, plus subpackages `laws/`, `observations/`, `encyclopedia/`, `knowledge_graph/`, `parameters/`, `physics_ai/`, `clouds/`). Real, tested coverage of most physics named in the blueprint exists — but as flat modules per topic (`cape.py`) rather than per-domain subpackages (`convection/cape.py`), and several named subdomains have no dedicated home yet: `microphysics/`, `turbulence/` (only `wind_turbulence.py`), `atmospheric_composition/`, `carbon_cycle/` (see `src/acf/climate/` instead), `land_surface/` (see `src/acf/earth_physics/`), `cryosphere/`, `ocean/` (see the separate top-level `src/acf/ocean/`), `hydrology/` (see the separate top-level `src/acf/hydrology/`). |
| `parameters/` — a real structured catalog, historical inventory ~152 parametrization modules | 🟡 `src/acf/parameters/` exists (`units.py`, `categories.py`, `search.py`, `converter.py`, `aliases.py`, `hub.py`, `registry.py`, `parameter.py`, `index.py`, `catalog.py`, `validator.py`) — a real registry/catalog engine, but organized as one flat parameter-management layer, not the blueprint's per-domain (`atmosphere/ocean/land/cryosphere/radiation/microphysics/turbulence/convection/chemistry/parameterizations/`) subpackage split. No verified count of "152 parametrization modules" exists in the current tree. |
| `standards/` | ✅ `src/acf/standards/` is real: `wmo_tables.py`, `noaa_parameters.py`, `manager.py`, `ecmwf_parameters.py`, `cf_standard_names.py`, `hub.py`, `grib2_tables.py`, plus an `ecmwf/` subpackage. Close match to the blueprint's intent (WMO/CF/ECMWF standards hub), though not file-identical (`units.py`/`dimensions.py`/`coordinates.py`/`naming.py`/`conventions.py` as named files don't exist separately). |
| `catalog/` | ✅ `src/acf/catalog/` is real: `dataset_registry.py`, `manager.py`, `dataset_entry.py`, `catalog_entry.py`, `default_mapping.py`, `ocean_parameters.py`, `dataset_catalog.py`, `climate_parameters.py`, `default_catalog.py`, `catalog.py`, `satellite_parameters.py`, `surface_parameters.py`, `atmospheric_parameters.py`, `parameter_mapper.py`. A second, distinct `src/acf/catalogs/` (plural) package also exists — a real, already-documented (`tests/test_collisions_consolidation.py`) intentional duplicate, not a naming accident. |

### L2 — Data & spatio-temporal core

| Blueprint | Current reality |
|---|---|
| `data/` | ✅ `src/acf/data/` is real and substantial: `dataset.py`, `archive_system.py`, `dataset_registry.py`, `universal_ingestion.py`, `dataset_validator.py`, `factory.py`, `manager.py`, `universal_reader.py`, `streaming.py`, `grib_reader.py`, `unit_converter.py`, `bufr_reader.py`, `metadata_inspector.py`, `workflow.py`, `engine.py`, `metadata.py`, `detector.py`, `netcdf_reader.py`, `data_catalog.py`, `preprocessing.py`, `validator.py`, `cache_manager.py`, plus `writers/`, `engine/`, `fusion/`, `integration/`, `readers/` subpackages. Broad real overlap; QC/provenance/transformations/resampling/interpolation exist but not as the blueprint's exact single-purpose files. |
| `io/` | ✅ `src/acf/io/` is real: `base_reader.py`, `factory.py`, `manager.py`, `registry.py`, plus `readers/`. FA/GRIB/NetCDF reading is real (via `acf.data`'s readers and `acf.importers`), but the blueprint's specific `readers/writers/adapters/formats` 4-way split (with dedicated `epygram_adapter.py`/`eccodes_adapter.py`/`xarray_adapter.py`) is not literally present — epygram/eccodes/xarray usage is real but embedded inside the data-layer readers rather than isolated adapter modules. |
| `model4d/` | ✅ Strong match. `src/acf/model4d/` is real and extensively audited (per `docs/STATUS.md`): `time_axis.py`, `field4d.py`, `interpolation.py`, `vertical_axis.py`, `constants.py`, `grid4d.py`, `exceptions.py`, `domain4d.py`, `operators.py`, plus `operators/`, `physics/`, `interpolation/` subpackages (the `physics/` subpackage alone has 151 files, 100% audit coverage per `docs/STATUS.md`). This is the blueprint's single best-matched layer. |
| `workspace/` | ✅ `src/acf/workspace/` is real: `manager.py`, `project.py`, `recent.py`, `serializer.py`, `metadata.py`, `exceptions.py`, `templates.py`. Real project-lifecycle code exists, though the blueprint's `project.acf` file format and its `data/maps/models/reports/scripts/exports/logs/cache/plugins/` per-project directory convention have not been independently verified against this document. |

### L3 — Domain & high-level engines

| Blueprint | Current reality |
|---|---|
| `maps/` | ✅ Two real implementations exist: `src/acf/maps/` (`projection.py`, `map_engine.py`, `layer_manager.py`, `canvas.py`, `contours.py`, `vector.py`, `streamlines.py`, `basemap.py`, plus `projections/layers/styles/canvas/renderers` subpackages) and `src/acf/gui/map/` (the one actually embedded in the live GUI windows). Already documented in `docs/architecture/duplicate_components.md` as a genuine, not-yet-consolidated duplicate — see that file and `tests/test_collisions_consolidation.py::test_map_canvas_is_a_real_verified_duplicate_not_yet_consolidated`. |
| `visualization/` | ✅ `src/acf/visualization/` is real and large: `layer.py`, `layer_group.py`, `layer_collection.py`, `auto_renderer.py`, `data_renderer.py`, `cartopy_renderer.py`, `renderer.py`, `colormap.py`, `visualization_manager.py`, `layer_manager.py`, `radar_satellite_center.py`, plus `layer_engine/`, `scene/`, `timeline/`, `layers/`, `legends/`, `volume_engine/`, `ai_forecast_center/`, `gpu/`, `camera/`, `widgets/` subpackages. The blueprint's `scientific/` (skewt/hodograph/sounding) diagrams exist too, but under `src/acf/gui/dashboard/` (e.g. `acf_workstation_sounding_panel.py`) rather than a dedicated `visualization/scientific/` module. |
| `models/` | ✅ `src/acf/models/` is real: `manager.py`, `ensemble.py`, `forecast_config.py`, `base_model.py`, `hub.py`, `registry.py`, `detector.py`, plus per-model subpackages `common/`, `implementations/`, `arpege/`, `wrf/`, `openifs/`, `arome/`, `aladin/`, `icon/`. Direct, close match to the blueprint. |
| `ai/` | ✅ `src/acf/ai/` is real and broad: `engine.py`, `cloud_reasoning.py`, plus `data_assimilation/`, `uncertainty/`, `physics_informed/`, `ensemble/`, `xai/`, `emergency_assistant/`, `forecast/`, `analyzers/`, `atmosphere_explorer/`, `digital_twin/`, `decision_support/`, `neural_models/`, `alerts/`, `simulation/`, `plugins/`. No dedicated `ai/agents/` or `ai/rag/` subpackage — a real, verified gap: a repo-wide search for RAG (`retriever`/`vector_store`/`embeddings`-style modules) found nothing beyond a name coincidence in `src/acf/storage/` — **RAG is not implemented anywhere in this codebase today.** |
| `awci/` (historical, layer 3) | See §2 below — AWCI is intentionally not part of ACF's own layer 3 per the "AWCI separation" decision both blueprints agree on. |

### L4 — Presentation & applications

| Blueprint | Current reality |
|---|---|
| `gui/` | ✅ `src/acf/gui/` is real and is the actual live application (`app.py` is the real `acf-gui` entry point, launching `ACFWorkstationWindow` — see `docs/STATUS.md`'s 2026-09-21 ESOC-removal entry). Contains `theme.py`, `menu.py`, `statusbar.py`, `toolbar.py`, `earth_system_operations.py`, `bootstrap.py`, `single_instance.py`, `splash.py`, plus `layer_panel/`, `docks/`, `map/`, `dialogs/`, `resources/`, `workers/`, `dashboard/`, `widgets/` subpackages. The blueprint's flat `gui/main_window.py` central-file convention does not match reality: the live default window is `acf.gui.dashboard.acf_workstation_window.ACFWorkstationWindow`; `acf.gui.main_window` is confirmed dead legacy code (removed 2026-09-21 alongside ESOC, since it subclassed the now-deleted `ESOCWindow`). |
| `dashboard/` | ✅ Two real dashboard trees exist: `src/acf/dashboard/` (blueprint-shaped: `manager.py`, `window.py`, `dashboard.py`, `layout.py`, `widgets.py`, `panels/` — but itself unreachable from the running app today, a pre-existing, disclosed state, see that module's own docstring) and the much larger, actually-live `src/acf/gui/dashboard/` (AWCI dashboard, ACF Workstation, and ~30 other panel/window modules). |
| `api/` | 🟡 `src/acf/api/` exists but is minimal (`api.py` only) versus the blueprint's `routes/{data,models,diagnostics,maps,visualization,ai,reports,system}.py` + `schemas/`/`services/`/`middleware/` split. A separate, more built-out `src/acf/web/` package also exists (not in the blueprint's naming) — worth reconciling in any real migration. |
| `alerts/` | 🟡 `src/acf/alerts/` exists (`warning_engine.py`) — real but much thinner than the blueprint's `engine/rules/thresholds/events/notification/severity` split. |
| `reports/` | 🟡 `src/acf/reports/` exists with a `briefings/` subpackage, but no `generator.py`/`scientific_report.py`/`model_report.py`/`diagnostic_report.py`/`export.py`/`templates/` as named. |

### Project root

`tests/`, `docs/`, `resources/`, `scripts/`, `examples/`, `tools/`, `assets/`,
`configs/` all exist at the repository root today, though none has been
individually re-verified against the blueprint's own internal layout (e.g.
`tools/acfctl/` — an operational CLI control point — was not found in a
`tools/` survey; `acfctl start/stop/status/report` does not exist).

## 2. AWCI — current state vs. the separate-project blueprint

**Headline finding: `src/awci/` (a separate top-level package) does not
exist.** All AWCI-related code lives inside `src/acf/`, split mainly across
`src/acf/awci/` (the complexity/hazard computation itself) and
`src/acf/aviation/` (aviation domain knowledge), plus the live GUI dashboard
under `src/acf/gui/dashboard/awci_*.py`. Adopting the AWCI blueprint as
written means a real, first-time separation into its own top-level package —
this is new construction, not a rename of an equivalent existing tree.

| Blueprint layer | Closest current equivalent |
|---|---|
| `awci/core/` | ❌ No dedicated AWCI application/lifecycle/registry core exists; AWCI code is simply part of `acf.*`'s own process. |
| `awci/knowledge/` (aviation/meteorology/regulations/hazards/knowledge_graph) | 🟡 **Migrated 2026-09-21** — see §2j. Real, physically moved to `src/awci/knowledge/`: `airports/airport_database.py`, `icao/{live_source,metar_decoder,sigmet_decoder,taf_decoder,products}.py`, `performance/aircraft_performance.py`, `routing/flight_routing.py`, `hazards/aviation_hazards.py`, `graphics/cross_section.py`, with `acf.aviation.<x>` kept as a real backward-compatible re-export for all 10 modules plus the package itself. No `knowledge_graph/` (entities/relations/ontology) for aviation exists yet — the one real content gap remaining in this layer. |
| `awci/data/` + `data/connectors/` | 🟡 **`awci/data/` created 2026-09-21** (see §2e, §2i below), now holding `archive_field.py` (real ALADIN RESTOR archive ingestion via EPyGrAM) and the 3 generic model-import adapters `model_import.py`/`model_import_cross_section.py`/`model_import_evolution.py`. `src/acf/connectors/` is also real: `pirep_reports.py`, `nexrad_stations.py`, `argo_floats.py`, `wmo_wis.py`, `eumetsat_mtg.py`, `live_connectors.py` — genuine METAR/PIREP/radar/satellite connectors exist, still under `acf.connectors` rather than `awci.data.connectors`, not yet migrated; SIGMET/AIRMET/NOTAM/TAF connectors are decoders under `acf.aviation.icao`, not separate `connectors/` modules. |
| `awci/observations/` | 🟡 Overlaps with `acf.connectors` + `acf.aviation.icao` above; no single `observations/hub.py` aggregation point. |
| `awci/forecast/` | ✅ `src/acf/forecast/` is real: `forecast_engine.py`, `engine.py` — used across the AWCI dashboard's real per-model runs. |
| `awci/vertical/` | ✅ Real and substantial — `awci.complexity.vertical_field` (**migrated 2026-09-21**, see §2d below), `acf.gui.dashboard.acf_workstation_sounding_panel`, and the AWCI dashboard's own `AWCIVerticalSoundingWidget`/`ACFVerticalSoundingWidget` cover profile/sounding/wind-shear/icing-profile territory, just not under a dedicated `awci/vertical/` package with the blueprint's exact file split (skew_t/tephigram/emagram/stuve as separate diagram modules). **Deliberately not placed under a new `awci/vertical/` package**: despite its name, `vertical_field.py` is not the blueprint's general-purpose sounding/diagram engine — it is `AWCICalculator` applied along a vertical profile (its own docstring: "same real complexity computation as spatial_field.py exactly"), so it was migrated alongside `calculator.py`/`spatial_field.py` into `awci/complexity/` instead, as one coherent field-computation unit. |
| `awci/hazards/` (one module per hazard) | ✅ **Migrated 2026-09-21** — see §2b, §2g, §2h and §2i below. Physically moved to `src/awci/hazards/{icing_temperature_range,ceiling,visibility,dust,microburst,volcanic_ash,wind_shear,cat_turbulence,orographic_froude,hydrometeor_phase,convective_energy,theta_e,updraft,terrain_elevation}.py` (14 modules), with `acf.awci.<module>` kept as a real backward-compatible re-export. `spatial_field.py` now imports all 9 of its real hazard/thermo dependencies directly from `awci.hazards`, none through the `acf.awci` shim anymore. This is now a literal, not just conceptual, match to the blueprint's `awci/hazards/` (still flat rather than one-subpackage-per-hazard, which the blueprint itself is ambiguous about — it lists both a flat file-per-hazard example and per-hazard subdirectories). |
| `awci/complexity/` (the actual AWCI score) | ✅ **Migrated 2026-09-21** — see §2c and §2i below. `AWCICalculator` (the actual scoring/aggregation engine), `WeightsManager`, `Normalizer`, and `scientific_status` physically moved to `src/awci/complexity/`, joined by `scale_classification.py`/`wind_classification.py`/`spatial_field.py`/`vertical_field.py`/`temporal_field.py` (Phases 3-5) and then, in the single largest phase (§2i), 14 more real modules: `calibration.py`, `config_loader.py`, `diagnostic_registry.py`, `execution_report.py`, `forecaster_validation.py`, `input_adapter.py`, `metar_verification.py`, `method_comparison.py`, `path_sampling.py`, `pipeline.py`, `result.py`, `run_report.py`, `validation_cases.py`, `workstation_fields.py` — with `acf.awci.<module>` kept as a real backward-compatible re-export for all 23. Matches the blueprint's core principle (traceable scientific factors, not an arbitrary score) — this has been the subject of extensive audit across this session and prior ones. **As of Phase 8, `src/acf/awci/` contains nothing but re-export shims and `__init__.py` — every real line of AWCI complexity-engine code now lives under `src/awci/`.** |
| `awci/comparison/` + `awci/consensus/` | 🟡 **`awci/comparison/` created 2026-09-21** (see §2i below) with `multi_model_fusion.py` (real full-field multi-model fusion) and `regridding.py` (real generic grid regridding, its one real dependent). This is distinct from `ModelConsensusEngine` (see the "corrected 2026-09-21" note directly above from an earlier pass of this same document): the real `ModelConsensusEngine` lives in `src/acf/visualization/ai_forecast_center/model_consensus_engine.py` (604 lines), a genuine non-GUI domain layer already reachable independently of the GUI — it is imported directly by `acf.awci.calculator`, `acf.awci.result`, `acf.awci.multi_model_fusion`, `acf.forecast.engine`, and `acf.core.contracts.uncertainty`, in addition to 9 GUI dashboard modules. The only real gap versus the blueprint for *that* module is its **location/naming**: it sits under `acf.visualization.ai_forecast_center` rather than `acf.models.comparison`/`acf.models.consensus`/`awci.comparison`. A literal move would need to update 15+ real importers (across science, awci, forecast, core.contracts and GUI) plus 5 test files — assessed 2026-09-21 as real, mechanical, but high-blast-radius work with no functional benefit, so deferred rather than done reflexively; see the gap-analysis conclusion below. |
| `awci/flight/` | 🟡 `src/acf/aviation/routing/flight_routing.py` covers routing; no dedicated `planning.py`/`corridor.py`/`fuel_weather.py`/`route_weather.py` as named. |
| `awci/airport/` | 🟡 **`awci/airport/` created 2026-09-21** (see §2i below) with its first real module, `airport.py` (real airport approach/departure corridor geometry). `src/acf/aviation/airports/airport_database.py` (not yet migrated) covers the airport data; no dedicated runway/terminal/crosswind/runway_condition/disruption modules as named — some of this (crosswind, ceiling, visibility) exists inside `awci.hazards`'s own hazard modules instead. |
| `awci/decision/` | ❌ No dedicated decision-support engine (risk_matrix/scenario/recommendation) exists as a standalone module; the AWCI dashboard's "Current Situation"/risk cards present some of this information in the UI layer directly. |
| `awci/ai/` | 🟡 Overlaps with `acf.ai.emergency_assistant`/`acf.ai.decision_support`/`acf.ai.xai`, not AWCI-specific. |
| `awci/visualization/` (maps/complexity overlays) | ✅ Real — `acf.gui.map.map_layers` (e.g. `VolcanicAshLayer`, `MicroburstLayer`), `acf.gui.dashboard.awci_map_panel` — again inside the GUI layer, not a standalone visualization package. |
| `awci/dashboard/` | ✅ Very real and mature — `src/acf/gui/dashboard/awci_dashboard.py` and its ~15 companion modules (`awci_topbar.py`, `awci_route_chart.py`, `awci_situation_panel.py`, `awci_model_spread_chart.py`, etc.) are the single most heavily tested part of the whole codebase. Reachable both embedded (`AWCIDashboard` widget) and as its own standalone process (`acf-awci` / `acf.awci_app`, confirmed independent per `tests/test_awci_app.py`). |
| `awci/reports/` | 🟡 `src/acf/gui/dashboard/awci_messages_panel.py`/`awci_execution_report`-style panels exist in the GUI; no standalone `reports/aviation_report.py` generator. |
| `awci/api/` | ❌ No dedicated AWCI API surface; `src/acf/api/` and `src/acf/web/` are ACF-general, not AWCI-specific. |
| `awci/alerts/` | 🟡 `acf.gui.dashboard.awci_alerts_panel`-style UI exists; no standalone alerts engine. |
| `awci/plugins/` | ❌ Not found. |
| `awci/workspace/` | ❌ No AWCI-specific project/session format; ACF's own `acf.workspace` is general-purpose. |
| `awci/provenance/` | 🟡 Provenance discipline is a strong, repeatedly-enforced *convention* throughout this codebase (real formulas, real citations, "honest disclosure" of what's simulated vs. real — see `docs/STATUS.md` at length) but not a dedicated `provenance/lineage.py`/`audit.py` module.

## 2a. `model4d`/`models` migration (started 2026-09-21)

The first concrete migration step, scoped from this document at the user's
request. Findings:

- **`model4d`** needs no real migration: `model4d/operators/` already
  matches the blueprint's own `operators/` subpackage with real, audited
  content (`advection.py`, `divergence.py`, `gradient.py`, `laplacian.py`,
  `curl.py`, `diffusion.py`). Renaming files for literal blueprint-name
  parity (`gradient.py` → `gradients.py`, `curl.py` → `vorticity.py`) was
  considered and rejected: it would touch imports across the 152 audited
  files in `model4d/physics/` for zero functional or architectural gain.
- **`models`**: found and removed 7 genuinely dead placeholder files under
  `models/implementations/` (`arome.py`, `arpege.py`, `gefs.py`, `gfs.py`,
  `icon.py`, `ifs.py`, `wrf.py` — each a 28-line docstring-only stub with
  zero real code, confirmed by `grep` to have zero real importers anywhere
  in `src/` or `tests/`, and already implicitly flagged as non-real by
  `models/__init__.py`'s own prior-audit docstring). Real per-model logic
  lives elsewhere already: `models/{arome,aladin,arpege,wrf,icon,openifs}/
  ingestion_adapter.py` (real EPyGrAM-backed adapters) and
  `models/implementations/era5.py` (the one real `implementations/` file).
  Verified after removal: `ruff`/`mypy` clean, 93 tests passed across
  `test_model_detector.py`, `test_wrf_icon_openifs_adapters.py`,
  `test_model_adapter_protocol.py`, `test_ai_forecast_center.py`,
  `test_awci_calculator.py`.
- The comparison/consensus location question (§1 above, "corrected
  2026-09-21") remains open — deferred pending a decision on whether the
  15+-file blast radius is worth a purely organizational move.

## 2b. AWCI separate-package migration, Phase 1: `awci/hazards/` (2026-09-21)

Scoped in response to the explicit request "passe à AWCI en package séparé"
(move to AWCI as a separate package). Before touching anything, real import
counts were surveyed: **153 files import `acf.awci.*`, 123 test files
reference it** — a full one-shot cutover of everything AWCI-related into
`src/awci/` was assessed as too large and too risky to do safely in one
pass, so this phase moves the single subsystem already identified above as
the closest real blueprint match, with a strategy that keeps every existing
caller working:

1. Created `src/awci/` as a genuine new top-level package (confirmed
   importable with zero reinstall — this venv's editable install puts
   `src/` directly on `sys.path`, so any new top-level directory under it
   is automatically importable) and `src/awci/hazards/`.
2. Physically moved the 10 real hazard modules there via `git mv`
   (preserving history): `icing_temperature_range.py`, `ceiling.py`,
   `visibility.py`, `dust.py`, `microburst.py`, `volcanic_ash.py`,
   `wind_shear.py`, `cat_turbulence.py`, `orographic_froude.py`,
   `hydrometeor_phase.py`.
3. Fixed the one real intra-group dependency found by inspection
   (`hydrometeor_phase.py` importing `is_within_icing_temperature_range`
   from its sibling `icing_temperature_range.py`, both moving together) to
   point at the new `awci.hazards.` location. The two dependencies that
   point *out* of the group (`microburst.py` → `acf.awci.normalizer`,
   `cat_turbulence.py` → `acf.awci.workstation_fields`) were left as-is,
   since those modules are staying in `acf.awci` for now — `awci` legitimately
   depending on `acf` matches both reference architectures' own stated
   relationship (AWCI is built on top of ACF).
4. Left a real backward-compatible re-export at every old location
   (`acf.awci.<module>` now does `from awci.hazards.<module> import *`),
   verified to be the *same* object, not a copy
   (`test_awci_package_migration_hazards.py`,
   `test_old_acf_awci_namespace_reexports_the_exact_same_real_module`) — so
   none of the 153/123 existing real callers needed to change.

**Verified, not assumed**: `ruff`/`mypy` clean on `src/awci/` and
`src/acf/awci/` (57 files); direct import smoke test confirmed identity
(`acf.awci.dust.compute_real_dust_risk_at_point is
awci.hazards.dust.compute_real_dust_risk_at_point`); 325 tests passed
across every test file that imports these 10 modules directly (spatial
field, synthetic field, component detail, path sampling, ISA altitude,
map-layer-complexity, and 5 ACF Workstation panel tests); a broader
`-k "awci and not gui"` sweep (excluding the slow full GUI suite) passed
894/895, the one failure being the already-confirmed pre-existing,
unrelated native crash on the `acf-awci --version` subprocess's own
interpreter shutdown (see `docs/STATUS.md`'s ESOC-removal entry for the
first time this exact crash was isolated and confirmed independent of
Python code). A dedicated new test file,
`tests/test_awci_package_migration_hazards.py` (12 tests), locks in the
re-export identity and the new package's real top-level existence going
forward.

**What is intentionally not done yet**: as of Phase 8 (§2i below),
`src/acf/awci/` contains **zero** remaining real modules — everything is
either `__init__.py` or a re-export shim. Only `src/acf/aviation/`
(17 files) has not moved into the `awci` namespace at all. That is the
one real remaining candidate for a further phase.

## 2c. AWCI separate-package migration, Phase 2: `awci/complexity/` (2026-09-21)

Continuing directly from Phase 1 ("continue avec calculator.py"). Scoped
before touching anything: **57 files import `acf.awci.calculator`
specifically, 100 reference `AWCICalculator` overall, 48 test files touch
this engine** — confirmed to be, as flagged in §2b, the single
widest-blast-radius module in the whole `acf.awci` package. Investigation
found a clean, small, acyclic dependency chain suited to moving together as
one coherent unit: `scientific_status.py` (self-contained, zero `acf.awci`
siblings) → `{normalizer.py, weights.py}` (each depends only on
`scientific_status`) → `calculator.py` (depends on all three, plus the
external `acf.ai.ensemble.ensemble_manager`). These four map directly onto
the blueprint's own `awci/complexity/` layer (`engine.py`/`weights.py`/
`normalization.py`/classification types).

1. Created `src/awci/complexity/`.
2. Physically moved all four modules there via `git mv` (history
   preserved): `scientific_status.py`, `normalizer.py`, `weights.py`,
   `calculator.py`.
3. Fixed the 3 real intra-group imports found by inspection
   (`normalizer.py` and `weights.py` each importing from
   `acf.awci.scientific_status`; `calculator.py` importing from both) to
   point at the new sibling locations within `awci.complexity`.
   `calculator.py`'s one real external dependency
   (`acf.ai.ensemble.ensemble_manager`) was left untouched — it's a
   genuinely separate ACF subsystem, not part of this move.
4. Left a real backward-compatible re-export at every old location,
   verified to be the exact same object, not a copy — including the
   "shim reaching a shim" case: `awci.hazards.microburst` (Phase 1) still
   imports `Normalizer` via `acf.awci.normalizer`, which is now itself a
   Phase 2 shim forwarding to `awci.complexity.normalizer` — confirmed the
   chain resolves to the one real class
   (`test_awci_package_migration_complexity.py::
   test_hazards_modules_still_reach_the_moved_normalizer_through_the_shim`).
5. `acf/awci/__init__.py` needed **no changes**: its existing relative
   imports (`from .calculator import AWCICalculator`) still resolve, since
   the shim file physically exists at that same path.

**Verified, not assumed**: `ruff`/`mypy` clean (62 files under `src/awci/`
+ `src/acf/awci/`); direct import identity confirmed for
`AWCICalculator`/`Normalizer`/`WeightsManager` at both the module level and
`acf.awci`'s own package-level re-exports; `AWCICalculator()` still
constructs through its full real dependency chain; 507 tests passed across
every test file touching the calculator/normalizer/weights/scientific_status
directly (all `test_awci_calculator*.py` variants, `test_awci_result.py`,
`test_awci_pipeline.py`, `test_awci_scientific_status.py`,
`test_fire_weather.py`, `tests/scientific/regression/test_golden_datasets.py`,
etc.); a broader `-k "awci"` sweep (excluding the slow full GUI suite)
passed 913/914, the one failure being the same already-confirmed
pre-existing native subprocess-shutdown crash from Phase 1; a targeted GUI
sweep (ACF Workstation, AWCI dashboard reference parity/synchronization/
analysis panels — all real, heavy consumers of `AWCICalculator`) passed
101/108 (7 skipped, 0 failed); full test collection under xvfb — 4879
tests, 0 errors. A new `tests/test_awci_package_migration_complexity.py`
(6 tests) locks in the re-export identity, the shim-of-a-shim chain, and
end-to-end construction going forward.

## 2d. AWCI separate-package migration, Phase 3: `spatial_field.py` + `vertical_field.py` (2026-09-21)

Continuing directly from Phase 2 ("continue avec spatial_field.py et
vertical_field.py"). Scoped before touching anything: 46 files reference
`acf.awci.spatial_field`, 63 reference `acf.awci.vertical_field`; no
code-level import exists between the two (only cross-referencing
docstrings), so no ordering constraint between them.

**Placement decision, made and disclosed rather than followed
mechanically**: neither module has an obvious 1:1 blueprint folder. Despite
its name, `vertical_field.py` is not the blueprint's general-purpose
`awci/vertical/` sounding/diagram engine — its own docstring states it
applies "the same real complexity computation as `spatial_field.py`
exactly", just along a vertical profile instead of a horizontal grid. Both
are, in substance, `AWCICalculator` applied across a coordinate space, so
both were migrated into `awci/complexity/` alongside `calculator.py`
(Phase 2) as one coherent field-computation unit, rather than splitting
`vertical_field.py` into a separate `awci/vertical/` package on name
similarity alone.

1. Physically moved both via `git mv`: `spatial_field.py`,
   `vertical_field.py` → `src/awci/complexity/`.
2. Updated their `AWCICalculator` import from the `acf.awci.calculator`
   shim to a direct relative import (`.calculator`), since both now live
   in the same package as the real calculator.
3. `spatial_field.py` additionally imports 6 already-migrated hazard
   functions (`ceiling`/`dust`/`hydrometeor_phase`/`microburst`/
   `visibility`/`wind_shear`) — repointed these from the `acf.awci.*` shim
   to their real `awci.hazards.*` location directly (Phase 1), since both
   packages now live under the same `awci` namespace. Left its 3 remaining
   `acf.awci` imports (`convective_energy`, `theta_e`, `updraft`) as-is —
   those modules have not migrated yet.
4. Left a real backward-compatible re-export at both old locations,
   verified identical to the new objects.

**Verified, not assumed**: `ruff`/`mypy` clean (64 files); direct import
identity confirmed for `compute_real_complexity_field`/`score_volume`;
326 tests passed across every non-GUI test file touching these two modules
directly (`test_awci_spatial_field*.py`, `test_awci_vertical_field*.py`,
`test_awci_volume_3d.py`, `test_map_layers_awci.py`,
`test_map_layers_module_complexity.py`, `test_certification_engine.py`,
`test_convective_energy.py`, `test_core_contracts.py`, `test_events.py`,
`test_isa_pressure_altitude.py`, plus 4 ACF Workstation panel tests); a
broader `-k "awci"` sweep (excluding the slow full GUI suite) passed
913/914, the one failure being the same already-confirmed pre-existing
native subprocess-shutdown crash; full test collection under xvfb — 4883
tests, 0 errors. A new `tests/test_awci_package_migration_fields.py`
(4 tests) locks in the re-export identity and that both modules reach the
migrated calculator/hazards as real siblings, not stale copies.

## 2e. AWCI separate-package migration, Phase 4: `archive_field.py` + `temporal_field.py` (2026-09-21)

Continuing directly from Phase 3 ("continue avec archive_field.py et
temporal_field.py"). Scoped before touching anything: 9 files reference
`acf.awci.archive_field`, 17 reference `acf.awci.temporal_field`.

**Placement decision, and the first real split of this migration**:
inspection showed these two modules, despite sharing this session's request,
do not belong in the same place. `archive_field.py` has **zero** dependency
on `AWCICalculator` or any other `awci.complexity` module — it only imports
`acf.data.readers.epygram_reader.EPyGrAMReader` and
`acf.science.moisture.Moisture`, and its own docstring identifies it as a
real archived-data ingestion tier (real ALADIN RESTOR FULLPOS output,
decoded via EPyGrAM), not a complexity computation. This is the blueprint's
`awci/data/` Data Hub layer by function, not `awci/complexity/` by
proximity. `temporal_field.py`, by contrast, directly imports both
`AWCICalculator` and `vertical_field.score_volume` (Phases 2-3) — it applies
the same real complexity computation along a time series, exactly the
`spatial_field.py`/`vertical_field.py` pattern, so it joined them.

1. Created `src/awci/data/` (the blueprint's Data Hub layer, started with
   its first real module) and moved `archive_field.py` there unchanged — no
   internal imports needed fixing, since it has no `acf.awci` sibling
   dependencies at all.
2. Moved `temporal_field.py` into `src/awci/complexity/`, repointing its
   `AWCICalculator`/`score_volume` imports from the `acf.awci.*` shims to
   direct relative imports (`.calculator`, `.vertical_field`), since all
   three now live in the same package.
3. Left a real backward-compatible re-export at both old locations,
   verified identical to the new objects.

**Verified, not assumed**: `ruff`/`mypy` clean (67 files); direct import
identity confirmed for `load_real_aladin_restor_run`/
`sample_archive_at_point`/`restor_fullpos_path` (archive_field) and
`compute_real_complexity_evolution`/`profile_over_time` (temporal_field);
23 tests passed across `test_awci_archive_field.py` (16 skipped for the
same pre-existing, disclosed reason as before this migration — the real
RESTOR ALADIN archive file is machine-local, not in git, and genuinely
absent from this sandbox), `test_awci_temporal_field.py`, and
`test_moisture.py`; 87 GUI tests passed across the real consumers
(`test_acf_general_dashboard.py`, `test_acf_workstation_global_timeline.py`,
`test_acf_workstation_temporal.py`, `test_awci_dashboard_evolution.py`,
`test_awci_dashboard_level_slider.py`,
`test_awci_dashboard_reference_parity.py`); full test collection under
xvfb — 4887 tests, 0 errors. A new
`tests/test_awci_package_migration_data_and_temporal.py` (4 tests) locks
in the re-export identity for both modules and the placement rationale
itself (asserts `archive_field` genuinely has no `AWCICalculator`
dependency, so a future edit can't silently re-couple it to the
complexity engine without the test noticing).

## 2f. AWCI separate-package migration, Phase 5: `scale_classification.py` + `wind_classification.py` (2026-09-21)

Continuing directly from Phase 4 ("continue avec scale_classification.py
et wind_classification.py"). Scoped before touching anything: both are
small (124/133 lines) and fully self-contained —
`scale_classification.py` has zero `acf.awci` or external dependencies at
all (pure `Enum` classes + threshold functions), `wind_classification.py`
imports only the external `acf.science.wind_turbulence` (WMO Beaufort
scale, real jet-stream threshold). Only 2-3 real dependents each
(`acf.awci.result` references the former only in a comment;
`acf.gui.dashboard.awci_component_detail` imports the latter).

Both map directly onto the blueprint's own `awci/complexity/
classification.py` — the same `awci.complexity` package every module in
Phases 2-4 already joined — so this phase was the simplest so far: no
internal import fixes needed at all, since neither module has a real
sibling dependency.

1. Moved both via `git mv` into `src/awci/complexity/`.
2. Left a real backward-compatible re-export at both old locations,
   verified identical to the new objects (`classify_spatial_scale`/
   `classify_temporal_scale` for the former,
   `classify_wind_beaufort_force`/`classify_jet_stream` for the latter).

**Verified, not assumed**: `ruff`/`mypy` clean (69 files); direct import
identity confirmed for all 4 real public functions; 61 tests passed across
`test_awci_scale_classification.py`, `test_awci_wind_classification.py`,
`test_awci_component_detail.py`, `test_awci_result.py`; full test
collection under xvfb — 4889 tests, 0 errors. A new
`tests/test_awci_package_migration_classification.py` (2 tests) locks in
the re-export identity going forward.

`awci/complexity/` now holds 9 real modules: `scientific_status.py`,
`normalizer.py`, `weights.py`, `calculator.py`, `spatial_field.py`,
`vertical_field.py`, `temporal_field.py`, `scale_classification.py`,
`wind_classification.py` — the blueprint's own `engine.py`/`weights.py`/
`normalization.py`/`classification.py` core, essentially complete.

## 2g. AWCI separate-package migration, Phase 6: `convective_energy.py` + `theta_e.py` (2026-09-21)

Continuing directly from Phase 5 ("continue avec convective_energy.py et
theta_e.py"). Scoped before touching anything: `convective_energy.py` has
zero `acf.*` imports at all (pure NumPy + MetPy CAPE/CIN calculation);
`theta_e.py` imports only external `acf.physics_guard`/`acf.science.*`
modules. 14 and 20 real dependents respectively. Both follow the exact
`compute_real_<x>_at_point` pattern of the 10 hazard modules from Phase 1,
and — critically — both are consumed by `spatial_field.py`
(`awci.complexity/`) the same way the Phase 1 hazards already are.

**Placement**: joined `awci.hazards/` rather than starting a third package.
Neither is a named "hazard" in the blueprint's own sense (they are
thermodynamic building blocks - CAPE/CIN, equivalent potential
temperature - that other hazard computations and `spatial_field.py` build
on), but forcing a new home for two modules that are structurally
identical to the other 10 already there would fragment the codebase for
no real benefit; disclosed here rather than silently deviating from the
blueprint's own naming.

1. Moved both via `git mv` into `src/awci/hazards/`.
2. Repointed `spatial_field.py`'s imports of both from the `acf.awci.*`
   shim to their real `awci.hazards.*` location directly, matching Phase 3's
   treatment of the other 6 hazard imports it already uses.
3. Left a real backward-compatible re-export at both old locations.

**Verified, not assumed**: `ruff`/`mypy` clean (71 files); direct import
identity confirmed for `compute_real_cape_cin_at_point`/
`compute_real_theta_e_at_point`, including that `spatial_field.py` itself
now reaches the real migrated functions directly; 98 tests passed across
every test file touching these two modules
(`test_acf_workstation_convection.py`, `test_acf_workstation_map_inspector.py`,
`test_acf_workstation_stability_indices.py`,
`test_acf_workstation_thermodynamics.py`, `test_awci_ceiling.py`,
`test_awci_spatial_field.py`, `test_awci_spatial_field_microburst.py`,
`test_awci_theta_e.py`, `test_convective_energy.py`); a long-running,
broader `tests/gui/ -k "awci or workstation"` sweep (started before this
phase, covering everything through Phase 5) finished at **458 passed, 8
skipped, 0 failed** in 17m41s, confirming zero GUI regressions across the
whole migration so far; full test collection under xvfb — 4892 tests, 0
errors. A new `tests/test_awci_package_migration_thermodynamic_hazards.py`
(3 tests) locks in the re-export identity and that `spatial_field.py`
reaches both as real siblings.

## 2h. AWCI separate-package migration, Phase 7: `updraft.py` (2026-09-21)

Continuing directly from Phase 6 ("continue avec updraft.py"). Scoped
before touching anything: `updraft.py` imports only the external
`acf.science.clouds.dynamics.CloudDynamicsEngine`, has 12 real dependents,
and is the third and last of `spatial_field.py`'s own three
`compute_real_<x>_at_point`-style dependencies (alongside
`convective_energy.py`/`theta_e.py` from Phase 6) — same pattern, same
placement rationale, joined `awci.hazards/`.

1. Moved via `git mv` into `src/awci/hazards/`.
2. Repointed `spatial_field.py`'s last remaining `acf.awci.*` import to
   `awci.hazards.updraft` directly.
3. Left a real backward-compatible re-export at the old location.

With this, `spatial_field.py` no longer imports anything through the
`acf.awci` shim at all — all 9 of its real per-point hazard/thermodynamic
inputs are direct `awci.hazards` imports.

**Verified, not assumed**: `ruff`/`mypy` clean (72 files); direct import
identity confirmed for `compute_real_max_updraft_velocity`, including that
`spatial_field.py` reaches it directly; 69 tests passed across
`test_awci_calculator_updraft.py`, `test_awci_layer_grids.py`,
`test_awci_spatial_field.py`, `test_awci_updraft.py`; full test collection
under xvfb — 4895 tests, 0 errors. A new
`tests/test_awci_package_migration_updraft.py` (3 tests) locks in the
re-export identity and, via source inspection, that `spatial_field.py`
genuinely has zero remaining `from acf.awci.` import lines.

## 2i. AWCI separate-package migration, Phase 8: the remaining 21 modules, in one batch (2026-09-21)

The user asked to continue automatically through the remaining modules "un
par un" (one by one) rather than stopping after each. Given the batch was
large, this phase still did the same investigate-first work as every prior
phase - it just did it for all 21 modules up front before moving anything,
then executed and verified as one coherent unit.

**Dependency graph, built before any move**: grepped every remaining
module's top-level imports for `acf.awci.*`/relative references, producing
a topological order:
- 10 leaves with zero internal `acf.awci` dependencies: `airport.py`,
  `execution_report.py`, `forecaster_validation.py`, `input_adapter.py`,
  `path_sampling.py`, `regridding.py`, `result.py`, `run_report.py`,
  `terrain_elevation.py`, `validation_cases.py`.
- 6 depending only on already-migrated modules (Phases 1-7):
  `calibration.py`/`config_loader.py` (→ `calculator.py`),
  `diagnostic_registry.py` (→ `scientific_status.py`),
  `metar_verification.py` (→ `ceiling.py`/`visibility.py`),
  `method_comparison.py` (→ `calculator.py`/`normalizer.py`),
  `model_import.py` (→ `convective_energy.py`).
- 5 depending on same-batch siblings, moved last:
  `model_import_cross_section.py`/`model_import_evolution.py` (→
  `model_import.py`), `multi_model_fusion.py` (→ `regridding.py` +
  `spatial_field.py`), `pipeline.py` (→ `calculator.py`/
  `execution_report.py`/`input_adapter.py`/`result.py`),
  `workstation_fields.py` (→ `convective_energy.py`/`orographic_froude.py`/
  `terrain_elevation.py`/`theta_e.py`/`wind_shear.py`).

**Placement, decided by real role, not by batching convenience** - read
each module's own docstring/function signatures rather than guessing from
the filename:
- **`awci/airport/`** (new): `airport.py` - real airport approach/
  departure corridor geometry, a direct, named blueprint layer.
- **`awci/comparison/`** (new): `multi_model_fusion.py` (real full-field
  multi-model fusion) + `regridding.py` (its one real dependent, generic
  grid regridding) - the blueprint's own comparison/fusion concept,
  distinct from `ModelConsensusEngine` (see the corrected row above).
- **`awci/data/`**: `model_import.py`, `model_import_cross_section.py`,
  `model_import_evolution.py` - generic counterparts to `archive_field.py`
  (Phase 4), same data-ingestion role.
- **`awci/hazards/`**: `terrain_elevation.py` - follows the
  `compute_real_<x>_at_point` pattern of the other 13 hazard modules
  (`compute_real_terrain_slope_aspect_at_point`).
- **`awci/complexity/`** (the remaining 14): `calibration.py`,
  `config_loader.py`, `diagnostic_registry.py`, `execution_report.py`,
  `forecaster_validation.py`, `input_adapter.py`, `metar_verification.py`,
  `method_comparison.py`, `path_sampling.py`, `pipeline.py`, `result.py`,
  `run_report.py`, `validation_cases.py`, `workstation_fields.py` - all
  either directly wrap/verify/configure `AWCICalculator`, or (like
  `workstation_fields.py`) play the same "aggregate real hazard fields for
  a consumer" role as `spatial_field.py` already migrated there.

**Execution**: all 21 physically moved via `git mv`. Fixing internal
imports surfaced real cross-file dependencies a first top-of-file-only
pass would have missed - a second, thorough sweep for `deferred` (function-
body) imports and `__all__`-restricted modules found and fixed:
- 6 deferred (inside-function) imports across `path_sampling.py` (4),
  `execution_report.py`, `model_import.py` (×2) that a naive top-of-file
  grep had missed.
- `config_loader.py`'s and `model_import_cross_section.py`'s own deferred
  imports of `weights.py`/`path_sampling.py`.
- Two modules already migrated in **earlier phases** that turned out to
  depend on modules moved in **this** phase: `cat_turbulence.py` (Phase 1)
  imports `workstation_fields.real_grid_spacing_m`, and `normalizer.py`
  (Phase 2) has a deferred import of `ceiling.MVFR_CEILING_M` - both
  repointed to their real cross-package `awci.*` locations while already
  working correctly through the shim, since finding them meant they could
  be cleaned up now rather than left as permanent shim traffic.
- `model_import.py`, `model_import_cross_section.py`, and
  `model_import_evolution.py` each have a real `__all__` - their shims'
  `import *` correctly (by design) only re-exports what's listed there;
  verified against the real `__all__`, not "every public name", to avoid
  false-positive gaps.
- `regridding.py`'s shim needed two explicit private-name re-exports
  (`_cell_edges_latitude`, `_natural_edges`) beyond its `import *` -
  `tests/test_regridding.py` does real whitebox testing of these internal
  helpers directly, and `import *` never re-exports underscore names by
  design. Found via a full `pytest --collect-only` sweep after the initial
  shim pass (a real, if brief, regression before this fix), not assumed
  clean.

**Verified, not assumed**: `ruff`/`mypy` clean (95 files under `src/awci/`
+ `src/acf/awci/`); identity confirmed programmatically for all 21 modules
(17 checked as "every public name matches", 3 checked against their real
`__all__`, the shim-private-name case checked separately); 416 tests
passed across every non-GUI test file touching these 21 modules directly;
33 GUI tests passed across the real consumers
(`test_acf_workstation_interaction_graph_panel.py`,
`test_acf_workstation_multimodel.py`,
`test_awci_dashboard_execution_report.py`,
`test_awci_dashboard_imported_cross_section.py`,
`test_awci_dashboard_imported_model.py`); a broader `-k "awci"` sweep
(excluding the slow full GUI suite) passed 929/930, the one failure being
the same already-confirmed pre-existing native subprocess-shutdown crash;
full test collection under xvfb — 4895 tests, 0 errors (unchanged count -
a pure migration, no tests added or removed by the move itself). A new
`tests/test_awci_package_migration_phase8.py` (23 tests) locks in the
re-export identity for all 21 modules, the private-name shim fix, the 2
new packages' real top-level existence, and the 2 cross-phase dependency
fixes. All 58 migration lock-in tests across Phases 1-8 together
(`tests/test_awci_package_migration_*.py`) pass as one suite.

**With this phase, `src/acf/awci/` contains nothing but `__init__.py` and
44 re-export shims** - every real line of AWCI complexity-engine,
hazard-diagnostic, data-ingestion, comparison, and airport-operations code
now lives under the new top-level `src/awci/` package, exactly as the
adopted reference architecture specifies. The one remaining real gap
before the whole AWCI subsystem is genuinely separate is
`src/acf/aviation/` (17 files) - not yet touched.

## 2j. AWCI separate-package migration, Phase 9: `src/acf/aviation/` → `awci/knowledge/` (2026-09-21)

The user asked to continue with `src/acf/aviation/` - the one remaining real
gap noted at the end of §2i. This is a structurally different package from
`acf.awci`: 17 files across 6 already-organized subpackages
(`airports/`, `graphics/`, `hazards/`, `icao/`, `performance/`, `routing/`),
not a flat directory of loosely-related modules.

**Investigation, before any move**:
- `acf.aviation` is largely self-contained. Internal cross-references, all
  within the package itself: `icao/live_source.py` and `icao/products.py`
  both import the 3 decoders (`metar_decoder.py`, `sigmet_decoder.py`,
  `taf_decoder.py`); `icao/taf_decoder.py` imports regex helpers
  (`_CLOUD_RE`, `_VIS_M_RE`, `_VV_RE`, `_WIND_RE`, `_WX_RE`) from
  `icao/metar_decoder.py`; `routing/flight_routing.py` imports
  `airports/airport_database.py` (the one real cross-subpackage
  dependency). One external dependency in the whole package:
  `icao/metar_decoder.py` imports `acf.physics_guard.variable_quality`
  (kept as-is - a genuinely different, unrelated subsystem, not part of
  this migration).
- 27 external dependents of `acf.aviation.*` found via
  `grep -rl "acf\.aviation\." src/ tests/`. Critically, 11 of them are
  **already-migrated `awci/*` modules from earlier phases** -
  `awci/airport/airport.py` (Phase 8), `awci/hazards/{volcanic_ash,
  cat_turbulence,microburst,icing_temperature_range}.py` (Phase 1/6),
  `awci/complexity/{scientific_status,metar_verification,normalizer,
  result,weights,calculator}.py` (Phases 2/8) - confirming `acf.aviation`
  is already deeply, real load-bearing coupled to the new package, not an
  independent island.
- Read module docstrings rather than guessing from filenames:
  `hazards/aviation_hazards.py` is a hazard-**definitions registry**
  (`AviationHazardEngine`/`AviationHazardInfo`/
  `AVIATION_HAZARDS_REGISTRY`) - conceptually distinct from
  `awci/hazards/`'s real per-point numeric computation, despite the name
  clash. `graphics/cross_section.py` is a flight-route vertical
  cross-section engine. `icao/live_source.py` is real live METAR/TAF/SIGMET
  fetching - the real caller that makes the decoders reachable outside
  tests.

**Placement decision (disclosed)**: move the *entire* `acf.aviation`
package as one coherent unit into a new `src/awci/knowledge/` package,
preserving its internal subpackage structure unchanged
(`knowledge/airports/`, `knowledge/graphics/`, `knowledge/hazards/`,
`knowledge/icao/`, `knowledge/performance/`, `knowledge/routing/`). This
matches the blueprint's own `awci/knowledge/` "Aviation Knowledge Base"
layer. An alternative was considered and rejected: fragmenting across
several new top-level packages by stricter layer-name matching (e.g. a
separate `awci/observations/` for `icao/`, `awci/flight/` for `routing/`).
Rejected because `acf.aviation` was already a coherent, well-organized
package - fragmenting it for marginal naming purity would cost real
cohesion for no functional gain, consistent with the same reasoning
applied in Phases 6-7 (keeping `convective_energy.py`/`theta_e.py`/
`updraft.py` together in `hazards/` rather than starting a third package).
The resulting **naming overlap is intentional and disclosed**:
`awci.knowledge.hazards` (aviation hazard *definitions* registry) and the
pre-existing `awci.hazards` (real per-point complexity *computation*) are
two distinct concepts at two distinct layers that happen to share a
directory name, exactly mirroring the real distinction already present in
the original codebase.

**Execution**: all 17 files physically moved via `git mv`
(`airports/{__init__,airport_database}.py`,
`graphics/{__init__,cross_section}.py`,
`hazards/{__init__,aviation_hazards}.py`,
`icao/{__init__,live_source,metar_decoder,products,sigmet_decoder,
taf_decoder}.py`, `performance/{__init__,aircraft_performance}.py`,
`routing/{__init__,flight_routing}.py`), plus the top-level
`acf/aviation/__init__.py` reconstructed as `awci/knowledge/__init__.py`
with its 6 real imports repointed to relative-package form. Internal
cross-references fixed to `awci.knowledge.*` (4 real import lines:
`icao/live_source.py`, `icao/products.py`, `icao/taf_decoder.py`,
`routing/flight_routing.py`). A second, deeper grep pass for deferred
(function-body) imports across the whole moved package found none this
time - all of `acf.aviation`'s cross-references were real top-of-file
imports.

The mandatory comprehensive sweep (`grep -rn "acf\.aviation\." src/awci/`,
across the *entire* `src/awci/` tree, not just the newly-moved files)
confirmed the 11 already-migrated dependents found during investigation
and repointed the 4 that had real top-of-file import statements
(the other 7 references were docstrings/comments citing
`acf.aviation.hazards.aviation_hazards` as a scientific source, left as
historical citations, matching how earlier phases treated comment-only
references): `awci/airport/airport.py`, `awci/hazards/cat_turbulence.py`,
`awci/hazards/microburst.py`, `awci/complexity/metar_verification.py` now
import `awci.knowledge.*` directly instead of round-tripping through the
`acf.aviation` shim.

**Verified, not assumed**: `ruff check src/awci/ src/acf/aviation/
src/acf/awci/` clean; `mypy src/awci/knowledge/ src/acf/aviation/` clean
(34 source files); identity confirmed programmatically for all 10 real
modules plus the package-level `__init__.py`'s `__all__` (11 checks, all
passed); full test collection under xvfb - 4918 tests, 0 errors (up from
4895 at the end of §2i because this phase's own new lock-in test file adds
tests, not because of a regression); a `-k "aviation or awci"` sweep
(excluding the slow full GUI suite) passed 971/972, the one failure being
the same already-confirmed pre-existing native subprocess-shutdown crash
in `test_awci_app.py`; the one GUI file with real `acf.aviation`
dependencies, `tests/gui/test_awci_dashboard_alerts_button.py`, passed
4/4. A new `tests/test_awci_package_migration_phase9.py` (14 tests) locks
in the re-export identity for all 10 modules and the package `__init__`,
the new package's real top-level existence, the internal
same-package cross-references, and the 4 cross-phase dependency fixes.

**With this phase, `src/acf/aviation/` contains nothing but `__init__.py`
files and 11 real re-export shims** - every real line of aviation
knowledge-base code (airport data, aircraft performance, METAR/TAF/SIGMET
decoding and live source, flight routing, and the aviation hazard
definitions registry) now lives under `src/awci/knowledge/`. Combined with
§2i, **the entire real-code half of the AWCI separate-package migration
(both `src/acf/awci/` and `src/acf/aviation/`) is now complete** - the one
remaining piece from the original scope (§3.1) is the AWCI-specific
portions of `src/acf/gui/dashboard/`, deliberately left in the GUI layer as
real consumers rather than moved (consistent with how the dashboard layer
has been treated throughout this whole migration).

## 2k. AWCI separate-package migration, Phase 10: the dashboard (2026-09-21)

The user asked to continue with "le tableau de bord GUI" - the AWCI
dashboard itself, the one remaining piece named at the end of §2j.

**Investigation, before any move**: `src/acf/gui/dashboard/` holds two
clearly, consistently named families of modules side by side: ~30
`acf_workstation_*.py`/`acf_general_dashboard*.py` files (ACF's own
general-purpose scientific workstation) and 29 `awci_*.py` files (the
real, operational AWCI dashboard - map, alerts, hazards, cross-section,
vertical profile, situation panel, messages, execution report, and the
top-level `AWCIDashboard`/`AWCIDashboardWindow`). Unlike every prior
phase, this family already had a hard naming split from the ACF-side
family, but real coupling in both directions had to be mapped before
moving anything:

- **Internal dependency graph among the 29 files** (built via grep, used
  for the move order): 17 true leaves (`awci_colors`, `awci_gauge`,
  `awci_synthetic_field`, etc.), 7 depending only on leaves
  (`awci_map_panel`, `awci_cross_section`, `awci_route_chart`, etc.), then
  `awci_alerts_panel`, then `awci_footer_summary`/`awci_situation_panel`,
  then `awci_dashboard` (which imports ~20 of the other 28), and finally
  `awci_window`.
- **References to already-migrated `awci.*` code**: 19 real import
  statements (top-of-file and deferred) across `awci_component_detail.py`,
  `awci_dashboard.py`, `awci_execution_report_dialog.py`,
  `awci_synthetic_field.py`, `awci_alerts_panel.py`, `awci_messages_panel.py`
  reaching into what used to be `acf.awci.*`/`acf.aviation.icao.*` - all
  of it already physically relocated to `awci.complexity`/`awci.hazards`/
  `awci.data`/`awci.knowledge.icao` in Phases 1-9.
- **Real, load-bearing reverse coupling from ACF's own dashboard**: 12
  `acf_workstation_*.py` files import `AWCIMapPanel` as a reusable map
  widget; `acf_general_dashboard.py` imports 6 real AWCI dashboard widgets
  (`AWCICrossSection`, `AWCIEvolutionChart`, `AWCIGauge`, `AWCIMapPanel`,
  `AWCIModelSpreadChart`, `AWCIRadar`); `acf/dashboard/window.py` and
  `acf/awci_app.py` (the `acf-awci` console-script entry point) both
  launch `AWCIDashboardWindow` directly. This is real widget reuse, not
  incidental - confirmed by reading the actual import statements, not
  assumed from the file layout.
- **Reverse coupling the other way**: `awci_dashboard.py` itself imports
  `acf.gui.dashboard.acf_workstation_sounding_panel.ACFVerticalSoundingWidget`
  - AWCI's dashboard genuinely reuses one of ACF's own panels too.

**Placement decision**: move all 29 `awci_*.py` files as one unit into a
new `src/awci/dashboard/` package - the blueprint's own §16 "application
layer above everything else". Real module names kept as-is (not renamed
to the blueprint's own illustrative file names like `application.py`/
`layout.py`/`state.py`), since this is real, functional, already-tested
code, not a fresh build from the blueprint's sketch.

**Handling the reverse coupling (disclosed)**: the blueprint's own closing
note (§22, "remove AWCI from the ACF dashboard... AWCI can exist as a
separate dashboard") points toward eventually decoupling ACF's own
dashboard from AWCI's widgets entirely. That is a real product/architecture
decision - whether `acf_workstation_*.py` keeps reusing `AWCIMapPanel`, or
gets its own independent map widget - not a mechanical migration step, and
was not asked for. So, consistent with how every external caller of a
migrated module has been treated throughout this whole migration (Phases
1-9 never touched a caller outside the package being moved - it always
kept working through the backward-compatible shim), the 12
`acf_workstation_*.py` files, `acf_general_dashboard.py`,
`acf_general_dashboard_window.py`, `acf/dashboard/window.py`, and
`acf/awci_app.py` were **deliberately left importing
`acf.gui.dashboard.awci_*` unchanged** - they keep working exactly as
before, through the shim. `acf/awci_app.py` itself (the registered
`acf-awci` console-script entry point in `pyproject.toml`) was also
deliberately left in place rather than moved - moving a package's
entry-point module is a packaging-level decision distinct from moving its
implementation, out of scope for this phase.

**Execution**: all 29 files physically moved via `git mv` in the
topological order above. Internal cross-references (`from
acf.gui.dashboard.awci_X import ...`) repointed to `from
awci.dashboard.awci_X import ...`. All 19 references to already-migrated
`awci.*` code repointed to their real direct locations (e.g.
`acf.awci.diagnostic_registry` → `awci.complexity.diagnostic_registry`,
`acf.awci.archive_field` → `awci.data.archive_field`,
`acf.aviation.icao.live_source` → `awci.knowledge.icao.live_source`) -
the same module-name → real-package mapping established across Phases
1-9, applied here as a mechanical lookup, not re-derived per file. Real
ACF-infrastructure imports genuinely needed by the dashboard
(`acf.gui.theme_tokens`, `acf.gui_screen_utils`, `acf.gui.map.*`,
`acf.hpc_connector`, `acf.data.manager`, `acf.science.clouds.dynamics`,
`acf.physics_guard`, `acf.visualization.ai_forecast_center.
model_consensus_engine`) left untouched - AWCI as an application
genuinely depends on ACF as its underlying framework for these, exactly
as intended.

**A real bug found and fixed, not just a migration artifact**: two test
files (`tests/test_awci_messages_panel.py`, 6 tests;
`tests/gui/test_awci_dashboard_alerts_button.py`, 1 test) use
`unittest.mock.patch("acf.gui.dashboard.awci_messages_panel.
fetch_and_decode_station", ...)` to stub the live METAR/TAF/SIGMET fetch
without real network access. `mock.patch` rebinds the name on the
*specific module object* named by the dotted path - since
`AWCIMessagesDialog`'s real code now lives in (and reads its own global
`fetch_and_decode_station` from) `awci.dashboard.awci_messages_panel`,
patching the *shim's* namespace at the old `acf.gui.dashboard.
awci_messages_panel` path no longer reaches the code that actually calls
it; `import *` only copies the name once, at shim-import time, into the
shim's own namespace, not a live link back to the real module's globals.
Found via a full `-k "awci or aviation"` test sweep (not assumed clean) -
7 failures, all with the exact same shape (a mocked live fetch silently
not taking effect, the dialog falling back to its honest error/empty
state instead of the fake data). Fixed by repointing all 7 patch targets
in both files to the real `awci.dashboard.awci_messages_panel.*` path.
This is a real, general lesson for any future phase: `mock.patch` targets
must always follow a moved module's *real* location, never the
backward-compatible shim's.

**Verified, not assumed**: `ruff check` clean (one unrelated,
already-existing pre-migration unused import in `awci_footer.py`,
confirmed via `git show` against the file's own prior content -
untouched, not this phase's concern); `mypy` clean except 15
already-existing, pre-migration Qt-layout-nullability errors in
`awci_route_chart.py`/`awci_situation_panel.py`/`awci_footer_summary.py`
(confirmed identical against the pre-move file content); identity
confirmed programmatically for all 29 modules plus the 13 private names
6 real whitebox tests import directly (`_AIRPORTS`,
`_ALL_VERTICAL_PROFILE_LEVELS_HPA`, `_FLIGHT_LEVEL_SELECTOR_OPTIONS_HPA`,
`_POINT_OF_INTEREST`, `_REGIONAL_ROUTE`, `_REGIONAL_CITY_LABELS`,
`_ModelConsensusWorker`, `_ModelDisagreementFieldWorker`,
`_ModelVerticalProfilesWorker`, `_synthetic_inputs`, `_ElidingLabel`,
`_hpa_to_ft`, `_AXES`); full test collection under xvfb - 4932 tests, 0
errors (4918 + 14 for this phase's own new lock-in test file); a
`-k "awci or aviation"` sweep (excluding the slow full GUI suite) passed
1024/1031 after the mock-patch fix (7 real fixes applied, the remaining
failure being the same already-confirmed pre-existing native
subprocess-shutdown crash in `test_awci_app.py`); the whole `-k "awci"`
subset of `tests/gui/` re-run clean after the fix. A new
`tests/test_awci_package_migration_phase10.py` (45 tests) locks in the
re-export identity for all 29 modules, all 13 private-name shim
additions, the internal cross-references, and the cross-package
references to already-migrated `awci.*` code.

**With this phase, `src/acf/gui/dashboard/` holds only ACF's own real
dashboard code plus 29 backward-compatible re-export shims** for AWCI's
dashboard - every real line of the AWCI dashboard itself now lives under
the new top-level `src/awci/dashboard/` package. Combined with §2i-§2j,
the entire real-code body of the AWCI separate-package migration named in
the original scope (§3.1) is now complete: `src/acf/awci/`,
`src/acf/aviation/`, and the AWCI-specific dashboard modules are all real,
physically separate `awci.*` code, each with a full backward-compatible
shim at its old location. The remaining, deliberately-untouched pieces
are ACF-side integration points (`acf_workstation_*.py`'s `AWCIMapPanel`
reuse, `acf_general_dashboard.py`'s widget reuse, `acf/dashboard/window.py`'s
and `acf/awci_app.py`'s launch of `AWCIDashboardWindow`) and the
`acf-awci` console-script entry point itself - real product/packaging
decisions about how separate ACF and AWCI should ultimately be, not
migration mechanics.

## 3. What this means for a real migration

Adopting these two blueprints literally would require, at minimum:

1. **Splitting `src/acf/awci/` + `src/acf/aviation/` + the AWCI portions of
   `src/acf/gui/dashboard/` into a new top-level `src/awci/` package** —
   **complete** (Phases 1-10, §2a-§2k): 44 real modules physically moved
   into `awci.{hazards,complexity,data,comparison,airport}`, 17 more into
   `awci.knowledge.{airports,graphics,hazards,icao,performance,routing}`,
   and the 29-module AWCI dashboard into `awci.dashboard`. `src/acf/awci/`,
   `src/acf/aviation/`, and the AWCI modules of `src/acf/gui/dashboard/`
   now hold only backward-compatible re-export shims. The deliberately
   untouched pieces (ACF-side widget reuse, the `acf-awci` console-script
   entry point) are real product/packaging decisions, not migration
   mechanics - see §2k's own closing note.
2. **Reorganizing `src/acf/science/` and `src/acf/parameters/` from flat,
   topic-named modules into the blueprint's per-domain subpackages** —
   **started 2026-09-21** (Phase 1, §4a): the 21-module
   `science/thermodynamics/` subdomain is done. A large but mechanically
   simpler rename/move than item 1, since the underlying real physics is
   already implemented and tested; the risk is import breakage across the
   ~50+ modules that consume them, not re-deriving formulas. See §4 below.
3. **Filling genuine, currently-absent pieces**: a RAG layer (`ai/rag/`),
   an AWCI-specific decision-support engine, an AWCI-specific
   provenance/audit module, `acfctl` as an operational CLI, and a real
   `awci/plugins/` extension mechanism. None of these exist as fabricated
   placeholders today — they are simply not built yet, which is the
   correct, honest state to report rather than inventing stubs.
4. **Deciding what to do with confirmed, already-documented duplicates**
   (`acf.maps` vs `acf.gui.map`, `acf.catalog` vs `acf.catalogs`, and a
   newly-found instance of the same pattern: `acf.science.parameters`,
   the real `PhysicalParameter` data model, vs the top-level
   `acf.parameters`, a real, unrelated catalog/registry/converter/units
   system — see §4's own investigation notes) before or during the
   reorganization, since the blueprints assume one canonical location per
   concern.

## 4. ACF `science/`/`parameters/` per-domain reorganization

Started 2026-09-21 ("continue avec la réorganisation de science/ et
parameters/"), following item 2 above. `src/acf/science/` holds ~60 flat,
topic-named modules plus 7 already-existing subpackages
(`clouds/`, `encyclopedia/`, `knowledge_graph/`, `laws/`, `observations/`,
`parameters/`, `physics_ai/`) that don't correspond to the blueprint's own
19 subdomain names. `src/acf/parameters/` is a separate, real
catalog/registry system (`aliases.py`, `catalog.py`, `categories.py`,
`converter.py`, `hub.py`, `index.py`, `parameter.py`, `registry.py`,
`search.py`, `units.py`, `validator.py`) - genuinely distinct from the
blueprint's own idealized `parameters/atmosphere/ocean/land/...` sketch
and, confusingly, distinct from `acf.science.parameters` too (a small,
real `PhysicalParameter` data model: `definitions.py`, `engine.py`,
`physical_parameter.py`) - a second, newly-found instance of the same
duplicate-naming pattern already flagged for `acf.maps`/`acf.catalog`.
Given the scale (dwarfing any single AWCI phase - `science/` alone is
larger than all of `acf.awci` + `acf.aviation` combined) and the
blueprint's own "initial atmospheric priority" callout, this reorganization
proceeds the same way the AWCI migration did: one bounded, fully-verified
phase at a time, `git mv` + backward-compatible shims, never a big-bang
rewrite.

### 4a. Phase 1: `science/thermodynamics/` (2026-09-21)

**Placement**: the blueprint names `science/thermodynamics/` as its own
"initial atmospheric priority" subdomain. 21 real, already-existing flat
modules map to it directly by content: `thermodynamics.py`,
`potential_temperature.py`, `virtual_temperature.py`,
`virtual_potential_temperature.py`, `equivalent_potential_temperature.py`,
`mixing_ratio.py`, `saturation_mixing_ratio.py`, `specific_humidity.py`,
`vapor_pressure.py`, `saturation_vapor_pressure.py`,
`relative_humidity.py`, `humidity.py`, `air_density.py`, `dewpoint.py`,
`wet_bulb_temperature.py`, `moist_static_energy.py`,
`dry_static_energy.py`, `hypsometric_equation.py`,
`geopotential_height.py`, `pressure.py`, `temperature.py` - real module
names kept as-is (not renamed to the blueprint's own smaller illustrative
set), following the same precedent established throughout the AWCI
migration.

**Investigation, before any move**: each module follows a clean
one-class-per-module pattern (`PotentialTemperature`, `DewPoint`, etc.),
matching the style already used by the existing `science/clouds/`
subpackage - its own `__init__.py` was read first as the real, in-codebase
precedent for how a science subpackage should re-export its public API.
Internal cross-references: only `equivalent_potential_temperature.py`
depends on two same-batch siblings (`saturation_mixing_ratio.py`,
`saturation_vapor_pressure.py`); everything else is either a true leaf or
depends only on `acf.science.constants` (staying in its current flat
location this phase - moving it now would touch nearly every other
`science/` module, out of scope for a single bounded phase). No `__all__`
restrictions, no deferred imports, no underscore-prefixed whitebox test
imports found in any of the 21 modules. External fan-in checked per
module via grep - a real but manageable 1-10 dependents each (`cape.py`
had the most, 10), the same order of magnitude the shim strategy already
proved out across 100+ AWCI callers.

**Execution**: all 21 files physically moved via `git mv` into a new
`src/acf/science/thermodynamics/` package. The one internal cross-
reference repointed to a relative-package import. `__init__.py` written
re-exporting all 21 real classes with a real `__all__`, mirroring
`science/clouds/__init__.py`'s own established style. 21 shims created at
the old flat locations. The mandatory sweep across the whole codebase
found 7 already-migrated `awci.*` modules (from Phases 1-10) depending on
thermodynamics modules moved in this phase - repointed to
`acf.science.thermodynamics.*` directly: `awci/hazards/visibility.py`,
`awci/hazards/theta_e.py`, `awci/hazards/hydrometeor_phase.py`,
`awci/hazards/dust.py`, `awci/hazards/ceiling.py`,
`awci/complexity/metar_verification.py`,
`awci/complexity/workstation_fields.py`. Six still-flat `acf.science.*`
siblings (`cin.py`, `lcl.py`, `cape.py`, `dynamics.py`, `radiosonde.py`,
`moisture.py`, `laws/thermodynamics.py`) also reference the moved
modules - deliberately left importing the `acf.science.<module>` shim
unchanged, exactly as every external caller outside the package being
moved has been treated throughout this whole reorganization effort; they
will be cleaned up naturally when each of *them* is moved in a future
phase (`cape.py`/`cin.py`/`lcl.py` likely into `science/convection/`,
matching the blueprint's own next-named subdomain).

**Verified, not assumed**: `ruff check` clean (the same single,
already-existing, pre-migration unused import in `awci_footer.py` noted in
§2k - untouched, unrelated); `mypy` clean (22 source files); identity
confirmed programmatically for all 21 modules plus the package `__init__`;
full test collection under xvfb - 4977 tests, 0 errors; a targeted sweep
across every thermodynamics/moisture/convection-adjacent keyword (`-k
"thermodynamic or potential_temperature or ... or cape or cin or lcl"`,
non-GUI) passed 472/472 (9 skipped); a new
`tests/test_science_thermodynamics_reorganization.py` (25 tests) locks in
the re-export identity for all 21 modules, the package's own `__all__`,
the internal cross-reference, and the 7 cross-package fixes into
already-migrated `awci.*` code.

**A real bug found and fixed during §4b, retroactively affecting this
phase too**: `thermodynamics.py` was moved into a package of the exact
same name (`acf.science.thermodynamics`), and a flat shim file was
written at the old `src/acf/science/thermodynamics.py` path - but a
regular package always shadows a same-named module in CPython's import
resolution, so that shim file was permanently unreachable, dead code
from the moment it was written; every real caller happened to keep
working anyway only because the package's own `__init__.py` already
re-exports `Thermodynamics` directly (the one name any real caller ever
imported from that bare path). Found while investigating §4b's own,
identical `stability.py`/`science.stability` collision. Fixed by
deleting the dead `thermodynamics.py` shim file entirely and updating
`tests/test_science_thermodynamics_reorganization.py` to lock in the
package-level re-export instead of a nonexistent flat one.

### 4b. Phase 2: `science/stability/` and `science/convection/` (2026-09-21)

**Placement**: 7 real modules map to the blueprint's `science/stability/`
subdomain by content: `stability.py` (a composite `Stability` index
aggregator - the closest real match to the blueprint's illustrative
`stability_diagnostics.py`), `bulk_richardson_number.py`, `k_index.py`,
`sweat_index.py`, `total_totals.py`, `lifted_index.py`,
`showalter_index.py`. 8 real modules map to `science/convection/`:
`cape.py`, `cin.py`, `lcl.py`, `lfc.py`, `parcel_ascent.py` (the real
match for the blueprint's illustrative `parcel.py`),
`storm_relative_helicity.py`, `storm_motion.py`, `bulk_wind_shear.py` -
the last three are not named in the blueprint's own smaller sketch, but
are real, standard severe-convective-storm kinematic diagnostics (SRH,
storm motion, bulk shear) computed alongside CAPE/CIN in operational
forecasting; placed here by real role, a disclosed decision.

**Investigation, before any move**: `stability.py`'s own `Stability`
class is a real composite aggregator that reuses `CAPE`, `CIN`, `LCL`,
`KIndex`, `LiftedIndex`, `ShowalterIndex`, `StormRelativeHelicity`,
`SWEATIndex`, `TotalTotals` directly - a genuine cross-domain dependency
spanning both new packages, confirmed by reading its actual imports, not
assumed from the filename. `cape.py`/`cin.py` depend on
`VirtualTemperature` and `lcl.py` on `EquivalentPotentialTemperature` -
both already moved to `science/thermodynamics/` in §4a, so these
references were repointed directly rather than left on the
`acf.science.thermodynamics` shim. `parcel_ascent.py` depends on
`radiosonde.py` (still flat, not part of this phase) - deliberately left
on the shim, same treatment as every other still-flat sibling. No
`__all__` restrictions, no deferred imports, no underscore-prefixed
whitebox test imports found in any of the 15 modules. External fan-in
1-10 dependents per module (`cape.py` highest, 10).

**A real bug found and fixed, not just a migration artifact**: moving
`stability.py` into a package also named `stability` reproduces the exact
same shadowing bug retroactively found in `thermodynamics.py` (§4a's own
note above) - a flat `stability.py` shim would be permanently
unreachable, dead code. No such shim was written this time; the
package's own `__init__.py` re-exports `Stability` directly instead,
which is what the sole real caller (`radiosonde.py`) and the tests
already use. This is now the established pattern for any future
self-named aggregator module: check whether the flat module and its own
target package would share a name *before* writing a flat shim for it,
and skip the shim in favor of the package's own re-export when they do.

**Execution**: all 15 files physically moved via `git mv`. `stability.py`'s
9 internal imports repointed - 4 to same-package siblings
(`acf.science.stability.{k_index,lifted_index,showalter_index,
sweat_index,total_totals}`), 4 to the sibling `convection` package
(`acf.science.convection.{cape,cin,lcl,storm_relative_helicity}`).
`cape.py`/`cin.py`/`lcl.py` repointed to
`acf.science.thermodynamics.*` directly. Two `__init__.py` files written
re-exporting all real classes with a real `__all__` each, mirroring
`science/clouds/__init__.py`'s established style. 14 shims created at the
old flat locations (all except `stability.py`, per the bug fix above).
The mandatory sweep across the whole codebase found 2 already-migrated
`awci.*` modules depending on modules moved in this phase - repointed to
`acf.science.{stability,convection}.*` directly:
`awci/hazards/wind_shear.py` (`BulkWindShear`) and
`awci/complexity/workstation_fields.py` (`LCL`, `StormMotion`,
`StormRelativeHelicity`). 4 still-flat `acf.science.*` siblings
(`laws/thermodynamics.py`, `laws/dynamics.py`,
`encyclopedia/convection_extended.py`, `radiosonde.py`) also reference
the moved modules - deliberately left on the shim, to be cleaned up when
each of them is itself moved in a future phase.

**Verified, not assumed**: `ruff check`/`mypy` clean (17 source files
across both packages); identity confirmed programmatically for all 15
modules (14 via their flat shim, `Stability` via the package directly)
plus both packages' own `__all__`; full test collection under xvfb - 5002
tests, 0 errors; a targeted stability/convection sweep (non-GUI) passed
252/252 (6 skipped); the 3 directly-relevant GUI test files (workstation
thermodynamics/convection/stability_indices) passed 16/16. A new
`tests/test_science_stability_convection_reorganization.py` (21 tests)
locks in the re-export identities, both packages' `__all__`, the
`Stability`-via-package special case, the cross-domain `Stability`↔
`convection` dependency, the `cape`/`cin`/`lcl`↔`thermodynamics`
dependencies, and the 2 cross-package fixes into already-migrated
`awci.*` code.

**What remains for item 2** (before §4c below): the other 16 blueprint
subdomains (`constants/`, `dynamics/`, `radiation/`, `microphysics/`,
`turbulence/`, `boundary_layer/`, `clouds/` [already a real subpackage,
but not yet reconciled with the blueprint's own `clouds/` role],
`precipitation/`, `atmospheric_composition/`, `ocean/`, `hydrology/`,
`cryosphere/`, `land_surface/`, `carbon_cycle/`, `climate/`,
`diagnostics/`), the entire `parameters/` reorganization (including the
`acf.science.parameters` vs `acf.parameters` duplicate-naming question,
item 4 above), and reconciling the 6 other already-existing
non-blueprint-named `science/` subpackages
(`encyclopedia/`, `knowledge_graph/`, `laws/`, `observations/`,
`physics_ai/` - `clouds/` counted above).

### 4c. Phase 3: `science/dynamics/` (2026-09-21)

**Placement**: 6 real modules map to the blueprint's `science/dynamics/`
subdomain directly by content: `dynamics.py` (a composite `Dynamics`
class grouping all dynamics diagnostics, mirroring `stability.py`'s own
aggregator role from §4b), `divergence.py`, `vorticity.py`,
`frontogenesis.py`, `fronts.py` (`AirMass`/`FrontType`/`FrontMovement`,
three real classes in one module), `potential_vorticity.py`.

**Investigation, before any move**: `dynamics.py` depends on 4 same-batch
siblings (`divergence.py`, `frontogenesis.py`, `potential_vorticity.py`,
`vorticity.py`) plus 2 already-migrated `science/thermodynamics/`
modules from §4a (`geopotential_height.py`, `hypsometric_equation.py`) -
confirmed by reading its real imports, exactly as anticipated when this
phase was scoped at the end of §4b. No `__all__` restrictions, no
deferred imports, no underscore-prefixed whitebox test imports found in
any of the 6 modules. External fan-in 1-9 dependents per module
(`divergence.py` highest, 9).

**Applying the established self-naming-collision check** (from §4a/§4b's
bug-fix note): `dynamics.py` shares its own name with the new
`acf.science.dynamics` package, so - per the now-established rule - no
flat shim was written for it; the package's own `__init__.py`
re-exports `Dynamics` directly instead, exactly like
`Thermodynamics`/`Stability` before it. Confirmed the one real bare-path
caller (`acf/science/engine.py`, `from acf.science.dynamics import
Dynamics`) already resolves correctly through the package for this exact
reason.

**Execution**: all 6 files physically moved via `git mv`.
`dynamics.py`'s 6 internal imports repointed - 4 to same-package
siblings, 2 to `acf.science.thermodynamics.*` directly. `__init__.py`
written re-exporting all 6 real classes (`Dynamics`, `Divergence`,
`Vorticity`, `Frontogenesis`, `AirMass`, `FrontType`, `FrontMovement` -
7 names from 6 modules, `fronts.py` contributing 3) with a real
`__all__`. 5 shims created at the old flat locations (all except
`dynamics.py`). The mandatory sweep found 1 already-migrated `awci.*`
module depending on a module moved in this phase -
`awci/complexity/workstation_fields.py` (`Divergence`) - repointed to
`acf.science.dynamics.divergence` directly. 2 still-flat `acf.science.*`
siblings (`synoptic.py`, and `engine.py`'s own bare-path `Dynamics`
import, already correctly resolving through the package) left
unchanged.

**Verified, not assumed**: `ruff check`/`mypy` clean (7 source files);
identity confirmed programmatically for all 5 shimmed modules (`Dynamics`
via the package directly) plus the package's own `__all__`; full test
collection under xvfb - 5023 tests, 0 errors; a targeted
dynamics/divergence/vorticity/frontogenesis/fronts/potential_vorticity/
synoptic sweep (non-GUI) passed 554/554. A new
`tests/test_science_dynamics_reorganization.py` (10 tests) locks in the
re-export identities, the `Dynamics`-via-package special case, the
cross-package dependency into `science/thermodynamics/`, and the 1
cross-package fix into already-migrated `awci.*` code.

### 4d. Phase 4: `science/constants/` (2026-09-21)

**Placement**: the single flat `constants.py` (23 real physical/numerical
constants: gas constants, latent heats, Earth/reference-atmosphere
values, a disclosed floating-point tolerance - no classes, a true leaf)
maps directly to the blueprint's own `science/constants/` layer.

**A notably simpler phase than §4a-§4c**: `constants.py` has zero
internal `acf.science.*` imports (nothing to repoint) and, being purely
data (constants, not classes), its real callers already spell the import
exactly as `from acf.science.constants import G` - the *package's* own
future canonical path, not a deeper submodule path. Since `constants.py`
shares its own name with its new package (the same self-naming collision
already found and fixed in §4a/§4b/§4c), there is no flat shim - the
package's own `__init__.py` re-exports all 23 constants directly. Because
the import path `acf.science.constants` itself never changes (only *what*
resolves it - a package instead of a flat module - changes, transparently
to every caller), **zero external files needed any edit** for this
phase - the only phase so far where that is true. Confirmed by grepping
every real caller (21 files: 16 across `science/` including 6
already-migrated `thermodynamics/`/`convection/` modules, 1 already-
migrated `awci/complexity/workstation_fields.py`, and 4 test files) and
verifying none needs a code change.

**Execution**: `constants.py` physically moved via `git mv` into
`src/acf/science/constants/constants.py`. `__init__.py` written
re-exporting all 23 real constants with a real `__all__`.

**Verified, not assumed**: `ruff check`/`mypy` clean (2 source files);
identity confirmed programmatically for all 23 constants (both by name
and by `__all__` completeness against the real module's own public
names); full test collection under xvfb - 5033 tests, 0 errors; a broad
targeted sweep across every constants-adjacent domain (`-k "constant or
visibility or cin or lcl or cape or hypsometric or ... or terrain"`,
non-GUI) passed 443/443 (6 skipped). A new
`tests/test_science_constants_reorganization.py` (5 tests) locks in the
package-level re-export, the `__all__` completeness, the absence of a
dead flat shim, and that real callers across `science/` and `awci/`
still resolve to the exact same objects.

### 4e. Phase 5: `science/radiation/` (2026-09-21) - and why there is no `microphysics/` counterpart

**Placement**: the single flat `radiation.py` (4 real classes -
`StefanBoltzmann`, `PlanckLaw`, `BeerLambert`, `SolarPosition` - plus 5
real physical constants: `BOLTZMANN_K`, `PLANCK_H`, `SOLAR_CONSTANT_S0`,
`SPEED_OF_LIGHT_C`, `STEFAN_BOLTZMANN_SIGMA`) maps directly to the
blueprint's own `science/radiation/` layer. No internal
`acf.science.*` imports, a true leaf.

**Investigated and deliberately not done: `microphysics/`.** The user
asked to continue with both `radiation/` and `microphysics/`. No flat
top-level `microphysics.py` module exists anywhere under `acf.science` -
confirmed by grep, not assumed. The only real microphysics content in the
codebase is `CloudMicrophysicsEngine`, already living in
`science/clouds/microphysics.py`, inside the already-existing `clouds/`
subpackage (one of the 6 non-blueprint-named subpackages named at the end
of every phase's "what remains" note). Moving or splitting that single
file out of `clouds/` into a new, separate `microphysics/` package would
be a real architecture decision about whether `clouds/` and
`microphysics/` should be reconciled as the blueprint's own two distinct
top-level subdomains, or whether cloud microphysics stays inside the
already-coherent `clouds/` package (mirroring, e.g., how AWCI's
`convective_energy.py`/`theta_e.py`/`updraft.py` were deliberately kept
together in `awci/hazards/` in Phases 6-7 rather than split out) - not a
mechanical single-file move like every other phase so far. Left
untouched and flagged here rather than unilaterally restructured.

**Applying the established self-naming-collision check**: `radiation.py`
shares its own name with the new `acf.science.radiation` package, so - per
the rule from §4a-§4d - no flat shim was written; the package's own
`__init__.py` re-exports all 9 real names (4 classes + 5 constants)
directly. The one real caller of the bare path
(`science/laws/radiation.py` - a distinct, coincidentally same-named
sibling module in the `laws/` subpackage, importing `PlanckLaw` and
`SolarPosition`) needed no code change, exactly like `constants.py` in
§4d: the import path itself never changed.

**Execution**: `radiation.py` physically moved via `git mv` into
`src/acf/science/radiation/radiation.py`. `__init__.py` written
re-exporting all 9 real names (the initial pass caught only the 4
classes; a second, more careful pass over `vars()` found the 5 module-
level physical constants and the stdlib `math` import that needed
excluding from `__all__` - the same "check every public name against the
real module, not an assumed subset" discipline applied throughout this
whole reorganization effort).

**Verified, not assumed**: `ruff check`/`mypy` clean (2 source files);
identity confirmed programmatically for all 9 real names and `__all__`
completeness against the real module's own public API (excluding the
stdlib `math` import); full test collection under xvfb - 5038 tests, 0
errors; a targeted radiation/Planck/Stefan-Boltzmann/Beer-Lambert/solar-
position sweep (non-GUI) passed 90/90. A new
`tests/test_science_radiation_reorganization.py` (5 tests) locks in the
package-level re-export, `__all__` completeness, the absence of a dead
flat shim, and that the real `laws/radiation.py` caller still resolves
correctly - plus a documented note explaining why `microphysics/` was
not done this phase.

Both migration efforts (§2, the AWCI separate-package migration, and §4,
the ACF `science/`/`parameters/` reorganization) follow the same proven
method: real investigation before any move, `git mv` + backward-
compatible shims, a mandatory codebase-wide sweep for cross-package
references, and full verification (ruff/mypy/identity checks/targeted and
broad test sweeps/collection) before every commit.
