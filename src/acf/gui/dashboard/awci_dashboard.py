"""
AWCI Dashboard
==============

Full "AWCI - Aviation Weather Complexity Index" operational dashboard,
matching the reference concept mockup: global map, vertical cross-section,
component radar, regional map, route planning, risk summary, stats bar and
footer. Every AWCI number shown is the real output of
acf.awci.calculator.AWCICalculator; only the underlying meteorological
input fields are a synthetic demo pattern (see awci_synthetic_field.py's
docstring) - exactly the "Concept Output - Research Prototype" framing the
reference mockup itself uses.
"""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget

from acf.gui.dashboard.awci_cross_section import AWCICrossSection
from acf.gui.dashboard.awci_footer import AWCIFooter
from acf.gui.dashboard.awci_map_panel import AWCIMapPanel
from acf.gui.dashboard.awci_radar import AWCIRadar
from acf.gui.dashboard.awci_risk_summary import AWCIRiskSummary
from acf.gui.dashboard.awci_route_chart import AWCIRouteChart
from acf.gui.dashboard.awci_stats_bar import AWCIStatsBar
from acf.gui.dashboard.awci_synthetic_field import awci_at, awci_grid

# Reference-style demo route/point of interest: JFK -> CDG (global map / cross-section)
_GLOBAL_ROUTE = [(40.64, -73.78, "JFK"), (49.01, 2.55, "CDG")]
# Regional demo route: within the North Africa regional map extent
_REGIONAL_ROUTE = [(36.75, 3.06, "Alger"), (32.90, 13.19, "Tripoli")]
_REGIONAL_EXTENT = (-12.0, 35.0, 15.0, 40.0)  # lon_min, lon_max, lat_min, lat_max
_POINT_OF_INTEREST = (34.5, 12.3)  # matches the reference's example point (lat, lon)


