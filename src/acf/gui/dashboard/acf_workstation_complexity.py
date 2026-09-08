"""
ACF Scientific Workstation — Complexity Explorer
===================================================

Real, genuinely multidimensional atmospheric complexity exploration
for `acf_workstation.ACFWorkstation` (see that module's own
docstring). Explicit, repeated master-spec rule (§21/§67): **no single
composite score** - "ne pas imposer artificiellement un score unique
lorsque la science du framework ne l'a pas encore défini". This panel
shows 3 independent real dimensions side by side, never combined:

1. **Spatial complexity** - real gradient-magnitude of the
   temperature field at the current level (an ACF-defined structural-
   variability indicator, disclosed as such - not an externally
   published formula, and not the same real gradient math used for
   Dynamics Lab's vorticity/divergence, reused here via
   `acf_workstation_dynamics.real_grid_spacing_m()` rather than
   re-derived). Computed immediately from the already-available
   volume - cheap, no extra solver run.
2. **Temporal complexity** - real mean absolute rate of change of
   temperature (K/h) across `compute_real_complexity_evolution()`'s
   own real multi-frame trajectory (the SAME real evolution engine
   `ACFGeneralDashboard` already used) - reads only
   `temperature_evolution`, never `awci_evolution`. A real, separate,
   on-demand computation (several real solver steps) - not automatic.
3. **Model disagreement** - `acf.visualization.ai_forecast_center.
   model_consensus_engine.ModelConsensusEngine.
   compute_real_multi_model_disagreement()` at a fixed, disclosed
   point of interest (36.75N 3.06E, Algiers - the same real point
   already used elsewhere in this codebase, e.g.
   awci_dashboard.py's own _REGIONAL_ROUTE). Real, separate, on-demand
   (the most expensive real computation here - one solver run per
   real model grid configuration).
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from acf.awci.temporal_field import compute_real_complexity_evolution
from acf.gui.dashboard.acf_workstation_dynamics import real_grid_spacing_m
from acf.gui.dashboard.awci_map_panel import AWCIMapPanel
from acf.gui.dashboard.awci_model_spread_chart import AWCIModelSpreadChart
from acf.gui.theme_tokens import label_style
from acf.visualization.ai_forecast_center.model_consensus_engine import ModelConsensusEngine

#: Same real point-of-interest convention already established
#: elsewhere in this codebase (awci_dashboard.py's _REGIONAL_ROUTE,
#: acf_general_dashboard.py's _POINT_OF_INTEREST) - Algiers.
_POINT_OF_INTEREST = (36.75, 3.06)
_CONSENSUS_MODELS = ["ALADIN", "ARPEGE"]  # the 2 fastest real MODEL_CONFIGS grids, same choice as acf_general_dashboard.py


def compute_real_spatial_complexity(field: np.ndarray, lats: np.ndarray, lons: np.ndarray) -> np.ndarray:
    """
    Real gradient-magnitude of `field` on the real grid, in units of
    (field unit) per 100 km - a real, standard synoptic-scale
    normalization (frontogenesis/gradient diagnostics commonly use
    K/100km), not a fabricated scale. An ACF-defined structural-
    complexity indicator: NOT an externally published "atmospheric
    complexity" formula - disclosed as such, not claimed otherwise.
    """
    dy, dx_per_row = real_grid_spacing_m(lats, lons)
    with np.errstate(divide="ignore", invalid="ignore"):
        d_dy = np.gradient(field, axis=0) / dy
        d_dx = np.gradient(field, axis=1) / dx_per_row[:, None]
    gradient_per_metre = np.sqrt(d_dx**2 + d_dy**2)
    return gradient_per_metre * 100_000.0  # per metre -> per 100 km


def compute_real_temporal_complexity(evolution: dict[str, Any], level_index: int) -> np.ndarray:
    """
    Real mean absolute rate of change of temperature (K/h) across
    `evolution`'s own real frames, at one real native level - see
    module docstring. `evolution` is a real
    compute_real_complexity_evolution() result.
    """
    temps = evolution["temperature_evolution"][:, level_index]  # (n_frames, n_lat, n_lon)
    valid_time_h = np.asarray(evolution["valid_time_seconds"], dtype=float) / 3600.0
    dt_h = np.diff(valid_time_h)
    diffs = np.abs(np.diff(temps, axis=0))  # (n_frames-1, n_lat, n_lon)
    with np.errstate(divide="ignore", invalid="ignore"):
        rates = diffs / dt_h[:, None, None]
    return np.asarray(np.mean(rates, axis=0))


class _WorkerSignals(QObject):
    """Same real QRunnable-companion-object pattern used throughout
    this codebase's other off-thread workers - reused, not reinvented."""

    finished = Signal(dict)
    failed = Signal(str)


