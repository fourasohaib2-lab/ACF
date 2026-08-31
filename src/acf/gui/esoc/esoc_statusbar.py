"""ESOC Status Bar displaying real-time operational & HPC cluster metrics (ACF-HPC-001)."""

from PySide6.QtWidgets import QLabel, QStatusBar


class ESOCStatusBar(QStatusBar):
    """Status Bar displaying live operational & HPC hardware indicators."""

    def __init__(self) -> None:
        super().__init__()

        # NOTE (correction — persistently visible fabrication): every
        # label below used to start (and, for hpc_status/hardware,
        # silently reset back to on every update_metrics() call - see
        # its own NOTE) at a fixed "Connected"/"14%/28%"/"12
        # Connected"/a specific dataset filename, with no real cluster,
        # sensor, stream, or dataset ever behind any of it. Unlike the
        # dock panels (see panel_manager.py's NOTE), this status bar is
        # visible at all times regardless of which panel is open,
        # making it the single most persistently-shown fabrication
        # found this session. Not fabricated.
        self._cpu_pct: float | None = None
        self._gpu_pct: float | None = None
        self._ram_gb: float | None = None
        self._disk_tb: float | None = None
        self._mpi_ranks: int | None = None

        self.lbl_hpc_status = QLabel("HPC: Not Connected")
        self.lbl_utc = QLabel("UTC: 2026-08-03 08:00:00Z")
        self.lbl_sim_time = QLabel("Sim Time: t+006h")
        self.lbl_fcst_hour = QLabel("FCST: +024h")
        self.lbl_hardware = QLabel(self._format_hardware_label())
        self.lbl_streams = QLabel("Streams: 0 Connected")
        self.lbl_dataset = QLabel("Dataset: None loaded")
        self.lbl_layer = QLabel("Layer: Satellite RGB")
        self.lbl_proj = QLabel("Projection: 2D Mercator")
        self.lbl_workspace = QLabel("Workspace: Meteorologist")

        self.lbl_hpc_status.setStyleSheet("padding: 2px 6px; font-weight: bold; color: #76FF03;")
        self.lbl_utc.setStyleSheet("padding: 2px 6px; color: #E0E0E0;")
        self.lbl_sim_time.setStyleSheet("padding: 2px 6px; color: #81D4FA;")
        self.lbl_fcst_hour.setStyleSheet("padding: 2px 6px; color: #FFD54F;")
        self.lbl_hardware.setStyleSheet("padding: 2px 6px; color: #A1887F;")
        self.lbl_streams.setStyleSheet("padding: 2px 6px; color: #81C784;")
        self.lbl_dataset.setStyleSheet("padding: 2px 6px; color: #CE93D8;")
        self.lbl_layer.setStyleSheet("padding: 2px 6px; color: #80DEEA;")
        self.lbl_proj.setStyleSheet("padding: 2px 6px; color: #FFB74D;")
        self.lbl_workspace.setStyleSheet("padding: 2px 6px; font-weight: bold; color: #BA68C8;")

        self.addWidget(self.lbl_hpc_status)
        self.addWidget(self.lbl_utc)
        self.addWidget(self.lbl_sim_time)
        self.addWidget(self.lbl_fcst_hour)
        self.addWidget(self.lbl_hardware)
        self.addWidget(self.lbl_streams)
        self.addWidget(self.lbl_dataset)
        self.addWidget(self.lbl_layer)
        self.addWidget(self.lbl_proj)
        self.addPermanentWidget(self.lbl_workspace)

    def _format_hardware_label(self) -> str:
        """Build the hardware label from currently known fields, showing N/A for anything never reported."""
        cpu = f"{self._cpu_pct:.0f}%" if self._cpu_pct is not None else "N/A"
        gpu = f"{self._gpu_pct:.0f}% (A100)" if self._gpu_pct is not None else "N/A"
        ram = f"{self._ram_gb:.1f}GB" if self._ram_gb is not None else "N/A"
        disk = f"{self._disk_tb:.1f}TB" if self._disk_tb is not None else "N/A"
        mpi = str(self._mpi_ranks) if self._mpi_ranks is not None else "N/A"
        return f"CPU: {cpu} | GPU: {gpu} | RAM: {ram} | Disk: {disk} | MPI: {mpi}"

    def update_metrics(
        self,
        utc_str: str | None = None,
        sim_time: str | None = None,
        fcst_hour: str | None = None,
        cpu_pct: float | None = None,
        gpu_pct: float | None = None,
        workspace_mode: str = "Meteorologist",
        selected_layer: str | None = None,
        projection: str | None = None,
        hpc_connected: bool | None = None,
        ram_gb: float | None = None,
        disk_tb: float | None = None,
        mpi_ranks: int | None = None,
        streams_connected: int | None = None,
        dataset_name: str | None = None,
    ) -> None:
        """
        Update status bar indicators.

        NOTE (correction): cpu_pct/gpu_pct/hpc_connected used to default
        to fixed fake values (14.0/28.0/True) that got silently
        re-applied on EVERY call - including calls that only wanted to
        change sim_time or workspace_mode (see esoc_window.py's real
        call sites, neither of which ever passes these) - meaning the
        status bar reset itself back to "HPC: Connected (Slurm)" and
        fake hardware numbers on every workspace switch or simulation
        step. RAM/Disk/MPI were pure hardcoded literals with no
        parameter at all. All of these now default to None (leave
        unchanged) and are only applied when a real caller actually
        supplies them; ram_gb/disk_tb/mpi_ranks/streams_connected/
        dataset_name are new optional parameters so a real backend can
        wire them in later without any further signature change. Not
        fabricated.
        """
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

        if hpc_connected is not None:
            conn_str = "Connected (Slurm)" if hpc_connected else "Not Connected"
            self.lbl_hpc_status.setText(f"HPC: {conn_str}")

        hardware_changed = False
        for attr, value in (
            ("_cpu_pct", cpu_pct),
            ("_gpu_pct", gpu_pct),
            ("_ram_gb", ram_gb),
            ("_disk_tb", disk_tb),
            ("_mpi_ranks", mpi_ranks),
        ):
            if value is not None:
                setattr(self, attr, value)
                hardware_changed = True
        if hardware_changed:
            self.lbl_hardware.setText(self._format_hardware_label())

        if streams_connected is not None:
            self.lbl_streams.setText(f"Streams: {streams_connected} Connected")
        if dataset_name:
            self.lbl_dataset.setText(f"Dataset: {dataset_name}")

        self.lbl_workspace.setText(f"Workspace: {workspace_mode}")
