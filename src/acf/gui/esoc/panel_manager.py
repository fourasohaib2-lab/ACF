"""Panel Manager instantiating 28 operational PySide6 dock panels for ESOC (ACF-HPC-001)."""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.hpc_terminal_panel import HPCTerminalPanel
from acf.gui.esoc.module_registry import ModuleRegistry


def _not_connected_label(key: str) -> QLabel:
    """Real, honest disclosure (added 2026-09-04, building the 7
    previously-empty System Explorer categories - Catalog/Products/
    Reports/Output/Plugins/Geoengineering/Machine Learning) for when
    `ModuleRegistry.get_module(key)` genuinely returns `None` (the
    real class failed to import/construct - see `ModuleRegistry`'s own
    `_safe_import_register()`) - never silently shown as if real data
    were available, matching this file's own established "not
    fabricated" discipline for every panel above."""
    lbl = QLabel(f"⚠ Real subsystem '{key}' is not connected (see ESOC's own status line/logs for why).")
    lbl.setStyleSheet("color: #FF7043; font-size: 11px; font-style: italic;")
    return lbl


def _example_layout_disclaimer() -> QLabel:
    """
    Shared disclaimer label used across panels below that show
    illustrative example values in their tables/text blocks rather
    than live telemetry - see the NOTE (correction) at each call site
    for what each panel used to claim.
    """
    lbl = QLabel("⚠ Example layout — not wired to a live data source yet")
    lbl.setStyleSheet("color: #FF7043; font-size: 10px; font-style: italic;")
    return lbl


class BasePanelWidget(QWidget):
    """Generic base class for operational panels."""

    def __init__(
        self,
        title_text: str,
        color_hex: str,
        registry: ModuleRegistry,
        dispatcher: CommandDispatcher,
    ) -> None:
        super().__init__()
        self.registry = registry
        self.dispatcher = dispatcher

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)

        title = QLabel(title_text)
        title.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {color_hex};")
        self.main_layout.addWidget(title)


class HPCDashboardPanel(BasePanelWidget):
    """1. HPC Master Dashboard Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("⚡ HPC MASTER CONTROL DASHBOARD", "#90A4AE", registry, dispatcher)

        h_btn = QHBoxLayout()
        btn_conn = QPushButton("🔌 Connect HPC Cluster")
        btn_dis = QPushButton("❌ Disconnect")
        btn_conn.clicked.connect(lambda: self.dispatcher.dispatch("connect_hpc"))
        btn_dis.clicked.connect(lambda: self.dispatcher.dispatch("disconnect_hpc"))
        h_btn.addWidget(btn_conn)
        h_btn.addWidget(btn_dis)
        self.main_layout.addLayout(h_btn)

        # NOTE (correction): this text block used to be labeled "Cluster
        # Live Operational Status" and show specific fixed numbers (4
        # running jobs, 64 nodes, InfiniBand HDR 200 Gbps...) at widget
        # construction time, with no connection to any real cluster -
        # self.registry/self.dispatcher (available here) were never
        # consulted. An operator glancing at this dashboard could
        # believe a real cluster with real running jobs was connected
        # when the "Connect HPC Cluster" button above had never even
        # been clicked. Not fabricated.
        self.main_layout.addWidget(_example_layout_disclaimer())
        self.txt_status = QTextEdit()
        self.txt_status.setReadOnly(True)
        self.txt_status.setText(
            "Example Layout (values below are illustrative, not live):\n"
            "• Connected Host: login01.hpc.university.edu\n"
            "• Scheduler: Slurm 23.02 (Active)\n"
            "• Execution Mode: Hybrid (Workstation + Supercomputer)\n"
            "• Active Jobs: 4 Running, 0 Queued\n"
            "• Total Compute Nodes: 64 Nodes (2048 Cores)\n"
            "• GPU Accelerator Nodes: 16 NVIDIA A100 Nodes (64 GPUs)\n"
            "• MPI Domain Ranks: 128 Active Processes\n"
            "• Interconnect: InfiniBand HDR 200 Gbps"
        )
        self.main_layout.addWidget(self.txt_status)


class ClusterExplorerPanel(BasePanelWidget):
    """2. HPC Cluster Topology Explorer Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🌐 HPC CLUSTER TOPOLOGY & PARTITIONS", "#81D4FA", registry, dispatcher)
        # NOTE (correction): this table used to show 4 fixed partitions
        # all marked "ONLINE" with no connection to any real cluster
        # topology query. Not fabricated.
        self.main_layout.addWidget(_example_layout_disclaimer())
        self.table = QTableWidget(4, 4)
        self.table.setHorizontalHeaderLabels(["Partition", "Nodes", "GPUs/Node", "Status"])
        data = [
            ("gpu", "16", "4 (A100)", "EXAMPLE"),
            ("compute", "32", "0", "EXAMPLE"),
            ("highmem", "8", "0", "EXAMPLE"),
            ("debug", "8", "2 (A100)", "EXAMPLE"),
        ]
        for row, (p, n, g, st) in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(p))
            self.table.setItem(row, 1, QTableWidgetItem(n))
            self.table.setItem(row, 2, QTableWidgetItem(g))
            self.table.setItem(row, 3, QTableWidgetItem(st))
        self.main_layout.addWidget(self.table)


