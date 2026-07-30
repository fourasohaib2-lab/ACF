"""
Atmospheric Complexity Framework (ACF)

GUI - Theme

Purpose:
--------
PySide6 Qt GUI components, dock panels, map canvas controllers, and navigation.

Responsibilities:
-----------------
• Manage theme logic and state representations.
• Integrate with the gui subsystem of the ACF scientific engine.

Major Components:
-----------------
• ThemeManager

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.gui module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from pathlib import Path

class ThemeManager:

    def __init__(self):
        self.theme = "dark"

    def stylesheet(self):

        root = Path(__file__).parent

        file = root / "resources" / "themes" / f"{self.theme}.qss"

        return file.read_text(encoding="utf-8")

    def set_theme(self, name):

        self.theme = name
