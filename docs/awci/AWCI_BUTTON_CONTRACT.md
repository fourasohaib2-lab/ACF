# AWCI Button Contract

**Date:** 2026-09-03. Real buttons only (`QPushButton`/`QRadioButton`/
`QCheckBox` instances in `src/acf/gui/dashboard/awci_dashboard.py` and
`awci_map_panel.py`). Hover/focus/active visual states are handled
uniformly by the shared stylesheet (`acf.gui.theme_tokens.dashboard_stylesheet()`)
rather than per-button custom styling — noted once here rather than
repeated per row as identical boilerplate. Keyboard: every button below
is a real `QPushButton`/`QRadioButton`, focusable and activatable with
Space/Enter by native Qt behavior; no custom keyboard handling exists or
is needed beyond that.

| ID | Label | Tooltip (real, from source) | Disabled when | Loading state | Click → state mutation | Error behavior |
|---|---|---|---|---|---|---|
| `real_physics_button` | 🔬 Real Physics / ↩ Back to Demo | explains the real `CoupledEarthSolver` volume every panel switches to | while a run is in flight | button text → "🔬 Computing…", disabled | `_real_physics_active`, `_real_volume` | `_on_real_physics_failed` shows `⚠ Real physics computation failed: <msg>` in the status line, button re-enabled |
| `play_evolution_button` | ▶ Play Evolution (4D) / ⏸ Stop Animation | explains the real continuous solver trajectory | hidden until Real Physics has run once | text → "⏳ Computing 4D evolution…", disabled | `_evolution`, `_evolution_frame_index`, timer active | `_on_evolution_failed` shows the real error, button re-enabled |
| `view_3d_button` | 🧊 3D View | explains the real rotatable 3D volume | until Real Physics has run once | none (dialog itself is instant on an already-real volume) | opens/raises `AWCIVolume3DView` | none needed (no network/compute at click time) |
| `messages_button` | 📨 Message | explains the real NOAA fetch, discloses it can fail per-station | never | per-station error shown inline in the dialog | opens/raises `AWCIMessagesDialog`, triggers a real fetch | honest per-report error text, never fabricated data |
| `alerts_button` | 🔔 Alerts (`<n>`) | explains the real elevated-risk + live-METAR-flag source | never | none | opens/raises `AWCIAlertsDialog` | none (reads already-computed real state) |
| `view_mode_global_radio` / `_regional_radio` / `_cross_section_radio` | Global / Regional / Vertical Cross-Section | — | never | none | `AWCIMapPanel.set_extent()` | none |
| `vertical_profile_button` | 🔍 See Vertical Profile | explains the real per-FL scores | never | none | opens/refreshes `AWCIVerticalProfile` dialog | none |
| `compare_fl_button` | 🛩 Compare FL280/FL320 / 🛩 Hide FL280/FL320 Comparison | explains the real second sample and its cost | never | none | `AWCIRouteChart.set_comparison_series()`/`clear_comparison_series()` | none |
| Zoom in/out (`+`/`−`) | — | "Zoom in"/"Zoom out" | never | none | `MapCamera.zoom_in/out()` | none |
| Reset view (`⤢`) | — | "Reset view" | never | none | `MapCamera.reset()`/panel's own default extent | none |
| Download PNG (`⬇`) | — | "Save this map as a real PNG image" | never | none | `figure.savefig()` after a real save-file dialog | user cancel = no-op |
| `awci_layer_checkbox` | AWCI | — | never | none | `self._contour.set_visible()` | none |
| Wind/Turbulence/Icing checkboxes (built 2026-09-03, `extra_layer_checkboxes`) | — | each layer's own real formula/disclosed proxy (see `AWCIMapPanel._EXTRA_LAYER_SPECS`) | never | none | `contour.set_visible()` on that layer's real contour (`awci_layer_grids()` in demo mode, `acf.awci.path_sampling.real_layer_grids_at_level()` in Real Physics mode) | real in both modes |
| Convection/CAPE/Clouds checkboxes (built 2026-09-03, `extra_layer_checkboxes`) | — | each layer's own real formula/disclosed proxy (see `AWCIMapPanel._EXTRA_LAYER_SPECS`) | never | none | `contour.set_visible()` on that layer's real `awci_layer_grids()`-built contour | demo mode only — while Real Physics mode is active the checkbox stays enabled but is a real no-op (the real solver volume carries no CAPE/precipitation field; a disclosed scope limit, not a fake toggle) |
| `flight_level_selector` (built this closure) | FL100 / FL180 / FL240 / FL280 / FL300 / FL320 / FL390 | explains the real ICAO/FAA ISA-derived hPa per level (FL300 excepted — the pipeline's bit-identical literal 300.0 hPa default) | never | none | demo mode: `_current_flight_level_hpa`; Real Physics mode: nearest real native level → `_current_level_index` (syncs `level_slider`) | none needed (no network/compute failure mode — a real, already-known option list) |
| Risk summary badge (`_RiskRow`, one per risk row, built this closure) | 🌪️ Turbulence / ❄️ Icing / ⛈️ Convective / 📊 Overall / 🌡️ Physical / 🎯 Forecast | none (no `setToolTip()` yet — not part of this closure's scope) | never | none | turbulence/icing/convective: opens `AWCIComponentDetailDialog` (same one the radar/component-list rows use); overall/physical/forecast: opens `AWCIRiskBadgeDetailDialog` | none (reads already-computed real state, same as `_ComponentRow`) |
