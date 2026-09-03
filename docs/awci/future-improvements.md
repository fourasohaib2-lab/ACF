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
vertical bulk wind shear) instead.

## 6. Real per-grid-cell CAPE contour map layer

Also disclosed in the previous closure: a real per-point CAPE formula
exists (`acf.awci.convective_energy.compute_real_cape_cin_at_point()`)
but a real contour layer needs it computed across a whole grid plus a
new map-overlay layer class — a separate, larger feature than a LAYERS
checkbox. The checkbox exists, honestly disabled.

## 7. Reconciling the two incompatible map-layer systems

Also disclosed previously: `acf.gui.map.layers.layer_manager.LayerManager`
+ `acf.gui.map.layer_toggle_panel.LayerTogglePanel` (used by ESOC's
`MapCanvas`) and `acf.gui.map.map_layers` (a different `LayerManager`,
unrelated interface) both exist and are not interoperable. Unifying them
is a real, separate architectural task, not something this dashboard's
own LAYERS checkbox panel should attempt unilaterally.
