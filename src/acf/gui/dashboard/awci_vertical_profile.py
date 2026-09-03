"""
AWCI Vertical Profile Widget
============================

Shows real AWCI complexity by vertical level (real named flight levels
PLUS real standard pressure levels - docs/ACF_MASTER_PROMPT.md §51).

Reachable, real UI (updated 2026-09-03): this widget predates the AWCI
dashboard rebuild and was genuinely unused for a while (the rebuilt
dashboard used AWCICrossSection instead for its own vertical cross-
section panel), but was wired into a real "🔍 See Vertical Profile"
button/dialog during this session's own dashboard-parity closure (see
awci_dashboard.py's `_open_vertical_profile()`) - no longer dead code.

Real level ordering (added 2026-09-03, §51's standard-pressure-level
closure): `set_profile()` trusts the CALLER's own dict insertion order
rather than re-deriving one internally. An earlier version sorted by
parsing "FL<n>" labels - that only ever worked because every real
caller supplied flight-level-only labels; it silently could not
interleave real standard pressure levels ("850 hPa", "Surface", ...)
by true altitude among flight levels (their `parse_fl()` key was
always 0). The real caller (`awci_dashboard.py`'s
`_ALL_VERTICAL_PROFILE_LEVELS_HPA`) already computes the correct real
altitude order from actual hPa values before calling `set_profile()` -
a single source of truth for that order, not duplicated here.
"""

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class AWCIVerticalProfile(QWidget):
    """
    Vertical profile of AWCI complexity by flight level.

    Shows how complexity varies with altitude.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._profile: dict[str, float] = {}
        self._highlight_level: str | None = None
        self._title = "Profil Vertical AWCI"

        self.setMinimumSize(200, 250)
        self.setStyleSheet("background: transparent;")

    def set_profile(self, profile: dict[str, float]):
        """
        Set vertical profile data.

        Parameters
        ----------
        profile : dict
            {level: score} where level is string like 'FL100', 'FL300'
        """
        self._profile = profile
        self.update()

    def set_highlight(self, level: str):
        """Highlight a specific flight level."""
        self._highlight_level = level
        self.update()

    def set_title(self, title: str):
        """Set widget title."""
        self._title = title
        self.update()

    def paintEvent(self, event):
        """Draw the vertical profile."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        width = rect.width()
        height = rect.height()

        # Draw title
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor(200, 200, 220), 1))
        painter.drawText(10, 20, self._title)

        if not self._profile:
            painter.setPen(QPen(QColor(100, 100, 130), 1))
            painter.drawText(10, height // 2, "Aucune donnée")
            painter.end()
            return

        # Real altitude order (see module docstring) - the caller
        # already sorted this dict by real hPa before calling
        # set_profile(), so this widget draws it left-to-right exactly
        # as given rather than re-deriving a (label-format-specific,
        # previously incorrect for mixed level types) order itself.
        sorted_items = list(self._profile.items())

        # Draw profile
        margin_left = 50
        margin_right = 20
        margin_top = 35
        # Widened from 20 (2026-09-03, §51's standard-pressure-level
        # closure) - the rotated level labels below now need real
        # vertical room to read (up to 12 real levels can share this
        # chart now, vs. up to 6 before).
        margin_bottom = 45

        plot_width = width - margin_left - margin_right
        plot_height = height - margin_top - margin_bottom

        if plot_width < 10 or plot_height < 10:
            painter.end()
            return

        # Find min/max scores
        scores = list(self._profile.values())
        max_score = max(100, max(scores) + 10)

        # Draw bars
        bar_width = min(20, plot_width / len(sorted_items) * 0.7)
        bar_spacing = bar_width * 0.3

        font.setPointSize(7)
        font.setBold(False)
        painter.setFont(font)

        for i, (level, score) in enumerate(sorted_items):
            x = margin_left + i * (bar_width + bar_spacing) + bar_spacing / 2

            # Normalize score to height
            normalized = score / max_score
            bar_height = normalized * plot_height
            y = margin_top + plot_height - bar_height

            # Determine color based on score
            if score >= 85:
                color = QColor(255, 0, 0)
            elif score >= 65:
                color = QColor(255, 100, 0)
            elif score >= 50:
                color = QColor(255, 200, 0)
            elif score >= 35:
                color = QColor(100, 200, 50)
            else:
                color = QColor(0, 200, 100)

            # Highlight if this level is selected
            is_highlight = self._highlight_level == level

            # Draw bar
            if is_highlight:
                painter.setBrush(QBrush(color.lighter(130)))
                painter.setPen(QPen(QColor(255, 255, 255), 2))
            else:
                painter.setBrush(QBrush(color))
                painter.setPen(QPen(Qt.PenStyle.NoPen))

            painter.drawRect(int(x), int(y), int(bar_width), int(bar_height))

            # Draw score text
            painter.setPen(QPen(QColor(200, 200, 220), 1))
            score_text = f"{int(score)}"
            painter.drawText(int(x), int(y - 12), int(bar_width), 12, Qt.AlignmentFlag.AlignCenter, score_text)

            # Draw level label - rotated (added 2026-09-03, §51's
            # standard-pressure-level closure: up to 12 real levels can
            # now share this chart, vs. up to 6 before, and labels like
            # "850 hPa"/"Surface" are real longer than "FL100" - a
            # horizontal label no longer reliably fits one narrow bar's
            # own width without being clipped). Anchored at the bar's
            # own horizontal center, angled so it reads outward without
            # overlapping its neighbours.
            painter.save()
            painter.setPen(QPen(QColor(150, 150, 180), 1))
            painter.translate(x + bar_width / 2, margin_top + plot_height + 8)
            painter.rotate(-55)
            painter.drawText(0, 0, level)
            painter.restore()

        # Draw grid lines
        painter.setPen(QPen(QColor(50, 50, 80), 1, Qt.PenStyle.DashLine))
        for grid_score in [25, 50, 75]:
            y = margin_top + plot_height - (grid_score / max_score) * plot_height
            painter.drawLine(margin_left, int(y), width - margin_right, int(y))

            painter.setPen(QPen(QColor(100, 100, 130), 1))
            painter.drawText(5, int(y) + 4, 35, 12, Qt.AlignmentFlag.AlignRight, f"{grid_score}")

        painter.end()

    def sizeHint(self):
        return QSize(250, 300)
