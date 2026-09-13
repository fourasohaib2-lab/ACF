# ACF Scientific Workstation — Rebuild Design (2026-09-13)

## Context

Earlier in this session, every ACF/AWCI dashboard (GUI packages, per-subsystem
`*Dashboard` classes, entry points, and their ESOC wiring) was deleted at the
user's explicit request. That sweep is still in progress on the non-GUI
subsystem side when this rebuild was requested (see git history around this
commit for the exact state of that unrelated cleanup).

The user then asked to rebuild the ACF Scientific Workstation **from scratch**,
using `acf_workstation_reference.jpg` (repo root) as the **sole authoritative**
visual reference — explicitly *not* `docs/reference/acf_scientific_workstation_reference.jpg`,
which the previous (now-deleted) implementation targeted. The two images are
confirmed different designs (different IA, different panel set) — this is not
a restoration, it is a new build against a new mockup, reusing real data
plumbing from the old implementation where it still applies.

AWCI's own dashboard is explicitly out of scope for this spec — it will get
its own separate design pass once this one ships.

## Reference

`acf_workstation_reference.jpg` (repo root). Key regions, top to bottom:

1. Top bar: ACF branding, "ACF Engine ONLINE" status, date/time (UTC), bell,
   settings, user profile.
2. Left sidebar: Home · Data (Datasets/Models/Observations) · Science
   (Thermodynamics/Humidity/Stability/Convection/Wind & Shear/Gradients/
   Vertical Structure/Complexity) · Analysis (2D Maps/3D Volumes/4D
   Space-Time/Profiles/Cross Sections/Model Comparison) · Reports ·
   Infrastructure (HPC/Slurm/Jobs/Storage) · Settings.
3. Current Configuration bar: Model, Cycle, Forecast hour, Domain,
   Resolution, Grid, Vertical Levels, "Change" button.
4. Hero map: "Atmospheric Complexity" with 2D/3D/4D toggle, 0–1 colorscale,
   playback transport + forecast-hour slider (T0..+48h), "Layers" button.
5. Key Atmospheric Variables: Temperature (850 hPa), Relative Humidity
   (700 hPa), Wind Speed (850 hPa), CAPE, CIN, LCL — each a labeled bar gauge.
6. Complexity Overview: circular gauge (e.g. "0.73 High") plus a breakdown
   list of 8 factors (Instability, Moisture, Shear, Convection, Gradients,
   Vertical Structure, Temporal Evolution, Model Disagreement).
7. Model Agreement: one bar per model (AROME/ALADIN/ARPEGE/WRF) plus an
   overall verdict string (e.g. "Low Agreement").
8. Key Alerts & Hazards: Convection/Turbulence/Low Visibility/Icing, each
   with a High/Medium/Low badge.
9. Second row: Vertical Cross Section, Atmospheric Profiles (skew-T style),
   Model Comparison (2×2 grid of small per-model maps), Time Evolution
   (per-model complexity-index line chart over the forecast range).
10. Footer row: Data Sources (per-model + Observations status), System
    Status (engine/HPC/DB/API), Running Jobs (gauge + breakdown by stage),
    Recent Activity (log).
11. Bottom-right: Earth image + tagline (decorative, no real data).

## Decisions made during brainstorming

- **Scope**: ACF Workstation only. AWCI dashboard is a separate future spec.
- **Data**: real, existing repo sources (AROME/ALADIN/RESTOR/`acf.awci`/
  `acf.hpc_connector`/etc.) — same honesty convention as the rest of the
  codebase: a value that cannot be genuinely computed reports an explicit
  `NOT_*_NO_*_CONNECTED`-style status, never a fabricated number.
- **Stack**: PySide6/Qt desktop, consistent with the rest of `acf.gui`
  (matplotlib/Cartopy embedded via `FigureCanvasQTAgg`), integrated into ESOC
  the same way the previous Workstation was.
