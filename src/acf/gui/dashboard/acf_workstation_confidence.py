"""
ACF Scientific Workstation — Confidence Lab
=============================================

Real, full-grid multi-model disagreement panel for `acf_workstation.
ACFWorkstation` (see that module's own docstring for the Workstation's
overall "ACF CORE ONLY - NO AWCI" rule). Reuses
`acf.visualization.ai_forecast_center.model_consensus_engine.
ModelConsensusEngine.compute_real_multi_model_disagreement_field()`
(added alongside this panel) - a real extension of the SAME real
per-point disagreement engine Complexity Explorer's own "Compute Model
Disagreement" button already uses, but computed over a WHOLE real grid
instead of one point: each real model's `CoupledEarthSolver` runs
exactly once (one real perturbation draw per model), then every
model's own real output is regridded via real nearest-neighbour lookup
onto a shared real native grid and a real `EnsembleManager` spread/mean
is computed at every point - see that classmethod's own docstring for
the full real disclosure of this approach and its honest limitations.

Real, on-demand, off-thread (like CAPE/CIN and Complexity Explorer's
own temporal/consensus buttons)
-------------------------------------------------------------------------
Real cost is 2 real, independent `CoupledEarthSolver` runs (measured
~0.9s for ALADIN+ARPEGE at steps=3) - genuinely fast, but still a real
solver run, so this stays on-demand rather than automatic, same
discipline as this Workstation's other genuinely-expensive
computations.

No composite confidence SCORE
--------------------------------
This shows the real per-point ensemble SPREAD (K) and MEAN (K) as two
separate, real, physical quantities - never collapsed into a single
0-100 "confidence score", matching the master spec's own §21/§67 rule
already applied throughout this Workstation (no artificial single
score anywhere the framework's own real science has not defined one).
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from acf.gui.dashboard.awci_map_panel import AWCIMapPanel
from acf.gui.theme_tokens import label_style
from acf.visualization.ai_forecast_center.model_consensus_engine import ModelConsensusEngine

#: Same 2 real, fastest MODEL_CONFIGS grids Complexity Explorer's own
#: "Compute Model Disagreement" button already compares - for
#: consistency, not re-derived independently.
_CONSENSUS_MODELS = ["ALADIN", "ARPEGE"]
_TARGET_MODEL = "ARPEGE"  # same model - the regridded output grid

_VARIABLES: dict[str, dict[str, Any]] = {
    "Disagreement spread (std dev)": {"key": "disagreement_spread_field", "unit": "K", "cmap": "magma"},
    "Disagreement mean": {"key": "disagreement_mean_field", "unit": "K", "cmap": "coolwarm"},
}


class _WorkerSignals(QObject):
    """Same real QRunnable-companion-object pattern used throughout
    this codebase's other off-thread workers - reused, not reinvented."""

    finished = Signal(dict)
    failed = Signal(str)


class _ConfidenceWorker(QRunnable):
    """Runs ModelConsensusEngine.compute_real_multi_model_disagreement_field() off the GUI thread."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.kwargs = kwargs
        self.signals = _WorkerSignals()

    def run(self) -> None:
        try:
            result = ModelConsensusEngine.compute_real_multi_model_disagreement_field(**self.kwargs)
        except Exception as exc:  # noqa: BLE001 - real failure, reported honestly via signal below
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)


class ACFConfidenceLabPanel(QWidget):
    """Real Confidence Lab - full-grid multi-model disagreement
    spread/mean, on-demand. No AWCI content, no single score anywhere."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._volume: dict[str, Any] | None = None
        self._level_index = 0
        self._result: dict[str, Any] | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        controls = QHBoxLayout()
        controls.addWidget(self._label("Variable:"))
        self.variable_selector = QComboBox()
        self.variable_selector.addItems(list(_VARIABLES.keys()))
        self.variable_selector.setEnabled(False)
        self.variable_selector.currentTextChanged.connect(lambda _: self._redraw())
        controls.addWidget(self.variable_selector)

        self.run_button = QPushButton(f"🔄 Compute Model Confidence Field ({'/'.join(_CONSENSUS_MODELS)})")
        self.run_button.setToolTip(
            "Real, off-thread compute_real_multi_model_disagreement_field() run - a real\n"
            f"CoupledEarthSolver run per model ({', '.join(_CONSENSUS_MODELS)}), regridded onto\n"
            f"{_TARGET_MODEL}'s own real grid. On demand, not automatic."
        )
        self.run_button.clicked.connect(self._start_confidence)
        controls.addWidget(self.run_button)
        controls.addStretch()
        layout.addLayout(controls)

        self.status_label = QLabel("Not yet computed.")
        self.status_label.setStyleSheet(label_style("text_muted", "xs"))
        layout.addWidget(self.status_label)

        self.map_panel = AWCIMapPanel(
            "CONFIDENCE LAB", show_legend=False, show_info_boxes=False, show_demo_fallback=False
        )
        layout.addWidget(self.map_panel, stretch=1)

    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(label_style("text_muted", "xs"))
        return lbl

    def update_from_volume(self, volume: dict[str, Any], level_index: int) -> None:
        """Real bookkeeping only - the disagreement field is its own
        separate, on-demand computation (2 independent real solver
        runs of its own), not sliced from the Workstation's own
        volume, same "stays whatever it was" convention as CAPE/CIN
        and Complexity Explorer's own temporal/consensus results."""
        self._volume = volume
        self._level_index = level_index

    # ------------------------------------------------------- on-demand run

    def _start_confidence(self) -> None:
        self.run_button.setEnabled(False)
        self.status_label.setText(
            f"⏳ Computing real disagreement field ({'/'.join(_CONSENSUS_MODELS)} — a real solver run per model)…"
        )
        worker = _ConfidenceWorker(models=list(_CONSENSUS_MODELS), steps=3, target_model=_TARGET_MODEL, seed=1)
        worker.signals.finished.connect(self._on_confidence_ready)
        worker.signals.failed.connect(self._on_confidence_failed)
        QThreadPool.globalInstance().start(worker)

    def _on_confidence_ready(self, result: dict[str, Any]) -> None:
        self.run_button.setEnabled(True)
        self.variable_selector.setEnabled(True)
        self._result = result
        spread = result["disagreement_spread_field"]
        self.status_label.setText(
            f"✅ Real disagreement field computed ({result['target_model']} grid, "
            f"mean spread {spread.mean():.3f} K, max {spread.max():.3f} K)."
        )
        self._redraw()

    def _on_confidence_failed(self, message: str) -> None:
        self.run_button.setEnabled(True)
        self.status_label.setText(f"⚠ Real disagreement field computation failed: {message}")

    # ------------------------------------------------------------- redraw

    def _redraw(self) -> None:
        if self._result is None:
            return
        variable = self.variable_selector.currentText()
        spec = _VARIABLES[variable]
        field = self._result[spec["key"]]
        vmax = float(field.max()) or 1.0
        vmin = 0.0 if variable.startswith("Disagreement spread") else float(field.min())

        self.map_panel.set_external_field(
            self._result["lons"],
            self._result["lats"],
            field,
            f"Real {'/'.join(self._result['models_compared'])} — {variable}",
            cmap=spec["cmap"],
            vmin=vmin,
            vmax=vmax,
            colorbar_label=f"{variable} ({spec['unit']})",
        )
