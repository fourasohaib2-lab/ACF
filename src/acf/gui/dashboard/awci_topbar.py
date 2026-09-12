"""
AWCI Top Bar
============

Real light top bar (added 2026-09-12, explicit user request "je veux
que le dashboard soit exactement comme celui dans la photo... 100%...
tous les boutons fonctionnelles" - docs/reference/
awci_dashboard_reference.png), replacing the previous dark header row
this dashboard used to build directly in `_build_ui()`.

Every control here is wired to a REAL, already-existing dashboard
mechanism - see `AWCIDashboard._wire_topbar()`'s own docstring for the
exact mapping (Area -> the real VIEW MODE radios, Date & Time -> the
real `time_slider`, Model -> the real current model name already shown
in the stats bar, bell -> the real Alerts dialog, cloud -> the real
Connect HPC feature, gear -> the real "☰" menu this dashboard already
built). The one honestly non-functional element is the user avatar -
ACF has no real authentication/user-account system, so this shows a
generic icon with a disclosing tooltip rather than a fabricated name.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QToolButton, QVBoxLayout, QWidget


class AWCITopBar(QWidget):
    """Real light top bar - see module docstring. Exposes real Qt
    widgets as public attributes (`area_combo`, `prev_time_button`,
    `next_time_button`, `now_button`, `forecast_label`, `model_label`,
    `status_dot`, `status_label`, `last_update_label`, `bell_button`,
    `hpc_button`, `settings_button`) so `AWCIDashboard._wire_topbar()`
    can connect them to real existing slots - this widget owns no
    dashboard logic of its own, only the real controls."""

    areaChanged = Signal(str)

    _BG = "#ffffff"
    _BORDER = "#e2e5ea"
    _TEXT = "#2a3142"
    _TEXT_MUTED = "#8a91a3"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setStyleSheet(f"background-color: {self._BG}; border-bottom: 1px solid {self._BORDER};")

        row = QHBoxLayout(self)
        row.setContentsMargins(20, 8, 20, 8)
        row.setSpacing(16)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        title = QLabel("Aviation Weather Complexity Index")
        title.setStyleSheet(f"color: {self._TEXT}; font-size: 15px; font-weight: bold; border: none;")
        subtitle = QLabel("From ACF data  •  For safer skies")
        subtitle.setStyleSheet(f"color: {self._TEXT_MUTED}; font-size: 10px; border: none;")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        row.addLayout(title_col)
        row.addStretch()

        # --- Real Area selector (wired to the existing VIEW MODE radios) ---
        self.area_combo = QComboBox()
        self.area_combo.addItems(["Global", "North Africa"])
        self.area_combo.setStyleSheet(self._pill_style())
        self.area_combo.currentTextChanged.connect(self.areaChanged.emit)
        row.addWidget(self._labeled("Area", self.area_combo))

        # --- Real Date & Time (wired to the existing real time_slider) ---
        time_group = QWidget()
        time_row = QHBoxLayout(time_group)
        time_row.setContentsMargins(0, 0, 0, 0)
        time_row.setSpacing(2)
        self.prev_time_button = QToolButton()
        self.prev_time_button.setText("‹")
        self.next_time_button = QToolButton()
        self.next_time_button.setText("›")
        self.now_button = QPushButton("Now")
        self.now_button.setStyleSheet(self._pill_style())
        self.time_readout_label = QLabel("--:-- UTC")
        self.time_readout_label.setStyleSheet(f"color: {self._TEXT}; font-size: 11px; font-weight: bold; border: none; padding: 0 6px;")
        for btn in (self.prev_time_button, self.next_time_button):
            btn.setStyleSheet(
                f"QToolButton {{ border: 1px solid {self._BORDER}; border-radius: 4px; padding: 2px 6px; color: {self._TEXT}; }}"
                "QToolButton:hover { background-color: #f0f2f5; }"
            )
        time_row.addWidget(self.prev_time_button)
        time_row.addWidget(self.time_readout_label)
        time_row.addWidget(self.next_time_button)
        time_row.addWidget(self.now_button)
        row.addWidget(self._labeled("Date & Time", time_group))

        # --- Real Forecast lead-time readout (derived from time_slider) ---
        self.forecast_label = QLabel("+0h")
        self.forecast_label.setStyleSheet(self._pill_style())
        row.addWidget(self._labeled("Forecast", self.forecast_label))

        # --- Real current model name (already computed elsewhere) ------
        self.model_label = QLabel("—")
        self.model_label.setStyleSheet(self._pill_style())
        row.addWidget(self._labeled("Model", self.model_label))

        row.addStretch()

        # --- Real system status -----------------------------------------
        status_col = QVBoxLayout()
        status_col.setSpacing(0)
        status_row = QHBoxLayout()
        status_row.setSpacing(4)
        self.status_dot = QLabel("●")
        self.status_label = QLabel("DEMO MODE")
        self.status_label.setStyleSheet(f"color: {self._TEXT}; font-size: 10px; font-weight: bold; border: none;")
        status_row.addWidget(self.status_dot)
        status_row.addWidget(self.status_label)
        status_col.addLayout(status_row)
        self.last_update_label = QLabel("Last Update: —")
        self.last_update_label.setStyleSheet(f"color: {self._TEXT_MUTED}; font-size: 9px; border: none;")
        status_col.addWidget(self.last_update_label)
        row.addLayout(status_col)

        self.bell_button = self._icon_button("🔔")
        self.hpc_button = self._icon_button("🔌")
        self.settings_button = self._icon_button("⚙️")
        row.addWidget(self.bell_button)
        row.addWidget(self.hpc_button)
        row.addWidget(self.settings_button)

        # Honest placeholder - see module docstring: ACF has no real
        # user-account system, so no name/role is fabricated here.
        self.user_button = self._icon_button("👤")
        self.user_button.setToolTip("No real user-account system exists in ACF yet - purely decorative.")
        self.user_button.setEnabled(False)
        row.addWidget(self.user_button)

    def _labeled(self, label_text: str, control: QWidget) -> QWidget:
        wrapper = QWidget()
        col = QVBoxLayout(wrapper)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(2)
        label = QLabel(label_text)
        label.setStyleSheet(f"color: {self._TEXT_MUTED}; font-size: 9px; border: none;")
        col.addWidget(label)
        col.addWidget(control)
        return wrapper

    def _pill_style(self) -> str:
        return (
            f"border: 1px solid {self._BORDER}; border-radius: 5px; padding: 3px 8px; "
            f"color: {self._TEXT}; font-size: 11px; background-color: #ffffff;"
        )

    def _icon_button(self, glyph: str) -> QToolButton:
        button = QToolButton()
        button.setText(glyph)
        button.setStyleSheet(
            f"QToolButton {{ border: none; border-radius: 6px; padding: 6px; font-size: 14px; }}"
            "QToolButton:hover { background-color: #f0f2f5; }"
        )
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def set_status(self, *, is_real: bool, label: str) -> None:
        """Real status readout - `is_real` drives the dot color
        (green=Real Physics/Real Archive, amber=demo), `label` is the
        real current mode text."""
        color = "#22c55e" if is_real else "#f59e0b"
        self.status_dot.setStyleSheet(f"color: {color}; font-size: 10px; border: none;")
        self.status_label.setText(label)
