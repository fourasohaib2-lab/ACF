"""
Atmospheric Complexity Framework (ACF) - ESOC GUI

Global NWP Forecast Center Command Panel (ACF-NWP-001).
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from acf.analysis.postprocessing import PostProcessingEngine
from acf.data.preprocessing import PreprocessingEngine


class NWPForecastCenterPanel(QWidget):
    """
    Unified ESOC GUI Panel hosting the Global NWP Forecast Center:
    - Tab 1: Forecast Center Control
    - Tab 2: Model Configuration Engine
    - Tab 3: Simulation Monitor
    - Tab 4: Verification & Metrics
    - Tab 5: Output Browser
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.preproc = PreprocessingEngine()
        self.postproc = PostProcessingEngine()

        self.setWindowTitle("ACF NWP Forecast Center")
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            "QTabWidget::pane { border: 1px solid #2E364A; background: #161A23; }"
            "QTabBar::tab { background: #202636; color: #A0B0D0; padding: 6px 12px; font-weight: bold; }"
            "QTabBar::tab:selected { background: #0088CC; color: white; }"
        )

        self.tab_center = self._build_center_tab()
        self.tab_config = self._build_config_tab()
        self.tab_monitor = self._build_monitor_tab()
        self.tab_verify = self._build_verify_tab()
        self.tab_browser = self._build_browser_tab()

        self.tabs.addTab(self.tab_center, "🌐 Forecast Center")
        self.tabs.addTab(self.tab_config, "⚙️ Model Config")
        self.tabs.addTab(self.tab_monitor, "📊 Simulation Monitor")
        self.tabs.addTab(self.tab_verify, "📈 Verification Panel")
        self.tabs.addTab(self.tab_browser, "📁 Output Browser")

        layout.addWidget(self.tabs)

    def _build_center_tab(self) -> QWidget:
        w = QWidget()
        tab_layout = QVBoxLayout(w)

        lbl = QLabel("🌐 OPERATIONAL GLOBAL & REGIONAL FORECAST COMMAND")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #00E6FF;")
        tab_layout.addWidget(lbl)

        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setText(
            "Active NWP Forecast Cycles:\n"
            "• AROME 00Z Cycle: COMPLETED (48h forecast, 1.3 km grid)\n"
            "• ARPEGE 00Z Cycle: RUNNING (102h forecast, 105 hybrid levels)\n"
            "• ALADIN 06Z Cycle: QUEUED\n"
            "• WRF-Algeria 00Z Cycle: COMPLETED (72h forecast)\n"
            "• ECMWF IFS 00Z Ingestion: COMPLETED (0.1° resolution)"
        )
        tab_layout.addWidget(txt)
        return w

    def _build_config_tab(self) -> QWidget:
        w = QWidget()
        tab_layout = QVBoxLayout(w)

        lbl_title = QLabel("⚙️ FORECAST CONFIGURATION ENGINE")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #00E6FF;")
        tab_layout.addWidget(lbl_title)

        h1 = QHBoxLayout()
        lbl_m = QLabel("Model:")
        lbl_m.setStyleSheet("color: #D0D8E8;")
        h1.addWidget(lbl_m)
        cb_model = QComboBox()
        cb_model.addItems(["AROME", "ARPEGE", "ALADIN", "WRF", "ICON", "IFS", "FV3", "MPAS", "GFS"])
        h1.addWidget(cb_model)

        lbl_d = QLabel("Domain:")
        lbl_d.setStyleSheet("color: #D0D8E8;")
        h1.addWidget(lbl_d)
        txt_dom = QLineEdit("Algeria_Domain")
        h1.addWidget(txt_dom)
        tab_layout.addLayout(h1)

        h2 = QHBoxLayout()
        lbl_f = QLabel("Forecast Hours:")
        lbl_f.setStyleSheet("color: #D0D8E8;")
        h2.addWidget(lbl_f)
        sp_fcst = QSpinBox()
        sp_fcst.setRange(1, 240)
        sp_fcst.setValue(48)
        h2.addWidget(sp_fcst)

        lbl_n = QLabel("Nodes:")
        lbl_n.setStyleSheet("color: #D0D8E8;")
        h2.addWidget(lbl_n)
        sp_nodes = QSpinBox()
        sp_nodes.setRange(1, 128)
        sp_nodes.setValue(4)
        h2.addWidget(sp_nodes)

        tab_layout.addLayout(h2)

        btn_save = QPushButton("💾 Save & Generate Namelist")
        btn_save.setStyleSheet("background-color: #0088CC; color: white; font-weight: bold; padding: 6px;")
        tab_layout.addWidget(btn_save)

        tab_layout.addStretch()
        return w

    def _build_monitor_tab(self) -> QWidget:
        w = QWidget()
        tab_layout = QVBoxLayout(w)
        lbl_title = QLabel("📊 SIMULATION MONITOR")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #00E6FF;")
        tab_layout.addWidget(lbl_title)

        # NOTE (correction): this table used to show 3 fixed runs with
        # specific progress/walltime/COMPLETED-RUNNING statuses at
        # widget construction time, with no connection to any real
        # scheduler or job monitor - matches the same fabrication
        # pattern found across gui/esoc/panel_manager.py (fixed earlier
        # this session). Not fabricated.
        lbl_disclaimer = QLabel("⚠ Example layout — not wired to a live data source yet")
        lbl_disclaimer.setStyleSheet("color: #FF7043; font-size: 10px; font-style: italic;")
        tab_layout.addWidget(lbl_disclaimer)
        table = QTableWidget(3, 5)
        table.setHorizontalHeaderLabels(["Run ID", "Model", "Progress", "Walltime", "Status"])
        data = [
            ("arome_00z_1001", "AROME", "N/A", "N/A", "EXAMPLE"),
            ("arpege_00z_1002", "ARPEGE", "N/A", "N/A", "EXAMPLE"),
            ("wrf_00z_1003", "WRF", "N/A", "N/A", "EXAMPLE"),
        ]
        for row, (rid, m, pr, wt, st) in enumerate(data):
            table.setItem(row, 0, QTableWidgetItem(rid))
            table.setItem(row, 1, QTableWidgetItem(m))
            table.setItem(row, 2, QTableWidgetItem(pr))
            table.setItem(row, 3, QTableWidgetItem(wt))
            table.setItem(row, 4, QTableWidgetItem(st))

        tab_layout.addWidget(table)
        return w

    def _build_verify_tab(self) -> QWidget:
        w = QWidget()
        tab_layout = QVBoxLayout(w)
        lbl_title = QLabel("📈 NWP VERIFICATION METRICS (SYNOP / TEMP)")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #00E6FF;")
        tab_layout.addWidget(lbl_title)

        table = QTableWidget(4, 5)
        table.setHorizontalHeaderLabels(["Parameter", "RMSE", "BIAS", "MAE", "ACC Score"])
        metrics = [
            ("2m Temperature (T2M)", "1.15 K", "+0.24 K", "0.89 K", "0.982"),
            ("10m Wind Speed", "1.85 m/s", "-0.12 m/s", "1.40 m/s", "0.954"),
            ("MSLP Pressure", "0.75 hPa", "+0.05 hPa", "0.55 hPa", "0.995"),
            ("24h Precip ETS (>1mm)", "--", "--", "--", "0.684"),
        ]
        for row, (p, r, b, m, a) in enumerate(metrics):
            table.setItem(row, 0, QTableWidgetItem(p))
            table.setItem(row, 1, QTableWidgetItem(r))
            table.setItem(row, 2, QTableWidgetItem(b))
            table.setItem(row, 3, QTableWidgetItem(m))
            table.setItem(row, 4, QTableWidgetItem(a))

        tab_layout.addWidget(table)
        return w

    def _build_browser_tab(self) -> QWidget:
        w = QWidget()
        tab_layout = QVBoxLayout(w)
        lbl_title = QLabel("📁 FORECAST OUTPUT BROWSER")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #00E6FF;")
        tab_layout.addWidget(lbl_title)

        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setText(
            "Outputs Available in /onm/dem/home/sfoura/ACF/outputs/:\n"
            "• ICMSHAROME+0048.fa (AROME 48h FA Format, 1.2 GB)\n"
            "• ARPEGE_GLOBAL_00Z_20260804.grib2 (GRIB2 0.1°, 3.4 GB)\n"
            "• wrfout_d01_2026-08-04_00:00:00.nc (NetCDF4 CF, 2.1 GB)\n"
            "• surfex_out.lfi (SURFEX Surface LFI Format, 450 MB)\n"
            "• AROME_T2M_20260804.tif (GeoTIFF Map Raster, 48 MB)"
        )
        tab_layout.addWidget(txt)
        return w
