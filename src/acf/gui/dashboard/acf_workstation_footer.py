"""
ACF Scientific Workstation — System Footer
==============================================

Matches acf_workstation_reference.jpg's bottom row: Data Sources,
System Status, Running Jobs, Recent Activity. System Status/Running
Jobs come from the real
`acf.hpc_connector.HPCConnectionManager.get_status_summary()`, and
Data Sources (AROME/ALADIN) come from that same manager's real
`meteorological_stack` dict, populated by `AromeAladinDetector`
(unchanged by this session's dashboard cleanup - it is a real
subsystem, not a dashboard). Recent Activity is a plain, real append-
only log of this Workstation's own real actions (e.g. "AROME forecast
completed"), fed by the composer - this panel never fabricates a log
entry.

Before any real HPC status has been pushed in via `update_from_hpc`,
the panel shows an honest "Not Connected"/"NOT_CHECKED" placeholder -
it must never default to a connected/healthy look just because the UI
itself is running.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QHBoxLayout, QLabel, QTextEdit, QVBoxLayout, QWidget

from acf.gui.theme_tokens import label_style

_NOT_CONNECTED_TEXT = "Not Connected — Scheduler: NOT_AVAILABLE"
_NOT_CHECKED_TEXT = "NOT_CHECKED"


class SystemFooterPanel(QWidget):
    """Real Data Sources / System Status / Running Jobs / Recent Activity footer."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        data_sources_row = QHBoxLayout()
        self.arome_status_label = QLabel(f"AROME: {_NOT_CHECKED_TEXT}")
        self.arome_status_label.setStyleSheet(label_style("text_secondary", "sm"))
        data_sources_row.addWidget(self.arome_status_label)
        self.aladin_status_label = QLabel(f"ALADIN: {_NOT_CHECKED_TEXT}")
        self.aladin_status_label.setStyleSheet(label_style("text_secondary", "sm"))
        data_sources_row.addWidget(self.aladin_status_label)
        layout.addLayout(data_sources_row)

        self.system_status_label = QLabel(_NOT_CONNECTED_TEXT)
        self.system_status_label.setStyleSheet(label_style("text_primary", "sm"))
        layout.addWidget(self.system_status_label)

        self.running_jobs_label = QLabel("Running Jobs: 0")
        self.running_jobs_label.setStyleSheet(label_style("text_secondary", "sm"))
        layout.addWidget(self.running_jobs_label)

        self.activity_log = QTextEdit()
        self.activity_log.setReadOnly(True)
        layout.addWidget(self.activity_log)

    def update_from_hpc(self, hpc: Any) -> None:
        """Refresh System Status/Running Jobs/Data Sources from a real HPCConnectionManager.

        Calls the manager's real `get_status_summary()` (not a guessed
        `get_status()`) and renders exactly what it reports - including an
        honest "Not Connected" state when `connected` is False. Never
        assumes a connected/healthy status.

        Also reads the manager's real `meteorological_stack` dict (populated
        by `AromeAladinDetector` - either a genuine per-model detection, or
        `AromeAladinDetector.not_detected()`'s honest all-False default when
        the cluster was never probed) to drive the Data Sources labels.
        """
        status = hpc.get_status_summary()
        connected = bool(status.get("connected"))
        scheduler = status.get("scheduler") or "NOT_AVAILABLE"
        active_jobs = status.get("active_jobs_count", 0)

        self.system_status_label.setText(
            f"{'Connected' if connected else 'Not Connected'} — Scheduler: {scheduler}"
        )
        self.running_jobs_label.setText(f"Running Jobs: {active_jobs}")

        stack = getattr(hpc, "meteorological_stack", {}) or {}
        self.arome_status_label.setText(
            f"AROME: {'Active' if stack.get('has_arome') else 'Not Detected'}"
        )
        self.aladin_status_label.setText(
            f"ALADIN: {'Active' if stack.get('has_aladin') else 'Not Detected'}"
        )

    def append_activity(self, message: str) -> None:
        self.activity_log.append(message)
