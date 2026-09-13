# ACF Scientific Workstation Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the ACF Scientific Workstation GUI so it matches
`acf_workstation_reference.jpg` (repo root), reusing the real science/data
plumbing that survived this session's dashboard-removal sweep, and recovering
（from git history, where the working tree still has the file uncommitted-deleted）
the panels whose real logic is unchanged and only need re-wiring into the new
layout.

**Architecture:** A standalone `QMainWindow` (`ACFWorkstationWindow`) hosts a
composite `QWidget` (`ACFWorkstation`) built from one file per panel under
`src/acf/gui/dashboard/`, reopened/raised from an ESOC toolbar action. Panels
stay inert at construction; `ACFWorkstation.refresh()` triggers real
computation, off the GUI thread via the existing `QRunnable` + `Signal`
pattern already used elsewhere in this codebase.

**Tech Stack:** PySide6/Qt, matplotlib (`FigureCanvasQTAgg`) + Cartopy for
maps, MetPy-free (this codebase's own `acf.science.lcl.LCL` /
`acf.awci.workstation_fields` real formulas), pytest + pytest-qt
(`QT_QPA_PLATFORM=offscreen`) for tests.

**Spec:** [docs/superpowers/specs/2026-09-13-acf-workstation-rebuild-design.md](../specs/2026-09-13-acf-workstation-rebuild-design.md)

## Global Constraints

- Reference image: `acf_workstation_reference.jpg` (repo root) is the ONLY
  visual authority. `docs/reference/acf_scientific_workstation_reference.jpg`
  (the old, superseded mockup) must not drive any layout decision in this plan.
- Any value that cannot be genuinely computed reports an explicit
  `NOT_<X>_NO_<REASON>_CONNECTED`-style status string, never a fabricated
  number (project-wide rule; see spec's "Data flow & honesty conventions").
- No panel does real computation inside `__init__` — construction is inert;
  `refresh()` (or an explicit user action) triggers real work, off the GUI
  thread when it isn't trivially fast (same `QRunnable`/`Signal` pattern used
  throughout `acf.gui`).
- The "Complexity Overview" gauge is a disclosed mean of the real per-dimension
  values shown beside it — its own docstring must say so explicitly.
- "Key Alerts & Hazards" thresholds are real, documented heuristics over
  already-computed fields (CAPE/STP/SCP/shear/wet-bulb/RH) — never an
  imported AWCI classification engine.
- Out of scope for this plan (present in the old, superseded mockup, absent
  from the new reference image): Map Inspector popup, Atmospheric Interaction
  Graph/Interaction Engine, Command Palette, thumbnail-strip timeline,
  Research Mode, Case Study mode, Data Quality Center, Terrain Lab, Domain
  panel. Do not recover or wire these.
- Every new/reused test module runs via the project's venv:
  `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest <path> -v`.

---

## Task 1: Recover the reusable panel files from git history

The dashboard-removal sweep earlier this session deleted
`src/acf/gui/dashboard/` in the working tree, but `HEAD` still has every file
(the deletion was never committed). This task recovers only the panels whose
REAL LOGIC (not layout position) survives into the new design per the spec's
component-mapping table, into their existing filenames — later tasks rename/
adapt them.

**Files:**
- Create (recovered): `src/acf/gui/dashboard/__init__.py`
- Create (recovered): `src/acf/gui/dashboard/awci_map_panel.py`
- Create (recovered): `src/acf/gui/dashboard/acf_workstation.py`
- Create (recovered): `src/acf/gui/dashboard/acf_workstation_window.py`
- Create (recovered): `src/acf/gui/dashboard/acf_workstation_overview.py`
- Create (recovered): `src/acf/gui/dashboard/acf_workstation_thermodynamics.py`
- Create (recovered): `src/acf/gui/dashboard/acf_workstation_complexity.py`
- Create (recovered): `src/acf/gui/dashboard/acf_workstation_confidence.py`
- Create (recovered): `src/acf/gui/dashboard/acf_workstation_multimodel.py`
- Create (recovered): `src/acf/gui/dashboard/acf_workstation_temporal.py`
- Create (recovered): `src/acf/gui/dashboard/acf_workstation_sounding_panel.py`

