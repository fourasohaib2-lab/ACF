"""
ACF Scientific Workstation — Temporal Evolution Lab
=====================================================

Real multi-frame trajectory viewer for `acf_workstation.
ACFWorkstation` (see that module's own docstring for the Workstation's
overall "ACF CORE ONLY - NO AWCI" rule). Reuses
`acf.awci.temporal_field.compute_real_complexity_evolution()` as-is -
the SAME real off-thread evolution engine Complexity Explorer's own
"Run Temporal Analysis" button already uses for its single aggregated
rate-of-change map - but exposes the full real (n_frames, n_levels,
n_lat, n_lon) trajectory this panel reads only the raw physical
fields from (`temperature_evolution`/`wind_speed_evolution`/
`specific_humidity_evolution`/`pressure_evolution_hpa`, never
`awci_evolution`), letting a real frame slider scrub through the
actual real integration steps: a genuinely distinct capability from
Complexity Explorer's own single summary statistic, not a
re-presentation of the same result.

Real, on-demand, off-thread (like CAPE/CIN and Complexity Explorer's
own temporal/consensus buttons)
-------------------------------------------------------------------------
A real multi-frame `CoupledEarthSolver` integration is genuinely
expensive (several real solver steps per frame - the underlying
function's own docstring measures ~1.4s/frame at full ARPEGE
resolution) - never automatic. Same n_frames=4/steps_per_frame=3
parameters Complexity Explorer's own "Run Temporal Analysis" button
already uses, for consistency (not re-derived independently).

Honest scope
-------------
The frame slider re-slices the ALREADY-computed real trajectory - no
new solver run per frame. The Workstation's own level slider also
re-slices this same trajectory (real, immediate, no new run) once
computed; changing MODEL or clicking the Workstation's own "🔄 Run"
starts a fresh real volume but does NOT automatically recompute this
panel's own evolution - the previous real trajectory (from whichever
model/run it was actually computed against) stays displayed until the
user explicitly re-runs it, same "stays whatever it was, on-demand,
not tied to a Workstation refresh" convention already established for
Complexity Explorer's own temporal/consensus results and this panel's
own sibling, Thermodynamics Lab's CAPE/CIN.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget

from acf.awci.temporal_field import compute_real_complexity_evolution
from acf.gui.dashboard.awci_map_panel import AWCIMapPanel
from acf.gui.theme_tokens import label_style

#: Real per-variable evolution key + unit + a real, disclosed physical
#: rendering range - the SAME ranges acf_workstation_overview.py's own
#: _VARIABLES already uses for these exact quantities (not
#: re-derived independently - these are real, generous physical
#: envelopes, not fabricated score bands).
_VARIABLES: dict[str, dict[str, Any]] = {
    "Temperature": {"key": "temperature_evolution", "unit": "K", "cmap": "coolwarm", "vmin": 230.0, "vmax": 310.0},
    "Wind speed": {"key": "wind_speed_evolution", "unit": "m/s", "cmap": "viridis", "vmin": 0.0, "vmax": 40.0},
    "Specific humidity": {
        "key": "specific_humidity_evolution", "unit": "kg/kg", "cmap": "YlGnBu", "vmin": 0.0, "vmax": 0.02,
    },
    "Pressure": {"key": "pressure_evolution_hpa", "unit": "hPa", "cmap": "cividis", "vmin": 100.0, "vmax": 1050.0},
}

#: Same real parameters Complexity Explorer's own "Run Temporal
#: Analysis" button already uses (acf_workstation_complexity.py) - for
#: consistency, not re-derived independently.
_N_FRAMES = 4
_STEPS_PER_FRAME = 3


class _WorkerSignals(QObject):
    """Same real QRunnable-companion-object pattern used throughout
    this codebase's other off-thread workers - reused, not reinvented."""

    finished = Signal(dict)
    failed = Signal(str)


