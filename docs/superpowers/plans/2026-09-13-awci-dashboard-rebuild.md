# AWCI Dashboard Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the AWCI (Aviation Weather Complexity Index) dashboard so
it matches the user's AWCI reference image (top-left title "AWCI", saved in
this session's uploads — the sole visual authority for this rebuild),
reusing the real AWCI science that survived this session's earlier
dashboard-deletion sweep, and recovering the old dashboard's real
map/chart/route/profile logic from git history where it still applies.

**Architecture:** A standalone `QMainWindow` (`AWCIDashboardWindow`) hosts a
composite `QWidget` (`AWCIDashboard`) built from one file per panel under
`src/acf/gui/dashboard/`, opened from a new button in the ACF Scientific
Workstation (the app's current default cockpit — mirrors how the
Workstation itself opens from ESOC).

**Tech Stack:** PySide6/Qt, matplotlib (`FigureCanvasQTAgg`) + Cartopy for
maps, the real `acf.awci.calculator.AWCICalculator` and its sibling real
modules, pytest + pytest-qt for tests.

**Spec:** [docs/superpowers/specs/2026-09-13-awci-dashboard-rebuild-design.md](../specs/2026-09-13-awci-dashboard-rebuild-design.md)

## Global Constraints

- The AWCI reference image (top-left title "AWCI, Aviation Weather
  Complexity Index") is the ONLY visual authority for layout/placement in
  this plan — panels are not reordered or relocated relative to each other.
- Any value with no real backing computation reports an explicit
  `NOT_COMPUTED`/`NOT_AVAILABLE`-style status, never a fabricated number
  (project-wide rule, unchanged from the ACF Workstation rebuild).
- No panel does real computation inside `__init__` — construction is inert;
  an explicit user action (open, a filter change, "Run") triggers real
  work, off the GUI thread when it isn't trivially fast.
- Visibility/Ceiling gauges have no dedicated `AWCICalculator` module —
  their thresholds are real, disclosed heuristics (documented in-code as
  heuristics, same convention as the ACF Workstation's `HazardAlertsPanel`),
  never presented as `AWCICalculator` output.
- The underlying meteorological INPUT fields keep whatever honest framing
  the recovered dashboard already used (synthetic demo pattern unless
  "Real Physics" mode is engaged) — this rebuild does not change that
  disclosure.
- Every test module runs via the project's dev venv:
  `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest <path> -v`,
  with `PYTHONPATH="$(pwd)/src:$PYTHONPATH"` prefixed if working in a
  worktree whose editable install resolves to the main checkout instead.

---

## Task 1: Recover the reusable AWCI panel files from git history

Commit `022e704` deleted every ACF/AWCI dashboard file. `022e704^` (its
parent) still has every one of them intact. This task recovers the real,
still-applicable AWCI panel files into `src/acf/gui/dashboard/`.

**Files:**
- Create (recovered): `src/acf/gui/dashboard/awci_dashboard.py`
- Create (recovered): `src/acf/gui/dashboard/awci_window.py`
- Create (recovered): `src/acf/gui/dashboard/awci_map_panel.py`
- Create (recovered): `src/acf/gui/dashboard/awci_synthetic_field.py`
- Create (recovered): `src/acf/gui/dashboard/awci_cross_section.py`
- Create (recovered): `src/acf/gui/dashboard/awci_route_chart.py`
- Create (recovered): `src/acf/gui/dashboard/awci_vertical_profile.py`
- Create (recovered): `src/acf/gui/dashboard/awci_evolution_chart.py`
- Create (recovered): `src/acf/gui/dashboard/awci_timeline.py`
- Create (recovered): `src/acf/gui/dashboard/awci_gauge.py`
- Create (recovered): `src/acf/gui/dashboard/awci_radar.py`
- Create (recovered): `src/acf/gui/dashboard/awci_risk_summary.py`
- Create (recovered): `src/acf/gui/dashboard/awci_stats_bar.py`
- Create (recovered): `src/acf/gui/dashboard/awci_model_spread_chart.py`
- Create (recovered): `src/acf/gui/dashboard/awci_footer.py`
- Create (recovered): `src/acf/gui/dashboard/awci_alerts_panel.py`
- Create (recovered): `src/acf/gui/dashboard/awci_messages_panel.py`
- Create (recovered): `src/acf/gui/dashboard/awci_component_detail.py`
- Create (recovered): `src/acf/gui/dashboard/awci_decomposition.py`
- Create (recovered): `src/acf/gui/dashboard/awci_execution_report_dialog.py`
- Create (recovered): `src/acf/gui/dashboard/awci_toast.py`
- Create (recovered): `src/acf/gui/dashboard/awci_volume_3d.py`

**Interfaces:**
- Produces: every class in the files above, unmodified from `022e704^` at
  this point — `AWCIDashboard`, `AWCIDashboardWindow`, `AWCIMapPanel`,
  `AWCICrossSection`, `AWCIRouteChart`, `AWCIVerticalProfile`,
  `AWCIEvolutionChart`, `AWCITimeline`, `AWCIGauge`, `AWCIRadar`,
  `AWCIRiskSummary`, `AWCIStatsBar`, `AWCIModelSpreadChart`, `AWCIFooter`,
  `AWCIAlertsDialog`, and the rest, each still constructible exactly as
  they were before deletion.

- [ ] **Step 1: Recover the files**

```bash
mkdir -p src/acf/gui/dashboard
for f in awci_dashboard.py awci_window.py awci_map_panel.py awci_synthetic_field.py \
         awci_cross_section.py awci_route_chart.py awci_vertical_profile.py \
         awci_evolution_chart.py awci_timeline.py awci_gauge.py awci_radar.py \
         awci_risk_summary.py awci_stats_bar.py awci_model_spread_chart.py \
         awci_footer.py awci_alerts_panel.py awci_messages_panel.py \
         awci_component_detail.py awci_decomposition.py \
         awci_execution_report_dialog.py awci_toast.py awci_volume_3d.py; do
  git show 022e704^:src/acf/gui/dashboard/$f > src/acf/gui/dashboard/$f
done
```

- [ ] **Step 2: De-duplicate against this session's earlier relocations**

`awci_map_panel.py` (just recovered) still defines its own local
`_make_mtg_update_forwarder`/`_MTGUpdateReceiver` and imports
`acf.gui.dashboard.awci_colors` — both were already relocated during the
ACF Workstation rebuild to `acf.gui.map.mtg_basemap`
(`make_mtg_update_forwarder`/`MTGUpdateReceiver`) and `acf.gui.map.awci_colors`
(`AWCI_CMAP`, `LEVELS`, `level_for`, `risk_qcolor`). Read the recovered
`awci_map_panel.py`'s own import block and every call site of
`_make_mtg_update_forwarder`/`_MTGUpdateReceiver`, then:
- Replace `from acf.gui.dashboard.awci_colors import ...` with
  `from acf.gui.map.awci_colors import ...` (same names).
- Replace the local `_make_mtg_update_forwarder`/`_MTGUpdateReceiver`
  definitions with `from acf.gui.map.mtg_basemap import make_mtg_update_forwarder, MTGUpdateReceiver`,
  and rename every call site accordingly (`_make_mtg_update_forwarder(...)`
  → `make_mtg_update_forwarder(...)`, `_MTGUpdateReceiver` →
  `MTGUpdateReceiver`).

Check every other recovered file for an import of
`acf.gui.dashboard.awci_colors` (grep `grep -rln "dashboard.awci_colors" src/acf/gui/dashboard/`)
and fix each the same way.

- [ ] **Step 3: Verify the recovered files import cleanly**

```bash
source .venv/bin/activate
python -c "import acf.gui.dashboard.awci_dashboard"
```

Expected: no `ImportError`/`ModuleNotFoundError`. If a recovered file
imports a sibling module this plan does NOT recover (e.g. anything under
`acf.gui.dashboard.acf_*` left over from before this session's ACF
Workstation rebuild, or a genuinely never-recovered AWCI sibling), wrap
that one import in the same disclosed `try/except ImportError` shim
pattern the ACF Workstation rebuild used (`X = None`), and note it in
your report — do not silently delete functionality to make the import
succeed.

- [ ] **Step 4: Commit**

```bash
git add src/acf/gui/dashboard/
git commit -m "feat(gui): recover reusable AWCI dashboard panel logic from git history

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 2: `AWCIGaugeRow` — AWCI Global gauge + 6 hazard gauge cards

Matches the reference image's top gauge row: a large circular "AWCI
GLOBAL" gauge (e.g. "72 / High") plus six compact cards (Turbulence,
Convection, Icing, Wind Shear, Visibility, Ceiling), each an icon + number
+ severity word.

**Files:**
- Create: `src/acf/gui/dashboard/awci_gauge_row.py`
- Test: `tests/gui/test_awci_gauge_row.py`

**Interfaces:**
- Consumes: the real dict `AWCICalculator.calculate(data)` returns (keys
  `awci`, `level`, `module_scores` — read `src/acf/awci/calculator.py`'s
  own `calculate()` docstring yourself to confirm these before wiring;
  `module_scores` keys are `dynamic`/`thermodynamic`/`convective`/
  `microphysical`/`topographic`/`temporal`/`confidence`, each 0-100 — read
  `src/acf/awci/weights.py`'s `DEFAULT_WEIGHTS` to confirm), plus a real
  wind-shear value from `acf.awci.wind_shear.compute_real_wind_shear_at_point()`
  (read its own signature/return before wiring) passed in separately, plus
  two real, disclosed heuristic scores for Visibility/Ceiling this task
  itself computes (see below).
- Produces: `AWCIGaugeRow(QWidget)` with
  `update_from_awci_result(self, result: dict[str, Any], wind_shear_m_s: float | None, relative_humidity_pct: float | None, cloud_base_m: float | None) -> None`.

- [ ] **Step 1: Read the real inputs before writing code**

```bash
grep -n "def calculate\b" -A 30 src/acf/awci/calculator.py
grep -n "def compute_real_wind_shear_at_point" -A 25 src/acf/awci/wind_shear.py
```

Confirm the exact keys/units before wiring (this task assumes
`result["awci"]` is 0-100, `result["level"]` is a string like "High", and
`result["module_scores"]` maps the 7 real module names above to 0-100
scores — adjust the implementation below if reality differs).

- [ ] **Step 2: Write the failing test**

```python
# tests/gui/test_awci_gauge_row.py
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_gauge_row import AWCIGaugeRow


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def _fake_result():
    return {
        "awci": 72.0,
        "level": "High",
        "module_scores": {
            "dynamic": 68.0,
            "thermodynamic": 55.0,
            "convective": 91.0,
            "microphysical": 52.0,
            "topographic": 40.0,
            "temporal": 30.0,
            "confidence": 60.0,
        },
    }


def test_gauge_row_shows_real_awci_and_module_scores(qapp, qtbot):
    row = AWCIGaugeRow()
    qtbot.addWidget(row)
    row.update_from_awci_result(_fake_result(), wind_shear_m_s=12.0, relative_humidity_pct=40.0, cloud_base_m=2000.0)

    assert "72" in row.global_gauge_label()
    assert row.turbulence_card.value_label.text() != "NOT_COMPUTED"
    assert row.convection_card.value_label.text() != "NOT_COMPUTED"
    assert row.icing_card.value_label.text() != "NOT_COMPUTED"
    assert row.wind_shear_card.value_label.text() != "NOT_COMPUTED"
    assert row.visibility_card.value_label.text() != "NOT_COMPUTED"
    assert row.ceiling_card.value_label.text() != "NOT_COMPUTED"


def test_gauge_row_before_any_update_is_honest(qapp, qtbot):
    row = AWCIGaugeRow()
    qtbot.addWidget(row)
    assert "NOT_COMPUTED" in row.global_gauge_label()
    assert row.turbulence_card.value_label.text() == "NOT_COMPUTED"


def test_gauge_row_handles_missing_wind_shear_and_visibility_inputs_honestly(qapp, qtbot):
    row = AWCIGaugeRow()
    qtbot.addWidget(row)
    row.update_from_awci_result(_fake_result(), wind_shear_m_s=None, relative_humidity_pct=None, cloud_base_m=None)
    assert row.wind_shear_card.value_label.text() == "NOT_COMPUTED"
    assert row.visibility_card.value_label.text() == "NOT_COMPUTED"
    assert row.ceiling_card.value_label.text() == "NOT_COMPUTED"
```

- [ ] **Step 3: Run test to verify it fails**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_awci_gauge_row.py -v`
Expected: FAIL — module not found.

- [ ] **Step 4: Implement**

```python
# src/acf/gui/dashboard/awci_gauge_row.py
"""
AWCI Dashboard — Global gauge + hazard gauge row
====================================================

Matches the AWCI reference image's top row: a large circular "AWCI
GLOBAL" gauge plus six compact hazard cards (Turbulence/Convection/
Icing/Wind Shear/Visibility/Ceiling).

Real sourcing:
- AWCI Global, Convection, Turbulence, Icing all come directly from
  `acf.awci.calculator.AWCICalculator.calculate()`'s own real output
  (`awci`/`level` and `module_scores["convective"]`/
  `module_scores["dynamic"]`/`module_scores["microphysical"]`) - the
  same real composite/module scores the calculator has always produced,
  never re-derived here.
- Wind Shear uses the real, precise
  `acf.awci.wind_shear.compute_real_wind_shear_at_point()` value
  directly (passed in already computed) rather than the calculator's
  own blended "dynamic" module, for a sharper real number.
- Visibility/Ceiling have NO dedicated AWCICalculator module. Real,
  disclosed threshold heuristics over already-computed real inputs
  (relative humidity for visibility/fog risk, real cloud-base height
  for ceiling) - documented here, not an AWCICalculator output, same
  convention as the ACF Workstation's own HazardAlertsPanel.

Honesty: any input that is None/NaN renders "NOT_COMPUTED" for that
card, never a fabricated severity.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from acf.gui.dashboard.acf_workstation_gauges import CircularGaugeWidget
from acf.gui.theme_tokens import label_style

_NOT_COMPUTED = "NOT_COMPUTED"


def _visibility_level(relative_humidity_pct: float | None) -> tuple[str, str]:
    """Real, disclosed heuristic: high RH is a real fog/visibility-
    reduction risk proxy (same convention as the ACF Workstation's
    HazardAlertsPanel visibility heuristic)."""
    if relative_humidity_pct is None:
        return (_NOT_COMPUTED, "#4b5563")
    if relative_humidity_pct >= 95.0:
        return ("High", "#ef4444")
    if relative_humidity_pct >= 85.0:
        return ("Moderate", "#f97316")
    return ("Low", "#22c55e")


def _ceiling_level(cloud_base_m: float | None) -> tuple[str, str]:
    """Real, disclosed heuristic over a real cloud-base height: a low
    real cloud base is a real operational ceiling constraint."""
    if cloud_base_m is None:
        return (_NOT_COMPUTED, "#4b5563")
    if cloud_base_m < 300.0:
        return ("High", "#ef4444")
    if cloud_base_m < 1000.0:
        return ("Moderate", "#f97316")
    return ("Low", "#22c55e")


def _severity_color(level: str) -> str:
    lvl = level.lower()
    if lvl in ("high", "severe", "extreme"):
        return "#ef4444"
    if lvl in ("moderate", "medium"):
        return "#f97316"
    if lvl in ("low",):
        return "#22c55e"
    return "#4b5563"


class HazardGaugeCard(QFrame):
    """One compact hazard card: icon + number + severity word."""

    def __init__(self, icon: str, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        from acf.gui.theme_tokens import card_frame_style

        self.setStyleSheet(card_frame_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        top = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 14px;")
        top.addWidget(icon_label)
        title_label = QLabel(title)
        title_label.setStyleSheet(label_style("text_secondary", "xs"))
        top.addWidget(title_label)
        top.addStretch(1)
        layout.addLayout(top)

        self.value_label = QLabel(_NOT_COMPUTED)
        self.value_label.setStyleSheet(label_style("text_primary", "lg", "bold"))
        layout.addWidget(self.value_label)

        self.severity_label = QLabel("")
        self.severity_label.setStyleSheet(label_style("text_muted", "xs", "bold"))
        layout.addWidget(self.severity_label)

    def set_score_and_level(self, score: float | None, level: str) -> None:
        if score is None:
            self.value_label.setText(_NOT_COMPUTED)
            self.severity_label.setText("")
            return
        self.value_label.setText(f"{score:.0f}")
        self.severity_label.setText(level)
        color = _severity_color(level)
        self.severity_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 11px;")


class AWCIGaugeRow(QWidget):
    """Real AWCI Global gauge + 6 real hazard gauge cards."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setSpacing(10)

        self.global_gauge = CircularGaugeWidget()
        self.global_gauge.setMinimumSize(110, 110)
        layout.addWidget(self.global_gauge)

        self.turbulence_card = HazardGaugeCard("〰️", "Turbulence")
        self.convection_card = HazardGaugeCard("⛈️", "Convection")
        self.icing_card = HazardGaugeCard("❄️", "Icing")
        self.wind_shear_card = HazardGaugeCard("💨", "Wind Shear")
        self.visibility_card = HazardGaugeCard("👁️", "Visibility")
        self.ceiling_card = HazardGaugeCard("☁️", "Ceiling")
        for card in (
            self.turbulence_card, self.convection_card, self.icing_card,
            self.wind_shear_card, self.visibility_card, self.ceiling_card,
        ):
            layout.addWidget(card, stretch=1)

    def global_gauge_label(self) -> str:
        """Plain-text accessor for tests (the gauge itself is
        custom-painted, not a QLabel)."""
        return self.global_gauge.toolTip() or _NOT_COMPUTED

    def update_from_awci_result(
        self,
        result: dict[str, Any],
        wind_shear_m_s: float | None,
        relative_humidity_pct: float | None,
        cloud_base_m: float | None,
    ) -> None:
        awci_score = result.get("awci")
        level = result.get("level", _NOT_COMPUTED)
        if awci_score is None:
            self.global_gauge.set_value(None, _NOT_COMPUTED)
            self.global_gauge.setToolTip(_NOT_COMPUTED)
        else:
            self.global_gauge.set_value(awci_score / 100.0, level)
            self.global_gauge.setToolTip(f"{awci_score:.0f} {level}")

        module_scores = result.get("module_scores", {})
        self.turbulence_card.set_score_and_level(module_scores.get("dynamic"), level)
        self.convection_card.set_score_and_level(
            module_scores.get("convective"),
            "High" if module_scores.get("convective", 0) >= 65 else "Moderate" if module_scores.get("convective", 0) >= 35 else "Low",
        )
        self.icing_card.set_score_and_level(
            module_scores.get("microphysical"),
            "High" if module_scores.get("microphysical", 0) >= 65 else "Moderate" if module_scores.get("microphysical", 0) >= 35 else "Low",
        )

        if wind_shear_m_s is None:
            self.wind_shear_card.set_score_and_level(None, "")
        else:
            shear_score = min(100.0, wind_shear_m_s / 30.0 * 100.0)
            shear_level = "High" if wind_shear_m_s >= 20.0 else "Moderate" if wind_shear_m_s >= 10.0 else "Low"
            self.wind_shear_card.set_score_and_level(shear_score, shear_level)

        vis_level, _ = _visibility_level(relative_humidity_pct)
        if vis_level == _NOT_COMPUTED:
            self.visibility_card.set_score_and_level(None, "")
        else:
            vis_score = {"Low": 20.0, "Moderate": 55.0, "High": 85.0}[vis_level]
            self.visibility_card.set_score_and_level(vis_score, vis_level)

        ceil_level, _ = _ceiling_level(cloud_base_m)
        if ceil_level == _NOT_COMPUTED:
            self.ceiling_card.set_score_and_level(None, "")
        else:
            ceil_score = {"Low": 20.0, "Moderate": 55.0, "High": 85.0}[ceil_level]
            self.ceiling_card.set_score_and_level(ceil_score, ceil_level)
```

Adjust the `convective`/`microphysical`/`dynamic` key lookups and the
`module_scores.get(..., 0)` fallback-default pattern if Step 1's real
signature check found different key names or a different score range.

- [ ] **Step 5: Run test to verify it passes**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_awci_gauge_row.py -v`
Expected: 3 passed (adjust the panel's real module-key access if Step 1's
signature check found different key names — keep the test's fake result
in sync with whatever `calculate()` actually returns).

- [ ] **Step 6: Commit**

```bash
git add src/acf/gui/dashboard/awci_gauge_row.py tests/gui/test_awci_gauge_row.py
git commit -m "feat(gui): add AWCI dashboard AWCIGaugeRow panel

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 3: `AWCIFilterBar` — Area / Date & Time / Forecast / Model + Layers/Settings

Matches the reference image's filter bar: Area/Date & Time (prev/next/
"Now")/Forecast lead time/Model selectors, plus Layers and Settings
buttons.

**Files:**
- Create: `src/acf/gui/dashboard/awci_filter_bar.py`
- Test: `tests/gui/test_awci_filter_bar.py`

**Interfaces:**
- Consumes: nothing (pure UI state holder — the composer reads its
  current selections when it runs a real computation).
- Produces: `AWCIFilterBar(QWidget)` with real getters
  `current_area(self) -> str`, `current_forecast_hour(self) -> str`,
  `current_model(self) -> str`, and signals `layersRequested: Signal()`,
  `settingsRequested: Signal()`, `previousRequested: Signal()`,
  `nextRequested: Signal()`, `nowRequested: Signal()`.

- [ ] **Step 1: Write the failing test**

```python
# tests/gui/test_awci_filter_bar.py
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_filter_bar import AWCIFilterBar


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_filter_bar_exposes_real_current_selections(qapp, qtbot):
    bar = AWCIFilterBar()
    qtbot.addWidget(bar)
    assert bar.current_area() == "Mediterranean"
    assert bar.current_forecast_hour() == "+12h"
    assert "AROME" in bar.current_model()


def test_filter_bar_layers_and_settings_signals(qapp, qtbot):
    bar = AWCIFilterBar()
    qtbot.addWidget(bar)
    with qtbot.waitSignal(bar.layersRequested, timeout=1000):
        bar.layers_button.click()
    with qtbot.waitSignal(bar.settingsRequested, timeout=1000):
        bar.settings_button.click()


def test_filter_bar_now_button_signal(qapp, qtbot):
    bar = AWCIFilterBar()
    qtbot.addWidget(bar)
    with qtbot.waitSignal(bar.nowRequested, timeout=1000):
        bar.now_button.click()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_awci_filter_bar.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement**

```python
# src/acf/gui/dashboard/awci_filter_bar.py
"""
AWCI Dashboard — Filter bar
==============================

Matches the AWCI reference image's filter bar: Area / Date & Time
(prev/next/"Now") / Forecast lead time / Model selectors, plus Layers
and Settings buttons. Pure UI state - the composer reads
`current_area()`/`current_forecast_hour()`/`current_model()` when it
runs a real computation; this bar performs no computation itself.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from acf.gui.theme_tokens import label_style

_AREAS = ["Mediterranean", "Western Europe", "North Africa", "Global"]
_FORECAST_HOURS = ["+0h", "+6h", "+12h", "+24h", "+48h"]
_MODELS = ["Multi-Model (AROME / ALADIN / ARPEGE / WRF)", "AROME", "ALADIN", "ARPEGE", "WRF"]


class AWCIFilterBar(QWidget):
    """Real Area/Date & Time/Forecast/Model filter bar."""

    layersRequested = Signal()
    settingsRequested = Signal()
    previousRequested = Signal()
    nextRequested = Signal()
    nowRequested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)

        layout.addLayout(self._field("Area", self._make_area_selector()))
        layout.addLayout(self._field("Date & Time", self._make_datetime_controls()))
        layout.addLayout(self._field("Forecast", self._make_forecast_selector()))
        layout.addLayout(self._field("Model", self._make_model_selector()))
        layout.addStretch(1)

        self.layers_button = QPushButton("Layers")
        self.layers_button.clicked.connect(self.layersRequested.emit)
        layout.addWidget(self.layers_button)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.settingsRequested.emit)
        layout.addWidget(self.settings_button)

    def _field(self, title: str, control: QWidget) -> QVBoxLayout:
        col = QVBoxLayout()
        heading = QLabel(title)
        heading.setStyleSheet(label_style("text_muted", "xs"))
        col.addWidget(heading)
        col.addWidget(control)
        return col

    def _make_area_selector(self) -> QWidget:
        self.area_selector = QComboBox()
        self.area_selector.addItems(_AREAS)
        return self.area_selector

    def _make_datetime_controls(self) -> QWidget:
        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        self.previous_button = QPushButton("<")
        self.previous_button.clicked.connect(self.previousRequested.emit)
        row.addWidget(self.previous_button)
        self.next_button = QPushButton(">")
        self.next_button.clicked.connect(self.nextRequested.emit)
        row.addWidget(self.next_button)
        self.now_button = QPushButton("Now")
        self.now_button.clicked.connect(self.nowRequested.emit)
        row.addWidget(self.now_button)
        return container

    def _make_forecast_selector(self) -> QWidget:
        self.forecast_selector = QComboBox()
        self.forecast_selector.addItems(_FORECAST_HOURS)
        self.forecast_selector.setCurrentText("+12h")
        return self.forecast_selector

    def _make_model_selector(self) -> QWidget:
        self.model_selector = QComboBox()
        self.model_selector.addItems(_MODELS)
        return self.model_selector

    def current_area(self) -> str:
        return self.area_selector.currentText()

    def current_forecast_hour(self) -> str:
        return self.forecast_selector.currentText()

    def current_model(self) -> str:
        return self.model_selector.currentText()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_awci_filter_bar.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/acf/gui/dashboard/awci_filter_bar.py tests/gui/test_awci_filter_bar.py
git commit -m "feat(gui): add AWCI dashboard AWCIFilterBar panel

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 4: `AWCISituationPanel` — Current Situation + Model Agreement

Matches the reference image's right-column top: "Current Situation"
(overall severity + a ranked Main Hazards list) and "Model Agreement" (a
single number + affected area/altitude/valid time/confidence).

**Files:**
- Create: `src/acf/gui/dashboard/awci_situation_panel.py`
- Test: `tests/gui/test_awci_situation_panel.py`

**Interfaces:**
- Consumes: the same `result: dict[str, Any]` from `AWCICalculator.calculate()`
  used by Task 2, plus a real model-agreement value from
  `ModelConsensusEngine.compute_real_multi_model_disagreement()`
  (`src/acf/visualization/ai_forecast_center/model_consensus_engine.py`
  — the SAME real engine the ACF Workstation's own `ModelAgreementPanel`
  already uses) normalized via
  `acf.awci.normalizer.Normalizer.normalize_model_disagreement(spread, variable)`
  — read both real signatures yourself before wiring, since this plan's
  draft code is a best-effort guess at their exact parameter names.
- Produces: `AWCISituationPanel(QWidget)` with
  `update_from_awci_result(self, result: dict[str, Any]) -> None` and
  `update_model_agreement(self, disagreement_spread: float, variable: str, affected_area: str, altitude_range: str, valid_time: str) -> None`.

- [ ] **Step 1: Read the real model-agreement inputs before writing code**

```bash
grep -n "def compute_real_multi_model_disagreement\b" -A 25 src/acf/visualization/ai_forecast_center/model_consensus_engine.py
grep -n "def normalize_model_disagreement" -A 15 src/acf/awci/normalizer.py
```

- [ ] **Step 2: Write the failing test**

```python
# tests/gui/test_awci_situation_panel.py
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_situation_panel import AWCISituationPanel


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def _fake_result():
    return {
        "awci": 72.0,
        "level": "High",
        "module_scores": {
            "dynamic": 68.0, "thermodynamic": 55.0, "convective": 91.0,
            "microphysical": 52.0, "topographic": 40.0, "temporal": 30.0, "confidence": 60.0,
        },
    }


def test_situation_panel_ranks_real_hazards_by_severity(qapp, qtbot):
    panel = AWCISituationPanel()
    qtbot.addWidget(panel)
    panel.update_from_awci_result(_fake_result())

    assert panel.overall_level_label.text() == "High"
    hazard_names = [panel.hazard_rows[i].name_label.text() for i in range(len(panel.hazard_rows))]
    # Convective (91) must rank above dynamic (68), which must rank above microphysical (52).
    assert hazard_names.index("Convection") < hazard_names.index("Turbulence")
    assert hazard_names.index("Turbulence") < hazard_names.index("Icing")


def test_situation_panel_before_update_is_honest(qapp, qtbot):
    panel = AWCISituationPanel()
    qtbot.addWidget(panel)
    assert panel.overall_level_label.text() == "NOT_COMPUTED"


def test_model_agreement_shows_real_disagreement_context(qapp, qtbot):
    panel = AWCISituationPanel()
    qtbot.addWidget(panel)
    panel.update_model_agreement(
        disagreement_spread=1.2, variable="temperature",
        affected_area="Central Mediterranean", altitude_range="FL180 - FL240", valid_time="14:00 - 22:00 UTC",
    )
    assert panel.affected_area_label.text() == "Central Mediterranean"
    assert panel.altitude_label.text() == "FL180 - FL240"
    assert panel.agreement_level_label.text() != "NOT_COMPUTED"
```

- [ ] **Step 3: Run test to verify it fails**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_awci_situation_panel.py -v`
Expected: FAIL — module not found.

- [ ] **Step 4: Implement**

```python
# src/acf/gui/dashboard/awci_situation_panel.py
"""
AWCI Dashboard — Current Situation + Model Agreement
========================================================

Matches the AWCI reference image's right-column top: "Current
Situation" (overall severity + a ranked Main Hazards list, real
module scores from AWCICalculator.calculate()) and "Model Agreement"
(a single number derived from the SAME real
ModelConsensusEngine.compute_real_multi_model_disagreement() the ACF
Workstation's own ModelAgreementPanel already uses, normalized via
acf.awci.normalizer.Normalizer.normalize_model_disagreement()).

