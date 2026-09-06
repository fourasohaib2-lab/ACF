"""
acf.gui.widgets.property_panel - PropertyPanel, the real property panel.

Verified 2026-09-06: used by acf.dashboard.layout (not to be confused
with the empty acf.gui.docks.property_panel.py stub - see that
package's own docstring).
"""

from PySide6.QtWidgets import (
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class PropertyPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Properties")
        title.setStyleSheet("""
            font-size:16px;
            font-weight:bold;
        """)

        self.editor = QTextEdit()
        self.editor.setReadOnly(True)

        self.editor.setPlainText("No object selected.")

        layout.addWidget(title)
        layout.addWidget(self.editor)

    def set_properties(self, text):
        self.editor.setPlainText(text)
