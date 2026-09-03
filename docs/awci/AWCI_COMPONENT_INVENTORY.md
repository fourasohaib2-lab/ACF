# AWCI Component Inventory

**Date:** 2026-09-03. Every component below is real and already present in
`src/acf/gui/dashboard/` (Python/PySide6/matplotlib widgets, not React
components — see `AWCI_UI_AUDIT.md` §0). Status column: ✅ real and wired,
🟡 real but partial/disclosed limitation, ⬜ not built (see
`future-improvements.md`).

| # | Component (mockup label) | File | Status | Data source |
|---|---|---|---|---|
| 1 | Header title + subheader | `awci_dashboard.py::_build_ui` | ✅ | static text |
| 2 | Header status badge (RESEARCH STAGE) | `awci_dashboard.py::_build_ui` | ✅ | static text |
| 3 | 🔬 Real Physics button | `awci_dashboard.py` | ✅ | triggers `compute_real_complexity_volume()` off-thread |
| 4 | ▶ Play Evolution (4D) button | `awci_dashboard.py` | ✅ | `compute_real_complexity_evolution()` off-thread |
| 5 | 🧊 3D View button + `AWCIVolume3DView` | `awci_volume_3d.py` | ✅ | same real volume as #3 |
| 6 | 📨 Message button + `AWCIMessagesDialog` | `awci_messages_panel.py` | ✅ | live NOAA METAR/TAF/SIGMET |
| 7 | 🔔 Alerts button + `AWCIAlertsDialog` | `awci_alerts_panel.py` | ✅ | real elevated risks + live METAR flags |
| 8 | VIEW MODE radios | `awci_dashboard.py` | ✅ | real `MapCamera.set_extent()` |
| 9 | AWCI GLOBAL MAP | `awci_map_panel.py::AWCIMapPanel` | ✅ | `awci_grid()` (demo) / real field (Real Physics) |
| 10 | AWCI SCALE legend | `awci_map_panel.py::_draw_awci_scale_legend` | ✅ | `awci_colors.LEVELS` |
| 11 | RENDERED / FLIGHT LEVEL info boxes | `awci_map_panel.py::_draw_info_boxes` | ✅ | wall-clock UTC + real ISA FL conversion |
| 12 | LAYERS panel | `awci_map_panel.py::_build_layers_panel` | 🟡 | All 7 toggles real (`awci_synthetic_field.awci_layer_grids()`, built 2026-09-03) — Wind (real speed, no direction), Turbulence/Clouds are disclosed proxies (wind-speed gradient / precipitation rate), Icing/Convection/CAPE are direct real formulas; demo mode only for now, empty (real no-op) in Real Physics mode — see AWCI_BUTTON_CONTRACT.md |
| 13 | Zoom/pan/reset/PNG-export buttons | `awci_map_panel.py` | ✅ | real `MapCamera` |
| 14 | Aircraft glyphs + route line | `awci_map_panel.py` | ✅ | real positions; clicking anywhere on the map (not just the glyph) sets the real point of interest — built this closure |
| 15 | POINT INFORMATION card | `awci_map_panel.py::set_point_marker` | ✅ | real `AWCICalculator.calculate()` at the point |
| 16 | VERTICAL CROSS-SECTION | `awci_cross_section.py` | ✅ | `cross_section_field()` (demo) / real volume sample |
| 17 | Cross-section colorbar | `awci_cross_section.py` | ✅ | same real contour |
| 18 | Cross-section hazard icons (❄ / ≈) | `awci_cross_section.py::set_hazard_overlay` | 🟡 | icing real in both modes; turbulence is a disclosed wind-shear proxy, not the full CAT index |
| 19 | AWCI COMPONENTS radar | `awci_radar.py` | ✅ | real `module_scores` |
| 20 | Component value list (clickable) | `awci_dashboard.py::_ComponentValueList` | ✅ | same real `module_scores` |
| 21 | Component detail dialog | `awci_component_detail.py` | ✅ | real formula/status/diagnostic-registry docs/drill-down trace |
| 22 | Stats bar (5 KPIs) | `awci_stats_bar.py` | ✅ | real grid statistics |
| 23 | FORECAST CONFIDENCE half-circle gauge | `awci_stats_bar.py::_ConfidenceGaugeBox` (`awci_gauge.py`) | ✅ | real `confidence_pct` |
| 24 | AWCI REGIONAL MAP | `awci_map_panel.py` (2nd instance) | ✅ | same real pipeline as #9 |
| 25 | Regional city labels (Tunis) | `awci_map_panel.py::set_city_labels` | ✅ | real public coordinate |
| 26 | REGIONAL TREND sparkline | `awci_timeline.py::AWCITimeline` | ✅ | real hourly scores ±6h |
| 27 | 🔍 See Vertical Profile button + dialog | `awci_vertical_profile.py::AWCIVerticalProfile` | ✅ | real scores per named FL |
| 28 | Valid Time slider | `awci_dashboard.py::time_slider` | ✅ | drives synthetic-pattern phase + trend sampling |
| 29 | Level slider | `awci_dashboard.py::level_slider` | 🟡 | still real-single-source-of-truth only in Real Physics mode — demo mode's own equivalent concept is now unified separately by the new Flight Level selector (#37), not by extending this slider itself into demo mode (the real volume's discrete native levels and the demo pattern's continuous hPa input aren't the same kind of value) |
| 30 | ROUTE PLANNING chart | `awci_route_chart.py` | ✅ | `route_profile()` (demo) / real sample |
| 31 | FL280/FL320 comparison | `awci_route_chart.py::set_comparison_series` | ✅ | real 2nd sample at a real ISA hPa level |
| 32 | RISK SUMMARY badges | `awci_risk_summary.py` | ✅ | real classification, clickable — turbulence/icing/convective reuse the real per-module detail dialog, overall/physical/forecast open a real module-score-breakdown popup (built this closure) |
| 33 | Recommendation banner | `awci_dashboard.py::_update_recommendation_banner` | ✅ | real template text from real elevated risks + real route segment |
| 34 | Footer (5 cells) | `awci_footer.py` | ✅ | static text |
| 35 | AWCI Input Adapter | `awci_input_adapter.py` (new) | ⬜→✅ this closure | bridges real `Dataset`/`VariableContract` into `AWCICalculator`'s dict contract |
| 36 | Map point-of-interest click | `awci_map_panel.py` + `awci_dashboard.py` | ⬜→✅ this closure | real lat/lon from the click, re-runs the real per-point pipeline |
| 37 | Flight-level selector | `awci_dashboard.py` | ⬜→✅ this closure | real named FLs; drives `_current_flight_level_hpa` (demo mode's point-of-interest pipeline) or the nearest real native level (Real Physics mode, syncing `level_slider`) |
| 38 | Date/calendar picker | — | ⬜ | not built — see `future-improvements.md` |
| 39 | RouteOptimizationEngine | — | ⬜ | intentionally not built — see `AWCI_UI_AUDIT.md` §8 |
