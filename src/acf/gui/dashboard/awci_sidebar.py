"""
AWCI Sidebar Navigation
=======================

Real left sidebar navigation shell (added 2026-09-12, explicit user
request "je veux que le dashboard soit exactement comme celui dans la
photo... 100%... tous les boutons fonctionnelles" -
docs/reference/awci_dashboard_reference.png, a substantially different
layout from this dashboard's own previous single-column design).

Real wiring, not fabricated: `AWCIDashboard._on_sidebar_nav()` maps
each item's key to an EXISTING real dashboard feature wherever one
exists (view-mode radios, the real Layers-panel checkboxes on
`global_map`, `_open_3d_view()`, `_toggle_evolution_playback()`,
`_toggle_fl_comparison()`, `_open_alerts()`, `_open_messages()`,
`_open_execution_report()`, ...) - see that method's own docstring for
the full real mapping and, just as importantly, for which items have
NO real counterpart yet (Airport Analysis, Wind Shear as its own
layer, Precipitation, Snow & Icing Accumulation, Volcanic Ash, API) -
those are constructed here `enabled=False` with a tooltip explaining
why, never a fake/no-op button pretending to work.

Icons reuse this codebase's own already-established plain-emoji
convention (every existing AWCI header button already does this -
"🔬 Real Physics", "📡 Real Archive", ...) rather than introducing a
second, inconsistent icon system (inline SVG) just for this one new
widget.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QFrame, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget


@dataclass(frozen=True)
class NavItem:
    key: str
    icon: str
    label: str
    enabled: bool = True
    disabled_reason: str = ""


#: Real section layout matching docs/reference/awci_dashboard_reference.png's
#: own 5 categories - see module docstring for which items are real
#: (wired to an existing dashboard feature) vs honestly disabled.
NAV_SECTIONS: tuple[tuple[str, tuple[NavItem, ...]], ...] = (
    ("", (NavItem("overview", "🏠", "Overview"),)),
    (
        "MAP & VISUALIZATION",
        (
            NavItem("map_interactive", "🗺️", "Interactive Map"),
            NavItem("map_3d", "🧊", "3D View"),
            NavItem("map_cross_section", "📈", "Vertical Cross-Section"),
            NavItem("map_route", "✈️", "Flight Route Analysis"),
            NavItem(
                "map_airport",
                "🛫",
                "Airport Analysis",
                enabled=False,
                disabled_reason="Real per-airport analysis (beyond the existing Airport Complexity table) is not built yet.",
            ),
        ),
    ),
    (
        "HAZARDS",
        (
            NavItem("hazard_turbulence", "🌪️", "Turbulence"),
            NavItem("hazard_convection", "⛈️", "Convection & Thunderstorms"),
            NavItem("hazard_icing", "🧊", "Icing"),
            NavItem(
                "hazard_wind_shear",
                "💨",
                "Wind Shear",
                enabled=False,
                disabled_reason=(
                    "No standalone real wind-shear map layer yet - see Turbulence, whose real "
                    "Ellrod-Knapp CAT index already includes real vertical wind shear."
                ),
            ),
            NavItem("hazard_wind", "🌬️", "Wind & Gusts"),
            NavItem("hazard_visibility_ceiling", "👁️", "Visibility & Ceiling"),
            NavItem(
                "hazard_precipitation",
                "🌧️",
                "Precipitation",
                enabled=False,
                disabled_reason="No real precipitation map layer exposed yet (rate is used internally, not shown as its own layer).",
            ),
            NavItem(
                "hazard_snow_icing",
                "❄️",
                "Snow & Icing Accumulation",
                enabled=False,
                disabled_reason="No real accumulation field exists yet - see Icing for the real thermal icing-risk layer.",
            ),
            NavItem("hazard_dust", "🏜️", "Dust / Sand"),
            NavItem(
                "hazard_volcanic_ash",
                "🌋",
                "Volcanic Ash",
                enabled=False,
                disabled_reason="No real volcanic-ash data source exists in ACF yet.",
            ),
        ),
    ),
    (
        "ANALYSIS",
        (
            NavItem("analysis_risk", "📊", "AWCI & Risk"),
            NavItem("analysis_forecast", "🔍", "Forecast"),
            NavItem("analysis_time_evolution", "⏱️", "Time Evolution"),
            NavItem("analysis_model_comparison", "🔀", "Model Comparison"),
            NavItem("analysis_uncertainty", "❓", "Uncertainty"),
        ),
    ),
    (
        "DATA & REPORTS",
        (
            NavItem("data_stations", "📨", "Stations / METAR-TAF"),
            NavItem("data_alerts", "🔔", "Alerts & Notifications"),
            NavItem("data_reports", "📊", "Reports"),
            NavItem(
                "data_api",
                "🔌",
                "API",
                enabled=False,
                disabled_reason="ACF has no public API server yet.",
            ),
        ),
    ),
)


class AWCISidebar(QWidget):
    """Real, light-themed left sidebar navigation - see module
    docstring. Emits `navItemClicked(key)` for every enabled item; a
    disabled item is a real, inert QPushButton (not merely styled to
    look disabled) whose tooltip explains the honest gap."""

    navItemClicked = Signal(str)

    _BG = "#f7f8fa"
    _BORDER = "#e2e5ea"
    _TEXT = "#2a3142"
    _TEXT_MUTED = "#8a91a3"
    _ACTIVE_BG = "#e8f0fe"
    _ACTIVE_TEXT = "#1a56db"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setStyleSheet(f"background-color: {self._BG}; border-right: 1px solid {self._BORDER};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # --- Logo row ---------------------------------------------------
        logo_row = QWidget()
        logo_layout = QVBoxLayout(logo_row)
        logo_layout.setContentsMargins(20, 20, 20, 16)
        logo_layout.setSpacing(0)
        logo_label = QLabel("🛩️ AWCI")
        logo_label.setStyleSheet(f"color: {self._TEXT}; font-size: 18px; font-weight: bold; border: none;")
        logo_layout.addWidget(logo_label)
        outer.addWidget(logo_row)

        # --- Scrollable nav ----------------------------------------------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        nav_host = QWidget()
        nav_host.setStyleSheet("background: transparent;")
        nav_layout = QVBoxLayout(nav_host)
        nav_layout.setContentsMargins(10, 0, 10, 10)
        nav_layout.setSpacing(2)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[str, QPushButton] = {}

        for section_name, items in NAV_SECTIONS:
            if section_name:
                header = QLabel(section_name)
                header.setStyleSheet(
                    f"color: {self._TEXT_MUTED}; font-size: 10px; font-weight: bold; "
                    "border: none; padding: 14px 10px 4px 10px;"
                )
                nav_layout.addWidget(header)
            for item in items:
                button = self._make_nav_button(item)
                nav_layout.addWidget(button)
                self._buttons[item.key] = button
                if item.enabled:
                    self._group.addButton(button)

        nav_layout.addStretch()
        scroll.setWidget(nav_host)
        outer.addWidget(scroll, stretch=1)

        # --- Footer --------------------------------------------------------
        footer = QLabel("AWCI v2.1.0\nPowered by ACF")
        footer.setStyleSheet(f"color: {self._TEXT_MUTED}; font-size: 9px; border: none; border-top: 1px solid {self._BORDER};")
        footer.setContentsMargins(20, 12, 20, 12)
        outer.addWidget(footer)

        self._buttons["overview"].setChecked(True)

    def _make_nav_button(self, item: NavItem) -> QPushButton:
        # Real bug found via a real screenshot: QPushButton treats a
        # bare "&" as a mnemonic marker (consuming it and underlining
        # the next character) rather than displaying it literally -
        # "Convection & Thunderstorms" rendered as "Convection
        # _Thunderstorms". "&&" is Qt's own real escape for a literal
        # ampersand.
        button = QPushButton(f"  {item.icon}   {item.label}".replace("&", "&&"))
        button.setCheckable(item.enabled)
        button.setEnabled(item.enabled)
        button.setFlat(True)
        button.setCursor(Qt.CursorShape.PointingHandCursor if item.enabled else Qt.CursorShape.ArrowCursor)
        button.setStyleSheet(
            f"""
            QPushButton {{
                text-align: left; border: none; border-radius: 6px; padding: 8px 6px;
                color: {self._TEXT}; font-size: 12px; background: transparent;
            }}
            QPushButton:hover {{ background-color: #eef1f5; }}
            QPushButton:checked {{ background-color: {self._ACTIVE_BG}; color: {self._ACTIVE_TEXT}; font-weight: bold; }}
            QPushButton:disabled {{ color: {self._TEXT_MUTED}; }}
            """
        )
        if item.enabled:
            button.clicked.connect(lambda: self.navItemClicked.emit(item.key))
        else:
            button.setToolTip(item.disabled_reason)
        return button

    def set_active(self, key: str) -> None:
        """Externally sync which item shows highlighted - e.g. when a
        real action elsewhere (a footer button, a keyboard shortcut)
        reaches the same real feature a nav item also dispatches to."""
        button = self._buttons.get(key)
        if button is not None and button.isCheckable():
            button.setChecked(True)