class _EvolutionWorker(QRunnable):
    """Runs compute_real_complexity_evolution() off the GUI thread."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.kwargs = kwargs
        self.signals = _WorkerSignals()

    def run(self) -> None:
        try:
            result = compute_real_complexity_evolution(**self.kwargs)
        except Exception as exc:  # noqa: BLE001 - real failure, reported honestly via signal below
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)


class ACFTemporalLabPanel(QWidget):
    """Real Temporal Evolution Lab - scrub through a real multi-frame
    CoupledEarthSolver trajectory. No AWCI content anywhere."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._volume: dict[str, Any] | None = None
        self._level_index = 0
        self._evolution: dict[str, Any] | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        controls = QHBoxLayout()
        controls.addWidget(self._label("Variable:"))
        self.variable_selector = QComboBox()
        self.variable_selector.addItems(list(_VARIABLES.keys()))
        self.variable_selector.currentTextChanged.connect(lambda _: self._redraw())
        controls.addWidget(self.variable_selector)

        self.run_button = QPushButton(f"🔄 Run Temporal Evolution ({_N_FRAMES} frames)")
        self.run_button.setToolTip(
            f"Real, off-thread compute_real_complexity_evolution() run - {_N_FRAMES} real\n"
            f"CoupledEarthSolver snapshots, {_STEPS_PER_FRAME} real integration steps apart.\n"
            "On demand, not automatic - a genuine multi-step solver run."
        )
        self.run_button.clicked.connect(self._start_evolution)
        controls.addWidget(self.run_button)
        controls.addStretch()
        layout.addLayout(controls)

        self.status_label = QLabel("Not yet computed.")
        self.status_label.setStyleSheet(label_style("text_muted", "xs"))
        layout.addWidget(self.status_label)

        frame_row = QHBoxLayout()
        frame_row.addWidget(self._label("Frame:"))
        self.frame_slider = QSlider(Qt.Orientation.Horizontal)
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(0)
        self.frame_slider.setEnabled(False)
        self.frame_slider.setFixedWidth(200)
        self.frame_slider.valueChanged.connect(lambda _: self._redraw())
        frame_row.addWidget(self.frame_slider)
        self.frame_label = QLabel("—")
        self.frame_label.setStyleSheet(label_style("text_secondary", "xs"))
        frame_row.addWidget(self.frame_label)
        frame_row.addStretch()
        layout.addLayout(frame_row)

        self.map_panel = AWCIMapPanel(
            "TEMPORAL EVOLUTION LAB", show_legend=False, show_info_boxes=False, show_demo_fallback=False
        )
        layout.addWidget(self.map_panel, stretch=1)

    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(label_style("text_muted", "xs"))
        return lbl

    def update_from_volume(self, volume: dict[str, Any], level_index: int) -> None:
        """Real re-slice of the already-computed volume for the level
        index only - see module docstring for why the evolution itself
        stays whatever it was (on-demand, not tied to a Workstation
        refresh)."""
        self._volume = volume
        self._level_index = level_index
        if self._evolution is not None:
            self._redraw()

    # ------------------------------------------------------- on-demand run

    def _start_evolution(self) -> None:
        if self._volume is None:
            self.status_label.setText("⚠ Run the Workstation's own volume computation first.")
            return
        self.run_button.setEnabled(False)
        self.status_label.setText(
            f"⏳ Computing real {_N_FRAMES}-frame evolution ({_STEPS_PER_FRAME} real solver steps apart)…"
        )
        worker = _EvolutionWorker(
            model=self._volume.get("model", "ARPEGE"),
            n_frames=_N_FRAMES,
            steps_per_frame=_STEPS_PER_FRAME,
            n_lat=len(self._volume["lats"]),
            n_lon=len(self._volume["lons"]),
            n_levels=self._volume["n_levels"],
            perturbation_scale=2.0,
            seed=1,
        )
        worker.signals.finished.connect(self._on_evolution_ready)
        worker.signals.failed.connect(self._on_evolution_failed)
        QThreadPool.globalInstance().start(worker)

    def _on_evolution_ready(self, evolution: dict[str, Any]) -> None:
        self.run_button.setEnabled(True)
        self._evolution = evolution
        self.status_label.setText(f"✅ Real {evolution['n_frames']}-frame evolution computed ({evolution['model']} grid).")
        self.frame_slider.setMaximum(evolution["n_frames"] - 1)
        self.frame_slider.setEnabled(True)
        self.frame_slider.setValue(0)
        self._redraw()

    def _on_evolution_failed(self, message: str) -> None:
        self.run_button.setEnabled(True)
        self.status_label.setText(f"⚠ Real temporal evolution failed: {message}")

    # ------------------------------------------------------------- redraw

    def _redraw(self) -> None:
        if self._evolution is None:
            return
        variable = self.variable_selector.currentText()
        spec = _VARIABLES[variable]
        frame = self.frame_slider.value()
        level = min(self._level_index, self._evolution["n_levels"] - 1)

        field = self._evolution[spec["key"]][frame, level]
        valid_time_h = self._evolution["valid_time_seconds"][frame] / 3600.0
        self.frame_label.setText(f"{frame + 1}/{self._evolution['n_frames']} — t+{valid_time_h:.2f}h")

        self.map_panel.set_external_field(
            self._evolution["lons"],
            self._evolution["lats"],
            field,
            f"Real {self._evolution['model']} — {variable} (t+{valid_time_h:.2f}h)",
            cmap=spec["cmap"],
            vmin=spec["vmin"],
            vmax=spec["vmax"],
            colorbar_label=f"{variable} ({spec['unit']})",
        )