class JobExplorerPanel(BasePanelWidget):
    """3. HPC Job Lifecycle Explorer Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("📋 HPC JOB LIFECYCLE EXPLORER", "#FFD54F", registry, dispatcher)

        h_btn = QHBoxLayout()
        btn_sub = QPushButton("🚀 Submit Job")
        btn_can = QPushButton("⏹ Cancel Job")
        btn_sub.clicked.connect(lambda: self.dispatcher.dispatch("submit_hpc_job"))
        btn_can.clicked.connect(lambda: self.dispatcher.dispatch("cancel_hpc_job"))
        h_btn.addWidget(btn_sub)
        h_btn.addWidget(btn_can)
        self.main_layout.addLayout(h_btn)

        # NOTE (correction): this table used to show 3 fixed jobs
        # ("slurm_1024" etc.) marked RUNNING/COMPLETED with no
        # connection to JobManager.list_jobs() (the real, already-honest
        # job registry - see hpc_connector/job_manager.py) despite
        # self.registry being available to reach it. Not fabricated.
        self.main_layout.addWidget(_example_layout_disclaimer())
        self.table = QTableWidget(3, 4)
        self.table.setHorizontalHeaderLabels(["Job ID", "Job Name", "Nodes/MPI", "Status"])
        jobs = [
            ("slurm_1024", "acf_coupled_sim", "4 / 128", "EXAMPLE"),
            ("slurm_1025", "acf_fno_surrogate", "1 / 4 GPU", "EXAMPLE"),
            ("slurm_1026", "acf_4dvar_cycle", "2 / 64", "EXAMPLE"),
        ]
        for row, (jid, name, n_mpi, st) in enumerate(jobs):
            self.table.setItem(row, 0, QTableWidgetItem(jid))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(n_mpi))
            self.table.setItem(row, 3, QTableWidgetItem(st))
        self.main_layout.addWidget(self.table)


class GPUMonitorPanel(BasePanelWidget):
    """4. NVIDIA/AMD GPU Hardware Monitor Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🎮 GPU ACCELERATION MONITOR (CUDA / ROCm)", "#76FF03", registry, dispatcher)
        # NOTE (correction): text used to be labeled "...Live Status"
        # with fixed load/temperature/power numbers, no nvidia-smi or
        # equivalent probe ever run. Not fabricated.
        self.main_layout.addWidget(_example_layout_disclaimer())
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText(
            "NVIDIA A100-SXM4-80GB Example Layout (not live):\n"
            "• GPU Core Load: 28%\n"
            "• VRAM Usage: 18.4 / 80.0 GB (HBM2e)\n"
            "• CUDA Core Compute: 19.5 TFLOPS\n"
            "• Temperature: 52°C\n"
            "• Power Usage: 240 W / 400 W Max"
        )
        self.main_layout.addWidget(self.txt)


class StorageMonitorPanel(BasePanelWidget):
    """5. HPC High-Performance Filesystem & Scratch Monitor."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("💾 HPC STORAGE & SCRATCH MONITOR", "#FF8A65", registry, dispatcher)
        # NOTE (correction): text used to be labeled "...Telemetry" with
        # fixed usage numbers and "Automated Sync: Active", no df/du
        # or sync process of any kind ever run. Not fabricated.
        self.main_layout.addWidget(_example_layout_disclaimer())
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText(
            "GPFS Parallel Storage Example Layout (not live):\n"
            "• Scratch Dir: /scratch/users/acf (450 GB / 10 TB)\n"
            "• Inundation Datasets: NetCDF4 / Zarr Stores\n"
            "• Checkpoints Saved: Step 360 (12.4 GB)\n"
            "• Automated Sync: Not Configured"
        )
        self.main_layout.addWidget(self.txt)
        btn_sync = QPushButton("🔄 Sync Local <-> HPC Storage")
        btn_sync.clicked.connect(lambda: self.dispatcher.dispatch("sync_hpc_storage"))
        self.main_layout.addWidget(btn_sync)


class BenchmarkPanel(BasePanelWidget):
    """6. Automated HPC Performance Benchmark Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("📊 BENCHMARK & PERFORMANCE SUITE", "#CE93D8", registry, dispatcher)
        btn_bench = QPushButton("⚡ Execute Full HPC Benchmark")
        btn_bench.clicked.connect(lambda: self.dispatcher.dispatch("benchmark_hpc"))
        self.main_layout.addWidget(btn_bench)
        # NOTE (correction): used to unconditionally show fixed
        # "CPU GFLOPS: 450.0 | GPU TFLOPS: 19.5..." results as if a
        # benchmark had already run - see
        # HPCConnectionManager.benchmark_performance()'s own NOTE
        # (correction), the same fabrication independently duplicated
        # here. Not fabricated.
        self.txt_bench = QTextEdit()
        self.txt_bench.setReadOnly(True)
        self.txt_bench.setText("Benchmark Status: Not run yet. Click 'Execute Full HPC Benchmark' above.")
        self.main_layout.addWidget(self.txt_bench)


