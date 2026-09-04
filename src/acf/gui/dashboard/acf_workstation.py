"""
ACF Scientific Workstation
============================

Real, AWCI-free "ACF Core" dashboard (built 2026-09-04, explicit user
request/master spec: "ACF CORE ONLY — NO AWCI" — a dashboard exposing
ACF's own modular atmospheric science - Dynamics, Thermodynamics,
Convection, Microphysics, Terrain, Temporal Evolution, Forecast
Confidence, an Interaction Engine, and a multidimensional Complexity
Explorer - never a single AWCI-style score/gauge/classification).
Matches the user's own reference photo,
`docs/reference/acf_dashboard_reference.jpg` (same file already used
by the *different*, AWCI-coupled `acf_general_dashboard.
ACFGeneralDashboard`, which this Workstation now replaces as ESOC's
"ACF Dashboard" entry point - see `acf_general_dashboard.py`'s own
NOTE for that history; it is not deleted, per project convention).

Phase 1 scope (2026-09-04) — a real, working chrome plus 3 real
content modules, all sliced from a SINGLE real solver run:
- **Overview** (`acf_workstation_overview.ACFOverviewPanel`): real
  Temperature/Wind speed/Specific humidity/Pressure fields.
- **Dynamics Lab** (`acf_workstation_dynamics.ACFDynamicsLabPanel`):
  real wind speed, real vorticity, real divergence.
- **Complexity Explorer** (`acf_workstation_complexity.
  ACFComplexityExplorerPanel`): real spatial/temporal/model-
  disagreement complexity dimensions, shown separately, never
  combined into one score.

Phase 2 (2026-09-04, same "continue" progressive discipline) added:
- **Thermodynamics Lab** (`acf_workstation_thermodynamics.
  ACFThermodynamicsLabPanel`): real θ-e (equivalent potential
  temperature)/relative humidity (auto, from the current level) and
  real CAPE/CIN from an actual MetPy parcel ascent (on-demand, a
  coarser real grid - see that module's own docstring for why).

Phase 3 (2026-09-04, same "continue" progressive discipline) added:
- **Microphysics Lab** (`acf_workstation_microphysics.
  ACFMicrophysicsLabPanel`): real surface precipitation-phase
  severity/wet-bulb temperature (auto, from the current level), via
  `acf.awci.hydrometeor_phase`'s own already-real, self-disclosed
  heuristic classification - no new species fabricated.
- **Dynamics Lab** gained a 4th real variable: bulk wind shear (full
  column, independent of the level slider), via
  `acf.awci.wind_shear.compute_real_wind_shear_at_point()`.

Phase 4 (2026-09-04, same "continue" progressive discipline) added:
- **Temporal Evolution Lab** (`acf_workstation_temporal.
  ACFTemporalLabPanel`): a real frame slider scrubbing through an
  actual multi-frame `CoupledEarthSolver` trajectory (on-demand, the
  SAME real `compute_real_complexity_evolution()` engine Complexity
  Explorer's own "Run Temporal Analysis" button already uses, but
  exposing the full real trajectory instead of one aggregated
  rate-of-change map).

Phase 5 (2026-09-04, same "continue" progressive discipline) added:
- **Confidence Lab** (`acf_workstation_confidence.
  ACFConfidenceLabPanel`): a real, full-grid multi-model disagreement
  map (spread/mean, never a single 0-100 confidence score), via a new
  `ModelConsensusEngine.compute_real_multi_model_disagreement_field()`
  classmethod - a real extension of the SAME engine Complexity
  Explorer's own "Compute Model Disagreement" button already uses at
  one point, here run over an entire real grid (measured ~0.9s for 2
  models) - the investigation deferred from Phase 4 found this
  genuinely feasible, not prohibitively expensive.

The remaining ~3 spec modules (Convection/Terrain Labs, Interaction
Engine, Multi-Model Lab, Data Quality Center, 3D/4D, Case Study Lab,
Research Mode, Configuration Management...) are listed in the left nav
as real, visible, DISABLED "Planned" items - not silently omitted, not
faked - matching the master spec's own §68 audit-honesty rule applied
in both directions: never claim something works when it's only
simulated, and never hide real future scope either. See the plan this
was built from (`reports/ACF_MASTER_AUDIT_v2.md`'s own dated entries)
for the full, disclosed rationale and what's deferred. Convection Lab
specifically was considered and deliberately deferred rather than
built as a thin wrapper: the one real, well-established formula
available for it (`acf.awci.updraft.
compute_real_max_updraft_velocity()`, w_max = sqrt(2*CAPE)) is, by
that module's own docstring, "a purely deterministic, monotonic
function of CAPE alone" - it "carries no real information CAPE itself
did not already carry" (already shown in Thermodynamics Lab) - a
genuine Convection Lab worth building deserves a real, independent
published composite index (e.g. SCP/STP, which need real
storm-relative helicity/effective shear this codebase does not yet
compute at every grid point), not a thin re-presentation of existing
data. Terrain Lab was considered and deliberately deferred too:
`acf.awci.orographic_froude`'s own docstring already discloses that
`CoupledEarthSolver`'s real state "has no terrain-elevation field at
all" and no real geometric height coordinate - a real Terrain Lab
would need either a real external elevation dataset (none exists in
this codebase today) or fabricated terrain, so it stays honestly
"(planned)" rather than built on invented elevation data.

Real data source, once, re-sliced everywhere
-----------------------------------------------
A real off-thread `_VolumeWorker` runs
`acf.awci.vertical_field.compute_real_complexity_volume()` (a real
`CoupledEarthSolver` run at AROME/ALADIN/ARPEGE's own real
`MODEL_CONFIGS` grid - the exact 3 real names the reference photo's
own Model chip shows) on "🔄 Run" or a Model-selector change. Every
content panel re-slices the SAME resulting volume (compute once,
re-slice per tab/level, this codebase's own established discipline -
`AWCIDashboard`/`ACFGeneralDashboard` already use it) - never a second
solver run per tab switch. Only the volume's real physical fields
(`temperature_volume`/`wind_speed_volume`/`u_volume`/`v_volume`/
`specific_humidity_volume`/`pressure_volume_hpa`) are ever read;
`awci_volume`/`physical_volume`/`forecast_volume` are never touched.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSlider,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.forecast.engine import MODEL_CONFIGS
from acf.gui.dashboard.acf_workstation_complexity import ACFComplexityExplorerPanel
from acf.gui.dashboard.acf_workstation_confidence import ACFConfidenceLabPanel
from acf.gui.dashboard.acf_workstation_dynamics import ACFDynamicsLabPanel
from acf.gui.dashboard.acf_workstation_microphysics import ACFMicrophysicsLabPanel
from acf.gui.dashboard.acf_workstation_overview import ACFOverviewPanel
from acf.gui.dashboard.acf_workstation_temporal import ACFTemporalLabPanel
from acf.gui.dashboard.acf_workstation_thermodynamics import ACFThermodynamicsLabPanel
from acf.gui.theme_tokens import dashboard_stylesheet, label_style

logger = logging.getLogger("acf.gui.dashboard.acf_workstation")

_DEFAULT_MODEL = "ARPEGE"  # smallest of the 3 real MODEL_CONFIGS grids - fastest real run, same default as acf_general_dashboard.py

#: Real, built modules (index into the QStackedWidget) vs. real,
#: disclosed-but-not-yet-built ones - see module docstring. Every name
#: here is a real §8 spec module name, not invented.
_ENABLED_MODULES = ["Overview", "Dynamics", "Thermodynamics", "Microphysics", "Temporal", "Confidence", "Complexity"]
_PLANNED_MODULES = [
    "Convection", "Terrain", "Interactions",
]


class _VolumeWorkerSignals(QObject):
    finished = Signal(dict)
    failed = Signal(str)


class _VolumeWorker(QRunnable):
    """Runs compute_real_complexity_volume() off the GUI thread - same
    real QRunnable/QThreadPool pattern used throughout this codebase's
    other dashboards."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.kwargs = kwargs
        self.signals = _VolumeWorkerSignals()

    def run(self) -> None:
        try:
            result = compute_real_complexity_volume(**self.kwargs)
        except Exception as exc:  # noqa: BLE001 - real failure, reported honestly via signal below
            logger.exception("ACF Scientific Workstation: volume computation failed")
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)


