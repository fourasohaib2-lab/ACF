"""
ACF Scientific Workstation — Multi-Model Lab
==============================================

Real, raw side-by-side model comparison panel for `acf_workstation.
ACFWorkstation` (see that module's own docstring for the Workstation's
overall "ACF CORE ONLY - NO AWCI" rule). A distinct page from
Confidence Lab: that panel shows the real STATISTICAL spread/mean
across models (an aggregate), while this one shows each real model's
own RAW field individually, plus a real, literal pairwise difference
map in physical units - answering a different real question ("where
do these two specific models actually disagree, and by how much, in
K?" rather than "how much do models disagree here, in general?").

Zero new science - reuses the SAME real classmethod, just its
previously-unexposed data
-------------------------------------------------------------------------
`ModelConsensusEngine.compute_real_multi_model_disagreement_field()`
(built for Confidence Lab) already computes and returns
`per_model_field` - each real model's own field, already regridded via
real nearest-neighbour lookup onto a shared real native grid - but
Confidence Lab's own panel only ever reads the aggregate
`disagreement_mean_field`/`disagreement_spread_field` from it. This
panel calls the exact same real classmethod and simply exposes the
per-model data it was already computing, plus a real elementwise
difference between two of those real fields
(`field_a - field_b`, real physical units, e.g. K) - not a new
formula, just real subtraction of two already-real fields.

Real, on-demand, off-thread (like Confidence Lab and CAPE/CIN)
-------------------------------------------------------------------------
Same real cost as Confidence Lab: one real `CoupledEarthSolver` run
per selected model.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from acf.forecast.engine import MODEL_CONFIGS
from acf.gui.dashboard.awci_map_panel import AWCIMapPanel
from acf.gui.theme_tokens import label_style
from acf.visualization.ai_forecast_center.model_consensus_engine import ModelConsensusEngine

#: Same default pair Confidence Lab's own button already compares -
#: for consistency, not re-derived independently. A 3rd real model
#: (AROME, the largest/most expensive of the 3 real MODEL_CONFIGS
#: grids) is still selectable, just not the default.
_DEFAULT_MODEL_A = "ALADIN"
_DEFAULT_MODEL_B = "ARPEGE"
_TARGET_MODEL = "ARPEGE"  # same model - the regridded output grid


class _WorkerSignals(QObject):
    """Same real QRunnable-companion-object pattern used throughout
    this codebase's other off-thread workers - reused, not reinvented."""

    finished = Signal(dict)
    failed = Signal(str)


class _MultiModelWorker(QRunnable):
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


