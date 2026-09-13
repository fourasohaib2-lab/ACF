"""
ACF Scientific Workstation — Shared Gauge Widgets
=====================================================

Real, custom-painted gauge widgets matching acf_workstation_reference.jpg's
visual language (a circular ring gauge for Complexity Overview, a colored
horizontal bar gauge for Key Atmospheric Variables/Model Agreement). These
are pure presentation widgets — they take a real, already-computed value
and paint it; they never compute anything themselves.

Added 2026-09-13 (explicit user request "chaque pixel... exactement comme
dans la photo") — replaces the earlier plain-text-only rendering of these
values with the reference image's own visual style.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget


class CircularGaugeWidget(QWidget):
    """A ring gauge (0-1 value) with a big centered number and a level
    word below it — matches the reference image's "Complexity Overview"
    dial. Track is a dim ring; the real value is drawn as a cyan/teal
    arc proportional to it. No computation here — `set_value()` just
    stores what it's told and repaints."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._value: float | None = None
        self._level_text: str = "NOT_COMPUTED"
        self.setMinimumSize(96, 96)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def set_value(self, value: float | None, level_text: str) -> None:
        self._value = value
        self._level_text = level_text
        self.update()

    def sizeHint(self):  # noqa: N802 - Qt override
        from PySide6.QtCore import QSize

        return QSize(110, 110)

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        side = min(self.width(), self.height())
        pen_width = max(6, side // 12)
        rect = QRectF(
            pen_width / 2, pen_width / 2, side - pen_width, side - pen_width
        )

        # Dim background track (full ring).
        track_pen = QPen(QColor("#1e3a4a"), pen_width)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(rect, 0, 360 * 16)

        if self._value is not None:
            value_pen = QPen(QColor("#22d3ee"), pen_width)
            value_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(value_pen)
            span = max(0.0, min(1.0, self._value)) * 360.0
            # Start at 12 o'clock (90° in Qt's 0=3-o'clock, CCW-positive
            # convention) and sweep clockwise.
            painter.drawArc(rect, 90 * 16, -int(span * 16))

        painter.setPen(QColor("#e6edf3"))
        number_font = QFont(self.font())
        number_font.setPointSizeF(max(9.0, side * 0.20))
        number_font.setBold(True)
        painter.setFont(number_font)
        number_text = f"{self._value:.2f}" if self._value is not None else "—"
        number_rect = QRectF(rect.left(), rect.top(), rect.width(), rect.height() * 0.55)
        painter.drawText(number_rect, Qt.AlignmentFlag.AlignCenter, number_text)

        painter.setPen(QColor("#8ea0b5"))
        level_font = QFont(self.font())
        level_font.setPointSizeF(max(7.0, side * 0.10))
        painter.setFont(level_font)
        level_rect = QRectF(rect.left(), rect.top() + rect.height() * 0.52, rect.width(), rect.height() * 0.3)
        painter.drawText(level_rect, Qt.AlignmentFlag.AlignCenter, self._level_text)

        painter.end()


class HorizontalBarGauge(QWidget):
    """A single colored horizontal bar gauge (the small track under each
    Key Atmospheric Variable, and each Model Agreement row) — a real
    0-1 fraction painted as a filled rounded rectangle over a dim
    track, in a caller-chosen color."""

    def __init__(self, color: str = "#3b82f6", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._fraction: float = 0.0
        self._color = QColor(color)
        self.setFixedHeight(6)
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)

    def set_color(self, color: str) -> None:
        self._color = QColor(color)
        self.update()

    def set_fraction(self, fraction: float | None) -> None:
        self._fraction = 0.0 if fraction is None else max(0.0, min(1.0, fraction))
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        radius = self.height() / 2.0

        track_rect = QRectF(0, 0, self.width(), self.height())
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#1c2e3f"))
        painter.drawRoundedRect(track_rect, radius, radius)

        fill_width = max(self.height(), self.width() * self._fraction)
        fill_rect = QRectF(0, 0, fill_width, self.height())
        painter.setBrush(self._color)
        painter.drawRoundedRect(fill_rect, radius, radius)
        painter.end()


class ColorDot(QWidget):
    """A small filled circle — the colored legend dot next to each
    Complexity Overview factor row."""

    def __init__(self, color: str = "#3b82f6", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color = QColor(color)
        self.setFixedSize(10, 10)

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._color)
        painter.drawEllipse(0, 0, self.width(), self.height())
        painter.end()
