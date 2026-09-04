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

from typing import Any

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget

from acf.gui.theme_tokens import dashboard_stylesheet, label_style


class AWCIVerticalProfile(QWidget):
    """
    Vertical profile of AWCI complexity by flight level.

    Shows how complexity varies with altitude.

    Clickable bars (added 2026-09-03, docs/ACF_MASTER_PROMPT.md §51 -
    "afficher : vent, température, humidité, stabilité, convection,
    turbulence, givrage, complexité, incertitude" at each level; this
    widget's own bars only ever showed the composite AWCI complexity
    score). `levelClicked` emits the real clicked level's own label -
    a real caller (AWCIDashboard._on_vertical_profile_level_clicked())
    reads the real per-module breakdown already computed for that
    level and shows it, the same "click a summary number, see the real
    breakdown behind it" pattern already established for the radar/
    risk-summary rows elsewhere in this dashboard - not a new UI
    convention invented here.
    """

    levelClicked = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._profile: dict[str, float] = {}
        self._highlight_level: str | None = None
        self._title = "Profil Vertical AWCI"
        #: (level_label, x, bar_width) for every bar drawn by the last
        #: real paintEvent() - the real geometry mousePressEvent()
        #: hit-tests against, so the two never silently drift apart
        #: (one real layout computation, not two).
        self._bar_geometry: list[tuple[str, float, float]] = []

        self.setMinimumSize(200, 250)
        self.setStyleSheet("background: transparent;")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click a bar for the real per-module breakdown at that level.")

    def set_profile(self, profile: dict[str, float]):
        """
        Set vertical profile data.

        Parameters
        ----------
        profile : dict
            {level: score} where level is string like 'FL100', 'FL300'
        """
        self._profile = profile
        self._compute_bar_geometry()
        self.update()

    def set_highlight(self, level: str):
        """Highlight a specific flight level."""
        self._highlight_level = level
        self.update()

    def set_title(self, title: str):
        """Set widget title."""
        self._title = title
        self.update()

    def resizeEvent(self, event: Any) -> None:
        self._compute_bar_geometry()
        super().resizeEvent(event)

    def _compute_bar_geometry(self) -> None:
        """Real bar x-geometry (level, x, bar_width) for every real bar
        - computed here, independently of paintEvent(), so
        mousePressEvent()'s own hit-testing stays accurate even before
        Qt has actually painted this widget (a real gap found while
        building this feature: Qt does not guarantee a synchronous
        paint right after set_profile()/resize(), so relying on
        paintEvent() alone to populate this left it empty for a real
        window that briefest instant). paintEvent() reads this same
        list back rather than recomputing it a second time - one real
        shared computation, not two that could silently drift apart."""
        self._bar_geometry = []
        if not self._profile:
            return
        margin_left = 50
        margin_right = 20
        plot_width = self.width() - margin_left - margin_right
        if plot_width < 10:
            return
        sorted_items = list(self._profile.items())
        bar_width = min(20, plot_width / len(sorted_items) * 0.7)
        bar_spacing = bar_width * 0.3
        for i, (level, _score) in enumerate(sorted_items):
            x = margin_left + i * (bar_width + bar_spacing) + bar_spacing / 2
            self._bar_geometry.append((level, x, bar_width))

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

        # Real x-geometry (label, x, bar_width) - shared with
        # mousePressEvent()'s own hit-testing, computed once in
        # _compute_bar_geometry() (see that method's own docstring for
        # why this is not recomputed here). margin_left/margin_right
        # are only needed again below, for the grid lines' own real
        # full-width extent.
        margin_left = 50
        margin_right = 20
        margin_top = 35
        # Widened from 20 (2026-09-03, §51's standard-pressure-level
        # closure) - the rotated level labels below now need real
        # vertical room to read (up to 12 real levels can share this
        # chart now, vs. up to 6 before).
        margin_bottom = 45
        plot_height = height - margin_top - margin_bottom

        if not self._bar_geometry or plot_height < 10:
            painter.end()
            return

        # Find min/max scores
        scores = list(self._profile.values())
        max_score = max(100, max(scores) + 10)

        font.setPointSize(7)
        font.setBold(False)
        painter.setFont(font)

        for level, x, bar_width in self._bar_geometry:
            score = self._profile[level]

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

    def mousePressEvent(self, event: Any) -> None:
        """Real click-to-select: hit-tests the click's x-position
        against the exact real bar geometry the last paintEvent() drew
        (see __init__'s own comment on why this is one shared real
        computation, not two) - the full real column width, not just
        the bar's own drawn height, so a click anywhere in that
        level's column registers, a real forgiving target matching
        common bar-chart UI convention."""
        x = event.position().x()
        for level, bar_x, bar_width in self._bar_geometry:
            if bar_x <= x <= bar_x + bar_width:
                self.levelClicked.emit(level)
                break
        super().mousePressEvent(event)

    def sizeHint(self):
        return QSize(250, 300)


