"""
ACF General Dashboard
=======================

NOTE (correction, 2026-09-04): despite this module's own "not AWCI-
specific" framing below, a real audit (prompted by the user's own new
"ACF Scientific Workstation — ACF CORE ONLY, NO AWCI" master spec)
found this dashboard genuinely is AWCI-coupled throughout -
`_render_frame()` calls `AWCICalculator().calculate()` directly,
`self.radar` is fed AWCI's own fixed 6-module `module_scores`, the
"Dominant couplings" label reads AWCI's own `interaction_scores`, and
the uncertainty gauge uses `Normalizer.normalize_model_disagreement()`
- not a cosmetic naming issue. `acf.gui.dashboard.acf_workstation.
ACFWorkstation` is the real, genuinely AWCI-free replacement, and is
now ESOC's own "ACF Dashboard" toolbar target instead of this class
(see `esoc_window.py`'s own NOTE). This class is NOT deleted - real,
tested, working code, kept per project convention (the same "not
deleted, flagged" precedent as e.g. `AWCITimeline`'s own history) -
just no longer ESOC's primary entry point for "the ACF dashboard".

ACF General Dashboard (superseded - see NOTE above)
=======================================================

Real, general ACF dashboard - explicit user request ("vasy respecte
le prompt"), matching docs/ACF_MASTER_PROMPT.md sections 27-29
(multi-view dashboard, layer architecture) and the user's own real
reference mockup, docs/reference/acf_dashboard_reference.jpg
("ATMOSPHERIC COMPLEXITY FRAMEWORK (ACF) — AWCI RESEARCH SUITE").
Distinct from acf.gui.dashboard.awci_dashboard.AWCIDashboard (built
against its own separate reference mockup earlier this session) - this
is ACF's general, multi-lead-time view, not AWCI-specific. This
session's own first conformance audit (reports/ACF_MASTER_AUDIT_v2.md)
confirmed no such dashboard existed anywhere in src/acf/gui before this.

Real engines reused, not reimplemented - see reports/ACF_MASTER_AUDIT_v2.md's
own update for this feature for the full rationale:
- acf.awci.temporal_field.compute_real_complexity_evolution() - ONE
  real continuous CoupledEarthSolver trajectory drives BOTH the 5
  lead-time tabs and the AWCI-evolution chart (re-sliced per tab
  click, never recomputed).
- acf.awci.path_sampling.sample_volume_cross_section() - real
  cross-section from the same real evolution frame's volume.
- acf.awci.calculator.AWCICalculator.calculate()/
  calculate_with_uncertainty() - real point score + real decomposition
  (dominant couplings) + real empirical uncertainty once a real
  multi-model comparison has run.
- acf.visualization.ai_forecast_center.model_consensus_engine.
  ModelConsensusEngine.compute_real_multi_model_disagreement() - real
  per-model spread, computed on demand (real cost, not automatic).
- acf.gui.dashboard.awci_gauge.AWCIGauge - a real, correct,
  self-documented ORPHAN (its own NOTE: "no longer instantiated by
  anything... not deleted per project convention") since the AWCI
  dashboard rebuild switched to AWCIRadar. This dashboard is its first
  real, live use since then - closes that orphan finding as a side
  effect.
- acf.gui.dashboard.awci_map_panel.AWCIMapPanel,
  acf.gui.dashboard.awci_cross_section.AWCICrossSection,
  acf.gui.dashboard.awci_radar.AWCIRadar, acf.gui.theme_tokens - the
  exact same real, already-built widgets/tokens the AWCI dashboard
  uses, for one consistent visual language project-wide.

Honest, disclosed scope decisions (not silently assumed - see the plan
this was built from):
- Lead-time tabs are real frames of ONE real evolution run (5 frames),
  not 5 independent solver runs - clicking a tab re-slices the
  already-computed real data, no new computation.
- The multi-model consensus/spread panel is real but on-demand (a
  genuine multi-model comparison is this dashboard's most expensive
  real computation) - not auto-computed on every tab click.
- No "JET STREAM SHEAR"/"CONVECTIVE PENETRATION" annotation labels are
  drawn on the cross-section - no real jet-stream/convective-cell
  detection algorithm exists in this codebase, and inventing one here
  would be exactly the kind of fabricated diagnostic the master prompt
  exists to prevent.
- The "dominant coupling" readout and point AWCI score come from one
  fixed, disclosed real point (Algiers, 36.75N 3.06E - already used
  elsewhere in this codebase, e.g. awci_dashboard.py's own
  _REGIONAL_ROUTE) rather than a real click-to-inspect-anywhere
  interaction on the map, to avoid the real complexity of
  disambiguating a real map click from a real pan-drag (EventMixin's
  mousePressEvent already starts a potential drag) within this pass's
  scope.

Hamburger menu (☰) (added 2026-09-04, explicit user instruction: keep
this dashboard's own fixed reference-mockup chrome clean - real
actions belong behind the "☰" icon shown top-left in the reference
mockup, not as extra inline buttons cluttering the main panels). The
mockup's own ☰ icon had never been built; "🔄 Refresh Evolution" and
"🔄 Compute Consensus" were real, working actions but lived as inline
QPushButtons not present anywhere in the reference image - moved
behind a real QMenu on this new button instead, wired to the exact
same real refresh()/_start_consensus() methods (QAction.triggered,
not QPushButton.clicked - both objects still expose the same
isEnabled()/setEnabled() the rest of this class' own disable-while-
running discipline already used). Any further real capability this
dashboard gains should be added here, not as a new inline widget in
the fixed layout.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMenu, QPushButton, QToolButton, QVBoxLayout, QWidget

from acf.awci.calculator import AWCICalculator
from acf.awci.path_sampling import sample_volume_cross_section
from acf.awci.temporal_field import compute_real_complexity_evolution
from acf.gui.dashboard.awci_cross_section import AWCICrossSection
from acf.gui.dashboard.awci_evolution_chart import AWCIEvolutionChart
from acf.gui.dashboard.awci_gauge import AWCIGauge
from acf.gui.dashboard.awci_map_panel import AWCIMapPanel
from acf.gui.dashboard.awci_model_spread_chart import AWCIModelSpreadChart
from acf.gui.dashboard.awci_radar import AWCIRadar
from acf.gui.theme_tokens import dashboard_stylesheet, label_style
from acf.physics_guard import PhysicsGuard
from acf.visualization.ai_forecast_center.model_consensus_engine import ModelConsensusEngine

logger = logging.getLogger("acf.gui.dashboard.acf_general_dashboard")

# compute_real_complexity_evolution() spaces frames UNIFORMLY - real
# per-frame "T+Xh" button text is set from the evolution's own real
# valid_time_seconds in _on_evolution_ready(), never fixed here.
_N_LEAD_TIME_FRAMES = 5
_DEFAULT_MODEL = "ARPEGE"  # smallest of the 3 real MODEL_CONFIGS grids - fastest real evolution run
_ROUTE = [(40.64, -73.78), (49.01, 2.55)]  # JFK -> CDG, same real demo route convention as awci_dashboard.py
_POINT_OF_INTEREST = (36.75, 3.06)  # Alger - same real point already used elsewhere (awci_dashboard.py's _REGIONAL_ROUTE)
_CONSENSUS_MODELS = ["ALADIN", "ARPEGE"]  # the 2 fastest real MODEL_CONFIGS grids


class _EvolutionWorkerSignals(QObject):
    """QRunnable itself cannot be a QObject - same companion-object
    pattern used throughout this codebase's other real off-thread
    workers (awci_dashboard.py's _EvolutionWorker, esoc_window.py's
    _AWCIFieldWorker) - reused, not reinvented."""

    finished = Signal(dict)
    failed = Signal(str)


class _EvolutionWorker(QRunnable):
    """Runs compute_real_complexity_evolution() off the GUI thread."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.kwargs = kwargs
        self.signals = _EvolutionWorkerSignals()

    def run(self) -> None:
        try:
            result = compute_real_complexity_evolution(**self.kwargs)
        except Exception as exc:
            logger.exception("ACF General Dashboard: evolution computation failed")
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)


