"""
Atmospheric Complexity Framework (ACF) - ESOC GUI

ACF HPC OPERATIONS CENTER Panel (ACF-HPC-003).
"""

from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from acf.hpc_connector.hpc_dashboard import HPCDashboard
from acf.hpc_connector.hpc_monitor import HPCMonitor


class HPCDashboardPanel(QWidget):
    """
    ESOC Panel rendering the ACF HPC Operations Center dashboard.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.dashboard = HPCDashboard(HPCMonitor())

        self.setWindowTitle("ACF HPC Operations Center")
        self._init_ui()

        # Auto-refresh timer every 10 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_dashboard)
        self.timer.start(10000)

        self.refresh_dashboard()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #1A1F2C; border-radius: 6px; padding: 6px;")
        header_layout = QHBoxLayout(header_frame)

        title = QLabel("🖥️ ACF HPC OPERATIONS CENTER")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00E6FF;")

        self.lbl_health_badge = QLabel("HEALTH: OPTIMAL (100%)")
        self.lbl_health_badge.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #00FF66; background-color: #0A2E1C; padding: 4px 8px; border-radius: 4px;"
        )

        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.setStyleSheet(
            "font-weight: bold; background-color: #0088CC; color: white; border-radius: 4px; padding: 4px 10px;"
        )
        btn_refresh.clicked.connect(self.refresh_dashboard)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_health_badge)
        header_layout.addWidget(btn_refresh)

        layout.addWidget(header_frame)

        # Overview Cards Grid
        grid = QGridLayout()
        grid.setSpacing(10)

        # Card 1: Cluster & Scheduler
        card_cluster = self._create_card("Cluster Overview", "#1E2433")
        c_layout = QVBoxLayout(card_cluster)
        self.lbl_cluster_name = QLabel("Cluster Name: Fennec")
        self.lbl_scheduler = QLabel("Scheduler: Slurm v23.02")
        self.lbl_status = QLabel("Status: Operational")
        for lbl in (self.lbl_cluster_name, self.lbl_scheduler, self.lbl_status):
            lbl.setStyleSheet("font-size: 12px; color: #D0D8E8;")
            c_layout.addWidget(lbl)
        grid.addWidget(card_cluster, 0, 0)

        # Card 2: Nodes Breakdown
        card_nodes = self._create_card("Nodes Status", "#1E2433")
        n_layout = QVBoxLayout(card_nodes)
        self.lbl_nodes_tot = QLabel("Total Nodes: --")
        self.lbl_nodes_idle = QLabel("Idle Nodes: --")
        self.lbl_nodes_down = QLabel("Down Nodes: --")
        for lbl in (self.lbl_nodes_tot, self.lbl_nodes_idle, self.lbl_nodes_down):
            lbl.setStyleSheet("font-size: 12px; color: #D0D8E8;")
            n_layout.addWidget(lbl)
        grid.addWidget(card_nodes, 0, 1)

        # Card 3: Jobs Breakdown
        card_jobs = self._create_card("Active Jobs", "#1E2433")
        j_layout = QVBoxLayout(card_jobs)
        self.lbl_jobs_running = QLabel("Running Jobs: --")
        self.lbl_jobs_pending = QLabel("Pending Jobs: --")
        for lbl in (self.lbl_jobs_running, self.lbl_jobs_pending):
            lbl.setStyleSheet("font-size: 12px; color: #D0D8E8;")
            j_layout.addWidget(lbl)
        grid.addWidget(card_jobs, 1, 0)

        # Card 4: Hardware Utilization (CPU / RAM)
        card_hw = self._create_card("Cluster Workload", "#1E2433")
        hw_layout = QVBoxLayout(card_hw)

        lbl_cpu = QLabel("CPU Utilization:")
        lbl_cpu.setStyleSheet("color: #A0B0D0; font-size: 11px;")
        hw_layout.addWidget(lbl_cpu)
        self.bar_cpu = QProgressBar()
        self.bar_cpu.setRange(0, 100)
        self.bar_cpu.setValue(0)
        self.bar_cpu.setStyleSheet("QProgressBar::chunk { background-color: #00E6FF; }")
        hw_layout.addWidget(self.bar_cpu)

        lbl_mem = QLabel("Memory Availability:")
        lbl_mem.setStyleSheet("color: #A0B0D0; font-size: 11px;")
        hw_layout.addWidget(lbl_mem)
        self.bar_mem = QProgressBar()
        self.bar_mem.setRange(0, 100)
        self.bar_mem.setValue(0)
        self.bar_mem.setStyleSheet("QProgressBar::chunk { background-color: #76FF03; }")
        hw_layout.addWidget(self.bar_mem)

        grid.addWidget(card_hw, 1, 1)

        layout.addLayout(grid)
        layout.addStretch()

    def _create_card(self, title_text: str, bg_color: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"background-color: {bg_color}; border-radius: 6px; padding: 8px;")
        t_label = QLabel(title_text)
        t_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #00E6FF; margin-bottom: 4px;")
        c_layout = QVBoxLayout(card)
        c_layout.addWidget(t_label)
        return card

    def refresh_dashboard(self) -> None:
        """Refreshes UI fields from backend HPCDashboard."""
        data = self.dashboard.refresh()

        health = data.get("cluster_health", {})
        score = data.get("health_score", 100.0)

        self.lbl_cluster_name.setText(f"Cluster Name: {health.get('cluster', 'Fennec')}")
        self.lbl_scheduler.setText(f"Scheduler: {health.get('scheduler', 'Slurm').upper()}")

        self.lbl_nodes_tot.setText(f"Total Nodes: {health.get('nodes_total', 0)}")
        self.lbl_nodes_idle.setText(f"Idle Nodes: {health.get('nodes_idle', 0)}")
        self.lbl_nodes_down.setText(f"Down Nodes: {health.get('nodes_down', 0)}")

        self.lbl_jobs_running.setText(f"Running Jobs: {health.get('jobs_running', 0)}")
        self.lbl_jobs_pending.setText(f"Pending Jobs: {health.get('jobs_pending', 0)}")

        cpu_val = int(health.get("cpu_load", 0.0))
        mem_val = int(health.get("memory_available", 0.0))

        self.bar_cpu.setValue(cpu_val)
        self.bar_mem.setValue(mem_val)

        status_text = "OPTIMAL" if score > 80 else "DEGRADED" if score > 50 else "CRITICAL"
        color = "#00FF66" if score > 80 else "#FFCC00" if score > 50 else "#FF3333"
        bg = "#0A2E1C" if score > 80 else "#332B00" if score > 50 else "#330A0A"

        self.lbl_health_badge.setText(f"HEALTH: {status_text} ({score}%)")
        self.lbl_health_badge.setStyleSheet(
            f"font-size: 12px; font-weight: bold; color: {color}; background-color: {bg}; padding: 4px 8px; border-radius: 4px;"
        )