class PlanetaryDashboardPanel(BasePanelWidget):
    """7. Planetary Health Score & 9 Planetary Boundaries Dashboard."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🌍 PLANETARY DASHBOARD & HEALTH SCORE", "#4FC3F7", registry, dispatcher)

        # NOTE (correction): this panel used to independently hardcode
        # a fake "68.4/100" health index and a 9-row boundaries table
        # with fixed "TRANSCENDED"/"SAFE ZONE" verdicts - the exact same
        # fabrication already found and fixed in
        # digital_twin.planetary_dashboard.PlanetaryDashboard.get_dashboard_summary()
        # and digital_twin.planetary_limits.planetary_boundaries.PlanetaryBoundariesSimulator
        # (both fixed earlier this session to honestly disclose no real
        # observation data is connected), duplicated here independently
        # in the GUI layer with no call into either honest class. Not
        # fabricated.
        self.main_layout.addWidget(_example_layout_disclaimer())
        lbl_score = QLabel("Planetary Health Index: Not Available (no observation tracker connected)")
        lbl_score.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFB74D; padding: 4px;")
        self.main_layout.addWidget(lbl_score)

        self.table = QTableWidget(9, 3)
        self.table.setHorizontalHeaderLabels(["Planetary Boundary", "Status", "Control Variable"])
        boundaries = [
            ("1. Climate Change", "EXAMPLE", "422 ppm CO2 (+1.25°C)"),
            ("2. Biosphere Integrity", "EXAMPLE", "E/MSY > 100"),
            ("3. Land-System Change", "EXAMPLE", "60% Forest Cover Remaining"),
            ("4. Freshwater Change", "EXAMPLE", "Blue & Green Water Deficit"),
            ("5. Biogeochemical (N & P)", "EXAMPLE", "P=22 Tg/yr, N=150 Tg/yr"),
            ("6. Ocean Acidification", "EXAMPLE", "Aragonite Saturation 2.90"),
            ("7. Atmospheric Aerosols", "EXAMPLE", "AOD = 0.12 Global Mean"),
            ("8. Stratospheric Ozone", "EXAMPLE", "285 Dobson Units"),
            ("9. Novel Entities", "EXAMPLE", "Synthetic Chemical Flux"),
        ]
        for row, (b_name, st, val) in enumerate(boundaries):
            self.table.setItem(row, 0, QTableWidgetItem(b_name))
            self.table.setItem(row, 1, QTableWidgetItem(st))
            self.table.setItem(row, 2, QTableWidgetItem(val))
        self.main_layout.addWidget(self.table)


class DataAssimilationPanel(BasePanelWidget):
    """8. Live Data Assimilation Telemetry Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🔄 DATA ASSIMILATION & OBSERVATION TELEMETRY", "#AED581", registry, dispatcher)

        # NOTE (correction): text used to be labeled "Live Data
        # Assimilation Metrics" with fixed observation counts and a
        # fixed "-18.4% RMSE improvement" - the real 4D-Var/EnKF/hybrid
        # algorithms this describes honestly raise NotImplementedError
        # rather than fabricate convergence (see
        # data_assimilation/assimilation/*, fixed earlier this
        # session). Not fabricated.
        self.main_layout.addWidget(_example_layout_disclaimer())
        self.txt_da = QTextEdit()
        self.txt_da.setReadOnly(True)
        self.txt_da.setText(
            "Data Assimilation Example Layout (not live):\n"
            "• Operational Schemes: Incremental 4D-Var / EnKF (50 Members) / Hybrid 4DEnVar\n"
            "• Active Feeds: Satellites, Radar Mosaic, SYNOP, ARGO, Aircraft (AMDAR), GNSS-RO, Lightning\n"
            "• Total Observations Ingested: 1,420,500 obs/cycle\n"
            "• Rejected Observations (QC): 1,704 (0.12% Filtered)\n"
            "• Innovation Statistics (O-B): Mean = 0.02 K, StdDev = 0.48 K\n"
            "• Analysis RMSE Improvement: -18.4% vs Background\n"
            "• Variational Cost Function: J(x) converged in 12 iterations"
        )
        self.main_layout.addWidget(self.txt_da)

        btn = QPushButton("⚡ Execute Incremental 4D-Var Cycle")
        btn.clicked.connect(lambda: self.dispatcher.dispatch("run_assimilation"))
        self.main_layout.addWidget(btn)