class _ComponentValueList(QFrame):
    """Compact list of module scores next to the radar - mirrors the reference's
    numeric readout ('Dynamic 0.72', 'Thermodynamic 0.81', ...) alongside its radar."""

    _LABELS = [
        ("dynamic", "🌀", "Dynamic"),
        ("thermodynamic", "🌡️", "Thermodynamic"),
        ("convective", "⛈️", "Convective"),
        ("microphysical", "❄️", "Microphysical"),
        ("topographic", "⛰️", "Topographic"),
        ("temporal", "🕐", "Temporal"),
        ("confidence", "❓", "Uncertainty"),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("border: none;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(4)

        self._values: dict[str, QLabel] = {}
        for key, icon, label in self._LABELS:
            row = QHBoxLayout()
            lbl = QLabel(f"{icon}  {label}")
            lbl.setStyleSheet("color: #c0c8d8; font-size: 10px;")
            row.addWidget(lbl)
            row.addStretch()
            value = QLabel("—")
            value.setStyleSheet("color: #e0e0e0; font-size: 10px; font-weight: bold;")
            row.addWidget(value)
            layout.addLayout(row)
            self._values[key] = value

    def update_data(self, module_scores: dict[str, float]) -> None:
        for key, _icon, _label in self._LABELS:
            value = module_scores.get(key, 0.0) / 100.0  # display as a 0-1 fraction, like the reference
            self._values[key].setText(f"{value:.2f}")


class AWCIDashboard(QWidget):
    """Complete AWCI operational dashboard."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._apply_theme()
        self.refresh()

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setSpacing(8)
        outer.setContentsMargins(10, 10, 10, 0)

        header = QLabel("AWCI – AVIATION WEATHER COMPLEXITY INDEX")
        header.setStyleSheet("color: #e0e0e0; font-size: 18px; font-weight: bold;")
        outer.addWidget(header)

        subheader = QLabel("Concept Output – Research Prototype")
        subheader.setStyleSheet("color: #8090a8; font-size: 11px;")
        outer.addWidget(subheader)

        # --- Row 1: global map (left) + cross-section & radar (right) -----
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        self.global_map = AWCIMapPanel("AWCI GLOBAL MAP (FL300)")
        self.global_map.set_flight_path(_GLOBAL_ROUTE)
        row1.addWidget(self.global_map, stretch=3)

        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        self.cross_section = AWCICrossSection()
        right_col.addWidget(self.cross_section, stretch=1)

        radar_row = QHBoxLayout()
        self.radar = AWCIRadar("AWCI COMPONENTS (example at point)")
        self.component_list = _ComponentValueList()
        radar_row.addWidget(self.radar, stretch=2)
        radar_row.addWidget(self.component_list, stretch=1)
        right_col.addLayout(radar_row, stretch=1)

        row1.addLayout(right_col, stretch=2)
        outer.addLayout(row1, stretch=3)

        # --- Stats bar -----------------------------------------------------
        self.stats_bar = AWCIStatsBar()
        outer.addWidget(self.stats_bar)

        # --- Row 2: regional map (left) + route/risk (right) --------------
        row2 = QHBoxLayout()
        row2.setSpacing(8)

        left_col2 = QVBoxLayout()
        self.regional_map = AWCIMapPanel("AWCI REGIONAL MAP – NORTH AFRICA (FL100)", extent=_REGIONAL_EXTENT)
        self.regional_map.set_flight_path(_REGIONAL_ROUTE)
        self.regional_map.set_point_marker(*_POINT_OF_INTEREST)
        left_col2.addWidget(self.regional_map, stretch=1)

        time_row = QHBoxLayout()
        time_label = QLabel("Valid Time:")
        time_label.setStyleSheet("color: #8090a8; font-size: 9px;")
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(23)
        self.time_slider.setValue(12)
        self.time_slider.sliderReleased.connect(self._on_time_changed)
        self.time_readout = QLabel("12Z")
        self.time_readout.setStyleSheet("color: #e0e0e0; font-size: 9px; font-weight: bold;")
        self.time_slider.valueChanged.connect(lambda v: self.time_readout.setText(f"{v:02d}Z"))
        time_row.addWidget(time_label)
        time_row.addWidget(self.time_slider, stretch=1)
        time_row.addWidget(self.time_readout)
        left_col2.addLayout(time_row)

        row2.addLayout(left_col2, stretch=3)

        right_col2 = QVBoxLayout()
        right_col2.setSpacing(8)
        op_header = QLabel("AWCI – OPERATIONAL USE EXAMPLE")
        op_header.setStyleSheet("color: #d0d8e8; font-size: 10px; font-weight: bold;")
        right_col2.addWidget(op_header)

        op_row = QHBoxLayout()
        self.route_chart = AWCIRouteChart()
        self.risk_summary = AWCIRiskSummary()
        op_row.addWidget(self.route_chart, stretch=2)
        op_row.addWidget(self.risk_summary, stretch=1)
        right_col2.addLayout(op_row, stretch=1)

        row2.addLayout(right_col2, stretch=2)
        outer.addLayout(row2, stretch=2)

        # --- Footer ---------------------------------------------------------
        self.footer = AWCIFooter()
        outer.addWidget(self.footer)

    def _apply_theme(self) -> None:
        self.setStyleSheet("""
            QWidget {
                background-color: #0d1b2a;
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
        """)

    # ------------------------------------------------------------- refresh

    def _on_time_changed(self) -> None:
        """Re-render the regional map with a genuinely shifted synthetic-pattern
        phase for the selected hour (see awci_synthetic_field.py's time_offset_hours) -
        the slider moves the pattern, it does not silently change anything else."""
        self.regional_map.update_data(flight_level_hpa=700.0, time_offset_hours=float(self.time_slider.value()))

    def refresh(self) -> None:
        """(Re)compute every panel from the real AWCICalculator (see module docstring)."""
        self.cross_section.update_data(_GLOBAL_ROUTE[0][:2], _GLOBAL_ROUTE[1][:2], cruise_hpa=300.0)

        point_result = awci_at(*_POINT_OF_INTEREST, flight_level_hpa=300.0)
        self.radar.update_data(point_result["module_scores"])
        self.component_list.update_data(point_result["module_scores"])

        _lons, _lats, grid = awci_grid(lat_step=4.0, lon_step=4.0, flight_level_hpa=300.0)
        flat_scores = [v for row in grid for v in row]
        self.stats_bar.update_data(flat_scores, confidence_pct=point_result["confidence"])

        route_scores = self.route_chart.update_data(_REGIONAL_ROUTE[0][:2], _REGIONAL_ROUTE[1][:2], cruise_hpa=850.0)
        overall_awci = max(route_scores) if route_scores is not None else point_result["awci"]
        # physical_score/forecast_score are for the point of interest, not
        # the route's worst point (unlike overall_awci above) - route-level
        # aggregation of the split scores is future work, not simulated
        # here.
        self.risk_summary.update_data(
            point_result["module_scores"],
            overall_awci,
            physical_score=point_result["physical_score"],
            forecast_score=point_result["forecast_score"],
        )

    # ---------------------------------------------------- external API

    def update_with_awci_result(self, result: dict[str, Any]) -> None:
        """Update the components radar/list with an externally-supplied AWCICalculator result."""
        self.radar.update_data(result.get("module_scores", {}))
        self.component_list.update_data(result.get("module_scores", {}))

    def set_data(self, awci_result: dict[str, Any]) -> None:
        self.update_with_awci_result(awci_result)
