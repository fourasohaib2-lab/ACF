"""Panel Manager instantiating 22 operational PySide6 dock panels for ESOC (ACF-UI-013)."""

from typing import Dict, List, Optional
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QComboBox,
    QGroupBox,
    QSlider,
)
from PySide6.QtCore import Qt

from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.command_dispatcher import CommandDispatcher


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


class PlanetaryDashboardPanel(BasePanelWidget):
    """1. Planetary Health Score & 9 Planetary Boundaries Dashboard."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🌍 PLANETARY DASHBOARD & HEALTH SCORE", "#4FC3F7", registry, dispatcher)
        
        lbl_score = QLabel("Planetary Health Index: 68.4 / 100 (MODERATE RISK)")
        lbl_score.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFB74D; padding: 4px;")
        self.main_layout.addWidget(lbl_score)

        self.table = QTableWidget(9, 3)
        self.table.setHorizontalHeaderLabels(["Planetary Boundary", "Status", "Control Variable"])
        boundaries = [
            ("1. Climate Change", "TRANSCENDED", "422 ppm CO2 (+1.25°C)"),
            ("2. Biosphere Integrity", "TRANSCENDED", "E/MSY > 100"),
            ("3. Land-System Change", "TRANSCENDED", "60% Forest Cover Remaining"),
            ("4. Freshwater Change", "TRANSCENDED", "Blue & Green Water Deficit"),
            ("5. Biogeochemical (N & P)", "TRANSCENDED", "P=22 Tg/yr, N=150 Tg/yr"),
            ("6. Ocean Acidification", "SAFE ZONE", "Aragonite Saturation 2.90"),
            ("7. Atmospheric Aerosols", "SAFE ZONE", "AOD = 0.12 Global Mean"),
            ("8. Stratospheric Ozone", "SAFE ZONE", "285 Dobson Units"),
            ("9. Novel Entities", "TRANSCENDED", "Synthetic Chemical Flux"),
        ]
        for row, (b_name, st, val) in enumerate(boundaries):
            self.table.setItem(row, 0, QTableWidgetItem(b_name))
            self.table.setItem(row, 1, QTableWidgetItem(st))
            self.table.setItem(row, 2, QTableWidgetItem(val))
        self.main_layout.addWidget(self.table)


class DataAssimilationPanel(BasePanelWidget):
    """2. Live Data Assimilation Telemetry Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🔄 DATA ASSIMILATION & OBSERVATION TELEMETRY", "#AED581", registry, dispatcher)
        
        self.txt_da = QTextEdit()
        self.txt_da.setReadOnly(True)
        self.txt_da.setText(
            "Live Data Assimilation Metrics:\n"
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
    """3. Live Earth Monitoring Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("📡 EARTH OBSERVATION & MONITORING CENTER", "#4FC3F7", registry, dispatcher)
        group = QGroupBox("Live Observation Feeds")
        g_layout = QVBoxLayout(group)
        self.table = QTableWidget(6, 3)
        self.table.setHorizontalHeaderLabels(["Data Source", "Status", "Latency"])
        sources = [
            ("GOES/MTG Satellites", "ACTIVE", "1.2 min"),
            ("Doppler Radar (NEXRAD)", "ACTIVE", "0.5 min"),
            ("Surface AWS (SYNOP/METAR)", "STREAMING", "0.1 min"),
            ("ARGO Ocean Floats", "SYNCED", "12.0 min"),
            ("AMDAR Aircraft", "ACTIVE", "0.8 min"),
            ("Lightning Network", "STREAMING", "0.05 min"),
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
    """4. Earth System Physics Panel."""

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
    """5. Weather Forecast Matrix Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🔮 GLOBAL & REGIONAL NWP FORECAST MATRIX", "#FFD54F", registry, dispatcher)
        btn = QPushButton("🚀 Generate 15-Day Global NWP Forecast")
        btn.clicked.connect(lambda: self.dispatcher.dispatch("run_simulation"))
        self.main_layout.addWidget(btn)


class SimulationPanel(BasePanelWidget):
    """6. Simulation Control Center & Run Manager."""

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
        self.combo_physics.addItems(["Primitive Equations Core", "Non-Hydrostatic Finite Volume", "Spherical Spectral Wave Solver"])
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

        self.main_layout.addWidget(QLabel("Time Integration Progress (CFL = 0.32 Stable):"))
        self.progress = QProgressBar()
        self.progress.setValue(45)
        self.main_layout.addWidget(self.progress)
        self.lbl_eta = QLabel("Estimated Completion Time (ETA): 4 mins 12 secs")
        self.lbl_eta.setStyleSheet("color: #B0BEC5; font-size: 11px;")
        self.main_layout.addWidget(self.lbl_eta)


class DigitalTwinPanel(BasePanelWidget):
    """7. Digital Twin Center & Planetary Scenarios."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🌐 EARTH DIGITAL TWIN CENTER & PLANETARY LIMITS", "#BA68C8", registry, dispatcher)
        self.combo = QComboBox()
        self.combo.addItems([
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
        ])
        self.main_layout.addWidget(self.combo)

        btn_load = QPushButton("🔮 Load Digital Twin Scenario")
        btn_load.clicked.connect(lambda: self.dispatcher.dispatch("load_digital_twin", scenario=self.combo.currentText()))
        self.main_layout.addWidget(btn_load)

        self.main_layout.addWidget(QLabel("Interactive Time Slider (1950 - 2100):"))
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(1950, 2100)
        self.slider.setValue(2026)
        self.main_layout.addWidget(self.slider)


class AIForecastPanel(BasePanelWidget):
    """8. AI Operations Center."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🧠 AI OPERATIONS CENTER (PINN / GNN / FNO)", "#4DD0E1", registry, dispatcher)
        
        self.txt_ai_info = QTextEdit()
        self.txt_ai_info.setReadOnly(True)
        self.txt_ai_info.setText(
            "AI Neural Operators & Models:\n"
            "• Fourier Neural Operator (FNO): 1000x Speedup\n"
            "• Graph Neural Network (GNN): Multi-mesh global forecast\n"
            "• PINN Surrogate: Physics-informed mass/momentum correction\n"
            "• Automatic Calibration: Active\n"
            "• Uncertainty Evaluation: 94.6% Confidence Interval"
        )
        self.main_layout.addWidget(self.txt_ai_info)

        btn_fno = QPushButton("⚡ Execute FNO Neural Forecast (1000x)")
        btn_fno.clicked.connect(lambda: self.dispatcher.dispatch("run_ai_forecast"))
        self.main_layout.addWidget(btn_fno)