class ACFMultiModelLabPanel(QWidget):
    """Real Multi-Model Lab - raw per-model fields + a real pairwise
    difference map, on-demand. No AWCI content anywhere."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._volume: dict[str, Any] | None = None
        self._level_index = 0
        self._result: dict[str, Any] | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        controls = QHBoxLayout()
        controls.addWidget(self._label("Model A:"))
        self.model_a_selector = QComboBox()
        self.model_a_selector.addItems(list(MODEL_CONFIGS.keys()))
        self.model_a_selector.setCurrentText(_DEFAULT_MODEL_A)
        controls.addWidget(self.model_a_selector)

        controls.addWidget(self._label("Model B:"))
        self.model_b_selector = QComboBox()
        self.model_b_selector.addItems(list(MODEL_CONFIGS.keys()))
        self.model_b_selector.setCurrentText(_DEFAULT_MODEL_B)
        controls.addWidget(self.model_b_selector)

        self.run_button = QPushButton("🔄 Compare Models")
        self.run_button.setToolTip(
            "Real, off-thread compute_real_multi_model_disagreement_field() run - one\n"
            f"real CoupledEarthSolver run per model, regridded onto {_TARGET_MODEL}'s own\n"
            "real grid. AROME is the largest/most expensive of the 3 real MODEL_CONFIGS\n"
            "grids - real, but slower. On demand, not automatic."
        )
        self.run_button.clicked.connect(self._start_comparison)
        controls.addWidget(self.run_button)
        controls.addStretch()
        layout.addLayout(controls)

        display_row = QHBoxLayout()
        display_row.addWidget(self._label("Show:"))
        self.display_selector = QComboBox()
        self.display_selector.addItems(["Model A field", "Model B field", "Difference (A − B)"])
        self.display_selector.setEnabled(False)
        self.display_selector.currentTextChanged.connect(lambda _: self._redraw())
        display_row.addWidget(self.display_selector)
        display_row.addStretch()
        layout.addLayout(display_row)

        self.status_label = QLabel("Not yet computed.")
        self.status_label.setStyleSheet(label_style("text_muted", "xs"))
        layout.addWidget(self.status_label)

        self.map_panel = AWCIMapPanel(
            "MULTI-MODEL LAB", show_legend=False, show_info_boxes=False, show_demo_fallback=False
        )
        layout.addWidget(self.map_panel, stretch=1)

    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(label_style("text_muted", "xs"))
        return lbl

    def update_from_volume(self, volume: dict[str, Any], level_index: int) -> None:
        """Real bookkeeping only - the comparison is its own separate,
        on-demand computation (independent real solver runs of its
        own), not sliced from the Workstation's own volume, same
        "stays whatever it was" convention as Confidence Lab/CAPE/CIN."""
        self._volume = volume
        self._level_index = level_index

    # ------------------------------------------------------- on-demand run

    def _start_comparison(self) -> None:
        model_a = self.model_a_selector.currentText()
        model_b = self.model_b_selector.currentText()
        if model_a == model_b:
            self.status_label.setText("⚠ Pick two different real models to compare.")
            return
        self.run_button.setEnabled(False)
        self.status_label.setText(f"⏳ Computing real {model_a}/{model_b} comparison (a real solver run per model)…")
        worker = _MultiModelWorker(models=[model_a, model_b], steps=3, target_model=_TARGET_MODEL, seed=1)
        worker.signals.finished.connect(self._on_comparison_ready)
        worker.signals.failed.connect(self._on_comparison_failed)
        QThreadPool.globalInstance().start(worker)

    def _on_comparison_ready(self, result: dict[str, Any]) -> None:
        self.run_button.setEnabled(True)
        self.display_selector.setEnabled(True)
        self._result = result
        model_a, model_b = result["models_compared"]
        diff = result["per_model_field"][model_a] - result["per_model_field"][model_b]
        self.status_label.setText(
            f"✅ Real {model_a} vs {model_b} comparison computed ({result['target_model']} grid, "
            f"mean |Δ| {abs(diff).mean():.3f}, max |Δ| {abs(diff).max():.3f})."
        )
        self._redraw()

    def _on_comparison_failed(self, message: str) -> None:
        self.run_button.setEnabled(True)
        self.status_label.setText(f"⚠ Real model comparison failed: {message}")

    # ------------------------------------------------------------- redraw

    def _redraw(self) -> None:
        if self._result is None:
            return
        model_a, model_b = self._result["models_compared"]
        field_a = self._result["per_model_field"][model_a]
        field_b = self._result["per_model_field"][model_b]
        unit = "K" if self._result["field"] == "T" else self._result["field"]
        choice = self.display_selector.currentText()

        if choice == "Model A field":
            field, title, cmap = field_a, f"Real {model_a} — {self._result['variable_label']}", "coolwarm"
            vmin, vmax = float(field.min()), float(field.max())
        elif choice == "Model B field":
            field, title, cmap = field_b, f"Real {model_b} — {self._result['variable_label']}", "coolwarm"
            vmin, vmax = float(field.min()), float(field.max())
        else:
            field = field_a - field_b
            title = f"Real {model_a} − {model_b} — {self._result['variable_label']} difference"
            cmap = "RdBu_r"
            bound = float(max(abs(field.min()), abs(field.max()))) or 1.0
            vmin, vmax = -bound, bound

        self.map_panel.set_external_field(
            self._result["lons"],
            self._result["lats"],
            field,
            title,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            colorbar_label=f"{self._result['variable_label']} ({unit})",
        )