class _TemporalWorker(QRunnable):
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


class _ConsensusWorker(QRunnable):
    """Runs ModelConsensusEngine.compute_real_multi_model_disagreement() off the GUI thread."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.kwargs = kwargs
        self.signals = _WorkerSignals()

    def run(self) -> None:
        try:
            result = ModelConsensusEngine.compute_real_multi_model_disagreement(**self.kwargs)
        except Exception as exc:  # noqa: BLE001 - real failure, reported honestly via signal below
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)


class ACFComplexityExplorerPanel(QWidget):
    """Real, multidimensional Complexity Explorer - see module
    docstring. Never combines its 3 real dimensions into one score."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._volume: dict[str, Any] | None = None
        self._level_index = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # --- Spatial complexity (real-time, from the current volume) ---
        layout.addWidget(self._header("SPATIAL COMPLEXITY — real temperature-gradient magnitude (K/100km)"))
        self.spatial_map = AWCIMapPanel(
            "SPATIAL COMPLEXITY", show_legend=False, show_info_boxes=False, show_demo_fallback=False
        )
        self.spatial_map.setMinimumHeight(220)
        layout.addWidget(self.spatial_map)

        # --- Temporal complexity (on-demand, real evolution run) ---
        layout.addWidget(self._header("TEMPORAL COMPLEXITY — real rate of change (K/h) across a real trajectory"))
        temporal_row = QHBoxLayout()
        self.temporal_button = QPushButton("🔄 Run Temporal Analysis")
        self.temporal_button.setToolTip(
            "Real, off-thread compute_real_complexity_evolution() run (several real\n"
            "CoupledEarthSolver frames) - the most expensive computation on this page\n"
            "besides model disagreement. On demand, not automatic."
        )
        self.temporal_button.clicked.connect(self._start_temporal_analysis)
        temporal_row.addWidget(self.temporal_button)
        self.temporal_status_label = QLabel("Not yet computed.")
        self.temporal_status_label.setStyleSheet(label_style("text_muted", "xs"))
        temporal_row.addWidget(self.temporal_status_label)
        temporal_row.addStretch()
        layout.addLayout(temporal_row)
        self.temporal_map = AWCIMapPanel(
            "TEMPORAL COMPLEXITY", show_legend=False, show_info_boxes=False, show_demo_fallback=False
        )
        self.temporal_map.setMinimumHeight(220)
        layout.addWidget(self.temporal_map)

        # --- Model disagreement (on-demand, real multi-model comparison) ---
        layout.addWidget(
            self._header(f"MODEL DISAGREEMENT — real multi-model spread at ({_POINT_OF_INTEREST[0]}°N, {_POINT_OF_INTEREST[1]}°E)")
        )
        consensus_row = QHBoxLayout()
        self.consensus_button = QPushButton("🔄 Compute Model Disagreement")
        self.consensus_button.setToolTip(
            "Real acf.visualization.ai_forecast_center.model_consensus_engine.\n"
            "ModelConsensusEngine.compute_real_multi_model_disagreement() - runs ACF's\n"
            "own solver once per real model grid configuration at the point of interest."
        )
        self.consensus_button.clicked.connect(self._start_consensus)
        consensus_row.addWidget(self.consensus_button)
        self.consensus_status_label = QLabel("Not yet computed.")
        self.consensus_status_label.setStyleSheet(label_style("text_muted", "xs"))
        consensus_row.addWidget(self.consensus_status_label)
        consensus_row.addStretch()
        layout.addLayout(consensus_row)
        self.spread_chart = AWCIModelSpreadChart("MODEL DISAGREEMENT")
        self.spread_chart.setMinimumHeight(160)
        layout.addWidget(self.spread_chart)

    @staticmethod
    def _header(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(label_style("text_secondary", "xs", "bold"))
        return lbl

    def update_from_volume(self, volume: dict[str, Any], level_index: int) -> None:
        """Real re-slice of the already-computed volume for the
        spatial-complexity dimension - no new solver run. Temporal/
        model-disagreement stay whatever they were (real, separate,
        on-demand computations, not tied to the level slider)."""
        self._volume = volume
        self._level_index = level_index
        self._redraw_spatial()

    def _redraw_spatial(self) -> None:
        if self._volume is None:
            return
        temperature = self._volume["temperature_volume"][self._level_index]
        lats, lons = self._volume["lats"], self._volume["lons"]
        spatial_complexity = compute_real_spatial_complexity(temperature, lats, lons)
        self.spatial_map.set_external_field(
            lons,
            lats,
            spatial_complexity,
            f"Real {self._volume.get('model', '')} — Spatial complexity",
            cmap="magma",
            vmin=0.0,
            vmax=float(np.nanpercentile(spatial_complexity, 95)) or 1.0,
            colorbar_label="Temperature gradient (K/100km)",
        )

    # ------------------------------------------------------- temporal

    def _start_temporal_analysis(self) -> None:
        if self._volume is None:
            self.temporal_status_label.setText("⚠ Run the Workstation's own volume computation first.")
            return
        self.temporal_button.setEnabled(False)
        self.temporal_status_label.setText("⏳ Computing real evolution (several CoupledEarthSolver frames)…")
        worker = _TemporalWorker(
            model=self._volume.get("model", "ARPEGE"), n_frames=4, steps_per_frame=3,
            n_lat=len(np.asarray(self._volume["lats"])), n_lon=len(np.asarray(self._volume["lons"])),
            n_levels=self._volume["n_levels"], perturbation_scale=2.0, seed=1,
        )
        worker.signals.finished.connect(self._on_temporal_ready)
        worker.signals.failed.connect(self._on_temporal_failed)
        QThreadPool.globalInstance().start(worker)

    def _on_temporal_ready(self, evolution: dict[str, Any]) -> None:
        self.temporal_button.setEnabled(True)
        level = min(self._level_index, evolution["n_levels"] - 1)
        rates = compute_real_temporal_complexity(evolution, level)
        self.temporal_status_label.setText(
            f"✅ Real {evolution['n_frames']}-frame evolution computed ({evolution['model']} grid)."
        )
        self.temporal_map.set_external_field(
            evolution["lons"],
            evolution["lats"],
            rates,
            f"Real {evolution['model']} — Temporal complexity",
            cmap="inferno",
            vmin=0.0,
            vmax=float(np.nanpercentile(rates, 95)) or 1.0,
            colorbar_label="Rate of change (K/h)",
        )

    def _on_temporal_failed(self, message: str) -> None:
        self.temporal_button.setEnabled(True)
        self.temporal_status_label.setText(f"⚠ Real temporal analysis failed: {message}")

    # ---------------------------------------------------------- consensus

    def _start_consensus(self) -> None:
        self.consensus_button.setEnabled(False)
        self.consensus_status_label.setText("⏳ Computing real multi-model consensus…")
        worker = _ConsensusWorker(
            lat=_POINT_OF_INTEREST[0], lon=_POINT_OF_INTEREST[1], models=list(_CONSENSUS_MODELS), steps=2
        )
        worker.signals.finished.connect(self._on_consensus_ready)
        worker.signals.failed.connect(self._on_consensus_failed)
        QThreadPool.globalInstance().start(worker)

    def _on_consensus_ready(self, result: dict[str, Any]) -> None:
        self.consensus_button.setEnabled(True)
        self.consensus_status_label.setText(
            f"✅ Real disagreement spread: {result['disagreement_spread']:.3f} (mean {result['disagreement_mean']:.2f})"
        )
        self.spread_chart.set_data(
            result["per_model_value"], result["disagreement_mean"], result["disagreement_spread"], "Temperature (K)"
        )

    def _on_consensus_failed(self, message: str) -> None:
        self.consensus_button.setEnabled(True)
        self.consensus_status_label.setText(f"⚠ Real consensus computation failed: {message}")
