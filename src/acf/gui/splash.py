"""
Atmospheric Complexity Framework (ACF)

GUI - Splash

Purpose:
--------
PySide6 Qt GUI components, dock panels, map canvas controllers, and navigation.

Responsibilities:
-----------------
• Manage splash logic and state representations.
• Integrate with the gui subsystem of the ACF scientific engine.

Major Components:
-----------------
• SplashScreen

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.gui module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from acf import __version__


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ACF Loading")
        self.setFixedSize(600, 300)

        layout = QVBoxLayout(self)

        title = QLabel("Atmospheric Complexity Framework")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:24px;font-weight:bold;")

        # NOTE (correction): hardcoded "0.1.0-alpha" was stale - same
        # category of bug already fixed in dashboard/panels/status_panel.py,
        # ProductionUpdater and VersionManager.get_version() this session.
        # acf.__version__ is "0.1.0" (acf/core/version.py).
        version = QLabel(f"Version {__version__}")
        version.setAlignment(Qt.AlignCenter)

        status = QLabel("Initializing ACF...")
        status.setAlignment(Qt.AlignCenter)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(version)
        layout.addSpacing(20)
        layout.addWidget(status)
        layout.addStretch()
