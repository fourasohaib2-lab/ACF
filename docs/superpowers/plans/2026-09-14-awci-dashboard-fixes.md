# AWCI Dashboard Fixes & Reference-Layout Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the 8 real-data honesty defects and the 4 reference-image layout gaps found by an independent audit of the AWCI dashboard on `origin/develop` (branch `awci-dashboard-fixes`).

**Architecture:** Localized, mechanical fixes to existing files for the honesty defects (Tasks 1-6); a targeted disclosure fix for Task 7; layout restructuring of `awci_dashboard.py`'s `_build_ui()` for Tasks 8-9, re-parenting/resizing existing, already-tested panel classes rather than rewriting them; a final full verification pass (Task 10).

**Tech Stack:** PySide6/Qt, matplotlib, real `acf.awci.*` science backend.

**Spec:** `docs/superpowers/specs/2026-09-14-awci-dashboard-fixes-design.md`

## Global Constraints

- Every displayed value is either genuinely computed or shows an explicit `NOT_COMPUTED`/`—`-style status — never a fabricated number (project-wide convention, binding for every task in this plan).
- No panel performs real computation inside `__init__`.
- Every honesty fix needs a test driven by the REAL runtime input path (what the widget receives from `refresh()`), never a hand-fed fixture using the reference image's own numbers.
- Placement matches the reference image as closely as real data honestly allows — panels are not silently relocated beyond what each task specifies.
- Reference image: `/home/souhaib/.claude/uploads/601e2542-aff9-45ae-a7ce-d1c9147c6efb/4213efcc-image.png`.
- Full GUI suite (`tests/gui/`) must stay green (452+ passing, 0 failed) throughout.
- Commit messages end with: `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`

---

### Task 1: Fix fabricated Visibility/Ceiling (`0 / Very Low` hardcoded)

**Files:**
- Modify: `src/acf/gui/dashboard/awci_synthetic_field.py` (`_synthetic_inputs()`)
- Modify: `src/acf/gui/dashboard/awci_dashboard.py` (wherever the Real Physics tier builds its point data dict — grep for `"pressure":` near `_apply_volume_at_level` or similar)
- Test: `tests/gui/test_awci_synthetic_field.py` (or wherever `_synthetic_inputs`/`awci_at` is tested)

**Interfaces:**
- Consumes: `acf.awci.ceiling.compute_real_ceiling_at_point(temperature, specific_humidity, flight_level_hpa)` and `acf.awci.visibility.compute_real_visibility_risk_at_point(temperature, specific_humidity, flight_level_hpa)` — both already imported and used 200 lines away in this same file's `awci_grid_layers()`-style function for the map's Ceiling/Visibility layers. Each returns a dict with `is_real_data: bool` plus its own value key (`ceiling_height_m`, `visibility_risk_score`).
- Produces: `_synthetic_inputs()`'s returned dict gains `ceiling_height_m` and `visibility_risk` keys (note the key name difference: the calculator expects `data["visibility_risk"]`, not `data["visibility_risk_score"]`) whenever the underlying computation reports `is_real_data=True`; omitted (not set to a fabricated 0 or NaN) otherwise, so `AWCICalculator.calculate()`'s own `"ceiling_height_m" in data`/`"visibility_risk" in data` opt-in check behaves correctly.

- [ ] **Step 1: Read the real functions and the existing map-layer usage**

```bash
grep -n "compute_real_ceiling_at_point\|compute_real_visibility_risk_at_point" -A 3 src/acf/gui/dashboard/awci_synthetic_field.py
sed -n '90,140p' src/acf/awci/ceiling.py
sed -n '125,175p' src/acf/awci/visibility.py
```

Confirm the real return shape of both functions (keys, `is_real_data` semantics) before writing any code.

- [ ] **Step 2: Write the failing test**

Add to whatever test file already covers `_synthetic_inputs`/`awci_at` (create `tests/gui/test_awci_synthetic_field.py` if none exists):