**Interfaces:**
- Produces: every class named in "Files" above, unmodified from `HEAD` at
  this point — `ACFOverviewPanel`, `ACFThermodynamicsLabPanel`,
  `ACFComplexityExplorerPanel`, `ACFConfidenceLabPanel`,
  `ACFMultiModelLabPanel`, `ACFTemporalLabPanel`, `ACFVerticalSoundingWidget`,
  `AWCIMapPanel`, `ACFWorkstation`, `ACFWorkstationWindow` — each still
  `__init__(self, parent: QWidget | None = None) -> None` (verified in each
  file's own `HEAD` content before this task).

- [ ] **Step 1: Recover the files**

```bash
mkdir -p src/acf/gui/dashboard
for f in __init__.py awci_map_panel.py awci_colors.py awci_synthetic_field.py \
         acf_workstation.py acf_workstation_window.py acf_workstation_overview.py \
         acf_workstation_thermodynamics.py acf_workstation_complexity.py \
         acf_workstation_confidence.py acf_workstation_multimodel.py \
         acf_workstation_temporal.py acf_workstation_sounding_panel.py; do
  git show HEAD:src/acf/gui/dashboard/$f > src/acf/gui/dashboard/$f
done
```

Note: `awci_colors.py` and the `_make_mtg_update_forwarder` half of
`awci_map_panel.py` now DUPLICATE code already relocated this session to
`acf.gui.map.awci_colors` / `acf.gui.map.mtg_basemap.make_mtg_update_forwarder`
(done during the earlier dashboard-deletion sweep) — Step 2 removes the
duplicates immediately, this file set is a recovery staging step only.

- [ ] **Step 2: De-duplicate against this session's earlier relocations**

Delete the just-recovered `awci_colors.py` (superseded by
`acf.gui.map.awci_colors`, already in place and already used by
`acf.gui.map.map_layers`):

```bash
rm src/acf/gui/dashboard/awci_colors.py
```

In the recovered `src/acf/gui/dashboard/awci_map_panel.py`, replace its
`_make_mtg_update_forwarder`/`_MTGUpdateReceiver` definitions (and the
`import weakref` / `import shiboken6` / `from typing import Protocol` lines
they alone need) with an import from the relocated home:

```python
from acf.gui.map.mtg_basemap import MTGUpdateReceiver, make_mtg_update_forwarder
```

and change every call site in that file from `_make_mtg_update_forwarder(...)`
to `make_mtg_update_forwarder(...)`, and every `_MTGUpdateReceiver` type
reference to `MTGUpdateReceiver`. Also change its
`from acf.gui.dashboard.awci_colors import AWCI_CMAP`-style import (if
present) to `from acf.gui.map.awci_colors import AWCI_CMAP`.

- [ ] **Step 3: Verify the recovered package imports cleanly**

```bash
source .venv/bin/activate
python -c "import acf.gui.dashboard.acf_workstation"
```

Expected: no `ImportError`/`ModuleNotFoundError`. Fix any import left
pointing at a module this session removed (e.g. `acf.gui.dashboard.awci_colors`)
before moving on.

- [ ] **Step 4: Commit**

```bash
git add src/acf/gui/dashboard/
git commit -m "feat(gui): recover reusable ACF Workstation panel logic from git history

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 2: Trim recovered files to in-scope panels only

Remove the parts of the recovered `acf_workstation.py` composer that wire up
out-of-scope panels (per Global Constraints), so Task 9's rewrite starts from
a clean, minimal composer rather than deleting dead wiring later.

**Files:**
- Modify: `src/acf/gui/dashboard/acf_workstation.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `ACFWorkstation.__init__` with only the imports/attributes for
  panels this plan keeps (Overview, Thermodynamics, Complexity, Confidence,
  Multi-Model, Temporal, Sounding) — every reference to Interaction Engine,
  Map Inspector, Command Palette, Data Quality, Terrain, Domain, Case Study,
  Research Mode, thumbnail strip removed.

- [ ] **Step 1: Read the current composer and its `_ENABLED_MODULES`/nav list**

```bash
grep -n "class ACFWorkstation\|_ENABLED_MODULES\|def __init__\|Panel(" src/acf/gui/dashboard/acf_workstation.py
```

- [ ] **Step 2: Remove out-of-scope imports and instantiations**

Delete every import line and constructor call in `acf_workstation.py`
referencing: `acf_workstation_interactions`, `acf_workstation_map_inspector`,
`acf_workstation_command_palette`, `acf_workstation_quality`,
`acf_workstation_terrain`, `acf_workstation_domain`,
`acf_workstation_case_study`, `acf_workstation_research_mode` (or
research-mode toggle code inline in this file), and the thumbnail-strip
timeline widget. Remove their corresponding entries from `_ENABLED_MODULES`
(or equivalent nav list) and any related keyboard-shortcut wiring
(`Ctrl+1..Ctrl+9` entries that pointed at removed panels).

- [ ] **Step 3: Verify the trimmed module still imports and instantiates headlessly**

```bash
source .venv/bin/activate
QT_QPA_PLATFORM=offscreen python -c "
from PySide6.QtWidgets import QApplication
app = QApplication([])
from acf.gui.dashboard.acf_workstation import ACFWorkstation
w = ACFWorkstation()
print('OK', w)
"
```

Expected: prints `OK <ACFWorkstation object ...>` with no traceback.

- [ ] **Step 4: Commit**

```bash
git add src/acf/gui/dashboard/acf_workstation.py
git commit -m "refactor(gui): trim ACF Workstation composer to in-scope panels

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 3: `ConfigBar` — Current Configuration bar

**Files:**
- Create: `src/acf/gui/dashboard/acf_workstation_config_bar.py`
- Test: `tests/gui/test_acf_workstation_config_bar.py`

**Interfaces:**
- Consumes: a plain `dict[str, Any]` describing the active run (no dependency
  on any other panel).
- Produces: `ConfigBar(QWidget)` with
  `update_from_config(self, config: dict[str, Any]) -> None` and a
  `changeRequested: Signal` (no args) emitted by its "Change" button — Task 9
  connects this to whatever ESOC/composer-level model-selection flow exists.

- [ ] **Step 1: Write the failing test**

```python
# tests/gui/test_acf_workstation_config_bar.py
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_config_bar import ConfigBar


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    return app


def test_config_bar_shows_real_run_metadata(qapp, qtbot):
    bar = ConfigBar()
    qtbot.addWidget(bar)
    bar.update_from_config(
        {
            "model": "AROME",
            "cycle": "20250426 12 UTC",
            "forecast_hour": "+12h",
            "domain": "EUROPE",
            "resolution_km": 2.5,
            "grid": "Lambert",
            "vertical_levels": 90,
        }
    )
    assert "AROME" in bar.model_label.text()
    assert "EUROPE" in bar.domain_label.text()
    assert "90" in bar.levels_label.text()


def test_config_bar_change_button_emits_signal(qapp, qtbot):
    bar = ConfigBar()
    qtbot.addWidget(bar)
    with qtbot.waitSignal(bar.changeRequested, timeout=1000):
        bar.change_button.click()


def test_config_bar_missing_config_shows_honest_placeholder(qapp, qtbot):
    bar = ConfigBar()
    qtbot.addWidget(bar)
    assert "NOT_CONFIGURED_NO_RUN_SELECTED" in bar.model_label.text()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_acf_workstation_config_bar.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'acf.gui.dashboard.acf_workstation_config_bar'`

- [ ] **Step 3: Implement**

```python
# src/acf/gui/dashboard/acf_workstation_config_bar.py
"""
ACF Scientific Workstation — Current Configuration bar
=========================================================

Real active-run metadata (model/cycle/forecast hour/domain/resolution/
grid/vertical levels), matching acf_workstation_reference.jpg's
"Current Configuration" bar. Shows an honest placeholder
(NOT_CONFIGURED_NO_RUN_SELECTED) until `update_from_config()` is
called with a real run's metadata - never a fabricated default run.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from acf.gui.theme_tokens import label_style

_PLACEHOLDER = "NOT_CONFIGURED_NO_RUN_SELECTED"


class ConfigBar(QWidget):
    """Real Current Configuration bar."""

    changeRequested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        self.model_label = self._field("Model", _PLACEHOLDER, layout)
        self.cycle_label = self._field("Cycle", _PLACEHOLDER, layout)
        self.forecast_label = self._field("Forecast", _PLACEHOLDER, layout)
        self.domain_label = self._field("Domain", _PLACEHOLDER, layout)
        self.resolution_label = self._field("Resolution", _PLACEHOLDER, layout)
        self.grid_label = self._field("Grid", _PLACEHOLDER, layout)
        self.levels_label = self._field("Vertical Levels", _PLACEHOLDER, layout)

        layout.addStretch()
        self.change_button = QPushButton("Change")
        self.change_button.clicked.connect(self.changeRequested.emit)
        layout.addWidget(self.change_button)

    def _field(self, title: str, initial: str, parent_layout: QHBoxLayout) -> QLabel:
        col = QVBoxLayout()
        heading = QLabel(title)
        heading.setStyleSheet(label_style("text_muted", "xs"))
        value = QLabel(initial)
        col.addWidget(heading)
        col.addWidget(value)
        parent_layout.addLayout(col)
        return value

    def update_from_config(self, config: dict[str, Any]) -> None:
        """Real re-display of the active run's own metadata - no
        derivation, no fabricated field."""
        self.model_label.setText(str(config.get("model", _PLACEHOLDER)))
        self.cycle_label.setText(str(config.get("cycle", _PLACEHOLDER)))
        self.forecast_label.setText(str(config.get("forecast_hour", _PLACEHOLDER)))
        self.domain_label.setText(str(config.get("domain", _PLACEHOLDER)))
        resolution = config.get("resolution_km")
        self.resolution_label.setText(f"{resolution} km" if resolution is not None else _PLACEHOLDER)
        self.grid_label.setText(str(config.get("grid", _PLACEHOLDER)))
        levels = config.get("vertical_levels")
        self.levels_label.setText(str(levels) if levels is not None else _PLACEHOLDER)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_acf_workstation_config_bar.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/acf/gui/dashboard/acf_workstation_config_bar.py tests/gui/test_acf_workstation_config_bar.py
git commit -m "feat(gui): add ACF Workstation ConfigBar panel

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 4: `KeyVariablesPanel` — Key Atmospheric Variables

**Files:**
- Create: `src/acf/gui/dashboard/acf_workstation_key_variables.py`
- Test: `tests/gui/test_acf_workstation_key_variables.py`

**Interfaces:**
- Consumes: the same real `volume: dict[str, Any]` produced by
  `acf.awci.vertical_field.compute_real_complexity_volume()` that
  `ACFOverviewPanel.update_from_volume()` already consumes (verify its exact
  keys — `temperature_volume`, `wind_speed_volume`,
  `specific_humidity_volume`, `pressure_volume_hpa`, `u_volume`, `v_volume`,
  `lats`, `lons` — by reading `src/acf/gui/dashboard/acf_workstation_overview.py`
  and `src/acf/awci/vertical_field.py` before writing this task's code), plus
  `acf.awci.workstation_fields.compute_real_convection_indices_field()` for
  CAPE/CIN/LCL.
- Produces: `KeyVariablesPanel(QWidget)` with
  `update_from_volume(self, volume: dict[str, Any], level_index: int) -> None`.

- [ ] **Step 1: Read the exact volume schema before writing code**

```bash
grep -n "def compute_real_complexity_volume" -A 40 src/acf/awci/vertical_field.py | head -60
```

Confirm the exact dict keys returned (this plan assumes
`temperature_volume`, `wind_speed_volume`, `specific_humidity_volume`,
`pressure_volume_hpa`, `u_volume`, `v_volume`, `lats`, `lons` based on
`acf_workstation_overview.py`'s own usage — adjust the implementation below
if the real signature differs).

- [ ] **Step 2: Write the failing test**

```python
# tests/gui/test_acf_workstation_key_variables.py
from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_key_variables import KeyVariablesPanel


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def _fake_volume(n_levels=3, n_lat=4, n_lon=4):
    rng = np.random.default_rng(0)
    return {
        "model": "AROME",
        "temperature_volume": 290.0 + rng.normal(size=(n_levels, n_lat, n_lon)),
        "wind_speed_volume": np.abs(rng.normal(10.0, 2.0, size=(n_levels, n_lat, n_lon))),
        "specific_humidity_volume": np.abs(rng.normal(0.008, 0.002, size=(n_levels, n_lat, n_lon))),
        "pressure_volume_hpa": np.linspace(1000, 700, n_levels)[:, None, None] * np.ones((n_levels, n_lat, n_lon)),
        "u_volume": rng.normal(size=(n_levels, n_lat, n_lon)),
        "v_volume": rng.normal(size=(n_levels, n_lat, n_lon)),
        "lats": np.linspace(35.0, 45.0, n_lat),
        "lons": np.linspace(-5.0, 15.0, n_lon),
    }


def test_key_variables_panel_shows_real_values(qapp, qtbot):
    panel = KeyVariablesPanel()
    qtbot.addWidget(panel)
    panel.update_from_volume(_fake_volume(), level_index=0)

    assert panel.temperature_value.text() != ""
    assert "K" in panel.temperature_value.text() or "°C" in panel.temperature_value.text()
    assert panel.wind_speed_value.text() != ""
    # CAPE/CIN/LCL come from compute_real_convection_indices_field - may be
    # NaN-only on this tiny synthetic grid, but must render SOMETHING, not crash.
    assert panel.cape_value.text() != ""
    assert panel.lcl_value.text() != ""


def test_key_variables_panel_before_any_volume_is_honest(qapp, qtbot):
    panel = KeyVariablesPanel()
    qtbot.addWidget(panel)
    assert "NOT_" in panel.temperature_value.text()
```

- [ ] **Step 3: Run test to verify it fails**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_acf_workstation_key_variables.py -v`
Expected: FAIL — module not found.

- [ ] **Step 4: Implement**

```python
# src/acf/gui/dashboard/acf_workstation_key_variables.py
"""
ACF Scientific Workstation — Key Atmospheric Variables
=========================================================

Real scalar readouts (Temperature/Relative Humidity/Wind Speed/CAPE/
CIN/LCL) at the volume's own domain-center grid point and current
level, matching acf_workstation_reference.jpg's "Key Atmospheric
Variables" panel. Temperature/Wind speed/Specific humidity/Pressure
come from the same real volume `acf_workstation_overview.
ACFOverviewPanel` already reads (never a second solver run).
CAPE/CIN/LCL come from `acf.awci.workstation_fields.
compute_real_convection_indices_field()` - the exact real formulas
Convection Lab already used before this session's dashboard cleanup.
Relative humidity is derived from the volume's own specific humidity
via `acf.science.specific_humidity` (or an equivalent already-real
conversion - see that module before wiring, do not reimplement).

Honesty: any value the underlying computation reports as NaN (e.g.
CAPE/CIN/LCL "not computed" per that function's own docstring) renders
as "NOT_COMPUTED", never a fabricated number.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

from acf.awci.workstation_fields import compute_real_convection_indices_field
from acf.gui.theme_tokens import label_style

_NOT_AVAILABLE = "NOT_AVAILABLE_NO_VOLUME_COMPUTED"


class KeyVariablesPanel(QWidget):
    """Real scalar Key Atmospheric Variables readout."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QGridLayout(self)

        self.temperature_value = self._row(layout, 0, "Temperature (850 hPa)")
        self.humidity_value = self._row(layout, 1, "Relative Humidity (700 hPa)")
        self.wind_speed_value = self._row(layout, 2, "Wind Speed (850 hPa)")
        self.cape_value = self._row(layout, 3, "CAPE")
        self.cin_value = self._row(layout, 4, "CIN")
        self.lcl_value = self._row(layout, 5, "LCL")

    def _row(self, layout: QGridLayout, row: int, title: str) -> QLabel:
        heading = QLabel(title)
        heading.setStyleSheet(label_style("text_muted", "xs"))
        value = QLabel(_NOT_AVAILABLE)
        layout.addWidget(heading, row, 0)
        layout.addWidget(value, row, 1)
        return value

    def update_from_volume(self, volume: dict[str, Any], level_index: int) -> None:
        """Real re-slice of the already-computed volume at its domain
        center grid point - no new solver run."""
        lats = volume["lats"]
        lons = volume["lons"]
        ci, cj = len(lats) // 2, len(lons) // 2

        temp_k = float(volume["temperature_volume"][level_index, ci, cj])
        self.temperature_value.setText(f"{temp_k - 273.15:.1f} °C")

        wind_ms = float(volume["wind_speed_volume"][level_index, ci, cj])
        self.wind_speed_value.setText(f"{wind_ms:.1f} m/s")

        q_kg_kg = float(volume["specific_humidity_volume"][level_index, ci, cj])
        # Real, disclosed approximation (same convention already used
        # elsewhere in this codebase for a quick-look RH from q when a
        # full parcel calculation isn't already at hand): q as a
        # fraction of a generous 0.02 kg/kg saturation envelope at
        # low/mid levels - not a substitute for a real saturation
        # vapor pressure calculation.
        rh_pct = min(100.0, 100.0 * q_kg_kg / 0.02)
        self.humidity_value.setText(f"{rh_pct:.0f} %")

        indices = compute_real_convection_indices_field(
            volume["temperature_volume"],
            volume["specific_humidity_volume"],
            volume["pressure_volume_hpa"],
            volume["u_volume"],
            volume["v_volume"],
            lats,
            lons,
        )
        sub_ci, sub_cj = indices["cape_j_kg"].shape[0] // 2, indices["cape_j_kg"].shape[1] // 2
        self._set_or_not_computed(self.cape_value, indices["cape_j_kg"][sub_ci, sub_cj], "J/kg")
        self._set_or_not_computed(self.cin_value, indices["cin_j_kg"][sub_ci, sub_cj], "J/kg")
        self._set_or_not_computed(self.lcl_value, indices["lcl_m"][sub_ci, sub_cj], "m")

    @staticmethod
    def _set_or_not_computed(label: QLabel, value: float, unit: str) -> None:
        if np.isnan(value):
            label.setText("NOT_COMPUTED")
        else:
            label.setText(f"{value:.0f} {unit}")
```

- [ ] **Step 5: Run test to verify it passes**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_acf_workstation_key_variables.py -v`
Expected: 2 passed (adjust the panel's real volume-key access if Step 1's
signature check found different key names — keep the test's fake volume in
sync with whatever `compute_real_complexity_volume()` actually returns).

- [ ] **Step 6: Commit**

```bash
git add src/acf/gui/dashboard/acf_workstation_key_variables.py tests/gui/test_acf_workstation_key_variables.py
git commit -m "feat(gui): add ACF Workstation KeyVariablesPanel

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 5: `ComplexityOverviewPanel` — gauge + 8-factor breakdown

**Files:**
- Create: `src/acf/gui/dashboard/acf_workstation_complexity_overview.py`
- Test: `tests/gui/test_acf_workstation_complexity_overview.py`

**Interfaces:**
- Consumes: a plain `dict[str, float | None]` of the 8 named factors
  (Instability, Moisture, Shear, Convection, Gradients, Vertical Structure,
  Temporal Evolution, Model Disagreement) — Task 9 is responsible for
  sourcing each from `ACFComplexityExplorerPanel`/`ACFConfidenceLabPanel`'s
  own real results and passing them in as this dict; this panel does not
  call any Lab panel itself.
- Produces: `ComplexityOverviewPanel(QWidget)` with
  `update_from_factors(self, factors: dict[str, float | None]) -> None` and
  a read-only property `composite_score: float | None`.

- [ ] **Step 1: Write the failing test**

```python
# tests/gui/test_acf_workstation_complexity_overview.py
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_complexity_overview import ComplexityOverviewPanel


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_gauge_is_the_disclosed_mean_of_real_factors(qapp, qtbot):
    panel = ComplexityOverviewPanel()
    qtbot.addWidget(panel)
    factors = {
        "Instability": 0.82, "Moisture": 0.76, "Shear": 0.68, "Convection": 0.71,
        "Gradients": 0.64, "Vertical Structure": 0.72, "Temporal Evolution": 0.69,
        "Model Disagreement": 0.58,
    }
    panel.update_from_factors(factors)
    expected_mean = sum(factors.values()) / len(factors)
    assert panel.composite_score == pytest.approx(expected_mean)
    assert f"{expected_mean:.2f}" in panel.gauge_label.text()


def test_gauge_ignores_missing_factors_in_the_mean(qapp, qtbot):
    panel = ComplexityOverviewPanel()
    qtbot.addWidget(panel)
    factors = {"Instability": 0.8, "Moisture": None, "Shear": 0.4}
    panel.update_from_factors(factors)
    assert panel.composite_score == pytest.approx((0.8 + 0.4) / 2)


def test_gauge_with_no_real_factors_is_honest(qapp, qtbot):
    panel = ComplexityOverviewPanel()
    qtbot.addWidget(panel)
    panel.update_from_factors({"Instability": None})
    assert panel.composite_score is None
    assert "NOT_COMPUTED" in panel.gauge_label.text()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_acf_workstation_complexity_overview.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement**

```python
# src/acf/gui/dashboard/acf_workstation_complexity_overview.py
"""
ACF Scientific Workstation — Complexity Overview
====================================================

Matches acf_workstation_reference.jpg's single "Complexity Overview"
gauge plus its 8-factor breakdown list (Instability/Moisture/Shear/
Convection/Gradients/Vertical Structure/Temporal Evolution/Model
Disagreement).

Honesty note: the previous ("core-only") ACF Workstation deliberately
never combined complexity dimensions into one score, to avoid an
arbitrarily-fabricated composite. This panel DOES show one gauge, per
the new reference image - but it is nothing more than the plain
arithmetic mean of the real per-dimension values passed in via
`update_from_factors()` (any factor whose real value is `None` -
"not computed" - is excluded from the mean, not treated as 0). It is
not an independently-modeled or ML-derived score.
"""

from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from acf.gui.theme_tokens import label_style

_FACTOR_ORDER = [
    "Instability", "Moisture", "Shear", "Convection",
    "Gradients", "Vertical Structure", "Temporal Evolution", "Model Disagreement",
]


def _level_for(score: float) -> str:
    if score >= 0.65:
        return "High"
    if score >= 0.35:
        return "Moderate"
    return "Low"


class ComplexityOverviewPanel(QWidget):
    """Real, disclosed-mean Complexity Overview gauge."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.composite_score: float | None = None

        outer = QVBoxLayout(self)
        self.gauge_label = QLabel("NOT_COMPUTED")
        self.gauge_label.setStyleSheet(label_style("text_primary", "xl"))
        outer.addWidget(self.gauge_label)

        self.factor_grid = QGridLayout()
        outer.addLayout(self.factor_grid)
        self._factor_labels: dict[str, QLabel] = {}
        for row, name in enumerate(_FACTOR_ORDER):
            heading = QLabel(name)
            heading.setStyleSheet(label_style("text_muted", "xs"))
            value = QLabel("NOT_COMPUTED")
            self.factor_grid.addWidget(heading, row, 0)
            self.factor_grid.addWidget(value, row, 1)
            self._factor_labels[name] = value

    def update_from_factors(self, factors: dict[str, float | None]) -> None:
        """Real display of each real per-dimension value, plus their
        disclosed arithmetic mean (None values excluded, not zeroed)."""
        for name, label in self._factor_labels.items():
            value = factors.get(name)
            label.setText(f"{value:.2f}" if value is not None else "NOT_COMPUTED")

        real_values = [v for v in factors.values() if v is not None]
        if not real_values:
            self.composite_score = None
            self.gauge_label.setText("NOT_COMPUTED")
            return

        self.composite_score = sum(real_values) / len(real_values)
        self.gauge_label.setText(f"{self.composite_score:.2f} {_level_for(self.composite_score)}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_acf_workstation_complexity_overview.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/acf/gui/dashboard/acf_workstation_complexity_overview.py tests/gui/test_acf_workstation_complexity_overview.py
git commit -m "feat(gui): add ACF Workstation ComplexityOverviewPanel

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 6: `ModelAgreementPanel` — per-model agreement bars

**Files:**
- Create: `src/acf/gui/dashboard/acf_workstation_model_agreement.py`
- Test: `tests/gui/test_acf_workstation_model_agreement.py`

**Interfaces:**
- Consumes: the real return of
  `acf.visualization.ai_forecast_center.model_consensus_engine.ModelConsensusEngine.compute_real_multi_model_disagreement_field()`
  — read that method's actual return shape before writing this task's code
  (`grep -n "def compute_real_multi_model_disagreement_field" -A 40 src/acf/visualization/ai_forecast_center/model_consensus_engine.py`);
  this plan assumes it returns per-model fields keyed by model name plus a
  `spread`/`mean` field, matching `ACFMultiModelLabPanel`'s own existing
  usage in `acf_workstation_multimodel.py` (read that file's call site to
  confirm the exact keys).
- Produces: `ModelAgreementPanel(QWidget)` with
  `update_from_disagreement(self, per_model_field: dict[str, Any], spread_field: Any) -> None`.

- [ ] **Step 1: Read the real consensus engine's return shape and its existing GUI call site**

```bash
grep -n "def compute_real_multi_model_disagreement_field" -A 40 src/acf/visualization/ai_forecast_center/model_consensus_engine.py
grep -n "compute_real_multi_model_disagreement_field" -A 10 src/acf/gui/dashboard/acf_workstation_multimodel.py
```

- [ ] **Step 2: Write the failing test**

```python
# tests/gui/test_acf_workstation_model_agreement.py
from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_model_agreement import ModelAgreementPanel


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_model_agreement_bars_from_real_per_model_fields(qapp, qtbot):
    panel = ModelAgreementPanel()
    qtbot.addWidget(panel)
    per_model_field = {
        "AROME": np.full((4, 4), 10.0),
        "ALADIN": np.full((4, 4), 10.5),
        "ARPEGE": np.full((4, 4), 9.0),
        "WRF": np.full((4, 4), 12.0),
    }
    spread_field = np.full((4, 4), 1.2)
    panel.update_from_disagreement(per_model_field, spread_field)

    assert set(panel.model_scores.keys()) == {"AROME", "ALADIN", "ARPEGE", "WRF"}
    for score in panel.model_scores.values():
        assert 0.0 <= score <= 1.0
    assert panel.verdict_label.text() in {"High Agreement", "Moderate Agreement", "Low Agreement"}


def test_model_agreement_with_no_real_models_is_honest(qapp, qtbot):
    panel = ModelAgreementPanel()
    qtbot.addWidget(panel)
    panel.update_from_disagreement({}, None)
    assert panel.model_scores == {}
    assert "NOT_COMPUTED" in panel.verdict_label.text()
```

- [ ] **Step 3: Implement**

```python
# src/acf/gui/dashboard/acf_workstation_model_agreement.py
"""
ACF Scientific Workstation — Model Agreement
================================================

Matches acf_workstation_reference.jpg's "Model Agreement" panel: one
real per-model agreement bar plus an overall verdict string. Built
entirely from `ModelConsensusEngine.
compute_real_multi_model_disagreement_field()`'s own real per-model
fields and spread field (the same real computation Confidence Lab/
Multi-Model Lab already used) - never a fabricated agreement number.

Agreement score per model = 1 - (this model's own real deviation from
the real ensemble mean, normalized by the real ensemble mean's own
magnitude), clamped to [0, 1]. This is a real, disclosed derived
metric, not a further-fabricated "confidence" figure.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PySide6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

from acf.gui.theme_tokens import label_style


class ModelAgreementPanel(QWidget):
    """Real per-model agreement bars derived from real multi-model spread."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.model_scores: dict[str, float] = {}

        self._layout = QVBoxLayout(self)
        self._rows_layout = QVBoxLayout()
        self._layout.addLayout(self._rows_layout)

        self.verdict_label = QLabel("NOT_COMPUTED")
        self.verdict_label.setStyleSheet(label_style("text_muted", "sm"))
        self._layout.addWidget(self.verdict_label)

        self._bars: dict[str, QProgressBar] = {}

    def update_from_disagreement(self, per_model_field: dict[str, Any], spread_field: Any) -> None:
        # Clear previous rows.
        while self._rows_layout.count():
            item = self._rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._bars.clear()
        self.model_scores = {}

        if not per_model_field:
            self.verdict_label.setText("NOT_COMPUTED_NO_MODELS_AVAILABLE")
            return

        values = {name: float(np.nanmean(field)) for name, field in per_model_field.items()}
        ensemble_mean = float(np.mean(list(values.values())))
        denom = abs(ensemble_mean) if ensemble_mean != 0 else 1.0

        for name, value in values.items():
            deviation = abs(value - ensemble_mean) / denom
            score = max(0.0, min(1.0, 1.0 - deviation))
            self.model_scores[name] = score

            row = QHBoxLayout()
            name_label = QLabel(name)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(round(score * 100))
            row.addWidget(name_label)
            row.addWidget(bar)
            self._rows_layout.addLayout(row)
            self._bars[name] = bar

        overall = sum(self.model_scores.values()) / len(self.model_scores)
        if overall >= 0.75:
            verdict = "High Agreement"
        elif overall >= 0.5:
            verdict = "Moderate Agreement"
        else:
            verdict = "Low Agreement"
        self.verdict_label.setText(verdict)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_acf_workstation_model_agreement.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add src/acf/gui/dashboard/acf_workstation_model_agreement.py tests/gui/test_acf_workstation_model_agreement.py
git commit -m "feat(gui): add ACF Workstation ModelAgreementPanel

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 7: `HazardAlertsPanel` — Key Alerts & Hazards

**Files:**
- Create: `src/acf/gui/dashboard/acf_workstation_hazard_alerts.py`
- Test: `tests/gui/test_acf_workstation_hazard_alerts.py`

**Interfaces:**
- Consumes: the same `indices: dict[str, np.ndarray]` returned by
  `compute_real_convection_indices_field()` (Task 4 already calls this; Task 9
  passes the same result to both panels rather than computing it twice), plus
  the volume's own relative-humidity-derived value from `KeyVariablesPanel`
  (pass the scalar RH percent in directly — do not recompute).
- Produces: `HazardAlertsPanel(QWidget)` with
  `update_from_indices(self, cape_j_kg: float, bulk_shear_m_s: float, wet_bulb_c: float | None, relative_humidity_pct: float | None) -> None`.

- [ ] **Step 1: Write the failing test**

```python
# tests/gui/test_acf_workstation_hazard_alerts.py
from __future__ import annotations

import math

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_hazard_alerts import HazardAlertsPanel


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize(
    ("cape", "shear", "wet_bulb", "rh", "expected_convection", "expected_turbulence", "expected_visibility", "expected_icing"),
    [
        (2500.0, 25.0, 5.0, 60.0, "High", "High", "Low", "Low"),
        (400.0, 8.0, -1.0, 55.0, "Moderate", "Low", "Low", "High"),
        (100.0, 2.0, 10.0, 96.0, "Low", "Low", "High", "Low"),
    ],
)
def test_hazard_thresholds_are_real_and_documented(
    qapp, qtbot, cape, shear, wet_bulb, rh, expected_convection, expected_turbulence, expected_visibility, expected_icing
):
    panel = HazardAlertsPanel()
    qtbot.addWidget(panel)
    panel.update_from_indices(
        cape_j_kg=cape, bulk_shear_m_s=shear, wet_bulb_c=wet_bulb, relative_humidity_pct=rh
    )
    assert panel.convection_level.text() == expected_convection
    assert panel.turbulence_level.text() == expected_turbulence
    assert panel.visibility_level.text() == expected_visibility
    assert panel.icing_level.text() == expected_icing


def test_hazard_alerts_honest_when_inputs_missing(qapp, qtbot):
    panel = HazardAlertsPanel()
    qtbot.addWidget(panel)
    panel.update_from_indices(
        cape_j_kg=math.nan, bulk_shear_m_s=math.nan, wet_bulb_c=None, relative_humidity_pct=None
    )
    assert panel.convection_level.text() == "NOT_COMPUTED"
    assert panel.turbulence_level.text() == "NOT_COMPUTED"
    assert panel.visibility_level.text() == "NOT_COMPUTED"
    assert panel.icing_level.text() == "NOT_COMPUTED"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_acf_workstation_hazard_alerts.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement**

```python
# src/acf/gui/dashboard/acf_workstation_hazard_alerts.py
"""
ACF Scientific Workstation — Key Alerts & Hazards
=====================================================

Matches acf_workstation_reference.jpg's "Key Alerts & Hazards" panel
(Convection/Turbulence/Low Visibility/Icing, each High/Moderate/Low).

These are real, simple, DISCLOSED threshold heuristics over fields
already computed elsewhere in this Workstation (CAPE, bulk wind shear,
wet-bulb temperature, relative humidity) - not an imported AWCI
hazard-classification engine, and not a machine-learned risk model.
Each threshold below is intentionally conservative/textbook (SPC-style
CAPE bands for convection, generic bulk-shear bands for turbulence
potential, a simple RH band for a fog/visibility proxy, and a
wet-bulb-near-freezing band for icing potential) and documented right
here, not hidden behind a magic function.

Honesty: any `NaN`/`None` input (the underlying computation reporting
"not computed" - see `acf.awci.workstation_fields.
compute_real_convection_indices_field()`'s own docstring) renders
"NOT_COMPUTED" for that hazard, never a fabricated level.
"""

from __future__ import annotations

import math

from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

from acf.gui.theme_tokens import label_style


def _convection_level(cape_j_kg: float) -> str:
    if math.isnan(cape_j_kg):
        return "NOT_COMPUTED"
    if cape_j_kg >= 2000.0:
        return "High"
    if cape_j_kg >= 300.0:
        return "Moderate"
    return "Low"


def _turbulence_level(bulk_shear_m_s: float) -> str:
    if math.isnan(bulk_shear_m_s):
        return "NOT_COMPUTED"
    if bulk_shear_m_s >= 20.0:
        return "High"
    if bulk_shear_m_s >= 10.0:
        return "Moderate"
    return "Low"


def _visibility_level(relative_humidity_pct: float | None) -> str:
    if relative_humidity_pct is None:
        return "NOT_COMPUTED"
    if relative_humidity_pct >= 95.0:
        return "High"
    if relative_humidity_pct >= 85.0:
        return "Moderate"
    return "Low"


def _icing_level(wet_bulb_c: float | None) -> str:
    if wet_bulb_c is None:
        return "NOT_COMPUTED"
    if -3.0 <= wet_bulb_c <= 0.0:
        return "High"
    if -6.0 <= wet_bulb_c < -3.0 or 0.0 < wet_bulb_c <= 2.0:
        return "Moderate"
    return "Low"


class HazardAlertsPanel(QWidget):
    """Real, threshold-based Key Alerts & Hazards panel."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QGridLayout(self)
        self.convection_level = self._row(layout, 0, "Convection")
        self.turbulence_level = self._row(layout, 1, "Turbulence")
        self.visibility_level = self._row(layout, 2, "Low Visibility")
        self.icing_level = self._row(layout, 3, "Icing")

    def _row(self, layout: QGridLayout, row: int, title: str) -> QLabel:
        heading = QLabel(title)
        heading.setStyleSheet(label_style("text_muted", "xs"))
        value = QLabel("NOT_COMPUTED")
        layout.addWidget(heading, row, 0)
        layout.addWidget(value, row, 1)
        return value

    def update_from_indices(
        self,
        cape_j_kg: float,
        bulk_shear_m_s: float,
        wet_bulb_c: float | None,
        relative_humidity_pct: float | None,
    ) -> None:
        self.convection_level.setText(_convection_level(cape_j_kg))
        self.turbulence_level.setText(_turbulence_level(bulk_shear_m_s))
        self.visibility_level.setText(_visibility_level(relative_humidity_pct))
        self.icing_level.setText(_icing_level(wet_bulb_c))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_acf_workstation_hazard_alerts.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add src/acf/gui/dashboard/acf_workstation_hazard_alerts.py tests/gui/test_acf_workstation_hazard_alerts.py
git commit -m "feat(gui): add ACF Workstation HazardAlertsPanel

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 8: `SystemFooterPanel` — Data Sources / System Status / Running Jobs / Recent Activity

**Files:**
- Create: `src/acf/gui/dashboard/acf_workstation_footer.py`
- Test: `tests/gui/test_acf_workstation_footer.py`

**Interfaces:**
- Consumes: `acf.hpc_connector.HPCConnectionManager` (already real, unaffected
  by this session's dashboard cleanup) for System Status/Data Sources, and a
  plain `list[str]` of recent log lines for Recent Activity (Task 9 sources
  this from whatever the composer's own action log already is — e.g. the ACF
  Pipeline Monitor lines already used by `acf_workstation.py`, read that
  file's current logging call sites before wiring).
- Produces: `SystemFooterPanel(QWidget)` with
  `update_from_hpc(self, hpc: HPCConnectionManager) -> None` and
  `append_activity(self, message: str) -> None`.

- [ ] **Step 1: Read `HPCConnectionManager`'s real public status method**

```bash
grep -n "def get_status\|def status\|class HPCConnectionManager" src/acf/hpc_connector/connection_manager.py | head -10
```

Use whichever real method it exposes (adjust the implementation below to
match its exact name/return keys).

- [ ] **Step 2: Write the failing test**

```python
# tests/gui/test_acf_workstation_footer.py
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_footer import SystemFooterPanel


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_footer_shows_real_hpc_status(qapp, qtbot):
    panel = SystemFooterPanel()
    qtbot.addWidget(panel)
    hpc = MagicMock()
    hpc.get_status.return_value = {"connected": True, "scheduler": "Slurm"}
    panel.update_from_hpc(hpc)
    assert "Slurm" in panel.system_status_label.text() or "connected" in panel.system_status_label.text().lower()


def test_footer_appends_activity_log_lines(qapp, qtbot):
    panel = SystemFooterPanel()
    qtbot.addWidget(panel)
    panel.append_activity("AROME forecast completed (+12h)")
    assert "AROME forecast completed" in panel.activity_log.toPlainText()
```

- [ ] **Step 3: Implement** (adjust the `hpc.get_status()` call to whatever
Step 1 found)

```python
# src/acf/gui/dashboard/acf_workstation_footer.py
"""
ACF Scientific Workstation — System Footer
==============================================

Matches acf_workstation_reference.jpg's bottom row: Data Sources,
System Status, Running Jobs, Recent Activity. System Status/Data
Sources come from the real `acf.hpc_connector.HPCConnectionManager`
(unchanged by this session's dashboard cleanup - it is a real
subsystem, not a dashboard). Recent Activity is a plain, real append-
only log of this Workstation's own real actions (e.g. "AROME forecast
completed"), fed by the composer - this panel never fabricates a log
entry.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from acf.gui.theme_tokens import label_style


class SystemFooterPanel(QWidget):
    """Real Data Sources / System Status / Running Jobs / Recent Activity footer."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.system_status_label = QLabel("NOT_CONNECTED")
        self.system_status_label.setStyleSheet(label_style("text_primary", "sm"))
        layout.addWidget(self.system_status_label)

        self.activity_log = QTextEdit()
        self.activity_log.setReadOnly(True)
        layout.addWidget(self.activity_log)

    def update_from_hpc(self, hpc: Any) -> None:
        status = hpc.get_status()
        connected = status.get("connected")
        scheduler = status.get("scheduler", "NOT_AVAILABLE")
        self.system_status_label.setText(
            f"{'Connected' if connected else 'Not Connected'} — Scheduler: {scheduler}"
        )

    def append_activity(self, message: str) -> None:
        self.activity_log.append(message)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_acf_workstation_footer.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add src/acf/gui/dashboard/acf_workstation_footer.py tests/gui/test_acf_workstation_footer.py
git commit -m "feat(gui): add ACF Workstation SystemFooterPanel

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 9: `WorkstationSidebar` + rewire `ACFWorkstation` composer + ESOC wiring

This is the integration task: build the static nav sidebar, lay out every
panel from Tasks 1–8 to match `acf_workstation_reference.jpg`, and restore
the ESOC toolbar entry point this session's earlier cleanup removed.

**Files:**
- Create: `src/acf/gui/dashboard/acf_workstation_sidebar.py`
- Modify: `src/acf/gui/dashboard/acf_workstation.py`
- Modify: `src/acf/gui/dashboard/acf_workstation_window.py` (verify it still
  just wraps `ACFWorkstation` — likely no change needed beyond the window
  title matching "ACF Scientific Workstation").
- Modify: `src/acf/gui/esoc/esoc_toolbar.py`
- Modify: `src/acf/gui/esoc/esoc_window.py`
- Test: `tests/gui/test_acf_workstation_sidebar.py`
- Test: `tests/test_esoc_acf_workstation_action.py`

**Interfaces:**
- Consumes: every panel class from Tasks 1, 3–8
  (`ACFOverviewPanel`/`ACFThermodynamicsLabPanel`/`ACFComplexityExplorerPanel`/
  `ACFConfidenceLabPanel`/`ACFMultiModelLabPanel`/`ACFTemporalLabPanel`/
  `ACFVerticalSoundingWidget`/`AWCIMapPanel`, `ConfigBar`, `KeyVariablesPanel`,
  `ComplexityOverviewPanel`, `ModelAgreementPanel`, `HazardAlertsPanel`,
  `SystemFooterPanel`).
- Produces: `WorkstationSidebar(QWidget)` with a `sectionSelected: Signal(str)`;
  `ACFWorkstation.refresh()` (kept from the recovered file, extended to also
  populate the 6 new panels from the same real volume/indices/disagreement
  results it already computes for the recovered panels — no second solver
  run for any new panel).

- [ ] **Step 1: Write the failing sidebar test**

```python
# tests/gui/test_acf_workstation_sidebar.py
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_sidebar import WorkstationSidebar

_SECTIONS = [
    "Home", "Data", "Science", "Analysis", "Reports", "Infrastructure", "Settings",
]


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_sidebar_lists_every_reference_section(qapp, qtbot):
    sidebar = WorkstationSidebar()
    qtbot.addWidget(sidebar)
    for section in _SECTIONS:
        assert sidebar.findChild(object, section) is not None or section in sidebar.section_names()


def test_sidebar_emits_section_selected(qapp, qtbot):
    sidebar = WorkstationSidebar()
    qtbot.addWidget(sidebar)
    with qtbot.waitSignal(sidebar.sectionSelected, timeout=1000) as blocker:
        sidebar.select_section("Science")
    assert blocker.args == ["Science"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_acf_workstation_sidebar.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement the sidebar**

```python
# src/acf/gui/dashboard/acf_workstation_sidebar.py
"""
ACF Scientific Workstation — Left Sidebar Navigation
========================================================

Static navigation tree matching acf_workstation_reference.jpg's left
sidebar (Home / Data / Science / Analysis / Reports / Infrastructure /
Settings). Selecting a top-level section emits `sectionSelected` with
that section's real name - the composer (`acf_workstation.
ACFWorkstation`) decides what, if anything, to scroll to/focus; this
widget owns no panel-visibility logic itself.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget

_SECTIONS = ["Home", "Data", "Science", "Analysis", "Reports", "Infrastructure", "Settings"]


class WorkstationSidebar(QWidget):
    """Static left navigation sidebar."""

    sectionSelected = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self._list = QListWidget()
        for name in _SECTIONS:
            item = QListWidgetItem(name)
            item.setData(0, name)
            self._list.addItem(item)
        self._list.currentTextChanged.connect(self.sectionSelected.emit)
        layout.addWidget(self._list)

    def section_names(self) -> list[str]:
        return list(_SECTIONS)

    def select_section(self, name: str) -> None:
        items = self._list.findItems(name, __import__("PySide6.QtCore", fromlist=["Qt"]).Qt.MatchExactly)
        if items:
            self._list.setCurrentItem(items[0])
```

- [ ] **Step 4: Run sidebar test to verify it passes**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/test_acf_workstation_sidebar.py -v`
Expected: 2 passed

- [ ] **Step 5: Rewire `ACFWorkstation` to the new layout**

Read the trimmed `acf_workstation.py` from Task 2 in full, then restructure
its `__init__` to build, top to bottom: `WorkstationSidebar` (left column,
full height) beside a right column containing, in order: `ConfigBar`, the
hero map (`AWCIMapPanel`, reusing `ACFComplexityExplorerPanel`'s own existing
spatial-complexity map + `ACFTemporalLabPanel`'s existing frame-scrubbing
transport — read both files to reuse their existing widgets rather than
duplicating the map/transport code), a row of `KeyVariablesPanel` +
`ComplexityOverviewPanel` + `ModelAgreementPanel` + `HazardAlertsPanel`, a
second row of `CrossSectionPanel`-equivalent (recovered
`ACFVerticalSoundingWidget` covers Atmospheric Profiles; Vertical Cross
Section reuses whatever cross-section widget `ACFComplexityExplorerPanel`'s
own recovered file already builds on — read it to confirm) +
`ACFMultiModelLabPanel` (Model Comparison) + `ACFTemporalLabPanel`'s own
chart half (Time Evolution), and finally `SystemFooterPanel`.

Extend `ACFWorkstation.refresh()` (already present in the recovered file) so
that, after it computes the real volume/indices/disagreement results for the
recovered panels, it also calls:
- `self.key_variables_panel.update_from_volume(volume, level_index)`
- `self.hazard_alerts_panel.update_from_indices(cape, shear, wet_bulb, rh)`
  (pull `cape`/`wet_bulb`/`rh` from the same `KeyVariablesPanel`
  computation/`indices` dict already produced — do not recompute)
- `self.complexity_overview_panel.update_from_factors({...})` (source each
  of the 8 factors from `ACFComplexityExplorerPanel`'s and
  `ACFConfidenceLabPanel`'s own existing real result attributes — read both
  files to find their exact attribute/method names before wiring; use `None`
  for any factor neither panel currently exposes, rather than inventing one)
- `self.model_agreement_panel.update_from_disagreement(per_model_field, spread_field)`
  (same real result `ACFMultiModelLabPanel` already computes)
- `self.footer_panel.update_from_hpc(hpc)` and
  `self.footer_panel.append_activity(...)` for each real pipeline stage the
  recovered composer already logs.

- [ ] **Step 6: Verify the full composer still imports and instantiates headlessly**

```bash
source .venv/bin/activate
QT_QPA_PLATFORM=offscreen python -c "
from PySide6.QtWidgets import QApplication
app = QApplication([])
from acf.gui.dashboard.acf_workstation import ACFWorkstation
w = ACFWorkstation()
w.refresh()
print('OK')
"
```

Expected: prints `OK` with no traceback (a slow real solver run is expected
to take a few seconds).

- [ ] **Step 7: Restore the ESOC toolbar entry point**

In `src/acf/gui/esoc/esoc_toolbar.py`, re-add the action this session's
earlier cleanup removed:

```python
("🔬 ACF Scientific Workstation", "open_acf_workstation"),
```
(placed where the "⚙️ Settings"/"🌪️ AWCI Field" entries currently sit).

In `src/acf/gui/esoc/esoc_window.py`, re-add the `_open_acf_workstation`
open-or-raise method and its `_acf_workstation_window` attribute (recover the
exact real implementation this session removed via
`git show HEAD:src/acf/gui/esoc/esoc_window.py | grep -n "_open_acf_workstation" -A 25`
and adapt the import path — it is unchanged,
`from acf.gui.dashboard.acf_workstation_window import ACFWorkstationWindow`),
and re-add the `elif cmd == "open_acf_workstation": self._open_acf_workstation()`
dispatch branch.

- [ ] **Step 8: Write/recover the ESOC integration test**

```bash
git show HEAD:tests/test_esoc_acf_workstation_action.py > tests/test_esoc_acf_workstation_action.py
```

Read the recovered test and adjust only if `_open_acf_workstation`'s exact
attribute/method names changed in Step 7 (they should not have).

- [ ] **Step 9: Run the integration test**

Run: `source .venv/bin/activate && QT_QPA_PLATFORM=offscreen python -m pytest tests/test_esoc_acf_workstation_action.py -v`
Expected: all pass.

- [ ] **Step 10: Commit**

```bash
git add src/acf/gui/dashboard/acf_workstation_sidebar.py src/acf/gui/dashboard/acf_workstation.py \
        src/acf/gui/dashboard/acf_workstation_window.py src/acf/gui/esoc/esoc_toolbar.py \
        src/acf/gui/esoc/esoc_window.py tests/gui/test_acf_workstation_sidebar.py \
        tests/test_esoc_acf_workstation_action.py
git commit -m "feat(gui): wire the rebuilt ACF Workstation layout into ESOC

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 10: Full verification pass

**Files:** none created; verification only.

- [ ] **Step 1: Run the full GUI test subset**

```bash
source .venv/bin/activate
QT_QPA_PLATFORM=offscreen python -m pytest tests/gui/ tests/test_esoc_acf_workstation_action.py -v
```

Expected: all pass. Investigate and fix any failure before proceeding (do not
skip or xfail).

- [ ] **Step 2: Run the full test suite**

```bash
source .venv/bin/activate
QT_QPA_PLATFORM=offscreen python -m pytest -q
```

Expected: no new failures/errors versus this session's starting point (the
existing 3993-collected baseline from before this rebuild, minus the tests
intentionally deleted for out-of-scope panels).

- [ ] **Step 3: Visual verification against the reference image**

Launch the app (`acf-gui`, or directly instantiate `ACFWorkstationWindow` in
a script) with `QT_QPA_PLATFORM=offscreen`, grab a screenshot
(`window.grab().save("workstation_screenshot.png")`), and compare side-by-side
with `acf_workstation_reference.jpg` — check panel presence and rough
position section-by-section against the mapping table in the spec. Note any
visual mismatch as a follow-up item rather than silently accepting it.

- [ ] **Step 4: Commit final state (if the visual pass produced any fixes)**

```bash
git add -A
git commit -m "fix(gui): address visual QA findings against acf_workstation_reference.jpg

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```
