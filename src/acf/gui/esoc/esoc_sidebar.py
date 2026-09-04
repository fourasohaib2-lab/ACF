"""ESOC Left System Explorer Sidebar with Global Search & Right Multi-Tab Inspector (ACF-HPC-002).

NOTE (correction — fabricated "live" inspector tabs): ESOCRightSidebar's
7 tabs used to unconditionally display specific fixed values at widget
construction time - a selected grid cell's temperature/wind/SST, CAPE/
CIN/tornado-parameter diagnostics, a SHA256 "checksum" (itself
corrupted - a truncated copy of the well-known SHA256-of-empty-string
example hash), a running data-assimilation/forecast log, and GPU/TFLOPS
performance numbers - none connected to any real selection, dataset,
simulation, or HPC telemetry feed (this file has no such connection
available at all). This is the same fabricated-panel-content pattern
already found and fixed across 20 of 26 other ESOC operator panels
(see panel_manager.py's own NOTE (correction) entries and its shared
_example_layout_disclaimer() helper, reused here rather than
reinvented) - this file was evidently missed in that pass. Clicking
"Render Plot" also used to unconditionally append "[PLOT RENDERED]:
... generated successfully" with no plot ever actually rendered
anywhere (no chart widget, no matplotlib figure). Not fabricated.
"""

from collections.abc import Callable

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import _example_layout_disclaimer


