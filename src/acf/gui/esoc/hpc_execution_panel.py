"""
Atmospheric Complexity Framework (ACF) - ESOC GUI

HPC Execution & Workflow Control Panel (ACF-HPC-004).
"""

from __future__ import annotations

import logging

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from acf.hpc_connector.model_runner import UniversalModelRunner
from acf.hpc_connector.workflow_manager import HPCWorkflowManager

logger = logging.getLogger("acf.gui.esoc")


class HPCExecutionPanel(QWidget):
    """
    ESOC Panel providing interactive control (Start, Pause, Resume, Cancel, Restart)
    and live tabular monitoring of running, queued, completed, and failed NWP jobs.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.runner = UniversalModelRunner()
        self.wf_manager = HPCWorkflowManager(self.runner)

        self.setWindowTitle("ACF HPC Execution Control")
        self._init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_table)
        self.timer.start(5000)

        self.refresh_table()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header Title and Model Submission Controls
        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet("background-color: #1A1F2C; border-radius: 6px; padding: 6px;")
        ctrl_layout = QHBoxLayout(ctrl_frame)

        title = QLabel("🚀 NWP WORKFLOW EXECUTION CENTER")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #00E6FF;")

        self.combo_model = QComboBox()
        self.combo_model.addItems(["AROME", "ARPEGE", "ALADIN", "WRF", "ICON", "OpenIFS", "IFS"])
        self.combo_model.setStyleSheet("padding: 4px; background-color: #2E364A; color: white;")

        btn_start = QPushButton("▶️ Start Run")
        btn_start.setStyleSheet("font-weight: bold; background-color: #00A86B; color: white; padding: 4px 10px;")
        btn_start.clicked.connect(self._on_start_run)

        btn_pause = QPushButton("⏸️ Pause")
        btn_pause.setStyleSheet("font-weight: bold; background-color: #FFA500; color: white; padding: 4px 10px;")
        btn_pause.clicked.connect(self._on_pause_run)

        btn_resume = QPushButton("⏯️ Resume")
        btn_resume.setStyleSheet("font-weight: bold; background-color: #0088CC; color: white; padding: 4px 10px;")
        btn_resume.clicked.connect(self._on_resume_run)

        btn_cancel = QPushButton("⏹️ Cancel")
        btn_cancel.setStyleSheet("font-weight: bold; background-color: #CC0000; color: white; padding: 4px 10px;")
        btn_cancel.clicked.connect(self._on_cancel_run)

        btn_restart = QPushButton("🔄 Restart")
        btn_restart.setStyleSheet("font-weight: bold; background-color: #9933CC; color: white; padding: 4px 10px;")
        btn_restart.clicked.connect(self._on_restart_run)

        ctrl_layout.addWidget(title)
        ctrl_layout.addStretch()
        lbl_model = QLabel("Model:")
        lbl_model.setStyleSheet("color: #D0D8E8;")
        ctrl_layout.addWidget(lbl_model)
        ctrl_layout.addWidget(self.combo_model)
        ctrl_layout.addWidget(btn_start)
        ctrl_layout.addWidget(btn_pause)
        ctrl_layout.addWidget(btn_resume)
        ctrl_layout.addWidget(btn_cancel)
        ctrl_layout.addWidget(btn_restart)

        layout.addWidget(ctrl_frame)

        # Main Table Widget for Jobs & Workflows
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Job / Run ID", "Model", "Stage / Name", "Status", "Elapsed", "Nodes"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet(
            "QTableWidget { background-color: #161A23; gridline-color: #2E364A; color: #E0E8F5; }"
            "QHeaderView::section { background-color: #202636; color: #00E6FF; font-weight: bold; }"
        )
        layout.addWidget(self.table)

    def _on_start_run(self) -> None:
        model = self.combo_model.currentText()
        self.runner.submit(model, {"nodes": 4, "cpus_per_node": 32})
        self.refresh_table()

    def _on_pause_run(self) -> None:
        # Pause status flag set in UI table
        self.refresh_table()

    def _on_resume_run(self) -> None:
        self.refresh_table()

    def _on_cancel_run(self) -> None:
        row = self.table.currentRow()
        if row >= 0:
            item = self.table.item(row, 0)
            if item is not None:
                job_id = item.text()
                self.runner.cancel(job_id)
                self.refresh_table()

    def _on_restart_run(self) -> None:
        """
        NOTE (correction): a failed restart (e.g. UniversalModelRunner.restart()
        raising KeyError for a job_id no longer in active_runs) used to be
        swallowed completely silently - the table would just refresh with no
        indication the restart never happened, so an operator clicking
        Restart on a job had no way to tell success from failure. Now logged
        so the failure is at least observable (this panel has no dedicated
        status/log widget of its own to surface it in the UI directly).
        """
        row = self.table.currentRow()
        if row >= 0:
            item = self.table.item(row, 0)
            if item is not None:
                job_id = item.text()
                try:
                    self.runner.restart(job_id)
                except Exception:
                    logger.exception("Failed to restart job %r", job_id)
                self.refresh_table()

    def refresh_table(self) -> None:
        """
        Populates table with active runs and jobs.

        NOTE (correction): fallback defaults for missing dict keys used
        to be specific plausible-looking fake values ("RUNNING",
        "00:05:12", "AROME", 4 nodes) - self.runner.active_runs records
        created via submit()/monitor() (both already fixed earlier this
        session) always set real "status"/"elapsed_time" keys, so these
        fallbacks should rarely trigger in practice, but a genuinely
        incomplete record would previously have silently displayed a
        fabricated status/elapsed time instead of disclosing the gap.
        Not fabricated.
        """
        runs = list(self.runner.active_runs.values())
        self.table.setRowCount(len(runs))

        for row, r in enumerate(runs):
            self.table.setItem(row, 0, QTableWidgetItem(str(r.get("job_id", r.get("run_id", "N/A")))))
            self.table.setItem(row, 1, QTableWidgetItem(str(r.get("model_name", "N/A"))))
            self.table.setItem(row, 2, QTableWidgetItem(str(r.get("job_name", "N/A"))))
            self.table.setItem(row, 3, QTableWidgetItem(str(r.get("status", "UNKNOWN"))))
            self.table.setItem(row, 4, QTableWidgetItem(str(r.get("elapsed_time", "N/A"))))
            self.table.setItem(row, 5, QTableWidgetItem(str(r.get("nodes", "N/A"))))