class EarthMonitoringPanel(BasePanelWidget):
    """9. Live Earth Monitoring Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("📡 EARTH OBSERVATION & MONITORING CENTER", "#4FC3F7", registry, dispatcher)
        # NOTE (correction): group box used to be labeled "Live
        # Observation Feeds" with every source marked ACTIVE/STREAMING/
        # SYNCED and specific latency figures, with no real feed
        # connection of any kind. Not fabricated.
        self.main_layout.addWidget(_example_layout_disclaimer())
        group = QGroupBox("Observation Feeds (Example Layout)")
        g_layout = QVBoxLayout(group)
        self.table = QTableWidget(6, 3)
        self.table.setHorizontalHeaderLabels(["Data Source", "Status", "Latency"])
        sources = [
            ("GOES/MTG Satellites", "EXAMPLE", "1.2 min"),
            ("Doppler Radar (NEXRAD)", "EXAMPLE", "0.5 min"),
            ("Surface AWS (SYNOP/METAR)", "EXAMPLE", "0.1 min"),
            ("ARGO Ocean Floats", "EXAMPLE", "12.0 min"),
            ("AMDAR Aircraft", "EXAMPLE", "0.8 min"),
            ("Lightning Network", "EXAMPLE", "0.05 min"),
        ]
        for row, (src, st, lat) in enumerate(sources):
            self.table.setItem(row, 0, QTableWidgetItem(src))
            self.table.setItem(row, 1, QTableWidgetItem(st))
            self.table.setItem(row, 2, QTableWidgetItem(lat))
        g_layout.addWidget(self.table)
        self.main_layout.addWidget(group)
        btn = QPushButton("🔄 Refresh Ingestion Streams")
        btn.clicked.connect(lambda: self.dispatcher.dispatch("refresh_observations"))
        self.main_layout.addWidget(btn)


class EarthPhysicsPanel(BasePanelWidget):
    """10. Earth System Physics Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("⚛️ EARTH SYSTEM PHYSICS & CONTINUUM MECHANICS", "#81C784", registry, dispatcher)
        self.info = QTextEdit()
        self.info.setReadOnly(True)
        self.info.setText(
            "Physical Laws & Equations:\n"
            "• Mass Conservation: d(rho)/dt + div(rho*U) = 0\n"
            "• Navier-Stokes: DU/Dt = -1/rho * grad(p) - f x U\n"
            "• Thermodynamics: Cp * DT/Dt = omega/rho + Q_rad + Q_latent\n"
            "• Ocean Seawater EOS: rho = rho0 * [1 - alpha*(T-T0) + beta*(S-S0)]"
        )
        self.main_layout.addWidget(self.info)


class ForecastPanel(BasePanelWidget):
    """11. Weather Forecast Matrix Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🔮 GLOBAL & REGIONAL NWP FORECAST MATRIX", "#FFD54F", registry, dispatcher)
        btn = QPushButton("🚀 Generate 15-Day Global NWP Forecast")
        btn.clicked.connect(lambda: self.dispatcher.dispatch("run_simulation"))
        self.main_layout.addWidget(btn)


class SimulationPanel(BasePanelWidget):
    """12. Simulation Control Center & Run Manager."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🚀 SIMULATION CONTROL CENTER & RUN MANAGER", "#FFB74D", registry, dispatcher)

        h_ctrl = QHBoxLayout()
        self.btn_run = QPushButton("▶ Run")
        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_resume = QPushButton("⏯ Resume")
        self.btn_stop = QPushButton("⏹ Stop")
        self.btn_restart = QPushButton("🔄 Restart")

        self.btn_run.clicked.connect(lambda: self.dispatcher.dispatch("run_simulation"))
        self.btn_pause.clicked.connect(lambda: self.dispatcher.dispatch("pause_simulation"))
        self.btn_resume.clicked.connect(lambda: self.dispatcher.dispatch("run_simulation"))
        self.btn_stop.clicked.connect(lambda: self.dispatcher.dispatch("stop_simulation"))
        self.btn_restart.clicked.connect(lambda: self.dispatcher.dispatch("run_simulation"))

        h_ctrl.addWidget(self.btn_run)
        h_ctrl.addWidget(self.btn_pause)
        h_ctrl.addWidget(self.btn_resume)
        h_ctrl.addWidget(self.btn_stop)
        h_ctrl.addWidget(self.btn_restart)
        self.main_layout.addLayout(h_ctrl)

        group_cfg = QGroupBox("Model Schemes & Resolution Parameters")
        cfg_layout = QVBoxLayout(group_cfg)

        h_par1 = QHBoxLayout()
        h_par1.addWidget(QLabel("Physics Scheme:"))
        self.combo_physics = QComboBox()
        self.combo_physics.addItems(
            ["Primitive Equations Core", "Non-Hydrostatic Finite Volume", "Spherical Spectral Wave Solver"]
        )
        h_par1.addWidget(self.combo_physics)

        h_par1.addWidget(QLabel("Microphysics:"))
        self.combo_micro = QComboBox()
        self.combo_micro.addItems(["6-Species Double Moment", "Kessler Bulk Scheme", "Morrison 2-Moment"])
        h_par1.addWidget(self.combo_micro)
        cfg_layout.addLayout(h_par1)

        h_par2 = QHBoxLayout()
        h_par2.addWidget(QLabel("Convection:"))
        self.combo_conv = QComboBox()
        self.combo_conv.addItems(["Kain-Fritsch Scheme", "Tiedtke Mass-Flux", "Grell-Freitas Scheme"])
        h_par2.addWidget(self.combo_conv)

        h_par2.addWidget(QLabel("Resolution:"))
        self.combo_res = QComboBox()
        self.combo_res.addItems(["Global 25km", "Global 9km", "Regional 3km", "Convective 1km"])
        h_par2.addWidget(self.combo_res)
        cfg_layout.addLayout(h_par2)

        self.main_layout.addWidget(group_cfg)

        # NOTE (correction): progress bar/ETA used to be fixed at
        # 45%/"4 mins 12 secs" from widget construction, before any run
        # was ever started via the ▶ Run button above - an operator
        # could believe a simulation was already 45% underway. Not
        # fabricated.
        self.main_layout.addWidget(QLabel("Time Integration Progress:"))
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.main_layout.addWidget(self.progress)
        self.lbl_eta = QLabel("Estimated Completion Time (ETA): Not running")
        self.lbl_eta.setStyleSheet("color: #B0BEC5; font-size: 11px;")
        self.main_layout.addWidget(self.lbl_eta)


