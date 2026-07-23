"""
ACF System Status Panel
"""

from datetime import datetime

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class StatusPanel(QWidget):
    """
    Panneau d'état du système ACF.
    """

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("System Status")
        title.setStyleSheet("""
            font-size:16px;
            font-weight:bold;
        """)

        layout.addWidget(title)

        self.info = QLabel()

        self.info.setStyleSheet("""
            font-family:Consolas;
            font-size:11pt;
        """)

        layout.addWidget(self.info)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)

        self.update_status()

    #######################################################

    def update_status(self):

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        text = f"""
ACF Version : 0.1.0-alpha

Workspace   : Ready
Dashboard   : Ready

Loaded Data : None
Model       : None

Console     : Ready
Charts      : Ready
Timeline    : Ready

Current Time
{now}
"""

        self.info.setText(text)
