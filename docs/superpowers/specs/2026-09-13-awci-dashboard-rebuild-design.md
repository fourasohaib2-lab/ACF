# AWCI Dashboard Rebuild — Design (2026-09-13)

## Context

Every ACF/AWCI dashboard (including the original `AWCIDashboard`,
`src/acf/gui/dashboard/awci_dashboard.py`, ~2800 lines) was deleted earlier
this session at the user's explicit request. The underlying real AWCI
science (`src/acf/awci/*.py` — the calculator, wind shear, hydrometeor
phase, path sampling, multi-model fusion, temporal/vertical fields, real
ALADIN archive access, etc.) was **not** deleted — only the GUI layer was.
The ACF Scientific Workstation was then rebuilt (separately, already
shipped) against a *different* reference image than the one that drove the
old AWCI dashboard.

The user has now shared a **new** AWCI reference image (saved locally,
referenced throughout this spec as "the reference image") and wants the
AWCI dashboard rebuilt against it, following the exact same process used
for the ACF Workstation rebuild: recover the old dashboard's real logic
from git history (`git show 022e704^:src/acf/gui/dashboard/awci_dashboard.py`
and its sibling files, e.g. `awci_map_panel.py`, `awci_synthetic_field.py`),
re-lay it out to match the new reference image exactly (same placement,
same content, same functional depth), and ship it as a window reachable
from the ACF Scientific Workstation (the app's current default cockpit —
ESOC is no longer the entry point).

## Reference

The image shows, top to bottom / left to right:

1. **Top bar**: AWCI logo/wordmark ("Aviation Weather Complexity Index",
   "From ACF data · For safer skies"), "SYSTEM ONLINE / ACF Data: Connected"
   status, "Last Update" timestamp, notification/weather/settings icons,
   user profile (name + role + chevron).
2. **Left sidebar**: Overview; Map & Visualization (Interactive Map/3D
   View/Vertical Cross-Section/Flight Route Analysis/Airport Analysis);
   Hazards (Turbulence/Convection & Thunderstorms/Icing/Wind Shear/Wind &
   Gusts/Visibility & Ceiling/Precipitation/Snow & Icing Accumulation/
   Dust-Sand/Volcanic Ash); Analysis (AWCI & Risk/Forecast/Time Evolution/
   Model Comparison/Uncertainty); Data & Reports (Stations METAR-TAF/Alerts
   & Notifications/Reports/API).
3. **Filter bar**: Area/Date & Time (with prev/next/"Now")/Forecast lead
   time/Model (multi-model) selectors, Layers and Settings buttons.
4. **Hazard gauge row**: a large circular "AWCI GLOBAL" gauge (72/High)
   plus six compact cards — Turbulence, Convection, Icing, Wind Shear,
   Visibility, Ceiling — each an icon, a number, and a severity word.
5. **Hero map**: collapsible "Map Layers" panel (per-hazard layer
   checkboxes + opacity slider), 2D/3D/4D toggle, a real basemap with a
   complexity heatmap overlay, a flight-route overlay with airport
   markers, a color-scale legend, and a playback transport (route/lead-time
   scrubber, "Live Data" indicator).
6. **Right column**: "Current Situation" (overall severity + a Main
   Hazards list with per-hazard severity), "Model Agreement" (single
   number + affected area/altitude/valid time/confidence), and "Airport
   Complexity" (a small table: airport, AWCI score, trend arrow, status
   badge).
7. **Second row (4 cards)**: Vertical Cross Section, Atmospheric Profile
   (Temperature/Wind/Humidity tabs), Flight Route Analysis (route map +
   per-segment risk table + a "Critical Zone" callout), Time Evolution
   (AWCI) (a multi-line chart, Global/Route/Airport tabs).
8. **AWCI Vertical Profile card**: a per-level table (altitude → AWCI
   score, colored) alongside a small vertical strip visualization.
9. **Bottom row (3 cards)**: Recent Alerts (a short severity-colored list),
   Latest Updates (a checklist-style log with timestamps), Quick Actions
   (Generate Report / Route Analysis / Save Scenario / Export Data
   buttons).

## Decisions made during brainstorming

