"""
Atmospheric Complexity Framework (ACF)

GUI - Property Panel

Purpose:
--------
PySide6 Qt GUI components, dock panels, map canvas controllers, and navigation.

Responsibilities:
-----------------
• Manage property panel logic and state representations.
• Integrate with the gui subsystem of the ACF scientific engine.

Major Components:
-----------------
• PropertyPanel

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.gui module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
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