```python
from __future__ import annotations

from acf.gui.dashboard.awci_synthetic_field import _synthetic_inputs, awci_at


def test_synthetic_inputs_supplies_real_ceiling_and_visibility_when_available():
    raw = _synthetic_inputs(lat=20.0, lon=10.0, flight_level_hpa=300.0)
    # At a point where the real ceiling/visibility computations report
    # real data, both keys must be present so AWCICalculator.calculate()
    # does not silently default them to a fabricated-looking 0.0.
    from acf.awci.ceiling import compute_real_ceiling_at_point
    from acf.awci.visibility import compute_real_visibility_risk_at_point

    ceil = compute_real_ceiling_at_point(raw["temperature"], raw["specific_humidity"], 300.0)
    vis = compute_real_visibility_risk_at_point(raw["temperature"], raw["specific_humidity"], 300.0)
    if ceil["is_real_data"]:
        assert "ceiling_height_m" in raw
        assert raw["ceiling_height_m"] == ceil["ceiling_height_m"]
    else:
        assert "ceiling_height_m" not in raw
    if vis["is_real_data"]:
        assert "visibility_risk" in raw
        assert raw["visibility_risk"] == vis["visibility_risk_score"]
    else:
        assert "visibility_risk" not in raw


def test_awci_at_no_longer_forces_ceiling_and_visibility_to_worst_case():
    result = awci_at(lat=20.0, lon=10.0, flight_level_hpa=300.0)
    module_scores = result["module_scores"]
    # Real data should produce a genuinely varying score, not the
    # calculator's own "no signal supplied" 0.0 sentinel every time.
    # (0.0 is still an acceptable REAL outcome for some points - the
    # actual assertion is that it is no longer LITERALLY ALWAYS 0.0
    # for every point/level combination, which was the bug.)
    scores_across_points = [
        awci_at(lat=lat, lon=lon, flight_level_hpa=300.0)["module_scores"].get("ceiling", 0.0)
        for lat in (-40.0, 0.0, 40.0)
        for lon in (-90.0, 0.0, 90.0)
    ]
    assert len(set(scores_across_points)) > 1, "ceiling score is still a constant across points"
```

- [ ] **Step 3: Run the test to verify it fails**

```bash
source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_awci_synthetic_field.py -v
```

- [ ] **Step 4: Implement the fix in `_synthetic_inputs()`**

Add, just before the function's `return` statement, the same real computation already used by the map-layer function in this file (import locally inside the function to avoid a module-level circular-import risk, matching this file's own existing convention):

```python
    from acf.awci.ceiling import compute_real_ceiling_at_point
    from acf.awci.visibility import compute_real_visibility_risk_at_point

    result = {
        "temperature": temperature_k,
        "specific_humidity": specific_humidity,
        "wind_speed": wind_speed,
        "cape": cape,
        "cin": cin,
        "precipitation": precipitation,
        "pressure": flight_level_hpa,
        "altitude": terrain_elevation_m,
        "confidence": confidence,
        "temporal_change": temporal_change,
    }
    ceil = compute_real_ceiling_at_point(temperature_k, specific_humidity, flight_level_hpa)
    if ceil["is_real_data"]:
        result["ceiling_height_m"] = ceil["ceiling_height_m"]
    vis = compute_real_visibility_risk_at_point(temperature_k, specific_humidity, flight_level_hpa)
    if vis["is_real_data"]:
        result["visibility_risk"] = vis["visibility_risk_score"]
    return result
```

