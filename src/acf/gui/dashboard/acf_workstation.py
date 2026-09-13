"""
ACF Scientific Workstation
============================

Real, AWCI-free "ACF Core" dashboard (built 2026-09-04, explicit user
request/master spec: "ACF CORE ONLY — NO AWCI" — a dashboard exposing
ACF's own modular atmospheric science - Dynamics, Thermodynamics,
Convection, Microphysics, Terrain, Temporal Evolution, Forecast
Confidence, an Interaction Engine, and a multidimensional Complexity
Explorer - never a single AWCI-style score/gauge/classification).
Matches the user's own reference photo,
`docs/reference/acf_dashboard_reference.jpg` (same file already used
by the *different*, AWCI-coupled `acf_general_dashboard.
ACFGeneralDashboard`, which this Workstation now replaces as ESOC's
"ACF Dashboard" entry point - see `acf_general_dashboard.py`'s own
NOTE for that history; it is not deleted, per project convention).

Phase 1 scope (2026-09-04) — a real, working chrome plus 3 real
content modules, all sliced from a SINGLE real solver run:
- **Overview** (`acf_workstation_overview.ACFOverviewPanel`): real
  Temperature/Wind speed/Specific humidity/Pressure fields.
- **Dynamics Lab** (`acf_workstation_dynamics.ACFDynamicsLabPanel`):
  real wind speed, real vorticity, real divergence.
- **Complexity Explorer** (`acf_workstation_complexity.
  ACFComplexityExplorerPanel`): real spatial/temporal/model-
  disagreement complexity dimensions, shown separately, never
  combined into one score.

Phase 2 (2026-09-04, same "continue" progressive discipline) added:
- **Thermodynamics Lab** (`acf_workstation_thermodynamics.
  ACFThermodynamicsLabPanel`): real θ-e (equivalent potential
  temperature)/relative humidity (auto, from the current level) and
  real CAPE/CIN from an actual MetPy parcel ascent (on-demand, a
  coarser real grid - see that module's own docstring for why).

Phase 3 (2026-09-04, same "continue" progressive discipline) added:
- **Microphysics Lab** (`acf_workstation_microphysics.
  ACFMicrophysicsLabPanel`): real surface precipitation-phase
  severity/wet-bulb temperature (auto, from the current level), via
  `acf.awci.hydrometeor_phase`'s own already-real, self-disclosed
  heuristic classification - no new species fabricated.
- **Dynamics Lab** gained a 4th real variable: bulk wind shear (full
  column, independent of the level slider), via
  `acf.awci.wind_shear.compute_real_wind_shear_at_point()`.

Phase 4 (2026-09-04, same "continue" progressive discipline) added:
- **Temporal Evolution Lab** (`acf_workstation_temporal.
  ACFTemporalLabPanel`): a real frame slider scrubbing through an
  actual multi-frame `CoupledEarthSolver` trajectory (on-demand, the
  SAME real `compute_real_complexity_evolution()` engine Complexity
  Explorer's own "Run Temporal Analysis" button already uses, but
  exposing the full real trajectory instead of one aggregated
  rate-of-change map).

Phase 5 (2026-09-04, same "continue" progressive discipline) added:
- **Confidence Lab** (`acf_workstation_confidence.
  ACFConfidenceLabPanel`): a real, full-grid multi-model disagreement
  map (spread/mean, never a single 0-100 confidence score), via a new
  `ModelConsensusEngine.compute_real_multi_model_disagreement_field()`
  classmethod - a real extension of the SAME engine Complexity
  Explorer's own "Compute Model Disagreement" button already uses at
  one point, here run over an entire real grid (measured ~0.9s for 2
  models) - the investigation deferred from Phase 4 found this
  genuinely feasible, not prohibitively expensive.

Phase 6 (2026-09-04, same "continue" progressive discipline) added:
- **Interaction Engine** (`acf_workstation_interactions.
  ACFInteractionEnginePanel`): docs/ACF_MASTER_PROMPT.md §22 ("INTERACTIONS
  — CŒUR DU PROJET") is explicit: "Ne pas inventer arbitrairement
  `interaction = A × B` sans justification physique ou statistique."
  This panel computes the real, standard, published PEARSON
  CORRELATION COEFFICIENT (and its real pointwise spatial
  contribution, rendered as a map) between two real physical fields a
  user picks from across every other Lab already built (Overview's raw
  fields, Dynamics' vorticity/divergence/wind shear, Thermodynamics'
  θ-e/relative humidity, Microphysics' precipitation-phase severity/
  wet-bulb temperature) - a genuinely cross-module, statistically
  justified interaction measure, never an arbitrary unit-mismatched
  product.

Phase 7 (2026-09-04, same "continue" progressive discipline) added:
- **Data Quality Center** (`acf_workstation_quality.
  ACFDataQualityLabPanel`): real per-point docs/ACF_MASTER_PROMPT.md
  §32 quality status (VALID/OUT_OF_RANGE/MISSING/INVALID/...) for
  Temperature/Specific humidity/Pressure/Wind speed, via
  `acf.physics_guard.variable_quality.assess_variable_quality()` - the
  real, already-built §32 taxonomy this codebase had never run over a
  whole grid before. Independently confirmed the real pressure anomaly
  already flagged separately (task_f3c406d9): Pressure reads
  OUT_OF_RANGE at every real grid point (~2013 hPa is outside
  OPERATIONAL_RANGES' real [1000, 108500] Pa bound) - a genuine
  demonstration this real infrastructure catches a real problem, not a
  panel bug.

Phase 8 (2026-09-04, same "continue" progressive discipline) added:
- **Multi-Model Lab** (`acf_workstation_multimodel.
  ACFMultiModelLabPanel`): zero new science - calls the exact same
  `ModelConsensusEngine.compute_real_multi_model_disagreement_field()`
  Confidence Lab already uses, but exposes its previously-unread
  `per_model_field` data: each real model's own RAW field individually,
  plus a real, literal pairwise difference map (`field_a - field_b`,
  real physical units) - a distinct real question from Confidence
  Lab's own aggregate spread/mean ("where do these two SPECIFIC models
  actually disagree, and by how much?").

  Update (2026-09-06, explicit user request "la fusion multi-modèle"):
  the same panel gained a "🔀 Weighted Fusion" button and 2 more
  display choices, calling `ModelConsensusEngine.
  compute_real_weighted_field_fusion()` (a thin wrapper around the
  already-real, already-tested `acf.awci.multi_model_fusion.
  compute_real_multi_model_field_fusion()`) - a real weighted average
  of the 2 selected models' fields plus a real per-point spread field,
  kept as its own independent result state (`self._fusion_result`,
  distinct field-key convention from the comparison above) rather than
  merged into it.

Phase 9 (2026-09-04, same "continue" progressive discipline) added:
- **Real multi-format export** (PNG/SVG/CSV/JSON) on `AWCIMapPanel`
  itself (`awci_map_panel.py`) - so every map in this Workstation (and
  AWCIDashboard's own maps, which share this exact widget) gained 3
  new real export formats for free. The download button's PNG-only
  `QPushButton` became a real `QToolButton` + `QMenu` (same "real
  actions behind one control" convention as ACFGeneralDashboard's own
  "☰" menu) - CSV/JSON export the exact (lons, lats, grid) currently
  on screen, a real NaN cell (e.g. this Workstation's own
  show_demo_fallback=False empty state) honestly written as an empty
  CSV field / JSON `null`, never a fabricated 0.

Phase 10 (2026-09-04, same "continue" progressive discipline) added:
- **Real keyboard shortcuts** - Ctrl+R re-triggers the exact same real
  `refresh()` the "🔄 Run" button already does; F11 toggles the exact
  same real fullscreen the "⛶" button already does; Ctrl+1..Ctrl+9/
  Ctrl+0 jump to one of this Workstation's real enabled modules by its
  real position in `_ENABLED_MODULES` - one real shortcut per real
  module, generated from that same list, so it can never drift out of
  sync with the nav it targets.

Phase 11 (2026-09-04, same "continue" progressive discipline) added:
- **Command Palette** (Ctrl+K, `acf_workstation_command_palette.
  CommandPaletteDialog`): a real, fuzzy-searchable list of this
  Workstation's own already-real actions - "Run", "Toggle Fullscreen",
  "Go to <module>" for each of the 10 real enabled modules, and every
  on-demand Lab action (CAPE/CIN, temporal analysis, model
  disagreement, temporal evolution, model confidence, model
  comparison) - each entry a direct reference to the real method/
  button it triggers, never a new capability. Non-modal open-or-raise
  (`.show()`), same convention as `AWCIExecutionReportDialog`.

Phase 12 (2026-09-04, same "continue" progressive discipline) added:
- **Configuration Management** - the "⚙" button (previously disabled,
  its own tooltip disclosing "not yet implemented") became a real
  QToolButton + QMenu (same convention as the export menu/"☰" menu):
  "💾 Save Configuration…"/"📂 Load Configuration…" serialize/restore
  the real user-chosen SETTINGS this Workstation's model/level/nav/
  every Lab's own variable selector currently hold, as real JSON - the
  real computed DATA is never saved/replayed as a stand-in for a fresh
  solver run (this project's own no-fake-functionality rule); loading
  a configuration only restores what to look at, then the user still
  presses "🔄 Run" for real data. Also reachable from the Command
  Palette. A level_index restored before any real volume exists yet is
  honestly held pending and clamped against the next real volume's own
  real level count once computed.

Phase 13 (2026-09-04, same "continue" progressive discipline) added:
- **`/api/v1/workstation` HTTP API** (`acf.web.routers.
  workstation_router`) - closes the master spec's own disclosed
  "extension API pour ces nouveaux modules" item. Real
  `/theta_e`/`/dynamics`/`/wind_shear` GET endpoints call the exact
  same real functions the Dynamics/Thermodynamics Labs' own GUI panels
  use. Those functions were moved from the GUI panel modules (which
  import PySide6) into a new, real, Qt-free `acf.awci.
  workstation_fields` module first, so this web router never needs a
  GUI toolkit importable in the server process - the GUI panels now
  import the same functions FROM there (a plain re-export, zero
  behavior change, verified by the full existing GUI test suite
  passing unchanged). Same real request-size guard convention as
  `complexity_router`/`events_router` (`_solver_guard.py`, extended
  with a new `run_complexity_volume()` for a full 3D request).

Phase 14 (2026-09-04, same "continue" progressive discipline) added:
- **3D View** (`acf_workstation_3d.ACF3DAtmospherePanel`) - docs/
  ACF_MASTER_PROMPT.md §23's own explicit "3D — Structure volumique".
  Real `matplotlib` `Axes3D.contourf(..., zdir="z", offset=pressure)`
  stacks up to 6 real native levels of the current volume in one real
  3D view, each positioned at its own real mean pressure (never
  interpolated between levels) - a real "data cube", not a fabricated
  isosurface. No geographic basemap (disclosed in its own title) -
  real longitude/latitude/pressure axes only.

Phase 15 (2026-09-04, same "continue" progressive discipline) added:
- **Case Study Lab** (`acf_workstation_case_study.
  ACFCaseStudyLabPanel`) - honest reinterpretation, not fabricated
  data: this codebase has no real archived historical weather events
  anywhere (`CoupledEarthSolver` always stands in for a real
  operational model), so a "case" here is a real, named, reproducible
  Workstation CONFIGURATION (reusing Phase 12's own `_export_
  configuration()`/`_apply_configuration()`) the user bookmarks -
  never a claim that a real historical event is being replayed. Same
  "settings, never data" rule as Configuration Management: loading a
  case still requires pressing "🔄 Run" for fresh real data. Saved
  durably as real JSON under `<repo_root>/data/workstation/
  case_studies.json` (same real `data/*` convention as
  `events_router`/`datasets_router`'s own storage).

Phase 16 (2026-09-04, same "continue" progressive discipline) added:
- **Research Mode** (top-bar "🔬" toggle) - clicking Thermodynamics/
  Microphysics Lab's own map (reusing `AWCIMapPanel.pointClicked`,
  already real, already tested elsewhere) re-calls the exact real
  per-point formula fresh at the nearest real grid point
  (`compute_real_theta_e_at_point()`/`compute_real_hydrometeor_phase_
  at_point()`) and shows its FULL real return (dewpoint, relative
  humidity, wet-bulb, the function's own real `honest_limitation`
  text…) in a real dialog - not just the single value already
  rendered on the map. Real, bounded first pass: only these 2 Lab
  panels support it today, disclosed as such, not every panel.

Phase 17 (2026-09-04, same "continue" progressive discipline) fixed a
real root cause rather than adding a new module: the ~2013 hPa
pressure anomaly independently confirmed 3 times across this
Workstation (Thermodynamics Lab, Data Quality Center, Research Mode) -
task_f3c406d9 - was found and fixed. Root cause:
`acf.simulation_engine.numerical_core.earth_grid.EarthGrid`'s own
hybrid sigma-pressure `a_coeff` started at 100000.0 Pa instead of the
real, physically-required 0.0 Pa at the surface (b_coeff=1.0 there),
adding a spurious +1000 hPa to every real solver run's own real
surface pressure. One-line fix (`a_coeff = np.linspace(0.0, 100.0,
n_levels)`), verified against the FULL pre-existing test suite (4176
tests) before this fix - only 1 test failed, and it was a regression
guard for the anomaly itself (now updated to assert the corrected
VALID status instead). See `earth_grid.py`'s own NOTE and reports/
ACF_MASTER_AUDIT_v2.md's dated entry for the full investigation.

Phase 18 (2026-09-04, following the user's explicit "tu es le chef,
tu gères selon ton jugement" delegation) corrects the Phase 1/8
dismissal of Convection Lab above: that dismissal was wrong. A closer,
more thorough search of this codebase (the one this delegation
prompted) found that real, independent, SPC (NOAA Storm Prediction
Center)-verified composite formulas already existed and simply hadn't
been found the first time - `acf.science.storm_motion.StormMotion`
(Bunkers et al. 2000), `acf.science.storm_relative_helicity.
StormRelativeHelicity` (Davies-Jones/Burgess/Foster 1990),
`acf.science.severe_weather.SevereWeather` (SCP/STP/EHI), and
`acf.science.lcl.LCL` (Bolton 1980) all had real, complete, cited
implementations already sitting in the tree. The new **Convection
Lab** (`acf_workstation_convection.ACFConvectionLabPanel`, real
pipeline in `acf.awci.workstation_fields.
compute_real_convection_indices_field()`) composes these into 8 real,
separately-shown fields - CAPE, CIN, LCL height, bulk wind shear,
storm-relative helicity, EHI, SCP, STP - never merged into one further
fabricated score, same on-demand/off-thread/coarser-grid discipline as
Thermodynamics Lab's own CAPE/CIN. Building it against this solver's
own real output surfaced two real, disclosed characteristics of the
solver's own data, deliberately NOT fixed here (each flagged
separately for its own investigation, not blocking this Lab): CIN
comes out several thousand J/kg (real operational CIN is typically
0-300 J/kg) even though the same, already-tested CAPE/CIN pipeline is
applied correctly; and this solver's own real full-column wind shear
stays under 10 m/s across every configuration tried, so SCP's own
real EBWD term (by definition 0 below that threshold) reads 0 here - a
real, honest result given this solver's own real wind field, not a
bug in the formula or in SCP itself. See `acf_workstation_convection.
py`'s own module docstring for the full disclosure.

Phase 19 (2026-09-04, same "continue selon ton jugement" delegation)
investigated the first of those two disclosed findings (task_9f9c2f99)
and found a real, fixable bug, not just a solver characteristic:
`acf.awci.convective_energy.compute_real_cape_cin_at_point()` was
integrating negative buoyancy over the WHOLE real profile up to its
own 100 hPa cutoff, rather than stopping at the parcel's real Level of
Free Convection (LFC) - real operational CIN only counts the
negative-buoyancy area BELOW the LFC, not a genuinely stable layer
many kilometres above any real storm top. Fixed by calling MetPy's own
already-vetted `mpcalc.surface_based_cape_cin()` directly (the same
real function `acf.science.parcel_ascent.ParcelAscentEngine` already
wraps for a `SoundingProfile`) instead of hand-deriving the LFC/EL
bounding logic a second time - see that module's own docstring for the
full root-cause investigation (including a first attempt that fixed
the unstable case but not the equally-common genuinely-stable one) and
the fix. CIN now reads realistically (0-a few hundred J/kg, matching
real operational values) on this solver's own real output, verified
across multiple seeds/grid points; the Convection Lab's own CIN range
was updated from a dynamic percentile scale (needed while the
magnitude was inflated) to a fixed, generous 0-500 J/kg envelope.

Phase 20 (2026-09-04, same delegation, after the user explicitly chose
to pursue a real fix rather than leave it disclosed) resolved the
second finding (task_17a412ee): this solver's own full-column wind
shear stayed under 10 m/s because `acf.simulation_engine.
atmosphere_solver.atmospheric_model.AtmosphericModel.
initialize_state()` drew `U`/`V` independently at every real vertical
level with no structure at all - unlike `T`, which at least gets a
real standard lapse rate. Fixed by adding a real thermal-wind-balance
vertical shear (Holton & Hakim, "An Introduction to Dynamic
Meteorology") to `U`, on top of the exact same real per-level
stochastic draw this solver already used - see that module's own
docstring for the full derivation and its two real, disclosed
simplifications (equatorial regularization, a tropopause-region cap
preventing unbounded growth into the stratosphere). Real bulk shear
now spans a realistic 0-50 m/s range (verified across seeds/points) and
SCP genuinely varies instead of reading exactly 0 everywhere. Honest
scope, also disclosed there: this is a real SPEED shear, not a real
DIRECTIONAL one - `V` still has no systematic turning with height, so
SRH/EHI/SCP/STP may still often read small or negative on a
straight (non-veering) hodograph, a real, known meteorological
consequence, not a further bug.

Phase 21 (2026-09-04, same "continue selon ton jugement" delegation)
extended `/api/v1/workstation` (Phase 13) with a real `/convection` GET
endpoint - the same real `acf.awci.workstation_fields.
compute_real_convection_indices_field()` pipeline the Convection Lab's
own button uses, closing the same "extension API pour ces nouveaux
modules" item Phase 13 first opened, for the one real module built
since (Phase 18) that Phase 13 couldn't have covered yet. A dedicated
`validate_convection_stride()` guard (`_solver_guard.py`) additionally
bounds this endpoint's own real per-point MetPy parcel-ascent cost
(~5ms/point) - separate from, and stricter than, `run_complexity_
volume()`'s existing pre-stride solver-size guard, since a small
`stride` on an otherwise-small-enough volume could still request an
unbounded number of real parcel ascents.

Phase 22 (2026-09-04, explicit user authorization: "tu as mon accord")
built the **Terrain Lab** - the last remaining planned §8 spec module,
closing this Workstation's build-out. `acf.awci.orographic_froude`'s
own module docstring had named the exact real blocker:
"CoupledEarthSolver's real state has no terrain-elevation field at
all" - a real, cited mountain-wave Froude number formula already
existed (`compute_real_mountain_wave_froude_number_at_point()`, ICAO
Doc 9817), genuinely unable to run for lack of real input data. With
the user's explicit permission to download one real, small, external
file, `acf.awci.terrain_elevation` supplies it: a real, bundled 111 KB
SRTM15+ V2.7 1 arc-degree global elevation grid (Tozer et al., 2019,
Earth and Space Science - GMT's own official public data server; see
that module's own `data/NOTICE.md` for the full source/license
disclosure), interpolated onto this solver's own real grid. The new
**Terrain Lab** (`acf_workstation_terrain.ACFTerrainLabPanel`, real
pipeline in `acf.awci.workstation_fields.compute_real_terrain_field()`)
shows 3 real, separately-shown fields - terrain elevation, near-
surface Brunt-Väisälä static stability, and the real mountain-wave
Froude number - never merged into one further fabricated score.
Auto-rendered, not on-demand: unlike CAPE/CIN's real MetPy parcel
ascent, the real formulas here are simple, closed-form, and fully
vectorized across the whole real grid (verified in well under a
second even at this Workstation's largest real grid, AROME's
90x180=16200 points) - see that function's own docstring for the real
formulas composed and their honest, disclosed simplifications.
`_PLANNED_MODULES` is now empty - every real §8 spec module this
Workstation's plan named is built.

Phase 31 (2026-09-04, explicit user request, attaching the
Workstation's own true reference mockup -
`docs/reference/acf_scientific_workstation_reference.jpg` - and stating
twice: "garder ce modèle... ne change rien à 100%" and "chaque
détails... je veux garder le moindre détail et l'afficher a la
perfection comme dans les photos") realigned this Workstation's own
chrome to match that mockup's real nav tree exactly, as the first,
user-confirmed ("Structure d'abord") pass toward that full goal - a
real structural pass, not the complete pixel-perfect rebuild, which
continues in later phases:
- `_ENABLED_MODULES` now holds the mockup's own real 11 nav labels/
  order (Overview, Atmosphere State, Complexity Explorer, Atmospheric
  Interaction Engine, Dynamics/Thermodynamics/Convection/Microphysics/
  Terrain Lab, Temporal Evolution Lab, Forecast Consistency Lab) -
  every real Lab this Workstation already had keeps its own real
  backend and tests unchanged; only its nav label/position changed.
- The 4 real modules the mockup's own tree does not show
  (`_TOOLBAR_MODULES`: Multi-Model Lab, Data Quality Center, 3D
  Atmosphere View, Case Study Lab) were **not deleted** - moved to a
  real "🧰 More Labs" toolbar menu instead (`ne détruis pas
  l'existant`, this project's own established rule).
- Routing switched from row-index-coupled `stack.setCurrentIndex(row)`
  to a real `self._panel_by_name: dict[str, QWidget]` +
  `stack.setCurrentWidget(...)`, via the single `_navigate_to()` entry
  point every "go to X" control (nav list, Overview's own Quick
  Navigation buttons, the toolbar menu, the Command Palette) now
  shares - so nav content/order can change without breaking any other
  module's own mapping.
- Added the real, previously-missing **Overview** landing page
  (`acf_workstation_overview_landing.ACFOverviewLandingPanel`) - real
  current-model `MODEL_CONFIGS` grid metadata and real run status
  (mirrored verbatim from `status_label` via the new `_set_status()`
  sink), plus real quick-navigation buttons - no map, no composite
  score, nothing fabricated. The former sole "Overview" (the raw-
  fields map panel) is unchanged, relabelled "Atmosphere State".
- Relocated the real Research Mode toggle from the top bar into a new
  "DIAGNOSTICS" nav section, and added a real "DATA SOURCES" nav
  section (Model Data / Observations / Scientific Explorer), matching
  the mockup's own left-column layout:
  - **Model Data** opens a real dialog listing this Workstation's own
    real `MODEL_CONFIGS` grid metadata for all 3 real models.
  - **Observations** is an honest disclosure dialog - no real
    observation feed is connected; every field elsewhere in this
    Workstation comes from a real, live `CoupledEarthSolver` run.
  - **Scientific Explorer** is a real, live search dialog over
    `acf.science.encyclopedia.registry.EncyclopediaRegistry`'s own
    real, populated formula database (`search()`/`list_entries()`) -
    real name/domain/equation/description/references per entry, never
    fabricated.
Explicitly deferred to follow-up phases (disclosed, not silently
dropped): the "ACF Pipeline Monitor" status box, the always-visible
right-side panels (Vertical Complexity Sounding / Atmospheric
Interaction Graph / Forecast Consistency), the Global Timeline
scrubber with forecast-hour thumbnails, the Dynamics/Thermodynamics Lab
bottom thumbnail strips, and full Domain-selector-driven geographic
cropping across every panel.

Phase 32 (2026-09-04, continuing the same "pixel-perfect" goal,
picking the next item off Phase 31's own disclosed deferred list) built
the real "ACF Pipeline Monitor" status box, matching the mockup's own
left-column INGESTION/QC/NORMALIZATION/MODULES/INTERACTIONS/ANALYSIS/
VISUALIZATION stages exactly. `ACFPipelineMonitorWidget`
(`acf_workstation_pipeline_monitor.py`) is a pure display widget; every
status it shows is set from a real, verifiable place in this class's
own `refresh()`/`_on_volume_ready()`/`_on_volume_failed()` - Ingestion
once the real model/grid config is validated, Modules once the real
off-thread `compute_real_complexity_volume()` run completes, QC/
Normalization from two new real, Qt-free checks
(`acf_workstation_pipeline_checks.py`: `run_real_range_qc()` against
`acf.physics_guard.range_check.OPERATIONAL_RANGES`, and
`run_real_derivation_consistency_check()` re-verifying
`wind_speed_volume == sqrt(u_volume**2+v_volume**2)` and
`pressure_volume_hpa`'s strict positivity), Interactions/Analysis/
Visualization by directly inspecting whether each real panel's own
`_volume` attribute now points at this run's volume - never a
fabricated or cosmetic tick. Honest, real finding surfaced by this:
every real MODEL_CONFIGS grid's own top model level reaches ~1 hPa,
below OPERATIONAL_RANGES's own documented tropospheric-only 10 hPa
floor - QC genuinely reports "WARN" on every real run for this reason,
disclosed rather than hidden or worked around.

Phase 33 (2026-09-05, next item off the same disclosed deferred list)
built the first of the mockup's own 3 always-visible right-side
panels: the **Vertical Complexity Sounding**
(`acf_workstation_sounding_panel.ACFVerticalSoundingWidget`) - a real
temperature/wind-speed profile at a real (lat, lon) point, pressure-
inverted, fed by `acf.awci.vertical_field.vertical_profile_at_point()`
(a real nearest-neighbour column lookup already used by
`acf.awci.temporal_field`/`acf.awci.archive_field` - extended here to
also return `wind_speed_profile`, additive, no existing caller
affected). Every real Lab panel with its own map exposes
`AWCIMapPanel.pointClicked`; this class connects every one of them
(discovered via `hasattr(panel, "map_panel")`, not a hardcoded list)
to one shared `_on_map_point_clicked()` handler, so clicking ANY of
this Workstation's own maps updates the SAME persistent sounding
panel - matching the mockup's own single, shared right-column
position. Before any real click, `_on_volume_ready()` defaults it to
the real volume's own grid-center point rather than leaving it empty.
Deferred, disclosed: the mockup's own small colored stability-index
grid beside its sounding plot (High Shear/Stability/CIN/CAPE/Wind
Shear) - no real per-point stability summary exists at every column
today (only Thermodynamics Lab's own Research Mode click computes
real CAPE/CIN, and only for its own single point) - and the other 2
always-visible side panels (Atmospheric Interaction Graph, Forecast
Consistency).

Phase 34 (2026-09-05) built the second always-visible side panel:
the **Atmospheric Interaction Graph**
(`acf_workstation_interaction_graph_panel.ACFInteractionGraphWidget`) -
a real 5-node correlation network (Wind/Terrain/Humidity/Temperature/
Precipitation) at the current level, every edge the SAME real,
statistically-justified Pearson correlation
`acf_workstation_interactions.compute_real_local_interaction()` the
Interaction Engine tab already computes on demand - reused as-is here,
never reimplemented, just auto-applied to a fixed real node set and
drawn as a small network (edge color = sign of r, thickness/opacity =
|r|). Honest node-choice disclosure: the mockup's own 5th label reads
"Convection"; no real, cheap, always-available gridded convection
field exists in this Workstation today (CAPE/CIN is on-demand,
per-point only) - real Temperature substitutes for it instead of a
fabricated convection proxy. Re-sliced in `_on_volume_ready()`/
`_on_level_changed()` alongside the sounding panel (measured ~50ms at
AROME's own full 90x180 grid - cheap, no new solver run).

Phase 35 (2026-09-05, user delegated the design choice - "à toi de
voir l'idéal et efficace et rentable" - after being asked whether this
panel should compare models or successive forecast runs) built the
third and last always-visible-slot side panel: **Forecast
Consistency** (`acf_workstation_forecast_consistency_panel.
ACFForecastConsistencyWidget`) - reuses `ModelConsensusEngine.
compute_real_multi_model_disagreement_field()` exactly as Confidence
Lab's own on-demand button already does (one real solver run per real
model, regridded, real ensemble spread/mean), drawn here as a compact
real bar chart of each real model's own mean field value plus the real
ensemble spread as text. Stays on-demand (its own "▶ Compare" button,
not automatic) - same real-cost discipline as every other genuinely
expensive computation in this Workstation, and NOT tied to the main
"🔄 Run" volume (same "stays whatever it was" convention as Confidence
Lab / CAPE/CIN). Honest disclosure: the mockup's own literal x-axis
label reads "Sun N, N-1, N-2" (successive forecast RUNS over time) -
this Workstation has no real archived forecast-run history to compare
against (every field is a live solver run, never an archived NWP
product) - built as real MODEL-to-model consistency instead, a
genuine, already-built measure along a different real axis, disclosed
rather than faking a run history. All 3 mockup side panels are now
real and present; only the mockup's own small stability-index color
grid stays deferred (see Phase 33's own disclosure above).

Phase 36 (2026-09-05) built the real **Map Inspector**
(`acf_workstation_map_inspector.ACFMapInspectorDialog` +
`compute_real_map_inspector_snapshot()`) - a real, non-modal popup
that opens/refreshes on every real map click (any Lab panel's own
`AWCIMapPanel.pointClicked`, same shared `_on_map_point_clicked()`
already driving the sounding/interaction-graph panels), showing real
lat/lon/elevation/slope/aspect (`acf.awci.terrain_elevation.
compute_real_terrain_slope_aspect_at_point()`, added alongside this
panel - real central-differencing of the bundled elevation grid, at
its own real ~1-degree resolution, honestly disclosed as coarse, not
high-resolution local relief), real temperature/wind/humidity/
pressure at that exact point, real relative humidity/θ-e
(`acf.awci.theta_e.compute_real_theta_e_at_point()`), real
precipitation phase/wet-bulb (`acf.awci.hydrometeor_phase.
compute_real_hydrometeor_phase_at_point()`), real vorticity/
divergence (`acf.awci.workstation_fields.
compute_real_vorticity_divergence()`, evaluated over the current
level's real grid and sampled at the point), and real bulk wind shear
(`acf.awci.wind_shear.compute_real_wind_shear_at_point()`) - every
value a real, already-existing ACF function called fresh at the
clicked point, nothing new invented. Honest scope: CAPE/CIN is
deliberately NOT computed here (that real MetPy parcel-ascent
calculation is genuinely more expensive per point and already has a
dedicated home in Thermodynamics Lab's own Research Mode) - the
inspector says so explicitly rather than silently omitting it.

Phase 37 (2026-09-05) added a real thumbnail strip
(`acf_workstation_thumbnail_strip.ACFVariableThumbnailStrip`) below
Dynamics Lab's own main map, matching the mockup's own bottom
"DYNAMICS LAB" thumbnail row - a real, lightweight (plain
`pcolormesh`, no cartopy projection) small-multiple preview of all 4
real variables that Lab already offers (Wind speed/Relative
vorticity/Divergence/Bulk wind shear), computed once per redraw
(`ACFDynamicsLabPanel._all_fields()`) and shared between the main map
and every thumbnail - never recomputed per thumbnail. Clicking a
thumbnail switches the main map to it via the same real
`variable_selector`, no separate selection state.

Phase 38 (2026-09-05) closed Phase 37's own disclosed follow-up: a
matching real thumbnail strip for Thermodynamics Lab (Temperature/Dew
Point/θ-e/Inversions, exactly the mockup's own 4 labels). Two new real
field functions in `acf.awci.workstation_fields` made this possible
without any new physics: `compute_real_dewpoint_field()` reuses
`compute_real_theta_e_at_point()`'s own real `dewpoint_k` intermediate
value (already computed there, previously discarded) in a new,
separate per-point loop - kept separate from
`compute_real_theta_e_and_rh_fields()` rather than adding a 3rd return
value, so every one of that function's existing real callers (4 call
sites plus the `/api/v1/workstation` HTTP router) keeps its exact
current 2-value unpacking unchanged; `compute_real_temperature_
inversion_field()` is a real, disclosed, standard definition (real
`np.diff` along the level axis, clipped to non-negative - the real
maximum temperature-increase-with-height found in each column, 0 where
none exists) - genuinely new arithmetic, but standard, not invented
physics. `ACFThermodynamicsLabPanel`'s own `variable_selector` grew 3
new real entries (Temperature/Dew Point/Inversions) alongside its
existing θ-e/Relative humidity, so every thumbnail has a matching
full-size main-map view - nothing removed, only added. All 4 mockup
thumbnail rows this Workstation's 2 relevant Labs can honestly support
are now real and present.

Phase 39 (2026-09-05) built the **Stability Indices** panel
(`acf_workstation_stability_indices.ACFStabilityIndicesWidget`),
closing the sounding panel's own disclosed "Honest scope" gap from
Phase 33 - the mockup's small colored grid beside its sounding plot
(CAPE/CIN/Wind Shear/Static Stability). Every value is real and reused
as-is at the same clicked point: CAPE/CIN from `acf.awci.
convective_energy.compute_real_cape_cin_at_point()` (the same real
MetPy pipeline Thermodynamics Lab's own on-demand button uses - cheap
enough, ~5ms, for ONE point, unlike a whole grid), bulk wind shear
from `acf.awci.wind_shear.compute_real_wind_shear_at_point()`, and a
new real, scalar `compute_real_near_surface_static_stability_at_point()`
(`acf.awci.workstation_fields`) - the real, cheap (~7 microseconds,
measured) scalar sibling of `compute_real_terrain_field()`'s own
vectorized near-surface N, added so this per-point panel never pays
that function's own full-grid elevation/Froude-number cost (~0.5s at
AROME's own full resolution) just to read one value; cross-checked to
agree with it exactly. Independent of the level slider (CAPE/CIN/
shear/N are inherently full-column or lowest-2-level diagnostics), so
only updated in `_on_volume_ready()`/`_on_map_point_clicked()`, not
`_on_level_changed()`.

Phase 40 (2026-09-05) built the real **Domain** selector, matching the
mockup's own top-bar "Domain: Western Mediterranean" chip -
`acf_workstation_domain.crop_real_volume_to_domain()` slices EVERY
real lat/lon-shaped array an already-computed volume carries down to a
real, named rectangular box (generic over the volume's own field
names via shape-matching, not a hardcoded key list) - "Global" (no
crop) shows the real solver's own full native grid exactly as before;
any other real region only crops, never re-runs the solver and never
fabricates regional data. `_render_all_panels()` now computes this
real crop once per render and passes the SAME cropped object to every
real nav-tab panel (`_domain_cropped_volume()`); the always-visible
side panels (Sounding/Interaction Graph/Stability Indices/Map
Inspector) deliberately stay on the real, full uncropped volume - they
are per-point diagnostics, not maps, and a Domain selection should
never shrink what a click can reach. A real, honest minimum of 2x2
grid points is enforced (matplotlib's own `contourf()` genuinely
cannot render fewer) - a too-thin real crop falls back to Global with
a disclosed status message rather than crashing or rendering nothing.
The Pipeline Monitor's own Interactions/Analysis/Visualization checks
were fixed to compare against the actual real object every panel
received (`display_volume`, returned by `_render_all_panels()`) rather
than the raw run's own `volume` parameter, so re-running while a non-
Global domain is already selected never reports a false FAIL.

Phase 41 (2026-09-05) built the real **Global Timeline (Time
Machine)** bar (`acf_workstation_global_timeline.
ACFGlobalTimelineWidget`), a full-width bar at the very bottom of the
Workstation, matching the mockup's own position. Fed by `acf.awci.
temporal_field.compute_real_complexity_evolution()` - the SAME real
multi-frame `CoupledEarthSolver` integration Temporal Evolution Lab's
own on-demand button already uses (`n_frames=4`/`steps_per_frame=3`,
the same real constants) - real, on-demand (its own "🔄 Run Temporal
Analysis" button), independent of the main volume. Each real frame
gets a real thumbnail (`acf_workstation_thumbnail_strip.
ACFVariableThumbnailStrip`, extended with 2 new real, reusable
capabilities - `set_label()` for a post-computation real forecast-hour
label, `set_selected()` for a real highlight of the current frame) of
that frame's own real surface temperature, labelled with its own real
valid time. A real Play/Pause + speed control cycles through the
ALREADY-computed real frames (a `QTimer` UI convenience, never a new
computation per tick). Honest, disclosed scope: scrubbing here updates
only this widget's own readout - it does NOT drive the level slider,
Domain selection, or any nav-tab panel; wiring that would be a
substantially larger, separate integration, not attempted in this
pass.

Phase 42 (2026-09-05) closes the reference-mockup-parity project with
a deliberate NON-build, disclosed rather than silently skipped: the
mockup's own central "Domains"/"Layers" checklist (a long, repetitive
list - "Raster Layer"/"Vector Layer" appearing many times over,
alongside one confirmed-illegible AI-mockup-generation artifact
elsewhere on the same image, the Global Timeline's own caption) has no
real, distinct functional correspondence in this Workstation today -
every one of its own map panels already draws exactly one real,
already-controllable data layer (the selected variable's own
contour), not several independently toggleable raster/vector layers.
Investigated real options (a public `AWCIMapPanel.set_contour_
visible()` toggle; reusing that class's own existing AWCI-dashboard
Layers panel) were rejected: the latter hardcodes an "AWCI" checkbox
label, which would violate this Workstation's own explicit "ACF CORE
ONLY - NO AWCI" rule stated at the very top of this docstring. Rather
than build a thin, likely-confusing checklist just to visually match a
list that does not reliably specify real intended functionality, this
is disclosed as an intentional, permanent non-build - the same
"honest gap over invented affordance" discipline `awci_map_panel.py`'s
own docstring already established for its 6 real-data-less demo
layers. With this decision, every element of the reference mockup with
a real, honest functional correspondence (10 of the original 11
identified structural items) is now built - see `reports/
ACF_MASTER_AUDIT_v2.md`'s own Phase 32-42 entries for the full,
disclosed history of this project.

REBUILD (2026-09-13) — new reference image, new layout
---------------------------------------------------------
Everything above is this Workstation's own real history against its
PREVIOUS reference mockup (`docs/reference/acf_scientific_workstation_
reference.jpg`), kept verbatim as the honest record of why each real
panel exists. This module's LAYOUT no longer targets that image: per
`docs/superpowers/specs/2026-09-13-acf-workstation-rebuild-design.md`,
the sole visual authority is now `acf_workstation_reference.jpg` (repo
root), a genuinely different design. No real science was removed - the
recovered Lab panels keep their exact real backends and are all still
present; they are laid out differently and joined by 6 new panels.

Real layout actually built here (top to bottom), and where each piece's
real data comes from:
- Left: `acf_workstation_sidebar.WorkstationSidebar` (static nav tree).
  It never hides a panel - selecting a section scrolls the real
  content column to the matching real area (`_on_section_selected()`),
  and the two sub-entries that have a real dialog behind them
  (Data > Models / Data > Observations) open it.
- `acf_workstation_config_bar.ConfigBar` - the real ACTIVE RUN's own
  metadata, filled in `_on_volume_ready()` only (never from the model
  selector's pending value, so the bar can never claim a configuration
  that no panel below is actually showing).
- Hero "Atmospheric Complexity": `ACFComplexityExplorerPanel`'s OWN
  real spatial-complexity map widget, re-parented here (the same
  widget object its own `update_from_volume()` keeps drawing into -
  no second map, no duplicated logic), plus `ACFTemporalLabPanel`'s
  OWN real transport controls (run/frame slider/frame label).
  Disclosed: the transport scrubs that panel's real multi-frame
  trajectory, which renders in the "Time Evolution" cell below - the
  hero map itself shows the current level's real spatial complexity
  and is not animated by it.
  Deliberate non-build (disclosed, not silently dropped): the
  reference image's hero 2D/3D/4D toggle and "Layers" button. No real
  3D/4D panel survives this session's cleanup for the toggle to
  switch to, and every map here draws exactly one real, already-
  selectable field - a toggle with nothing real behind it would be a
  fabricated affordance (same discipline as Phase 42 above).
- Row 1: `KeyVariablesPanel` + `ComplexityOverviewPanel` +
  `ModelAgreementPanel` + `HazardAlertsPanel`.
- Row 2: Vertical Cross Section (honest
  NOT_AVAILABLE_NO_CROSS_SECTION_WIDGET_RECOVERED placeholder - no
  real cross-section widget exists in this rebuild's recovered panel
  set; checked directly in `acf_workstation_complexity.py`, which the
  task brief expected to carry one) + Atmospheric Profiles
  (`ACFVerticalSoundingWidget`) + Model Comparison
  (`ACFMultiModelLabPanel`) + Time Evolution (`ACFTemporalLabPanel`).
  Disclosed deviation from the reference image's literal shape (fix
  round 1, 2026-09-13): "Model Comparison" and "Time Evolution" reuse
  `ACFMultiModelLabPanel`/`ACFTemporalLabPanel` as complete widgets -
  their own existing real map-based UI - rather than building the
  reference image's literal "2×2 mini-map grid"/"per-model line chart"
  shape. Same honesty convention as the Vertical Cross Section gap
  above: the real functional correspondence (model comparison data,
  time-evolution data) is genuinely there, just presented via each
  panel's own already-real widget rather than a re-built literal shape.
- Science Labs tabs: `ACFOverviewPanel` (Atmosphere State),
  `ACFThermodynamicsLabPanel`, `ACFComplexityExplorerPanel` (its real
  temporal/model-disagreement half) and `ACFConfidenceLabPanel` -
  every recovered real Lab stays reachable, nothing deleted.
- `acf_workstation_footer.SystemFooterPanel` - real
  `HPCConnectionManager.get_status_summary()` status plus this
  Workstation's own real pipeline-activity log.

Single real computation per run, shared by every panel
--------------------------------------------------------
`refresh()` starts ONE real `compute_real_complexity_volume()` run
off-thread, then ONE real `compute_real_convection_indices_field()`
run off-thread over that same volume (`_IndicesWorker`) - the real
MetPy parcel-ascent pipeline behind CAPE/CIN/LCL/bulk shear, measured
~3.2s on ARPEGE's own real grid. That single real result feeds BOTH
`KeyVariablesPanel` and `HazardAlertsPanel` (which is why
`KeyVariablesPanel.update_from_volume()` now accepts it), and it is
computed once per real VOLUME, not once per level change: every index
in it is a full-column diagnostic, genuinely independent of the level
slider.

Real data source, once, re-sliced everywhere
-----------------------------------------------
A real off-thread `_VolumeWorker` runs
`acf.awci.vertical_field.compute_real_complexity_volume()` (a real
`CoupledEarthSolver` run at AROME/ALADIN/ARPEGE's own real
`MODEL_CONFIGS` grid - the exact 3 real names the reference photo's
own Model chip shows) on "🔄 Run" or a Model-selector change. Every
content panel re-slices the SAME resulting volume (compute once,
re-slice per tab/level, this codebase's own established discipline -
`AWCIDashboard`/`ACFGeneralDashboard` already use it) - never a second
solver run per tab switch. Only the volume's real physical fields
(`temperature_volume`/`wind_speed_volume`/`u_volume`/`v_volume`/
`specific_humidity_volume`/`pressure_volume_hpa`) are ever read;
`awci_volume`/`physical_volume`/`forecast_volume` are never touched.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import UTC, datetime
from typing import Any

import numpy as np
import shiboken6
from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, QTimer, Signal
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QScrollArea,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.awci.workstation_fields import (
    CONVECTION_GRID_STRIDE,
    compute_real_convection_indices_field,
)
from acf.forecast.engine import MODEL_CONFIGS
from acf.gui.dashboard.acf_workstation_complexity_overview import ComplexityOverviewPanel
from acf.gui.dashboard.acf_workstation_config_bar import ConfigBar
from acf.gui.dashboard.acf_workstation_footer import SystemFooterPanel
from acf.gui.dashboard.acf_workstation_hazard_alerts import HazardAlertsPanel
from acf.gui.dashboard.acf_workstation_key_variables import KeyVariablesPanel
from acf.gui.dashboard.acf_workstation_model_agreement import ModelAgreementPanel
from acf.gui.dashboard.acf_workstation_sidebar import WorkstationSidebar

# Conditional imports for modules that may be under rebuild
ACFComplexityExplorerPanel = None
ACFConfidenceLabPanel = None
ACFMultiModelLabPanel = None
ACFOverviewPanel = None
ACFVerticalSoundingWidget = None
ACFTemporalLabPanel = None
ACFThermodynamicsLabPanel = None

try:
    from acf.gui.dashboard.acf_workstation_complexity import ACFComplexityExplorerPanel
except ImportError:
    pass

try:
    from acf.gui.dashboard.acf_workstation_confidence import ACFConfidenceLabPanel
except ImportError:
    pass

try:
    from acf.gui.dashboard.acf_workstation_multimodel import ACFMultiModelLabPanel
except ImportError:
    pass

try:
    from acf.gui.dashboard.acf_workstation_overview import ACFOverviewPanel
except ImportError:
    pass

try:
    from acf.gui.dashboard.acf_workstation_sounding_panel import ACFVerticalSoundingWidget
except ImportError:
    pass

try:
    from acf.gui.dashboard.acf_workstation_temporal import ACFTemporalLabPanel
except ImportError:
    pass

try:
    from acf.gui.dashboard.acf_workstation_thermodynamics import ACFThermodynamicsLabPanel
except ImportError:
    pass
from acf.gui.theme_tokens import dashboard_stylesheet, label_style

logger = logging.getLogger("acf.gui.dashboard.acf_workstation")

_DEFAULT_MODEL = "ARPEGE"  # smallest of the 3 real MODEL_CONFIGS grids - fastest real run, same default as acf_general_dashboard.py

#: Real Science Labs tabs (rebuild, 2026-09-13): every recovered real
#: Lab panel that the new reference image has no dedicated cell for
#: stays reachable here - nothing real is deleted or hidden ("ne
#: détruis pas l'existant", this project's own established rule).
_SCIENCE_TAB_ORDER = [
    "Atmosphere State",
    "Thermodynamics Lab",
    "Complexity Explorer",
    "Forecast Consistency Lab",
]

#: Real, DISCLOSED normalization references turning three real,
#: dimensional ACF quantities into the 0-1 factor scale the reference
#: image's own Complexity Overview breakdown uses. These are plain,
#: documented reference magnitudes (clipped to [0, 1]), not a fitted or
#: learned model, and not a claim that the underlying quantity "is"
#: that value - the real dimensional values themselves remain visible
#: in their own panels (Complexity Explorer's maps, Confidence Lab's
#: spread field):
#: - gradients: 10 K/100km is a real, textbook synoptic frontal-zone
#:   temperature-gradient magnitude;
#: - temporal evolution: 5 K/h is a real, strong local temperature
#:   tendency (a genuinely fast-evolving situation);
#: - model disagreement: 5 K of real ensemble spread is a large
#:   multi-model temperature disagreement.
#: A factor with no real value behind it is reported as None (the
#: Complexity Overview panel renders NOT_COMPUTED and excludes it from
#: its disclosed mean) - never filled in with a fabricated number.
_GRADIENT_REFERENCE_K_PER_100KM = 10.0
_TEMPORAL_REFERENCE_K_PER_H = 5.0
_DISAGREEMENT_REFERENCE_K = 5.0
# Real, disclosed CAPE reference used for the Instability/Convection
# factors below (added 2026-09-13): 3000 J/kg is a standard "extreme
# instability" bound in operational convective-outlook practice (SPC
# mesoanalysis CAPE color scales top out in this range) - CAPE >= this
# value maps to the top of the panel's 0-1 scale, consistent with how
# Gradients/Temporal Evolution/Model Disagreement are already normalized
# against a disclosed reference magnitude in this same method.
_CAPE_REFERENCE_J_KG = 3000.0
# Real, disclosed effective-bulk-shear reference used for the Shear
# factor: 20 m/s is the SPC Supercell Composite Parameter's own "capped
# at 1.0" bulk-shear threshold (see acf.science.severe_weather.
# SevereWeather.supercell_composite_parameter's EBWD_term) - reused here
# rather than inventing a separate bound.
_SHEAR_REFERENCE_M_S = 20.0

#: Real mapping from a sidebar SECTION to the real content anchor this
#: composer scrolls to (see `_on_section_selected()`). Values are
#: attribute names resolved at call time, so this table can never
#: reference a widget that does not exist.
_SECTION_ANCHORS = {
    "Home": "config_bar",
    "Data": "config_bar",
    "Science": "science_tabs",
    "Analysis": "analysis_row_widget",
    "Reports": "footer_panel",
    "Infrastructure": "footer_panel",
    "Settings": "config_bar",
}


def _clip_unit(value: float) -> float:
    """Clip a real, already-normalized factor into the [0, 1] scale the
    reference image's own Complexity Overview breakdown uses - a real
    value above the disclosed reference magnitude reads as a full 1.0,
    never as an out-of-scale number."""
    return max(0.0, min(1.0, value))


class _VolumeWorkerSignals(QObject):
    finished = Signal(dict)
    failed = Signal(str)


class _VolumeWorker(QRunnable):
    """Runs compute_real_complexity_volume() off the GUI thread - same
    real QRunnable/QThreadPool pattern used throughout this codebase's
    other dashboards."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.kwargs = kwargs
        self.signals = _VolumeWorkerSignals()

    def run(self) -> None:
        try:
            result = compute_real_complexity_volume(**self.kwargs)
        except Exception as exc:  # noqa: BLE001 - real failure, reported honestly via signal below
            logger.exception("ACF Scientific Workstation: volume computation failed")
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)