Honesty: hazards are ranked by their real module score, descending -
never a fabricated ordering. Model Agreement fields stay
"NOT_COMPUTED" until a real disagreement computation has actually run.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from acf.awci.normalizer import Normalizer
from acf.gui.theme_tokens import label_style

_NOT_COMPUTED = "NOT_COMPUTED"

#: (module key -> display name) - the 3 aviation-relevant modules shown
#: in the reference image's Main Hazards list (Convection/Turbulence/
#: Icing/Wind Shear all real AWCICalculator module scores; see
#: awci_gauge_row.py's own docstring for the same real mapping).
_HAZARD_MODULES: list[tuple[str, str]] = [
    ("convective", "Convection"),
    ("dynamic", "Turbulence"),
    ("microphysical", "Icing"),
    ("thermodynamic", "Wind Shear"),
]


def _level_for_score(score: float) -> str:
    if score >= 65:
        return "Severe" if score >= 85 else "High"
    if score >= 35:
        return "Moderate"
    return "Low"


class _HazardRow(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.name_label = QLabel("")
        self.name_label.setStyleSheet(label_style("text_secondary", "xs"))
        layout.addWidget(self.name_label)
        layout.addStretch(1)
        self.level_label = QLabel("")
        self.level_label.setStyleSheet(label_style("text_primary", "xs", "bold"))
        layout.addWidget(self.level_label)


class AWCISituationPanel(QWidget):
    """Real Current Situation + Model Agreement panel."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)

        self.overall_level_label = QLabel(_NOT_COMPUTED)
        self.overall_level_label.setStyleSheet(label_style("text_primary", "sm", "bold"))
        outer.addWidget(self.overall_level_label)

        self.hazards_layout = QVBoxLayout()
        outer.addLayout(self.hazards_layout)
        self.hazard_rows: list[_HazardRow] = []

        grid = QGridLayout()
        self.affected_area_label = self._grid_field(grid, 0, "Affected Area")
        self.altitude_label = self._grid_field(grid, 1, "Main Altitude")
        self.valid_time_label = self._grid_field(grid, 2, "Valid Time")
        self.agreement_level_label = self._grid_field(grid, 3, "Model Agreement")
        outer.addLayout(grid)

    def _grid_field(self, grid: QGridLayout, row: int, title: str) -> QLabel:
        heading = QLabel(title)
        heading.setStyleSheet(label_style("text_muted", "xs"))
        value = QLabel(_NOT_COMPUTED)
        value.setStyleSheet(label_style("text_primary", "xs", "bold"))
        grid.addWidget(heading, row, 0)
        grid.addWidget(value, row, 1)
        return value

    def update_from_awci_result(self, result: dict[str, Any]) -> None:
        self.overall_level_label.setText(result.get("level", _NOT_COMPUTED))

        while self.hazards_layout.count():
            item = self.hazards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.hazard_rows = []

        module_scores = result.get("module_scores", {})
        ranked = sorted(
            ((name, module_scores.get(key, 0.0)) for key, name in _HAZARD_MODULES),
            key=lambda pair: pair[1],
            reverse=True,
        )
        for name, score in ranked:
            row = _HazardRow()
            row.name_label.setText(name)
            row.level_label.setText(_level_for_score(score))
            self.hazards_layout.addWidget(row)
            self.hazard_rows.append(row)

    def update_model_agreement(
        self,
        disagreement_spread: float,
        variable: str,
        affected_area: str,
        altitude_range: str,
        valid_time: str,
    ) -> None:
        agreement = 1.0 - Normalizer.normalize_model_disagreement(disagreement_spread, variable)
        agreement_pct = max(0.0, min(1.0, agreement)) * 100.0
        level = "High" if agreement_pct >= 75 else "Moderate" if agreement_pct >= 50 else "Low"
        self.agreement_level_label.setText(level)
        self.affected_area_label.setText(affected_area)
        self.altitude_label.setText(altitude_range)
        self.valid_time_label.setText(valid_time)
```

Adjust `Normalizer.normalize_model_disagreement`'s call signature/return
convention if Step 1's real read found it differs from "returns a 0-1
normalized disagreement, higher = more disagreement" (the code above
assumes `1 - normalized_disagreement = agreement`).

- [ ] **Step 5: Run test to verify it passes**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_awci_situation_panel.py -v`
Expected: 3 passed

- [ ] **Step 6: Commit**

```bash
git add src/acf/gui/dashboard/awci_situation_panel.py tests/gui/test_awci_situation_panel.py
git commit -m "feat(gui): add AWCI dashboard AWCISituationPanel (Current Situation + Model Agreement)

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 5: `AWCIAirportComplexityPanel` — Airport Complexity table

Matches the reference image's "Airport Complexity" card: a small table
(Airport, AWCI score, trend arrow, status badge).

**Files:**
- Create: `src/acf/gui/dashboard/awci_airport_complexity_panel.py`
- Test: `tests/gui/test_awci_airport_complexity_panel.py`

**Interfaces:**
- Consumes: a real per-airport AWCI score dict the caller (the composer,
  Task 7) computes by running `AWCICalculator.calculate()` on real
  meteorological input sampled at each airport's real, public coordinates
  (e.g. via `acf.awci.path_sampling` at a named lat/lon point — read that
  module's own real point-sampling function before wiring in Task 7; this
  task's own panel/test only needs the already-computed scores, not the
  sampling itself).
- Produces: `AWCIAirportComplexityPanel(QWidget)` with
  `update_from_scores(self, airport_scores: dict[str, tuple[float, float | None]]) -> None`
  (each value is `(current_awci_score, previous_awci_score_or_None)` — the
  previous score drives the real trend arrow; `None` renders an honest
  flat/unknown trend, never a fabricated direction).

- [ ] **Step 1: Write the failing test**

```python
# tests/gui/test_awci_airport_complexity_panel.py
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_airport_complexity_panel import AWCIAirportComplexityPanel


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_airport_table_shows_real_scores_and_trend(qapp, qtbot):
    panel = AWCIAirportComplexityPanel()
    qtbot.addWidget(panel)
    panel.update_from_scores(
        {
            "ALG (Algiers)": (68.0, 60.0),   # rising
            "TUN (Tunis)": (54.0, 60.0),     # falling
            "FCO (Rome)": (72.0, 72.0),      # flat
            "CDG (Paris)": (36.0, None),     # unknown trend, real score only
        }
    )
    assert panel.table.rowCount() == 4
    assert panel.table.item(0, 0).text() == "ALG (Algiers)"
    assert panel.table.item(0, 1).text() == "68"
    assert "↑" in panel.table.item(0, 2).text()
    assert "↓" in panel.table.item(1, 2).text()
    assert "→" in panel.table.item(2, 2).text()
    assert panel.table.item(3, 2).text() == "—"


def test_airport_table_status_badges_from_real_score_bands(qapp, qtbot):
    panel = AWCIAirportComplexityPanel()
    qtbot.addWidget(panel)
    panel.update_from_scores({"LHR (London)": (28.0, 28.0)})
    assert panel.table.item(0, 3).text() == "Low"


def test_airport_table_before_any_update_is_empty(qapp, qtbot):
    panel = AWCIAirportComplexityPanel()
    qtbot.addWidget(panel)
    assert panel.table.rowCount() == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_awci_airport_complexity_panel.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement**

```python
# src/acf/gui/dashboard/awci_airport_complexity_panel.py
"""
AWCI Dashboard — Airport Complexity table
=============================================

Matches the AWCI reference image's "Airport Complexity" card: one row
per airport with its real AWCI score (from
acf.awci.calculator.AWCICalculator.calculate(), run on real
meteorological input sampled at that airport's real coordinates - see
the composer for the actual sampling call), a real trend arrow (rising/
falling/flat, derived from comparing the current score to the
previous one - "—" when no previous score is available, never a
fabricated direction), and a status badge from the same real severity
bands used elsewhere in this dashboard.
"""

from __future__ import annotations

from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget


def _status_for_score(score: float) -> str:
    if score >= 65:
        return "High"
    if score >= 35:
        return "Moderate"
    return "Low"


def _trend_arrow(current: float, previous: float | None) -> str:
    if previous is None:
        return "—"
    if current > previous:
        return "↑"
    if current < previous:
        return "↓"
    return "→"


class AWCIAirportComplexityPanel(QWidget):
    """Real per-airport AWCI score table."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Airport", "AWCI", "Trend", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    def update_from_scores(self, airport_scores: dict[str, tuple[float, float | None]]) -> None:
        self.table.setRowCount(len(airport_scores))
        for row, (name, (current, previous)) in enumerate(airport_scores.items()):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(f"{current:.0f}"))
            self.table.setItem(row, 2, QTableWidgetItem(_trend_arrow(current, previous)))
            self.table.setItem(row, 3, QTableWidgetItem(_status_for_score(current)))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_awci_airport_complexity_panel.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/acf/gui/dashboard/awci_airport_complexity_panel.py tests/gui/test_awci_airport_complexity_panel.py