class DigitalTwinPanel(BasePanelWidget):
    """13. Digital Twin Center & Planetary Scenarios."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🌐 EARTH DIGITAL TWIN CENTER & PLANETARY LIMITS", "#BA68C8", registry, dispatcher)
        self.combo = QComboBox()
        self.combo.addItems(
            [
                "Present Earth Digital Twin (t=0)",
                "Historical Replay (1950 - Present)",
                "2030 Near-Term Digital Twin",
                "2050 Mid-Century Horizon",
                "2100 Far-Horizon Climate Target",
                "2300 Multi-Century Projection",
                "Net Zero Emission Pathway",
                "Geoengineering SRM Sandbox",
                "9 Planetary Boundaries Audit",
                "CMIP6 SSP1-1.9 (1.5°C Paris)",
                "CMIP6 SSP2-4.5 (Intermediate)",
                "CMIP6 SSP5-8.5 (Fossil-Fueled)",
            ]
        )
        self.main_layout.addWidget(self.combo)

        btn_load = QPushButton("🔮 Load Digital Twin Scenario")
        btn_load.clicked.connect(
            lambda: self.dispatcher.dispatch("load_digital_twin", scenario=self.combo.currentText())
        )
        self.main_layout.addWidget(btn_load)

        self.main_layout.addWidget(QLabel("Interactive Time Slider (1950 - 2100):"))
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(1950, 2100)
        self.slider.setValue(2026)
        self.main_layout.addWidget(self.slider)


class AIForecastPanel(BasePanelWidget):
    """14. AI Operations Center."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🧠 AI OPERATIONS CENTER (PINN / GNN / FNO)", "#4DD0E1", registry, dispatcher)

        # NOTE (correction): used to claim "Automatic Calibration:
        # Active" and a fixed "94.6% Confidence Interval" with no
        # calibration or uncertainty computation ever run for any
        # actual forecast. Not fabricated.
        #
        # NOTE (correction, later this session): "1000x Speedup (design
        # target)" on the FNO line, and the button below's "(1000x)"
        # suffix, both traced back to NeuralOperatorEngine.
        # acceleration_factor - a fabricated "1000.0" constant, never
        # benchmarked against anything (see that class's own NOTE),
        # since fixed to None. A real, trained (if narrowly-scoped -
        # surface temperature only) FNO surrogate now exists
        # (acf.ai.simulation.fno_model/fno_training) and is what the
        # button below actually runs, via ESOCController.
        # handle_run_ai_forecast()'s "surface_temperature_surrogate"
        # result - removed the unbenchmarked speedup claim rather than
        # attach it to the real model too.
        self.main_layout.addWidget(_example_layout_disclaimer())
        self.txt_ai_info = QTextEdit()
        self.txt_ai_info.setReadOnly(True)
        self.txt_ai_info.setText(
            "AI Neural Operators & Models (capabilities, not live status):\n"
            "• Fourier Neural Operator (FNO): real trained surrogate for surface\n"
            "  temperature (see AI Forecast result below); no benchmarked speedup\n"
            "• Graph Neural Network (GNN): Multi-mesh global forecast\n"
            "• PINN Surrogate: Physics-informed mass/momentum correction\n"
            "• Automatic Calibration: Not run\n"
            "• Uncertainty Evaluation: Not run"
        )
        self.main_layout.addWidget(self.txt_ai_info)

        btn_fno = QPushButton("⚡ Execute AI Forecast (trained FNO surrogate)")
        btn_fno.clicked.connect(lambda: self.dispatcher.dispatch("run_ai_forecast"))
        self.main_layout.addWidget(btn_fno)


