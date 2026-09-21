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
| `core/{application,configuration,context,exceptions,logging,lifecycle,registry,events,plugins,dependencies,environment,version}.py` | 🟡 `src/acf/core/` exists with `application.py`, `bootstrap.py`, `config.py`, `constants.py`, `environment.py`, `exceptions.py`, `logger.py`, `metadata.py`, `parameter.py`, `parameter_registry.py`, `plugin_manager.py`, `service_manager.py`, `version.py`, `default_parameters.py`, plus a `contracts/` subpackage. Real overlap on config/exceptions/logging/environment/version/plugins. **`lifecycle.py`/`registry.py`/`events.py`/`context.py` added 2026-09-21** — see §2ab: `Registry`/`Lifecycle` are real aliases for `ServiceManager`/`Bootstrap`; `EventBus`/`ApplicationContext` are genuinely new, generic content. `application.py` exists but is confirmed dead code (`docs/STATUS.md`'s own NOTE: nothing constructs it; `acf-gui` boots `ACFWorkstationWindow` directly). |
| `utils/{filesystem,paths,datetime,units,validation,serialization,hashing,caching,profiling,concurrency,numerical,decorators}.py` | 🟡 `src/acf/utils/` exists with `time.py`, `paths.py`, `system.py`, `validators.py`, `files.py`. Real overlap on paths/validation/time. **`serialization.py`/`hashing.py`/`decorators.py` added 2026-09-21** — see §2ac. `units.py` deliberately not duplicated (units live in `acf.normalization`); `caching.py`/`profiling.py`/`concurrency.py`/`numerical.py` deliberately not built — no real, disclosed caller need exists for any of them yet. |

### L1 — Scientific formulations & standards

| Blueprint | Current reality |
|---|---|
| `science/` with 19 subdomains (`thermodynamics/`, `dynamics/`, `stability/`, `convection/`, `radiation/`, `microphysics/`, `turbulence/`, `boundary_layer/`, `clouds/`, `precipitation/`, `atmospheric_composition/`, `ocean/`, `hydrology/`, `cryosphere/`, `land_surface/`, `carbon_cycle/`, `climate/`, `diagnostics/`, `constants/`) as subpackages | ✅ **Reorganized 2026-09-21** (Phases 1-7, §4a-§4g) — `src/acf/science/` now has real per-domain subpackages for 11 of the 19 named subdomains: `thermodynamics/` (22 modules, including the composite `moisture.py`), `stability/`, `convection/` (9, including `severe_weather.py`), `dynamics/` (9, including `synoptic.py`/`cyclones.py`/`wind.py`), `constants/`, `radiation/`, `turbulence/`, `boundary_layer/`, `precipitation/`, `diagnostics/`, `climate/` — each with `acf.science.<module>` kept as a real backward-compatible re-export (except for the handful of modules that collide with their own new package name, e.g. `thermodynamics.py`/`stability.py`/`dynamics.py`/`constants.py`/`radiation.py`/`boundary_layer.py`/`precipitation.py`/`diagnostics.py`, where the package's own `__init__.py` re-exports directly instead — see §4a-§4g for the full, per-module rationale). `clouds/` (§4h) turns out to already be the blueprint's own `clouds/` subdomain, just not previously recognized as such — no move needed. `microphysics/`, `atmospheric_composition/`, `carbon_cycle/`, `land_surface/`, `cryosphere/`, `ocean/`, `hydrology/` remain without a dedicated `science/` subpackage — confirmed genuinely absent or, for the last two, deliberately left as the separate, already-coherent top-level `src/acf/ocean/`/`src/acf/hydrology/` packages (§4h's own recommendation, not executed as a move). `encyclopedia/`, `knowledge_graph/`, `laws/`, `observations/`, `physics_ai/` remain as real ACF-specific subpackages with no blueprint subdomain counterpart (§4h). |
| `parameters/` — a real structured catalog, historical inventory ~152 parametrization modules | 🟡 `src/acf/parameters/` exists (`units.py`, `categories.py`, `search.py`, `converter.py`, `aliases.py`, `hub.py`, `registry.py`, `parameter.py`, `index.py`, `catalog.py`, `validator.py`) — a real registry/catalog engine, but organized as one flat parameter-management layer, not the blueprint's per-domain (`atmosphere/ocean/land/cryosphere/radiation/microphysics/turbulence/convection/chemistry/parameterizations/`) subpackage split. No verified count of "152 parametrization modules" exists in the current tree. **Investigated 2026-09-21 (§4h)**: not a simple reorganization candidate like `science/` above - there are 4 separate, real, independently-used namespaces touching this same vocabulary (`acf.parameters`, `acf.science.parameters`, `acf.catalog`, `acf.catalogs`) with zero cross-imports between them; unifying them is a real design decision put to the user rather than executed. |
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
| `ai/` | ✅ `src/acf/ai/` is real and broad: `engine.py`, `cloud_reasoning.py`, plus `data_assimilation/`, `uncertainty/`, `physics_informed/`, `ensemble/`, `xai/`, `emergency_assistant/`, `forecast/`, `analyzers/`, `atmosphere_explorer/`, `digital_twin/`, `decision_support/`, `neural_models/`, `alerts/`, `simulation/`, `plugins/`. No dedicated `ai/agents/` subpackage. `ai/rag/` was fully absent until **2026-09-21, when `src/awci/ai/rag/` was built** (see §2n below) — a real, lexical/BM25 evidence-retrieval layer over `awci.knowledge.*`, deliberately placed under `awci/ai/` (the AWCI-specific location named in `awci_reference_architecture.md` §14) rather than `acf.ai`, since its corpus is scoped to AWCI-specific, ICAO/WMO-cited knowledge only. `acf.ai`'s own general-purpose RAG gap remains real and unaddressed. |
| `awci/` (historical, layer 3) | See §2 below — AWCI is intentionally not part of ACF's own layer 3 per the "AWCI separation" decision both blueprints agree on. |

### L4 — Presentation & applications

| Blueprint | Current reality |
|---|---|
| `gui/` | ✅ `src/acf/gui/` is real and is the actual live application (`app.py` is the real `acf-gui` entry point, launching `ACFWorkstationWindow` — see `docs/STATUS.md`'s 2026-09-21 ESOC-removal entry). Contains `theme.py`, `menu.py`, `statusbar.py`, `toolbar.py`, `earth_system_operations.py`, `bootstrap.py`, `single_instance.py`, `splash.py`, plus `layer_panel/`, `docks/`, `map/`, `dialogs/`, `resources/`, `workers/`, `dashboard/`, `widgets/` subpackages. The blueprint's flat `gui/main_window.py` central-file convention does not match reality: the live default window is `acf.gui.dashboard.acf_workstation_window.ACFWorkstationWindow`; `acf.gui.main_window` is confirmed dead legacy code (removed 2026-09-21 alongside ESOC, since it subclassed the now-deleted `ESOCWindow`). |
| `dashboard/` | ✅ Two real dashboard trees exist: `src/acf/dashboard/` (blueprint-shaped: `manager.py`, `window.py`, `dashboard.py`, `layout.py`, `widgets.py`, `panels/` — but itself unreachable from the running app today, a pre-existing, disclosed state, see that module's own docstring) and the much larger, actually-live `src/acf/gui/dashboard/` (ACF Workstation and ~30 other panel/window modules - the AWCI dashboard itself physically moved out to `src/awci/dashboard/` on 2026-09-21, §2k; `acf.gui.dashboard.awci_*` now holds only re-export shims, `acf.dashboard.window.py` still launches `AWCIDashboardWindow` via a deferred import). |
| `api/` | 🟡 `src/acf/api/` exists but is minimal (`api.py` only) versus the blueprint's `routes/{data,models,diagnostics,maps,visualization,ai,reports,system}.py` + `schemas/`/`services/`/`middleware/` split. A separate, more built-out `src/acf/web/` package also exists (not in the blueprint's naming) — worth reconciling in any real migration. |
| `alerts/` | 🟡 `src/acf/alerts/` exists (`warning_engine.py`) — real but much thinner than the blueprint's `engine/rules/thresholds/events/notification/severity` split. |
| `reports/` | 🟡 `src/acf/reports/` exists with a `briefings/` subpackage, but no `generator.py`/`scientific_report.py`/`model_report.py`/`diagnostic_report.py`/`export.py`/`templates/` as named. |

### Project root

`tests/`, `docs/`, `resources/`, `scripts/`, `examples/`, `tools/`, `assets/`,
`configs/` all exist at the repository root today, though none has been
individually re-verified against the blueprint's own internal layout, except
`tools/acfctl/` — **built 2026-09-21** (see §2q below): a real, tested
`acfctl start|stop|status|report` operational control point, managing the 3
real, already-registered `acf-gui`/`acf-web`/`acf-awci` console-script apps
as real OS subprocesses.

## 2. AWCI — current state vs. the separate-project blueprint

**Headline finding, as originally surveyed: `src/awci/` (a separate
top-level package) did not exist.** All AWCI-related code used to live
inside `src/acf/`, split mainly across `src/acf/awci/` (the complexity/
hazard computation itself) and `src/acf/aviation/` (aviation domain
knowledge), plus the live GUI dashboard under
`src/acf/gui/dashboard/awci_*.py`.

**This has since been done.** `src/awci/` is now a real, separate
top-level package (Phases 1-10, §2a-§2k, all 2026-09-21):
`awci/hazards/`, `awci/complexity/`, `awci/data/`, `awci/comparison/`,
`awci/airport/` (from the former `src/acf/awci/`), `awci/knowledge/`
(from the former `src/acf/aviation/`), and `awci/dashboard/` (from the
former `src/acf/gui/dashboard/awci_*.py`, 29 modules). `src/acf/awci/`,
`src/acf/aviation/`, and the AWCI modules of `src/acf/gui/dashboard/` now
hold nothing but backward-compatible re-export shims. The table below is
kept in its original per-layer form (useful for seeing which blueprint
layers still have no real equivalent at all), but every row referencing a
since-migrated path has been updated to point at its real, current
`awci.*` location.

| Blueprint layer | Closest current equivalent |
|---|---|
| `awci/core/` | ✅ **Built 2026-09-21** — see §2z: `AWCIError` exception hierarchy (real sibling of `ACFError`), `EventBus`/`Event` (real app-lifecycle pub/sub, same discipline as `HookRegistry`/`AlertNotifier`), `ServiceRegistry` (real alias for `acf.core.service_manager.ServiceManager`), `AWCIContext`, `AWCILifecycle`, `AWCIApplication` (headless, distinct from the GUI-coupled `acf.awci_app` launcher), `configuration.py` (re-exports the already-real `awci.complexity.config_loader`), `logging.py` (`logs/awci.log` filtered sink). `dependencies.py` deliberately not a separate file — see `registry.py`'s own docstring. |
| `awci/knowledge/` (aviation/meteorology/regulations/hazards/knowledge_graph) | ✅ **Migrated 2026-09-21** — see §2j. Real, physically moved to `src/awci/knowledge/`: `airports/airport_database.py`, `icao/{live_source,metar_decoder,sigmet_decoder,taf_decoder,products}.py`, `performance/aircraft_performance.py`, `routing/flight_routing.py`, `hazards/aviation_hazards.py`, `graphics/cross_section.py`, with `acf.aviation.<x>` kept as a real backward-compatible re-export for all 10 modules plus the package itself. `knowledge_graph/` **built 2026-09-21** — see §2w: `entities.py` (10 real, cited aviation-hazard `KnowledgeNode`s) + `graph.py` (`build_aviation_knowledge_graph()`, seeding the already-real `acf.science.encyclopedia.knowledge_graph.KnowledgeGraphEngine` rather than a second engine); `relations.py`/`ontology.py` deliberately not separate files (see §2w). |
| `awci/data/` + `data/connectors/` | 🟡 **`awci/data/` created 2026-09-21** (see §2e, §2i below), now holding `archive_field.py` (real ALADIN RESTOR archive ingestion via EPyGrAM) and the 3 generic model-import adapters `model_import.py`/`model_import_cross_section.py`/`model_import_evolution.py`. `awci/data/connectors/` **built 2026-09-21** — see §2x: `pirep_reports.py`, `nexrad_stations.py`, `eumetsat_mtg.py` migrated from `acf.connectors` (the 3 already established as aviation-relevant, reused by `awci.observations.hub`), with `acf.connectors.<x>` kept as a real backward-compatible re-export. `argo_floats.py` (ocean, not aviation), `wmo_wis.py` (generic WMO bulletin-header parser) and `live_connectors.py` (generic, disclosed-unconnected NWP-model registry) deliberately stay under `acf.connectors` — not aviation-specific. SIGMET/AIRMET/NOTAM/TAF connectors are decoders under `awci.knowledge.icao` (moved from `acf.aviation.icao` in §2j), not separate `connectors/` modules. |
| `awci/observations/` | 🟡 **`hub.py` built 2026-09-21** (see §2r below) — real, single aggregation point over `awci.knowledge.icao.live_source` (METAR/TAF/SIGMET) + `acf.connectors.{pirep_reports,nexrad_stations,eumetsat_mtg}` (PIREP/radar/satellite), all already-real connectors, never re-implemented. The blueprint's full 11-file package (`stations.py`/`metar.py`/per-source `parser/decoder/validator` subpackages) deliberately not built — real METAR/TAF/SIGMET decoding already exists elsewhere; duplicating it would not close a real gap. |
| `awci/forecast/` | ✅ `src/acf/forecast/` is real: `forecast_engine.py`, `engine.py` — used across the AWCI dashboard's real per-model runs. |
| `awci/vertical/` | ✅ Real and substantial — `awci.complexity.vertical_field` (**migrated 2026-09-21**, see §2d below), `acf.gui.dashboard.acf_workstation_sounding_panel` (ACF's own sounding panel, correctly still in `acf.gui` - real, intentional reuse by the AWCI dashboard, not something that moved), and `awci.dashboard`'s own `AWCIVerticalSoundingWidget`/`AWCIVerticalProfile` (moved from `acf.gui.dashboard` in §2k) cover profile/sounding/wind-shear/icing-profile territory, just not under a dedicated `awci/vertical/` package with the blueprint's exact file split (skew_t/tephigram/emagram/stuve as separate diagram modules). **Deliberately not placed under a new `awci/vertical/` package**: despite its name, `vertical_field.py` is not the blueprint's general-purpose sounding/diagram engine — it is `AWCICalculator` applied along a vertical profile (its own docstring: "same real complexity computation as spatial_field.py exactly"), so it was migrated alongside `calculator.py`/`spatial_field.py` into `awci/complexity/` instead, as one coherent field-computation unit. |
| `awci/hazards/` (one module per hazard) | ✅ **Migrated 2026-09-21** — see §2b, §2g, §2h and §2i below. Physically moved to `src/awci/hazards/{icing_temperature_range,ceiling,visibility,dust,microburst,volcanic_ash,wind_shear,cat_turbulence,orographic_froude,hydrometeor_phase,convective_energy,theta_e,updraft,terrain_elevation}.py` (14 modules), with `acf.awci.<module>` kept as a real backward-compatible re-export. `spatial_field.py` now imports all 9 of its real hazard/thermo dependencies directly from `awci.hazards`, none through the `acf.awci` shim anymore. This is now a literal, not just conceptual, match to the blueprint's `awci/hazards/` (still flat rather than one-subpackage-per-hazard, which the blueprint itself is ambiguous about — it lists both a flat file-per-hazard example and per-hazard subdirectories). |
| `awci/complexity/` (the actual AWCI score) | ✅ **Migrated 2026-09-21** — see §2c and §2i below. `AWCICalculator` (the actual scoring/aggregation engine), `WeightsManager`, `Normalizer`, and `scientific_status` physically moved to `src/awci/complexity/`, joined by `scale_classification.py`/`wind_classification.py`/`spatial_field.py`/`vertical_field.py`/`temporal_field.py` (Phases 3-5) and then, in the single largest phase (§2i), 14 more real modules: `calibration.py`, `config_loader.py`, `diagnostic_registry.py`, `execution_report.py`, `forecaster_validation.py`, `input_adapter.py`, `metar_verification.py`, `method_comparison.py`, `path_sampling.py`, `pipeline.py`, `result.py`, `run_report.py`, `validation_cases.py`, `workstation_fields.py` — with `acf.awci.<module>` kept as a real backward-compatible re-export for all 23. Matches the blueprint's core principle (traceable scientific factors, not an arbitrary score) — this has been the subject of extensive audit across this session and prior ones. **As of Phase 8, `src/acf/awci/` contains nothing but re-export shims and `__init__.py` — every real line of AWCI complexity-engine code now lives under `src/awci/`.** |
| `awci/comparison/` + `awci/consensus/` | 🟡 **`awci/comparison/` created 2026-09-21** (see §2i below) with `multi_model_fusion.py` (real full-field multi-model fusion) and `regridding.py` (real generic grid regridding, its one real dependent). This is distinct from `ModelConsensusEngine` (see the "corrected 2026-09-21" note directly above from an earlier pass of this same document): the real `ModelConsensusEngine` lives in `src/acf/visualization/ai_forecast_center/model_consensus_engine.py` (604 lines), a genuine non-GUI domain layer already reachable independently of the GUI — it is imported directly by `acf.awci.calculator`, `acf.awci.result`, `acf.awci.multi_model_fusion`, `acf.forecast.engine`, and `acf.core.contracts.uncertainty`, in addition to 9 GUI dashboard modules. The only real gap versus the blueprint for *that* module is its **location/naming**: it sits under `acf.visualization.ai_forecast_center` rather than `acf.models.comparison`/`acf.models.consensus`/`awci.comparison`. A literal move would need to update 15+ real importers (across science, awci, forecast, core.contracts and GUI) plus 5 test files — assessed 2026-09-21 as real, mechanical, but high-blast-radius work with no functional benefit, so deferred rather than done reflexively; see the gap-analysis conclusion below. |
| `awci/flight/` | 🟡 **`src/awci/flight/` created 2026-09-21** (see §2t below) with `waypoint.py` (real great-circle intermediate-point generation) and `route_weather.py` (real per-route weather briefing composing routing + waypoints + live weather). `src/awci/knowledge/routing/flight_routing.py` (moved from `acf.aviation.routing` in §2j) covers routing itself. `planning.py`/`corridor.py`/`altitude.py`/`flight_levels.py`/`departure.py`/`arrival.py`/`alternate.py` real content already exists elsewhere; `fuel_weather.py` would need a real aircraft-type fuel-burn model this codebase does not have. |
| `awci/airport/` | 🟡 **`awci/airport/` created 2026-09-21** (see §2i below) with its first real module, `airport.py` (real airport approach/departure corridor geometry), which now imports `AirportDatabase` directly from `awci.knowledge.airports.airport_database` (moved from `acf.aviation.airports` in §2j, see that section) rather than through a shim. **`runway.py`/`weather.py` added 2026-09-21** (see §2s below) — real per-runway wind assessment and a real per-airport weather snapshot, both thin compositions of already-real formulas. `terminal.py`/`operations.py`/`runway_condition.py`/`departure.py`/`arrival.py`/`disruption.py` remain unbuilt — each would need real data or a real, cited regulatory threshold this codebase does not have. Crosswind/ceiling/visibility computation already lives in `awci.hazards`/`awci.knowledge.performance.aircraft_performance` rather than duplicated blueprint-named files. |
| `awci/decision/` | 🟡 **Phase 1 built 2026-09-21** (`context.py`/`situation.py`/`recommendation.py`/`engine.py`, real, headless, tested - see §2m below). Deliberately real-core-only, user-confirmed scope: composes already-computed AWCI outputs and reuses the 3 already-cited real `flight_recommendations` entries; `risk_matrix.py`/`confidence.py`/`alternatives.py`/`scenario.py` are NOT built - each needs its own real, cited methodology first (e.g. ICAO Doc 9859 SMS for `risk_matrix.py`), not an invented one. |
| `awci/ai/` | 🟡 `awci/ai/rag/` **built 2026-09-21** (see §2n below) - real, headless, lexical BM25 evidence-retrieval over `awci.knowledge.*`, no new dependency, no network/LLM call. `assistant.py`/`agents/`/`knowledge/`/`reasoning/`/`anomaly_detection/`/`explanation/`/`summarization/`/`orchestration/` remain unbuilt. Still overlaps conceptually with `acf.ai.emergency_assistant`/`acf.ai.decision_support`/`acf.ai.xai` for those unbuilt pieces. |
| `awci/visualization/` (maps/complexity overlays) | ✅ Real — `acf.gui.map.map_layers` (e.g. `VolcanicAshLayer`, `MicroburstLayer`, correctly still ACF-side generic map infrastructure) and `awci.dashboard.awci_map_panel` (**moved from `acf.gui.dashboard` 2026-09-21, §2k**) — the latter now a real module inside `awci/`, though still coupled to the GUI layer, not a standalone visualization package. |
| `awci/dashboard/` | ✅ **Migrated 2026-09-21, §2k** — `src/awci/dashboard/awci_dashboard.py` and its 28 companion modules (`awci_topbar.py`, `awci_route_chart.py`, `awci_situation_panel.py`, `awci_model_spread_chart.py`, etc. - 29 real modules total) are the single most heavily tested part of the whole codebase, and now the blueprint's own literal, physically separate `awci/dashboard/` "application layer above everything else" (§16). `acf.gui.dashboard.awci_*` kept as a real backward-compatible re-export for every module. Reachable both embedded (`AWCIDashboard` widget) and as its own standalone process (`acf-awci` / `acf.awci_app`, confirmed independent per `tests/test_awci_app.py` - `acf.awci_app` itself deliberately not moved, a packaging-level decision distinct from moving the dashboard's implementation, see §2k). |
| `awci/reports/` | 🟡 **`src/awci/reports/` created 2026-09-21** (see §2u below) with `generator.py` and `aviation_report.py` — a real, composed report over `awci.airport.weather`+`awci.decision`+`awci.provenance`, no new computation. `src/awci/dashboard/awci_messages_panel.py`/`awci_execution_report_dialog.py`-style panels (moved from `acf.gui.dashboard` in §2k) still exist separately in the GUI. `flight_report.py`/`airport_report.py`/`hazard_report.py`/`complexity_report.py`/`model_report.py`/`verification_report.py`/`templates/` deliberately not built — `aviation_report.py` already covers the same real composed content. |
| `awci/api/` | ✅ **Built 2026-09-21** — see §3a: real FastAPI app (`create_app()`) with 6 of 11 named `routes/` modules, each wired to a real, already-working AWCI engine (`observations`, `airports`, `flights`, `hazards`, `complexity`, `reports`). `forecasts.py`/`models.py`/`profiles.py`/`maps.py`/`ai.py` deliberately not built — no real backing engine to expose for each, disclosed in `awci/api/__init__.py`. `schemas/`/`services/`/`middleware/` not separate subpackages — real dataclasses/domain packages/no real middleware need. |
| `awci/alerts/` | 🟡 **`src/awci/alerts/` created 2026-09-21** (see §2v below) with `engine.py` (real, headless `AlertEngine` over `awci.decision.situation.SituationSnapshot`) and `notifications.py` (real in-process `AlertNotifier`, same pattern as `awci.plugins.hooks.HookRegistry`). `awci.dashboard.awci_alerts_panel`-style UI (moved from `acf.gui.dashboard` in §2k) still exists separately. `rules.py`/`thresholds.py`/`severity.py`/`hazard_alerts.py`/`airport_alerts.py`/`route_alerts.py`/`complexity_alerts.py` deliberately not built — real content already exists (`awci.decision.situation`) or no real per-scope taxonomy exists to split on. |
| `awci/plugins/` | ✅ **Built 2026-09-21** (see §2p below) — all 5 files named in `awci_reference_architecture.md` §20 (`interface.py`/`registry.py`/`loader.py`/`hooks.py`/`manager.py`), real, tested, working extensibility infrastructure (register/get, on-disk discovery, lifecycle hooks). Zero real AWCI module has been adapted to implement the new `AWCIPlugin` interface yet — honestly disclosed, not fabricated. |
| `awci/workspace/` | ✅ **Built 2026-09-21** — see §2y: `AWCIProject`/`AWCI_PROJECT_FOLDERS` (subclasses `acf.workspace.project.Project`, real `.awciproj` extension + the blueprint's own folder layout: data/forecasts/flights/airports/hazards/maps/reports/analysis/exports/logs), `AWCIProjectSerializer` (reuses `ProjectSerializer.save()` unchanged, overrides `load()`), `AWCIWorkspaceManager` (subclasses `WorkspaceManager`, own `~/.awci/recent_projects.json`). `session.py`/`state.py` deliberately not built — no real, coherent AWCI session/state concept exists beyond what an open project + `awci.decision`/`awci.alerts` already provide. |
| `awci/provenance/` | 🟡 **Built 2026-09-21** (see §2o below) — all 7 files named in `awci_reference_architecture.md` §22 (`lineage.py`/`source.py`/`calculation.py`/`version.py`/`audit.py`/`reproducibility.py`), a real assembler over `AWCIResult`/`Provenance`/`scientific_status`/`WeightsManager` — never a new computation, never a persisted audit log/database (a disclosed scope limit, not a fabricated one). Provenance discipline was already a strong, repeatedly-enforced *convention* throughout this codebase (real formulas, real citations, "honest disclosure" of what's simulated vs. real — see `docs/STATUS.md` at length); this closes the gap of it never having a dedicated, queryable module. |

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

## 2l. The ACF→AWCI reverse-coupling decision (2026-09-21)

The user explicitly asked to continue with "le découplage ACF↔AWCI" - the
one real product/architecture decision §2k's own closing note left open:
whether `acf_workstation_*.py` (ACF's own general-purpose scientific
workstation) should keep reusing `AWCIMapPanel` as its map widget, or get
its own independent one.

**Investigation, before any decision**: grepping `src/acf/gui/dashboard/`
for `AWCIMapPanel`/`AWCICrossSection`/`AWCIEvolutionChart`/`AWCIGauge`/
`AWCIModelSpreadChart`/`AWCIRadar` confirmed the coupling is real and
load-bearing, not incidental: 13 of the 15 `acf_workstation_*.py` files
directly instantiate `AWCIMapPanel(...)` as their real map-rendering
widget (e.g. `acf_workstation_overview.py`, `acf_workstation_complexity.py`,
`acf_workstation_thermodynamics.py`). Reading `ACFOverviewPanel.__init__`
(the simplest caller) confirmed this reuse is deliberate and already
half-mitigated: it constructs `AWCIMapPanel("ATMOSPHERIC STATE",
show_legend=False, show_info_boxes=False, show_demo_fallback=False)`,
explicitly disabling every AWCI-specific chrome element via constructor
flags `AWCIMapPanel` already exposes for exactly this "AWCI-free ACF
Scientific Workstation" use case (see that class's own
`show_demo_fallback` docstring, added 2026-09-04 for this exact purpose).

**Full read of `awci.dashboard.awci_map_panel.AWCIMapPanel`** (1518 lines)
before proposing any extraction boundary - this was not assumed from the
constructor-flag surface alone. Finding: `update_data()`, the panel's
real redraw method, is itself ~350 lines that genuinely interleave generic
Cartopy machinery (stock_img/COASTLINE/BORDERS basemap, the main
`contourf`, colorbar add/remove with its own documented
`figure.delaxes()` workaround for a real matplotlib cleanup bug, zoom/pan
extent application) with AWCI-specific business logic (the synthetic
demo-pattern fallback, the 9-entry `_EXTRA_LAYER_SPECS` table wired
directly to `awci.hazards.*` formulas, the "Model Disagreement" async
engine hookup, flight-path/aircraft-glyph/city-label drawing, the AWCI
SCALE legend, the RENDERED/FLIGHT LEVEL info boxes) - with no existing
seam between the two. Splitting them would mean rewriting this method
into a generic-base-class redraw path plus AWCI-specific override hooks,
carefully preserving: the exact Cartopy/matplotlib artist rebuild order
and alpha handling, the weakref+`shiboken6.isValid()` MTG-basemap-update
guard (a real, already-documented use-after-free fix), the real
click-vs-drag double-delivery guard in `mouseReleaseEvent()` (a real,
already-documented PySide6/matplotlib double-event-delivery fix), and the
lazy-build/opacity semantics of the extra-layer contours - across 7
dedicated test files (`tests/test_awci_map_panel_*.py`) plus every test
touching the 13 `acf_workstation_*.py` callers plus the relevant
`tests/gui/` suite.

**Decision (user-confirmed after this investigation was reported)**:
**documented and accepted as a disclosed trade-off, no code changed.**
The reverse coupling is real (an architecturally "backwards" dependency -
ACF, the general framework, importing a class named and designed for
AWCI, one specific vertical application built on top of it) but it is
already **functionally neutralized**: every ACF caller disables 100% of
the AWCI-specific chrome via the constructor flags `AWCIMapPanel` already
provides for this purpose, and reuses only the generic Cartopy render/
zoom/pan/click-to-point/export machinery. A full extraction into a clean
generic base class would fix the dependency *direction* but deliver no
functional or scientific benefit to either ACF or AWCI today, at a real,
non-trivial regression risk (rewriting a 350-line method with several
already-fixed, subtle Qt/matplotlib bugs baked into it, re-validated
across 7+13+ files and their test suites) - not a favorable risk/reward
trade for a purity-only refactor on a working, already-heavily-tested,
production GUI component. Per this project's own general rule ("minimize
changes susceptible of breaking existing [functionality]"), the coupling
stays as-is.

**If this is revisited later**: the natural, lower-risk extraction
boundary identified during this investigation is the truly self-contained
generic surface already implemented as isolated methods with no AWCI-
specific state reads - `zoom_in`/`zoom_out`/`reset_view`/`pan*`/
`_apply_camera_extent` (camera/extent), `mousePressEvent`/
`mouseReleaseEvent`/`_pixel_to_lonlat`/`pointClicked` (click-to-point),
and `_export_png`/`_export_svg`/`_export_csv`/`_export_json`
(export) - none of these three groups touch `_EXTRA_LAYER_SPECS`,
`awci_grid()`, or any other AWCI-specific data source. `update_data()`
itself is the one real blocker to a *complete* extraction and would need
to be split first were this revisited.

## 2m. The AWCI decision-support engine, Phase 1 (2026-09-21)

The user asked to build "le moteur d'aide à la décision AWCI" - the
`awci/decision/` gap named in the table above and in §3 point 3.
Given the real risk of fabricating decision logic or operational
recommendations in a safety-critical domain, the user was offered a
scoped choice (full 9-module blueprint suite, real-core-only, or
real-core plus a real ICAO SMS risk matrix) and confirmed
**"Noyau réel uniquement"** (real core only).

**Built**, all under a new, deliberately headless `src/awci/decision/`
package (no PySide6/matplotlib/cartopy import anywhere in it, verified
by test - a real requirement so this package is usable from a future
CLI/API layer too, per the reference architecture's own placement of
`decision/` as a peer to `dashboard/`, not a GUI submodule):

- `context.py` - `DecisionContext` (lat/lon/pressure_hpa/generated_at),
  with a real ICAO flight level derived via the already-implemented
  `calculate_isa_pressure_altitude()`.
- `situation.py` - `AWCI_SCORE_BANDS`/`classify_awci_score()` mirror
  `awci.dashboard.awci_colors.LEVELS`/`level_for()` exactly (locked by
  a parity test); `SITUATION_ROWS` mirrors `awci_risk_summary._ROWS`'s
  key/label/module fields (also parity-tested);
  `build_situation_snapshot()` composes a real situation from the same
  real inputs `awci_alerts_panel.compute_elevated_risks()` already
  takes - one deliberate, disclosed divergence: a row is omitted,
  never fabricated as a 0.0 "Very Low", when its real score is
  genuinely unavailable.
- `recommendation.py` - `get_flight_recommendations()`, a thin, real
  lookup into the 3 `AVIATION_HAZARDS_REGISTRY` entries that already
  carry real, ICAO/FAA-cited `flight_recommendations` text
  (`cat_turbulence`, `airframe_icing`, `microburst_windshear`).
  Returns `None` for any other hazard key - never a fabricated
  recommendation, and deliberately never infers one from a coarse AWCI
  module score (conflating a broad composite index with one specific
  named hazard would be a real, dangerous misattribution).
- `engine.py` - `assess()`, a thin orchestrator composing the two into
  a `DecisionSupportView`.

**A real, pre-existing bug found along the way, not fixed here**:
importing `awci.dashboard.awci_map_panel` as the very first
AWCI-dashboard-related module in a fresh process raises a real
circular-import `ImportError` (`acf.gui.map.map_layers`'s own import
of the OLD `acf.gui.dashboard.awci_colors` shim cascades into
`acf.gui.dashboard.__init__` eagerly importing `awci_dashboard`, which
re-enters the still-initializing `awci_map_panel` module). Every
existing test avoids it only by accident of import order. Worked
around in this phase's own new test (a literal formula cross-check
instead of importing that module) and queued as a separate follow-up
task rather than fixed inline, since it is unrelated to the decision
engine itself and touches shared GUI-import plumbing outside this
task's own scope.

**Verified**: `ruff check`/`mypy` clean on the new package; 27 new
tests in `tests/test_awci_decision_support.py`, including 4
parity-lock tests against the real GUI classification scales this
headless package mirrors; full non-GUI suite collection 4780 tests
(up from 4753, +27);
a targeted sweep (`-k "decision or risk_summary or alerts_panel or
awci_colors or map_panel"`, excluding `tests/gui`) shows 141 passed, 0
failed.

**Deliberately not built this phase** (real, cited methodology needed
first, not an ACF-invented one): `risk_matrix.py` (would need the real
ICAO Doc 9859 SMS 5x5 likelihood x severity matrix), `confidence.py`
(would need a real, defensible uncertainty/data-quality model - e.g.
wired to the real `ModelConsensusEngine` spread, not invented),
`alternatives.py` (would need real multi-point/multi-level AWCI
sampling to search over - computable from already-real
`vertical_field.py`/`spatial_field.py` outputs, but not attempted this
phase), `scenario.py` (would need real temporal-evolution wiring to
`temporal_field.py`). Each remains a real, honestly-reported gap, not
a fabricated stub.

## 2n. The AWCI RAG evidence-retrieval layer (2026-09-21)

The user asked to build "Le RAG layer" - the `ai/rag/` gap named in §3
point 3 and confirmed still fully absent by a fresh investigation
(zero embedding/vector-store/LLM-client dependency in
`requirements.txt`, zero real LLM API call anywhere in the codebase).
Given the real risk of a RAG layer either needing a new heavy
dependency (a local embedding model) or an external network/API-key
dependency (a hosted LLM), the user was offered a scoped choice and
confirmed, verbatim: lexical/deterministic retrieval now, a clean
retriever interface for a future embedding backend, no external LLM
API/network dependency, no fake knowledge/synthetic documents, exact
provenance (source path/module/symbol/version) on every result, a
strictly evidence-only role never replacing deterministic AWCI
calculations, and a corpus limited to documented/validated AWCI
knowledge only (never inventing a law/threshold "from assumptions").

**Built**, under a new, deliberately headless `src/awci/ai/rag/`
package (no PySide6/matplotlib/cartopy, and verified by test to import
neither `awci.complexity` nor `awci.hazards` - a strict, one-way,
read-only relationship to the rest of AWCI):

- `documents.py` - `Document`/`Provenance` dataclasses;
  `build_document_corpus()` walks `awci.knowledge` (the ~39-module
  real, ICAO/WMO/aviation-cited knowledge base built earlier this
  session) via `pkgutil`, extracting every real module docstring and
  every real class/enum docstring via `inspect` - never hand-typed or
  synthesized text. A class reused across modules (e.g. `CloudGenus`)
  is indexed once, under its real defining module, never duplicated.
  Provenance includes the real git commit hash last touching each
  source file (cached per file, honestly `None` when unavailable).
- `retriever.py` - a real `Retriever` protocol (`retrieve(query,
  top_k) -> list[ScoredDocument]`) as the one, stable public contract;
  `BM25Retriever`, Phase 1's real implementation, using the real,
  published Okapi BM25 algorithm (Robertson & Zaragoza 2009, standard
  k1=1.5/b=0.75 parameters) in pure Python - no new dependency. Returns
  an honestly empty list for a query sharing no real token with any
  document, never a fabricated "closest match".
- `citations.py` - `format_citation()`, built entirely from a
  document's own real provenance fields.

**Deliberately not built**: `ai/rag/embeddings.py`/`vector_store.py`
(the blueprint's own file names) - no real embedding backend has been
chosen, and creating empty/fake versions of those two files would
itself be a fabricated placeholder; the `Retriever` protocol is the
real extension point for that future work if/when a backend is chosen.

**Verified, not assumed**: a manual end-to-end run confirmed 80 real
documents built from the real corpus in 0.23 s, real citations with
real (short) git commit hashes, and a genuinely empty result for a
nonsense query. `ruff check`/`mypy` clean; 24 new tests
(`tests/test_awci_rag.py`), including corpus-determinism, a
provenance-vs-real-file-on-disk check, a direct `git log` cross-check,
BM25 ranking/empty-query/empty-corpus behavior, and 2 explicit
discipline tests (no `awci.complexity`/`awci.hazards` import; no
heavy ML/network dependency import anywhere in the package). Full
non-GUI suite collection: 4804 tests (up from 4780, +24); a targeted
sweep (`-k "rag or awci_knowledge or awci_icao_wmo"`, excluding
`tests/gui`) shows 203 passed, 0 failed.

## 2o. The AWCI provenance/audit module (2026-09-21)

The user asked to build "Le module de provenance/audit AWCI" - the
`awci/provenance/` gap named in §22 of the reference architecture and
§3 point 3 here. Investigation before building found real,
already-existing building blocks to compose rather than duplicate:
`acf.core.contracts.provenance.Provenance` (the generic reproducibility
contract, already attached to `AWCIResult.provenance`),
`awci.complexity.result.AWCIResult` (already carries
`module_scores`/`interaction_scores`/`dominant_factors`/
`raw_variables`/`lead_time_hours`/`vertical_level` and its own
`trace_chain()` string rendering), `awci.complexity.scientific_status`
(the real per-weight/threshold evidentiary status registry - nothing
CONFIRMED today), and `awci.complexity.weights.WeightsManager.
get_weight_status()` (the real, established wrapper around that
registry).

**Built**, under `src/awci/provenance/`, matching §22's own exact
7-file list, each a real assembler (never a new computation, matching
`build_awci_result()`'s own established discipline):

- `source.py` - `DataSource`/`describe_source()`, a thin "which data"
  view over `Provenance`'s own `input_files`/`dataset_version`/
  `run_identifier`.
- `version.py` - `VersionInfo`/`WeightVersionEntry`/
  `describe_version()`, a "which code version" view enriched, when a
  real `AWCICalculator` is supplied, with the real per-weight status of
  every weight that calculator actually uses today.
  `has_calibrated_or_validated_weight` is honestly `False` for every
  weight this codebase ships.
- `calculation.py` - `CalculationStep`/`describe_calculation()`, a
  structured counterpart to `AWCIResult.trace_chain()`'s own string
  rendering (module scores → interaction terms → final score).
- `lineage.py` - `LineageRecord`/`build_lineage()`, composing the 3
  above plus `dominant_factors`/`model`/`lead_time_hours`/
  `vertical_level` from `AWCIResult` itself.
- `audit.py` - `AuditRecord`/`build_audit_record()`/
  `format_audit_report()`, the top-level entry point - explicitly names
  which real `Provenance` fields are still at their honest "unknown"
  default rather than hiding the gap.
- `reproducibility.py` - `ReproducibilityCheck`/
  `verify_reproducibility()` (a real float-tolerance comparison between
  two already-computed `AWCIResult`s - never re-runs the calculation
  itself) and `is_reproducible_run()` (reuses `Provenance.
  is_fully_specified()`).

**Deliberately not a persisted, append-only audit log/database** - a
disclosed scope limit stated in the package's own `__init__.py`:
`Provenance`/`AWCIResult` are per-object snapshots attached at
construction time, and this package only assembles a structured view
of one snapshot at a time; a real cross-run audit trail (a database, a
file-based log) would be new, separate infrastructure this phase does
not build.

**Verified, not assumed**: a manual end-to-end run against a real
`AWCICalculator` (real 14-variable input, real `calculate()` output)
confirmed correct lineage/audit/reproducibility output, including
honest "unknown"/"not available" disclosure for every field genuinely
not supplied. `ruff check`/`mypy` clean; 25 new tests
(`tests/test_awci_provenance.py`), including exact-missing-field
disclosure checks, a real reproducibility mismatch detection (CAPE
changed → real, different AWCI score → `matches=False`), and 2
discipline tests (no `AWCICalculator` import/recompute inside
`audit.py`/`calculation.py`/`lineage.py`; `scientific_status` functions
reused by identity, not copied). Full non-GUI suite collection: 4829
tests (up from 4804, +25); a targeted sweep (`-k "provenance or
awci_result or scientific_status or calibration or weights_manager"`,
excluding `tests/gui`) shows 88 passed, 0 failed.

## 2p. The AWCI plugin extension mechanism (2026-09-21)

The user asked to work through the entire remaining-gaps list one item
at a time ("on les attaque toutes un par un sans lancé plusieurs à la
fois"). Started with `awci/plugins/` - the one gap-table row marked
flatly ❌ "Not found" with no partial credit at all (unlike every other
AWCI gap tackled this session), and, unlike `decision/`/`provenance/`/
`ai/rag/`, a pure software-engineering package with zero real
scientific-fabrication risk - so all 5 blueprint-named files
(`interface.py`/`registry.py`/`loader.py`/`hooks.py`/`manager.py`) were
built in one pass, matching §20's own text: "AWCI must be extensible...
a new data source, a new model, a new hazard, a new visualization, a
new aviation product, a new AI agent."

**Investigated existing precedent first**: `acf.ai.plugins.
base_plugin.AIPlugin`/`acf.ai.plugins.plugin_manager.PluginManager` is
a real, working ABC + register/get pattern already used elsewhere in
this codebase - this package follows that same convention rather than
inventing a new one. `acf.core.plugin_manager.PluginManager` (a
different, much thinner directory-lister, real caller: `acf.core.
bootstrap`) and `acf.plugins` (a confirmed, already-disclosed empty
stub with zero importers) were also checked and are unrelated/not
reused.

**Built**: `interface.py` (`AWCIPlugin` ABC with an abstract
`describe()`; `PluginCategory` - the 6 real categories transcribed
directly from §20's own text, not invented); `registry.py`
(`PluginRegistry` - real register/get/list_by_category/all,
`DuplicatePluginError` on a name collision, matching `calibration.py`'s
own `ValidationOverlapError` precedent for "never a silent overwrite");
`loader.py` (`discover_plugins()` - real `importlib`-based directory
scan; a broken/misbehaving plugin file is recorded as a real, disclosed
`PluginLoadError`, never silently skipped and never crashing discovery
of the other real files - only classes truly DEFINED in each loaded
file are indexed, same discipline as `awci.ai.rag.documents`);
`hooks.py` (`HookRegistry` - real named-hook register/dispatch with the
same real per-callback error isolation); `manager.py` (`PluginManager`
- thin orchestrator owning one `PluginRegistry` and one `HookRegistry`).

**Honest, disclosed scope**: no existing AWCI module (a hazard, a data
source, a visualization layer) has been adapted to implement
`AWCIPlugin` yet, and no fake "example" plugin ships in `src/` - real,
working, tested infrastructure with zero plugins registered by default.

**Verified, not assumed**: a manual end-to-end smoke test (real plugin
files written to a temp directory, discovered, one intentionally broken
file correctly isolated from a good one, hooks dispatched with one
failing callback correctly isolated from the others); `ruff check`/
`mypy` clean; 26 new tests (`tests/test_awci_plugins.py`), including
real on-disk plugin loading via `tmp_path`. Full non-GUI suite
collection: 4855 tests (up from 4829, +26); a targeted sweep (`-k
"plugin"`, excluding `tests/gui`) shows 33 passed (including the
pre-existing `acf.ai.plugins` tests), 0 failed.

## 2q. acfctl, the ACF operational control point (2026-09-21)

Third item of "on les attaque toutes un par un" (after `awci/plugins/`
and, restarting to acfctl since it was the other item never touched at
all): `tools/acfctl/` was the one project-root gap explicitly named in
§1 ("not found in a `tools/` survey").

**Real, disclosed scope**: manages the 3 real, already-registered
console-script apps (`pyproject.toml`'s own `[project.scripts]`:
`acf-gui`/`acf-web`/`acf-awci`) as real OS subprocesses, tracked via a
real PID file under the same real `~/.acf/` local-state directory
already established by `acf.workspace.recent`, using `psutil` (an
already-real dependency) for cross-platform liveness checks.
Deliberately not built on Qt's own `QLocalServer` single-instance
mechanism (`acf.gui.single_instance`) - that needs a running Qt event
loop and only ever covered `acf-gui`, not `acf-web`/`acf-awci`.
`status()` guards against PID reuse (a real, currently-alive but
unrelated process after a reboot) by also checking the real process's
own cmdline for the expected console-script name, not just PID
existence.

`report()` builds a real environment/health report (ACF version,
Python version, each app's PATH/running status, real free disk space)
from independently-verifiable facts only - explicitly never a
synthesized overall "status: OK", citing `docs/STATUS.md`'s own
already-documented `earth_system_operations.py` fabricated-
self-certification finding as the cautionary precedent this module is
deliberately built to avoid repeating.

**Deliberately NOT registered as a `pyproject.toml`
`[project.scripts]` entry**: `acf-gui`/`acf-web`/`acf-awci` all live
under `src/`, the only directory `[tool.setuptools.packages.find]`
actually scans; `tools/` (like every other real script already there)
is repo-root-only development tooling, not part of the installable
distribution. Registering `acfctl` there would silently break a real
`pip install`/wheel build - a real packaging inconsistency avoided
rather than introduced by reflexively mirroring the other 3 entries.
Callable as `python -m tools.acfctl <command>` instead.

**Verified, not assumed**: manual end-to-end smoke tests (a real health
report against this real installation; a real start/status/stop cycle
against a real, lightweight fake executable, never the actual heavy
`acf-gui`/`acf-web`/`acf-awci`, which need a real display/network).
`ruff check`/`mypy` clean; 22 new tests (`tests/test_acfctl.py`),
including a real start/stop lifecycle, a real PID-reuse detection test,
and a `pyproject.toml`-parsing parity test locking `KNOWN_APPS` to the
real `[project.scripts]` table. Full non-GUI suite collection: 4877
tests (up from 4855, +22); a targeted sweep (`-k "acfctl"`, excluding
`tests/gui`) shows 22 passed, 0 failed.

## 2r. The AWCI Observation Hub (2026-09-21)

Fourth item of "on les attaque toutes un par un": `awci/observations/`
- specifically the one, named gap ("no single `observations/hub.py`
aggregation point").

**Built**: `src/awci/observations/hub.py`'s `ObservationsHub` - a real,
thin aggregation point over 4 already-real, already-working connectors
scattered across 2 packages: `awci.knowledge.icao.live_source`
(METAR/TAF per-station, SIGMET FIR-wide - NOAA Aviation Weather
Center), `acf.connectors.pirep_reports.PIREPConnector` (Pilot Reports),
`acf.connectors.nexrad_stations.NEXRADRadarConnector` (NEXRAD station
status), `acf.connectors.eumetsat_mtg.EUMETSATMTGConnector` (MTG FCI
satellite quicklook). `ObservationsSnapshot` carries every real
per-source result unchanged - no synthesized aggregate "all good"
verdict; a real, dishonest per-source failure survives into the
snapshot untouched.

**Investigated and deliberately excluded** (disclosed in `hub.py`'s
own docstring): `acf.connectors.argo_floats` (real, but ocean buoys,
not an aviation source); `acf.connectors.live_connectors.
LiveDataConnectorEngine` (confirmed, by reading it first, to be a
different, still-disclosed-unconnected registry of general NWP-model
sources - ECMWF/NOAA-NOMADS/DWD/EUMETSAT-datastore/NASA/Copernicus -
every real fetch call still honestly returns
`NOT_SYNCED_NO_REAL_CONNECTION_ESTABLISHED`); `acf.connectors.wmo_wis.
WMOWISEngine` (a real GTS/WIS 2.0 bulletin-header PARSER given a
string, not a live fetcher - a different real shape, out of scope for
a "fetch current observations" hub).

**Deliberately not the blueprint's full 11-file package** (`stations.
py`/`metar.py`/`speci.py`/`pirep.py`/`radar.py`/`satellite.py`/
`lightning.py`/`surface.py`/`upper_air.py`/`aircraft_observations.py`,
plus per-source `parser/decoder/validator/interpreter` subpackages) -
real METAR/TAF/SIGMET parsing and decoding already exists
(`awci.knowledge.icao.metar_decoder`/`taf_decoder`/`sigmet_decoder`);
rebuilding a second, parallel `observations/metar/decoder.py` would be
pure duplication, not a real gap closed.

**Verified, not assumed**: `ruff check`/`mypy` clean; 12 new tests
(`tests/test_awci_observations_hub.py`), verifying the DELEGATION/
WIRING this module actually adds (correct arguments passed through to
each real connector, correct field assembly) via dependency injection
and monkeypatching at the hub's own call boundary - not re-testing
each connector's own already-covered real network/parsing behavior.
Full non-GUI suite collection: 4889 tests (up from 4877, +12); a
targeted sweep (`-k "observations_hub or aviation_live_source or
eumetsat_mtg_connector or pirep or nexrad"`, excluding `tests/gui`)
shows 47 passed, 0 failed.

## 2s. awci.airport.runway/weather (2026-09-21)

Fifth item of "on les attaque toutes un par un": `awci/airport/`'s
remaining named files (section 12 of the reference architecture).

**Built**: `runway.py` (`assess_runway_end_wind()`/
`assess_airport_runways_wind()`/`best_runway_end_for_wind()` - real
headwind/crosswind for every real runway end of a real airport,
composing `parse_runway_heading_magnetic_deg()` with
`AircraftPerformanceEngine.wind_components()`, both already real) and
`weather.py` (`build_weather_snapshot()` - a real per-airport weather
view composing the new `ObservationsHub` with the real ceiling
classification already in `awci.hazards.ceiling`, applied to a real
ceiling height taken directly from a real METAR's own decoded cloud
layers - the real ICAO BKN/OVC ceiling definition, a different, more
authoritative source than that module's own dewpoint-LCL estimate -
and the real WMO/ICAO present-weather meaning tables, decoded via
`metar_decoder`'s own already-real `_WX_RE` regex, reused directly).

**Deliberately not fabricated**: `weather.py` never forces a
precipitation RATE through `classify_precipitation_intensity()` - METAR
only ever gives a qualitative intensity (light/moderate/heavy), never a
quantified mm/h; inventing one would misrepresent what the real report
actually says. Locked in by a discipline test.

**Deliberately not built this round** (`awci/airport/__init__.py`'s own
updated docstring): `terminal.py` (no real terminal-infrastructure data
exists in this codebase), `operations.py`/`departure.py`/`arrival.py`/
`disruption.py` (each would need a real, cited regulatory go/no-go
threshold - e.g. a per-aircraft-type maximum demonstrated crosswind -
this codebase does not have), `runway_condition.py` (would need a real
ICAO Annex 3 runway-state-group METAR parser, which does not exist yet
- a real, separate, focused piece of work, deliberately not attempted
here to avoid scope creep). `crosswind.py`/`ceiling.py`/`visibility.py`
as separate blueprint-named files were also skipped - real content for
each already exists elsewhere (`aircraft_performance.py`,
`awci.hazards.ceiling`/`visibility`); duplicating it under `airport/`
would not close a real gap.

**Verified, not assumed**: manual end-to-end runs (a real LFPG
runway-wind assessment across all 8 real runway ends; a real KJFK
METAR - `BKN008 OVC015 -RA` - decoded and run through
`build_weather_snapshot()`, confirming 800 ft ceiling → real FAA IFR
category and `-RA` → "Light, Rain"). `ruff check`/`mypy` clean; 22 new
tests (`tests/test_awci_airport_runway_weather.py`), including
hand-verifiable wind-geometry cases (direct headwind/tailwind, pure
90-degree crosswind, reciprocal-runway symmetry) and 2 discipline
tests. Full non-GUI suite collection: 4911 tests (up from 4889, +22); a
targeted sweep (`-k "airport"`, excluding `tests/gui`) shows 41 passed,
0 failed.

## 2t. The AWCI Flight Planning Engine (2026-09-21)

Sixth item of "on les attaque toutes un par un": `awci/flight/`.

**Built**: `waypoint.py` (`great_circle_intermediate_point()`/
`generate_route_waypoints()` - the real, standard spherical
"intermediate point" navigation formula, Ed Williams' Aviation
Formulary, the same real family already used by `FlightRoutingEngine.
great_circle_distance_nm()`/`awci.airport.airport._destination_point()`
- complements, not replaces, `path_sampling.
sample_field_along_path()`'s own linear-interpolation approximation)
and `route_weather.py` (`build_route_weather_briefing()` - a real,
thin composition of `FlightRoutingEngine`'s route geometry, this
module's own waypoints, and `build_weather_snapshot()`/
`ObservationsHub` for real live weather at departure/arrival/every
real alternate).

**Honest, disclosed scope**: real weather is only fetched at real
airport stations - there is no real data source anywhere in this
codebase for weather at an arbitrary point along a route (that would
need a full NWP solver run sampled via
`sample_field_along_path()`); the real waypoint list stays positional
only, never paired with a fabricated weather value, locked in by a
discipline test.

**Deliberately not built this round**: `planning.py`/`route.py`/
`corridor.py`/`altitude.py`/`flight_levels.py`/`departure.py`/
`arrival.py`/`alternate.py` - real content for each already exists
elsewhere (`FlightRoutingEngine`, `awci.airport.airport`,
`awci.knowledge.performance.altimetry`); `fuel_weather.py` would need a
real aircraft-type fuel-burn model this codebase has no source for.

**Verified, not assumed**: manual end-to-end runs (a real LFPG-KJFK
5-waypoint route showing the real northward great-circle bow; a real
briefing composed against a fake hub returning real decoded METARs).
`ruff check`/`mypy` clean; 18 new tests (`tests/
test_awci_flight_waypoint_route_weather.py`), including hand-verifiable
spherical-geometry cases (equator quarter-point, antipodal rejection,
endpoint fractions) and a real distance cross-check (LFPG-KJFK > 3000
nm, matching the real ~3150 nm great-circle distance). Full non-GUI
suite collection: 4929 tests (up from 4911, +18); a targeted sweep
(`-k "flight or waypoint or route_weather"`, excluding `tests/gui`)
shows 53 passed, 0 failed.

## 2u. The AWCI Aviation Report generator (2026-09-21)

Seventh item of "on les attaque toutes un par un": `awci/reports/` -
specifically the named gap ("no standalone `reports/aviation_report.py`
generator").

**Built**: `generator.py` (`ReportSection`/`render_report()` - real,
generic, reusable text-rendering helpers) and `aviation_report.py`
(`build_aviation_report()`/`format_aviation_report()`), composing 3
already-real systems built earlier this session - `awci.airport.
weather.AirportWeatherSnapshot` (location, live weather, always
built), `awci.decision.DecisionSupportView` (hazards, confidence,
cited recommendations - built only when the caller supplies real
module scores), `awci.provenance.AuditRecord` (model, calculation,
provenance - built only when the caller supplies a real `AWCIResult`).
Matches section 17's own required preservation list (data sources,
model, time, location, calculation, factors, hazards, confidence,
uncertainty, provenance) directly, since every one of those already
exists as a real field on one of the 3 composed systems.

**Honest degradation**: every optional section renders "not available"
rather than a fabricated value when its underlying real data was never
supplied - verified by test with a weather-only report (decision/audit
both `None`) alongside a full 3-system composition.

**Deliberately not built this round**: `flight_report.py`/
`airport_report.py`/`hazard_report.py`/`complexity_report.py`/
`model_report.py`/`verification_report.py` - `aviation_report.py`
already covers the same real composed content a flight/airport-
specific report would otherwise duplicate; `templates/` would need a
real templating-engine decision out of scope here.

**Verified, not assumed**: manual end-to-end runs (a weather-only
report against a fake hub; a full report combining a real decoded KJFK
METAR - `BKN008 OVC015 -RA` - a real `AWCICalculator` run, and a real
`Provenance`, correctly showing the real IFR ceiling category, real
hazard severity bands, real cited CAT-turbulence recommendations, and
real provenance-completeness disclosure). `ruff check`/`mypy` clean;
13 new tests (`tests/test_awci_reports_aviation.py`). Full non-GUI
suite collection: 4942 tests (up from 4929, +13); a targeted sweep
(`-k "reports_aviation or awci_decision or awci_provenance or
airport_runway"`, excluding `tests/gui`) shows 87 passed, 0 failed.

## 2v. The AWCI alerts engine (2026-09-21)

Eighth item of "on les attaque toutes un par un": `awci/alerts/` -
specifically the named gap ("only a UI panel (`awci_alerts_panel`), no
standalone alerts engine").

**Built**: `engine.py` (`Alert`/`AlertEngine.alerts_for()` - a real,
headless composition over `SituationSnapshot`, reusing its own real
"elevated" rule rather than duplicating a second severity scale;
`hazard_key_map` lets a caller attach real, cited recommendations to a
specific elevated row, never inferred automatically) and
`notifications.py` (`AlertNotifier` - real, generic, in-process
subscriber register/dispatch, the same real error-isolation pattern
already established by `awci.plugins.hooks.HookRegistry`).
Deliberately headless (verified by test) - usable outside the GUI
dashboard, matching this session's `decision`/`ai.rag`/`provenance`
packages' own precedent.

**Deliberately not built this round**: `rules.py`/`thresholds.py`/
`severity.py` (the real severity bands this package uses already exist
in `awci.decision.situation`); `hazard_alerts.py`/`airport_alerts.py`/
`route_alerts.py`/`complexity_alerts.py` (no real per-scope hazard
taxonomy exists beyond what `SituationSnapshot` already provides).

**Verified, not assumed**: manual end-to-end run (a real
`SituationSnapshot` with 3 elevated rows correctly producing 3 alerts,
one with real cited CAT-turbulence recommendations attached; a real
failing subscriber correctly isolated from 2 other real subscribers).
`ruff check`/`mypy` clean; 15 new tests (`tests/test_awci_alerts.py`).
Full non-GUI suite collection: 4957 tests (up from 4942, +15); a
targeted sweep (`-k "alerts or awci_plugins"`, excluding `tests/gui`)
shows 66 passed, 0 failed.

## 2w. The AWCI aviation knowledge graph (2026-09-21)

Ninth item of "on les attaque toutes un par un": `awci/knowledge/
knowledge_graph/` - `docs/architecture/awci_reference_architecture.md`
section 2 ("Aviation Knowledge Base") names `entities.py`/
`relations.py`/`graph.py`/`ontology.py` under this path, but no such
package existed - the one real content gap remaining in the otherwise
fully migrated `awci/knowledge/` layer (§2j).

**Built**: `entities.py` (`AVIATION_KNOWLEDGE_NODES` - 10 real, cited
aviation-hazard `KnowledgeNode`s: jet stream, clear air turbulence,
orographic wave, rotor turbulence, wake turbulence, thunderstorm,
microburst, airframe icing, cold front, squall line, each citing an
already-real, already-built `awci.knowledge.meteorology`/`hazards`/
`performance` module plus a real ICAO/FAA source - ICAO Doc 9837, 9817,
4444, Annex 3 Ch3; FAA AC 00-54; FAA Aviation Weather Handbook Ch19)
and `graph.py` (`build_aviation_knowledge_graph()` - seeds the
already-real, already-working
`acf.science.encyclopedia.knowledge_graph.KnowledgeGraphEngine` (real
BFS `find_path()`/`explain_chain()`/`get_related_concepts()`) with
those nodes plus 7 real, cited causal edges: jet stream→CAT
(`associated_with`, ICAO Doc 9837), orographic wave→rotor turbulence
(`produces`, ICAO Doc 9817), cumulonimbus→microburst and
thunderstorm→microburst (`produces`, FAA AC 00-54/ICAO Doc 9837),
thunderstorm→squall line (`produces`), cold front→thunderstorm
(`triggers`), updraft→airframe icing (`produces`, FAA Aviation Weather
Handbook Ch19). The edges from the base engine's own already-real
general nodes (`cumulonimbus`, `updraft`) into the new aviation nodes
mean the two node sets are genuinely interconnected, not two disjoint
islands - e.g. `explain_chain("cold front", "microburst")` returns a
real 2-hop causal chain (cold front → thunderstorm → microburst) with
a real citation on each edge.

**Deliberately not built this round**: a second graph engine class -
`KnowledgeGraphEngine` is reused by identity, not copied; a duplicate
would re-implement already-real, already-tested pathfinding/
explanation logic for no benefit. `relations.py` as a separate file -
the edges are built inline via `add_edge()`, the exact same convention
the base engine's own `_build_default_graph()` already uses; splitting
them into a second file would change no real logic, only add
indirection. `ontology.py` - a formal ontology/reasoner framework
(e.g. OWL/RDF class hierarchies) is a real, separate architectural
decision out of scope for this session, and nothing in this codebase
currently needs one: the flat node/edge graph already answers every
real query this package's callers need.

**Verified, not assumed**: manual end-to-end run confirming real
connectivity - `get_related_concepts("jet stream")` returns
`[("clear air turbulence", "associated_with")]`;
`find_path("orographic wave", "rotor turbulence")` returns the direct
2-node path; `explain_chain("cold front", "microburst")` returns the
real 2-hop chain with a real reference on each edge;
`explain_chain("wake turbulence", "airframe icing")` honestly reports
`connected: False` (no real causal link asserted between them); the
base engine's own pre-existing nodes (`cape`, `cumulonimbus`,
`instability`) remain present after seeding. `ruff check`/`mypy` clean
on the new package. 15 new tests
(`tests/test_awci_knowledge_graph.py`), including a discipline test
that every added edge carries a real, non-empty `reference` and a test
that no second `KnowledgeGraphEngine`-like class is defined in
`graph.py`. Full non-GUI collection in this session's environment:
4595 tests collected with 45 pre-existing collection errors unrelated
to this change (the already-tracked `awci_map_panel` circular-import
bug, `task_468ac835` - confirmed by collecting `tests/test_map_camera.py`
standalone, which succeeds with 8 tests when not collected alongside
the full suite); none of the 45 errors touch
`awci/knowledge/knowledge_graph/` or this test file. A targeted
`pytest tests/test_awci_knowledge_graph.py` run shows 15 passed, 0
failed.

## 2x. AWCI separate-package migration, Phase 11: aviation-relevant `acf.connectors/` → `awci/data/connectors/` (2026-09-21)

Tenth item of "on les attaque toutes un par un": `awci/data/` +
`data/connectors/` - `docs/architecture/awci_reference_architecture.md`
names `src/awci/data/connectors/`, but the real network connectors
were still under `acf.connectors`, unmigrated.

**Investigation, before any move**: `acf.connectors` has 6 real
modules, not all aviation-relevant. `awci.observations.hub` (built
earlier in this same sequence) already established, by reading each
module's own docstring/behavior, which 3 are genuinely aviation
observation sources - `pirep_reports.py` (real NOAA PIREP fetch),
`nexrad_stations.py` (real NEXRAD radar station status fetch),
`eumetsat_mtg.py` (real MTG FCI satellite quicklook fetch) - and which
3 are not: `argo_floats.py` (ocean buoy data), `wmo_wis.py` (a generic
WMO GTS/WIS bulletin-header parser covering all WMO data types, not
aviation-specific), `live_connectors.py` (`LiveDataConnectorEngine` -
a generic, disclosed-unconnected NWP-model registry spanning
ECMWF/NOAA/DWD/EUMETSAT/NASA/Copernicus). This phase reuses that same
already-real distinction rather than re-deriving it.
`grep -rl "acf\.connectors\.\(pirep_reports\|nexrad_stations\|eumetsat_mtg\)" src/ tests/`
found 4 real dependents outside the connectors package itself:
`acf/gui/map/mtg_basemap.py` (top-of-file import),
`acf/gui/dashboard/acf_workstation.py` (2 deferred function-body
imports), `awci/observations/hub.py` (top-of-file imports, built
earlier this session), plus their own 3 dedicated test files and 2
more test files exercising them indirectly
(`tests/test_awci_observations_hub.py`,
`tests/gui/test_acf_workstation_data_sources.py`).

**Placement decision (disclosed)**: move only the 3 real,
already-established aviation-relevant connectors - not the whole
`acf.connectors` package - mirroring the same selective-scope
reasoning `awci.observations.hub`'s own docstring already used for the
same 3-vs-3 split. The blueprint's own `awci/data/connectors/` file
list (`acf.py`/`grib.py`/`fa.py`/`lfa.py`/`netcdf.py`/`metar.py`/
`speci.py`/`taf.py`/`sigmet.py`/`airmet.py`/`radar.py`/`satellite.py`/
`lightning.py`/`pirep.py`/`notam.py`) is a file-format/product-per-file
layout, structurally different from this codebase's real
network-connector-per-source layout - not matched 1:1, and disclosed
as such in the new package's `__init__.py`: METAR/TAF/SIGMET decoding
already exists under `awci.knowledge.icao`; GRIB/FA/LFA/NetCDF model
ingestion already exists under `awci.data.archive_field`/
`model_import*`; AIRMET/NOTAM/lightning connectors do not exist
anywhere in this codebase and are not fabricated here.

**Execution**: 3 files physically moved via `git mv`
(`pirep_reports.py`, `nexrad_stations.py`, `eumetsat_mtg.py`) into the
new `src/awci/data/connectors/` package, plus a new
`awci/data/connectors/__init__.py` disclosing the scope decision. The
3 old `acf/connectors/<x>.py` paths rebuilt as real backward-compatible
re-export shims. Real top-of-file/deferred imports repointed in all 3
real dependents (`mtg_basemap.py`, `acf_workstation.py`'s 2 deferred
imports, `observations/hub.py`); historical docstring/comment
citations of the old path left as-is (matching the Phase 9/§2j
precedent for comment-only references) except one in `argo_floats.py`
that pointed at `eumetsat_mtg`'s real error-handling convention by
name - updated to the new path since it is a live cross-reference, not
a historical note. `eumetsat_mtg.py`'s own internal logger name
(`logging.getLogger(...)`) updated to match its new module path.

The 3 moved modules' own dedicated test files
(`test_eumetsat_mtg_connector.py`, `test_nexrad_stations_connector.py`,
`test_pirep_reports_connector.py`) plus `test_awci_observations_hub.py`,
`test_mtg_basemap.py` and `tests/gui/test_acf_workstation_data_sources.py`
repointed to import from the new location. The eumetsat_mtg test
file's `unittest.mock.patch("...eumetsat_mtg.requests.*")` calls
needed this too, not just the import line - the shim module no longer
has its own `requests` import to patch, only the real module at the
new path does.

**Verified, not assumed**: manual end-to-end identity check (both old
and new import paths resolve to the exact same real class objects for
all 3 connectors); `ruff check` clean on every touched file; the one
pre-existing `mypy` error in `eumetsat_mtg.py` (a `requests.get()`
`params` typing mismatch) confirmed unchanged by diffing `mypy`
output against the pre-migration committed state - not introduced by
this move. New `tests/test_awci_data_connectors_migration.py` (7
tests) locks in re-export identity, confirms the 3 non-aviation
connectors were deliberately left unshimmed under `acf.connectors`,
and confirms the real cross-package dependents were repointed. A
targeted sweep (`-k "connectors or eumetsat or nexrad or pirep or
observations_hub"`, excluding `tests/gui`, plus the GUI-dependent
tests run separately under `xvfb-run`) shows 49 passed, 0 failed. Full
non-GUI collection: 4602 tests (up from 4595, +7 for the new migration
lock-in file), same pre-existing 45 collection errors (§2w's already-
tracked `task_468ac835` circular import) confirmed unrelated.

## 2y. The AWCI-specific workspace/project format (2026-09-21)

Eleventh item of "on les attaque toutes un par un": `awci/workspace/`
- the specific gap named in
`docs/architecture/acf_awci_architecture_gap_analysis.md` ("No
AWCI-specific project/session format; ACF's own `acf.workspace` is
general-purpose").

**Investigation**: `acf.workspace` is a real, working, general-purpose
project system - `Project` (a dataclass with a real, previously-
corrected JSON `to_dict()`/`from_dict()` round-trip), `WorkspaceManager`
(create/open/save/close, plus `RecentProjectsManager` tracking), and
`ProjectSerializer` (`save()`/`load()`, with a real previously-
corrected rename-cleanup fix removing a stale old `.acfproj` file on a
genuine project rename). `docs/architecture/awci_reference_architecture.md`
section 21 says an AWCI project keeps a different real folder set:
`data/ forecasts/ flights/ airports/ hazards/ maps/ reports/ analysis/
exports/ logs/` - distinct from ACF's own `data/maps/models/reports/
scripts/exports/logs/cache/plugins`.

**Placement decision (disclosed)**: subclass `Project`/
`WorkspaceManager` rather than build a second, independently invented
project system. `AWCIProject` overrides only `project_file` (real
`.awciproj` extension, so an AWCI project and an ACF project never
collide in the same directory) and `from_dict()` (to construct the
subclass); every other field/method (`to_dict()`, `touch()`,
`summary()`) is inherited unchanged. `AWCIProjectSerializer.save()`
reuses the base `ProjectSerializer.save()` completely unchanged - it
was already written polymorphically (`project.to_dict()`/
`project.project_file`/`project.touch()`, never hardcoding the
`Project` class itself), so it writes an `AWCIProject` correctly with
zero duplicated logic, including the base's own rename-cleanup fix.
Only `load()` needed a real override, since the base hardcodes
`Project.from_dict(data)` rather than the caller's subclass.
`AWCIWorkspaceManager` reuses `save_project()`/`close_project()`/
`recent_projects()`/`has_project()`/`project()`/`project_name()`/
`project_path()` unchanged (locked in by identity in the new test
file) and overrides only `create_project()`/`open_project()` for the
AWCI folder layout and file format; its own recent-projects file
defaults to `~/.awci/recent_projects.json` rather than ACF's
`~/.acf/recent_projects.json`, since listing an `.awciproj` file in
ACF's own recent-projects file would let a caller try to open it with
the wrong serializer.

**Deliberately not built this round**: `session.py`/`state.py` (the
blueprint's remaining named files) - no real, coherent "AWCI session"
or "AWCI state" concept exists anywhere in this codebase distinct from
what already exists: an open `AWCIProject` (this package),
`SituationSnapshot`/`DecisionContext` (`awci.decision`), and
`AlertEngine` (`awci.alerts`) already cover the real state a caller
would track. Wrapping them in a new session/state class with no real
added behavior would be padding, not a real gap - a future real GUI
session-state concept would be a real, disclosed addition when the GUI
actually needs one.

**Verified, not assumed**: manual end-to-end run - a real `AWCIProject`
created on disk with all 10 real `AWCI_PROJECT_FOLDERS` subdirectories,
a real `.awciproj` JSON file, closed and reopened with `datasets`/
`metadata`/`settings`/`created` all round-tripping correctly; a real
rename (`Orig` → `Renamed`) correctly removed the stale
`Orig.awciproj` and left only `Renamed.awciproj`, confirming the reused
base serializer's rename-cleanup fix applies polymorphically.
`ruff check`/`mypy` clean on the new package and its test file. 9 new
tests (`tests/test_awci_workspace.py`), including 2 discipline tests
asserting `AWCIWorkspaceManager`'s 7 reused lifecycle methods and
`AWCIProjectSerializer.save` are the literal same real function objects
as the base class's, not copies. Full non-GUI collection: 4611 tests
(up from 4602, +9), same pre-existing 45 collection errors
(`task_468ac835`, already tracked in §2w/§2x) confirmed unrelated. A
targeted sweep (`-k "workspace" --continue-on-collection-errors`)
shows 12 passed (9 new + 3 pre-existing ACF workspace tests), 0
failed.

## 2z. The AWCI application/lifecycle core (2026-09-21)

Twelfth item of "on les attaque toutes un par un": `awci/core/` - the
specific gap named in
`docs/architecture/acf_awci_architecture_gap_analysis.md` ("No
dedicated AWCI application/lifecycle/registry core exists; AWCI code
is simply part of `acf.*`'s own process").

**Investigation**: `src/acf/core/` already exists and is real -
`ConfigManager`, `get_logger()` (loguru), `PluginManager` (simple
directory-scan, distinct from the far more sophisticated
`awci.plugins` built earlier this session), `ServiceManager` (a real,
fully generic name→service registry), `Bootstrap`/`Application` (a
real headless startup sequence, confirmed never actually constructed
anywhere - `acf-gui` launches `ACFWorkstationWindow` directly instead
- per that module's own already-existing NOTE), and a real
`ACFError` exception hierarchy. Two more real, already-existing,
directly relevant pieces found: `acf.awci_app` (the real, GUI-coupled
standalone AWCI launcher - its own `--version` output is the only
place this codebase already names the real "AWCI" application
identity: `"ACF AWCI (Atmospheric Weather Complexity Index)"`) and
`awci.complexity.config_loader` (a real, already-versioned, JSON-
backed AWCI configuration system, built earlier in this codebase's
history to close `docs/ACF_MASTER_PROMPT.md` section 56's own gap -
already exactly what the blueprint's `configuration.py` wants).
`src/acf/aeos/events/event_bus.py`'s `PlanetaryEventBus` was also
found and read, but not reused - its event vocabulary
(`PlanetaryEvent.event_type` values like `EarthquakeDetected`/
`CycloneDetected`) is hardcoded to `acf.aeos`'s own Earth-system
domain, not a generic app-lifecycle bus.

**Placement decision (disclosed)**: reuse every real, already-generic
ACF component directly rather than duplicate it (`ServiceManager` as
`ServiceRegistry`, `awci.complexity.config_loader` as
`configuration.py`, `acf.__version__` as AWCI's own version - AWCI
ships inside the `acf` distribution and has no independent release),
and build only what is genuinely AWCI-specific or genuinely new:
a real `AWCIError` hierarchy kept as a sibling of `ACFError` rather
than a subclass (matching the reference architecture's own explicit
framing of AWCI as "a separate aviation product/project... not... a
subpackage buried inside ACF's own layer 3"); a real `EventBus`/
`Event` at a new, genuine scope (arbitrary named app-lifecycle events,
distinct from `awci.plugins.hooks.HookRegistry`'s plugin hooks and
`awci.alerts.notifications.AlertNotifier`'s alert dispatch, but
following the exact same real dispatch/error-isolation discipline
already established by both); a real `logs/awci.log` filtered loguru
sink, alongside (not replacing) `acf.core.logger`'s own shared
unfiltered sinks, matching the same separate-artifact convention
`awci.workspace`'s own `~/.awci/recent_projects.json` already
established; a real `AWCIContext`/`AWCILifecycle`/`AWCIApplication`
wiring these together, mirroring `Bootstrap`'s own real shape but with
AWCI's own real components (`get_awci_logger()`,
`AWCIWorkspaceManager`) instead of ACF's generic ones.

**Deliberately not built this round**: `dependencies.py` - "service
registration/lookup by name" (`registry.py`) and "dependency
injection" are the same real concept in this codebase; splitting them
into two files would add indirection with no real behavioral
difference. Plugin discovery is not re-implemented inside
`AWCILifecycle` - a caller passes an already-constructed
`awci.plugins.manager.PluginManager` through `start()`'s
`extra_services` parameter instead, reusing the real, already-built
plugin system rather than a second discovery pass.

**Verified, not assumed**: manual end-to-end run - a real
`AWCIApplication` started (services `logger`/`workspace` both real and
reachable via `ServiceRegistry.get()`), a real `EventBus.emit()`
dispatched with zero errors, `stop()` then a second `stop()` correctly
raising `AWCILifecycleError`; confirmed `logs/awci.log` was genuinely
created on disk with the real log line. `ruff check`/`mypy` clean on
the new package and its test file (12 source files, 0 errors). 19 new
tests (`tests/test_awci_core.py`), every test that constructs a real
`AWCIWorkspaceManager` (via `AWCILifecycle`/`AWCIApplication`)
monkeypatching `Path.home()` to an isolated `tmp_path` first - confirmed
by direct inspection that the real user's `~/.awci` was never created
by this test run. Full non-GUI collection: 4630 tests (up from 4611,
+19), same pre-existing 45 collection errors (`task_468ac835`, already
tracked in §2w/§2x/§2y) confirmed unrelated. A targeted sweep
(`-k "awci_core or service_manager" --continue-on-collection-errors`)
shows 21 passed, 0 failed.

## 2aa. The AWCI HTTP API (2026-09-21)

Thirteenth item of "on les attaque toutes un par un": `awci/api/` -
the specific gap named in
`docs/architecture/acf_awci_architecture_gap_analysis.md` ("No
dedicated AWCI API surface; `src/acf/api/` and `src/acf/web/` are
ACF-general, not AWCI-specific").

**Investigation**: `fastapi` is already a real, declared optional
dependency (`pyproject.toml`'s `web` extra). `acf.web.
hpc_dashboard_server.create_app()` already establishes a real,
working app-assembly pattern (construct `FastAPI`, stash injectable
real dependencies on `app.state` for tests, `include_router()` per
real domain) with real routers already covering ACF-general concerns
(`acf.web.routers.complexity_router` already serves the same real
`AWCICalculator` engine AWCI's own `awci.complexity` package now
owns, round-tripped through the `acf.awci` shim). No real HTTP
surface exists anywhere for AWCI's own domain packages built earlier
in this same "on les attaque" sequence
(`awci.observations`/`awci.airport`/`awci.flight`/`awci.reports`).

**Placement decision (disclosed)**: build a genuinely separate AWCI
FastAPI app (not add routers to ACF's existing one), matching the
reference architecture's own framing of AWCI as a separate product.
Build only the `routes/` modules with a real, already-working backing
engine to expose - 6 of the blueprint's 11 named files
(`observations.py`, `airports.py`, `flights.py`, `hazards.py`,
`complexity.py`, `reports.py`) - never a fabricated endpoint over data
this codebase cannot actually produce. `complexity.py` imports
`awci.complexity.calculator.AWCICalculator` directly rather than via
the `acf.awci` shim, matching this session's own "repoint real
dependents to the new location directly" discipline already applied
throughout the AWCI package migration (§2j, §2x). One shared, generic
`routes/_serialization.py` helper (`to_json_safe()`) converts any real
dataclass response (`datetime` → ISO string, nested
dataclasses/tuples/dicts walked recursively) - no parallel Pydantic
schema layer duplicating fields these dataclasses already declare.

**Deliberately not built this round**, disclosed in
`awci/api/__init__.py`: `forecasts.py` (no real AWCI-specific NWP
forecast-retrieval engine to expose - ACF's own solver-based forecast
pipeline is not a per-request HTTP concern); `models.py` (would
duplicate `acf.web.routers.models_router`'s already-real ACF-general
model listing); `profiles.py`
(`awci.knowledge.graphics.cross_section.FlightCrossSectionEngine`
only produces real waypoint geometry - already exposed via
`routes/flights.py` - every atmospheric field it would report is
honestly `None`, no real data source wired to it); `maps.py` (no real
AWCI-specific tile-serving concept exists anywhere in this codebase);
`ai.py` (`awci.ai` exists as a headless Python API but has no HTTP
surface wired yet, and several of its named subsystems remain unbuilt
per the broader remaining-gaps list - a real, disclosed future
addition, not fabricated ahead of it). `schemas/`/`services/`/
`middleware/` are not separate subpackages - real dataclasses/the
`awci.*` domain packages themselves/no real middleware need (auth,
rate limiting) exists anywhere in this codebase today.

**Verified, not assumed**: manual end-to-end run via FastAPI's
`TestClient` against a real running app instance - `/health`,
`/hazards`, `/hazards/{key}` (both a real hit and a real 404),
`/airports/{icao}/runways` (both a real hit and a real 404 for an
unknown airport), `/complexity/score` (a real `AWCICalculator`
computation, not a canned response) all exercised directly before any
test file was written. `ruff check`/`mypy` clean (the 3 mypy findings
in the new test file are the exact same accepted duck-typed-fake-vs-
nominal-type pattern already present in
`tests/test_awci_observations_hub.py`, not a new issue class). 14 new
tests (`tests/test_awci_api.py`), every network-calling connector
faked/monkeypatched using the exact same real isolation discipline
`tests/test_awci_observations_hub.py` already established - no real
network call made by this test run. Full non-GUI collection: 4644
tests (up from 4630, +14), same pre-existing 45 collection errors
(`task_468ac835`, already tracked in §2w/§2x/§2y/§2z) confirmed
unrelated. A targeted sweep (`-k "awci_api"
--continue-on-collection-errors`) shows 14 passed, 0 failed.

## 2ab. Closing acf.core's own remaining gap (2026-09-21)

Fourteenth item of "on les attaque toutes un par un" - the first of a
5-part ACF-general batch (`core/`, `utils/`, `api/`, `alerts/`,
`reports/`, each tackled as its own item): the `core/{...}` row's own
named-but-missing files, distinct from every AWCI-specific item
before this one.

**Built**: `registry.py` (`Registry` - a real alias for the already-
generic `acf.core.service_manager.ServiceManager`), `lifecycle.py`
(`Lifecycle` - a real alias for the already-real
`acf.core.bootstrap.Bootstrap`), `events.py` (`EventBus`/`Event` -
genuinely new, generic app-lifecycle pub/sub, same real dispatch/
error-isolation discipline as `awci.core.events.EventBus` - a real,
independent sibling rather than a shared import, since AWCI is a
separate product per the adopted reference architecture and
`acf.core.events` did not exist when the AWCI one was built),
`context.py` (`ApplicationContext` - bundles `Registry`+`EventBus`,
ACF's own general-scope counterpart to `awci.core.context.
AWCIContext`, with no project/workspace field since
`acf.workspace.Project` is reachable through the registry like any
other real service).

**Verified, not assumed**: manual end-to-end run (registry get/set,
event subscribe/emit, context bundling both). `ruff check`/`mypy`
clean. 7 new tests
(`tests/test_acf_core_lifecycle_registry_events.py`), including
identity checks for the 2 real aliases and a real isolation check
that two `ApplicationContext()` instances never share state. Full
non-GUI collection: 4651 tests (up from 4644, +7), same pre-existing
45 collection errors (`task_468ac835`) confirmed unrelated.

## 2ac. Closing acf.utils's own remaining gap (2026-09-21)

Fifteenth item of "on les attaque toutes un par un" - second of the
5-part ACF-general batch: the `utils/{...}` row's own named-but-
missing standalone modules.

**Built**: `serialization.py` (`to_json_safe()` - promoted from
`awci.api.routes._serialization`, built earlier this session for the
AWCI HTTP API, once the same real, generic need was recognized beyond
that one caller; that module now re-exports this one, locked in by an
identity test rather than keeping a duplicate), `hashing.py`
(`sha256_of_bytes`/`sha256_of_text`/`sha256_of_file` - real, stdlib-
only), `decorators.py` (`retry` - real, stdlib-only retry decorator,
not yet wired into any existing connector).

**Deliberately not built**: `units.py` (real unit handling already
lives in `acf.normalization` - duplicating it here would contradict
this project's own reuse discipline); `caching.py`/`profiling.py`/
`concurrency.py`/`numerical.py` (no real, disclosed caller need
exists for any of them yet - building them speculatively would be
premature abstraction, which `AGENTS.md` explicitly warns against,
not a real gap).

**Verified, not assumed**: manual end-to-end run (dataclass/datetime/
nested-structure conversion; real SHA-256 digests matched directly
against stdlib `hashlib` output, including a chunked-read path over a
2 MiB file; real retry success-after-failure and exhausted-attempts
behavior). `ruff check`/`mypy` clean. 13 new tests
(`tests/test_acf_utils_serialization_hashing_decorators.py`); the
pre-existing 14 `tests/test_awci_api.py` tests re-run clean after the
`_serialization.py` re-export change (no behavior change, only where
the implementation lives). Full non-GUI collection: 4664 tests (up
from 4651, +13), same pre-existing 45 collection errors
(`task_468ac835`) confirmed unrelated.

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
   mechanics - see §2k's own closing note. The ACF-side widget reuse was
   investigated and explicitly decided in §2l: kept as a disclosed,
   functionally-neutralized trade-off rather than extracted.
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

### 4f. Phase 6: `science/turbulence/` and `science/boundary_layer/` (2026-09-21)

**Placement**: two single flat modules, one to each blueprint subdomain.
`wind_turbulence.py` (3 real classes - `CATIndex`, `JetStream`,
`TKEProduction` - plus a real constant `JET_STREAM_THRESHOLD_M_S`) maps
to `science/turbulence/`. `boundary_layer.py` (4 real classes -
`MoninObukhovLength`, `FrictionVelocity`, `BowenRatio`, `PBLHeight` -
plus a real constant `VON_KARMAN`) maps to `science/boundary_layer/`.
Both depend only on `acf.science.constants` (already migrated in §4d,
resolving transparently through its own package) and nothing else - true
leaves, no cross-batch dependency between them.

**A visible contrast in the self-naming-collision rule**:
`wind_turbulence.py` does **not** collide with its own target package
name (`science/turbulence/`), so - unlike every module renamed into a
same-named package in §4a-§4e - it keeps a real, working flat shim at
`src/acf/science/wind_turbulence.py`. `boundary_layer.py` **does**
collide with `science/boundary_layer/`, so it gets no flat shim, per the
established rule - the package's own `__init__.py` re-exports its 5 real
names directly instead. Both cases were checked explicitly before
writing either `__init__.py`, now a standing step in this reorganization's
own method.

**Execution**: both files physically moved via `git mv`, keeping their
real names (`turbulence/wind_turbulence.py`,
`boundary_layer/boundary_layer.py`). Two `__init__.py` files written,
each re-exporting only the names genuinely defined in their own module
(the constants transitively imported from `acf.science.constants` - `G`
in `wind_turbulence.py`; `CP`/`EPSILON`/`G`/`LV` in `boundary_layer.py` -
deliberately excluded from each package's own `__all__`, matching the
precedent from §4a's `equivalent_potential_temperature.py`). One real
flat shim written for `wind_turbulence.py`. The mandatory sweep found 2
already-migrated `awci.*` modules depending on `wind_turbulence.py` -
`awci/hazards/cat_turbulence.py` and
`awci/complexity/wind_classification.py` - repointed to
`acf.science.turbulence.wind_turbulence` directly (`path_sampling.py`'s
own reference was comment-only, left as-is). `boundary_layer.py` has 2
still-flat `acf.science.*` dependents (`laws/boundary_layer.py`,
`surface_fire.py`) - needed no code change, since the bare
`acf.science.boundary_layer` import path itself never changed, exactly
like `constants.py`/`radiation.py` in §4d/§4e.

**Verified, not assumed**: `ruff check`/`mypy` clean (4 source files
across both packages); identity confirmed programmatically for both
modules (`wind_turbulence.py` via its real shim, `boundary_layer.py` via
its package directly) and both packages' own `__all__`; full test
collection under xvfb - 5043 tests, 0 errors; a targeted turbulence/
CAT/wind-classification/boundary-layer/jet-stream/Monin-Obukhov/friction-
velocity/Bowen/PBL/surface-fire sweep (non-GUI) passed 147/147. A new
`tests/test_science_turbulence_boundary_layer_reorganization.py`
(7 tests) locks in both packages' re-export identities, the contrasting
shim-vs-no-shim treatment, the 2 cross-package fixes into already-migrated
`awci.*` code, and that the 2 still-flat `acf.science.*` siblings still
resolve correctly.

### 4g. Phase 7: `precipitation/`, `diagnostics/`, `climate/`, and extending `dynamics/`/`convection/`/`thermodynamics/` (2026-09-21)

The user asked to continue "pour tout" (for everything remaining). This
phase covers every still-flat `science/` module that maps cleanly to one
of the blueprint's 19 subdomains; what does *not* map cleanly is
inventoried below rather than force-fit, per AGENTS.md's "never invent
placeholders" rule.

**Placement, 8 files across 6 packages**:
- **`science/precipitation/`** (new): `precipitation.py` (`VIL`,
  `EchoTop`, `PrecipitationIntensity`, `HydrometeorType`,
  `ECHO_TOP_THRESHOLD_DBZ`) - direct blueprint match, self-named
  collision (no flat shim).
- **`science/diagnostics/`** (new): `diagnostics.py`
  (`DiagnosticAlert`, `SituationDiagnosis`) - direct blueprint match,
  self-named collision (no flat shim).
- **`science/climate/`** (new): `climatology.py`
  (`ClimatologicalRecord`, `Climatology`, `HeatColdWave`) - real content
  is climate records/heatwave diagnostics, a clean fit for the
  blueprint's `climate/` (not `climatology/`) - no name collision, real
  flat shim kept.
- **`science/dynamics/`** (extending §4c): `synoptic.py` (`Coriolis`,
  `GeostrophicWind`, `ThermalWind`, `ErtelPotentialVorticity`,
  `EARTH_RADIUS_M`) - already depended on `potential_vorticity.py`,
  moved there in §4c, confirming the scoping note left at the end of
  that section. `cyclones.py` (`GradientWind`, `BruntVaisalaFrequency`,
  `RossbyRadius`, `Bombogenesis`, `SaffirSimpson`,
  `BOMB_REFERENCE_LATITUDE_DEG`) - a real but mixed-role module (gradient
  wind balance and Rossby radius are dynamics; Brunt-Väisälä frequency is
  arguably a stability concept too; Saffir-Simpson is a classification
  scale, not a formula) - kept together as the one coherent file it
  already was, a disclosed placement decision, rather than fragmented
  across `dynamics/`/`stability/`/`diagnostics/` for marginal naming
  purity (same reasoning as the AWCI `knowledge/` whole-package decision).
  `wind.py` (`Wind`) - basic wind-vector speed/direction kinematics.
- **`science/convection/`** (extending §4b): `severe_weather.py`
  (`SevereWeather`) - a composite severe-convection index combining
  CAPE/CIN, vertical wind shear and storm-relative helicity, verified
  against NOAA SPC's own mesoanalysis definitions - the same real role
  as `storm_relative_helicity.py`/`storm_motion.py`/`bulk_wind_shear.py`
  already placed there in §4b.
- **`science/thermodynamics/`** (extending §4a): `moisture.py`
  (`Moisture`) - a real composite aggregator reusing 7 already-migrated
  same-package siblings directly (dewpoint, mixing ratio, relative/
  specific humidity, saturation mixing ratio and vapor pressure),
  mirroring `stability.py`'s own aggregator role from §4b.

**Investigated and deliberately left flat - no clean blueprint domain
exists for these**:
- `ensemble_uncertainty.py` (`EnsembleMember`, `EnsembleRun`,
  `UncertaintyEstimate`, `ConsensusResult`) - model-ensemble/consensus
  statistics, not atmospheric physics; depends on `climatology.py`
  (moved this phase) and continues to resolve correctly through its real
  flat shim, needing no code change.
- `radiosonde.py` (`SoundingLevel`, `SoundingProfile`) - a shared data
  structure used across many domains (already consumed by
  `parcel_ascent.py`, `stability.py`, `moisture.py`), not itself a
  domain-specific formula module.
- `surface_fire.py` (`SaturationVaporPressureFAO56`,
  `PenmanMonteithFAO56`) - FAO-56 reference evapotranspiration, real
  agriculture/fire-weather science outside the blueprint's 19 named
  atmospheric subdomains.
- `visibility.py` (`Koschmieder`, `ICAOCategory`, `FogRisk`) -
  atmospheric-optics visibility physics; no blueprint subdomain names
  this concern directly (closest candidates - `boundary_layer/`,
  `diagnostics/` - would both be a stretch, not a clean fit).
- `engine.py` (`ScienceEngine`), `query_engine.py`
  (`ScientificQueryEngine`), `registry.py` (`ScientificRegistry`) - real
  cross-cutting infrastructure that orchestrates/queries all the domain
  packages from above; correctly stays flat at the `acf.science` top
  level, exactly where a facade/registry belongs, not domain-specific.

**Confirmed still genuinely absent, not fabricated**: `atmospheric_composition/`,
`ocean/`, `hydrology/`, `cryosphere/`, `land_surface/`, `carbon_cycle/` have
no real content anywhere inside `src/acf/science/` - the closest real code
lives in entirely separate top-level packages (`acf.ocean`, `acf.hydrology`,
`acf.climate` for carbon-cycle-adjacent content, `acf.earth_physics` for
land-surface-adjacent content), already noted in §1's own gap table. Moving
those separate top-level packages *into* `science/` as its own subdomains
would be a real, disclosed architecture decision on its own (not attempted
this phase) - distinct from every reorganization phase so far, which has
only ever relocated code that was already inside `science/`.

**Execution**: all 8 files physically moved via `git mv`. Internal cross-
references repointed: `synoptic.py`'s `potential_vorticity` import,
`moisture.py`'s 7 thermodynamics imports. Three `__init__.py` files
written for the new packages; three existing `__init__.py` files
(`dynamics/`, `convection/`, `thermodynamics/`) extended with the new
real names and a docstring note on what Phase 7 added. Real flat shims
written for `climatology.py`/`synoptic.py`/`cyclones.py`/`wind.py`/
`severe_weather.py`/`moisture.py`; no shims for the two self-collision
cases (`precipitation.py`/`diagnostics.py`). The mandatory sweep found 6
real import statements across 5 already-migrated `awci.*` modules -
repointed to their new direct locations:
`awci/hazards/hydrometeor_phase.py` (`HydrometeorType`),
`awci/complexity/workstation_fields.py` (`BruntVaisalaFrequency`,
`SevereWeather`), `awci/data/model_import_cross_section.py`,
`awci/data/model_import.py` (both deferred, inside-function imports of
`Moisture` - a reminder that the deferred-import sweep from the AWCI
migration still applies here), `awci/data/archive_field.py` (`Moisture`).
Comment-only references in `scientific_status.py`, `diagnostic_registry.py`,
`orographic_froude.py`, and `path_sampling.py`'s own comment-only
`wind_turbulence` reference from §4f, left untouched.

**Verified, not assumed**: `ruff check`/`mypy` clean (49 source files
across the 6 touched packages); identity confirmed programmatically for
all 8 modules (2 self-collision packages checked against their own
`__all__`, 6 real shims checked against their real module, all 3 extended
packages' `__all__` checked for completeness); full test collection under
xvfb - 5050 tests, 0 errors; a broad targeted sweep across every
Phase-7-adjacent keyword (precipitation/diagnostics/climatology/synoptic/
cyclones/wind/severe_weather/moisture/hydrometeor_phase/
orographic_froude/terrain/archive_field/model_import, non-GUI) passed
519/519 (16 skipped). A new
`tests/test_science_precipitation_diagnostics_climate_dynamics_convection_thermodynamics_phase7.py`
(6 tests) locks in the re-export identities for all 8 modules, the
self-collision-vs-real-shim contrast, the 3 extended packages' `__all__`
completeness, the 2 internal cross-references, and the 6 cross-package
fixes into already-migrated `awci.*` code.

With this phase, every real, blueprint-mappable `science/` module has
been reorganized into its per-domain subpackage. What remains for item 2
is: reconciling the 6 already-existing, non-blueprint-named subpackages
(`clouds/`, `encyclopedia/`, `knowledge_graph/`, `laws/`, `observations/`,
`physics_ai/`) with the blueprint's own subdomain names (a real
architecture decision, not a mechanical move - `clouds/` alone holds real
`microphysics.py`/`thermodynamics.py`/`radiation.py`/`dynamics.py`
content that already, coincidentally, shares names with the new
`science/{microphysics,thermodynamics,radiation,dynamics}` concepts,
raising real merge-vs-keep-separate questions for each), the entire
`parameters/` reorganization (including the `acf.science.parameters` vs
`acf.parameters` duplicate-naming question), and the decision on whether
to bring `acf.ocean`/`acf.hydrology`/etc. into `science/` as the
blueprint's own subdomains or leave them as separate top-level packages.

### 4h. Investigating the three remaining items from §4g (2026-09-21) - findings, not file moves

The user asked to continue through everything remaining, one item at a
time. Investigated all three; two resolve with **no code change needed**
(a real, disclosed finding, not a fabricated non-action), the third is a
genuine design decision put to the user rather than executed unilaterally.

**1. Reconciling the 6 non-blueprint-named `science/` subpackages -
resolved, no action needed.** Read every one:
- **`science/clouds/`** already *is* the blueprint's own `science/clouds/`
  subdomain (one of its 19 named subdomains) - it was never a duplicate
  needing reconciliation, just not previously recognized as already
  satisfying the blueprint. Its `microphysics.py`/`thermodynamics.py`/
  `radiation.py`/`dynamics.py`/`severe_weather.py` files each define one
  real, cloud-specific engine class (`CloudMicrophysicsEngine`,
  `CloudThermodynamicsEngine`, `CloudRadiationEngine`,
  `CloudDynamicsEngine`, `SevereWeatherCloudModule`) - genuinely distinct
  code from the general-atmosphere `science/{microphysics,thermodynamics,
  radiation,dynamics,convection}` packages (§4a/§4c/§4e/§4g), which
  happen to share file names because both describe the same physical
  process at different scopes (all-atmosphere vs. cloud-specific) -
  exactly the same kind of intentional, disclosed naming overlap already
  established for `awci.knowledge.hazards` vs. `awci.hazards` earlier in
  this document. This also closes the open question from §4e: no
  separate `science/microphysics/` package was created, because the only
  real microphysics content in the codebase is this cloud-specific
  engine, already correctly placed.
- **`encyclopedia/`, `knowledge_graph/`, `laws/`, `observations/`,
  `physics_ai/`** are real, substantial ACF-specific subsystems (a
  scientific-fact encyclopedia, a knowledge graph, law-verification
  modules, Earth-observation ingestion, physics-informed AI) that simply
  do not correspond to any of the blueprint's 19 named `science/`
  subdomains - there is nothing to reconcile them *with*. They exist
  alongside the blueprint's own domain structure as ACF's own additional
  capabilities, not as competing implementations of the same domains.

**2. `acf.ocean`/`acf.hydrology`/etc. vs. the blueprint's own `ocean/`/
`hydrology/`/etc. subdomains - investigated, recommendation given, not
executed.** `acf.ocean` (13 files: `observations/`, `forecasting/`,
`models/`, `cyclones/`, `oceanography/`, `waves/`) and `acf.hydrology`
(15 files: `drought/`, `observations/`, `soil_groundwater/`, `runoff/`,
`models/`, `flooding/`, `core/`) are both substantial, already
well-organized, independently-structured top-level packages - not flat
modules waiting to be slotted into a subdomain, and not something either
migration effort in this document has ever relocated wholesale (every
phase so far has only ever moved code that was already loosely organized
*within* the package being reorganized). **Recommendation: leave both, and
`acf.climate`/`acf.earth_physics`, exactly where they are.** Moving a
mature, real, already-coherent top-level package into `science/` purely
to match the blueprint's own subdomain name would be pure churn -
real risk (dozens of real callers to repoint) for zero functional
benefit, and contradicts this whole reorganization's own established
principle (see the AWCI `knowledge/` whole-package decision, and
`cyclones.py`'s own disclosed placement in §4g) of not fragmenting or
relocating an already-coherent subsystem for naming purity alone. Not
executed as a move; flagged here as the considered, disclosed
conclusion rather than left silently undone.

**3. The `parameters/`/`catalog/` question - re-investigated 2026-09-21,
§4h's own original assessment corrected: already resolved, no action
needed.** §4h's first pass concluded this needed a real design decision
("four genuinely separate, real, independently-used subsystems... zero
cross-imports... a real product/architecture decision... put to the
user"). That conclusion was itself based on insufficient investigation -
it never read the packages' own `__init__.py` docstrings or the
already-existing compatibility shims, which turn out to already answer
the question. Corrected here rather than left standing:

  - `acf.core.parameter`/`acf.core.parameter_registry` - **already real,
    explicit compatibility shims** ("CORE - Parameter (Compatibility
    Layer forwarding to acf.parameters.parameter)"), each a one-line
    `from acf.parameters.<x> import <X>`. Not an independent duplicate at
    all; `acf.parameters` is already canonical here. Nothing to do.
  - `acf.science.parameters` (`PhysicalParameter`) - a genuinely distinct,
    much richer scientific-documentation data model (governing equation,
    LaTeX form, CF/GRIB2/BUFR/NetCDF cross-references, references,
    limitations, applicability) than `acf.parameters.Parameter`'s simple
    code/name/unit record - a real, intentional homonym, not a duplicate,
    the same class of finding as `PluginManager`/`DataManager`/
    `Divergence`/`Dynamics` already locked in as "different on purpose" in
    `tests/test_collisions_consolidation.py`. Should stay separate; now
    locked in by a new test added to that same file today (see the
    "Verified" note at the end of this section), closing the gap this
    document itself left open in §4a.
  - `acf.catalog` (singular) vs `acf.catalogs` (plural) - **already
    investigated and explicitly documented as intentionally separate**,
    dated 2026-09-06 (before this whole migration session began), in both
    packages' own `__init__.py` docstrings: `acf.catalog` is "the real,
    load-bearing parameter/dataset catalog... verified by grep: this is
    the version actually imported by real application code"; `acf.catalogs`
    is "a small CF/ECMWF-standards-specific extension, NOT a competing
    duplicate" - its own `catalog_manager.py` is already an explicit
    compatibility shim to `acf.catalog.manager`, while its real, distinct
    content (`base_catalog.py`, `cf/catalog.py`, `ecmwf/catalog.py`,
    `hub.py`) is a real, separate concern - a thin `BaseCatalog`-ABC loader
    exposing ACF's own already-real `acf.standards.cf_standard_names`/
    `acf.standards.ecmwf.manager` content through the catalog interface,
    with its own real, distinct caller (`acf.search.scientific_search`).
    Nothing to consolidate; already correctly organized.

  The blueprint's own `parameters/` sketch describes a fifth thing
  entirely - real NWP *parameterization schemes* organized by physical
  domain ("the historical inventory reached 152 parametrization modules")
  - which genuinely does not exist anywhere in this codebase and would be
  new construction, not a reorganization, explicitly out of scope per
  AGENTS.md's "never invent placeholders" rule. This remains the one real,
  honest gap versus the blueprint - not a design decision, a content gap.

  **Lesson for future investigation, stated plainly since this document
  itself got it wrong on the first pass**: before concluding two same-
  vocabulary packages are an unresolved duplicate needing a design
  decision, read their own `__init__.py`/module docstrings and grep for
  existing "Compatibility Layer"/"forwarding to" shims first - this
  codebase has a real, established, already-applied convention
  (`tests/test_collisions_consolidation.py`, "ACF-017 Class Collision
  Resolution") for exactly this situation, and several pairs that look
  unresolved from the file tree alone turn out to already be handled.

  **Verified**: added
  `test_physical_parameter_vs_parameter_is_a_real_homonym_not_a_duplicate`
  to `tests/test_collisions_consolidation.py`, following the file's own
  established `PluginManager`/`DataManager`/`MapCanvas` pattern - real,
  passing, confirms `PhysicalParameter` and `Parameter` are both
  independently constructible and carry genuinely different real fields
  (`governing_equation`/`cf_standard_name`/... vs `code`/`unit`), not
  interchangeable. No source code outside the tests file changed for
  this item - `parameters/`/`catalog/` needed no move, only this
  documentation correction and one new lock-in test.

Both migration efforts (§2, the AWCI separate-package migration, and §4,
the ACF `science/`/`parameters/` reorganization) follow the same proven
method: real investigation before any move, `git mv` + backward-
compatible shims, a mandatory codebase-wide sweep for cross-package
references, and full verification (ruff/mypy/identity checks/targeted and
broad test sweeps/collection) before every commit.
