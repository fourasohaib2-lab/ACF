"""ESOC Top Master Operational Toolbar (ACF-UI-013)."""

from typing import Callable, Optional
from PySide6.QtWidgets import QToolBar, QComboBox, QLabel, QWidget, QHBoxLayout
from PySide6.QtGui import QAction
from acf.gui.esoc.esoc_workspace import WorkspaceMode


class ESOCToolbar(QToolBar):
    """Top operational toolbar for action buttons and workspace mode selection."""

    def __init__(
        self,
        on_action_callback: Optional[Callable[[str], None]] = None,
        on_mode_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        super().__init__("ESOC Master Operational Toolbar")
        self.on_action_callback = on_action_callback
        self.on_mode_callback = on_mode_callback

        self.setMovable(False)

        actions = [
            ("📂 Open Dataset", "open_dataset"),
            ("📡 Live Stream", "live_stream"),
            ("🔮 Forecast", "trigger_forecast"),
            ("🚀 Simulation", "trigger_sim"),
            ("🔄 Assimilation", "trigger_da"),
            ("🌐 Digital Twin", "trigger_twin"),
            ("🌡️ Climate", "trigger_climate"),
            ("⚠️ Hazards", "trigger_hazards"),
            ("🧠 AI", "trigger_ai"),
            ("💾 Export", "export_data"),
            ("📷 Screenshot", "take_screenshot"),
            ("🎬 Movie", "render_movie"),
            ("⚙️ Settings", "open_settings"),
            ("❓ Help", "open_help"),
        ]

        for label, cmd in actions:
            act = QAction(label, self)
            act.triggered.connect(lambda checked=False, c=cmd: self._trigger_action(c))
            self.addAction(act)

        self.addSeparator()

        mode_container = QWidget()
        m_layout = QHBoxLayout(mode_container)
        m_layout.setContentsMargins(4, 0, 4, 0)

        lbl_mode = QLabel("Workspace Mode: ")
        lbl_mode.setStyleSheet("font-weight: bold; color: #81D4FA;")
        m_layout.addWidget(lbl_mode)

        self.combo_mode = QComboBox()
        for mode in WorkspaceMode:
            self.combo_mode.addItem(mode.value)

        self.combo_mode.currentTextChanged.connect(self._on_mode_changed)
        m_layout.addWidget(self.combo_mode)

        self.addWidget(mode_container)

    def _trigger_action(self, cmd: str) -> None:
        if self.on_action_callback:
            self.on_action_callback(cmd)

    def _on_mode_changed(self, mode_str: str) -> None:
        if self.on_mode_callback:
            self.on_mode_callback(mode_str)
