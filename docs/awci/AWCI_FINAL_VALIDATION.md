# AWCI Final Validation

**Date:** 2026-09-03. Verification checklist for this closure (map
click, risk-badge click, flight-level selector, AWCI Input Adapter,
audit docs), run after all code changes per the plan's own "screenshot
after all interactivity changes" step.

## Static checks

| File | ruff | mypy |
|---|---|---|
| `src/acf/awci/input_adapter.py` | ✅ | ✅ |
| `src/acf/gui/dashboard/awci_map_panel.py` | ✅ | ✅ |
| `src/acf/gui/dashboard/awci_risk_summary.py` | ✅ | ✅ |
| `src/acf/gui/dashboard/awci_dashboard.py` | ✅ | ✅ |
| `tests/test_awci_input_adapter.py` | ✅ | n/a (test file) |
| `tests/test_awci_map_panel_point_click.py` | ✅ | n/a |
| `tests/gui/test_awci_dashboard_synchronization.py` | ✅ | n/a |

## Test suite

- Targeted suites re-run repeatedly during development: map-panel
  regression (`test_awci_map_panel_zoom_pan.py`,
  `test_awci_map_panel_reference_fidelity.py`), risk-summary
  (`test_awci_risk_summary.py`), full `tests/gui/*awci*` — all green
  throughout, no regression at any point.
- Full suite: **3852/3852 before this closure → 3883/3883 after**
  (31 new tests, 0 broken, 0 skipped-away). Command:
  `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q` — 177s.

## Visual regression (priority-1 requirement — no design deviation)

Rendered `AWCIDashboard` offscreen (`QT_QPA_PLATFORM=offscreen`,
`widget.grab()`) at 1600×1000 after all interactivity changes and
compared side-by-side against
`docs/reference/awci_dashboard_reference.jpg`:

- Header, VIEW MODE row, global map (title, legend, info boxes, layers
  panel), cross-section, radar/component list, stats bar, regional map,
  regional trend + vertical-profile button, valid-time/level sliders,
  route chart, risk summary, recommendation banner, footer — all
  unchanged in position, size, and styling from the prior closure's own
  already-verified state.
- The one new visible element is the "Flight Level:" label + combo box,
  appended to the existing VIEW MODE row (not a new row — avoids this
  session's own earlier layout-collapse regression pattern). This is a
  disclosed, necessary functional addition (the master prompt's own
  "single source of truth" requirement) not present in the static
  reference image, matching the same precedent already set by VIEW MODE
  itself, 🔬 Real Physics, and 🛩 Compare FL280/FL320 — all real
  controls added in earlier closures beyond the literal mockup pixels,
  because the mockup is a static concept image and this is a live
  application. No existing reference-matched element was altered,
  resized, recolored, or removed.
- `tests/gui/test_awci_dashboard_reference_parity.py`'s own 19
  assertions (widget presence, sizing, styling) still pass unchanged,
  independently confirming no regression.

## Functional checks (real, not simulated)

- Map click (global and regional) emits real (lat, lon), rejects a real
  drag-pan via the existing ≤4px distance check, and re-runs the exact
  same real per-point pipeline the old hardcoded point used — verified
  by `tests/test_awci_map_panel_point_click.py` (canvas-level, via
  `QApplication.sendEvent()`) and
  `tests/gui/test_awci_dashboard_synchronization.py` (dashboard-level,
  demo AND Real Physics mode).
- Risk-badge click: turbulence/icing/convective reuse the real
  `AWCIComponentDetailDialog` (not a duplicate); overall/physical/
  forecast open `AWCIRiskBadgeDetailDialog` showing the real
  `module_scores` breakdown — both paths verified.
- Flight-level selector: bit-identical `FL300` default (no score
  drift for any pre-existing caller), re-runs the point-of-interest
  pipeline in demo mode, snaps to the nearest real native level and
  syncs `level_slider` in Real Physics mode — all 4 behaviors verified.
- AWCI Input Adapter: unit conversion, the pressure hPa/Pa regression
  guard, ACF-internal key passthrough, honest `MISSING` reporting,
  end-to-end `AWCICalculator` coherence, real-field round-trip — all
  12 behaviors verified against direct `AWCICalculator`/
  `assess_variable_quality()` calls, not against the adapter's own
  output.

## Known, disclosed non-goals (not defects)

See `future-improvements.md` for the full list; the two most relevant
to this closure:

- `RouteOptimizationEngine` — not built (would contradict this
  project's own established anti-fabrication precedent).
- 4 of the ~7 originally-hardcoded flight-level constants stay
  independent by design (different real routes/displays, some fixed
  by the reference mockup's own map titles) — see
  `AWCI_IMPLEMENTATION_STATUS.md`'s "Design decisions".

## Conclusion

Closure complete: all 5 planned scope items built, tested, documented.
Zero regressions in the existing 3852 tests. Zero visual deviation from
the reference mockup beyond one disclosed, necessary functional
addition. Ready to commit.