(Adjust variable names to match whatever the real local variable names are at that point in the function — read Step 1's grep output first.)

- [ ] **Step 5: Fix the Real Physics tier's point dict the same way**

Grep `awci_dashboard.py` for wherever the Real Physics tier (`_apply_volume_at_level` or similarly named method) builds its own point data dict for `AWCICalculator.calculate()` — it currently supplies only temperature/wind/humidity/pressure. Add the same `ceiling_height_m`/`visibility_risk` keys there too, sourced from the SAME real volume data already available at that point (read the surrounding code to find the real temperature/humidity values already in scope, and reuse `compute_real_ceiling_at_point`/`compute_real_visibility_risk_at_point` exactly as above — do not invent a second computation path).

- [ ] **Step 6: Run the tests to verify they pass**

```bash
source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_awci_synthetic_field.py tests/gui/test_awci_hazard_row.py -v
```

Note: `tests/gui/test_awci_hazard_row.py` currently feeds `visibility: 28.0, ceiling: 46.0` directly as a fake `module_scores` dict at the widget level — that test exercises the WIDGET's own display logic given a score, which stays valid and does not need to change. This task fixes the DATA SOURCE upstream of that widget; if any test elsewhere directly asserts the old `0 / Very Low` behavior end-to-end from `refresh()`, update it to expect real varying values instead.

- [ ] **Step 7: Commit**

```bash
git add src/acf/gui/dashboard/awci_synthetic_field.py src/acf/gui/dashboard/awci_dashboard.py tests/gui/test_awci_synthetic_field.py
git commit -m "fix(awci): stop fabricating Visibility/Ceiling as a constant 0/Very Low

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 2: Fix fake "✅ REAL - genuinely computed" badge for unsupplied modules

**Files:**
- Modify: `src/acf/gui/dashboard/awci_component_detail.py`
- Test: wherever this dialog is tested (grep for `AWCIComponentDetailDialog` under `tests/gui/`)

**Interfaces:**
- Consumes: the same `raw_data`/`info.real_inputs` structures already used correctly by this dialog's own "Real Physics" branch (`info.real_in_real_physics`) and its per-input disclosure line.
- Produces: the demo-mode branch's `is_real`/`source_label` now genuinely reflect whether the module's real inputs were present in `raw_data`, matching the already-correct per-input disclosure rendered below it.

- [ ] **Step 1: Read the current demo-mode branch and the correct Real Physics branch for comparison**

```bash
grep -n "is_real, source_label\|real_in_real_physics\|real_inputs" -B3 -A15 src/acf/gui/dashboard/awci_component_detail.py
```

- [ ] **Step 2: Write the failing test**

Find or create a test that constructs the dialog (or calls its badge-computing method directly) for a module whose `real_inputs` were NOT supplied in demo mode (e.g. `visibility` before Task 1's fix, or any module you can construct a missing-input case for) and asserts the badge does NOT read "✅ REAL - genuinely computed" — it should show an honest "not supplied" style badge instead (match whatever wording this dialog already uses for the Real Physics tier's own `⚠ DEFAULT` case, or introduce an equivalent for demo mode if none exists).

- [ ] **Step 3: Fix the demo-mode branch**

Replace the hardcoded `is_real, source_label = True, "demo synthetic pattern"` with a real check against whether every field in `info.real_inputs` was present in the actual data dict supplied to `AWCICalculator.calculate()` for this module — mirror the logic pattern already correctly used by the Real Physics branch (`info.real_in_real_physics`), adapted for demo mode's own real-inputs list.

- [ ] **Step 4: Run tests, verify pass**

```bash
source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/ -k "component_detail" -v
```

- [ ] **Step 5: Commit**

```bash
git add src/acf/gui/dashboard/awci_component_detail.py tests/gui/
git commit -m "fix(awci): component detail badge no longer claims REAL for unsupplied inputs

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 3: Fix Time Evolution chart's X-axis/Y-value decoupling

**Files:**
- Modify: `src/acf/gui/dashboard/awci_dashboard.py` (the Time Evolution chart update method — grep for `time_offset_hours=float(offset)` near the evolution chart code)
- Modify: `tests/gui/test_awci_dashboard_reference_parity.py` (the test whose docstring rationalizes the frozen Y values)
- Modify: `tests/gui/test_awci_dashboard_analysis_panels.py` (the test that hardcodes the same wrong `time_offset_hours=float(offset)` in its "independent recomputation")

**Interfaces:**
- Consumes: `awci_at(lat, lon, flight_level_hpa, time_offset_hours)` — `time_offset_hours` must be the REAL absolute hour (`current_hour + offset`), not the bare relative `offset`, to genuinely anchor the series to the Valid Time slider.

- [ ] **Step 1: Read the current buggy method in full**

```bash
grep -n "time_offset_hours=float(offset)\|current_hour + offset" -B5 -A15 src/acf/gui/dashboard/awci_dashboard.py
```

Confirm exactly which method builds the Time Evolution series and how `current_hour`/`offset` are named and scoped there.

- [ ] **Step 2: Write the failing test**

```python
# In whatever test file already covers Time Evolution (or a new one)
def test_time_evolution_values_genuinely_change_with_valid_time(qtbot):
    # Construct the dashboard, set the Valid Time slider to two different
    # hours, and assert the plotted Y VALUES differ, not just the X labels.
    ...
    dashboard._update_time_evolution_chart()  # or whatever the real method name is, at hour A
    values_a = list(dashboard.evolution_chart.get_ydata())  # adapt to the real accessor
    # move the Valid Time slider to a different hour
    ...
    dashboard._update_time_evolution_chart()  # at hour B
    values_b = list(dashboard.evolution_chart.get_ydata())
    assert values_a != values_b, "Time Evolution values are decoupled from the Valid Time slider"
```

(Adapt to the real method/accessor names found in Step 1 — read the existing `test_awci_dashboard_reference_parity.py:383-391` and `test_awci_dashboard_analysis_panels.py:188-191` tests first, since they already construct and drive this exact chart; reuse their existing setup/fixture code rather than inventing new scaffolding.)

- [ ] **Step 3: Run to verify it fails (or already passes if the existing tests happen to catch it once corrected — see Step 5)**

- [ ] **Step 4: Fix the anchoring bug**

Change the sampling call from `time_offset_hours=float(offset)` to `time_offset_hours=float(current_hour + offset)` (using the real variable names found in Step 1) so the series is genuinely anchored to the absolute Valid Time, matching what the method's own docstring already (incorrectly) claims it does. Update that docstring if it needs rewording to now be accurate.

- [ ] **Step 5: Correct the two existing tests that encode the bug**

`tests/gui/test_awci_dashboard_reference_parity.py`'s test at line ~383-391 currently asserts only that X data changed and rationalizes frozen Y values in its docstring — update its assertion to also check Y values change, and correct/remove the docstring's now-false rationalization.

`tests/gui/test_awci_dashboard_analysis_panels.py`'s test at line ~188-191 hardcodes the same wrong `time_offset_hours=float(offset)` in its own "independent recomputation" used to verify the chart — fix it to use `float(current_hour + offset)` so it genuinely re-derives what the fixed chart should show, not what the old buggy chart showed.

- [ ] **Step 6: Run all three test files to verify everything passes**

```bash
source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_awci_dashboard_reference_parity.py tests/gui/test_awci_dashboard_analysis_panels.py -v
```

- [ ] **Step 7: Commit**

```bash
git add src/acf/gui/dashboard/awci_dashboard.py tests/gui/test_awci_dashboard_reference_parity.py tests/gui/test_awci_dashboard_analysis_panels.py
git commit -m "fix(awci): anchor Time Evolution chart to the real absolute Valid Time

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 4: Fix Model Agreement headline fabricating "Very High" for an unmeasured ensemble

**Files:**
- Modify: `src/acf/gui/dashboard/awci_situation_panel.py`
- Test: `tests/gui/test_awci_situation_panel.py` (the test hardcoding `model_disagreement: 0.0` and asserting the resulting label)

**Interfaces:**
- Consumes: the same `disagreement` value already computed (always `0.0` today since `model_realizations` is never wired in).
- Produces: when `disagreement == 0.0` (the calculator's own "unmeasured" default, not a genuine zero-spread measurement), the headline itself reads `NOT_COMPUTED` — the existing explanatory subtext ("No real multi-model ensemble wired in yet...") stays as-is underneath it.

- [ ] **Step 1: Read the current `if disagreement == 0.0` branch and the `_AGREEMENT_LABELS` table**

```bash
grep -n "_AGREEMENT_LABELS\|disagreement == 0.0" -B3 -A15 src/acf/gui/dashboard/awci_situation_panel.py
```

- [ ] **Step 2: Write the failing test**

Update or add a test asserting that when `disagreement=0.0` (unmeasured), the rendered headline text is `NOT_COMPUTED` (or this codebase's exact honest-status string — check what other panels in this same file already use for their own `NOT_COMPUTED`-style state and match it exactly), not `"Very High"` or any other severity word.

- [ ] **Step 3: Fix the branch**

Change the `disagreement == 0.0` branch's headline output to the honest status string, keeping the disclosing subtext.

- [ ] **Step 4: Fix `tests/gui/test_awci_situation_panel.py`'s existing test**

It currently hardcodes `model_disagreement: 0.0` and asserts a specific (now-wrong) label — update its expected assertion to the new honest headline.

- [ ] **Step 5: Run tests, verify pass**

```bash
source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_awci_situation_panel.py -v
```

- [ ] **Step 6: Commit**

```bash
git add src/acf/gui/dashboard/awci_situation_panel.py tests/gui/test_awci_situation_panel.py
git commit -m "fix(awci): Model Agreement headline says NOT_COMPUTED, not a fabricated Very High

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 5: Fix Real Physics tier rendering a fabricated-looking "Confidence 100%"

**Files:**
- Modify: `src/acf/gui/dashboard/awci_dashboard.py` (the Real Physics confidence-bar rendering call — grep for `confidence_pct=100.0`)
- Test: wherever the stats bar / confidence rendering is tested

**Interfaces:**
- Consumes: `AWCICalculator`'s own default `confidence=100.0` (meaning "no confidence signal was computed", not "maximum confidence").
- Produces: the Real Physics tier's confidence display shows the honest `NOT_COMPUTED` status instead of a full green 100% bar, when this default (uncomputed) value is what's actually being passed.

- [ ] **Step 1: Read the current call site**

```bash
grep -n "confidence_pct=100.0" -B10 -A5 src/acf/gui/dashboard/awci_dashboard.py
```

Read the surrounding comment (already honest in the code) to understand exactly why `100.0` is passed today.

- [ ] **Step 2: Write the failing test** covering the stats bar / confidence widget's honest-`NOT_COMPUTED` rendering when fed this specific "uncomputed default" case (distinguish it from a genuinely-computed 100% confidence, if such a real path exists elsewhere in this codebase — check before assuming EVERY 100.0 confidence value is fake).

- [ ] **Step 3: Fix the call site** to pass the honest `NOT_COMPUTED` signal (whatever sentinel this widget already supports — check `stats_bar.update_data()`'s own signature for a `None`/optional-confidence convention before inventing a new one) instead of the literal `100.0`.

- [ ] **Step 4: Run tests, verify pass.**

- [ ] **Step 5: Commit**

```bash
git add src/acf/gui/dashboard/awci_dashboard.py tests/gui/
git commit -m "fix(awci): Real Physics tier shows NOT_COMPUTED confidence, not a fabricated 100%

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 6: Fix `module_scores.get(key, 0.0)` fabricating a real-looking zero for a missing key

**Files:**
- Modify: `src/acf/gui/dashboard/awci_hazard_row.py`
- Modify: `src/acf/gui/dashboard/awci_alerts_panel.py`
- Modify: `src/acf/gui/dashboard/awci_dashboard.py` (the drill-down call site)
- Test: `tests/gui/test_awci_hazard_row.py` (specifically `test_missing_module_score_keys_default_honestly_to_zero`, which must be corrected, not just re-asserted)

**Interfaces:**
- Consumes: `module_scores: dict[str, float]` from a real `AWCICalculator.calculate()` result.
- Produces: at each of the 3 call sites, a missing key now renders the honest `—`/`NOT_COMPUTED` status (matching the pattern already used for Wind Shear's `key=None` case in the same file) instead of a fabricated `0.0`.

- [ ] **Step 1: Read all 3 call sites and the existing Wind Shear `key=None` honest pattern to mirror**

```bash
grep -n "module_scores.get(.*0\.0)" src/acf/gui/dashboard/awci_hazard_row.py src/acf/gui/dashboard/awci_alerts_panel.py src/acf/gui/dashboard/awci_dashboard.py
grep -n "key=None\|key is None" -B3 -A10 src/acf/gui/dashboard/awci_hazard_row.py
```

- [ ] **Step 2: Rename/correct the existing misleading test**

`tests/gui/test_awci_hazard_row.py::test_missing_module_score_keys_default_honestly_to_zero` currently asserts `row._cards["Turbulence"].value_label.text() == "0"` for an empty `module_scores` dict — rename it to something like `test_missing_module_score_keys_render_honestly_as_unknown` and change its assertion to expect the honest `—` (or whatever this widget's real unknown-value display text is — check `set_value(None)`'s actual rendering) instead of `"0"`.

- [ ] **Step 3: Fix all 3 call sites**

Replace `module_scores.get(key, 0.0)` with `module_scores.get(key)` (returns `None` for a missing key) and route that `None` through the same honest-unknown display path each widget already supports (`set_value(None)` for the hazard cards; check `awci_alerts_panel.py`'s and the drill-down's own equivalent).

- [ ] **Step 4: Run tests, verify pass**

```bash
source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_awci_hazard_row.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/acf/gui/dashboard/awci_hazard_row.py src/acf/gui/dashboard/awci_alerts_panel.py src/acf/gui/dashboard/awci_dashboard.py tests/gui/test_awci_hazard_row.py
git commit -m "fix(awci): a missing module score renders honestly, not as a fabricated 0

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 7: Disclose the AWCI Global gauge/hazard-card location mismatch and Airport Complexity's always-demo-tier data

**Files:**
- Modify: `src/acf/gui/dashboard/awci_dashboard.py` (both the gauge/card update call site and the Airport Complexity table update call site)
- Test: wherever these two panels are already tested

**Interfaces:**
- Consumes: the existing `overall_awci` (route max) vs `point_result["module_scores"]` (point value) values already computed; the existing knowledge of which data tier is currently active.
- Produces: a visible UI disclosure (a tooltip, a small label, or a title-bar caption — your judgment on the lightest-touch real fix that is actually visible to a user, not buried in a code comment) that these two panels/values reflect two different real quantities/sources.

- [ ] **Step 1: Read the current gauge/hazard-row update call and the Airport Complexity update call**

```bash
grep -n "overall_awci = max(route_scores)" -B5 -A15 src/acf/gui/dashboard/awci_dashboard.py
grep -n "def _update_airport_complexity\|_AIRPORTS\b" -A20 src/acf/gui/dashboard/awci_dashboard.py
```

- [ ] **Step 2: Add a visible disclosure for the gauge/card mismatch**

Add a tooltip on the AWCI Global gauge (or a small caption near it) stating it reflects the maximum AWCI along the demo route, distinct from the 6 hazard cards below it which reflect the point of interest — reuse this dashboard's own existing tooltip-setting convention (grep for `.setToolTip(` nearby for the exact style/wording pattern already used elsewhere in this file).

- [ ] **Step 3: Add a visible "Demo grid" disclosure on the Airport Complexity table when the active tier is not demo**

When the currently active data tier (Real Physics / Real Archive / imported model) is not demo, add a small visible tag/label on or near the Airport Complexity table (matching this dashboard's own existing tier-indicator conventions — check how the dashboard already indicates the active tier elsewhere, e.g. the `DEMO MODE`/`RESEARCH STAGE` badges in the top bar, and reuse that visual language) stating the table's values are still demo-tier, since real per-airport sampling has not been wired for the other tiers.

- [ ] **Step 4: Add tests** covering both disclosures render (or don't render, when demo tier is active) as expected.

- [ ] **Step 5: Run tests, verify pass.**

- [ ] **Step 6: Commit**

```bash
git add src/acf/gui/dashboard/awci_dashboard.py tests/gui/
git commit -m "feat(awci): visibly disclose the AWCI gauge/card location mismatch and Airport Complexity's demo-tier data

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 8: Layout — filter bar as its own row (Layers/Settings buttons) and hero map resize/reposition

**Files:**
- Modify: `src/acf/gui/dashboard/awci_dashboard.py` (`_build_ui()`)
- Test: `tests/gui/test_awci_dashboard_reference_parity.py` (extend with new layout assertions) or a new test file

**Interfaces:**
- Consumes: the existing `awci_topbar.py`/`AWCITopBar` widget (currently hosting the Area/Date&Time/Forecast/Model selectors merged into it) and the existing hero map widget (`AWCIMapPanel` or equivalent).
- Produces: the filter bar's Area/Date & Time/Forecast/Model selectors move into their OWN row below the top bar (not merged into it), with Layers and Settings buttons added to that row; the hero map grows to occupy roughly the reference image's ~65% width / ~40% height footprint, with its Map Layers panel floating over the map's top-left corner (not docked outside it) and a visible opacity slider; the AWCI SCALE legend renders unclipped; a play/timeline transport row is added beneath the map matching the reference image's layout.

- [ ] **Step 1: Read `_build_ui()`'s current top-of-layout structure in full**

This file is ~3,442 lines. Before changing anything, read the FULL current top bar / filter-selector / hero map section (from wherever the top bar is constructed through to wherever the map widget is added to its layout) — do not guess at the current structure from grep alone.

```bash
grep -n "def _build_ui\|AWCITopBar\|_wire_topbar\|AWCIMapPanel\|Map Layers\|self.map_panel" src/acf/gui/dashboard/awci_dashboard.py
```

- [ ] **Step 2: Extract the filter selectors into their own row**

Move the Area/Date & Time/Forecast/Model selector widgets (currently constructed as part of the top bar, per `AWCITopBar`/`_wire_topbar()`) into a new, dedicated `QHBoxLayout` row placed directly below the top bar and above the hero map, matching the reference image's filter-bar position. Add Layers and Settings `QPushButton`s to this new row — read `awci_dashboard.py`'s own existing Settings-menu convention (if a Settings dialog/menu already exists elsewhere in this file per the earlier ACF Workstation/AWCI work, reuse or extend it rather than building a second one) and a Layers button that toggles the Map Layers panel's visibility (see Step 3).

- [ ] **Step 3: Resize and reposition the hero map**

Increase the map widget's size policy/stretch factor so it occupies the reference image's proportions (~65% width / ~40% height of the dashboard's overall viewport) rather than its current ~28%/~19%. Move the Map Layers panel (checkboxes + opacity slider) to float as an overlay anchored to the map's own top-left corner (a child widget positioned via `move()`/`raise_()` over the map canvas, or a `QDockWidget`-style floating panel — match whatever floating-panel pattern this codebase already uses elsewhere, if any; otherwise the simplest correct approach is a semi-transparent child `QFrame` parented to the map widget itself, positioned in `resizeEvent`). Confirm an opacity slider control already exists somewhere in this dashboard (grep for `QSlider` near the map code) and make it visible in this floating panel if it was previously hidden/unreachable.

- [ ] **Step 4: Fix the AWCI SCALE legend clipping**

Read the legend widget's current size constraints; remove whatever fixed width/height is causing the reference image's full legend to be cut off (e.g. increase a `setFixedWidth`/`setMaximumWidth` or switch to `setMinimumWidth` + Preferred size policy).

- [ ] **Step 5: Add a play/timeline transport row beneath the map**

Add a `QHBoxLayout` row beneath the map (or as part of the Map Layers panel/map footer, whichever placement most closely matches the reference image) containing: a play/pause button, a scrubber (`QSlider`) tied to the SAME real Valid Time value already driving the rest of the dashboard (do not invent a second time-control mechanism — connect this new scrubber to the existing Valid Time slider's value, either by making them the same widget instance reused here or by keeping them synchronized via signals), and a "Live Data" indicator label reflecting whatever real freshness/tier state this dashboard already tracks (reuse the existing `DEMO MODE`/tier-badge convention rather than fabricating a new "live" claim when in demo mode — an honest label here might read "Demo Data" instead of "Live Data" when the active tier is demo; use your judgment on the honest wording, consistent with this dashboard's own established disclosure conventions).

- [ ] **Step 6: Write/extend tests** asserting: the filter selectors are no longer children of the top bar widget but of the new filter row; Layers/Settings buttons exist and are connected; the map widget's size policy/stretch factor changed; the new transport row's scrubber genuinely drives the same Valid Time value (moving it changes displayed data, mirroring Task 3's own real-value-changes-with-slider test pattern).

- [ ] **Step 7: Visual check**

Launch `AWCIDashboardWindow` offscreen, `.refresh()`, screenshot, and visually compare the filter bar + hero map region against the reference image — confirm it's now materially closer (do not require pixel-perfection in this single task; the final Task 10 does the full section-by-section re-audit).

- [ ] **Step 8: Run the full GUI suite to check for regressions**

```bash
source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/ -q
```

- [ ] **Step 9: Commit**

```bash
git add src/acf/gui/dashboard/awci_dashboard.py tests/gui/
git commit -m "feat(awci): filter bar as its own row, hero map resized/repositioned toward the reference layout

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 9: Layout — right column repositioning and second-row card fidelity

**Files:**
- Modify: `src/acf/gui/dashboard/awci_dashboard.py` (`_build_ui()`, the row containing Current Situation/Model Agreement/Airport Complexity, and the second row containing Vertical Cross Section/Atmospheric Profile/Flight Route Analysis/AWCI Vertical Profile)
- Test: `tests/gui/test_awci_dashboard_reference_parity.py` or equivalent

**Interfaces:**
- Consumes: the existing `AWCISituationPanel`/equivalent (Current Situation, Model Agreement, Airport Complexity), and the existing Vertical Cross Section / Atmospheric Profile / Flight Route Analysis / AWCI Vertical Profile widgets — all already real and tested; this task re-parents and resizes them, it does not rewrite their internals.

- [ ] **Step 1: Read the current row containing Current Situation/Model Agreement/Airport Complexity in full**, and the current second row.

```bash
grep -n "situation_panel\|Current Situation\|Model Agreement\|Airport Complexity" src/acf/gui/dashboard/awci_dashboard.py
grep -n "Vertical Cross Section\|Atmospheric Profile\|Flight Route Analysis\|AWCI Vertical Profile" src/acf/gui/dashboard/awci_dashboard.py
```

- [ ] **Step 2: Move Current Situation/Model Agreement/Airport Complexity into a narrower right column beside the hero map**

Restructure the layout so the row containing the hero map (Task 8) and this right column share one `QHBoxLayout` (map at ~65% stretch, right column at ~35% stretch, or whatever ratio matches the reference image), instead of the right column rendering as a full-width row above the map. This is the most structurally significant change in this plan — read the plan's own spec docstring (Task 7's disclosed decision in the ORIGINAL implementation, `awci_dashboard.py:1152-1158`, explaining why this wasn't done originally: preserving already-tested panels rather than a risky full teardown) and proceed carefully, preserving every existing signal/slot connection on these widgets — only their PARENT/layout position changes, not their internals.

- [ ] **Step 3: Un-clip Vertical Cross Section and Atmospheric Profile card titles**

Read why their titles currently truncate (a fixed card width too narrow for the real title text) and widen/adjust accordingly.

- [ ] **Step 4: Bring Flight Route Analysis and AWCI Vertical Profile closer to the reference presentation**

For Flight Route Analysis: if a route mini-map widget already exists elsewhere in this codebase (check the abandoned `awci-dashboard-rebuild` branch's own recovered `AWCIRouteChart`/`awci_route_chart.py` for a reusable pattern, or this file's own existing route-map code used elsewhere on this same dashboard) and it isn't currently used in this card, wire it in alongside the existing segment table; add a "Critical Zone" callout (a small colored banner) when a real segment along the route crosses into a High/Severe classification, using the same `_level_for_score`-style real threshold already established elsewhere in this dashboard.

For AWCI Vertical Profile: if an altitude/AWCI colour-chip table view already exists elsewhere (check `awci_vertical_profile.py` for a reusable table-rendering method) and isn't currently used in this card's presentation, wire it in instead of (or alongside) the current bar chart.

Use your judgment on scope here — if either of these two sub-fixes turns out to require substantially more than a targeted re-wiring of already-existing code (e.g. no reusable route-map/table code exists anywhere and building one from scratch would be a multi-hour task), STOP and report this as a finding for the ledger rather than improvising a large new component; a documented, disclosed gap is preferable to a rushed low-quality addition.

- [ ] **Step 5: Write/extend tests** covering the right column's new parent/layout position and any card content changes made in Steps 3-4.

- [ ] **Step 6: Visual check + full suite**

```bash
source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/ -q
```

- [ ] **Step 7: Commit**

```bash
git add src/acf/gui/dashboard/awci_dashboard.py tests/gui/
git commit -m "feat(awci): move Current Situation/Model Agreement/Airport Complexity to the right column, improve second-row card fidelity

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 10: Full verification pass

**Files:** none created; verification only.

- [ ] **Step 1: Run the full GUI test suite**

```bash
source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/ -v
```

Expected: all pass, 452+ (this plan's own new/corrected tests included).

- [ ] **Step 2: Run the full repo test suite**

```bash
source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest -q
```

Expected: no new failures/errors versus this branch's own clean baseline.

- [ ] **Step 3: Re-run the same section-by-section visual audit used before this plan started**

Launch `AWCIDashboardWindow` offscreen, `.refresh()`, screenshot, and compare against the reference image region-by-region (top bar, sidebar, filter bar, gauge row, hero map + layers/2D-3D-4D/transport, right column, second row × 4 cards, AWCI Vertical Profile, bottom row) — produce an honest, updated count of how many of the ~14 reference regions are now correctly placed, and disclose any region still not fully matched rather than rounding up.

- [ ] **Step 4: Re-run the real-data honesty spot-checks** from the original audit (Visibility/Ceiling no longer constant; component detail badge no longer fabricates REAL; Time Evolution values genuinely change with Valid Time; Model Agreement headline honest; Real Physics confidence honest; missing module scores render honestly) — confirm each is genuinely fixed by driving the real dashboard, not just by re-reading the diffs.

- [ ] **Step 5: Commit any final small fixes surfaced by this pass**

```bash
git add -A
git commit -m "fix(awci): address final verification findings

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```
