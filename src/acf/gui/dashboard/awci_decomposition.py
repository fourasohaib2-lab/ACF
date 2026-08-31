"""
AWCI Decomposition Widget
=========================

Bar chart showing AWCI decomposition by module.
"""

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class AWCIDecomposition(QWidget):
    """Widget displaying AWCI decomposition as horizontal bars."""

    MODULE_COLORS = {
        "dynamic": QColor(66, 133, 244),  # Blue
        "thermodynamic": QColor(234, 67, 53),  # Red
        "convective": QColor(251, 188, 5),  # Yellow
        "microphysical": QColor(52, 168, 83),  # Green
        "topographic": QColor(156, 39, 176),  # Purple
        "temporal": QColor(255, 152, 0),  # Orange
        "confidence": QColor(0, 188, 212),  # Cyan
    }

    MODULE_LABELS = {
        "dynamic": "Dynamic Complexity",
        "thermodynamic": "Thermodynamic Complexity",
        "convective": "Convective Complexity",
        "microphysical": "Microphysical Complexity",
        "topographic": "Topographic Complexity",
        "temporal": "Temporal Complexity",
        "confidence": "Uncertainty",
    }

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._decomposition: dict[str, float] = {}
        self._title = "AWCI Components"
        self.setMinimumSize(280, 250)
        self.setStyleSheet("background: transparent;")

    def set_decomposition(self, decomposition: dict[str, float]):
        self._decomposition = decomposition
        self.update()

    def set_title(self, title: str):
        self._title = title
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        width = rect.width() - 20
        height = rect.height()

        # Title
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor(200, 200, 220), 1))
        painter.drawText(10, 20, self._title)

        if not self._decomposition:
            painter.setPen(QPen(QColor(100, 100, 130), 1))
            painter.drawText(10, height // 2, "No data")
            painter.end()
            return

        # Sort by value descending
        items = sorted(self._decomposition.items(), key=lambda x: x[1], reverse=True)

        bar_height = min(22, (height - 40) // len(items))
        bar_spacing = 4
        start_y = 35

        font.setPointSize(8)
        font.setBold(False)
        painter.setFont(font)

        for i, (key, value) in enumerate(items):
            y = start_y + i * (bar_height + bar_spacing)
            bar_width = (value / 100) * (width - 120)

            color = self.MODULE_COLORS.get(key, QColor(150, 150, 150))
            label = self.MODULE_LABELS.get(key, key)

            # Bar
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawRect(10, y, int(bar_width), bar_height)

            # Label
            painter.setPen(QPen(QColor(200, 200, 220), 1))
            painter.drawText(
                10, y, 100, bar_height, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, label
            )

            # Value
            painter.setPen(QPen(QColor(200, 200, 220), 1))
            painter.drawText(
                10 + int(bar_width) + 5,
                y,
                40,
                bar_height,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                f"{int(value)}%",
            )

        painter.end()

    def sizeHint(self):
        return QSize(300, 250)