class ESOCLeftSidebar(QWidget):
    """Left Sidebar: Universal Global Search Bar + System Explorer navigation tree.

    NOTE (correction, 2026-09-04): the "🔍 Universal Search" placeholder
    always promised real modules/AI results, but this class had no way
    to reach `ModuleRegistry` at all - `ESOCLayout` (the only real
    caller, `esoc_layout.py`) constructed it with zero arguments, so
    `_on_search_text_changed()` could only ever filter this widget's
    own static `self.categories` label tree. `ModuleRegistry.
    global_search()`/`is_connected()`/`get_system_status_summary()`
    (fixed the same day this note was written - see that module's own
    docstring) had, verified by a repo-wide grep, ZERO real callers
    anywhere in the app. New optional `registry` parameter closes that
    gap two ways: a real search now also queries
    `registry.global_search()` and reports the real match count/names
    beneath the search box (the tree's own static filter is unchanged,
    still real, still useful for pure category browsing - this is a
    real, additive second result, not a replacement); and a real,
    always-visible status line reports `registry.
    get_system_status_summary()`'s own real connected-subsystem count
    - this and global_search() were the last 2 pieces of ModuleRegistry
    with no real GUI consumer anywhere; both now have one."""

    def __init__(
        self,
        on_select_callback: Callable[[str], None] | None = None,
        registry: ModuleRegistry | None = None,
    ) -> None:
        super().__init__()
        self.on_select_callback = on_select_callback
        self.registry = registry

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        header = QLabel("📁 SYSTEM EXPLORER")
        header.setStyleSheet("font-weight: bold; font-size: 12px; color: #4FC3F7;")
        layout.addWidget(header)

        # Real registry.get_system_status_summary() readout (added
        # 2026-09-04) - this and global_search() below were, before
        # this same day's closures, the last 2 pieces of ModuleRegistry
        # API with zero real GUI consumers anywhere in the app (see
        # module_registry.py's own docstring). A static snapshot taken
        # once at construction time - ModuleRegistry itself has no
        # "reconnect" concept, every registration already ran by the
        # time this widget exists, so there is nothing real to refresh
        # later. Hidden (not "0/0") when no registry was supplied.
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #9fb0c9; font-size: 10px;")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        if self.registry is not None:
            summary = self.registry.get_system_status_summary()
            connected, total = summary["connected_count"], summary["total_modules"]
            dot = "🟢" if connected == total else "🟡"
            self.status_label.setText(f"{dot} {connected}/{total} real subsystems connected")
            self.status_label.setToolTip(
                "From ModuleRegistry.get_system_status_summary() - a real subsystem is "
                "'connected' only when its actual class was found and instantiated; a "
                "missing/renamed class honestly counts as not connected, never silently "
                "hidden."
            )
            self.status_label.setVisible(True)

        search_box = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Universal Search (Modules, Parameters, Maps, AI)...")
        self.search_input.textChanged.connect(self._on_search_text_changed)
        search_box.addWidget(self.search_input)
        layout.addLayout(search_box)

        # Real ModuleRegistry.global_search() results (added 2026-09-04
        # - see this class's own NOTE above) - hidden until a real,
        # non-empty query has actually run, so it never shows a
        # misleading "0 results" before the user has typed anything.
        self.search_results_label = QLabel("")
        self.search_results_label.setWordWrap(True)
        self.search_results_label.setStyleSheet("color: #4FC3F7; font-size: 10px;")
        self.search_results_label.setVisible(False)
        layout.addWidget(self.search_results_label)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)

        self.categories = {
            "Earth System": [
                "Atmosphere",
                "Ocean",
                "Hydrology",
                "Cryosphere",
                "Biosphere",
                "Land Surface",
                "Carbon Cycle",
                "Atmospheric Chemistry",
                "Air Quality",
                "Aerosols",
                "Dust",
                "Wildfires",
                "Volcanoes",
                "Geology",
            ],
            "Forecast": [
                "Short-Range NWP",
                "Medium-Range (15 days)",
                "Global Circulation",
                "One-Click Forecast Pipeline",
            ],
            "Assimilation": ["4D-Var Solver", "EnKF (50-member)", "Hybrid 4DEnVar", "Quality Control"],
            "Simulation": ["Coupled Earth Solver", "Finite Volume", "Spectral Solver", "AMR"],
            "Digital Twin": ["Present Earth", "Historical Replay", "2030", "2050", "2100", "2300"],
            "Climate": ["CMIP6 Trajectories", "SSP1-1.9 to SSP5-8.5", "Sea Level Rise"],
            "Planetary Limits": ["9 Planetary Boundaries Audit", "Freshwater & Biosphere"],
            "Geoengineering": ["Stratospheric Aerosol Injection", "Direct Air Capture (DACCS)"],
            "Artificial Intelligence": ["Fourier Neural Operators (FNO)", "GNN Surrogates", "PINN Models"],
            "Machine Learning": ["Model Calibration", "Feature Importance", "Uncertainty Quant"],
            "Earth Physics": ["Mass/Energy Conservation", "Navier-Stokes", "Thermodynamics"],
            "Monitoring": ["GOES/MTG Satellites", "NEXRAD Radar", "SYNOP/METAR AWS", "ARGO Floats"],
            "Verification": ["RMSE & MAE", "ACC Correlation", "CRPS & Brier Score", "ROC Curve"],
            "Products": ["Weather Bulletins", "Aviation SIGMETs", "Hydrological Warnings"],
            "Reports": ["Executive Risk Briefings", "Climate Impact Assessments"],
            "Catalog": ["WMO Standards", "CF-1.8 Conventions", "ECMWF Parameters"],
            "Output": ["NetCDF4 Files", "Cloud Zarr Stores", "GRIB2 Datasets", "GeoTIFF Maps"],
            "Settings": ["Workspace Modes", "Layer Preferences", "API Keys", "System Config"],
            "Plugins": ["Custom Physics Extensions", "AI Model Plug-ins"],
            "HPC": [
                "HPC Profiles",
                "Job Explorer",
                "Storage & Scratch",
                "Remote Terminal",
                "CUDA GPU Monitor",
                "MPI Domain Topology",
                "Benchmarks",
            ],
        }

        self._populate_tree(self.categories)
        self.tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.tree)

    def _populate_tree(self, categories: dict) -> None:
        self.tree.clear()
        for cat, items in categories.items():
            parent = QTreeWidgetItem(self.tree, [cat])
            for item in items:
                QTreeWidgetItem(parent, [item])
        self.tree.expandAll()

    def _on_search_text_changed(self, text: str) -> None:
        if not text or len(text.strip()) == 0:
            self._populate_tree(self.categories)
            self.search_results_label.setVisible(False)
            return

        query = text.lower().strip()
        filtered = {}
        for cat, items in self.categories.items():
            matching_items = [i for i in items if query in i.lower() or query in cat.lower()]
            if matching_items or query in cat.lower():
                filtered[cat] = matching_items if matching_items else items
        self._populate_tree(filtered)

        self._update_real_search_results(text)

    def _update_real_search_results(self, text: str) -> None:
        """Real registry.global_search() results for this same query -
        see this class's own NOTE (correction) for why this exists.
        A caller with no registry (e.g. this widget used standalone,
        as several tests do) simply gets no real-results line, never a
        fabricated one."""
        if self.registry is None:
            self.search_results_label.setVisible(False)
            return

        results = self.registry.global_search(text)
        if not results:
            self.search_results_label.setText(f"🔍 0 real matches in ModuleRegistry for \"{text}\"")
        else:
            shown = ", ".join(r["name"] for r in results[:5])
            more = f" (+{len(results) - 5} more)" if len(results) > 5 else ""
            self.search_results_label.setText(f"🔍 {len(results)} real match(es): {shown}{more}")
        self.search_results_label.setVisible(True)

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        text = item.text(0)
        if self.on_select_callback:
            self.on_select_callback(text)


