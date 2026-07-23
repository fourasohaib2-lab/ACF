from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QSizePolicy,
)


class MapView(QWidget):
    """
    Main scientific map area.

    This widget will later host:
      - Cartopy
      - Matplotlib
      - OpenGL
      - Satellite imagery
      - Radar
      - GRIB / NetCDF rendering
      - Interactive layers
    """

    def __init__(self):
        super().__init__()

        self._build_ui()

    def _build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.placeholder = QLabel(
            "🌍 Atmospheric Complexity Framework\n\n"
            "Interactive Map Workspace"
        )

        self.placeholder.setAlignment(Qt.AlignCenter)

        self.placeholder.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        self.placeholder.setStyleSheet("""
            background-color: #1e1e1e;
            color: white;
            font-size: 28px;
            font-weight: bold;
            border: none;
        """)

        layout.addWidget(self.placeholder)

    def clear(self):
        self.placeholder.setText("")

    def set_message(self, text: str):
        self.placeholder.setText(text)
