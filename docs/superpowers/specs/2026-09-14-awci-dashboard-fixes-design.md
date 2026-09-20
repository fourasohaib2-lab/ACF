# AWCI Dashboard Fixes & Reference-Layout Completion — Design (2026-09-14)

## Context

Two independent AWCI dashboard rebuilds happened concurrently in this
project: one on `origin/develop` (a purpose-built 6-phase redesign with a
real sidebar/topbar, four real data tiers, and 452 passing GUI tests) and
one on a now-abandoned branch (`awci-dashboard-rebuild`, functionally solid
but without a sidebar/topbar). An independent audit of `origin/develop`
(2026-09-13/14) found it to be the stronger foundation — closer to the
reference image's layout (sidebar and topbar are near-exact matches),
extensively tested, and free of the double-scaling class of bug found and
fixed repeatedly on the other branch. This plan continues directly on
`origin/develop` (checked out as branch `awci-dashboard-fixes`), fixing the
audit's disclosed defects and closing the remaining reference-image layout
gap, rather than reconciling two divergent implementations by hand.

Reference image: top-left title "AWCI, Aviation Weather Complexity Index",
saved at `/home/souhaib/.claude/uploads/601e2542-aff9-45ae-a7ce-d1c9147c6efb/4213efcc-image.png`.

The user's standing requirement (unchanged from the original request):
placement, content and function must match the reference image as closely
as this codebase's real data honestly allows — never a fabricated value to
fill a gap, and never silently relocating a real panel from where it
audited correctly today.

## Audit findings this plan must resolve

### Real-data honesty defects (binding — same convention as elsewhere in
this project: every displayed value is either genuinely computed or shows
an explicit `NOT_COMPUTED`/similar status, never a fabricated number)

1. **Visibility/Ceiling hardcoded to `0 / Very Low`.** `AWCICalculator`'s
   `visibility`/`ceiling` modules are opt-in and default to `0.0` when
   `visibility_risk`/`ceiling_height_m` are absent from the input dict —
   `calculator.py`'s own comment states `0.0` means "no signal supplied",
   NOT "unlimited ceiling". `awci_synthetic_field._synthetic_inputs()`
   never supplies these two keys, so both hazard cards always render a
   fabricated-looking `Very Low` (worst-case) severity. The fix already
   exists and is used 200 lines away in the same file for the map's
   Ceiling/Visibility layers: `compute_real_ceiling_at_point()` /
   `compute_real_visibility_risk_at_point()`.
2. **`✅ REAL - genuinely computed` badge shown for unsupplied modules.**
   `awci_component_detail.py`'s demo-mode branch hardcodes
   `is_real, source_label = True, "demo synthetic pattern"` regardless of
   whether the module's real inputs were actually present in the data
   dict — directly contradicting the honest per-input disclosure line
   rendered two rows below it in the same dialog.
3. **Time Evolution chart's X-axis is decoupled from its Y-values.** The
   chart samples at the *relative* `time_offset_hours=float(offset)` but
   labels the X-axis with `(current_hour + offset) % 24` (the *absolute*
   hour) — moving the Valid Time slider relabels the axis without
   changing a single plotted value. The method's own docstring claims the
   series is sampled "around the SAME current Valid Time slider value",
   which is false. Two existing tests encode this bug as intentional and
   must be corrected alongside the fix.
4. **Model Agreement headline reads "Very High" when no real ensemble was
   ever supplied.** `model_realizations` is never wired into the GUI, so
   `disagreement` is always `0.0` (the calculator's own default, meaning
   *unmeasured*, not *perfect*). The current `if disagreement == 0.0`
   branch turns this into a reassuring "Very High agreement" headline
   with a small disclosing note underneath — the headline itself must be
   honest (`NOT_COMPUTED`), with the explanation staying as the subtext.
5. **Real Physics tier's Confidence renders as a fabricated-looking 100%.**
   `AWCICalculator`'s own default `confidence=100.0` (meaning "no
   confidence signal was computed") is rendered as a full green bar
   labelled "Confidence 100%" — must render `NOT_COMPUTED` instead.