class HazardsPanel(BasePanelWidget):
    """15. Hazard Operations Center & Civil Protection."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("⚠️ HAZARD OPERATIONS CENTER & EMERGENCY RESPONSE", "#E57373", registry, dispatcher)

        # NOTE (correction — operationally dangerous): this panel is
        # titled "HAZARD OPERATIONS CENTER & EMERGENCY RESPONSE" and
        # used to unconditionally display "Active Hazard Threats"
        # naming a specific fake Category 3 hurricane, flash flood,
        # wildfire, heatwave, and air pollution alert - the exact same
        # fabrication already found and fixed in
        # hazard_operations.hazard_detection_engine.HazardDetectionEngine.detect_all_hazards()
        # (see its own NOTE - "one of the most operationally dangerous
        # findings this session"), duplicated here independently in the
        # GUI layer with no call into that now-honest class. An
        # operator opening this panel on a quiet day would see 5
        # simultaneous fabricated active disasters. Not fabricated.
        self.main_layout.addWidget(_example_layout_disclaimer())
        self.txt_threats = QTextEdit()
        self.txt_threats.setReadOnly(True)
        self.txt_threats.setText(
            "No active hazard scan connected. Click 'Trigger Emergency Hazard Assessment' below.\n"
            "Example layout only (values below are illustrative, not real threats):\n"
            "• Tropical Cyclone: Cat 3 Hurricane Track (Caribbean)\n"
            "• Flash Flood: Inundation Depth 0.85m (Mississippi Basin)\n"
            "• Wildfire: Rothermel Spread Rate 4.2 m/min (California)\n"
            "• Heatwave: Temp Anomaly +6.2°C (Southern Europe)\n"
            "• Air Pollution: PM2.5 Alert (East Asia)"
        )
        self.main_layout.addWidget(self.txt_threats)

        btn = QPushButton("🚨 Trigger Emergency Hazard Assessment")
        btn.clicked.connect(lambda: self.dispatcher.dispatch("assess_hazards"))
        self.main_layout.addWidget(btn)


class ClimatePanel(BasePanelWidget):
    """16. Climate Scenarios Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🌡️ CLIMATE SCENARIOS (CMIP6 / SSP)", "#FF8A65", registry, dispatcher)
        btn = QPushButton("📈 Project SSP Horizon Trajectory")
        btn.clicked.connect(lambda: self.dispatcher.dispatch("run_climate_projection"))
        self.main_layout.addWidget(btn)


class OceanPanel(BasePanelWidget):
    """17. Oceanography Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🌊 3D OCEAN DYNAMICS & WAVE SPECTRA", "#0288D1", registry, dispatcher)
        # NOTE (correction): fixed AMOC/wave numbers shown with no real
        # ocean model or observation connected. Not fabricated.
        self.main_layout.addWidget(_example_layout_disclaimer())
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText(
            "Ocean Hydrodynamics (Example Layout):\n• AMOC Strength: 18.2 Sverdrups\n• Peak Wave Period (Tp): 11.4 s\n• Significant Wave Height (Hs): 3.2 m"
        )
        self.main_layout.addWidget(self.txt)


class HydrologyPanel(BasePanelWidget):
    """18. Hydrology & Inundation Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("💧 HYDROLOGY & FLASH FLOOD INUNDATION", "#0097A7", registry, dispatcher)
        # NOTE (correction): fixed runoff/inundation numbers shown with
        # no real hydrological model or observation connected. Not
        # fabricated.
        self.main_layout.addWidget(_example_layout_disclaimer())
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText(
            "Hydrological Runoff (Example Layout):\n• Soil Moisture Saturation: 84%\n• River Basin Runoff Q: 1240 m^3/s\n• Max Inundation Depth: 0.85 m"
        )
        self.main_layout.addWidget(self.txt)


class CryospherePanel(BasePanelWidget):
    """19. Cryosphere Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("❄️ CRYOSPHERE & POLAR SEA-ICE MONITOR", "#80DEEA", registry, dispatcher)
        # NOTE (correction): fixed ice extent/thickness numbers shown
        # with no real satellite or model observation connected. Not
        # fabricated.
        self.main_layout.addWidget(_example_layout_disclaimer())
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText(
            "Polar Sea Ice (Example Layout):\n• Arctic Ice Extent: 4.2 million km^2\n• Ice Thickness: 1.8 m\n• Permafrost Thaw Rate: 2.1 cm/yr"
        )
        self.main_layout.addWidget(self.txt)


class AirQualityPanel(BasePanelWidget):
    """20. Air Quality & Chemistry Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🌫️ AIR QUALITY & ATMOSPHERIC CHEMISTRY", "#CE93D8", registry, dispatcher)
        # NOTE (correction): fixed AQI numbers shown with no real
        # sensor network or chemistry model connected. Not fabricated.
        self.main_layout.addWidget(_example_layout_disclaimer())
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText(
            "Air Quality Index (Example Layout):\n• PM2.5: 18 ug/m^3 (Good)\n• Ozone O3: 42 ppb\n• NO2 Column: 1.2e15 molec/cm^2"
        )
        self.main_layout.addWidget(self.txt)


class CarbonPanel(BasePanelWidget):
    """21. Terrestrial & Ocean Carbon Cycle Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🌱 CARBON CYCLE & NET ECOSYSTEM EXCHANGE (NEE)", "#A5D6A7", registry, dispatcher)
        # NOTE (correction): fixed GPP/NEE numbers shown with no real
        # carbon-cycle model or observation connected. Not fabricated.
        self.main_layout.addWidget(_example_layout_disclaimer())
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText(
            "Carbon Flux Balance (Example Layout):\n• Gross Primary Productivity (GPP): 120 GtC/yr\n• Net Ecosystem Exchange (NEE): -4.2 GtC/yr (Sink)"
        )
        self.main_layout.addWidget(self.txt)


class SpaceWeatherPanel(BasePanelWidget):
    """22. Space Weather Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("☀️ SPACE WEATHER & GEOMAGNETIC MONITOR", "#FFF176", registry, dispatcher)
        # NOTE (correction): fixed Kp/solar-wind numbers shown with no
        # real geomagnetic observation connected. Not fabricated.
        self.main_layout.addWidget(_example_layout_disclaimer())
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText(
            "Space Weather Conditions (Example Layout):\n• Geomagnetic Kp Index: Kp = 3 (Quiet)\n• Solar Wind Speed: 420 km/s\n• Ionosphere TEC: 24.5 TECU"
        )
        self.main_layout.addWidget(self.txt)