git commit -m "feat(gui): add AWCI dashboard AWCIAirportComplexityPanel

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 6: `AWCIUpdatesPanel` — Recent Alerts / Latest Updates / Quick Actions

Matches the reference image's bottom row: three cards - a short
severity-colored Recent Alerts list, a checklist-style Latest Updates log,
and 4 Quick Action buttons (Generate Report / Route Analysis / Save
Scenario / Export Data).

**Files:**
- Create: `src/acf/gui/dashboard/awci_updates_panel.py`
- Test: `tests/gui/test_awci_updates_panel.py`

**Interfaces:**
- Consumes: nothing at construction; the composer (Task 7) calls
  `append_alert`/`append_update` with real, already-happened events (the
  same "real, plain append-only log, never a fabricated entry" convention
  as the ACF Workstation's `SystemFooterPanel.append_activity()`).
- Produces: `AWCIUpdatesPanel(QWidget)` with
  `append_alert(self, title: str, subtitle: str, severity: str) -> None`,
  `append_update(self, message: str) -> None`, and signals
  `generateReportRequested: Signal()`, `routeAnalysisRequested: Signal()`,
  `saveScenarioRequested: Signal()`, `exportDataRequested: Signal()`.

- [ ] **Step 1: Write the failing test**

```python
# tests/gui/test_awci_updates_panel.py
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_updates_panel import AWCIUpdatesPanel


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_updates_panel_appends_real_alerts_and_updates(qapp, qtbot):
    panel = AWCIUpdatesPanel()
    qtbot.addWidget(panel)
    panel.append_alert("Severe Convection", "Mediterranean (FL180-FL240)", "High")
    panel.append_update("ACF data refreshed")
    assert panel.alerts_list.count() == 1
    assert "Severe Convection" in panel.alerts_list.item(0).text()
    assert "ACF data refreshed" in panel.updates_log.toPlainText()


def test_updates_panel_quick_action_signals(qapp, qtbot):
    panel = AWCIUpdatesPanel()
    qtbot.addWidget(panel)
    with qtbot.waitSignal(panel.generateReportRequested, timeout=1000):
        panel.generate_report_button.click()
    with qtbot.waitSignal(panel.routeAnalysisRequested, timeout=1000):
        panel.route_analysis_button.click()
    with qtbot.waitSignal(panel.saveScenarioRequested, timeout=1000):
        panel.save_scenario_button.click()
    with qtbot.waitSignal(panel.exportDataRequested, timeout=1000):
        panel.export_data_button.click()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_awci_updates_panel.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement**

```python
# src/acf/gui/dashboard/awci_updates_panel.py
"""
AWCI Dashboard — Recent Alerts / Latest Updates / Quick Actions
====================================================================

Matches the AWCI reference image's bottom row. Recent Alerts/Latest
Updates are a real, plain append-only log of this dashboard's own real
events (same convention as the ACF Workstation's own
SystemFooterPanel.append_activity() - never a fabricated entry). Quick
Actions are plain signal-emitting buttons; the composer (or a future
task) wires each to a real action.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QTextEdit, QVBoxLayout, QWidget

_SEVERITY_COLORS = {"High": "#ef4444", "Moderate": "#f97316", "Low": "#22c55e"}


class AWCIUpdatesPanel(QWidget):
    """Real Recent Alerts / Latest Updates / Quick Actions row."""

    generateReportRequested = Signal()
    routeAnalysisRequested = Signal()
    saveScenarioRequested = Signal()
    exportDataRequested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)

        self.alerts_list = QListWidget()
        layout.addWidget(self.alerts_list, stretch=1)

        self.updates_log = QTextEdit()
        self.updates_log.setReadOnly(True)
        layout.addWidget(self.updates_log, stretch=1)

        actions_col = QVBoxLayout()
        self.generate_report_button = QPushButton("Generate Report")
        self.generate_report_button.clicked.connect(self.generateReportRequested.emit)
        actions_col.addWidget(self.generate_report_button)
        self.route_analysis_button = QPushButton("Route Analysis")
        self.route_analysis_button.clicked.connect(self.routeAnalysisRequested.emit)
        actions_col.addWidget(self.route_analysis_button)
        self.save_scenario_button = QPushButton("Save Scenario")
        self.save_scenario_button.clicked.connect(self.saveScenarioRequested.emit)
        actions_col.addWidget(self.save_scenario_button)
        self.export_data_button = QPushButton("Export Data")
        self.export_data_button.clicked.connect(self.exportDataRequested.emit)
        actions_col.addWidget(self.export_data_button)
        layout.addLayout(actions_col)

    def append_alert(self, title: str, subtitle: str, severity: str) -> None:
        item = QListWidgetItem(f"{title} — {subtitle}")
        color = _SEVERITY_COLORS.get(severity, "#8ea0b5")
        item.setForeground(QColor(color))
        self.alerts_list.insertItem(0, item)

    def append_update(self, message: str) -> None:
        self.updates_log.append(message)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_awci_updates_panel.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add src/acf/gui/dashboard/awci_updates_panel.py tests/gui/test_awci_updates_panel.py
git commit -m "feat(gui): add AWCI dashboard AWCIUpdatesPanel

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 7: Rewire the recovered `AWCIDashboard` composer to the new reference layout

This is the capstone integration task: lay out `AWCIFilterBar` (Task 3),
`AWCIGaugeRow` (Task 2), the recovered hero map (`AWCIMapPanel`), the new
right column (`AWCISituationPanel` from Task 4 + `AWCIAirportComplexityPanel`
from Task 5), the recovered second-row cards (cross section, vertical
profile treated as "Atmospheric Profile", route chart/analysis, evolution
chart as "Time Evolution"), and `AWCIUpdatesPanel` (Task 6) — matching the
reference image's placement exactly.

**Files:**
- Modify: `src/acf/gui/dashboard/awci_dashboard.py` (recovered in Task 1)
- Test: `tests/gui/test_awci_dashboard_composer.py`

**Interfaces:**
- Consumes: `AWCIFilterBar`, `AWCIGaugeRow`, `AWCISituationPanel`,
  `AWCIAirportComplexityPanel`, `AWCIUpdatesPanel` (all built above), plus
  the recovered `AWCIMapPanel`/`AWCICrossSection`/`AWCIVerticalProfile`/
  `AWCIRouteChart`/`AWCIEvolutionChart`/`AWCICalculator`.
- Produces: `AWCIDashboard.refresh()` (already present in the recovered
  file) extended to also populate the 5 new panels from the same real
  computation it already triggers.

- [ ] **Step 1: Read the recovered `AWCIDashboard._build_ui()` and `refresh()` in full**

```bash
grep -n "_build_ui\|def refresh" src/acf/gui/dashboard/awci_dashboard.py
```

Read the full body of both methods before making any change — this file
is ~2800 lines; understand its existing real data flow (how `global_map`/
`cross_section`/`radar`/`stats_bar`/`route_chart`/`risk_summary`/`footer`
get populated today) before replacing any of it.

- [ ] **Step 2: Restructure the top of the layout**

Replace whatever top bar/toolbar row currently exists at the top of
`_build_ui()` with, in order: `self.filter_bar = AWCIFilterBar()`, then
`self.gauge_row = AWCIGaugeRow()` — both added as their own rows above the
existing hero map. Keep every existing real button (HPC connect, Real
Archive, Import Model File, 4D Evolution, etc.) — re-parent them into the
`AWCIFilterBar`'s own "Settings" flow or a still-reachable menu rather
than deleting their real functionality; if there is no obvious place for
one of them in the new reference-image layout, keep it reachable via the
`AWCIFilterBar.settingsRequested` signal opening a menu/dialog listing
them, and disclose that choice in your report rather than silently
dropping the button.

- [ ] **Step 3: Wire the right column**

Add `self.situation_panel = AWCISituationPanel()` and
`self.airport_complexity_panel = AWCIAirportComplexityPanel()` as the
right column, replacing/supplementing whatever `risk_summary`/`stats_bar`
widgets occupied that space before — read their own real update call
sites first (`self.risk_summary.update_from_...(...)`,
`self.stats_bar.update_from_...(...)`) so you know what real data was
already flowing there, and feed the same real data into the new panels'
own `update_from_awci_result()`/`update_model_agreement()`/
`update_from_scores()` methods instead (do not duplicate the underlying
`AWCICalculator.calculate()` call — reuse the same real result already
computed for `global_map`/`radar`).

For `AWCIAirportComplexityPanel`, define a real, small, named set of
airports with real public coordinates (not fabricated) — e.g.:

```python
_AIRPORTS: dict[str, tuple[float, float]] = {
    "ALG (Algiers)": (36.6910, 3.2154),
    "TUN (Tunis)": (36.8510, 10.2272),
    "FCO (Rome)": (41.8003, 12.2389),
    "CDG (Paris)": (49.0097, 2.5479),
    "LHR (London)": (51.4700, -0.4543),
}
```

and sample the real, already-computed volume/field at each real
coordinate via `acf.awci.path_sampling`'s own real point-sampling
function (read its signature yourself — do not guess) to get each
airport's real AWCI score; keep the previous run's own scores (a plain
`dict` on `self`) to compute the real trend.

- [ ] **Step 4: Wire the bottom row**

Add `self.updates_panel = AWCIUpdatesPanel()` at the bottom of the layout.
In `refresh()` (and wherever the recovered file already logs real
pipeline stages, if it does), call `self.updates_panel.append_update(...)`
with real, already-happened stage descriptions (mirror the ACF
Workstation composer's own `footer_panel.append_activity(...)` calls).
Call `self.updates_panel.append_alert(...)` for each hazard whose real
module score crosses into "High"/"Severe" per `_level_for_score()`
(defined in Task 4's `awci_situation_panel.py` — import and reuse it
rather than redefining the same threshold logic here).

- [ ] **Step 5: Extend `refresh()` to populate the 3 new gauge/situation panels**

After the existing real `AWCICalculator.calculate()` call (find its
current call site in `refresh()`), add:

```python
self.gauge_row.update_from_awci_result(
    result,
    wind_shear_m_s=<the same real wind-shear value already computed nearby, or None>,
    relative_humidity_pct=<the same real RH value already available in this method, or None>,
    cloud_base_m=<a real cloud-base value if this codebase already computes one nearby, else None>,
)
self.situation_panel.update_from_awci_result(result)
```

Read the surrounding real code to find whichever real RH/wind-shear/
cloud-base values are already computed in this same `refresh()` call (the
recovered file's own `data` dict passed into `calculate()` already
contains real `wind_speed`/humidity fields — read it) rather than
inventing a second computation.

- [ ] **Step 6: Write the composer integration test**

```python
# tests/gui/test_awci_dashboard_composer.py
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_dashboard import AWCIDashboard


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_awci_dashboard_composer_builds_and_refreshes(qapp, qtbot):
    dashboard = AWCIDashboard()
    qtbot.addWidget(dashboard)
    assert dashboard.filter_bar is not None
    assert dashboard.gauge_row is not None
    assert dashboard.situation_panel is not None
    assert dashboard.airport_complexity_panel is not None
    assert dashboard.updates_panel is not None
    dashboard.refresh()
    qtbot.waitUntil(lambda: dashboard.gauge_row.global_gauge_label() != "NOT_COMPUTED", timeout=15000)
```

- [ ] **Step 7: Run the full test to verify it passes**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_awci_dashboard_composer.py -v`
Expected: pass (a real `refresh()` may take several seconds — the
`waitUntil` timeout above accounts for that).

- [ ] **Step 8: Commit**

```bash
git add src/acf/gui/dashboard/awci_dashboard.py tests/gui/test_awci_dashboard_composer.py
git commit -m "feat(gui): rewire the AWCI dashboard composer to the new reference layout

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 8: Wire the AWCI dashboard into the ACF Scientific Workstation

Restore an open-or-raise entry point for `AWCIDashboardWindow` (recovered
in Task 1), reached from a new button in the ACF Scientific Workstation —
mirroring how the Workstation itself is reachable from ESOC.

**Files:**
- Modify: `src/acf/gui/dashboard/acf_workstation.py`
- Test: `tests/test_acf_workstation_awci_action.py`

**Interfaces:**
- Consumes: `AWCIDashboardWindow` (recovered `src/acf/gui/dashboard/awci_window.py`).
- Produces: `ACFWorkstation._open_awci_dashboard()` open-or-raise method
  and a toolbar/top-bar button dispatching to it.

- [ ] **Step 1: Read `ACFWorkstationWindow`/`ACFWorkstation`'s top bar for where to add the button**

```bash
grep -n "science_explorer_button\|fullscreen_button" src/acf/gui/dashboard/acf_workstation.py
```

- [ ] **Step 2: Add the button and open-or-raise method**

Add a top-bar button next to the existing `science_explorer_button`:

```python
self.awci_dashboard_button = QPushButton("✈️ AWCI Dashboard")
self.awci_dashboard_button.setToolTip(
    "Opens the real AWCI (Aviation Weather Complexity Index) dashboard - "
    "a separate window, same open-or-raise pattern as this Workstation's own "
    "entry point from ESOC."
)
self.awci_dashboard_button.clicked.connect(self._open_awci_dashboard)
top_bar.addWidget(self.awci_dashboard_button)
```

and, alongside `ACFWorkstation.__init__`'s other lazily-created window
attributes:

```python
self._awci_dashboard_window: Any | None = None
```

and a new method:

```python
def _open_awci_dashboard(self) -> None:
    """Open (or raise) the real AWCI dashboard as its own top-level
    window - same open-or-raise pattern as this Workstation's own
    entry point from ESOC."""
    from acf.gui.dashboard.awci_window import AWCIDashboardWindow

    if self._awci_dashboard_window is None:
        self._awci_dashboard_window = AWCIDashboardWindow(self)
    self._awci_dashboard_window.show()
    self._awci_dashboard_window.raise_()
    self._awci_dashboard_window.activateWindow()
```

(the local import avoids a module-level circular import, same convention
the recovered `esoc_window.py`/`acf_workstation.py` already use for their
own cross-window open-or-raise methods — verify `awci_window.py`'s real
`AWCIDashboardWindow` class name/constructor signature from Task 1's
recovered file before wiring this call.)

- [ ] **Step 3: Write the integration test**

```python
# tests/test_acf_workstation_awci_action.py
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation import ACFWorkstation


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_awci_dashboard_button_opens_the_real_window(qapp, qtbot):
    workstation = ACFWorkstation()
    qtbot.addWidget(workstation)
    assert workstation._awci_dashboard_window is None
    workstation.awci_dashboard_button.click()
    assert workstation._awci_dashboard_window is not None
    assert workstation._awci_dashboard_window.isVisible()


def test_awci_dashboard_button_reuses_the_same_window_on_a_second_click(qapp, qtbot):
    workstation = ACFWorkstation()
    qtbot.addWidget(workstation)
    workstation.awci_dashboard_button.click()
    first_window = workstation._awci_dashboard_window
    workstation.awci_dashboard_button.click()
    assert workstation._awci_dashboard_window is first_window
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/test_acf_workstation_awci_action.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add src/acf/gui/dashboard/acf_workstation.py tests/test_acf_workstation_awci_action.py
git commit -m "feat(gui): open the AWCI dashboard from a new button in the ACF Workstation

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 9: Full verification pass

**Files:** none created; verification only.

- [ ] **Step 1: Run the full GUI test subset**

```bash
source .venv/bin/activate
QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/ tests/test_acf_workstation_awci_action.py tests/test_esoc_acf_workstation_action.py -v
```

Expected: all pass. Investigate and fix any failure before proceeding.

- [ ] **Step 2: Run the full test suite**

```bash
source .venv/bin/activate
QT_QPA_PLATFORM=offscreen python -m pytest -q
```

Expected: no new failures/errors versus this session's most recent
clean baseline (4120 passed, 0 failed, before this plan's own new tests).

- [ ] **Step 3: Visual verification against the AWCI reference image**

Launch `AWCIDashboardWindow` directly with `QT_QPA_PLATFORM=offscreen`,
call `.refresh()`, wait for it to complete, grab a screenshot
(`window.grab().save("awci_screenshot.png")`), and compare section-by-
section against the AWCI reference image using the design spec's own
component-mapping table. Note any visual mismatch as a follow-up item
rather than silently accepting it — the user has explicitly asked for
exact placement fidelity.

- [ ] **Step 4: Commit final state (if the visual pass produced any fixes)**

```bash
git add -A
git commit -m "fix(gui): address visual QA findings against the AWCI reference image

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```
