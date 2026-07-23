from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class ChartPanel(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("📈 Scientific Charts")
        title.setStyleSheet("font-size:16px;font-weight:bold;")

        layout.addWidget(title)
        layout.addWidget(
            QLabel("Charts will appear here.")
        )
