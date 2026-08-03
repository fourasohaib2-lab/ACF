
"""
AWCI Gauge Widget
=================

Circular gauge displaying AWCI score with needle.
"""

import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QConicalGradient

from typing import Optional


class AWCIGauge(QWidget):
    """Circular gauge widget for AWCI score (0-100)."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._score = 0.0
        self._target_score = 0.0
        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self._animate)
        self._animation_timer.setInterval(16)
        self._animating = False

        self.levels = [
            (0, "Very Low", QColor(0, 200, 100)),
            (20, "Low", QColor(100, 200, 50)),
            (35, "Moderate", QColor(255, 200, 0)),
            (50, "High", QColor(255, 150, 0)),
            (65, "Very High", QColor(255, 100, 0)),
            (85, "Extreme", QColor(255, 0, 0)),
        ]

        self.setMinimumSize(180, 180)
        self.setStyleSheet("background: transparent;")

    def set_score(self, score: float, animate: bool = True):
        """Set AWCI score (0-100)."""
        self._target_score = max(0.0, min(100.0, score))
        if animate:
            self._animating = True
            self._animation_timer.start()
        else:
            self._score = self._target_score
            self.update()

    def _animate(self):
        """Animate needle."""
        diff = self._target_score - self._score
        if abs(diff) < 0.1:
            self._score = self._target_score
            self._animating = False
            self._animation_timer.stop()
            self.update()
            return
        self._score += diff * 0.15
        self.update()

    def _get_level_and_color(self, score: float) -> tuple:
        for threshold, level, color in reversed(self.levels):
            if score >= threshold:
                return level, color
        return self.levels[0][1], self.levels[0][2]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        size = min(rect.width(), rect.height()) - 20
        center = rect.center()

        # Background
        painter.setBrush(QBrush(QColor(30, 30, 50)))
        painter.setPen(QPen(QColor(50, 50, 80), 2))
        painter.drawEllipse(center, size // 2, size // 2)

        # Arc
        start_angle = 135
        span_angle = 270

        for i in range(len(self.levels) - 1):
            threshold_start = self.levels[i][0]
            threshold_end = self.levels[i + 1][0]
            color_start = self.levels[i][2]
            color_end = self.levels[i + 1][2]

            angle_start = start_angle + (threshold_start / 100) * span_angle
            angle_end = start_angle + (threshold_end / 100) * span_angle

            gradient = QConicalGradient(center, angle_start)
            gradient.setColorAt(0.0, color_start)
            gradient.setColorAt(1.0, color_end)

            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(Qt.NoPen))
            painter.drawPie(
                rect.adjusted(10, 10, -10, -10),
                int(angle_start * 16),
                int((angle_end - angle_start) * 16)
            )

        # Inner circle
        painter.setBrush(QBrush(QColor(20, 20, 40)))
        painter.setPen(QPen(QColor(50, 50, 80), 1))
        painter.drawEllipse(center, size // 2 - 20, size // 2 - 20)

        # Needle
        angle = start_angle + (self._score / 100) * span_angle
        angle_rad = angle * math.pi / 180

        needle_length = size // 2 - 25
        needle_x = center.x() + needle_length * 0.7 * math.cos(angle_rad)
        needle_y = center.y() + needle_length * 0.7 * math.sin(angle_rad)

        painter.setPen(QPen(QColor(255, 255, 255), 3))
        painter.drawLine(center, int(needle_x), int(needle_y))

        # Center dot
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QPen(Qt.NoPen))
        painter.drawEllipse(center, 8, 8)

        # Score
        level, color = self._get_level_and_color(self._score)
        painter.setPen(QPen(color, 1))
        font = painter.font()
        font.setPointSize(22)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            center.x() - 30, center.y() + 10,
            60, 40,
            Qt.AlignCenter,
            f"{int(self._score)}"
        )

        # Level
        font.setPointSize(9)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QPen(QColor(180, 180, 200), 1))
        painter.drawText(
            center.x() - 50, center.y() + 50,
            100, 20,
            Qt.AlignCenter,
            level
        )

        painter.end()

    def sizeHint(self):
        return self.minimumSize()
