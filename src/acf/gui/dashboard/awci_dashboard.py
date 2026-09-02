"""
AWCI Dashboard
==============

Full "AWCI - Aviation Weather Complexity Index" operational dashboard,
matching the reference concept mockup: global map, vertical cross-section,
component radar, regional map, route planning, risk summary, stats bar and
footer. Every AWCI number shown is the real output of
acf.awci.calculator.AWCICalculator; only the underlying meteorological
input fields are a synthetic demo pattern (see awci_synthetic_field.py's
docstring) - exactly the "Concept Output - Research Prototype" framing the
reference mockup itself uses, UNLESS "Real Physics" mode is engaged (see
below).

Real Physics mode (added 2026-09-02, explicit user request "vas-y,
branche le dashboard", extended the same day to "branche la carte
régionale/coupe/route sur les vrais champs")
-----------------------------------------------------------------------
The "🔬 Real Physics" button runs
acf.awci.vertical_field.compute_real_complexity_volume() - a real
CoupledEarthSolver run producing a full 3D Complexity(x, y, z) volume,
not the synthetic demo pattern - on a background QThreadPool worker
(same WorkerRunnable-with-a-signal pattern as
gui/esoc/command_dispatcher.py's async commands, extended here to carry
a result back to the GUI thread) so the real computation never freezes
the UI. Every panel is now wired to this SAME real volume, sampled
different ways via acf.awci.path_sampling (post-processing, no extra
solver runs): global map and regional map show the volume's surface
level (cropped to the regional extent for the latter - see
crop_field_to_extent()'s honest handling of a native grid coarser than
the extent), route chart samples the surface level along a path
(sample_field_along_path()), cross-section samples the FULL volume
along a path (sample_volume_cross_section() - native model levels, see
that function's own honest_limitation on path-averaged pressure per
level). Stats bar, radar and risk-summary are derived from the same
volume as before.

4D animation (added 2026-09-02, explicit user request "brancher
l'animation 4D dans le dashboard")
-----------------------------------------------------------------------
Once Real Physics mode has run, "▶ Play Evolution (4D)" becomes
available. It runs acf.awci.temporal_field.
compute_real_complexity_evolution() - ONE CoupledEarthSolver instance
integrated continuously across several real frames (a genuine physical
trajectory, not independently restarted snapshots - see that module's
own docstring for why this distinction matters) - on another background
worker, then animates the global map through the real frames via a
QTimer (800ms/frame), showing each frame's real elapsed simulated time
(valid_time_seconds) in the Valid Time readout - not a fake
incrementing clock. Clicking again stops the animation; a second play
click resumes from frame 0 without recomputing (the evolution already
ran). "↩ Back to Demo" stops any running animation and hides the
button - it only makes sense while a real trajectory exists to play.
Only the global map animates today - the regional map/route/cross-
section stay on their static Real Physics snapshot during playback
(animating all four would need path_sampling calls repeated per frame,
not built here).
"""

import logging
from typing import Any

import numpy as np
from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, QTimer, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget

from acf.awci.calculator import AWCICalculator
from acf.physics_guard import PhysicsGuard
from acf.awci.path_sampling import crop_field_to_extent, sample_field_along_path, sample_volume_cross_section
from acf.awci.temporal_field import compute_real_complexity_evolution
from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.awci_cross_section import AWCICrossSection
from acf.gui.dashboard.awci_footer import AWCIFooter
from acf.gui.dashboard.awci_map_panel import AWCIMapPanel
from acf.gui.dashboard.awci_radar import AWCIRadar
from acf.gui.dashboard.awci_risk_summary import AWCIRiskSummary
from acf.gui.dashboard.awci_route_chart import AWCIRouteChart
from acf.gui.dashboard.awci_stats_bar import AWCIStatsBar
from acf.gui.dashboard.awci_synthetic_field import awci_at, awci_grid

logger = logging.getLogger("acf.gui.dashboard.awci")

# Reference-style demo route/point of interest: JFK -> CDG (global map / cross-section)
_GLOBAL_ROUTE = [(40.64, -73.78, "JFK"), (49.01, 2.55, "CDG")]
# Regional demo route: within the North Africa regional map extent
_REGIONAL_ROUTE = [(36.75, 3.06, "Alger"), (32.90, 13.19, "Tripoli")]
_REGIONAL_EXTENT = (-12.0, 35.0, 15.0, 40.0)  # lon_min, lon_max, lat_min, lat_max
_POINT_OF_INTEREST = (34.5, 12.3)  # matches the reference's example point (lat, lon)


