# AWCI Interaction Matrix

**Date:** 2026-09-03 (updated after implementation — 3 rows below that
were planned as **NEW** are now real, built, and tested; see
AWCI_IMPLEMENTATION_STATUS.md for the closure's final as-built state).
Real interactions only. No row describes a decorative/dead control.

| Element | Event | State change | Action | UI impact |
|---|---|---|---|---|
| 🔬 Real Physics button | click | `_real_physics_active=True`, `_real_volume=<volume>` | `compute_real_complexity_volume()` off-thread | every panel switches to the real solver field |
| ▶ Play Evolution button | click | `_evolution=<result>`, timer active | `compute_real_complexity_evolution()` off-thread + `QTimer` | global map animates through real frames |
| 🧊 3D View button | click | opens/raises `AWCIVolume3DView` | none (reads `_real_volume`) | real 3D stacked contour view |
| 📨 Message button | click | opens/raises `AWCIMessagesDialog` | live NOAA fetch, off-thread | real METAR/TAF/SIGMET text |
| 🔔 Alerts button | click | opens/raises `AWCIAlertsDialog` | reads `_last_risk_inputs` | real elevated-risk list |
| VIEW MODE: Global/Regional/Vertical Cross-Section | click (radio) | none persisted | `AWCIMapPanel.set_extent()` | global map camera zooms |
| Global/Regional map | drag | camera pan | `MapCamera.pan()` | map view shifts |
| Global/Regional map | wheel | camera zoom | `MapCamera.zoom_in/out()` | map view zooms |
| Global/Regional map | double-click | camera reset | `MapCamera.reset()` | map returns to default view |
| Global/Regional map | click (not a drag — see `AWCIMapPanel.mouseReleaseEvent()`'s own real ≤4px click-vs-drag distance check) | `_point_of_interest=(lat, lon)` | re-runs the real per-point pipeline (`refresh()` in demo mode, `_apply_volume_at_level()` in Real Physics mode) | Point Information card, radar, component list, risk summary, recommendation banner all update for the new point |
| LAYERS → AWCI checkbox | toggle | contour visibility | `self._contour.set_visible()` | heatmap shown/hidden |
| LAYERS → Wind/Turbulence/Icing/Convection/CAPE/Clouds | toggle | shows/hides a real contour built from `awci_layer_grids()` | `contour.set_visible()` | real per-layer contour appears/disappears (demo mode only — real no-op while Real Physics mode is active, see AWCI_BUTTON_CONTRACT.md) |
| Zoom +/− buttons | click | camera zoom | `MapCamera.zoom_in/out()` | map view zooms |
| Reset view button | click | camera reset | `MapCamera.reset()`/`set_extent()` | map returns to default |
| Download PNG button | click | none | `figure.savefig()` | real PNG file written (after explicit user save-dialog confirmation) |
| Radar / component list row | click | opens `AWCIComponentDetailDialog` | reads real `module_scores`/`raw_data`/`AWCIResult` | shows real formula, status, diagnostic docs, drill-down trace |
| Risk summary badge | click | turbulence/icing/convective: opens the SAME `AWCIComponentDetailDialog` as the matching radar/component-list row (reused, not a second dialog); overall/physical/forecast: opens `AWCIRiskBadgeDetailDialog` | reads `_last_risk_inputs`/`_last_point_raw_data`/`_last_point_mode` — the same real inputs the badge already displays | shows the real score plus the real module_scores breakdown behind that composite number |
| Flight Level selector | change | demo mode: `_current_flight_level_hpa=<hpa>`; Real Physics mode: nearest real native level → `_current_level_index` (and syncs `level_slider`'s own position) | demo mode: re-runs `refresh()`'s point-of-interest pipeline (radar, component list, regional trend, stats-bar grid scan, risk summary); Real Physics mode: `_apply_volume_at_level()` at the nearest level (same full re-render `level_slider` itself triggers) | demo mode: radar/component list/regional trend/stats bar/risk summary update, global/regional map titles and cross-section/route-chart cruise levels are UNCHANGED (fixed, matching the reference mockup); Real Physics mode: everything `level_slider` already updates, plus `level_slider`'s handle moves to match |
| Valid Time slider | release | `time_offset_hours` changes | re-samples the synthetic pattern / real trend window | regional map, regional trend sparkline update |
| Level slider (Real Physics) | change | `_current_level_index=<idx>` | re-slices the already-computed real volume | global/regional map, route chart, stats, radar, risk summary, point info update, no new solver run |
| 🔍 See Vertical Profile button | click | opens/refreshes `AWCIVerticalProfile` dialog | real `AWCICalculator.calculate()` per named FL | bar chart of real scores by flight level |
| 🛩 Compare FL280/FL320 button | click (toggle) | `_fl_comparison_active` | 2 real route samples at 2 real ISA hPa levels | route chart shows dual-line comparison + legend |
| Component detail dialog | (opens) | none | none | static real display of the clicked component's data |
| Alerts dialog | (opens) | none | reads real inputs | static real display |
| Messages dialog tabs | click | none | none (already fetched) | switches which real station's METAR/TAF is shown |
| 3D view | mouse drag | matplotlib 3D rotation | none | real 3D view rotates |

## Single sources of truth (real, current)

- `_last_risk_inputs`, `_last_awci_result` — the exact values every
  read-only dialog (alerts, component detail) displays; never
  recomputed independently.
- `_current_level_index` — real shared vertical-level index while Real
  Physics mode is active.
- `_current_flight_level_hpa` — real shared flight level for the
  point-of-interest pipeline (radar, component list, regional trend,
  stats-bar grid scan) in demo mode, replacing 3 of the ~7
  independently hardcoded `flight_level_hpa` constants the pre-closure
  audit found. The other 4 (`cross_section`'s 300 hPa cruise for the
  global JFK→CDG route, `route_chart`'s 850 hPa cruise for the
  regional Alger→Tripoli route, `_on_time_changed()`'s 700 hPa for the
  regional map's own FL100-labelled background pattern, and the
  FL280/FL320 comparison's own two literals) are DELIBERATELY left
  independent — each is a different real route/display already fixed
  to its own real level (some named directly in a map title, matching
  the reference mockup), not a duplicate of this same value; unifying
  them would change what those panels actually show, which the
  pre-closure audit did not find broken. See
  `_FLIGHT_LEVEL_SELECTOR_OPTIONS_HPA`'s own docstring for the
  selector's real ICAO/FAA ISA-derived hPa per level (one disclosed
  exception: "FL300" is pinned to the literal 300.0 hPa this pipeline
  always used, not the ISA-derived ~300.9 hPa, so this closure's
  default stays bit-identical to the pre-closure behavior).
- `_point_of_interest` — real shared point, replacing the hardcoded
  `_POINT_OF_INTEREST` module constant. Updated by
  `AWCIMapPanel.pointClicked` from either the global or regional map.
