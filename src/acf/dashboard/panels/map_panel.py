from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class MapPanel(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("🌍 Main Map")
        title.setStyleSheet("font-size:18px;font-weight:bold;")

        placeholder = QLabel(
            "Interactive map will appear here."
        )

        placeholder.setMinimumHeight(500)

        layout.addWidget(title)
        layout.addWidget(placeholder)