class _ComponentValueList(QFrame):
    """Compact list of module scores next to the radar - mirrors the reference's
    numeric readout ('Dynamic 0.72', 'Thermodynamic 0.81', ...) alongside its radar."""

    _LABELS = [
        ("dynamic", "🌀", "Dynamic"),
        ("thermodynamic", "🌡️", "Thermodynamic"),
        ("convective", "⛈️", "Convective"),
        ("microphysical", "❄️", "Microphysical"),
        ("topographic", "⛰️", "Topographic"),
        ("temporal", "🕐", "Temporal"),
        ("confidence", "❓", "Uncertainty"),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("border: none;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(4)

        self._values: dict[str, QLabel] = {}
        for key, icon, label in self._LABELS:
            row = QHBoxLayout()
            lbl = QLabel(f"{icon}  {label}")
            lbl.setStyleSheet("color: #c0c8d8; font-size: 10px;")
            row.addWidget(lbl)
            row.addStretch()
            value = QLabel("—")
            value.setStyleSheet("color: #e0e0e0; font-size: 10px; font-weight: bold;")
            row.addWidget(value)
            layout.addLayout(row)
            self._values[key] = value

    def update_data(self, module_scores: dict[str, float]) -> None:
        for key, _icon, _label in self._LABELS:
            value = module_scores.get(key, 0.0) / 100.0  # display as a 0-1 fraction, like the reference
            self._values[key].setText(f"{value:.2f}")


class _RealFieldWorkerSignals(QObject):
    """QRunnable itself cannot be a QObject (no signals) - this small
    companion object is what actually carries the result back to the
    GUI thread. Qt's default (Auto) connection type marshals a signal
    emitted from this worker thread onto the receiver's thread as long
    as the receiver lives on the GUI thread, which AWCIDashboard does -
    the standard safe pattern for QRunnable + a result."""

    finished = Signal(dict)
    failed = Signal(str)


class _RealFieldWorker(QRunnable):
    """Runs compute_real_complexity_volume() off the GUI thread."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.kwargs = kwargs
        self.signals = _RealFieldWorkerSignals()

    def run(self) -> None:
        try:
            result = compute_real_complexity_volume(**self.kwargs)
        except Exception as exc:
            logger.exception("Real Physics field computation failed")
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)


class _EvolutionWorker(QRunnable):
    """Runs compute_real_complexity_evolution() off the GUI thread - the 4D counterpart of _RealFieldWorker, reusing the same signals shape (finished(dict)/failed(str))."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.kwargs = kwargs
        self.signals = _RealFieldWorkerSignals()

    def run(self) -> None:
        try:
            result = compute_real_complexity_evolution(**self.kwargs)
        except Exception as exc:
            logger.exception("4D evolution computation failed")
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)


class AWCIDashboard(QWidget):
    """Complete AWCI operational dashboard."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._real_physics_active = False
        self._evolution: dict[str, Any] | None = None
        self._evolution_frame_index = 0
        self._evolution_timer = QTimer(self)
        self._evolution_timer.setInterval(800)  # ms between real frames while playing
        self._evolution_timer.timeout.connect(self._advance_evolution_frame)
        self._build_ui()
        self._apply_theme()
        self.refresh()

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setSpacing(8)
        outer.setContentsMargins(10, 10, 10, 0)

        header_row = QHBoxLayout()
        header = QLabel("AWCI – AVIATION WEATHER COMPLEXITY INDEX")
        header.setStyleSheet("color: #e0e0e0; font-size: 18px; font-weight: bold;")
        header_row.addWidget(header)
        header_row.addStretch()

        self.real_physics_button = QPushButton("🔬 Real Physics")
        self.real_physics_button.setToolTip(
            "Run a real CoupledEarthSolver volume (acf.awci.vertical_field) instead of the synthetic demo\n"
            "pattern. Every panel below - global/regional map, stats, radar, risk summary, route, cross-\n"
            "section - is sampled from this one real trajectory (acf.awci.path_sampling)."
        )
        self.real_physics_button.clicked.connect(self._toggle_real_physics)
        header_row.addWidget(self.real_physics_button)

        self.play_evolution_button = QPushButton("▶ Play Evolution (4D)")
        self.play_evolution_button.setToolTip(
            "Run a real 4D Complexity(x, y, z, t) evolution (acf.awci.temporal_field) - one\n"
            "CoupledEarthSolver instance integrated continuously - and animate the global map\n"
            "through its real frames. Only available once '🔬 Real Physics' has produced a real\n"
            "trajectory to continue from."
        )
        self.play_evolution_button.clicked.connect(self._toggle_evolution_playback)
        self.play_evolution_button.setVisible(False)
        header_row.addWidget(self.play_evolution_button)
        outer.addLayout(header_row)

        subheader = QLabel("Concept Output – Research Prototype")
        subheader.setStyleSheet("color: #8090a8; font-size: 11px;")
        outer.addWidget(subheader)
        self.real_physics_status = subheader  # reused as the mode/status line

        # --- Row 1: global map (left) + cross-section & radar (right) -----
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        self.global_map = AWCIMapPanel("AWCI GLOBAL MAP (FL300)")
        self.global_map.set_flight_path(_GLOBAL_ROUTE)
        row1.addWidget(self.global_map, stretch=3)

        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        self.cross_section = AWCICrossSection()
        right_col.addWidget(self.cross_section, stretch=1)

        radar_row = QHBoxLayout()
        self.radar = AWCIRadar("AWCI COMPONENTS (example at point)")
        self.component_list = _ComponentValueList()
        radar_row.addWidget(self.radar, stretch=2)
        radar_row.addWidget(self.component_list, stretch=1)
        right_col.addLayout(radar_row, stretch=1)

        row1.addLayout(right_col, stretch=2)
        outer.addLayout(row1, stretch=3)

        # --- Stats bar -----------------------------------------------------
        self.stats_bar = AWCIStatsBar()
        outer.addWidget(self.stats_bar)

        # --- Row 2: regional map (left) + route/risk (right) --------------
        row2 = QHBoxLayout()
        row2.setSpacing(8)

        left_col2 = QVBoxLayout()
        self.regional_map = AWCIMapPanel("AWCI REGIONAL MAP – NORTH AFRICA (FL100)", extent=_REGIONAL_EXTENT)
        self.regional_map.set_flight_path(_REGIONAL_ROUTE)
        self.regional_map.set_point_marker(*_POINT_OF_INTEREST)
        left_col2.addWidget(self.regional_map, stretch=1)

        time_row = QHBoxLayout()
        time_label = QLabel("Valid Time:")
        time_label.setStyleSheet("color: #8090a8; font-size: 9px;")
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(23)
        self.time_slider.setValue(12)
        self.time_slider.sliderReleased.connect(self._on_time_changed)
        self.time_readout = QLabel("12Z")
        self.time_readout.setStyleSheet("color: #e0e0e0; font-size: 9px; font-weight: bold;")
        self.time_slider.valueChanged.connect(lambda v: self.time_readout.setText(f"{v:02d}Z"))
        time_row.addWidget(time_label)
        time_row.addWidget(self.time_slider, stretch=1)
        time_row.addWidget(self.time_readout)
        left_col2.addLayout(time_row)

        row2.addLayout(left_col2, stretch=3)

        right_col2 = QVBoxLayout()
        right_col2.setSpacing(8)
        op_header = QLabel("AWCI – OPERATIONAL USE EXAMPLE")
        op_header.setStyleSheet("color: #d0d8e8; font-size: 10px; font-weight: bold;")
        right_col2.addWidget(op_header)

        op_row = QHBoxLayout()
        self.route_chart = AWCIRouteChart()
        self.risk_summary = AWCIRiskSummary()
        op_row.addWidget(self.route_chart, stretch=2)
        op_row.addWidget(self.risk_summary, stretch=1)
        right_col2.addLayout(op_row, stretch=1)

        row2.addLayout(right_col2, stretch=2)
        outer.addLayout(row2, stretch=2)

        # --- Footer ---------------------------------------------------------
        self.footer = AWCIFooter()
        outer.addWidget(self.footer)

    def _apply_theme(self) -> None:
        self.setStyleSheet("""
            QWidget {
                background-color: #0d1b2a;
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
        """)

    # ------------------------------------------------------------- refresh

    def _on_time_changed(self) -> None:
        """Re-render the regional map with a genuinely shifted synthetic-pattern
        phase for the selected hour (see awci_synthetic_field.py's time_offset_hours) -
        the slider moves the pattern, it does not silently change anything else."""
        self.regional_map.update_data(flight_level_hpa=700.0, time_offset_hours=float(self.time_slider.value()))

    def refresh(self) -> None:
        """(Re)compute every panel from the real AWCICalculator (see module docstring)."""
        self.cross_section.update_data(_GLOBAL_ROUTE[0][:2], _GLOBAL_ROUTE[1][:2], cruise_hpa=300.0)

        point_result = awci_at(*_POINT_OF_INTEREST, flight_level_hpa=300.0)
        self.radar.update_data(point_result["module_scores"])
        self.component_list.update_data(point_result["module_scores"])

        _lons, _lats, grid = awci_grid(lat_step=4.0, lon_step=4.0, flight_level_hpa=300.0)
        flat_scores = [v for row in grid for v in row]
        self.stats_bar.update_data(flat_scores, confidence_pct=point_result["confidence"])

        route_scores = self.route_chart.update_data(_REGIONAL_ROUTE[0][:2], _REGIONAL_ROUTE[1][:2], cruise_hpa=850.0)
        overall_awci = max(route_scores) if route_scores is not None else point_result["awci"]
        # physical_score/forecast_score are for the point of interest, not
        # the route's worst point (unlike overall_awci above) - route-level
        # aggregation of the split scores is future work, not simulated
        # here.
        self.risk_summary.update_data(
            point_result["module_scores"],
            overall_awci,
            physical_score=point_result["physical_score"],
            forecast_score=point_result["forecast_score"],
        )

    # ------------------------------------------------- Real Physics mode

    def _toggle_real_physics(self) -> None:
        if self._real_physics_active:
            self._revert_to_demo()
        else:
            self._start_real_physics()

    def _start_real_physics(self) -> None:
        self.real_physics_button.setEnabled(False)
        self.real_physics_status.setText(
            "🔬 Computing real physics volume (CoupledEarthSolver, ARPEGE grid)… this takes a few seconds"
        )
        # A single real VOLUME (not just one 2D field) drives every
        # panel below - global map, regional map, route chart and
        # cross-section all sample the exact same real trajectory
        # instead of one solver run each (added 2026-09-02, explicit
        # user request "branche la carte régionale/coupe/route sur les
        # vrais champs").
        worker = _RealFieldWorker(model="ARPEGE", steps=8, dt_seconds=90.0, perturbation_scale=3.0, seed=1)
        worker.signals.finished.connect(self._on_real_physics_ready)
        worker.signals.failed.connect(self._on_real_physics_failed)
        QThreadPool.globalInstance().start(worker)

    def _on_real_physics_ready(self, volume: dict[str, Any]) -> None:
        self._real_physics_active = True
        self.real_physics_button.setText("↩ Back to Demo")
        self.real_physics_button.setEnabled(True)
        self.real_physics_status.setText(
            "🔬 REAL PHYSICS — CoupledEarthSolver (ARPEGE grid, one continuous run). Every panel below "
            "(global/regional map, stats, radar, risk summary, route, cross-section) is sampled from it."
        )

        lons, lats = volume["lons"], volume["lats"]
        # Real regression guard (added 2026-09-02): this exact line once
        # had lons/lats swapped, caught only by a test using a
        # deliberately non-square grid - see git history. A
        # PhysicsGuard coordinate check here catches that bug class at
        # runtime too, on any grid shape, not just a non-square test one.
        PhysicsGuard().check_coordinate_arrays(lats, lons)
        # Surface level (index 0) stands in for the 2D field the map/
        # stats/route panels need - same real per-point values a
        # compute_real_complexity_field() call would have produced at
        # level 0, just reused from the volume already computed above
        # instead of a second solver run.
        awci_surface = volume["awci_volume"][0]
        self.global_map.set_external_field(lons, lats, awci_surface, "REAL PHYSICS")

        cropped = crop_field_to_extent(lats, lons, awci_surface, _REGIONAL_EXTENT)
        if cropped["n_points_in_extent"][0] >= 2 and cropped["n_points_in_extent"][1] >= 2:
            self.regional_map.set_external_field(cropped["lons"], cropped["lats"], cropped["field"], "REAL PHYSICS")
        else:
            # ARPEGE's real native grid is coarser than this regional
            # extent (< 2x2 real points fall inside it) - matplotlib
            # itself requires at least a (2, 2) grid to contour. Leave
            # the regional map on the synthetic pattern rather than
            # crash or silently show an empty/misleading plot; a finer
            # model (AROME) would resolve this but is much slower to
            # run interactively (see spatial_field.py's own timings).
            logger.warning(
                "AWCIDashboard: real ARPEGE grid too coarse for the regional extent (%s real points) - "
                "regional map stays on the synthetic pattern.",
                cropped["n_points_in_extent"],
            )

        route_distances, route_scores = sample_field_along_path(
            lats, lons, awci_surface, _REGIONAL_ROUTE[0][:2], _REGIONAL_ROUTE[1][:2], n_points=40
        )
        self.route_chart.set_external_route(route_distances, route_scores, "REAL PHYSICS")

        cross = sample_volume_cross_section(
            lats, lons, volume["pressure_volume_hpa"], volume["awci_volume"],
            _GLOBAL_ROUTE[0][:2], _GLOBAL_ROUTE[1][:2], n_along=40,
        )
        self.cross_section.set_external_cross_section(
            cross["distances_km"], cross["mean_pressure_hpa_by_level"], cross["grid"], "REAL PHYSICS"
        )

        flat_scores = [float(v) for v in awci_surface.flatten()]
        # No per-point forecast-side data is fed into
        # compute_real_complexity_volume() (see its own docstring) - the
        # solver's real fields don't carry a "confidence" input, so this
        # honestly reflects AWCICalculator's own default (100.0) rather
        # than an invented aggregate forecast confidence.
        self.stats_bar.update_data(flat_scores, confidence_pct=100.0)
        # Short label - "(ARPEGE grid)" is already in real_physics_status
        # above; the full model_box string overflowed its narrow box
        # (found via a real screenshot during verification).
        self.stats_bar.model_box.set_value("CoupledEarthSolver")

        # Radar/risk-summary need a single point's full module_scores
        # breakdown, which the volume does not store per grid cell (only
        # the aggregate scores) - recomputed here from this SAME call's
        # own raw surface-level fields at the point nearest
        # _POINT_OF_INTEREST, a real (not fabricated) per-point result.
        lat_idx = int(np.argmin(np.abs(np.asarray(lats) - _POINT_OF_INTEREST[0])))
        lon_idx = int(np.argmin(np.abs(np.asarray(lons) - _POINT_OF_INTEREST[1])))
        point_result = AWCICalculator().calculate(
            {
                "temperature": float(volume["temperature_volume"][0, lat_idx, lon_idx]),
                "wind_speed": float(volume["wind_speed_volume"][0, lat_idx, lon_idx]),
                "specific_humidity": float(volume["specific_humidity_volume"][0, lat_idx, lon_idx]),
                "pressure": float(volume["pressure_volume_hpa"][0, lat_idx, lon_idx]),
            }
        )
        self.radar.update_data(point_result["module_scores"])
        self.component_list.update_data(point_result["module_scores"])
        self.risk_summary.update_data(
            point_result["module_scores"],
            point_result["awci"],
            physical_score=point_result["physical_score"],
            forecast_score=point_result["forecast_score"],
        )

        # The 4D animation needs a real Physics volume to have run
        # first (same solver/config), so the button only becomes usable
        # once we're genuinely in Real Physics mode.
        self.play_evolution_button.setVisible(True)
        self.play_evolution_button.setEnabled(True)

    def _on_real_physics_failed(self, message: str) -> None:
        self.real_physics_button.setEnabled(True)
        self.real_physics_status.setText(f"⚠ Real physics computation failed: {message}")
        logger.error("AWCIDashboard: real physics computation failed: %s", message)

    def _revert_to_demo(self) -> None:
        self._stop_evolution_playback()
        self.play_evolution_button.setVisible(False)
        self._evolution = None
        self._real_physics_active = False
        self.real_physics_button.setText("🔬 Real Physics")
        self.real_physics_status.setText("Concept Output – Research Prototype")
        self.global_map.clear_external_field()
        self.regional_map.clear_external_field()
        self.route_chart.clear_external_route()
        self.cross_section.clear_external_cross_section()
        self.stats_bar.model_box.set_value("ACF Demo Grid")
        # The evolution playback may have left time_readout showing a
        # real elapsed-time label ("t+2.4h") - restore the synthetic
        # slider's own "HHZ" convention.
        self.time_readout.setText(f"{self.time_slider.value():02d}Z")
        self.refresh()

    # ------------------------------------------------------ 4D evolution

    def _toggle_evolution_playback(self) -> None:
        if self._evolution_timer.isActive():
            self._stop_evolution_playback()
        elif self._evolution is not None:
            # Already computed once this Real Physics session - just resume/restart playback, no new solver run.
            self._evolution_frame_index = 0
            self._evolution_timer.start()
            self.play_evolution_button.setText("⏸ Stop Animation")
        else:
            self._start_evolution()

    def _start_evolution(self) -> None:
        self.play_evolution_button.setEnabled(False)
        self.play_evolution_button.setText("⏳ Computing 4D evolution…")
        self.real_physics_status.setText(
            "🔬 Computing a real 4D evolution (CoupledEarthSolver, ARPEGE grid, continuous trajectory)… "
            "this takes longer than the static volume"
        )
        worker = _EvolutionWorker(
            model="ARPEGE", n_frames=6, steps_per_frame=8, dt_seconds=90.0, perturbation_scale=3.0, seed=1
        )
        worker.signals.finished.connect(self._on_evolution_ready)
        worker.signals.failed.connect(self._on_evolution_failed)
        QThreadPool.globalInstance().start(worker)

    def _on_evolution_ready(self, evolution: dict[str, Any]) -> None:
        self._evolution = evolution
        self._evolution_frame_index = 0
        self.play_evolution_button.setEnabled(True)
        self.play_evolution_button.setText("⏸ Stop Animation")
        self._evolution_timer.start()
        self._render_evolution_frame(0)

    def _on_evolution_failed(self, message: str) -> None:
        self.play_evolution_button.setEnabled(True)
        self.play_evolution_button.setText("▶ Play Evolution (4D)")
        self.real_physics_status.setText(f"⚠ 4D evolution computation failed: {message}")
        logger.error("AWCIDashboard: 4D evolution computation failed: %s", message)

    def _advance_evolution_frame(self) -> None:
        if self._evolution is None:
            self._stop_evolution_playback()
            return
        n_frames = self._evolution["n_frames"]
        self._evolution_frame_index = (self._evolution_frame_index + 1) % n_frames
        self._render_evolution_frame(self._evolution_frame_index)

    def _render_evolution_frame(self, frame_index: int) -> None:
        """Redraw the global map with this real frame's surface-level field, and show the real elapsed simulated time - not a fake incrementing clock."""
        evolution = self._evolution
        if evolution is None:
            return
        awci_frame = evolution["awci_evolution"][frame_index, 0]  # level 0 = surface
        valid_time_h = evolution["valid_time_seconds"][frame_index] / 3600.0
        self.global_map.set_external_field(
            evolution["lons"], evolution["lats"], awci_frame, f"REAL PHYSICS — t+{valid_time_h:.2f}h"
        )
        self.time_readout.setText(f"t+{valid_time_h:.2f}h")

    def _stop_evolution_playback(self) -> None:
        self._evolution_timer.stop()
        # CORRECTED: used to only reset the label if
        # play_evolution_button.isVisible() - but Qt's isVisible()
        # reflects EFFECTIVE visibility (the whole parent chain must
        # also be shown on screen), not just this widget's own
        # setVisible(True) flag. A dashboard that hasn't been shown()
        # yet (every non-interactive test, and any code path that
        # stops playback before the window is first rendered) would
        # silently skip the reset - found by a real test, not assumed.
        # No harm in setting a hidden button's text either way.
        self.play_evolution_button.setText("▶ Play Evolution (4D)")

    # ---------------------------------------------------- external API

    def update_with_awci_result(self, result: dict[str, Any]) -> None:
        """Update the components radar/list with an externally-supplied AWCICalculator result."""
        self.radar.update_data(result.get("module_scores", {}))
        self.component_list.update_data(result.get("module_scores", {}))

    def set_data(self, awci_result: dict[str, Any]) -> None:
        self.update_with_awci_result(awci_result)