6. **`module_scores.get(key, 0.0)` silently fabricates a real-looking zero
   for a genuinely missing key**, at three call sites
   (`awci_hazard_row.py`, `awci_alerts_panel.py`,
   `awci_dashboard.py`'s drill-down). A missing key is *unknown*, not
   *zero* — must render `—`/`NOT_COMPUTED`, matching the honest pattern
   already used for Wind Shear (`key=None` → `—` with a disclosing
   tooltip). The existing test that asserts the `0.0` fallback and names
   it "honestly" must be corrected to assert the honest `—` instead.
7. **AWCI GLOBAL gauge and the 6 hazard cards are computed at different
   spatial locations with no disclosure**: the gauge shows the maximum
   AWCI along the demo flight route, the cards show the point of
   interest — can show a "Low" global gauge next to an "Extreme"
   Turbulence card with nothing explaining why. Must be either
   reconciled to the same source or clearly, visibly labelled as two
   different real quantities (not just in a code comment).
8. **Airport Complexity is silently always demo-tier data**, even while
   Real Physics or Real Archive is the active tier elsewhere on screen —
   disclosed only in a docstring, not in the UI. Must be disclosed
   visibly (e.g. a small "Demo grid" tag on the table) whenever the
   active tier is not demo.

### Layout gaps versus the reference image (independently audited,
~5 of ~14 regions correctly placed today)

9. **Filter bar** (Area / Date & Time / Forecast / Model selectors, plus
   Layers and Settings buttons) is currently merged into the top bar
   instead of its own row, and the Layers/Settings buttons are missing
   entirely.
10. **Hero map** renders far smaller than the reference's ~65%/~40% of
    the viewport, with a large empty band of orphaned buttons beside it;
    the Map Layers panel is docked outside the map instead of floating
    over its top-left corner and has no visible opacity slider; the AWCI
    SCALE legend is clipped; there is no play/timeline transport bar at
    all.
11. **Right column** (Current Situation / Model Agreement / Airport
    Complexity) currently renders as a full-width row above the map
    instead of a narrower column beside it, matching the reference.
12. **Second-row cards** (Vertical Cross Section, Atmospheric Profile,
    Flight Route Analysis, AWCI Vertical Profile) are present but
    severely clipped or reduced to bar charts instead of their reference
    presentation (a route mini-map + segment table + Critical Zone
    callout for Flight Route Analysis; an altitude/AWCI colour-chip table
    + 3D layer stack for AWCI Vertical Profile; visible, unclipped titles
    and tabs for the others).

## Decisions

- **Scope**: fix all 8 real-data honesty defects (small, mostly
  mechanical, high priority per this project's core convention) plus the
  4 layout gaps (larger, more structural). Both tracks matter — the
  user's original demand covers both function and placement.
- **Non-goals carried over from the prior audit**: no attempt to unify
  `awci_gauge.py`'s separate colour table with `awci_colors.LEVELS` unless
  it's touched incidentally by another fix in this plan (flagged as a
  pre-existing Minor finding, not blocking).
- **Testing discipline**: every honesty fix needs a new or corrected test
  that exercises the REAL runtime input path (what the widget actually
  receives from `refresh()`), not a hand-fed fixture using the reference
  image's own numbers — this was the audit's central criticism of the
  existing test suite's blind spot.
- **Architecture**: no new files for the honesty fixes (they are localized
  corrections to existing files). The layout fixes restructure
  `awci_dashboard.py`'s `_build_ui()` layout tree — existing panel classes
  (`awci_situation_panel.py`, `awci_map_panel.py`, etc.) are re-parented
  and resized, not rewritten from scratch, preserving their own already-
  audited real data wiring.

## Testing

- One test (new or corrected) per honesty fix, each driven by the widget's
  real runtime input path.
- Visual verification after the layout fixes: launch `AWCIDashboardWindow`
  offscreen, `.refresh()`, screenshot, compare section-by-section against
  the reference image using the same rubric as the prior audit (~14
  regions), documenting the resulting region-by-region match honestly —
  including any regions still not fully matched, if the layout work proves
  too large to close 100% in one pass.
- Full GUI suite (`tests/gui/`) run clean (452+ passing, 0 failed) before
  considering this plan done.

## Open items for the implementation plan (not this spec)

- Exact task split and ordering between the 8 honesty fixes (small,
  parallelizable in principle but touching some shared files — the plan
  must sequence tasks that touch the same file) and the 4 layout fixes
  (more sequential, since hero map resize and right-column repositioning
  affect the same top-level layout tree).
- Whether the hero map / right column / second-row layout work fits in a
  single task each or needs further splitting once `_build_ui()`'s current
  ~688-line structure is read in full by the implementer.
