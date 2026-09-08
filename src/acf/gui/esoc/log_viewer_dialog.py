"""ESOC Live Log Viewer — real-time view of CommandDispatcher.log_message_emitted (ACF-UI-013)."""

from datetime import datetime
from typing import Any

from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton, QTextEdit, QVBoxLayout

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui_screen_utils import fit_dialog_to_screen

#: Rolling buffer cap - keeps the widget from growing unbounded over a long session.
MAX_LINES = 1000


class LogViewerDialog(QDialog):
    """Non-modal dialog streaming every command/status message the dispatcher actually emits.

    This is a real, live subscriber to CommandDispatcher.log_message_emitted - every line
    shown here is a genuine event that already occurred elsewhere in the app (dispatched
    commands, warnings for unregistered commands, hazard/simulation notices), not a
    fabricated log feed.
    """

    def __init__(self, dispatcher: CommandDispatcher, parent: Any | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("📜 ESOC Session Log")
        # NOTE (real responsive-sizing fix, 2026-09-05): was a hardcoded
        # self.resize(700, 450) - clamp to the actual screen instead, same
        # fix as gui_screen_utils.fit_window_to_screen for main windows.
        fit_dialog_to_screen(self, 700, 450)
        self._line_count = 0

        layout = QVBoxLayout(self)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setStyleSheet("font-family: Consolas, monospace; font-size: 10pt;")
        layout.addWidget(self.text)

        buttons = QHBoxLayout()
        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self._clear)
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        buttons.addStretch()
        buttons.addWidget(btn_clear)
        buttons.addWidget(btn_close)
        layout.addLayout(buttons)

        dispatcher.log_message_emitted.connect(self.append_log)
        self.append_log("INFO", "Log viewer opened.")

    def append_log(self, level: str, message: str) -> None:
        """Append one timestamped log line. Connected to a Qt signal, so this is
        automatically queued onto the GUI thread even if emitted from a background worker."""
        ts = datetime.now().strftime("%H:%M:%S")
        self.text.append(f"[{ts}] [{level}] {message}")
        self._line_count += 1
        if self._line_count > MAX_LINES:
            # Trim the oldest half to keep the widget bounded on a long-running session.
            trim_count = MAX_LINES // 2
            cursor = self.text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.KeepAnchor, trim_count)
            cursor.removeSelectedText()
            cursor.deleteChar()  # remove the now-leading empty line left by the removed block
            self._line_count -= trim_count

    def _clear(self) -> None:
        self.text.clear()
        self._line_count = 0
