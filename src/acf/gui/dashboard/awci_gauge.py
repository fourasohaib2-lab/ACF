"""
AWCI Gauge Widget
=================

Circular gauge displaying AWCI score with needle.

NOTE (found, NOT changed - RÈGLE D'OR / single source of truth): as of the
AWCI dashboard rebuild (awci_dashboard.py), this widget is no longer
instantiated by anything - the rebuilt AWCIDashboard uses AWCIRadar instead
of AWCIGauge + AWCIDecomposition for the components view, to match the
reference mockup's radar chart. Still re-exported by this package's
__init__.py and fully correct/self-contained, just currently unreachable
from any real UI. Not deleted per project convention - flagged so nobody
mistakes it for live code. Same situation as data/engine.py's NOTE.

Half-circle mode (added 2026-09-03, docs/reference/awci_dashboard_reference.jpg
parity work): the mockup's own "FORECAST CONFIDENCE" gauge is a half-circle
band (green/yellow/red), unlike this widget's original ~270 degree arc -
`half_circle=True` reuses the exact same real arc-drawing/needle code with
`start_angle=180, span_angle=180` instead of inventing a second gauge
widget. First real, live use of this class since the dashboard rebuild
above - mounted in AWCIStatsBar fed by the SAME real
AWCICalculator.calculate()['confidence'] value already computed there,
never a second/fabricated number.
"""

import math

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QConicalGradient, QPainter, QPen
from PySide6.QtWidgets import QWidget


class AWCIGauge(QWidget):
    """Circular (or half-circle) gauge widget for a 0-100 score."""

    def __init__(self, parent: QWidget | None = None, half_circle: bool = False):
        super().__init__(parent)

        self._score = 0.0
        self._target_score = 0.0
        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self._animate)
        self._animation_timer.setInterval(16)
        self._animating = False
        self._half_circle = half_circle
        # Real arc geometry - see module docstring's "Half-circle mode"
        # note for why half_circle reuses this same drawing code rather
        # than a second widget.
        self._start_angle = 180 if half_circle else 135
        self._span_angle = 180 if half_circle else 270

        self.levels = [
            (0, "Very Low", QColor(0, 200, 100)),
            (20, "Low", QColor(100, 200, 50)),
            (35, "Moderate", QColor(255, 200, 0)),
            (50, "High", QColor(255, 150, 0)),
            (65, "Very High", QColor(255, 100, 0)),
            (85, "Extreme", QColor(255, 0, 0)),
        ]

        self.setMinimumSize(180, 100 if half_circle else 180)
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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        if self._half_circle:
            # Real geometry for a half-circle gauge (see module
            # docstring): diameter limited by BOTH the available width
            # and twice the available height (only the top half is
            # ever drawn), pivot at the bottom-center so the arc reads
            # as a real speedometer band, not a circle cut in half.
            size = min(rect.width() - 20, 2 * (rect.height() - 20))
            center = QPoint(rect.center().x(), rect.bottom() - 10)
        else:
            size = min(rect.width(), rect.height()) - 20
            center = rect.center()

        if not self._half_circle:
            # Background - only drawn for the full-circle gauge; a
            # half-circle gauge shows just the arc band itself (see
            # module docstring), never a dark half-disc behind it.
            painter.setBrush(QBrush(QColor(30, 30, 50)))
            painter.setPen(QPen(QColor(50, 50, 80), 2))
            painter.drawEllipse(center, size // 2, size // 2)

        # Arc
        start_angle = self._start_angle
        span_angle = self._span_angle

        arc_rect = (
            rect.adjusted(rect.width() // 2 - size // 2, rect.height() - size - 10, -(rect.width() // 2 - size // 2), -10)
            if self._half_circle
            else rect.adjusted(10, 10, -10, -10)
        )

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
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawPie(arc_rect, int(angle_start * 16), int((angle_end - angle_start) * 16))

        if not self._half_circle:
            # Inner circle
            painter.setBrush(QBrush(QColor(20, 20, 40)))
            painter.setPen(QPen(QColor(50, 50, 80), 1))
            painter.drawEllipse(center, size // 2 - 20, size // 2 - 20)
        else:
            # Inner cutout - same donut-ring look as the full-circle
            # gauge, confined to the visible half via arc_rect above.
            inner_rect = arc_rect.adjusted(18, 18, -18, 0)
            painter.setBrush(QBrush(QColor(20, 20, 40)))
            painter.setPen(QPen(QColor(50, 50, 80), 1))
            painter.drawPie(inner_rect, int(start_angle * 16), int(span_angle * 16))

        # Needle
        angle = start_angle + (self._score / 100) * span_angle
        angle_rad = angle * math.pi / 180

        needle_length = size // 2 - 25
        needle_x = center.x() + needle_length * 0.7 * math.cos(angle_rad)
        needle_y = center.y() + needle_length * 0.7 * math.sin(angle_rad)

        painter.setPen(QPen(QColor(255, 255, 255), 3))
        painter.drawLine(center.x(), center.y(), int(needle_x), int(needle_y))

        # Center dot
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawEllipse(center, 8, 8)

        # Score
        level, color = self._get_level_and_color(self._score)
        painter.setPen(QPen(color, 1))
        font = painter.font()
        font.setPointSize(22)
        font.setBold(True)
        painter.setFont(font)
        score_text_y = center.y() - size // 4 if self._half_circle else center.y() + 10
        painter.drawText(center.x() - 30, score_text_y, 60, 40, Qt.AlignmentFlag.AlignCenter, f"{int(self._score)}")

        # Level
        font.setPointSize(9)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QPen(QColor(180, 180, 200), 1))
        level_text_y = score_text_y + 30 if self._half_circle else center.y() + 50
        painter.drawText(center.x() - 50, level_text_y, 100, 20, Qt.AlignmentFlag.AlignCenter, level)

        painter.end()

    def sizeHint(self):
        return self.minimumSize()
