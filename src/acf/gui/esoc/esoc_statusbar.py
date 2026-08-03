"""ESOC Status Bar displaying real-time operational & hardware metrics (ACF-UI-013)."""

from PySide6.QtWidgets import QStatusBar, QLabel


class ESOCStatusBar(QStatusBar):
    """Status Bar displaying live operational & hardware indicators."""

    def __init__(self) -> None:
        super().__init__()

        self.lbl_utc = QLabel("UTC: 2026-08-03 08:00:00Z")
        self.lbl_sim_time = QLabel("Sim Time: t+006h")
        self.lbl_fcst_hour = QLabel("FCST: +024h")
        self.lbl_hardware = QLabel("CPU: 14% | GPU: 28% | RAM: 18.4GB | Disk: 1.2TB | Threads: 16 | MPI: 128")
        self.lbl_streams = QLabel("Streams: 12 Connected")
        self.lbl_dataset = QLabel("Dataset: ERA5_Global_25km.nc")
        self.lbl_layer = QLabel("Layer: Satellite RGB")
        self.lbl_proj = QLabel("Projection: 2D Mercator")
        self.lbl_workspace = QLabel("Workspace: Meteorologist")

        self.lbl_utc.setStyleSheet("padding: 2px 6px; color: #E0E0E0;")
        self.lbl_sim_time.setStyleSheet("padding: 2px 6px; color: #81D4FA;")
        self.lbl_fcst_hour.setStyleSheet("padding: 2px 6px; color: #FFD54F;")
        self.lbl_hardware.setStyleSheet("padding: 2px 6px; color: #A1887F;")
        self.lbl_streams.setStyleSheet("padding: 2px 6px; color: #81C784;")
        self.lbl_dataset.setStyleSheet("padding: 2px 6px; color: #CE93D8;")
        self.lbl_layer.setStyleSheet("padding: 2px 6px; color: #80DEEA;")
        self.lbl_proj.setStyleSheet("padding: 2px 6px; color: #FFB74D;")
        self.lbl_workspace.setStyleSheet("padding: 2px 6px; font-weight: bold; color: #BA68C8;")

        self.addWidget(self.lbl_utc)
        self.addWidget(self.lbl_sim_time)
        self.addWidget(self.lbl_fcst_hour)
        self.addWidget(self.lbl_hardware)
        self.addWidget(self.lbl_streams)
        self.addWidget(self.lbl_dataset)
        self.addWidget(self.lbl_layer)
        self.addWidget(self.lbl_proj)
        self.addPermanentWidget(self.lbl_workspace)

    def update_metrics(
        self,
        utc_str: str = None,
        sim_time: str = None,
        fcst_hour: str = None,
        cpu_pct: float = 14.0,
        gpu_pct: float = 28.0,
        workspace_mode: str = "Meteorologist",
        selected_layer: str = None,
        projection: str = None,
    ) -> None:
        """Update status bar indicators."""
        if utc_str:
            self.lbl_utc.setText(f"UTC: {utc_str}")
        if sim_time:
            self.lbl_sim_time.setText(f"Sim Time: {sim_time}")
        if fcst_hour:
            self.lbl_fcst_hour.setText(f"FCST: {fcst_hour}")
        if selected_layer:
            self.lbl_layer.setText(f"Layer: {selected_layer}")
        if projection:
            self.lbl_proj.setText(f"Projection: {projection}")

        self.lbl_hardware.setText(
            f"CPU: {cpu_pct:.0f}% | GPU: {gpu_pct:.0f}% | RAM: 18.4GB | Disk: 1.2TB | Threads: 16 | MPI: 128"
        )
        self.lbl_workspace.setText(f"Workspace: {workspace_mode}")
