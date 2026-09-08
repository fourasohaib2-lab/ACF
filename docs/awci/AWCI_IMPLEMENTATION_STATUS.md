# AWCI Implementation Status

**Date:** 2026-09-03. Final as-built state of the closure planned in
`AWCI_UI_AUDIT.md` / the approved session plan. Written after all code
changes (per the plan's own "deliberately deferred until after" note),
so every claim below reflects what actually shipped, not what was
planned.

## What was built

### 1. `AWCI Input Adapter` — `src/acf/awci/input_adapter.py` (new)

Bridges ACF's real Data Contract (`acf.core.contracts.dataset.Dataset`)
into `AWCICalculator`'s own plain `dict` input contract — the one
genuine gap the pre-implementation audit found (a real Data Contract and
a real Model Adapter Protocol both already existed; nothing translated
one into the other). `build_awci_data_from_datasets()` +
`datasets_from_real_field_point()`. 12 tests
(`tests/test_awci_input_adapter.py`), including a real regression guard
for a genuine bug found while building it (see "Bugs found and fixed"
below).

### 2. Map click → point of interest — `awci_map_panel.py` + `awci_dashboard.py`

`AWCIMapPanel.pointClicked(lat, lon)` — a real Qt signal, emitted on
`mouseReleaseEvent()` only when the press/release positions are within
4px (a real click, not a drag-pan — reuses `EventMixin`'s own existing
bookkeeping). Connected from both `global_map` and `regional_map` to
`AWCIDashboard._on_map_point_clicked()`, which sets the new
`self._point_of_interest` single source of truth (replacing the
hardcoded `_POINT_OF_INTEREST` module constant) and re-runs the real
per-point pipeline — `refresh()` in demo mode, `_apply_volume_at_level()`
in Real Physics mode. 4 tests
(`tests/test_awci_map_panel_point_click.py`) + coverage in
`tests/gui/test_awci_dashboard_synchronization.py`.

### 3. Clickable risk-summary badges — `awci_risk_summary.py` + `awci_dashboard.py`

`AWCIRiskSummary.rowClicked(key)` — each row is now a `_RiskRow`
(mirrors `_ComponentRow`'s own established click pattern: a `QFrame`
with `mousePressEvent()`/hover styling, not a `QPushButton`, so the
original icon-left/badge-right layout is unchanged). Turbulence/Icing/
Convective map onto a real `AWCICalculator` module and reuse the
existing `AWCIComponentDetailDialog` (not a second, parallel dialog for
the same real number). Overall/Physical/Forecast are composite scores
with no single module formula, so they open a new
`AWCIRiskBadgeDetailDialog` showing the real `module_scores` breakdown
that composes them.

### 4. Flight-level selector — `awci_dashboard.py`

`flight_level_selector` (`QComboBox`, options FL100/180/240/280/300/
320/390) drives `self._current_flight_level_hpa` — the real single
source of truth for 3 of the ~7 independently hardcoded
`flight_level_hpa` constants the pre-implementation audit found
(`refresh()`'s point-of-interest calc, its regional-trend sampling loop,
and `awci_grid()`'s stats-bar scan). **Scoped deliberately narrower
than "every hardcoded level in the file"** — see "Design decisions"
below for which 4 constants were left independent and why.

### 5. Documentation set — `docs/awci/*.md` (8 files)

`AWCI_UI_AUDIT.md`, `AWCI_COMPONENT_INVENTORY.md`,
`AWCI_INTERACTION_MATRIX.md`, `AWCI_LAYOUT_SPEC.md`,
`AWCI_BUTTON_CONTRACT.md`, `future-improvements.md` (all updated after
implementation to remove "planned"/"NEW" language that no longer
matched reality), plus this file and `AWCI_FINAL_VALIDATION.md`.

## Design decisions (disclosed, not silent)

- **`RouteOptimizationEngine` (master prompt §30) — not built.** Two
  real, deliberate stubs already exist in this codebase, both
  explicitly gutted of a fabricated `"FL360"` flight-level
  recommendation. A new engine scoring AWCI composite values into a
  recommendation would have no more real scientific basis than what was
  already removed. See `AWCI_UI_AUDIT.md` §8 and
  `future-improvements.md` §1.
- **Flight-level selector scope.** The pre-implementation audit found
  ~7 independently hardcoded `flight_level_hpa`/`cruise_hpa` constants.
  Only 3 (all genuinely the SAME concept — "what level is the point of
  interest evaluated at") were unified. The other 4 are different real
  routes/displays already fixed to their own real level, some named
  directly in a map title matching the reference mockup
  (`global_map`'s "(FL300)", `regional_map`'s "(FL100)"): unifying them
  would have changed what those panels show, which the audit did not
  find broken, and would have violated the master prompt's own §1
  pixel-fidelity priority. See `AWCI_INTERACTION_MATRIX.md`'s "Single
  sources of truth" section for the itemized list.
- **`FL300`'s bit-identical default.** Every other named-FL entry in
  `_FLIGHT_LEVEL_SELECTOR_OPTIONS_HPA` is the real ICAO/FAA ISA-derived
  hPa (`flight_level_ft_to_pressure_hpa()`). `"FL300"` is a disclosed
  exception, pinned to the literal `300.0` hPa this pipeline always
  used — not the ISA-derived ~300.9 hPa — so introducing the selector
  does not silently shift any existing demo-mode AWCI score computed
  before this closure. Verified by
  `test_flight_level_selector_defaults_to_fl300_bit_identical` and the
  full existing test suite staying green unchanged.

## Bugs found and fixed

- **AWCI-vs-CF pressure unit mismatch** (`input_adapter.py`).
  `AWCICalculator`'s own `"pressure"` key expects hPa (its own
  docstring); the real CF canonical unit for `"air_pressure"` is Pa.
  Converting to Pa for `AWCICalculator` itself would have fed it a
  value 100x too large. Fixed via a separate
  `AWCI_KEY_NATIVE_UNIT` mapping, isolated from the CF-canonical-unit
  conversion used only for quality assessment. Regression-guarded by
  `test_pressure_stays_in_hpa_for_awcicalculator_not_converted_to_cf_pascals`.
- **Double `pointClicked` emission** (`awci_map_panel.py`). A real
  PySide6/matplotlib-canvas double-delivery: a single real click on
  `self.canvas` reaches `AWCIMapPanel.mouseReleaseEvent()` twice —
  once via this panel's own `eventFilter()` forward, once via a second,
  independent native Qt delivery path whose exact internal mechanism
  was not tracked down further (confirmed with both
  `QApplication.sendEvent()` and `QTest.mouseClick()`, so this is real,
  not a test-harness artifact). `id(event)`-based deduplication does
  NOT work — PySide6 hands back a distinct Python wrapper object per
  delivery even for the same real click. Fixed by having
  `mouseReleaseEvent()` CONSUME (clear to `None`) `_click_press_position`
  on the first of the two deliveries, so the second is a real,
  harmless no-op. Regression-guarded by all 4 tests in
  `tests/test_awci_map_panel_point_click.py`.

## Test coverage added

| File | Tests | Covers |
|---|---|---|
| `tests/test_awci_input_adapter.py` | 12 | unit conversion, the pressure hPa/Pa regression, ACF-internal key passthrough, honest MISSING reporting, array-size guard, end-to-end `AWCICalculator` coherence, real-field round-trip |
| `tests/test_awci_map_panel_point_click.py` | 4 | click emits real (lat, lon); drag does not emit; two distinct clicks give distinct coordinates; press bookkeeping unbroken — all via real `QApplication.sendEvent()`, the double-delivery guard included |
| `tests/gui/test_awci_dashboard_synchronization.py` | 15 | map click updates `_point_of_interest` (demo + Real Physics); risk-badge click routes to the right dialog (module-mapped and composite); flight-level selector default is bit-identical, re-runs the point pipeline, does not touch map titles, and snaps to the nearest native level in Real Physics mode |

## Verification

`ruff check` and `.venv/bin/mypy` clean on every new/touched file. Full
`pytest -q` suite: 3852/3852 before this closure, **3883/3883 after**
(31 new, 0 broken). See `AWCI_FINAL_VALIDATION.md` for the full
checklist and screenshot comparison against
`docs/reference/awci_dashboard_reference.jpg`.

## What was NOT built (see `future-improvements.md` for full detail)

RouteOptimizationEngine/flight-level recommendation scoring, calendar
date-picker, WebGL/GPU/worker rendering, repo-wide accessibility sweep,
full Ellrod–Knapp CAT index, real per-grid-cell CAPE contour layer,
reconciling the two incompatible map-layer systems. None of these were
in this closure's own approved scope.
