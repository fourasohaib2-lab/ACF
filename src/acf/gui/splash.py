"""
acf.gui.splash - SplashScreen, the real startup splash screen.

Verified 2026-09-06: used by acf.gui.app at application startup.
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