- **Scope**: build the entire reference image in one pass (matching the
  ACF Workstation rebuild's own approach), not split into waves.
- **Code reuse**: recover the old `AWCIDashboard`'s real logic from git
  history as the starting point (its real HPC connect flow, real ALADIN
  archive access, real physics volume computation, model import, flight
  route sampling, vertical/cross-section sampling are all genuinely
  reusable) — rework layout/placement only, per the reference image.
- **Component mapping** (approved):

| Reference section | Real data source |
|---|---|
| AWCI Global gauge | `AWCICalculator.calculate()["awci"]` (existing real composite score) |
| Turbulence / Convection / Icing / Wind Shear gauges | `AWCICalculator.calculate_module_scores()`'s real `dynamic`/`convective`/`microphysical` modules, plus `acf.awci.wind_shear.compute_real_wind_shear_at_point()` |
| Visibility / Ceiling gauges | No dedicated module in `AWCICalculator` — real, disclosed threshold heuristics (same convention as the ACF Workstation's `HazardAlertsPanel`: RH-based visibility proxy, cloud-base/ceiling proxy), documented as heuristics, not an `AWCICalculator` output |
| Model Agreement | `AWCICalculator`'s real `model_disagreement` output |
| Hero map + Map Layers + 2D/3D/4D + transport | Recovered `awci_map_panel.py` (real zoom/pan/export already built) + the old dashboard's real "Real Physics" volume flow (`compute_real_complexity_volume`) |
| Current Situation / Main Hazards | Derived from the same real module scores, ranked by severity |
| Airport Complexity table | Real AWCI score sampled at named points via `acf.awci.path_sampling` |
| Vertical Cross Section | Recovered real `sample_volume_cross_section()` flow |
| Atmospheric Profile | Recovered real vertical-profile flow (`_open_vertical_profile` in the old dashboard) |
| Flight Route Analysis | Recovered real `path_sampling.sample_field_along_path()` flow |
| Time Evolution (AWCI) | Recovered real temporal-field flow (`acf.awci.temporal_field`, the old `_EvolutionWorker`) |
| AWCI Vertical Profile | Same real volume, per-level table view |
| Recent Alerts / Latest Updates / Quick Actions | A real, plain append-only action log (same convention as the ACF Workstation's `SystemFooterPanel`) — never a fabricated entry |

- **Architecture**: a standalone `AWCIDashboardWindow`, opened from a new
  button in the ACF Scientific Workstation (mirroring how the Workstation
  itself is opened from ESOC) — not a new top-level app command.

## Honesty conventions (binding, same as the ACF Workstation)

- No panel computes anything inside `__init__`; real computation is
  triggered by an explicit user action (open, "Run", a filter change),
  off the GUI thread for anything expensive, exactly like the recovered
  old dashboard's own worker pattern.
- Any value with no real backing computation renders an explicit
  `NOT_COMPUTED`/`NOT_AVAILABLE`-style status — never a fabricated number.
  Visibility/Ceiling's own heuristic thresholds are documented in their
  module's own docstring as heuristics, not `AWCICalculator` output.
- The underlying meteorological INPUT fields stay whatever the recovered
  dashboard's own honest framing already was (a synthetic demo pattern
  unless "Real Physics" mode is engaged, per the recovered file's own
  docstring) — this rebuild does not silently upgrade or downgrade that
  disclosure.
- Placement matches the reference image exactly, per the user's explicit
  instruction — panels are not reordered or relocated relative to each
  other even where a different arrangement might seem cleaner.

## Testing

- One test module per new/adapted panel (gauge row, hero map wrapper,
  Current Situation/Model Agreement/Airport Complexity, the 2nd-row 4
  cards, AWCI Vertical Profile, the bottom-row 3 cards).
- One integration test verifying `AWCIDashboardWindow` opens with a real
  volume and that the ACF Workstation's own new button opens/raises it.
- Full suite run (via the project's `.venv`, `QT_QPA_PLATFORM=offscreen`)
  before considering this done, plus a screenshot comparison against the
  reference image (same discipline as the Workstation rebuild's own Task
  10).

## Open items for the implementation plan (not this spec)

- Exact file-by-file split of what's recovered verbatim vs. rewritten
  (the plan should confirm against the actual recovered file's real
  structure, listed above).
- The Visibility/Ceiling heuristic's exact thresholds (to be chosen by
  the implementer, disclosed in-code, following the same discipline as
  the Workstation's own `HazardAlertsPanel` thresholds).
- Any Qt widget-level layout differences needed to make pixel placement
  match the reference image once real content is actually rendered
  (icon choices, exact card proportions) — the visual-QA task should
  reconcile these against the reference image directly.