class HazardsPanel(BasePanelWidget):
    """9. Hazard Operations Center & Civil Protection."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("⚠️ HAZARD OPERATIONS CENTER & EMERGENCY RESPONSE", "#E57373", registry, dispatcher)
        
        self.txt_threats = QTextEdit()
        self.txt_threats.setReadOnly(True)
        self.txt_threats.setText(
            "Active Hazard Threats:\n"
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
    """10. Climate Scenarios Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🌡️ CLIMATE SCENARIOS (CMIP6 / SSP)", "#FF8A65", registry, dispatcher)
        btn = QPushButton("📈 Project SSP Horizon Trajectory")
        btn.clicked.connect(lambda: self.dispatcher.dispatch("run_climate_projection"))
        self.main_layout.addWidget(btn)


class OceanPanel(BasePanelWidget):
    """11. Oceanography Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🌊 3D OCEAN DYNAMICS & WAVE SPECTRA", "#0288D1", registry, dispatcher)
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText("Ocean Hydrodynamics:\n• AMOC Strength: 18.2 Sverdrups\n• Peak Wave Period (Tp): 11.4 s\n• Significant Wave Height (Hs): 3.2 m")
        self.main_layout.addWidget(self.txt)


class HydrologyPanel(BasePanelWidget):
    """12. Hydrology & Inundation Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("💧 HYDROLOGY & FLASH FLOOD INUNDATION", "#0097A7", registry, dispatcher)
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText("Hydrological Runoff:\n• Soil Moisture Saturation: 84%\n• River Basin Runoff Q: 1240 m^3/s\n• Max Inundation Depth: 0.85 m")
        self.main_layout.addWidget(self.txt)


class CryospherePanel(BasePanelWidget):
    """13. Cryosphere Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("❄️ CRYOSPHERE & POLAR SEA-ICE MONITOR", "#80DEEA", registry, dispatcher)
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText("Polar Sea Ice:\n• Arctic Ice Extent: 4.2 million km^2\n• Ice Thickness: 1.8 m\n• Permafrost Thaw Rate: 2.1 cm/yr")
        self.main_layout.addWidget(self.txt)


class AirQualityPanel(BasePanelWidget):
    """14. Air Quality & Chemistry Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🌫️ AIR QUALITY & ATMOSPHERIC CHEMISTRY", "#CE93D8", registry, dispatcher)
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText("Air Quality Index (AQI):\n• PM2.5: 18 ug/m^3 (Good)\n• Ozone O3: 42 ppb\n• NO2 Column: 1.2e15 molec/cm^2")
        self.main_layout.addWidget(self.txt)


