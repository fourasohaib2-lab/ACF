# AWCI — Future Improvements (deliberately not built)

**Date:** 2026-09-03. Per the master prompt's own §2 rule ("si une
amélioration est intéressante mais non nécessaire à la référence: ne pas
l'implémenter, la documenter"), the items below were considered and
explicitly excluded from this closure, each for a real, disclosed reason
— not silently dropped.

## 1. RouteOptimizationEngine (flight-level recommendation scoring)

**Why not built:** two real, deliberate stubs already exist in this
codebase — `acf/science/query_engine.py`'s "best flight level" branch
and `acf/ai_expert/aviation_reasoning.py`'s `analyze_flight_hazards()` —
both explicitly gutted of a fabricated `"recommended_flight_level:
FL360"` result and now honestly return `None`/`is_real_data: False`. A
new engine producing a flight-level "recommendation" purely from AWCI
composite scores would have no more real scientific basis than what was
already removed. **What would make this real:** a genuine scientific
basis for weighting AWCI-module contributions into an operational
recommendation (e.g. validated against real forecaster judgment per
docs/ACF_MASTER_PROMPT.md §34/§37, which this project's own audit
(`reports/ACF_MASTER_AUDIT_v2.md`) already tracks as a separate, larger,
still-open item) — not a UI task.

## 2. Calendar / date picker

The reference mockup shows a static date string ("2025-05-20 12:00
UTC"), not an interactive picker widget. The dashboard's real
interactive time axis is `time_slider` (0-23h), which already drives the
regional map and trend sparkline. A real `QDateEdit`/`QCalendarWidget`
would need a genuine multi-day dataset behind it (the synthetic demo
pattern and the real `CoupledEarthSolver` run are both single-run,
single-day) — building the picker without real multi-day data behind it
would be exactly the kind of decorative-but-inert control this project's
own conventions exist to avoid.

## 3. WebGL / GPU / worker-based rendering

The master prompt's performance section (§67) describes a browser
canvas/WebGL architecture. This is a desktop PySide6/matplotlib
application, not a browser app — there is no DOM, no WebGL context, and
matplotlib's own `FigureCanvasQTAgg` already renders off the Qt event
loop's own paint cycle. The real, applicable performance techniques
already in use are: real off-thread `QRunnable` workers for expensive
solver runs (`_RealFieldWorker`/`_EvolutionWorker`), real "compute once,
re-slice per interaction" discipline (`acf.awci.path_sampling`) so
UI interactions never trigger a second solver run.

## 4. Repo-wide accessibility (ARIA-equivalent) sweep

No `QAccessible`/`setAccessibleName` convention exists anywhere in
`acf/gui/` today — this would be genuinely greenfield work across the
whole GUI package, disproportionate to this closure's own scope. This
closure adds real `setToolTip()`/keyboard-focusability (already native
to `QPushButton`/`QRadioButton`) to the specific new interactive controls
it introduces (flight-level selector, clickable risk badges, map
click-to-select), but does not attempt a systematic pass over the
pre-existing ~40 other widgets in this package.

## 5. Full Ellrod–Knapp CAT turbulence index

Disclosed in the previous closure (`reports/ACF_MASTER_AUDIT_v2.md`,
"Mise à jour 2026-09-03 — parité complète du dashboard AWCI"): the real
formula (`acf.science.wind_turbulence.CATIndex`) needs real horizontal
wind gradients no per-point pipeline in this codebase computes yet. The
cross-section's turbulence icons use a disclosed, honest proxy (real
vertical bulk wind shear) instead. **Update 2026-09-03 (suite):** the
map's own "Turbulence" LAYERS checkbox is now real too (explicit user
request "je veux rendre tout les boutons de awci en marche") — it
shows a horizontal wind-speed gradient magnitude
(`awci_layer_grids()`'s own `numpy.gradient()` over the real demo wind
grid), a different disclosed proxy from the cross-section's vertical
one. Still not the full Ellrod-Knapp index — this remains open. Also
now real in Real Physics mode (`acf.awci.path_sampling.
real_layer_grids_at_level()`, same disclosed proxy, applied to that
mode's own real wind field).

## 6. Real per-grid-cell CAPE contour map layer

**Closed 2026-09-03 (suite)**, explicit user request "je veux rendre
tout les boutons de awci en marche": `awci_synthetic_field.awci_layer_grids()`
now computes CAPE (and Wind/Icing/Convection/Clouds) across the same
real grid `awci_grid()` already uses, wired as 6 real LAYERS checkboxes
in `AWCIMapPanel` (`_EXTRA_LAYER_SPECS`, `_on_extra_layer_toggled()`).
**Update 2026-09-03 (suite):** Wind/Turbulence/Icing are now also real
in Real Physics mode (`acf.awci.path_sampling.real_layer_grids_at_level()`,
wired via `AWCIDashboard._apply_volume_at_level()` ->
`AWCIMapPanel.set_external_layer_grids()`). Convection/CAPE/Clouds stay
demo-mode-only by necessity, not by remaining scope: `compute_real_complexity_volume()`'s
own real volume carries temperature/wind_speed/u/v/specific_humidity/pressure
but genuinely no CAPE or precipitation field (the same limitation
already disclosed for the AWCI module scores themselves in Real
Physics mode) — a real CAPE/precipitation field for that mode would
require the solver itself to produce one, a separate, larger physics
task, not a UI wiring gap.

## 7. Reconciling the two incompatible map-layer systems

Also disclosed previously: `acf.gui.map.layers.layer_manager.LayerManager`
+ `acf.gui.map.layer_toggle_panel.LayerTogglePanel` (used by ESOC's
`MapCanvas`) and `acf.gui.map.map_layers` (a different `LayerManager`,
unrelated interface) both exist and are not interoperable. Unifying them
is a real, separate architectural task, not something this dashboard's
own LAYERS checkbox panel should attempt unilaterally.

## 8. Multi-variable vertical profile (§51)

**Update 2026-09-03:** `AWCIVerticalProfile` now covers §51's full real
level list (Surface/850/700/500/300/250 hPa + real named flight levels,
demo mode) — see `reports/ACF_MASTER_AUDIT_v2.md`'s own "§51" closure.
Still open: §51 also asks each level to show wind/temperature/humidity/
stability/convection/turbulence/icing individually, not just the
composite AWCI score. `AWCIVerticalProfile` is a single-series bar
chart; showing 7+ real variables per level would need a genuine widget
redesign (a real per-level breakdown table, or a multi-series chart) —
a separate, larger UI task, not attempted in this closure. The real
data itself (`AWCICalculator.calculate()`'s own `module_scores`) is
already computed at every level this widget already loops over
(`_open_vertical_profile()`) — the gap is purely in how it is
displayed, not in what is computed.

## 9. Real Physics mode's own standard-pressure-level profile

Also from the §51 closure above: `_ALL_VERTICAL_PROFILE_LEVELS_HPA`
(Surface/850/700/500/300/250 hPa) is demo mode only, deliberately.
`acf.awci.vertical_field.compute_real_complexity_volume()`'s own real
volume has no vertical interpolation (native solver levels only, see
that module's own `honest_limitation` string) - it cannot honestly
answer "what is the real value at exactly 500 hPa" the way the demo
pattern's continuous analytic function can. Building real vertical
interpolation into `acf.awci.vertical_field` would be a genuine,
separate physics task (not a UI gap) before this could be closed for
Real Physics mode too.
