"""
ACF Scientific Workstation — Command Palette
==============================================

Real, searchable Ctrl+K command list for `acf_workstation.
ACFWorkstation` (see that module's own docstring for the Workstation's
overall "ACF CORE ONLY - NO AWCI" rule). No new capability - every
command here already exists as a real button/shortcut somewhere else
in the chrome or a Lab panel; this dialog is purely a faster,
discoverable, fuzzy-searchable way to reach one of them, matching the
master spec's own design section, which explicitly names a Command
Palette (Ctrl+K) as a real UI element.

Non-modal, open-or-raise (`.show()`), not `.exec()`
-------------------------------------------------------
Same real convention already established elsewhere in this codebase
(e.g. `awci_execution_report_dialog.AWCIExecutionReportDialog`,
opened via `.show()`/`.raise_()`/`.activateWindow()`, never a blocking
`.exec()`) - keeps the dialog testable without a nested event loop and
lets the user keep the main window interactive alongside it.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QDialog, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout, QWidget


class CommandPaletteDialog(QDialog):
    """Real, fuzzy-filterable list of (label, callback) commands - see
    module docstring. `run_command(label)` is public so tests (and any
    other real caller) can execute a command directly, without
    depending on simulated key/mouse events to drive the search box
    and list widget."""

    def __init__(self, commands: list[tuple[str, Callable[[], None]]], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Command Palette")
        self.setModal(False)
        self._commands = commands

        layout = QVBoxLayout(self)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type a command…")
        self.search_input.textChanged.connect(self._filter)
        self.search_input.returnPressed.connect(self._activate_current)
        self.search_input.installEventFilter(self)
        layout.addWidget(self.search_input)

        self.result_list = QListWidget()
        self.result_list.itemActivated.connect(lambda item: self.run_command(item.text()))
        layout.addWidget(self.result_list)

        self.resize(420, 320)
        self._filter("")

    def set_commands(self, commands: list[tuple[str, Callable[[], None]]]) -> None:
        """Real, additive refresh point - not used internally today
        (this Workstation's own commands reference stable button/method
        references that never need rebuilding), kept public for a
        future real caller that wants to change the command set."""
        self._commands = commands
        self._filter(self.search_input.text())

    def _filter(self, text: str) -> None:
        self.result_list.clear()
        needle = text.strip().lower()
        for label, _callback in self._commands:
            if needle in label.lower():
                self.result_list.addItem(QListWidgetItem(label))
        if self.result_list.count() > 0:
            self.result_list.setCurrentRow(0)

    def _activate_current(self) -> None:
        item = self.result_list.currentItem()
        if item is not None:
            self.run_command(item.text())

    def run_command(self, label: str) -> None:
        """Real dispatch: run the real callback registered under
        `label` (a real, exact match - no fuzzy execution, only fuzzy
        LISTING, so a command never runs a different one than what's
        visibly highlighted) and close the palette."""
        for cmd_label, callback in self._commands:
            if cmd_label == label:
                callback()
                self.close()
                return

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        # Real Up/Down navigation while the search box has focus -
        # QListWidget never receives arrow keys typed into a sibling
        # QLineEdit by default, so this redirects them (standard Qt
        # command-palette pattern), leaving every other key untouched.
        if watched is self.search_input and event.type() == QEvent.Type.KeyPress:
            key = event.key()  # type: ignore[attr-defined]
            if key == Qt.Key.Key_Down:
                self.result_list.setCurrentRow(min(self.result_list.currentRow() + 1, self.result_list.count() - 1))
                return True
            if key == Qt.Key.Key_Up:
                self.result_list.setCurrentRow(max(self.result_list.currentRow() - 1, 0))
                return True
        return super().eventFilter(watched, event)