class _ConsensusWorkerSignals(QObject):
    finished = Signal(dict)
    failed = Signal(str)


class _ConsensusWorker(QRunnable):
    """Runs ModelConsensusEngine.compute_real_multi_model_disagreement() off the GUI thread."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.kwargs = kwargs
        self.signals = _ConsensusWorkerSignals()

    def run(self) -> None:
        try:
            result = ModelConsensusEngine.compute_real_multi_model_disagreement(**self.kwargs)
        except Exception as exc:
            logger.exception("ACF General Dashboard: consensus computation failed")
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)


class ACFGeneralDashboard(QWidget):
    """The real, general ACF dashboard - see module docstring."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._evolution: dict[str, Any] | None = None
        self._current_frame_index = 0
        self._build_ui()
        self.setStyleSheet(dashboard_stylesheet())
        # Honest, disclosed choice, consistent with AWCIDashboard's own
        # constructor convention (refresh() there is a fast synchronous
        # demo pattern; the heavy real off-thread computation only
        # starts on an explicit user action): the real evolution run
        # here is NOT auto-started at construction - the panels open in
        # their honest "Not yet computed" state until the user clicks
        # "🔄 Refresh Evolution", same on-demand discipline already
        # applied to the multi-model consensus button. Avoids starting
        # a real background QThreadPool computation the instant a
        # window (or a test) merely constructs this widget.

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setSpacing(8)
        outer.setContentsMargins(10, 10, 10, 0)

        # --- Top status row --------------------------------------------
        status_row = QHBoxLayout()

        # Real "☰" navigation menu (added 2026-09-04, see module
        # docstring) - matches the reference mockup's own top-left icon
        # exactly, and is this dashboard's real home for actions that
        # would otherwise clutter the fixed, mockup-matched panels
        # below. Real QAction entries, not decorative - each wired to
        # the exact same real method its former inline button called.
        self.menu_button = QToolButton()
        self.menu_button.setText("☰")
        self.menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.menu_button.setToolTip("Dashboard actions")
        self.nav_menu = QMenu(self.menu_button)

        self.refresh_button = QAction("🔄 Refresh Evolution", self)
        self.refresh_button.setToolTip(
            "Real, off-thread compute_real_complexity_evolution() run (CoupledEarthSolver,\n"
            f"{_N_LEAD_TIME_FRAMES} real frames) - drives every panel below from one real trajectory."
        )
        self.refresh_button.triggered.connect(self.refresh)
        self.nav_menu.addAction(self.refresh_button)

        self.consensus_button = QAction("🔄 Compute Consensus", self)
        self.consensus_button.setToolTip(
            "Real multi-model comparison (acf.visualization.ai_forecast_center.\n"
            "ModelConsensusEngine) - runs ACF's own solver once per real model grid\n"
            "configuration at the point of interest. The most expensive real\n"
            "computation in this dashboard - on demand, not automatic."
        )
        self.consensus_button.triggered.connect(self._start_consensus)
        self.nav_menu.addAction(self.consensus_button)

        self.menu_button.setMenu(self.nav_menu)
        status_row.addWidget(self.menu_button)

        header = QLabel("ATMOSPHERIC COMPLEXITY FRAMEWORK (ACF) — RESEARCH SUITE")
        header.setStyleSheet(label_style("text_primary", "lg", "bold"))
        status_row.addWidget(header)
        status_row.addStretch()

        self.science_status_label = QLabel("SCIENCE STATUS: RESEARCH / HYPOTHESIS")
        self.science_status_label.setStyleSheet(label_style("warning", "sm", "bold"))
        status_row.addWidget(self.science_status_label)

        self.model_tag_label = QLabel(f"MODEL: {_DEFAULT_MODEL}")
        self.model_tag_label.setStyleSheet(label_style("text_secondary", "sm"))
        status_row.addWidget(self.model_tag_label)

        self.quality_flag_label = QLabel("QUALITY: —")
        self.quality_flag_label.setStyleSheet(label_style("text_secondary", "sm"))
        status_row.addWidget(self.quality_flag_label)
        outer.addLayout(status_row)

        # --- Lead-time tabs ----------------------------------------------
        lead_time_row = QHBoxLayout()
        lead_time_row.addWidget(self._label("Lead time:", "text_muted", "xs"))
        self.lead_time_buttons: list[QPushButton] = []
        for i in range(_N_LEAD_TIME_FRAMES):
            # Placeholder text only - real labels are set in
            # _on_evolution_ready() from the evolution's own
            # valid_time_seconds once real data exists. compute_real_
            # complexity_evolution() spaces frames UNIFORMLY
            # (n_frames * steps_per_frame * dt_seconds), so a fixed
            # "T+3h/T+6h/T+12h/T+24h" label set (uneven spacing) would
            # be fabricated text not matching what was actually
            # computed - exactly the kind of mismatch the master
            # prompt's "never invent the project's state" (§69) rule
            # exists to prevent.
            btn = QPushButton(f"Frame {i + 1}")
            btn.setCheckable(True)
            btn.setChecked(i == 0)
            btn.clicked.connect(lambda checked=False, idx=i: self._on_lead_time_clicked(idx))
            lead_time_row.addWidget(btn)
            self.lead_time_buttons.append(btn)
        lead_time_row.addStretch()
        outer.addLayout(lead_time_row)

        self.status_label = QLabel("Not yet computed.")
        self.status_label.setStyleSheet(label_style("text_muted", "sm"))
        outer.addWidget(self.status_label)

        # --- Row 1: synoptic map (left) + cross-section (right) --------
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        self.map_panel = AWCIMapPanel("HIGH-RESOLUTION SYNOPTIC AWCI MAP", show_legend=True, show_info_boxes=True)
        # Neither AWCIMapPanel nor AWCICrossSection sets its own minimum
        # size (verified by reading both source files) - with this
        # dashboard's own extra rows below (lead-time tabs, decomposition
        # panel with 2 real AWCIGauge instances, each with a real
        # setMinimumSize(180, 180)) competing for vertical space, row1
        # was measured (real running-widget geometry check, not assumed)
        # collapsing to ~200px tall without an explicit floor - too small
        # to read the map. A real minimum height fixes it.
        self.map_panel.setMinimumHeight(380)
        row1.addWidget(self.map_panel, stretch=3)
        self.cross_section = AWCICrossSection("ATMOSPHERIC VERTICAL CROSS-SECTION")
        self.cross_section.setMinimumHeight(380)
        row1.addWidget(self.cross_section, stretch=2)
        outer.addLayout(row1, stretch=4)

        # --- Row 2: decomposition (left) + evolution (mid) + spread (right) ---
        row2 = QHBoxLayout()
        row2.setSpacing(8)

        decomposition_col = QVBoxLayout()
        decomposition_header = QLabel("SCIENTIFIC DECOMPOSITION & EXPLAINABILITY")
        decomposition_header.setStyleSheet(label_style("text_secondary", "sm", "bold"))
        decomposition_col.addWidget(decomposition_header)

        gauges_row = QHBoxLayout()
        complexity_col = QVBoxLayout()
        complexity_col.addWidget(self._label("ATMOSPHERIC COMPLEXITY", "text_muted", "xs"))
        self.complexity_gauge = AWCIGauge()
        complexity_col.addWidget(self.complexity_gauge)
        gauges_row.addLayout(complexity_col)

        uncertainty_col = QVBoxLayout()
        uncertainty_col.addWidget(self._label("MODEL UNCERTAINTY", "text_muted", "xs"))
        self.uncertainty_gauge = AWCIGauge()
        uncertainty_col.addWidget(self.uncertainty_gauge)
        gauges_row.addLayout(uncertainty_col)
        decomposition_col.addLayout(gauges_row)

        self.radar = AWCIRadar("MODULE DECOMPOSITION")
        decomposition_col.addWidget(self.radar)

        self.couplings_label = QLabel("Dominant couplings: —")
        self.couplings_label.setStyleSheet(label_style("text_primary", "sm"))
        self.couplings_label.setWordWrap(True)
        decomposition_col.addWidget(self.couplings_label)
        row2.addLayout(decomposition_col, stretch=2)

        # No fixed "(24h)" in the title - compute_real_complexity_evolution()'s
        # real time span depends on n_frames/steps_per_frame/dt_seconds
        # (see refresh() below) and must not be overstated; the chart's
        # own x-axis already shows the real per-frame hours honestly.
        self.evolution_chart = AWCIEvolutionChart("AWCI EVOLUTION")
        row2.addWidget(self.evolution_chart, stretch=2)

        spread_col = QVBoxLayout()
        self.spread_chart = AWCIModelSpreadChart("MULTI-MODEL CONSENSUS SPREAD")
        spread_col.addWidget(self.spread_chart)
        row2.addLayout(spread_col, stretch=2)

        outer.addLayout(row2, stretch=2)

        # --- Footer -------------------------------------------------------
        footer = QHBoxLayout()
        self.footer_label = QLabel("Session: — | Data: — | Algs: ACF Research Suite | System: —")
        self.footer_label.setStyleSheet(label_style("text_muted", "xs"))
        footer.addWidget(self.footer_label)
        footer.addStretch()
        outer.addLayout(footer)

    @staticmethod
    def _label(text: str, color: str, size: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(label_style(color, size))
        return lbl

    # --------------------------------------------------------- evolution

    def refresh(self) -> None:
        """Real, off-thread compute_real_complexity_evolution() run -
        drives both the lead-time tabs and the AWCI evolution chart
        from the SAME one real trajectory."""
        self.refresh_button.setEnabled(False)
        self.status_label.setText("⏳ Computing real ACF evolution (CoupledEarthSolver, 5 real frames)…")
        worker = _EvolutionWorker(
            model=_DEFAULT_MODEL,
            n_frames=_N_LEAD_TIME_FRAMES,
            steps_per_frame=4,
            n_lat=24,
            n_lon=36,
            n_levels=8,
            perturbation_scale=3.0,
            seed=1,
        )
        worker.signals.finished.connect(self._on_evolution_ready)
        worker.signals.failed.connect(self._on_evolution_failed)
        QThreadPool.globalInstance().start(worker)

    def _on_evolution_ready(self, evolution: dict[str, Any]) -> None:
        self.refresh_button.setEnabled(True)
        self._evolution = evolution
        self._current_frame_index = 0
        # Real per-frame labels from the evolution's own
        # valid_time_seconds - never a fixed guess (see the placeholder
        # buttons' own construction comment in _build_ui()). zip()
        # tolerates an evolution with fewer real frames than UI buttons
        # (e.g. a smaller n_frames override) without an IndexError - any
        # extra buttons just keep their placeholder text and are hidden.
        valid_times = evolution["valid_time_seconds"]
        for i, btn in enumerate(self.lead_time_buttons):
            has_real_frame = i < len(valid_times)
            btn.setVisible(has_real_frame)
            if has_real_frame:
                btn.setText(f"T+{valid_times[i] / 3600.0:.2f}h")
                btn.setChecked(i == 0)

        lats, lons = evolution["lats"], evolution["lons"]
        try:
            PhysicsGuard().check_coordinate_arrays(lats, lons)
            self.quality_flag_label.setText("QUALITY: PASS")
            self.quality_flag_label.setStyleSheet(label_style("success", "sm", "bold"))
        except Exception:
            logger.warning("ACF General Dashboard: coordinate quality check failed", exc_info=True)
            self.quality_flag_label.setText("QUALITY: FAIL")
            self.quality_flag_label.setStyleSheet(label_style("danger", "sm", "bold"))

        self.status_label.setText(
            f"✅ Real {evolution['n_frames']}-frame ACF evolution computed ({evolution['model']} grid)."
        )
        self._render_evolution_chart()
        self._render_frame(0)

    def _on_evolution_failed(self, message: str) -> None:
        self.refresh_button.setEnabled(True)
        self.status_label.setText(f"⚠ Real evolution computation failed: {message}")
        logger.error("ACF General Dashboard: evolution computation failed: %s", message)

    def _on_lead_time_clicked(self, index: int) -> None:
        if self._evolution is None:
            return
        for i, btn in enumerate(self.lead_time_buttons):
            btn.setChecked(i == index)
        self._current_frame_index = index
        self._render_frame(index)

    def _render_evolution_chart(self) -> None:
        evolution = self._evolution
        if evolution is None:
            return
        valid_time_hours = [t / 3600.0 for t in evolution["valid_time_seconds"]]
        awci_mean_per_frame = [float(np.mean(evolution["awci_evolution"][i, 0])) for i in range(evolution["n_frames"])]
        awci_max_per_frame = [float(np.max(evolution["awci_evolution"][i, 0])) for i in range(evolution["n_frames"])]
        self.evolution_chart.set_series(valid_time_hours, awci_mean_per_frame, awci_max_per_frame, current_frame_index=self._current_frame_index)

    def _render_frame(self, frame_index: int) -> None:
        """Real re-slice of the already-computed evolution - no new
        solver run, matching the AWCI dashboard's own level-slider
        discipline (compute once, re-slice per UI interaction)."""
        evolution = self._evolution
        if evolution is None:
            return
        lats, lons = evolution["lats"], evolution["lons"]
        valid_time_h = evolution["valid_time_seconds"][frame_index] / 3600.0

        awci_surface = evolution["awci_evolution"][frame_index, 0]
        self.map_panel.set_external_field(lons, lats, awci_surface, f"REAL ACF — t+{valid_time_h:.1f}h")

        cross = sample_volume_cross_section(
            lats, lons, evolution["pressure_evolution_hpa"][frame_index], evolution["awci_evolution"][frame_index],
            _ROUTE[0], _ROUTE[1], n_along=30,
        )
        self.cross_section.set_external_cross_section(
            cross["distances_km"], cross["mean_pressure_hpa_by_level"], cross["grid"], f"REAL ACF — t+{valid_time_h:.1f}h"
        )

        lat_idx = int(np.argmin(np.abs(np.asarray(lats) - _POINT_OF_INTEREST[0])))
        lon_idx = int(np.argmin(np.abs(np.asarray(lons) - _POINT_OF_INTEREST[1])))
        point_data = {
            "temperature": float(evolution["temperature_evolution"][frame_index, 0, lat_idx, lon_idx]),
            "wind_speed": float(evolution["wind_speed_evolution"][frame_index, 0, lat_idx, lon_idx]),
            "specific_humidity": float(evolution["specific_humidity_evolution"][frame_index, 0, lat_idx, lon_idx]),
            "pressure": float(evolution["pressure_evolution_hpa"][frame_index, 0, lat_idx, lon_idx]),
        }
        result = AWCICalculator().calculate(point_data)
        self.complexity_gauge.set_score(result["awci"], animate=False)
        self.radar.update_data(result["module_scores"])

        interaction_scores = result["interaction_scores"]
        if interaction_scores:
            dominant_term = max(interaction_scores, key=lambda k: interaction_scores[k])
            self.couplings_label.setText(
                f"Dominant couplings: {dominant_term.replace('_', ' ')} ({interaction_scores[dominant_term]:.0f})"
            )
        else:
            self.couplings_label.setText("Dominant couplings: none active at this point")

        self._render_evolution_chart()

    # ---------------------------------------------------------- consensus

    def _start_consensus(self) -> None:
        self.consensus_button.setEnabled(False)
        self.status_label.setText("⏳ Computing real multi-model consensus (ACF solver per real model grid)…")
        worker = _ConsensusWorker(
            lat=_POINT_OF_INTEREST[0], lon=_POINT_OF_INTEREST[1], models=list(_CONSENSUS_MODELS), steps=2
        )
        worker.signals.finished.connect(self._on_consensus_ready)
        worker.signals.failed.connect(self._on_consensus_failed)
        QThreadPool.globalInstance().start(worker)

    def _on_consensus_ready(self, result: dict[str, Any]) -> None:
        self.consensus_button.setEnabled(True)
        self.status_label.setText("✅ Real multi-model consensus computed.")
        self.spread_chart.set_data(
            result["per_model_value"], result["disagreement_mean"], result["disagreement_spread"], "Temperature (K)"
        )
        # Real uncertainty gauge - normalized real disagreement spread,
        # the same real Normalizer.normalize_model_disagreement()
        # formula AWCICalculator's own model_disagreement module uses,
        # not a separately invented scale.
        from acf.awci.normalizer import Normalizer

        normalized = Normalizer.normalize_model_disagreement(result["disagreement_spread"], "temperature")
        self.uncertainty_gauge.set_score(normalized * 100.0, animate=False)

    def _on_consensus_failed(self, message: str) -> None:
        self.consensus_button.setEnabled(True)
        self.status_label.setText(f"⚠ Real consensus computation failed: {message}")
        logger.error("ACF General Dashboard: consensus computation failed: %s", message)

    def status(self) -> dict[str, Any]:
        return {"has_evolution": self._evolution is not None, "current_frame_index": self._current_frame_index}
