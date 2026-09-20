# AWCI Final Polish — Logo, Single-Screen Fit, Button Audit, Completion Verification

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the remaining gap to the user's explicit demand: dashboard visually identical to the reference photo (dark navy top bar with its real AWCI logo, kept exactly as the user liked it), every figure sized so the whole dashboard fits on one screen with no scrolling, every button verified genuinely functional, and an honest final verification that the AWCI project is complete.

**Architecture:** Continues directly on branch `awci-dashboard-fixes` (PR #3 already open against `develop`). No new files; targeted fixes to `awci_topbar.py` (palette + logo), `awci_dashboard.py`'s analysis-row canvas sizing, and a verification-only final task.

**Reference image:** `docs/reference/awci_dashboard_reference.png` (confirmed identical to the image used throughout this whole plan) — dark navy (`#0b1220`-ish) top bar, a blue mountain-peak logo mark top-left before "AWCI", the same mark again bottom-right of the footer next to "Better information. Safer flights."

## Global Constraints

- Every displayed value stays genuinely computed or shows `NOT_COMPUTED` — this plan touches only presentation (color, size, logo), never data sourcing.
- No panel computes in `__init__`.
- Full `tests/gui/` suite stays green (488+ passing) throughout.
- Commit messages end with: `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`

---

### Task 1: Top bar dark palette + real AWCI logo mark

**Files:**
- Modify: `src/acf/gui/dashboard/awci_topbar.py`
- Test: `tests/gui/test_awci_dashboard_filter_row_and_hero_map.py` or a new small test file for the top bar

**Interfaces:**
- Consumes: nothing new.
- Produces: `AWCITopBar`'s `_BG`/`_TEXT`/`_TEXT_MUTED` recolored to the reference's dark navy palette; a new logo widget (a small painted/SVG mountain-peak mark in a rounded blue square, matching the reference image's top-left icon) added before the title text.

- [ ] **Step 1: Open the reference image and sample its real colors**

Read `docs/reference/awci_dashboard_reference.png` directly (already confirmed identical to this whole plan's reference) and identify the real top-bar background color, title/subtitle text colors, and the logo mark's exact shape/colors (a rounded-square badge with a lighter blue mountain/peak glyph, roughly matching this dashboard's own existing `accent_primary`/`TOKENS` blue if one already exists — check `TOKENS` first before inventing a new color).

- [ ] **Step 2: Fix the background/text palette**

Change `AWCITopBar._BG`, `_TEXT`, `_TEXT_MUTED` to the real dark-navy palette sampled in Step 1. Since a plain `QWidget` subclass doesn't paint a stylesheet `background-color` by default (this is the actual root cause of Task 10's finding F3 — the white text-boxes-on-dark-bar bug), either set `self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)` so the stylesheet background genuinely paints, or override `paintEvent`. Prefer `WA_StyledBackground` unless it conflicts with something else in this widget (check first). Verify by rendering: the bar must show a genuine solid dark background with light, readable text — not the old white-boxes-on-dark-page symptom.

- [ ] **Step 3: Add the real logo mark**

Add a small logo widget before the title/subtitle column — either a simple `QPainter`-drawn mountain-peak glyph in a rounded blue square (matching this codebase's own existing custom-painted-widget conventions, e.g. `CircularGaugeWidget` in `acf_workstation_gauges.py`, for style consistency) or an embedded SVG/PNG asset if one already exists in this repo's `docs/reference/` or asset directories (check first — do not fabricate a new asset file if a usable one already exists; if none exists, a simple painted glyph is the honest, lowest-risk choice). Size and position it to match the reference image's proportions (roughly a 32-40px square, left-aligned, vertically centered against the title/subtitle block).

- [ ] **Step 4: Write/extend tests**

Add a test asserting `WA_StyledBackground` (or equivalent) is set, the palette values match the new dark constants, and the logo widget exists and is visible.

- [ ] **Step 5: Run tests, verify pass**

```bash
source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/ -k "topbar or filter_row" -v
```

- [ ] **Step 6: Commit**

```bash
git add src/acf/gui/dashboard/awci_topbar.py tests/gui/
git commit -m "fix(awci): top bar dark navy palette (fixes Task 10 finding F3) + real AWCI logo mark

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 2: Shrink the analysis row's oversized canvases for single-screen fit

**Files:**
- Modify: `src/acf/gui/dashboard/awci_dashboard.py` (the analysis row's `min_panel_height`/canvas sizing, around line 1538 and its 5 consumers)
- Possibly: `src/acf/gui/dashboard/awci_cross_section.py`, `awci_route_chart.py`, `awci_evolution_chart.py`, `awci_vertical_profile.py` (their own `figsize_scale`/internal sizing if the fix needs to go deeper than the wrapper's `setMinimumHeight`)

**Interfaces:**
- Consumes: nothing new.
- Produces: the analysis row's 5 cards (Vertical Cross Section, Atmospheric Profile, Flight Route Analysis, Time Evolution, AWCI Vertical Profile) render at a height close to the reference image's own proportions (~250px, per Task 10's own measurement of the reference — confirm this yourself by measuring the reference image directly) instead of the current ~556px, WITHOUT losing legibility (axis labels, titles must stay readable) or breaking any existing real data/interaction (clicks, tooltips, hover).

- [ ] **Step 1: Measure the real current and target heights**

Read the reference image directly and measure the analysis row's real card height in pixels relative to the whole image height, converting to a real proportion. Read the current `min_panel_height = max(90, int(150 * self._screen_scale))` computation and its 5 consumers (`cross_section`, `route_chart`, `evolution_chart`, `vertical_profile_panel`, and the cross-section's own separate `setMinimumHeight` call at line ~1350) to understand why the actual rendered height (per Task 10's own measurement: 556px) is so much larger than this `min_panel_height` formula would suggest — there is likely a SECOND constraint (e.g. `figsize_scale` inside each chart widget driving matplotlib `Figure` size, or a stretch factor) actually setting the real height, not just `setMinimumHeight`. Find the REAL controlling constraint before changing anything.

- [ ] **Step 2: Reduce the real controlling constraint**

Once the real height driver is identified (likely each chart widget's own `figsize_scale`/matplotlib `Figure(figsize=...)` sizing, given `AWCICrossSection`/`AWCIRouteChart` are constructed with `figsize_scale=self._screen_scale`), reduce it proportionally so the rendered height approaches the reference's real measured proportion. Preserve `self._screen_scale`'s own existing per-screen adaptability — don't hardcode a fixed pixel value that would defeat the screen-scale mechanism already in place.

- [ ] **Step 3: Verify legibility is preserved**

Render the dashboard offscreen at `screen_scale=1.0` after the change and visually confirm axis labels/titles/legends are still readable at the new smaller size — if matplotlib font sizes need a proportional reduction too, apply the same scale factor to them (check each chart widget's own font-size constants).

- [ ] **Step 4: Re-measure the map's real height**

Per Task 9's own report, freeing space elsewhere was expected to let the hero map's stretch factor finally arbitrate toward a larger real height (it was pinned at its 460px minimum specifically because the content column exceeded the viewport). Measure whether shrinking the analysis row now lets the map grow closer to the reference's own ~40% height proportion, and record the real before/after measurement in your report.

- [ ] **Step 5: Verify single-screen, no-scroll fit at a real target resolution**

Render `AWCIDashboardWindow` (not just the bare `AWCIDashboard` widget) offscreen at a real common screen resolution (1920×1080, and also test 1600×900 as a smaller reasonable target) and measure whether the dashboard's real content height now fits within the window's real available viewport height without the `QScrollArea` needing to scroll. If it still doesn't fit at 1920×1080 after this task's own canvas-shrinking work, measure exactly how much overflow remains and report it honestly — do not silently under-deliver on "no scrolling" without disclosing the real gap.

- [ ] **Step 6: Run tests, verify pass**

```bash
source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/ -q
```

- [ ] **Step 7: Commit**

```bash
git add src/acf/gui/dashboard/awci_dashboard.py [any chart widget files touched]
git commit -m "fix(awci): shrink analysis-row canvases toward the reference's real proportions, verify single-screen fit

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 3: Full functional button audit

**Files:** none created; verification + any small, scoped fixes found.

- [ ] **Step 1: Enumerate every real clickable control in the fully-assembled dashboard**

Construct a real `AWCIDashboard` offscreen, `.refresh()`, and enumerate every `QPushButton`/`QToolButton`/checkable control reachable in the widget tree (top bar, filter row, gauge row, hero map's floating layers panel and transport row, right column, analysis row's 5 cards, bottom row's Quick Actions, any dialog-opening buttons in the Settings menu). For each one, drive a real `.click()` (or equivalent real interaction) and verify it produces a real, observable effect (a dialog opens, a value changes, a panel toggles, a real computation runs) — not a silent no-op.

- [ ] **Step 2: Fix any genuinely dead control found**

If Step 1 finds a control that does nothing (a second instance of the gear-button-class regression already fixed once in this plan), fix it with the same rigor as that earlier fix — read the real intended behavior, apply the minimal correct fix, add a test proving the click now works.

- [ ] **Step 3: Produce an honest audit table**

In your report, list every control checked, its real observed behavior, and its verdict (Functional / Fixed / Honestly disabled with a disclosing tooltip, per this dashboard's own established convention for genuinely-unavailable features like the user avatar or Save Scenario/Export Data).

- [ ] **Step 4: Run tests, verify pass; commit any fixes**

```bash
source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/ -q
git add -A
git commit -m "fix(awci): close [N] dead-control findings from a full button audit

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```
(Only if fixes were needed — if the audit finds nothing to fix, skip the commit and say so in the report.)

---

### Task 4: Final verification — is AWCI genuinely 100% complete?

**Files:** none created; verification only.

- [ ] **Step 1: Run the full `tests/gui/` suite and the full repo suite**

Compare against this plan's own established baseline (488 passed in `tests/gui/`; full repo suite ~5035 passed / 2 known pre-existing unrelated failures / 3 skipped).

- [ ] **Step 2: Re-run the section-by-section visual audit against the reference image**

Using the same ~14-region rubric used throughout this whole plan (top bar, sidebar, filter bar, gauge row, hero map + layers/2D-3D-4D/transport, right column, second-row cards ×4, AWCI Vertical Profile, bottom row), produce a final, honest, updated region count — including whether Task 1's logo/palette fix and Task 2's canvas-shrinking closed any of the previously-partial regions.

- [ ] **Step 3: Confirm no-scroll, single-screen fit is real**

Re-verify Task 2's Step 5 measurement at the final state, at 1920×1080.

- [ ] **Step 4: Re-verify all 6 real-data honesty defects stay fixed, live**

Same live-driven re-verification discipline as the original Task 10.

- [ ] **Step 5: State plainly, in the report, whether AWCI is honestly "100% done"**

If genuinely everything (visual fidelity, no-scroll fit, every button functional, every honesty defect fixed) is true, say so plainly. If any gap remains (even a small one), state exactly what it is and why — never round up to "100%" if it isn't literally true. This report is what will be relayed to the user, who explicitly asked for an honest 100%-completion check.

- [ ] **Step 6: Commit any final small fixes surfaced by this pass**

```bash
git add -A
git commit -m "fix(awci): final verification pass findings

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```
