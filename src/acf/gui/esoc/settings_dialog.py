"""ESOC Settings Dialog — application theme control (ACF-UI-013)."""

from typing import Any

from PySide6.QtWidgets import QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from acf.gui.theme import ThemeManager
from acf.gui_screen_utils import fit_dialog_to_screen


class SettingsDialog(QDialog):
    """Minimal settings dialog. Every control here does something real: the theme
    selector genuinely switches the live QApplication stylesheet via ThemeManager
    (acf/gui/resources/themes/{dark,light}.qss) - it does not merely display a choice."""

    def __init__(self, current_theme: str = "dark", parent: Any | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("⚙️ ESOC Settings")
        # NOTE (real responsive-sizing fix, 2026-09-05): was a hardcoded
        # self.resize(380, 160) - clamp to the actual screen instead, same
        # fix as gui_screen_utils.fit_window_to_screen for main windows.
        fit_dialog_to_screen(self, 380, 160)

        layout = QVBoxLayout(self)

        title = QLabel("⚙️ APPLICATION SETTINGS")
        title.setStyleSheet("font-weight: bold; font-size: 13px; color: #4FC3F7;")
        layout.addWidget(title)

        form = QFormLayout()
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["dark", "light"])
        self.combo_theme.setCurrentText(current_theme)
        form.addRow("Interface Theme:", self.combo_theme)
        layout.addLayout(form)

        note = QLabel("Applies immediately to the running application.")
        note.setStyleSheet("color: #9E9E9E; font-size: 9pt;")
        layout.addWidget(note)

        buttons = QHBoxLayout()
        btn_apply = QPushButton("Apply")
        btn_apply.clicked.connect(self._apply)
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        buttons.addStretch()
        buttons.addWidget(btn_apply)
        buttons.addWidget(btn_close)
        layout.addLayout(buttons)

    def _apply(self) -> None:
        from PySide6.QtWidgets import QApplication

        theme = ThemeManager()
        theme.set_theme(self.combo_theme.currentText())
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.setStyleSheet(theme.stylesheet())