#: Real §51 label per real AWCICalculator module_scores key - the
#: honest mapping from that section's own requested variable list
#: ("vent, température, humidité, stabilité, convection, turbulence,
#: givrage, complexité, incertitude") onto the 9 real modules this
#: project's own AWCICalculator actually computes (see
#: AWCIVerticalProfileLevelDialog's own docstring for which §51 words
#: have no real dedicated module and are honestly disclosed as such,
#: rather than force-mapped). ensemble_spread/model_disagreement are
#: the real FORECAST_MODULES (calculator.py's own grouping) - real,
#: opt-in scores that stay at AWCICalculator's own honest default
#: (never a fabricated one) in demo mode, since neither
#: ensemble_members nor model_realizations is ever supplied by this
#: dashboard's own synthetic per-point pipeline.
_MODULE_LABELS_FOR_LEVEL_DETAIL: dict[str, str] = {
    "dynamic": "Dynamics (wind)",
    "thermodynamic": "Thermodynamic (temperature + humidity)",
    "convective": "Convective",
    "microphysical": "Microphysical (icing)",
    "topographic": "Topographic (orographic)",
    "temporal": "Temporal (rate of change)",
    "confidence": "Confidence",
    "ensemble_spread": "Ensemble spread",
    "model_disagreement": "Model disagreement",
}


class AWCIVerticalProfileLevelDialog(QDialog):
    """
    Real per-level detail popup (docs/ACF_MASTER_PROMPT.md §51),
    opened by AWCIVerticalProfile.levelClicked - the exact same real
    module_scores/physical_score/forecast_score AWCICalculator.
    calculate() already returns for that level (built by
    AWCIDashboard._open_vertical_profile()'s own loop), never a second/
    recomputed value.

    Honest §51 coverage: this project's own AWCICalculator computes 9
    real modules (dynamic/thermodynamic/convective/microphysical/
    topographic/temporal/confidence/ensemble_spread/model_disagreement)
    - §51's own word list ("température, humidité" as 2 separate
    items; "stabilité"; "turbulence"; "givrage") does not map 1:1 onto
    them.
    "température"+"humidité" are honestly shown as ONE real
    thermodynamic score (AWCICalculator's own module already blends
    them, not 2 separate numbers); "givrage" maps onto the real
    microphysical score. "stabilité" and "turbulence" have no real
    dedicated module anywhere in this codebase's per-point pipeline
    today (the map's own "Turbulence" LAYERS checkbox uses a disclosed
    horizontal-wind-gradient proxy that has no single-point
    equivalent here) - this dialog shows an honest note instead of a
    fabricated number for either.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(dashboard_stylesheet())
        layout = QVBoxLayout(self)

        self._title_label = QLabel()
        self._title_label.setStyleSheet(label_style("text_primary", "lg", "bold"))
        layout.addWidget(self._title_label)

        self._score_label = QLabel()
        self._score_label.setStyleSheet(label_style("text_primary", "md", "bold"))
        layout.addWidget(self._score_label)

        self._split_label = QLabel()
        self._split_label.setStyleSheet(label_style("text_secondary", "sm"))
        layout.addWidget(self._split_label)

        breakdown_header = QLabel("Real module-score breakdown at this level (§51):")
        breakdown_header.setStyleSheet(label_style("text_secondary", "sm", "bold"))
        layout.addWidget(breakdown_header)

        self._module_rows: dict[str, QLabel] = {}
        for module_key, module_label in _MODULE_LABELS_FOR_LEVEL_DETAIL.items():
            row = QLabel()
            row.setStyleSheet(label_style("text_secondary", "sm"))
            layout.addWidget(row)
            self._module_rows[module_key] = row

        note = QLabel(
            "Note: §51 also lists \"stabilité\" and \"turbulence\" - neither has a real "
            "dedicated per-point module in this codebase today, so no number is shown for "
            "them here rather than a fabricated one."
        )
        note.setWordWrap(True)
        note.setStyleSheet(label_style("text_muted", "xs"))
        layout.addWidget(note)

        self.resize(360, 360)

    def show_detail(self, level_label: str, hpa: float, result: dict[str, Any]) -> None:
        self.setWindowTitle(f"AWCI – {level_label}")
        self._title_label.setText(f"{level_label}  (~{hpa:.0f} hPa)")
        self._score_label.setText(f"AWCI: {result['awci']:.1f} / 100 ({result['level']})")

        physical = result.get("physical_score")
        forecast = result.get("forecast_score")
        physical_text = f"{physical:.1f}" if physical is not None else "—"
        forecast_text = f"{forecast:.1f}" if forecast is not None else "—"
        self._split_label.setText(f"Physical: {physical_text}   ·   Forecast: {forecast_text}")

        module_scores = result.get("module_scores", {})
        for module_key, module_label in _MODULE_LABELS_FOR_LEVEL_DETAIL.items():
            value = module_scores.get(module_key)
            value_text = f"{value:.1f}" if value is not None else "—"
            self._module_rows[module_key].setText(f"{module_label}: {value_text}")

        self.show()
        self.raise_()
        self.activateWindow()