class GeologyPanel(BasePanelWidget):
    """23. Geology & Volcanology Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🌋 GEOLOGY & VOLCANIC ASH DISPERSION", "#D7CCC8", registry, dispatcher)
        # NOTE (correction — operationally dangerous, aviation-relevant):
        # used to claim a specific "Active Volcanic Plume: Etna Ash
        # Dispersion Model (FL300)" and "Seismic Events: M4.2" with no
        # real seismic/volcanic monitoring network connected - volcanic
        # ash advisories directly affect flight routing. Not fabricated.
        self.main_layout.addWidget(_example_layout_disclaimer())
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText(
            "Geological Status (Example Layout, no active events):\n• Active Volcanic Plume: Etna Ash Dispersion Model (FL300)\n• Seismic Events: M4.2 (Mediterranean)"
        )
        self.main_layout.addWidget(self.txt)


class VerificationPanel(BasePanelWidget):
    """24. Forecast Verification Metrics Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("📊 FORECAST VERIFICATION METRICS", "#A1887F", registry, dispatcher)
        btn = QPushButton("📊 Compute Verification Suite (RMSE, ACC, CRPS)")
        btn.clicked.connect(lambda: self.dispatcher.dispatch("verify_forecast"))
        self.main_layout.addWidget(btn)


class SystemConsolePanel(BasePanelWidget):
    """25. System Console Logs Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("💻 SYSTEM CONSOLE & OPERATIONAL LOGS", "#B0BEC5", registry, dispatcher)
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.main_layout.addWidget(self.log_display)
        self.dispatcher.log_message_emitted.connect(self._append_log)

    def _append_log(self, level: str, text: str) -> None:
        self.log_display.append(f"[{level}] {text}")


class HPCPanel(BasePanelWidget):
    """26. HPC Control Center."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("⚡ HPC CONTROL CENTER & CLUSTER METRICS", "#90A4AE", registry, dispatcher)
        # NOTE (correction): duplicates the same fabrication pattern as
        # HPCDashboardPanel above (fixed MPI ranks/GPU/job-queue numbers,
        # no real cluster connection). Not fabricated.
        self.main_layout.addWidget(_example_layout_disclaimer())
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText(
            "HPC Cluster Topology & Execution (Example Layout):\n"
            "• Active MPI Ranks: 128 Processes\n"
            "• CUDA GPU Acceleration: Enabled (NVIDIA A100 80GB)\n"
            "• OpenMP Threads: 16 Threads / Rank\n"
            "• Memory Bandwidth: 1.5 TB/s\n"
            "• Job Queue Status: 4 Active Jobs, 0 Queued\n"
            "• Fault-Tolerant Checkpoint: Step 360 Saved"
        )
        self.main_layout.addWidget(self.txt)


class AWCIDashboardPanel(QWidget):
    """28. Aviation Weather Complexity Index (AWCI) operational dashboard.

    Embeds the full acf.gui.dashboard.AWCIDashboard widget directly (it
    already has its own header/title, unlike the other panels here, so this
    intentionally skips BasePanelWidget's extra title bar to avoid a
    redundant double header). registry/dispatcher are accepted for
    signature consistency with every other panel constructor but are not
    used - the AWCI dashboard's own numbers come from the real
    AWCICalculator over a synthetic demo field (see
    acf.gui.dashboard.awci_synthetic_field's docstring), not from any
    registry-managed subsystem.

    Wrapped in a QScrollArea: the dashboard's maps/radar/charts need real
    vertical space to stay legible, but this panel shares the bottom dock
    with 27 other tabs at whatever height the operator has left it - a
    plain embed got compressed and overlapping there instead of scrolling.
    """

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__()
        self.registry = registry
        self.dispatcher = dispatcher

        from acf.gui.dashboard.awci_dashboard import AWCIDashboard

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.awci_dashboard = AWCIDashboard()
        self.awci_dashboard.setMinimumSize(1200, 900)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.awci_dashboard)
        layout.addWidget(scroll)


