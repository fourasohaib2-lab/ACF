"""
ACF Scientific Workstation — System Footer
==============================================

Matches acf_workstation_reference.jpg's bottom row: four real cards -
Data Sources, System Status, Running Jobs, Recent Activity. System
Status/Running Jobs come from the real
`acf.hpc_connector.HPCConnectionManager.get_status_summary()`, and
Data Sources (AROME/ALADIN) come from that same manager's real
`meteorological_stack` dict, populated by `AromeAladinDetector`
(unchanged by this session's dashboard cleanup - it is a real
subsystem, not a dashboard). ARPEGE/WRF/Observations have no real
per-model detector in this codebase (only AROME/ALADIN do) - shown
honestly as "NOT_DETECTABLE" rather than fabricating a status the app
cannot actually check. Recent Activity is a plain, real append-only
log of this Workstation's own real actions (e.g. "AROME forecast
completed"), fed by the composer - this panel never fabricates a log
entry.

Before any real HPC status has been pushed in via `update_from_hpc`,
the panel shows an honest "Not Connected"/"NOT_CHECKED" placeholder -
it must never default to a connected/healthy look just because the UI
itself is running.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QTextEdit, QVBoxLayout, QWidget

from acf.gui.theme_tokens import card_frame_style, label_style

_NOT_CONNECTED_TEXT = "Not Connected — Scheduler: NOT_AVAILABLE"
_NOT_CHECKED_TEXT = "NOT_CHECKED"

#: (key, display name) - AROME/ALADIN have a real detector
#: (`AromeAladinDetector`); ARPEGE/WRF/Observations don't, and are
#: shown as an honest "NOT_DETECTABLE" rather than fabricated.
_DATA_SOURCES: list[tuple[str, str]] = [
    ("arome", "AROME"),
    ("aladin", "ALADIN"),
    ("arpege", "ARPEGE"),
    ("wrf", "WRF"),
    ("observations", "Observations"),
]


def _card(title: str) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setStyleSheet(card_frame_style())
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(12, 10, 12, 10)
    layout.setSpacing(6)
    heading = QLabel(title)
    heading.setStyleSheet(label_style("text_primary", "xs", "bold"))
    layout.addWidget(heading)
    return frame, layout


def _status_dot(color: str) -> QLabel:
    dot = QLabel()
    dot.setFixedSize(8, 8)
    dot.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
    return dot


class SystemFooterPanel(QWidget):
    """Real Data Sources / System Status / Running Jobs / Recent Activity, as 4 cards."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(10)

        # --- Data Sources card ------------------------------------------
        sources_card, sources_layout = _card("Data Sources")
        self._source_labels: dict[str, QLabel] = {}
        for key, name in _DATA_SOURCES:
            row = QHBoxLayout()
            row.addWidget(_status_dot("#4b5563"))
            name_label = QLabel(name)
            name_label.setStyleSheet(label_style("text_secondary", "xs"))
            row.addWidget(name_label)
            row.addStretch(1)
            status_label = QLabel(_NOT_CHECKED_TEXT)
            status_label.setStyleSheet(label_style("text_muted", "xs"))
            row.addWidget(status_label)
            sources_layout.addLayout(row)
            self._source_labels[key] = status_label
        sources_layout.addStretch(1)
        outer.addWidget(sources_card, stretch=1)

        # Back-compat attribute names for existing callers/tests.
        self.arome_status_label = self._source_labels["arome"]
        self.aladin_status_label = self._source_labels["aladin"]

        # --- System Status card ------------------------------------------
        status_card, status_layout = _card("System Status")
        self.system_status_label = QLabel(_NOT_CONNECTED_TEXT)
        self.system_status_label.setStyleSheet(label_style("text_secondary", "xs"))
        self.system_status_label.setWordWrap(True)
        status_layout.addWidget(self.system_status_label)
        status_layout.addStretch(1)
        outer.addWidget(status_card, stretch=1)

        # --- Running Jobs card ------------------------------------------
        jobs_card, jobs_layout = _card("Running Jobs")
        self.running_jobs_label = QLabel(f"Running Jobs: {_NOT_CHECKED_TEXT}")
        self.running_jobs_label.setStyleSheet(label_style("text_primary", "lg", "bold"))
        self.running_jobs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        jobs_layout.addWidget(self.running_jobs_label)
        jobs_layout.addStretch(1)
        outer.addWidget(jobs_card, stretch=1)

        # --- Recent Activity card ------------------------------------------
        activity_card, activity_layout = _card("Recent Activity")
        self.activity_log = QTextEdit()
        self.activity_log.setReadOnly(True)
        self.activity_log.setFrameShape(QFrame.Shape.NoFrame)
        self.activity_log.setStyleSheet("background: transparent;")
        activity_layout.addWidget(self.activity_log)
        outer.addWidget(activity_card, stretch=2)

    def update_from_hpc(self, hpc: Any) -> None:
        """Refresh System Status/Running Jobs/Data Sources from a real HPCConnectionManager.

        Calls the manager's real `get_status_summary()` (not a guessed
        `get_status()`) and renders exactly what it reports - including an
        honest "Not Connected" state when `connected` is False. Never
        assumes a connected/healthy status.

        Also reads the manager's real `meteorological_stack` dict (populated
        by `AromeAladinDetector` - either a genuine per-model detection, or
        `AromeAladinDetector.not_detected()`'s honest all-False default when
        the cluster was never probed) to drive the AROME/ALADIN Data Sources
        rows. ARPEGE/WRF/Observations have no real detector in this
        codebase and are shown as "NOT_DETECTABLE".
        """
        status = hpc.get_status_summary()
        connected = bool(status.get("connected"))
        scheduler = status.get("scheduler") or "NOT_AVAILABLE"
        active_jobs = status.get("active_jobs_count")

        self.system_status_label.setText(
            f"{'Connected' if connected else 'Not Connected'} — Scheduler: {scheduler}"
        )
        if active_jobs is not None:
            self.running_jobs_label.setText(str(active_jobs))
        else:
            self.running_jobs_label.setText(_NOT_CHECKED_TEXT)

        stack = getattr(hpc, "meteorological_stack", {}) or {}
        self._source_labels["arome"].setText("Active" if stack.get("has_arome") else "Not Detected")
        self._source_labels["aladin"].setText("Active" if stack.get("has_aladin") else "Not Detected")
        self._source_labels["arpege"].setText("NOT_DETECTABLE")
        self._source_labels["wrf"].setText("NOT_DETECTABLE")
        self._source_labels["observations"].setText("NOT_DETECTABLE")

    def append_activity(self, message: str) -> None:
        self.activity_log.append(message)