class ACFWorkstation(QWidget):
    """The real ACF Scientific Workstation - see module docstring."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._volume: dict[str, Any] | None = None
        self._level_index = 0
        self._compute_started_at: float | None = None
        self._build_ui()
        self.setStyleSheet(dashboard_stylesheet())
        # Honest, disclosed choice, same convention as AWCIDashboard/
        # ACFGeneralDashboard's own constructors: no real background
        # computation starts merely from constructing this widget - the
        # panels open in their real "Not yet computed" state until the
        # user (or the hosting window, on open) triggers "🔄 Run".

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setSpacing(8)
        outer.setContentsMargins(10, 10, 10, 0)

        # --- Top bar -----------------------------------------------------
        top_bar = QHBoxLayout()
        header = QLabel("ACF SCIENTIFIC WORKSTATION")
        header.setStyleSheet(label_style("text_primary", "lg", "bold"))
        top_bar.addWidget(header)
        top_bar.addStretch()

        top_bar.addWidget(self._label("Model:"))
        self.model_selector = QComboBox()
        self.model_selector.addItems(list(MODEL_CONFIGS.keys()))
        self.model_selector.setCurrentText(_DEFAULT_MODEL)
        top_bar.addWidget(self.model_selector)

        self.run_button = QPushButton("🔄 Run")
        self.run_button.setToolTip(
            "Real, off-thread compute_real_complexity_volume() run (CoupledEarthSolver,\n"
            "the selected model's own real grid configuration) - drives every real\n"
            "module below from one real trajectory, re-sliced, never recomputed per tab."
        )
        self.run_button.clicked.connect(self.refresh)
        top_bar.addWidget(self.run_button)

        self.fullscreen_button = QPushButton("⛶")
        self.fullscreen_button.setToolTip("Toggle fullscreen")
        self.fullscreen_button.setFixedWidth(28)
        self.fullscreen_button.clicked.connect(self._toggle_fullscreen)
        top_bar.addWidget(self.fullscreen_button)

        self.settings_button = QPushButton("⚙")
        self.settings_button.setFixedWidth(28)
        self.settings_button.setEnabled(False)
        self.settings_button.setToolTip("Settings — not yet implemented")
        top_bar.addWidget(self.settings_button)
        outer.addLayout(top_bar)

        # --- Status + level row -------------------------------------------
        status_row = QHBoxLayout()
        self.status_label = QLabel("Not yet computed.")
        self.status_label.setStyleSheet(label_style("text_muted", "sm"))
        status_row.addWidget(self.status_label, stretch=1)

        status_row.addWidget(self._label("Level:"))
        self.level_slider = QSlider(Qt.Orientation.Horizontal)
        self.level_slider.setMinimum(0)
        self.level_slider.setMaximum(0)
        self.level_slider.setEnabled(False)
        self.level_slider.setFixedWidth(160)
        self.level_slider.valueChanged.connect(self._on_level_changed)
        status_row.addWidget(self.level_slider)
        self.level_label = QLabel("—")
        self.level_label.setStyleSheet(label_style("text_secondary", "xs"))
        status_row.addWidget(self.level_label)
        outer.addLayout(status_row)

        # --- Body: left nav + stacked real content -------------------------
        body = QHBoxLayout()
        body.setSpacing(8)

        nav_col = QVBoxLayout()
        nav_header = QLabel("ACF CORE")
        nav_header.setStyleSheet(label_style("text_secondary", "sm", "bold"))
        nav_col.addWidget(nav_header)
        self.nav_list = QListWidget()
        self.nav_list.setMaximumWidth(180)
        for name in _ENABLED_MODULES:
            self.nav_list.addItem(QListWidgetItem(name))
        for name in _PLANNED_MODULES:
            item = QListWidgetItem(f"{name} (planned)")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            item.setToolTip("Planned — not yet built (see the real, disclosed roadmap in reports/ACF_MASTER_AUDIT_v2.md)")
            self.nav_list.addItem(item)
        self.nav_list.setCurrentRow(0)
        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        nav_col.addWidget(self.nav_list, stretch=1)
        body.addLayout(nav_col)

        self.stack = QStackedWidget()
        self.overview_panel = ACFOverviewPanel()
        self.dynamics_panel = ACFDynamicsLabPanel()
        self.thermodynamics_panel = ACFThermodynamicsLabPanel()
        self.microphysics_panel = ACFMicrophysicsLabPanel()
        self.temporal_panel = ACFTemporalLabPanel()
        self.confidence_panel = ACFConfidenceLabPanel()
        self.complexity_panel = ACFComplexityExplorerPanel()
        self.stack.addWidget(self.overview_panel)
        self.stack.addWidget(self.dynamics_panel)
        self.stack.addWidget(self.thermodynamics_panel)
        self.stack.addWidget(self.microphysics_panel)
        self.stack.addWidget(self.temporal_panel)
        self.stack.addWidget(self.confidence_panel)
        self.stack.addWidget(self.complexity_panel)
        body.addWidget(self.stack, stretch=1)

        outer.addLayout(body, stretch=1)

    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(label_style("text_muted", "xs"))
        return lbl

    # --------------------------------------------------------------- volume

    def refresh(self) -> None:
        """Real, off-thread compute_real_complexity_volume() run - see
        module docstring."""
        self.run_button.setEnabled(False)
        model = self.model_selector.currentText()
        self.status_label.setText(f"⏳ Computing real ACF volume ({model} grid, CoupledEarthSolver)…")
        self._compute_started_at = time.monotonic()
        config = MODEL_CONFIGS[model]
        worker = _VolumeWorker(
            model=model, n_lat=config["n_lat"], n_lon=config["n_lon"], n_levels=config["n_levels"],
            steps=6, dt_seconds=90.0, perturbation_scale=3.0, seed=1,
        )
        worker.signals.finished.connect(self._on_volume_ready)
        worker.signals.failed.connect(self._on_volume_failed)
        QThreadPool.globalInstance().start(worker)

    def _on_volume_ready(self, volume: dict[str, Any]) -> None:
        self.run_button.setEnabled(True)
        self._volume = volume
        elapsed = time.monotonic() - self._compute_started_at if self._compute_started_at else 0.0
        # Honest, real status - never a fabricated forecast run-ID/valid-time
        # (this is a live solver run, not an archived NWP product).
        self.status_label.setText(
            f"✅ Live CoupledEarthSolver run ({volume['model']} grid, {volume['n_levels']} real levels) "
            f"— computed in {elapsed:.1f}s."
        )

        n_levels = volume["n_levels"]
        self.level_slider.setMaximum(max(0, n_levels - 1))
        self.level_slider.setEnabled(True)
        self.level_slider.blockSignals(True)
        self.level_slider.setValue(0)
        self.level_slider.blockSignals(False)
        self._level_index = 0
        self._update_level_label()
        self._render_all_panels()

    def _on_volume_failed(self, message: str) -> None:
        self.run_button.setEnabled(True)
        self.status_label.setText(f"⚠ Real volume computation failed: {message}")
        logger.error("ACF Scientific Workstation: volume computation failed: %s", message)

    def _on_level_changed(self, value: int) -> None:
        self._level_index = value
        self._update_level_label()
        self._render_all_panels()

    def _update_level_label(self) -> None:
        if self._volume is None:
            self.level_label.setText("—")
            return
        mean_pressure = float(self._volume["pressure_volume_hpa"][self._level_index].mean())
        self.level_label.setText(f"~{mean_pressure:.0f} hPa (native level {self._level_index + 1}/{self._volume['n_levels']})")

    def _render_all_panels(self) -> None:
        if self._volume is None:
            return
        self.overview_panel.update_from_volume(self._volume, self._level_index)
        self.dynamics_panel.update_from_volume(self._volume, self._level_index)
        self.thermodynamics_panel.update_from_volume(self._volume, self._level_index)
        self.microphysics_panel.update_from_volume(self._volume, self._level_index)
        self.temporal_panel.update_from_volume(self._volume, self._level_index)
        self.confidence_panel.update_from_volume(self._volume, self._level_index)
        self.complexity_panel.update_from_volume(self._volume, self._level_index)

    # ----------------------------------------------------------------- nav

    def _on_nav_changed(self, row: int) -> None:
        if row < 0 or row >= len(_ENABLED_MODULES):
            return
        self.stack.setCurrentIndex(row)

    def _toggle_fullscreen(self) -> None:
        window = self.window()
        if window.isFullScreen():
            window.showNormal()
        else:
            window.showFullScreen()

    def status(self) -> dict[str, Any]:
        return {"has_volume": self._volume is not None, "level_index": self._level_index}