class CatalogPanel(BasePanelWidget):
    """29. Parameter Catalog Browser - real, previously-unbuilt System
    Explorer category (2026-09-04): "Catalog" (WMO Standards, CF-1.8
    Conventions, ECMWF Parameters leaves) had zero real panel behind
    it - a genuine dead click on all 3 leaves.

    Real backend: `acf.catalog.manager.CatalogManager.scientific`
    (`ModuleRegistry`'s own real, already-connected "catalog" module) -
    a real `ScientificCatalog` populated with 64 real
    `CatalogEntry` records (surface/atmosphere/ocean/satellite/climate
    parameters - `acf.catalog.default_catalog.create_catalog()`), each
    with a real CF (Climate and Forecast conventions) `standard_name`
    and real physical `units` - genuinely real, cited scientific
    metadata, not invented for this panel.

    Honest scope: this catalog's own `grib_code`/`cf_name` fields exist
    in its schema (`acf.catalog.catalog_entry.CatalogEntry`) but are
    genuinely unpopulated (empty string) for every one of the 64 real
    entries in this codebase - shown as empty, never a fabricated WMO
    or ECMWF code this project has no real source for. The single real
    catalog below is what genuinely backs all 3 tree leaves (WMO
    Standards/CF-1.8 Conventions/ECMWF Parameters) - there is no
    separate real WMO-specific or ECMWF-specific data source in this
    codebase to distinguish them further (same "one real panel per
    category, not per leaf, when only one real backend exists"
    convention as Simulation/Forecast above)."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("📚 PARAMETER CATALOG (WMO / CF-1.8 / ECMWF)", "#4DB6AC", registry, dispatcher)

        catalog_manager = registry.get_module("catalog")
        if catalog_manager is None:
            self.main_layout.addWidget(_not_connected_label("catalog"))
            return

        self._entries = list(catalog_manager.scientific.all())

        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("🔍 Filter:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("parameter id, standard name, category…")
        self.search_input.textChanged.connect(self._apply_filter)
        search_row.addWidget(self.search_input)
        self.main_layout.addLayout(search_row)

        self.count_label = QLabel()
        self.count_label.setStyleSheet("color: #B0BEC5; font-size: 10px;")
        self.main_layout.addWidget(self.count_label)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Parameter ID", "CF Standard Name", "Long Name", "Units", "Category", "Level Type"]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.main_layout.addWidget(self.table)

        self._populate(self._entries)

    def _populate(self, entries: list[Any]) -> None:
        self.table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            for col, value in enumerate(
                (entry.parameter_id, entry.standard_name, entry.long_name, entry.units, entry.category, entry.level_type)
            ):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
        self.count_label.setText(f"{len(entries)} of {len(self._entries)} real catalog entries")

    def _apply_filter(self, text: str) -> None:
        query = text.strip().lower()
        if not query:
            self._populate(self._entries)
            return
        filtered = [
            e
            for e in self._entries
            if query in e.parameter_id.lower() or query in e.standard_name.lower() or query in e.category.lower()
        ]
        self._populate(filtered)


class PanelManager:
    """Instantiates and manages all 28 operational PySide6 ESOC panels."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        self.registry = registry
        self.dispatcher = dispatcher

        self.panels: dict[str, QWidget] = {
            "hpc_dashboard": HPCDashboardPanel(registry, dispatcher),
            "hpc_terminal": HPCTerminalPanel(registry, dispatcher),
            "cluster_explorer": ClusterExplorerPanel(registry, dispatcher),
            "job_explorer": JobExplorerPanel(registry, dispatcher),
            "gpu_monitor": GPUMonitorPanel(registry, dispatcher),
            "storage_monitor": StorageMonitorPanel(registry, dispatcher),
            "benchmark_panel": BenchmarkPanel(registry, dispatcher),
            "planetary_dashboard": PlanetaryDashboardPanel(registry, dispatcher),
            "data_assimilation": DataAssimilationPanel(registry, dispatcher),
            "earth_monitoring": EarthMonitoringPanel(registry, dispatcher),
            "earth_physics": EarthPhysicsPanel(registry, dispatcher),
            "forecast": ForecastPanel(registry, dispatcher),
            "simulation": SimulationPanel(registry, dispatcher),
            "digital_twin": DigitalTwinPanel(registry, dispatcher),
            "ai_forecast": AIForecastPanel(registry, dispatcher),
            "hazards": HazardsPanel(registry, dispatcher),
            "climate": ClimatePanel(registry, dispatcher),
            "ocean": OceanPanel(registry, dispatcher),
            "hydrology": HydrologyPanel(registry, dispatcher),
            "cryosphere": CryospherePanel(registry, dispatcher),
            "air_quality": AirQualityPanel(registry, dispatcher),
            "carbon": CarbonPanel(registry, dispatcher),
            "space_weather": SpaceWeatherPanel(registry, dispatcher),
            "geology": GeologyPanel(registry, dispatcher),
            "verification": VerificationPanel(registry, dispatcher),
            "system_console": SystemConsolePanel(registry, dispatcher),
            "hpc": HPCPanel(registry, dispatcher),
            "awci_dashboard": AWCIDashboardPanel(registry, dispatcher),
            "catalog": CatalogPanel(registry, dispatcher),
        }

    def get_panel(self, name: str) -> QWidget | None:
        """Return target QWidget panel by key identifier."""
        return self.panels.get(name)

    def list_panel_names(self) -> list[str]:
        """Return list of panel identifiers."""
        return list(self.panels.keys())


# Compatibility alias
ESOCPanelManager = PanelManager