class ESOCRightSidebar(QWidget):
    """Right Sidebar: 7 Inspector Tabs & Scientific Plotting Engine."""

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.tabs = QTabWidget()

        # 1. Properties Tab
        tab_props_container = QWidget()
        props_layout = QVBoxLayout(tab_props_container)
        props_layout.setContentsMargins(0, 0, 0, 0)
        props_layout.addWidget(_example_layout_disclaimer())
        self.tab_props = QTextEdit()
        self.tab_props.setReadOnly(True)
        self.tab_props.setText(
            "Example Layout (values below are illustrative, not tied to any real selection):\n"
            "• Selected Entity: Global Grid cell (45.0°N, 10.0°E)\n"
            "• Resolution: 25 km\n"
            "• Vertical Levels: 32 Hybrid Sigma-Pressure\n"
            "• 2m Temperature: 288.15 K (15.0°C)\n"
            "• Surface Pressure: 1013.25 hPa\n"
            "• Wind Vector: U=12.4 m/s, V=-3.1 m/s\n"
            "• Specific Humidity: 0.0084 kg/kg\n"
            "• SST Anomaly: +0.42°C\n"
            "• Soil Moisture: 0.28 m^3/m^3"
        )
        props_layout.addWidget(self.tab_props)

        # 2. Diagnostics Tab
        tab_diag_container = QWidget()
        diag_layout = QVBoxLayout(tab_diag_container)
        diag_layout.setContentsMargins(0, 0, 0, 0)
        diag_layout.addWidget(_example_layout_disclaimer())
        self.tab_diag = QTextEdit()
        self.tab_diag.setReadOnly(True)
        self.tab_diag.setText(
            "Example Layout (values below are illustrative, not computed from any real sounding):\n"
            "• CAPE: 1420 J/kg\n"
            "• CIN: 18 J/kg\n"
            "• Bulk Shear (0-6km): 24.5 m/s\n"
            "• Supercell Composite (SCP): 2.4\n"
            "• Significant Tornado (STP): 1.1\n"
            "• FWI Fire Weather Index: 34.2 (Extreme)"
        )
        diag_layout.addWidget(self.tab_diag)

        # 3. Metadata Tab
        tab_meta_container = QWidget()
        meta_layout = QVBoxLayout(tab_meta_container)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.addWidget(_example_layout_disclaimer())
        self.tab_meta = QTextEdit()
        self.tab_meta.setReadOnly(True)
        self.tab_meta.setText(
            "Example Layout (values below are illustrative, not read from any real dataset):\n"
            "• Standard: WMO / CF-1.8 Compliant\n"
            "• Ingestion Source: Sentinel-3 OLCI & GOES-16\n"
            "• Projection: WGS84 Spherical Ellipsoid\n"
            "• Grid Bounds: [-90, +90] Lat, [-180, +180] Lon\n"
            "• Checksum: not computed (no real file is connected to this example)"
        )
        meta_layout.addWidget(self.tab_meta)

        # 4. Simulation Tab
        tab_sim_container = QWidget()
        sim_layout = QVBoxLayout(tab_sim_container)
        sim_layout.setContentsMargins(0, 0, 0, 0)
        sim_layout.addWidget(_example_layout_disclaimer())
        self.tab_sim = QTextEdit()
        self.tab_sim.setReadOnly(True)
        self.tab_sim.setText(
            "Example Layout (values below are illustrative, not from any running simulation):\n"
            "• Engine: Coupled Earth Solver (ACF-DT-003)\n"
            "• Active Timestep: t = 60.0 s\n"
            "• Integration Step: 360 / 1440\n"
            "• CFL Condition Number: C = 0.32 (Stable)\n"
            "• Mass Conservation Error: < 1.2e-6"
        )
        sim_layout.addWidget(self.tab_sim)

        # 5. Logs Tab
        tab_logs_container = QWidget()
        logs_layout = QVBoxLayout(tab_logs_container)
        logs_layout.setContentsMargins(0, 0, 0, 0)
        logs_layout.addWidget(_example_layout_disclaimer())
        self.tab_logs = QTextEdit()
        self.tab_logs.setReadOnly(True)
        self.tab_logs.setText(
            "Example Layout (lines below are illustrative, not a real operational log):\n"
            "[INFO] Initialization complete.\n"
            "[INFO] Data Assimilation 4D-Var cycle converged in 12 iterations.\n"
            "[INFO] Forecast run started. HPC 128 MPI Ranks active.\n"
            "[WARNING] High CAPE detected over Central Plains."
        )
        logs_layout.addWidget(self.tab_logs)

        # 6. Performance Tab
        tab_perf_container = QWidget()
        perf_layout = QVBoxLayout(tab_perf_container)
        perf_layout.setContentsMargins(0, 0, 0, 0)
        perf_layout.addWidget(_example_layout_disclaimer())
        self.tab_perf = QTextEdit()
        self.tab_perf.setReadOnly(True)
        self.tab_perf.setText(
            "Example Layout (values below are illustrative, no HPC telemetry feed is connected here):\n"
            "• CPU Utilization: 14%\n"
            "• GPU Memory Usage: 18.4 / 80.0 GB (NVIDIA A100)\n"
            "• Compute Throughput: 19.5 TFLOPS\n"
            "• Frame Rate: 60 FPS (OpenGL 4.5 Rendering)\n"
            "• Memory Bandwidth: 1.5 TB/s"
        )
        perf_layout.addWidget(self.tab_perf)

        # 7. AI Analysis & Scientific Plotting Tab
        self.tab_ai_plot = QWidget()
        ai_layout = QVBoxLayout(self.tab_ai_plot)

        lbl_chart = QLabel("📈 Scientific Plot Generator:")
        lbl_chart.setStyleSheet("font-weight: bold; color: #4DD0E1;")
        ai_layout.addWidget(lbl_chart)

        self.combo_chart = QComboBox()
        self.combo_chart.addItems(
            [
                "Time Series Plot",
                "Vertical Profile (T, q, P)",
                "Cross Section (Lat-Height)",
                "Hovmöller Diagram",
                "Taylor Diagram (Forecast Verification)",
                "Skew-T Sounding Diagram",
                "Wind Rose (Speed & Direction)",
                "Ensemble Spread Plume Plot",
                "Streamlines & Vector Fields",
            ]
        )
        ai_layout.addWidget(self.combo_chart)

        btn_gen_chart = QPushButton("📊 Render Plot")
        btn_gen_chart.clicked.connect(self._render_plot)
        ai_layout.addWidget(btn_gen_chart)

        ai_layout.addWidget(_example_layout_disclaimer())
        self.txt_ai = QTextEdit()
        self.txt_ai.setReadOnly(True)
        self.txt_ai.setText(
            "Example Layout (AI explanation below is illustrative, not produced by any connected model):\n"
            "• Fourier Neural Operator detects baroclinic wave deepening.\n"
            "• Feature Importance: 500hPa vorticity (0.42) > SST (0.31) > Soil (0.18).\n"
            "• AI Confidence Evaluation: 94.6% calibrated.\n"
            "• Physics-AI Surrogate Acceleration: 1000x"
        )
        ai_layout.addWidget(self.txt_ai)

        self.tabs.addTab(tab_props_container, "Properties")
        self.tabs.addTab(tab_diag_container, "Diagnostics")
        self.tabs.addTab(tab_meta_container, "Metadata")
        self.tabs.addTab(tab_sim_container, "Simulation")
        self.tabs.addTab(tab_logs_container, "Logs")
        self.tabs.addTab(tab_perf_container, "Performance")
        self.tabs.addTab(self.tab_ai_plot, "AI Analysis & Plots")

        layout.addWidget(self.tabs)

    def _render_plot(self) -> None:
        """
        NOTE (correction): this used to unconditionally append
        "[PLOT RENDERED]: ... generated successfully" regardless of
        whether any plot was actually produced - no chart widget or
        matplotlib figure is created anywhere in this method or class.
        Not fabricated.
        """
        chart_type = self.combo_chart.currentText()
        self.txt_ai.append(f"\n[NOT IMPLEMENTED]: no real plotting backend is connected here for '{chart_type}'.")

    def set_properties_text(self, text: str) -> None:
        """Update properties tab display text."""
        self.tab_props.setText(text)
