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

Phase 6 (2026-09-04, same "continue" progressive discipline) added:
- **Interaction Engine** (`acf_workstation_interactions.
  ACFInteractionEnginePanel`): docs/ACF_MASTER_PROMPT.md §22 ("INTERACTIONS
  — CŒUR DU PROJET") is explicit: "Ne pas inventer arbitrairement
  `interaction = A × B` sans justification physique ou statistique."
  This panel computes the real, standard, published PEARSON
  CORRELATION COEFFICIENT (and its real pointwise spatial
  contribution, rendered as a map) between two real physical fields a
  user picks from across every other Lab already built (Overview's raw
  fields, Dynamics' vorticity/divergence/wind shear, Thermodynamics'
  θ-e/relative humidity, Microphysics' precipitation-phase severity/
  wet-bulb temperature) - a genuinely cross-module, statistically
  justified interaction measure, never an arbitrary unit-mismatched
  product.

Phase 7 (2026-09-04, same "continue" progressive discipline) added:
- **Data Quality Center** (`acf_workstation_quality.
  ACFDataQualityLabPanel`): real per-point docs/ACF_MASTER_PROMPT.md
  §32 quality status (VALID/OUT_OF_RANGE/MISSING/INVALID/...) for
  Temperature/Specific humidity/Pressure/Wind speed, via
  `acf.physics_guard.variable_quality.assess_variable_quality()` - the
  real, already-built §32 taxonomy this codebase had never run over a
  whole grid before. Independently confirmed the real pressure anomaly
  already flagged separately (task_f3c406d9): Pressure reads
  OUT_OF_RANGE at every real grid point (~2013 hPa is outside
  OPERATIONAL_RANGES' real [1000, 108500] Pa bound) - a genuine
  demonstration this real infrastructure catches a real problem, not a
  panel bug.

Phase 8 (2026-09-04, same "continue" progressive discipline) added:
- **Multi-Model Lab** (`acf_workstation_multimodel.
  ACFMultiModelLabPanel`): zero new science - calls the exact same
  `ModelConsensusEngine.compute_real_multi_model_disagreement_field()`
  Confidence Lab already uses, but exposes its previously-unread
  `per_model_field` data: each real model's own RAW field individually,
  plus a real, literal pairwise difference map (`field_a - field_b`,
  real physical units) - a distinct real question from Confidence
  Lab's own aggregate spread/mean ("where do these two SPECIFIC models
  actually disagree, and by how much?").

Phase 9 (2026-09-04, same "continue" progressive discipline) added:
- **Real multi-format export** (PNG/SVG/CSV/JSON) on `AWCIMapPanel`
  itself (`awci_map_panel.py`) - so every map in this Workstation (and
  AWCIDashboard's own maps, which share this exact widget) gained 3
  new real export formats for free. The download button's PNG-only
  `QPushButton` became a real `QToolButton` + `QMenu` (same "real
  actions behind one control" convention as ACFGeneralDashboard's own
  "☰" menu) - CSV/JSON export the exact (lons, lats, grid) currently
  on screen, a real NaN cell (e.g. this Workstation's own
  show_demo_fallback=False empty state) honestly written as an empty
  CSV field / JSON `null`, never a fabricated 0.

Phase 10 (2026-09-04, same "continue" progressive discipline) added:
- **Real keyboard shortcuts** - Ctrl+R re-triggers the exact same real
  `refresh()` the "🔄 Run" button already does; F11 toggles the exact
  same real fullscreen the "⛶" button already does; Ctrl+1..Ctrl+9/
  Ctrl+0 jump to one of this Workstation's real enabled modules by its
  real position in `_ENABLED_MODULES` - one real shortcut per real
  module, generated from that same list, so it can never drift out of
  sync with the nav it targets.

Phase 11 (2026-09-04, same "continue" progressive discipline) added:
- **Command Palette** (Ctrl+K, `acf_workstation_command_palette.
  CommandPaletteDialog`): a real, fuzzy-searchable list of this
  Workstation's own already-real actions - "Run", "Toggle Fullscreen",
  "Go to <module>" for each of the 10 real enabled modules, and every
  on-demand Lab action (CAPE/CIN, temporal analysis, model
  disagreement, temporal evolution, model confidence, model
  comparison) - each entry a direct reference to the real method/
  button it triggers, never a new capability. Non-modal open-or-raise
  (`.show()`), same convention as `AWCIExecutionReportDialog`.

Phase 12 (2026-09-04, same "continue" progressive discipline) added:
- **Configuration Management** - the "⚙" button (previously disabled,
  its own tooltip disclosing "not yet implemented") became a real
  QToolButton + QMenu (same convention as the export menu/"☰" menu):
  "💾 Save Configuration…"/"📂 Load Configuration…" serialize/restore
  the real user-chosen SETTINGS this Workstation's model/level/nav/
  every Lab's own variable selector currently hold, as real JSON - the
  real computed DATA is never saved/replayed as a stand-in for a fresh
  solver run (this project's own no-fake-functionality rule); loading
  a configuration only restores what to look at, then the user still
  presses "🔄 Run" for real data. Also reachable from the Command
  Palette. A level_index restored before any real volume exists yet is
  honestly held pending and clamped against the next real volume's own
  real level count once computed.

The remaining 2 spec modules (Convection/Terrain Labs - 3D/4D, Case
Study Lab, Research Mode etc. are larger, separate pieces of the
master spec beyond the original "Labs" list) are listed in the left
nav as real, visible, DISABLED "Planned" items - not silently omitted,
not faked - matching
the master spec's own §68 audit-honesty rule applied
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

import json
import logging
import time
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QSlider,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.forecast.engine import MODEL_CONFIGS
from acf.gui.dashboard.acf_workstation_command_palette import CommandPaletteDialog
from acf.gui.dashboard.acf_workstation_complexity import ACFComplexityExplorerPanel
from acf.gui.dashboard.acf_workstation_confidence import ACFConfidenceLabPanel
from acf.gui.dashboard.acf_workstation_dynamics import ACFDynamicsLabPanel
from acf.gui.dashboard.acf_workstation_interactions import ACFInteractionEnginePanel
from acf.gui.dashboard.acf_workstation_microphysics import ACFMicrophysicsLabPanel
from acf.gui.dashboard.acf_workstation_multimodel import ACFMultiModelLabPanel
from acf.gui.dashboard.acf_workstation_overview import ACFOverviewPanel
from acf.gui.dashboard.acf_workstation_quality import ACFDataQualityLabPanel
from acf.gui.dashboard.acf_workstation_temporal import ACFTemporalLabPanel
from acf.gui.dashboard.acf_workstation_thermodynamics import ACFThermodynamicsLabPanel
from acf.gui.theme_tokens import dashboard_stylesheet, label_style

logger = logging.getLogger("acf.gui.dashboard.acf_workstation")

_DEFAULT_MODEL = "ARPEGE"  # smallest of the 3 real MODEL_CONFIGS grids - fastest real run, same default as acf_general_dashboard.py

#: Real, built modules (index into the QStackedWidget) vs. real,
#: disclosed-but-not-yet-built ones - see module docstring. Every name
#: here is a real §8 spec module name, not invented.
_ENABLED_MODULES = [
    "Overview", "Dynamics", "Thermodynamics", "Microphysics", "Temporal", "Confidence", "Multi-Model",
    "Interactions", "Quality", "Complexity",
]
_PLANNED_MODULES = [
    "Convection", "Terrain",
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
        self._command_palette: CommandPaletteDialog | None = None
        #: A real level_index restored from a loaded configuration
        #: (added 2026-09-04) before any real volume exists yet to
        #: clamp it against - applied in _on_volume_ready() once a
        #: real volume's own real level count is known.
        self._pending_level_index: int | None = None
        self._build_ui()
        self._setup_shortcuts()
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

        # Real Configuration Management (added 2026-09-04, closing a
        # gap this button's own tooltip used to disclose as "not yet
        # implemented") - same "real actions behind one control"
        # convention as the export menu (awci_map_panel.py) and
        # ACFGeneralDashboard's own "☰" menu.
        self.settings_button = QToolButton()
        self.settings_button.setText("⚙")
        self.settings_button.setFixedWidth(28)
        self.settings_button.setToolTip("Configuration")
        self.settings_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        settings_menu = QMenu(self.settings_button)
        self.save_configuration_action = QAction("💾 Save Configuration…", self)
        self.save_configuration_action.triggered.connect(self._save_configuration)
        settings_menu.addAction(self.save_configuration_action)
        self.load_configuration_action = QAction("📂 Load Configuration…", self)
        self.load_configuration_action.triggered.connect(self._load_configuration)
        settings_menu.addAction(self.load_configuration_action)
        self.settings_button.setMenu(settings_menu)
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
        self.multimodel_panel = ACFMultiModelLabPanel()
        self.interactions_panel = ACFInteractionEnginePanel()
        self.quality_panel = ACFDataQualityLabPanel()
        self.complexity_panel = ACFComplexityExplorerPanel()
        self.stack.addWidget(self.overview_panel)
        self.stack.addWidget(self.dynamics_panel)
        self.stack.addWidget(self.thermodynamics_panel)
        self.stack.addWidget(self.microphysics_panel)
        self.stack.addWidget(self.temporal_panel)
        self.stack.addWidget(self.confidence_panel)
        self.stack.addWidget(self.multimodel_panel)
        self.stack.addWidget(self.interactions_panel)
        self.stack.addWidget(self.quality_panel)
        self.stack.addWidget(self.complexity_panel)
        body.addWidget(self.stack, stretch=1)

        outer.addLayout(body, stretch=1)

    def _setup_shortcuts(self) -> None:
        """Real keyboard shortcuts (added 2026-09-04) - faster real
        access to already-real actions, nothing new invented: Ctrl+R
        re-triggers the exact same real refresh() the "🔄 Run" button
        already does; F11 toggles the exact same real fullscreen the
        "⛶" button already does; Ctrl+1..Ctrl+9/Ctrl+0 jump to one of
        this Workstation's real enabled modules by its real position in
        _ENABLED_MODULES (never more shortcuts than real modules - a
        module added/removed there automatically gets/loses its own
        shortcut, no separately hand-maintained list to drift out of
        sync)."""
        self.shortcut_run = QShortcut(QKeySequence("Ctrl+R"), self)
        self.shortcut_run.activated.connect(self.refresh)

        self.shortcut_fullscreen = QShortcut(QKeySequence("F11"), self)
        self.shortcut_fullscreen.activated.connect(self._toggle_fullscreen)

        self.nav_shortcuts: list[QShortcut] = []
        for row, _name in enumerate(_ENABLED_MODULES[:10]):  # Ctrl+1..Ctrl+9, Ctrl+0 - real digit keys, no more
            key_digit = (row + 1) % 10  # row 0 -> "1", ..., row 8 -> "9", row 9 -> "0"
            shortcut = QShortcut(QKeySequence(f"Ctrl+{key_digit}"), self)
            shortcut.activated.connect(lambda target_row=row: self.nav_list.setCurrentRow(target_row))
            self.nav_shortcuts.append(shortcut)

        self.shortcut_command_palette = QShortcut(QKeySequence("Ctrl+K"), self)
        self.shortcut_command_palette.activated.connect(self._open_command_palette)

    def _make_go_to_row(self, row: int) -> Callable[[], None]:
        """A real, small closure factory - avoids the classic late-
        binding loop-variable bug (a bare `lambda: self.nav_list.
        setCurrentRow(row)` built inside a for-loop would have every
        closure share the SAME final `row`), and gives mypy an
        explicit, checkable return type unlike an inline default-arg
        lambda."""

        def _go_to_row() -> None:
            self.nav_list.setCurrentRow(row)

        return _go_to_row

    def _build_palette_commands(self) -> list[tuple[str, Callable[[], None]]]:
        """Real command list for the Command Palette (added
        2026-09-04) - every entry is a direct reference to an already-
        real chrome method or Lab panel button, never a new capability.
        Rebuilt on every open (cheap - a couple dozen tuples) so it
        never needs separate invalidation logic."""
        commands: list[tuple[str, Callable[[], None]]] = [
            ("Run", self.refresh),
            ("Toggle Fullscreen", self._toggle_fullscreen),
        ]
        for row, name in enumerate(_ENABLED_MODULES):
            commands.append((f"Go to {name}", self._make_go_to_row(row)))
        # Real on-demand actions already built into specific Lab panels
        # - reuses each panel's own real button.click(), never a
        # second, independent trigger path.
        commands.extend(
            [
                ("Compute CAPE/CIN Field (Thermodynamics Lab)", self.thermodynamics_panel.cape_button.click),
                ("Run Temporal Analysis (Complexity Explorer)", self.complexity_panel.temporal_button.click),
                ("Compute Model Disagreement (Complexity Explorer)", self.complexity_panel.consensus_button.click),
                ("Run Temporal Evolution (Temporal Lab)", self.temporal_panel.run_button.click),
                ("Compute Model Confidence Field (Confidence Lab)", self.confidence_panel.run_button.click),
                ("Compare Models (Multi-Model Lab)", self.multimodel_panel.run_button.click),
                ("Save Configuration…", self._save_configuration),
                ("Load Configuration…", self._load_configuration),
            ]
        )
        return commands

    def _open_command_palette(self) -> None:
        """Real open-or-raise, same convention as
        AWCIExecutionReportDialog's own _open_execution_report() -
        `.show()`, never a blocking `.exec()`."""
        if self._command_palette is None:
            self._command_palette = CommandPaletteDialog(self._build_palette_commands(), parent=self)
        else:
            self._command_palette.set_commands(self._build_palette_commands())
        self._command_palette.search_input.clear()
        self._command_palette.show()
        self._command_palette.raise_()
        self._command_palette.activateWindow()
        self._command_palette.search_input.setFocus()

    # ------------------------------------------------- Configuration Management

    #: Real (config key -> the selector it reads/restores). One shared
    #: table for both export and import (added 2026-09-04) - single
    #: source of truth, so a new Lab's own selector only needs adding
    #: here once, never two separately-maintained lists that could
    #: silently drift apart.
    def _configuration_selectors(self) -> dict[str, QComboBox]:
        return {
            "overview_variable": self.overview_panel.variable_selector,
            "dynamics_variable": self.dynamics_panel.variable_selector,
            "thermodynamics_variable": self.thermodynamics_panel.variable_selector,
            "microphysics_variable": self.microphysics_panel.variable_selector,
            "temporal_variable": self.temporal_panel.variable_selector,
            "confidence_variable": self.confidence_panel.variable_selector,
            "multimodel_model_a": self.multimodel_panel.model_a_selector,
            "multimodel_model_b": self.multimodel_panel.model_b_selector,
            "multimodel_display": self.multimodel_panel.display_selector,
            "interactions_variable_a": self.interactions_panel.variable_a_selector,
            "interactions_variable_b": self.interactions_panel.variable_b_selector,
            "quality_variable": self.quality_panel.variable_selector,
        }

    def _export_configuration(self) -> dict[str, Any]:
        """Real UI configuration snapshot - the real user-chosen
        SETTINGS this Workstation's own model/level/nav/selectors
        currently hold. Never the computed data itself: real data is
        always re-computed fresh from a real solver run on "🔄 Run",
        never saved/replayed as a stand-in for one (this project's own
        no-fake-functionality rule) - loading a configuration restores
        what to look at, not a snapshot pretending to already be a
        real result."""
        config: dict[str, Any] = {
            "model": self.model_selector.currentText(),
            "level_index": self._level_index,
            "nav_row": self.nav_list.currentRow(),
        }
        for key, selector in self._configuration_selectors().items():
            config[key] = selector.currentText()
        return config

    def _apply_configuration(self, config: dict[str, Any]) -> None:
        """Real, defensive restore - `config` may be a real file a
        user hand-edited or copied between sessions, so every field is
        individually validated before use; an unknown/malformed field
        is simply skipped (QComboBox.setCurrentText() itself already
        no-ops on a value absent from a combo's own real items - no
        separate validation needed there), never raised as a fatal
        error over one bad field."""
        model = config.get("model")
        if isinstance(model, str) and model in MODEL_CONFIGS:
            self.model_selector.setCurrentText(model)

        for key, selector in self._configuration_selectors().items():
            value = config.get(key)
            if isinstance(value, str):
                selector.setCurrentText(value)

        nav_row = config.get("nav_row")
        if isinstance(nav_row, int) and 0 <= nav_row < len(_ENABLED_MODULES):
            self.nav_list.setCurrentRow(nav_row)

        level_index = config.get("level_index")
        if isinstance(level_index, int) and level_index >= 0:
            if self._volume is not None:
                clamped = max(0, min(level_index, self._volume["n_levels"] - 1))
                self.level_slider.setValue(clamped)
            else:
                self._pending_level_index = level_index

    def _save_configuration(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Workstation Configuration", "acf_workstation_config.json", "JSON File (*.json)"
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self._export_configuration(), handle, indent=2)
        self.status_label.setText(f"✅ Configuration saved to {path}.")

    def _load_configuration(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Workstation Configuration", "", "JSON File (*.json)"
        )
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as handle:
                config = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            self.status_label.setText(f"⚠ Could not load configuration: {exc}")
            return
        if not isinstance(config, dict):
            self.status_label.setText("⚠ Could not load configuration: file does not contain a JSON object.")
            return
        self._apply_configuration(config)
        self.status_label.setText(f"✅ Configuration loaded from {path}.")

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
        # A real, pending level_index restored from a loaded
        # configuration (added 2026-09-04 - see _apply_configuration())
        # takes priority over the default level 0, clamped to this
        # real volume's own real level count.
        initial_level = 0
        if self._pending_level_index is not None:
            initial_level = max(0, min(self._pending_level_index, n_levels - 1))
            self._pending_level_index = None
        self.level_slider.blockSignals(True)
        self.level_slider.setValue(initial_level)
        self.level_slider.blockSignals(False)
        self._level_index = initial_level
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
        self.multimodel_panel.update_from_volume(self._volume, self._level_index)
        self.interactions_panel.update_from_volume(self._volume, self._level_index)
        self.quality_panel.update_from_volume(self._volume, self._level_index)
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