class _IndicesWorker(QRunnable):
    """Runs compute_real_convection_indices_field() off the GUI thread
    (rebuild, 2026-09-13) - the real MetPy parcel-ascent pipeline
    behind CAPE/CIN/LCL/bulk shear, measured ~3.2s on ARPEGE's own real
    grid, run ONCE per real volume and shared by the Key Atmospheric
    Variables and Key Alerts & Hazards panels. Same real QRunnable/
    QThreadPool pattern as _VolumeWorker above."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.kwargs = kwargs
        self.signals = _VolumeWorkerSignals()

    def run(self) -> None:
        try:
            result = compute_real_convection_indices_field(**self.kwargs)
        except Exception as exc:  # noqa: BLE001 - real failure, reported honestly via signal below
            logger.exception("ACF Scientific Workstation: convection indices computation failed")
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)


class ACFWorkstation(QWidget):
    """The real ACF Scientific Workstation - see module docstring."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._volume: dict[str, Any] | None = None
        self._level_index = 0
        self._compute_started_at: float | None = None
        #: A real level_index restored from a loaded configuration
        #: (added 2026-09-04) before any real volume exists yet to
        #: clamp it against - applied in _on_volume_ready() once a
        #: real volume's own real level count is known.
        self._pending_level_index: int | None = None
        #: Real step count of the most recently started run - set in
        #: refresh(), read back in _on_volume_ready() for the real
        #: "Modules" pipeline-stage detail text.
        self._last_steps: int = 0
        #: Real (lat, lon) last clicked on any of this Workstation's
        #: own maps (added Phase 33, 2026-09-05) - drives the
        #: always-visible Vertical Complexity Sounding panel; None
        #: until a real click happens, in which case _on_volume_ready()
        #: falls back to the real volume's own grid-center point.
        self._last_clicked_point: tuple[float, float] | None = None
        #: The real compute_real_convection_indices_field() result for
        #: the CURRENT volume (rebuild, 2026-09-13), computed once
        #: off-thread per real run and shared by the Key Atmospheric
        #: Variables and Key Alerts & Hazards panels - None until that
        #: real computation finishes (those panels honestly keep their
        #: own "not available" state until then, never a placeholder
        #: number).
        self._indices: dict[str, Any] | None = None
        #: Real HPCConnectionManager, constructed lazily on the first
        #: real footer update - never at import/construction time, and
        #: never connected by this Workstation itself (it only READS
        #: whatever real status the manager honestly reports).
        self._hpc: Any | None = None
        self._build_ui()
        self._setup_shortcuts()
        self.setStyleSheet(dashboard_stylesheet())
        # Honest, disclosed choice, same convention as AWCIDashboard/
        # ACFGeneralDashboard's own constructors: no real background
        # computation starts merely from constructing this widget - the
        # panels open in their real "Not yet computed" state until the
        # user (or the hosting window, on open) triggers "🔄 Run".

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        """Real layout of `acf_workstation_reference.jpg` (rebuild,
        2026-09-13) - see the module docstring's own REBUILD section for
        the full, disclosed component mapping (including the two
        deliberate, documented non-builds: the hero 2D/3D/4D + Layers
        controls, and the Vertical Cross Section cell)."""
        outer = QVBoxLayout(self)
        outer.setSpacing(8)
        outer.setContentsMargins(10, 10, 10, 0)

        # --- Top bar -----------------------------------------------------
        top_bar = QHBoxLayout()
        header = QLabel("ACF SCIENTIFIC WORKSTATION")
        header.setStyleSheet(label_style("text_primary", "lg", "bold"))
        top_bar.addWidget(header)

        # Real engine status - this Workstation's own solver pipeline is
        # in-process, so "ONLINE" here means exactly that the real
        # compute_real_complexity_volume() entry point is importable and
        # callable in this process (it was imported at module load), not
        # a claim about any remote service.
        self.engine_status_label = QLabel("ACF Engine ONLINE (in-process CoupledEarthSolver)")
        self.engine_status_label.setStyleSheet(label_style("text_secondary", "xs"))
        top_bar.addWidget(self.engine_status_label)
        top_bar.addStretch()

        # Real UTC clock (reference image's own top-bar date/time) -
        # the machine's real UTC time, ticking, never a frozen or
        # fabricated forecast timestamp.
        self.utc_clock_label = QLabel("")
        self.utc_clock_label.setStyleSheet(label_style("text_secondary", "xs"))
        top_bar.addWidget(self.utc_clock_label)
        self._clock_timer = QTimer(self)
        self._clock_timer.setInterval(1000)
        self._clock_timer.timeout.connect(self._update_utc_clock)
        self._clock_timer.start()
        self._update_utc_clock()

        top_bar.addWidget(self._label("Model:"))
        self.model_selector = QComboBox()
        self.model_selector.addItems(list(MODEL_CONFIGS.keys()))
        self.model_selector.setCurrentText(_DEFAULT_MODEL)
        top_bar.addWidget(self.model_selector)

        self.run_button = QPushButton("🔄 Run")
        self.run_button.setToolTip(
            "Real, off-thread compute_real_complexity_volume() run (CoupledEarthSolver,\n"
            "the selected model's own real grid configuration) - drives every real\n"
            "panel below from one real trajectory, re-sliced, never recomputed per panel."
        )
        self.run_button.clicked.connect(self.refresh)
        top_bar.addWidget(self.run_button)

        self.science_explorer_button = QPushButton("🔬 Science Explorer")
        self.science_explorer_button.setToolTip(
            "Real, live search over acf.science.encyclopedia.registry.\n"
            "EncyclopediaRegistry's own real, populated formula database."
        )
        self.science_explorer_button.clicked.connect(self._show_scientific_explorer_dialog)
        top_bar.addWidget(self.science_explorer_button)

        self.fullscreen_button = QPushButton("⛶")
        self.fullscreen_button.setToolTip("Toggle fullscreen")
        self.fullscreen_button.setFixedWidth(28)
        self.fullscreen_button.clicked.connect(self._toggle_fullscreen)
        top_bar.addWidget(self.fullscreen_button)

        # Real Configuration Management (added 2026-09-04) - same "real
        # actions behind one control" convention as the export menu
        # (awci_map_panel.py).
        self.settings_button = QToolButton()
        self.settings_button.setText("⚙")
        self.settings_button.setFixedWidth(28)
        self.settings_button.setToolTip("Configuration")
        self.settings_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        settings_menu = QMenu(self.settings_button)
        self.save_configuration_action = QAction("💾 Save Configuration…", self)
        self.save_configuration_action.triggered.connect(self._save_configuration)
        settings_menu.addAction(self.save_configuration_action)
        self.load_configuration_action = QAction("📂 Load Configuration…", self)
        self.load_configuration_action.triggered.connect(self._load_configuration)
        settings_menu.addAction(self.load_configuration_action)
        self.settings_button.setMenu(settings_menu)
        top_bar.addWidget(self.settings_button)
        outer.addLayout(top_bar)

        # --- Body: sidebar + scrollable real content column ---------------
        body = QHBoxLayout()
        body.setSpacing(8)

        self.sidebar = WorkstationSidebar()
        self.sidebar.setMaximumWidth(200)
        self.sidebar.sectionSelected.connect(self._on_section_selected)
        body.addWidget(self.sidebar)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)

        # --- Current Configuration bar -------------------------------------
        self.config_bar = ConfigBar()
        # The "Change" button is a real affordance for the real control
        # that changes the configuration - this Workstation's own model
        # selector - never a second, separate configuration path that
        # could drift out of sync with it.
        self.config_bar.changeRequested.connect(self._on_config_change_requested)
        content_layout.addWidget(self.config_bar)

        # --- Status + level row --------------------------------------------
        status_row = QHBoxLayout()
        self.status_label = QLabel("Not yet computed.")
        self.status_label.setStyleSheet(label_style("text_muted", "sm"))
        status_row.addWidget(self.status_label, stretch=1)

        status_row.addWidget(self._label("Level:"))
        self.level_slider = QSlider(Qt.Orientation.Horizontal)
        self.level_slider.setMinimum(0)
        self.level_slider.setMaximum(0)
        self.level_slider.setEnabled(False)
        self.level_slider.setFixedWidth(160)
        self.level_slider.valueChanged.connect(self._on_level_changed)
        status_row.addWidget(self.level_slider)
        self.level_label = QLabel("—")
        self.level_label.setStyleSheet(label_style("text_secondary", "xs"))
        status_row.addWidget(self.level_label)
        content_layout.addLayout(status_row)

        # --- Real panel objects --------------------------------------------
        # Every recovered Lab panel is constructed exactly as before -
        # their real backends are untouched; only WHERE their widgets
        # appear changed in this rebuild.
        self.overview_panel = ACFOverviewPanel()
        self.thermodynamics_panel = ACFThermodynamicsLabPanel()
        self.temporal_panel = ACFTemporalLabPanel()
        self.confidence_panel = ACFConfidenceLabPanel()
        self.multimodel_panel = ACFMultiModelLabPanel()
        self.complexity_panel = ACFComplexityExplorerPanel()
        self.sounding_panel = ACFVerticalSoundingWidget()

        self.key_variables_panel = KeyVariablesPanel()
        self.complexity_overview_panel = ComplexityOverviewPanel()
        self.model_agreement_panel = ModelAgreementPanel()
        self.hazard_alerts_panel = HazardAlertsPanel()
        self.footer_panel = SystemFooterPanel()

        self._lab_panels: dict[str, QWidget] = {
            "Atmosphere State": self.overview_panel,
            "Thermodynamics Lab": self.thermodynamics_panel,
            "Complexity Explorer": self.complexity_panel,
            "Forecast Consistency Lab": self.confidence_panel,
            "Temporal Evolution Lab": self.temporal_panel,
            "Multi-Model Lab": self.multimodel_panel,
        }

        # --- Hero: Atmospheric Complexity -----------------------------------
        # Reuses Complexity Explorer's OWN real spatial-complexity map
        # widget (re-parented, not duplicated: the same object its own
        # update_from_volume() keeps drawing into) and Temporal
        # Evolution Lab's OWN real transport controls.
        self.hero_widget = self._section_box("Atmospheric Complexity")
        hero_layout = self.hero_widget.layout()
        self.complexity_panel.spatial_map.setMinimumHeight(280)
        hero_layout.addWidget(self.complexity_panel.spatial_map, stretch=1)
        # Re-parenting spatial_map orphans its own "SPATIAL COMPLEXITY —"
        # header inside Complexity Explorer's own layout (still shown as a
        # full tab under Science Labs) - hide that specific child widget
        # rather than deleting it, so the panel's own standalone tests and
        # behaviour are untouched if it is ever used outside this composer.
        self.complexity_panel.spatial_header.setVisible(False)

        transport_row = QHBoxLayout()
        transport_row.addWidget(self.temporal_panel.run_button)
        transport_row.addWidget(self._label("Forecast frame:"))
        transport_row.addWidget(self.temporal_panel.frame_slider)
        transport_row.addWidget(self.temporal_panel.frame_label)
        transport_row.addStretch()
        # Same treatment for Temporal Evolution Lab's own orphaned "Frame:"
        # label, left behind in its own frame_row after frame_slider/
        # frame_label were re-parented above.
        self.temporal_panel.frame_row_label.setVisible(False)
        transport_note = QLabel(
            "Transport scrubs the real multi-frame trajectory rendered in “Time Evolution” below "
            "— the hero map shows this level's real spatial complexity and is not animated by it."
        )
        transport_note.setStyleSheet(label_style("text_muted", "xs"))
        transport_note.setWordWrap(True)
        hero_layout.addLayout(transport_row)
        hero_layout.addWidget(transport_note)
        content_layout.addWidget(self.hero_widget)

        # --- Row 1: key variables / complexity overview / agreement / hazards
        self.summary_row_widget = QWidget()
        summary_row = QHBoxLayout(self.summary_row_widget)
        summary_row.setContentsMargins(0, 0, 0, 0)
        summary_row.addWidget(self._wrap_in_box("Key Atmospheric Variables", self.key_variables_panel), stretch=1)
        summary_row.addWidget(self._wrap_in_box("Complexity Overview", self.complexity_overview_panel), stretch=1)
        summary_row.addWidget(self._wrap_in_box("Model Agreement", self.model_agreement_panel), stretch=1)
        summary_row.addWidget(self._wrap_in_box("Key Alerts & Hazards", self.hazard_alerts_panel), stretch=1)
        content_layout.addWidget(self.summary_row_widget)

        # --- Row 2: cross section / profiles / model comparison / time evolution
        self.analysis_row_widget = QWidget()
        analysis_row = QHBoxLayout(self.analysis_row_widget)
        analysis_row.setContentsMargins(0, 0, 0, 0)

        # Honest non-build, disclosed in place rather than silently
        # omitted: this rebuild's recovered panel set contains no real
        # cross-section widget (checked directly in
        # acf_workstation_complexity.py, which the task brief expected
        # to carry one - it builds 2 AWCIMapPanel maps and a spread
        # chart, no cross-section). Nothing is drawn here rather than a
        # plausible-looking fake section.
        self.cross_section_placeholder = QLabel(
            "NOT_AVAILABLE_NO_CROSS_SECTION_WIDGET_RECOVERED\n\n"
            "No real vertical cross-section widget exists in this rebuild's recovered "
            "panel set, so nothing is drawn here. The real per-point vertical structure "
            "that IS available is shown in “Atmospheric Profiles” beside this cell."
        )
        self.cross_section_placeholder.setWordWrap(True)
        self.cross_section_placeholder.setStyleSheet(label_style("text_muted", "xs"))
        analysis_row.addWidget(self._wrap_in_box("Vertical Cross Section", self.cross_section_placeholder), stretch=1)

        self.sounding_panel.setMinimumWidth(260)
        analysis_row.addWidget(self._wrap_in_box("Atmospheric Profiles", self.sounding_panel), stretch=1)
        analysis_row.addWidget(self._wrap_in_box("Model Comparison", self.multimodel_panel), stretch=1)
        analysis_row.addWidget(self._wrap_in_box("Time Evolution", self.temporal_panel), stretch=1)
        content_layout.addWidget(self.analysis_row_widget)

        # --- Science Labs tabs ------------------------------------------------
        self.science_tabs = QTabWidget()
        for name in _SCIENCE_TAB_ORDER:
            self.science_tabs.addTab(self._lab_panels[name], name)
        content_layout.addWidget(self._wrap_in_box("Science Labs", self.science_tabs))

        # --- Footer ------------------------------------------------------------
        content_layout.addWidget(self._wrap_in_box("System", self.footer_panel))
        content_layout.addStretch()

        # Same real responsive-sizing discipline as before the rebuild
        # (see panel_manager.py's own AWCIDashboardPanel scroll wrap):
        # a panel that does not fit the space actually given scrolls,
        # instead of forcing the whole window to grow permanently.
        self.content_scroll = QScrollArea()
        self.content_scroll.setWidgetResizable(True)
        self.content_scroll.setWidget(content)
        body.addWidget(self.content_scroll, stretch=1)

        # Every real Lab panel with its own map (discovered via hasattr,
        # not a hardcoded list) drives the SAME real sounding panel -
        # unchanged from Phase 33.
        for panel in self._lab_panels.values():
            map_panel = getattr(panel, "map_panel", None)
            if map_panel is not None:
                map_panel.pointClicked.connect(self._on_map_point_clicked)
        self.complexity_panel.spatial_map.pointClicked.connect(self._on_map_point_clicked)

        # Real cross-panel synchronization: whichever panel actually
        # computes a real result pushes it to every summary panel that
        # depends on it, so no two panels can end up showing
        # contradictory states after the same real user action.
        self.confidence_panel.disagreementComputed.connect(self._on_disagreement_result)
        self.multimodel_panel.comparisonComputed.connect(self._on_disagreement_result)
        self.complexity_panel.resultsUpdated.connect(self._update_complexity_overview)

        outer.addLayout(body, stretch=1)

    def _section_box(self, title: str) -> QWidget:
        """Real titled container (a frame + heading + vertical layout) -
        the reference image's own panel chrome, nothing more."""
        box = QFrame()
        box.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(box)
        layout.setContentsMargins(8, 6, 8, 8)
        layout.setSpacing(6)
        heading = QLabel(title.upper())
        heading.setStyleSheet(label_style("text_secondary", "xs", "bold"))
        layout.addWidget(heading)
        return box

    def _wrap_in_box(self, title: str, widget: QWidget) -> QWidget:
        box = self._section_box(title)
        box.layout().addWidget(widget, stretch=1)
        return box

    def _update_utc_clock(self) -> None:
        self.utc_clock_label.setText(
            datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
        )

    def _setup_shortcuts(self) -> None:
        """Real keyboard shortcuts - faster real access to already-real
        actions, nothing new invented: Ctrl+R re-triggers the exact same
        real refresh() the "🔄 Run" button already does; F11 toggles the
        exact same real fullscreen the "⛶" button already does;
        Ctrl+1..Ctrl+7 select one of the sidebar's own real sections by
        its real position in `WorkstationSidebar.section_names()` -
        generated from that same list, so they can never drift out of
        sync with the nav they target."""
        self.shortcut_run = QShortcut(QKeySequence("Ctrl+R"), self)
        self.shortcut_run.activated.connect(self.refresh)

        self.shortcut_fullscreen = QShortcut(QKeySequence("F11"), self)
        self.shortcut_fullscreen.activated.connect(self._toggle_fullscreen)

        self.nav_shortcuts: list[QShortcut] = []
        for row, name in enumerate(self.sidebar.section_names()[:10]):
            key_digit = (row + 1) % 10  # row 0 -> "1", ..., row 9 -> "0"
            shortcut = QShortcut(QKeySequence(f"Ctrl+{key_digit}"), self)
            shortcut.activated.connect(lambda target=name: self.sidebar.select_section(target))
            self.nav_shortcuts.append(shortcut)


    # ------------------------------------------------- Configuration Management

    #: Real (config key -> the selector it reads/restores). One shared
    #: table for both export and import (added 2026-09-04) - single
    #: source of truth, so a new Lab's own selector only needs adding
    #: here once, never two separately-maintained lists that could
    #: silently drift apart.
    def _configuration_selectors(self) -> dict[str, QComboBox]:
        return {
            "overview_variable": self.overview_panel.variable_selector,
            "thermodynamics_variable": self.thermodynamics_panel.variable_selector,
            "temporal_variable": self.temporal_panel.variable_selector,
            "confidence_variable": self.confidence_panel.variable_selector,
            "multimodel_model_a": self.multimodel_panel.model_a_selector,
            "multimodel_model_b": self.multimodel_panel.model_b_selector,
            "multimodel_display": self.multimodel_panel.display_selector,
        }

    def _export_configuration(self) -> dict[str, Any]:
        """Real UI configuration snapshot - the real user-chosen
        SETTINGS this Workstation's own model/level/nav/selectors
        currently hold. Never the computed data itself: real data is
        always re-computed fresh from a real solver run on "🔄 Run",
        never saved/replayed as a stand-in for one (this project's own
        no-fake-functionality rule) - loading a configuration restores
        what to look at, not a snapshot pretending to already be a
        real result."""
        config: dict[str, Any] = {
            "model": self.model_selector.currentText(),
            "level_index": self._level_index,
            "sidebar_section": self.sidebar.current_section(),
        }
        for key, selector in self._configuration_selectors().items():
            config[key] = selector.currentText()
        return config

    def _apply_configuration(self, config: dict[str, Any]) -> None:
        """Real, defensive restore - `config` may be a real file a
        user hand-edited or copied between sessions, so every field is
        individually validated before use; an unknown/malformed field
        is simply skipped (QComboBox.setCurrentText() itself already
        no-ops on a value absent from a combo's own real items - no
        separate validation needed there), never raised as a fatal
        error over one bad field."""
        model = config.get("model")
        if isinstance(model, str) and model in MODEL_CONFIGS:
            self.model_selector.setCurrentText(model)

        for key, selector in self._configuration_selectors().items():
            value = config.get(key)
            if isinstance(value, str):
                selector.setCurrentText(value)

        section = config.get("sidebar_section")
        if isinstance(section, str):
            # select_section() itself ignores a name that is not a real
            # section (see its own docstring) - no separate validation.
            self.sidebar.select_section(section)

        level_index = config.get("level_index")
        if isinstance(level_index, int) and level_index >= 0:
            if self._volume is not None:
                clamped = max(0, min(level_index, self._volume["n_levels"] - 1))
                self.level_slider.setValue(clamped)
            else:
                self._pending_level_index = level_index

    def _save_configuration(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Workstation Configuration", "acf_workstation_config.json", "JSON File (*.json)"
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self._export_configuration(), handle, indent=2)
        self.status_label.setText(f"✅ Configuration saved to {path}.")

    def _load_configuration(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Workstation Configuration", "", "JSON File (*.json)"
        )
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as handle:
                config = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            self.status_label.setText(f"⚠ Could not load configuration: {exc}")
            return
        if not isinstance(config, dict):
            self.status_label.setText("⚠ Could not load configuration: file does not contain a JSON object.")
            return
        self._apply_configuration(config)
        self.status_label.setText(f"✅ Configuration loaded from {path}.")

    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(label_style("text_muted", "xs"))
        return lbl

    # --------------------------------------------------------------- volume

    def _set_status(self, text: str) -> None:
        """Real, single status sink."""
        self.status_label.setText(text)

    def refresh(self) -> None:
        """Real, off-thread compute_real_complexity_volume() run - see
        module docstring."""
        self.run_button.setEnabled(False)
        model = self.model_selector.currentText()
        # The previous run's real convection indices belong to the
        # PREVIOUS volume - dropped here rather than shown beside the
        # new run's fields, which would be two panels contradicting
        # each other about the same real atmosphere.
        self._indices = None
        self._set_status(f"⏳ Computing real ACF volume ({model} grid, CoupledEarthSolver)…")
        self.footer_panel.append_activity(
            f"[Ingestion] Real {model} grid configuration validated — starting a real "
            f"CoupledEarthSolver volume run."
        )
        self._update_footer()
        self._compute_started_at = time.monotonic()
        config = MODEL_CONFIGS[model]
        steps = 6
        self._last_steps = steps

        worker = _VolumeWorker(
            model=model, n_lat=config["n_lat"], n_lon=config["n_lon"], n_levels=config["n_levels"],
            steps=steps, dt_seconds=90.0, perturbation_scale=3.0, seed=1,
        )
        worker.signals.finished.connect(self._on_volume_ready)
        worker.signals.failed.connect(self._on_volume_failed)
        QThreadPool.globalInstance().start(worker)

    def _on_volume_ready(self, volume: dict[str, Any]) -> None:
        self.run_button.setEnabled(True)
        self._volume = volume
        elapsed = time.monotonic() - self._compute_started_at if self._compute_started_at else 0.0
        # Honest, real status - never a fabricated forecast run-ID/valid-time
        # (this is a live solver run, not an archived NWP product).
        self._set_status(
            f"✅ Live CoupledEarthSolver run ({volume['model']} grid, {volume['n_levels']} real levels) "
            f"— computed in {elapsed:.1f}s."
        )

        n_levels = volume["n_levels"]
        self.level_slider.setMaximum(max(0, n_levels - 1))
        self.level_slider.setEnabled(True)
        # A real, pending level_index restored from a loaded
        # configuration (added 2026-09-04 - see _apply_configuration())
        # takes priority over the default level 0, clamped to this
        # real volume's own real level count.
        initial_level = 0
        if self._pending_level_index is not None:
            initial_level = max(0, min(self._pending_level_index, n_levels - 1))
            self._pending_level_index = None
        self.level_slider.blockSignals(True)
        self.level_slider.setValue(initial_level)
        self.level_slider.blockSignals(False)
        self._level_index = initial_level
        self._update_level_label()

        self._render_all_panels()

        # Real Vertical Complexity Sounding update (added Phase 33,
        # 2026-09-05) - reuses the real last-clicked point if there is
        # one (persists across runs, still a valid real lookup into the
        # NEW volume - vertical_profile_at_point() is a fresh nearest-
        # neighbour lookup every call), otherwise the real grid center.
        lat, lon = self._last_clicked_point or (float(volume["lats"][len(volume["lats"]) // 2]), float(volume["lons"][len(volume["lons"]) // 2]))
        self.sounding_panel.update_from_volume_and_point(volume, lat, lon, level_index=self._level_index)

        # Real Current Configuration bar + footer, from this real run.
        self._update_config_bar(volume, elapsed)
        self._update_footer()
        self.footer_panel.append_activity(
            f"[Modules] Real {volume['model']} volume computed in {elapsed:.1f}s "
            f"({volume['n_levels']} real native levels, {self._last_steps} real solver steps)."
        )

        # One real convection-indices run per real volume, off-thread -
        # shared by Key Atmospheric Variables and Key Alerts & Hazards
        # (see the module docstring's own "Single real computation per
        # run" section).
        self.footer_panel.append_activity(
            "[Analysis] Real convection indices (MetPy parcel ascent: CAPE/CIN/LCL/bulk shear) "
            f"starting off-thread on every {CONVECTION_GRID_STRIDE}th real grid row/column."
        )
        indices_worker = _IndicesWorker(
            temperature_volume=volume["temperature_volume"],
            specific_humidity_volume=volume["specific_humidity_volume"],
            pressure_volume_hpa=volume["pressure_volume_hpa"],
            u_volume=volume["u_volume"],
            v_volume=volume["v_volume"],
            lats=volume["lats"],
            lons=volume["lons"],
        )
        indices_worker.signals.finished.connect(self._on_indices_ready)
        indices_worker.signals.failed.connect(self._on_indices_failed)
        QThreadPool.globalInstance().start(indices_worker)

    def _on_volume_failed(self, message: str) -> None:
        self.run_button.setEnabled(True)
        self._set_status(f"⚠ Real volume computation failed: {message}")
        self.footer_panel.append_activity(f"[Modules] ⚠ Real volume computation failed: {message}")
        logger.error("ACF Scientific Workstation: volume computation failed: %s", message)

    # ------------------------------------------- real convection indices

    def _on_indices_ready(self, indices: dict[str, Any]) -> None:
        """One real `compute_real_convection_indices_field()` result for
        the current volume - rendered into BOTH panels that need it, so
        they can never disagree about the same real atmosphere."""
        self._indices = indices
        self.footer_panel.append_activity("[Analysis] Real convection indices computed.")
        self._render_indices_panels()

    def _on_indices_failed(self, message: str) -> None:
        self._indices = None
        self.footer_panel.append_activity(f"[Analysis] ⚠ Real convection indices failed: {message}")
        logger.error("ACF Scientific Workstation: convection indices failed: %s", message)

    def _render_indices_panels(self) -> None:
        """Real Key Atmospheric Variables + Key Alerts & Hazards render.

        Both read the SAME single real indices result (never a second
        MetPy parcel-ascent run), and the hazards panel reuses exactly
        the real values Key Variables just displayed
        (`last_center_values`) rather than re-deriving any of them. Wet
        bulb - the one hazard input those indices genuinely do not
        contain - comes from a real, single-point
        `compute_real_hydrometeor_phase_at_point()` call (measured ~16
        microseconds) at the same real domain-center surface cell, the
        same real function the former Microphysics Lab used."""
        if self._volume is None or self._indices is None:
            return
        volume = self._volume
        self.key_variables_panel.update_from_volume(volume, self._level_index, indices=self._indices)

        values = self.key_variables_panel.last_center_values
        if values is None:
            return

        from acf.awci.hydrometeor_phase import compute_real_hydrometeor_phase_at_point

        ci, cj = len(volume["lats"]) // 2, len(volume["lons"]) // 2
        phase = compute_real_hydrometeor_phase_at_point(
            float(volume["temperature_volume"][0, ci, cj]),
            float(volume["specific_humidity_volume"][0, ci, cj]),
            float(volume["pressure_volume_hpa"][0, ci, cj]),
        )
        wet_bulb_c = float(phase["wet_bulb_c"]) if phase.get("is_real_data") else None

        self.hazard_alerts_panel.update_from_indices(
            values["cape_j_kg"],
            values["bulk_shear_m_s"],
            wet_bulb_c,
            values["relative_humidity_pct"],
        )

    # ------------------------------------------------- complexity overview

    def _update_complexity_overview(self) -> None:
        """Real Complexity Overview factors - see `_GRADIENT_REFERENCE_
        K_PER_100KM` & co. for the exact disclosed normalizations.

        Gradients and Temporal Evolution come from Complexity Explorer's
        own real, already-computed fields; Model Disagreement from
        Confidence Lab's (or Multi-Model Lab's) own real disagreement
        result; and Instability/Moisture/Shear/Convection (added
        2026-09-13) from the SAME real per-cell values Key Atmospheric
        Variables / Key Alerts & Hazards already display
        (`key_variables_panel.last_center_values`) - never a second
        computation. Only Vertical Structure has genuinely no real source
        in this composer and stays None - the panel renders NOT_COMPUTED
        and excludes it from its disclosed mean - rather than invented
        from an unrelated quantity."""
        factors: dict[str, float | None] = {
            "Instability": None,
            "Moisture": None,
            "Shear": None,
            "Convection": None,
            "Gradients": None,
            "Vertical Structure": None,
            "Temporal Evolution": None,
            "Model Disagreement": None,
        }

        # Instability/Moisture/Shear/Convection: the real center-cell
        # values Key Atmospheric Variables just displayed - same NaN
        # handling as the other factors below (a NaN/missing center-cell
        # value stays None, never fabricated as 0).
        center = self.key_variables_panel.last_center_values
        if center is not None:
            cape = center.get("cape_j_kg")
            if cape is not None and not np.isnan(cape):
                # Real, disclosed CAPE normalization (see
                # `_CAPE_REFERENCE_J_KG`'s own comment) - shared by
                # Instability and Convection below: this composer has
                # exactly one real convective-intensity source per cell
                # (CAPE), so both factors read the same normalized value
                # rather than Convection being left NOT_COMPUTED or a
                # fabricated second quantity being invented for it.
                factors["Instability"] = _clip_unit(float(cape) / _CAPE_REFERENCE_J_KG)
                factors["Convection"] = factors["Instability"]

            shear = center.get("bulk_shear_m_s")
            if shear is not None and not np.isnan(shear):
                factors["Shear"] = _clip_unit(float(shear) / _SHEAR_REFERENCE_M_S)

            rh_pct = center.get("relative_humidity_pct")
            if rh_pct is not None and not np.isnan(rh_pct):
                # Already a real 0-100 percentage - just /100, clamped.
                factors["Moisture"] = _clip_unit(float(rh_pct) / 100.0)

        spatial = self.complexity_panel.spatial_complexity_field
        if spatial is not None:
            # Real, deliberate choice of the MEDIAN here (not the mean):
            # this real gradient field has a genuine, physical-grid
            # singularity at the poles - dx = R*cos(lat)*dlon goes to 0
            # on a regular lat/lon grid, so the real per-metre gradient
            # blows up in the polar rows and a domain mean is dominated
            # by them (measured ~2.8e14 K/100km mean vs ~9.7 K/100km at
            # the 95th percentile on a real ARPEGE run). Complexity
            # Explorer's own map scales by a percentile for exactly this
            # real reason; the median is the same robustness, disclosed.
            factors["Gradients"] = _clip_unit(
                float(np.nanmedian(spatial)) / _GRADIENT_REFERENCE_K_PER_100KM
            )

        temporal = self.complexity_panel.temporal_complexity_field
        if temporal is not None:
            factors["Temporal Evolution"] = _clip_unit(
                float(np.nanmean(temporal)) / _TEMPORAL_REFERENCE_K_PER_H
            )

        disagreement = (
            self.confidence_panel.last_disagreement_result()
            or self.multimodel_panel.last_comparison_result()
        )
        if disagreement is not None:
            spread = disagreement["disagreement_spread_field"]
            factors["Model Disagreement"] = _clip_unit(
                float(np.nanmean(np.abs(spread))) / _DISAGREEMENT_REFERENCE_K
            )

        self.complexity_overview_panel.update_from_factors(factors)

    def _on_disagreement_result(self, result: dict[str, Any]) -> None:
        """Real multi-model result from whichever panel actually
        computed it (Confidence Lab or Multi-Model Lab) - the Model
        Agreement panel and the Complexity Overview's own Model
        Disagreement factor are both refreshed from that SAME real
        result, never from a second run of the engine."""
        self.model_agreement_panel.update_from_disagreement(
            result.get("per_model_field", {}), result.get("disagreement_spread_field")
        )
        self._update_complexity_overview()
        self.footer_panel.append_activity(
            "[Interactions] Real multi-model disagreement result applied to Model Agreement "
            f"({'/'.join(result.get('models_compared', []))})."
        )

    # --------------------------------------------------- config bar / footer

    def _update_config_bar(self, volume: dict[str, Any], elapsed_s: float) -> None:
        """Real Current Configuration bar, filled from the REAL run that
        just completed (never the model selector's pending value).

        Honest field-by-field disclosure: `cycle` and `forecast_hour`
        are not archived-NWP metadata - this Workstation runs a live
        `CoupledEarthSolver` integration, so they report exactly that
        (the real UTC time this run completed, and the real integrated
        lead time of `steps` x `dt_seconds`), never a fabricated
        operational cycle label."""
        model = volume["model"]
        config = MODEL_CONFIGS.get(model, {})
        lead_hours = self._last_steps * 90.0 / 3600.0
        self.config_bar.update_from_config(
            {
                "model": model,
                "cycle": datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%MZ (live solver run)"),
                "forecast_hour": f"T+{lead_hours:.2f}h (real integrated lead time)",
                "domain": "Global (solver native grid — no domain crop)",
                "resolution_km": config.get("resolution_km"),
                "grid": f"{len(volume['lats'])}×{len(volume['lons'])}",
                "vertical_levels": volume["n_levels"],
            }
        )

    def _update_footer(self) -> None:
        """Real HPC status in the footer's System Status/Running Jobs/
        Data Sources - a real `HPCConnectionManager`, which honestly
        reports "Not Connected" when no real cluster session exists
        (this Workstation never connects one itself)."""
        try:
            from acf.hpc_connector.connection_manager import HPCConnectionManager

            if self._hpc is None:
                self._hpc = HPCConnectionManager()
            self.footer_panel.update_from_hpc(self._hpc)
        except Exception as exc:  # noqa: BLE001 - real failure, disclosed, never a fake "connected" state
            logger.warning("ACF Scientific Workstation: real HPC status unavailable: %s", exc)
            self.footer_panel.append_activity(f"[Infrastructure] ⚠ Real HPC status unavailable: {exc}")

    def _on_config_change_requested(self) -> None:
        """The Current Configuration bar's real "Change" button - opens
        this Workstation's own real model selector rather than a second,
        parallel configuration path that could drift out of sync."""
        self.model_selector.setFocus()
        self.model_selector.showPopup()

    # --------------------------------------------------------- sidebar nav

    def _on_section_selected(self, section: str) -> None:
        """Real sidebar routing - scrolls the real content column to the
        real area that section corresponds to, and opens the two real
        dialogs the "Data" sub-entries genuinely have behind them. A
        sub-entry with no real, already-built correspondence says so
        honestly in the status line rather than silently doing nothing
        or pretending to navigate somewhere."""
        subsection = self.sidebar.current_subsection()

        if section == "Data" and subsection == "Models":
            self._show_model_data_dialog()
            return
        if section == "Data" and subsection == "Observations":
            self._show_observations_dialog()
            return

        if section == "Science" and subsection in self._lab_panels:
            self.science_tabs.setCurrentWidget(self._lab_panels[subsection])
        elif section == "Science" and subsection == "Complexity":
            self.science_tabs.setCurrentWidget(self.complexity_panel)
        elif section == "Science" and subsection == "Thermodynamics":
            self.science_tabs.setCurrentWidget(self.thermodynamics_panel)

        anchor_name = _SECTION_ANCHORS.get(section)
        anchor = getattr(self, anchor_name, None) if anchor_name else None
        if anchor is not None:
            self.content_scroll.ensureWidgetVisible(anchor)

        if section == "Analysis" and subsection in {"3D Volumes", "4D Space-Time"}:
            self._set_status(
                f"“{subsection}” has no real panel in this rebuild — no real 3D/4D view "
                "survives this session's cleanup, and none is fabricated here."
            )
        elif section == "Analysis" and subsection == "Cross Sections":
            self._set_status(
                "Vertical Cross Section is NOT_AVAILABLE_NO_CROSS_SECTION_WIDGET_RECOVERED "
                "— see that cell's own disclosure."
            )

    def _on_map_point_clicked(self, lat: float, lon: float) -> None:
        """Real, shared handler for every map panel's own real
        `pointClicked` signal (added Phase 33, 2026-09-05) - updates
        the always-visible Vertical Complexity Sounding from whichever
        real map the user actually clicked."""
        self._last_clicked_point = (lat, lon)
        if self._volume is not None:
            self.sounding_panel.update_from_volume_and_point(self._volume, lat, lon, level_index=self._level_index)

    def _on_level_changed(self, value: int) -> None:
        self._level_index = value
        self._update_level_label()
        self._render_all_panels()
        if self._volume is not None:
            if self._last_clicked_point is not None:
                lat, lon = self._last_clicked_point
                self.sounding_panel.update_from_volume_and_point(self._volume, lat, lon, level_index=self._level_index)

    def _update_level_label(self) -> None:
        if self._volume is None:
            self.level_label.setText("—")
            return
        mean_pressure = float(self._volume["pressure_volume_hpa"][self._level_index].mean())
        self.level_label.setText(f"~{mean_pressure:.0f} hPa (native level {self._level_index + 1}/{self._volume['n_levels']})")

    def _render_all_panels(self) -> dict[str, Any]:
        """Re-slice the ONE real volume into every real panel that
        depends on it - so a single real user action (a run, or a level
        change) can never leave two panels describing different states
        of the same real atmosphere."""
        if self._volume is None:
            return {}
        display_volume = self._volume
        self.overview_panel.update_from_volume(display_volume, self._level_index)
        self.thermodynamics_panel.update_from_volume(display_volume, self._level_index)
        self.temporal_panel.update_from_volume(display_volume, self._level_index)
        self.confidence_panel.update_from_volume(display_volume, self._level_index)
        self.multimodel_panel.update_from_volume(display_volume, self._level_index)
        # Complexity Explorer's own resultsUpdated signal refreshes the
        # Complexity Overview panel from this same real re-slice.
        self.complexity_panel.update_from_volume(display_volume, self._level_index)
        # Key Atmospheric Variables / Key Alerts & Hazards only once the
        # real convection indices for THIS volume exist (they are
        # computed once per real run, off-thread) - until then those
        # panels honestly keep their own "not available" state.
        self._render_indices_panels()
        return display_volume


    def _show_model_data_dialog(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Model Data — real MODEL_CONFIGS")
        layout = QVBoxLayout(dialog)
        table = QTableWidget(len(MODEL_CONFIGS), 5)
        table.setHorizontalHeaderLabels(["Model", "Grid (lat×lon×levels)", "Resolution (km)", "Default steps", "Notes"])
        for row, (model, config) in enumerate(MODEL_CONFIGS.items()):
            table.setItem(row, 0, QTableWidgetItem(model))
            table.setItem(
                row, 1, QTableWidgetItem(f"{config['n_lat']}×{config['n_lon']}×{config['n_levels']}")
            )
            table.setItem(row, 2, QTableWidgetItem(str(config["resolution_km"])))
            table.setItem(row, 3, QTableWidgetItem(str(config["default_steps"])))
            table.setItem(row, 4, QTableWidgetItem("Real CoupledEarthSolver grid — this Workstation's own live run."))
        table.resizeColumnsToContents()
        layout.addWidget(table)
        dialog.resize(560, 200)
        dialog.exec()

    def _show_observations_dialog(self) -> None:
        """
        NOTE (correction, 2026-09-06): this dialog used to unconditionally
        state "No real observation feed is connected to this Workstation" -
        true when written, but stale by the time of this correction: ESOC's
        Earth Monitoring panel (acf.gui.esoc.panel_manager.
        EarthMonitoringPanel, Phases 57-60, same session) wired 4 real
        observation feeds (GOES/MTG, ARGO ocean floats, NOAA METAR
        stations, NEXRAD radar status) that this Workstation-level dialog
        never learned about. Reuses those exact same connectors/workers
        (never a second, duplicated implementation) rather than continuing
        to assert a now-false blanket claim. The underlying physics fields
        elsewhere in this Workstation genuinely still come only from
        CoupledEarthSolver - that half of the original disclosure stands.

        UPDATED (Phase 64, same session): a 5th real feed joined
        EarthMonitoringPanel - acf.connectors.pirep_reports.PIREPConnector
        (real NOAA PIREP - pilot reports, not AMDAR, which has no free
        public feed ACF can reach). Updated here too, in the same commit
        that adds it, specifically to not repeat the staleness this NOTE
        itself documents.
        """
        from acf.connectors.argo_floats import ArgoFloatsConnector
        from acf.connectors.nexrad_stations import NEXRADRadarConnector
        from acf.connectors.pirep_reports import PIREPConnector
        from acf.gui.esoc.panel_manager import (
            _ArgoFetchWorker,
            _METARFetchWorker,
            _NexradFetchWorker,
            _PIREPFetchWorker,
        )
        from acf.gui.map.mtg_basemap import MTGBasemapProvider

        dialog = QDialog(self)
        dialog.setWindowTitle("Observations")
        layout = QVBoxLayout(dialog)
        note = QLabel(
            "5 real observation feeds below (same connectors as the ESOC Earth Monitoring panel; "
            "PIREP is pilot reports, not AMDAR, which has no free public feed ACF can reach) - the "
            "physics fields shown elsewhere in this Workstation still come only from a real, live "
            "CoupledEarthSolver run, never from these observation feeds."
        )
        note.setWordWrap(True)
        layout.addWidget(note)

        table = QTableWidget(5, 2)
        table.setHorizontalHeaderLabels(["Feed", "Status"])
        rows = [
            "GOES/MTG Satellites",
            "ARGO Ocean Floats",
            "Surface AWS (SYNOP/METAR)",
            "Doppler Radar (NEXRAD)",
            "Aircraft Reports (PIREP)",
        ]
        for row, name in enumerate(rows):
            table.setItem(row, 0, QTableWidgetItem(name))
            table.setItem(row, 1, QTableWidgetItem("Checking..."))
        table.resizeColumnsToContents()
        layout.addWidget(table)
        dialog.resize(520, 220)

        provider = MTGBasemapProvider.instance()
        table.setItem(0, 1, QTableWidgetItem("LIVE" if provider.is_live else provider.status))

        # NOTE: these 3 fetches run async (same QThreadPool workers as
        # EarthMonitoringPanel) and their `finished` signal is delivered
        # on a Qt queued connection - it can arrive after the user has
        # already closed this dialog. Each callback checks
        # shiboken6.isValid(table) first, same lifetime-safety discipline
        # as panel_manager.py's _on_argo_fetched/_on_metar_fetched/
        # _on_nexrad_fetched (see _make_mtg_update_forwarder's own NOTE
        # for the crash this guards against).
        def _on_argo(result: Any) -> None:
            if not shiboken6.isValid(table):
                return
            text = f"LIVE ({result.profile_count} profiles/48h)" if result.is_real_data else result.status
            table.setItem(1, 1, QTableWidgetItem(text))

        def _on_metar(reporting: int, total: int) -> None:
            if not shiboken6.isValid(table):
                return
            text = f"LIVE ({reporting}/{total} stations)" if reporting > 0 else "NOT_REACHABLE_0_STATIONS_REPORTING"
            table.setItem(2, 1, QTableWidgetItem(text))

        def _on_nexrad(result: Any) -> None:
            if not shiboken6.isValid(table):
                return
            text = (
                f"LIVE ({result.stations_operational}/{result.stations_total} sites)"
                if result.is_real_data
                else result.status
            )
            table.setItem(3, 1, QTableWidgetItem(text))

        def _on_pirep(result: Any) -> None:
            if not shiboken6.isValid(table):
                return
            text = f"LIVE ({result.report_count} reports)" if result.is_real_data else result.status
            table.setItem(4, 1, QTableWidgetItem(text))

        argo_worker = _ArgoFetchWorker(ArgoFloatsConnector())
        argo_worker.signals.finished.connect(_on_argo)
        QThreadPool.globalInstance().start(argo_worker)

        metar_worker = _METARFetchWorker()
        metar_worker.signals.finished.connect(_on_metar)
        QThreadPool.globalInstance().start(metar_worker)

        nexrad_worker = _NexradFetchWorker(NEXRADRadarConnector())
        nexrad_worker.signals.finished.connect(_on_nexrad)
        QThreadPool.globalInstance().start(nexrad_worker)

        pirep_worker = _PIREPFetchWorker(PIREPConnector())
        pirep_worker.signals.finished.connect(_on_pirep)
        QThreadPool.globalInstance().start(pirep_worker)

        dialog.exec()

    def _show_scientific_explorer_dialog(self) -> None:
        from acf.science.encyclopedia.registry import EncyclopediaRegistry

        registry = EncyclopediaRegistry
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Scientific Explorer — {registry.count()} real formula entries")
        layout = QVBoxLayout(dialog)
        search_box = QLineEdit()
        search_box.setPlaceholderText("Search the real EncyclopediaRegistry (name, domain, equation)…")
        layout.addWidget(search_box)
        results = QTextEdit()
        results.setReadOnly(True)
        layout.addWidget(results)

        def render(entries: list[Any]) -> None:
            if not entries:
                results.setPlainText("No matching real entries.")
                return
            blocks = []
            for entry in entries[:50]:
                blocks.append(
                    f"{entry.name} ({entry.domain}/{entry.subdomain})\n"
                    f"  {entry.equation}\n"
                    f"  {entry.description}\n"
                    f"  References: {', '.join(entry.references) if entry.references else 'n/a'}"
                )
            results.setPlainText("\n\n".join(blocks))

        def on_search(text: str) -> None:
            render(registry.search(text) if text.strip() else registry.list_entries())

        search_box.textChanged.connect(on_search)
        render(registry.list_entries())
        dialog.resize(640, 480)
        dialog.exec()

    def _toggle_fullscreen(self) -> None:
        window = self.window()
        if window.isFullScreen():
            window.showNormal()
        else:
            window.showFullScreen()

    def status(self) -> dict[str, Any]:
        return {"has_volume": self._volume is not None, "level_index": self._level_index}
