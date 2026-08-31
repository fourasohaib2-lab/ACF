"""
AWCI Timeline Widget
====================
"""

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPolygon
from PySide6.QtWidgets import QWidget


class AWCITimeline(QWidget):
    """Timeline showing AWCI evolution over time."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._data: list[tuple[str, float]] = []
        self._forecast_start: int | None = None
        self._title = "Évolution AWCI"
        self.setMinimumSize(300, 150)
        self.setStyleSheet("background: transparent;")

    def set_data(self, data: list[tuple[str, float]], forecast_start: int | None = None):
        self._data = data
        self._forecast_start = forecast_start
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        width = rect.width()
        height = rect.height()

        # Title
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor(200, 200, 220), 1))
        painter.drawText(10, 20, self._title)

        if not self._data:
            painter.setPen(QPen(QColor(100, 100, 130), 1))
            painter.drawText(10, height // 2, "Aucune donnée")
            painter.end()
            return

        margin_left = 40
        margin_right = 20
        margin_top = 35
        margin_bottom = 25

        plot_width = width - margin_left - margin_right
        plot_height = height - margin_top - margin_bottom

        if plot_width < 10 or plot_height < 10:
            painter.end()
            return

        scores = [s for _, s in self._data]
        max_score = max(100, max(scores) + 10)

        # Grid lines
        painter.setPen(QPen(QColor(50, 50, 80), 1, Qt.PenStyle.DashLine))
        font.setPointSize(7)
        painter.setFont(font)
        for grid_score in [25, 50, 75]:
            y = margin_top + plot_height - (grid_score / max_score) * plot_height
            painter.drawLine(margin_left, int(y), width - margin_right, int(y))
            painter.setPen(QPen(QColor(100, 100, 130), 1))
            painter.drawText(5, int(y) + 4, 30, 12, Qt.AlignmentFlag.AlignRight, f"{grid_score}")

        # Points
        points = []
        for i, (_label, score) in enumerate(self._data):
            x = margin_left + (i / max(1, len(self._data) - 1)) * plot_width
            y = margin_top + plot_height - (score / max_score) * plot_height
            points.append(QPoint(int(x), int(y)))

        # Fill area under curve (polygon)
        if len(points) >= 2:
            polygon = points + [
                QPoint(points[-1].x(), margin_top + plot_height),
                QPoint(points[0].x(), margin_top + plot_height),
            ]
            painter.setBrush(QBrush(QColor(66, 133, 244, 50)))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawPolygon(QPolygon(polygon))

        # Draw line
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        if self._forecast_start is not None and 0 < self._forecast_start < len(points):
            # Historical (solid)
            painter.setPen(QPen(QColor(66, 133, 244), 2))
            for i in range(self._forecast_start - 1):
                painter.drawLine(points[i], points[i + 1])
            # Forecast (dashed)
            painter.setPen(QPen(QColor(255, 100, 100), 2, Qt.PenStyle.DashLine))
            for i in range(self._forecast_start - 1, len(points) - 1):
                painter.drawLine(points[i], points[i + 1])
        else:
            painter.setPen(QPen(QColor(66, 133, 244), 2))
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])

        # Data points
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        for i, p in enumerate(points):
            if self._forecast_start is not None and i >= self._forecast_start:
                painter.setBrush(QBrush(QColor(255, 100, 100)))
            else:
                painter.setBrush(QBrush(QColor(66, 133, 244)))
            painter.drawEllipse(p, 3, 3)

        # Time labels
        painter.setPen(QPen(QColor(150, 150, 180), 1))
        font.setPointSize(6)
        painter.setFont(font)
        step = max(1, len(self._data) // 8)
        for i, (label, _) in enumerate(self._data):
            if i % step == 0 or i == len(self._data) - 1:
                x = margin_left + (i / max(1, len(self._data) - 1)) * plot_width
                painter.drawText(
                    int(x) - 15, margin_top + plot_height + 12, 30, 12, Qt.AlignmentFlag.AlignCenter, label
                )

        painter.end()
