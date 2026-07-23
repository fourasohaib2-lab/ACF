from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

class MapView(QLabel):

    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.setText("Map View (Coming Soon)")
        self.setStyleSheet("""
            font-size:24px;
            border:1px solid gray;
        """)