- **Code reuse**: start from the previous implementation's real data-plumbing
  (recoverable from git history prior to this session's deletion) — the
  physics/statistics computations, not the previous panel layout, which
  targeted the other (now superseded) reference image.
- **Complexity Overview gauge**: the previous Workstation deliberately never
  combined complexity dimensions into one score (project rule: no
  arbitrarily-fabricated composite). This rebuild **does** show a single
  gauge, per the new reference image, but it must be a real, disclosed
  average of the real per-dimension values shown right below it — documented
  in the panel's own module docstring as exactly that (a mean), never
  presented as an independently-computed "AI score".
- **Key Alerts & Hazards**: the previous Workstation was explicitly
  "ACF CORE ONLY — NO AWCI" (no hazard/risk classification). This rebuild
  **includes** the panel, built from real, simple, documented thresholds over
  fields already computed elsewhere in the Workstation (e.g. CAPE → Convection
  potential, bulk shear → Turbulence potential) — disclosed in-code as
  heuristics, not an imported AWCI classification engine.
- **Architecture**: same as before — a standalone `QMainWindow`
  (`ACFWorkstationWindow`) hosting a composite widget (`ACFWorkstation`),
  reopened/raised from an ESOC toolbar button ("🔬 ACF Scientific
  Workstation"), not a tab embedded directly in ESOC.

## Component mapping

| Reference section | New panel (module, indicative) | Real data source |
|---|---|---|
| Current Configuration bar | `acf_workstation_config_bar.py` → `ConfigBar` | Active run metadata (model/cycle/domain/resolution/grid/levels) from `acf.hpc_connector`/RESTOR/`acf.awci` |
| Hero complexity map (2D/3D/4D, playback, layers) | `acf_workstation_map.py` → `ComplexityMapPanel` (built on the existing `AWCIMapPanel` machinery: zoom/pan/export, layer toggles) | `acf.awci.spatial_field.compute_real_complexity_field` / `acf.awci.vertical_field.compute_real_complexity_evolution` (`CoupledEarthSolver`) |
| Key Atmospheric Variables | `acf_workstation_key_variables.py` → `KeyVariablesPanel` | Overview panel's real T/wind/humidity/pressure + Thermodynamics Lab's real θ-e/RH/CAPE/CIN (MetPy parcel ascent); **LCL is new** — real MetPy `mpcalc.lcl()` over the same sounding, not previously exposed |
| Complexity Overview (gauge + 8 factors) | `acf_workstation_complexity_overview.py` → `ComplexityOverviewPanel` | Real per-dimension values from Complexity Explorer (spatial/temporal) + Confidence Lab (model disagreement); gauge = disclosed mean of those factors |
| Model Agreement | `acf_workstation_model_agreement.py` → `ModelAgreementPanel` | `ModelConsensusEngine.compute_real_multi_model_disagreement_field()`, converted to a per-model agreement score (e.g. `1 - normalized deviation from ensemble mean`) |
| Key Alerts & Hazards | `acf_workstation_hazard_alerts.py` → `HazardAlertsPanel` (new) | Real, documented thresholds over CAPE (convection), bulk shear (turbulence), RH/ceiling proxy (visibility), wet-bulb/precip-phase (icing) — all already computed by other panels, reused not recomputed |
| Vertical Cross Section | `acf_workstation_cross_section.py` → `CrossSectionPanel` | `acf.awci.path_sampling`/cross-section real machinery (as before) |
| Atmospheric Profiles (skew-T) | `acf_workstation_sounding_panel.py` → `SoundingPanel` (largely reused from the old `acf_workstation_sounding_panel.py`) | Same real sounding data as Thermodynamics Lab |
| Model Comparison (2×2 mini-maps) | `acf_workstation_model_comparison.py` → `ModelComparisonPanel` | Multi-Model Lab's real `per_model_field` |
| Time Evolution (per-model complexity curves) | `acf_workstation_time_evolution.py` → `TimeEvolutionPanel` | Temporal Evolution Lab's real multi-frame `CoupledEarthSolver` trajectory, split per model |
| Data Sources / System Status / Running Jobs / Recent Activity | `acf_workstation_footer.py` → `SystemFooterPanel` | `acf.hpc_connector` real status + the existing real ACF Pipeline Monitor log |
| Left sidebar navigation | `acf_workstation_sidebar.py` → `WorkstationSidebar` | Static navigation tree (Home/Data/Science/Analysis/Reports/Infrastructure/Settings) driving which panels are visible/focused |

**Explicitly out of scope for this pass** (present in the old, now-superseded
mockup/code, absent from the new reference image — dropped per YAGNI, not
forgotten): Map Inspector popup, Atmospheric Interaction Graph/Interaction
Engine, Command Palette, thumbnail-strip timeline, Research Mode, Case Study
mode, Data Quality Center, Terrain Lab, Domain panel. These can get their own
follow-up spec if the user wants them back.

## Data flow & honesty conventions

- Every panel stays inert at construction time (no computation in `__init__`)
  — `ACFWorkstation.refresh()` (called once by `ACFWorkstationWindow` on
  open, same as before) triggers the real computations, off the GUI thread
  where the existing pattern already does that (`QRunnable` + signals, as
  used by `_AWCIFieldWorker`/temporal/confidence panels previously).
- Any value that cannot be genuinely computed (missing model, no real
  connection, insufficient data) renders an explicit
  `NOT_<X>_NO_<REASON>_CONNECTED`-style status in the widget, never a
  plausible-looking fabricated number — same discipline as the rest of the
  codebase (see e.g. `acf.hazard_operations.hazard_dashboard`'s own history
  before this session's cleanup, or `acf.release.release_manager`).
- The Complexity Overview gauge's docstring states plainly that it is the
  mean of the factors listed below it, computed from real per-dimension
  values — not an independently-modeled composite score.
- The Hazard Alerts panel's module docstring documents its exact threshold
  rules and states they are simple, disclosed heuristics over already-real
  fields, not an AWCI-derived classification.

## Testing

- One test module per panel, adapted from the deleted
  `tests/gui/test_acf_workstation_*.py` / `tests/test_acf_workstation_*.py`
  where a direct analog exists (Overview, Dynamics-derived variables,
  Thermodynamics, Complexity, Confidence, Multi-Model, Temporal, Sounding,
  Cross Section) — updated to the new panel names/layout above.
- New tests for the genuinely new panels: `ComplexityOverviewPanel` (gauge
  value equals the disclosed mean; missing-data path reports the honest
  status), `HazardAlertsPanel` (each threshold rule, plus the missing-data
  path), `ModelAgreementPanel`, `ConfigBar`, `SystemFooterPanel`.
- One integration test (`tests/test_esoc_acf_workstation_action.py`
  equivalent) verifying the ESOC toolbar action opens/raises
  `ACFWorkstationWindow`.
- Full run via the project's dev venv (`.venv`, `pytest-qt`,
  `QT_QPA_PLATFORM=offscreen`) before calling this done.

## Open items for the implementation plan (not this spec)

- Exact new-vs-reused split file-by-file (this spec gives indicative module
  names; the plan should confirm against what's actually recoverable from
  git history).
- LCL computation placement (new, small — likely lives next to the existing
  Thermodynamics Lab sounding code rather than as a whole new module).
- Icon/visual polish pass (colors, spacing) to match the reference image's
  look, once the panels are functionally wired.