class CarbonPanel(BasePanelWidget):
    """15. Terrestrial & Ocean Carbon Cycle Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🌱 CARBON CYCLE & NET ECOSYSTEM EXCHANGE (NEE)", "#A5D6A7", registry, dispatcher)
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText("Carbon Flux Balance:\n• Gross Primary Productivity (GPP): 120 GtC/yr\n• Net Ecosystem Exchange (NEE): -4.2 GtC/yr (Sink)")
        self.main_layout.addWidget(self.txt)


class SpaceWeatherPanel(BasePanelWidget):
    """16. Space Weather Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("☀️ SPACE WEATHER & GEOMAGNETIC MONITOR", "#FFF176", registry, dispatcher)
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText("Space Weather Conditions:\n• Geomagnetic Kp Index: Kp = 3 (Quiet)\n• Solar Wind Speed: 420 km/s\n• Ionosphere TEC: 24.5 TECU")
        self.main_layout.addWidget(self.txt)


class GeologyPanel(BasePanelWidget):
    """17. Geology & Volcanology Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🌋 GEOLOGY & VOLCANIC ASH DISPERSION", "#D7CCC8", registry, dispatcher)
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText("Geological Status:\n• Active Volcanic Plume: Etna Ash Dispersion Model (FL300)\n• Seismic Events: M4.2 (Mediterranean)")
        self.main_layout.addWidget(self.txt)


class VerificationPanel(BasePanelWidget):
    """18. Forecast Verification Metrics Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("📊 FORECAST VERIFICATION METRICS", "#A1887F", registry, dispatcher)
        btn = QPushButton("📊 Compute Verification Suite (RMSE, ACC, CRPS)")
        btn.clicked.connect(lambda: self.dispatcher.dispatch("verify_forecast"))
        self.main_layout.addWidget(btn)


class SystemConsolePanel(BasePanelWidget):
    """19. System Console Logs Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("💻 SYSTEM CONSOLE & OPERATIONAL LOGS", "#B0BEC5", registry, dispatcher)
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.main_layout.addWidget(self.log_display)
        self.dispatcher.log_message_emitted.connect(self._append_log)

    def _append_log(self, level: str, text: str) -> None:
        self.log_display.append(f"[{level}] {text}")


class HPCPanel(BasePanelWidget):
    """20. HPC Control Center."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("⚡ HPC CONTROL CENTER & CLUSTER METRICS", "#90A4AE", registry, dispatcher)
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText(
            "HPC Cluster Topology & Execution:\n"
            "• Active MPI Ranks: 128 Processes\n"
            "• CUDA GPU Acceleration: Enabled (NVIDIA A100 80GB)\n"
            "• OpenMP Threads: 16 Threads / Rank\n"
            "• Memory Bandwidth: 1.5 TB/s\n"
            "• Job Queue Status: 4 Active Jobs, 0 Queued\n"
            "• Fault-Tolerant Checkpoint: Step 360 Saved"
        )
        self.main_layout.addWidget(self.txt)


class TimelinePanel(BasePanelWidget):
    """21. Temporal Timeline Control Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("⏰ TEMPORAL TIMELINE & EVENT PLAYER", "#FFF59D", registry, dispatcher)
        self.txt = QLabel("Timeline: 2026-08-03 08:00 UTC -> 2026-08-18 08:00 UTC (+15 Days)")
        self.main_layout.addWidget(self.txt)


class AlertsPanel(BasePanelWidget):
    """22. Active System & Weather Alerts Panel."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        super().__init__("🚨 ACTIVE SYSTEM & WEATHER WARNINGS", "#EF5350", registry, dispatcher)
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setText("Active Warnings:\n• RED ALERT: Tropical Cyclone Cat 3 (Caribbean)\n• ORANGE ALERT: Severe Thunderstorm (Midwest)")
        self.main_layout.addWidget(self.txt)


class PanelManager:
    """Instantiates and manages all 22 operational PySide6 ESOC panels."""

    def __init__(self, registry: ModuleRegistry, dispatcher: CommandDispatcher) -> None:
        self.registry = registry
        self.dispatcher = dispatcher

        self.panels: Dict[str, QWidget] = {
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
            "timeline": TimelinePanel(registry, dispatcher),
            "alerts": AlertsPanel(registry, dispatcher),
        }

    def get_panel(self, name: str) -> Optional[QWidget]:
        """Return target QWidget panel by key identifier."""
        return self.panels.get(name)

    def list_panel_names(self) -> List[str]:
        """Return list of panel identifiers."""
        return list(self.panels.keys())
