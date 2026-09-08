"""
ACF Scientific Workstation — ACF Pipeline Monitor (display widget)
=======================================================================

Real, honest per-stage status box (Phase 32, 2026-09-05), matching the
Workstation's own reference mockup's left-column "ACF PIPELINE
MONITOR" box exactly in position and the real stage names it shows
(INGESTION/QC/NORMALIZATION/MODULES/INTERACTIONS/ANALYSIS/
VISUALIZATION).

This widget is a pure display - it never computes a status itself.
`ACFWorkstation` calls `set_stage(name, status, detail)` from real
places in its own pipeline (see `acf_workstation_pipeline_checks.py`'s
own module docstring for exactly what each stage verifies); a stage
shows "—" (pending) until that real step has actually run for the
CURRENT volume, "RUNNING" while genuinely in progress, then "OK"/
"WARN"/"FAIL" reflecting a real, verifiable outcome - never a
fabricated or merely cosmetic tick.
"""

from __future__ import annotations

from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

from acf.gui.theme_tokens import COLORS

#: Real, ordered pipeline stages this Workstation's own code actually
#: goes through on a real run - see acf_workstation.py's own
#: refresh()/_on_volume_ready() for where each one is set.
STAGES: tuple[str, ...] = (
    "Ingestion",
    "QC",
    "Normalization",
    "Modules",
    "Interactions",
    "Analysis",
    "Visualization",
)

_STATUS_COLOR: dict[str, str] = {
    "OK": COLORS["success"],
    "WARN": COLORS["warning"],
    "FAIL": COLORS["danger"],
    "RUNNING": COLORS["accent_secondary"],
    "—": COLORS["text_muted"],
}


class ACFPipelineMonitorWidget(QWidget):
    """Real, honest pipeline-stage status box - see module docstring."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("ACF PIPELINE MONITOR")
        layout = QVBoxLayout(group)
        layout.setSpacing(2)
        outer.addWidget(group)

        self._labels: dict[str, QLabel] = {}
        for name in STAGES:
            label = QLabel()
            layout.addWidget(label)
            self._labels[name] = label
        self.reset()

    def reset(self) -> None:
        """Real, honest starting state - every stage genuinely pending
        (nothing has run yet for whatever volume comes next)."""
        for name in STAGES:
            self._set(name, "—", "Not yet reached in this run.")

    def set_stage(self, name: str, status: str, detail: str = "") -> None:
        """Set one real stage's real, current outcome.

        Parameters
        ----------
        name : one of STAGES.
        status : "—" (pending), "RUNNING", "OK", "WARN", or "FAIL".
        detail : the real, human-readable reason behind `status` -
            shown as this label's tooltip, never fabricated filler.
        """
        if name not in self._labels:
            raise ValueError(f"Unknown real pipeline stage {name!r} - expected one of {STAGES}")
        self._set(name, status, detail)

    def _set(self, name: str, status: str, detail: str) -> None:
        color = _STATUS_COLOR.get(status, COLORS["text_muted"])
        label = self._labels[name]
        label.setText(f"{name.upper():<14}[{status}]")
        label.setToolTip(detail or "Not yet reached in this run.")
        label.setStyleSheet(f"color: {color}; font-family: monospace; font-size: 11px;")

    def status_snapshot(self) -> dict[str, str]:
        """Real, current status per stage, read directly back off each
        label's own displayed `[STATUS]` tag - never a separately
        tracked value that could drift from what's actually shown."""
        snapshot: dict[str, str] = {}
        for name, label in self._labels.items():
            text = label.text()
            snapshot[name] = text.split("[", 1)[1].rstrip("]") if "[" in text else "—"
        return snapshot
