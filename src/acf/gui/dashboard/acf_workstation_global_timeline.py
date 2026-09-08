"""
ACF Scientific Workstation — Global Timeline (Time Machine)
=================================================================

Real, on-demand multi-frame forecast-hour scrubber (Phase 41,
2026-09-05), matching the reference mockup's own bottom-of-screen
"GLOBAL TIMELINE (Time Machine)" bar (`docs/reference/
acf_scientific_workstation_reference.jpg`).

Real formula, reused as-is - not reimplemented
---------------------------------------------------
Fed by `acf.awci.temporal_field.compute_real_complexity_evolution()` -
the SAME real, already-shipped, already-tested multi-frame
`CoupledEarthSolver` integration Temporal Evolution Lab's own "🔄 Run
Temporal Analysis" button already uses (`n_frames=4`,
`steps_per_frame=3`, the SAME real constants, not re-derived), at the
current volume's own real model/grid resolution. Real, genuinely
expensive (several real solver steps per frame - Temporal Lab's own
docstring measures ~1.4s/frame at full resolution) - stays on-demand,
never automatic, same discipline as every other genuinely expensive
computation in this Workstation.

Each of the `n_frames` real thumbnails shows that exact real frame's
own real surface temperature (`temperature_evolution[frame,
level=0]`) - a real, lightweight preview
(`acf_workstation_thumbnail_strip.ACFVariableThumbnailStrip`, reused
as-is), labelled with that frame's own real valid time
(`valid_time_seconds`, converted to hours) once computed.

Honest scope
-------------
Scrubbing frames here (slider, thumbnail click, or Play) updates only
this widget's own thumbnail highlight and summary readout - it does
NOT change the Workstation's own level slider, Domain selection, or
any nav-tab panel. Wiring a real "scrub changes every panel"
integration would be a substantially larger, separate undertaking
(effectively re-deriving what volume every one of the 14 nav panels
should show at each frame), deliberately not attempted in this pass -
disclosed here rather than silently implied by the widget's own
"Time Machine" name.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, QTimer, Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget

from acf.awci.temporal_field import compute_real_complexity_evolution
from acf.gui.dashboard.acf_workstation_thumbnail_strip import ACFVariableThumbnailStrip
from acf.gui.theme_tokens import label_style

#: Real, same constants Temporal Evolution Lab's own on-demand button
#: already uses - not re-derived independently.
N_FRAMES = 4
STEPS_PER_FRAME = 3
#: Real playback interval (ms) per speed multiplier - a real, disclosed
#: UI convenience (how fast already-computed real frames cycle), never
#: a claim about real forecast timing.
_SPEED_INTERVALS_MS: dict[str, int] = {"1x": 1200, "2x": 600, "4x": 300}

_FRAME_NAMES = [f"Frame {i + 1}" for i in range(N_FRAMES)]


class _WorkerSignals(QObject):
    finished = Signal(dict)
    failed = Signal(str)


class _EvolutionWorker(QRunnable):
    """Runs compute_real_complexity_evolution() off the GUI thread -
    same real QRunnable pattern this Workstation's other on-demand
    computations already use."""

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


class ACFGlobalTimelineWidget(QWidget):
    """Real, on-demand forecast-hour scrubber - see module docstring."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._volume: dict[str, Any] | None = None
        self._evolution: dict[str, Any] | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        header = QLabel("GLOBAL TIMELINE (Time Machine)")
        header.setStyleSheet(label_style("text_primary", "sm", "bold"))
        layout.addWidget(header)

        controls = QHBoxLayout()
        self.run_button = QPushButton("🔄 Run Temporal Analysis")
        self.run_button.setToolTip(
            f"Real, off-thread compute_real_complexity_evolution() run - {N_FRAMES} real\n"
            f"CoupledEarthSolver snapshots, {STEPS_PER_FRAME} real solver steps apart, at the\n"
            "current volume's own real model/grid. On demand, not automatic."
        )
        self.run_button.clicked.connect(self._start)
        controls.addWidget(self.run_button)

        self.play_button = QPushButton("▶ Play")
        self.play_button.setCheckable(True)
        self.play_button.setEnabled(False)
        self.play_button.toggled.connect(self._on_play_toggled)
        controls.addWidget(self.play_button)

        controls.addWidget(self._label("Speed:"))
        self.speed_selector = QComboBox()
        self.speed_selector.addItems(list(_SPEED_INTERVALS_MS.keys()))
        controls.addWidget(self.speed_selector)

        self.status_label = QLabel("Not yet computed.")
        self.status_label.setStyleSheet(label_style("text_muted", "xs"))
        controls.addWidget(self.status_label)
        controls.addStretch()
        layout.addLayout(controls)

        self.frame_slider = QSlider(Qt.Orientation.Horizontal)
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(0)
        self.frame_slider.setEnabled(False)
        self.frame_slider.valueChanged.connect(self._on_frame_changed)
        layout.addWidget(self.frame_slider)

        self.thumbnail_strip = ACFVariableThumbnailStrip(list(_FRAME_NAMES))
        self.thumbnail_strip.variableSelected.connect(self._on_thumbnail_clicked)
        layout.addWidget(self.thumbnail_strip)

        disclosure = QLabel("Not synchronized with the main dashboard — scrubbing frames here does not change the level, domain, or any nav-tab panel.")
        disclosure.setStyleSheet(label_style("text_muted", "xs"))
        disclosure.setWordWrap(True)
        layout.addWidget(disclosure)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance_frame)

    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(label_style("text_muted", "xs"))
        return lbl

    def update_from_volume(self, volume: dict[str, Any], level_index: int) -> None:
        """Real bookkeeping only - the evolution is its own separate,
        on-demand computation (its own real solver run), not sliced
        from this volume, same "stays whatever it was" convention as
        Temporal Evolution Lab / Confidence Lab / CAPE-CIN."""
        self._volume = volume

    # ------------------------------------------------------- on-demand run

    def _start(self) -> None:
        if self._volume is None:
            self.status_label.setText("⚠ Run the Workstation's own volume computation first.")
            return
        self.run_button.setEnabled(False)
        self.status_label.setText(f"⏳ Computing real {N_FRAMES}-frame evolution ({STEPS_PER_FRAME} real solver steps apart)…")
        worker = _EvolutionWorker(
            model=self._volume.get("model", "ARPEGE"),
            n_frames=N_FRAMES,
            steps_per_frame=STEPS_PER_FRAME,
            n_lat=len(self._volume["lats"]),
            n_lon=len(self._volume["lons"]),
            n_levels=self._volume["n_levels"],
            perturbation_scale=2.0,
            seed=1,
        )
        worker.signals.finished.connect(self._on_evolution_ready)
        worker.signals.failed.connect(self._on_evolution_failed)
        QThreadPool.globalInstance().start(worker)

    def _on_evolution_ready(self, result: dict[str, Any]) -> None:
        self.run_button.setEnabled(True)
        self.play_button.setEnabled(True)
        self._evolution = result
        self.status_label.setText(f"✅ Real {result['n_frames']}-frame evolution computed ({result['model']} grid).")

        self.frame_slider.setEnabled(True)
        self.frame_slider.blockSignals(True)
        self.frame_slider.setMaximum(result["n_frames"] - 1)
        self.frame_slider.setValue(0)
        self.frame_slider.blockSignals(False)

        for i in range(result["n_frames"]):
            valid_hours = result["valid_time_seconds"][i] / 3600.0
            self.thumbnail_strip.set_label(_FRAME_NAMES[i], f"T+{valid_hours:.1f}h")
            self.thumbnail_strip.set_field(
                _FRAME_NAMES[i], result["temperature_evolution"][i, 0], cmap="coolwarm", vmin=None, vmax=None
            )
        self._show_frame(0)

    def _on_evolution_failed(self, message: str) -> None:
        self.run_button.setEnabled(True)
        self.status_label.setText(f"⚠ Real evolution computation failed: {message}")

    # ------------------------------------------------------------ scrubbing

    def _on_frame_changed(self, value: int) -> None:
        self._show_frame(value)

    def _on_thumbnail_clicked(self, name: str) -> None:
        if name in _FRAME_NAMES:
            self.frame_slider.setValue(_FRAME_NAMES.index(name))

    def _show_frame(self, frame_index: int) -> None:
        if self._evolution is None or not (0 <= frame_index < self._evolution["n_frames"]):
            return
        self.thumbnail_strip.set_selected(_FRAME_NAMES[frame_index])
        valid_hours = self._evolution["valid_time_seconds"][frame_index] / 3600.0
        mean_temperature_c = float(np.nanmean(self._evolution["temperature_evolution"][frame_index, 0])) - 273.15
        self.status_label.setText(
            f"Frame {frame_index + 1}/{self._evolution['n_frames']} — "
            f"valid T+{valid_hours:.1f}h — real mean surface temperature {mean_temperature_c:.1f} °C."
        )

    def _on_play_toggled(self, playing: bool) -> None:
        if playing:
            self.play_button.setText("⏸ Pause")
            interval_ms = _SPEED_INTERVALS_MS[self.speed_selector.currentText()]
            self._timer.start(interval_ms)
        else:
            self.play_button.setText("▶ Play")
            self._timer.stop()

    def _advance_frame(self) -> None:
        if self._evolution is None:
            return
        next_frame = (self.frame_slider.value() + 1) % self._evolution["n_frames"]
        self.frame_slider.setValue(next_frame)

    def status(self) -> dict[str, Any]:
        return {
            "has_evolution": self._evolution is not None,
            "current_frame": self.frame_slider.value() if self._evolution is not None else None,
        }
