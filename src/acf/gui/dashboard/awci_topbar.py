"""
AWCI Top Bar
============

Real light top bar (added 2026-09-12, explicit user request "je veux
que le dashboard soit exactement comme celui dans la photo... 100%...
tous les boutons fonctionnelles" - docs/reference/
awci_dashboard_reference.png), replacing the previous dark header row
this dashboard used to build directly in `_build_ui()`.

Every control here is wired to a REAL, already-existing dashboard
mechanism - see `AWCIDashboard._wire_topbar()`'s own docstring for the
exact mapping (Area -> the real VIEW MODE radios, Date & Time -> the
real `time_slider`, Model -> the real current model name already shown
in the stats bar, bell -> the real Alerts dialog, cloud -> the real
Connect HPC feature, gear -> the real "☰" menu this dashboard already
built). The one honestly non-functional element is the user avatar -
ACF has no real authentication/user-account system, so this shows a
generic icon with a disclosing tooltip rather than a fabricated name.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPaintEvent, QPolygonF
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QToolButton, QVBoxLayout, QWidget

from acf.gui.theme_tokens import TOKENS


class AWCILogoMark(QWidget):
    """Real `QPainter`-drawn AWCI logo mark - a rounded navy-blue square
    badge with a lighter-blue mountain-peak glyph, matching the reference
    image's top-left icon (docs/reference/awci_dashboard_reference.png,
    sampled 2026-09-21: dark badge ground, two overlapping peak shapes in
    a #1196f9-ish bright blue to #052b5b-ish deep blue gradient). Follows
    this codebase's existing custom-painted-widget convention (see
    `AWCIGauge` in awci_gauge.py) rather than sourcing/fabricating an
    external image asset - no reusable logo asset exists anywhere in this
    repo (checked docs/reference/ and every assets/icons directory)."""

    def __init__(self, parent: QWidget | None = None, size: int = 36) -> None:
        super().__init__(parent)
        self._size = size
        self.setFixedSize(size, size)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(0, 0, self._size, self._size)
        radius = self._size * 0.28

        # Badge background - a real linear gradient between this
        # dashboard's own established accent blues (TOKENS.accent_primary
        # -> a deeper navy), not an invented one-off hex.
        badge_gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        badge_gradient.setColorAt(0.0, QColor(TOKENS.accent_primary))
        badge_gradient.setColorAt(1.0, QColor(TOKENS.bg_root))
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(badge_gradient)
        painter.drawPath(path)

        # Mountain-peak glyph - two overlapping triangular peaks, the
        # back one darker/deeper-blue and the front one the brighter
        # accent blue, mirroring the reference image's layered-peaks mark.
        painter.setClipPath(path)
        s = self._size
        back_peak = QPolygonF(
            [QPointF(s * 0.24, s * 0.74), QPointF(s * 0.52, s * 0.22), QPointF(s * 0.80, s * 0.74)]
        )
        painter.setBrush(QColor(TOKENS.bg_root).lighter(180))
        painter.drawPolygon(back_peak)

        front_peak = QPolygonF(
            [QPointF(s * 0.16, s * 0.80), QPointF(s * 0.40, s * 0.36), QPointF(s * 0.64, s * 0.80)]
        )
        painter.setBrush(QColor(TOKENS.accent_primary_hover))
        painter.drawPolygon(front_peak)

        painter.end()


class AWCITopBar(QWidget):
    """Real light top bar - see module docstring. Exposes real Qt
    widgets as public attributes (`area_combo`, `prev_time_button`,
    `next_time_button`, `now_button`, `forecast_label`, `model_label`,
    `status_dot`, `status_label`, `last_update_label`, `bell_button`,
    `hpc_button`, `settings_button`) so `AWCIDashboard._wire_topbar()`
    can connect them to real existing slots - this widget owns no
    dashboard logic of its own, only the real controls."""

    areaChanged = Signal(str)

    # Real dark-navy palette (fixed 2026-09-21, Task 1 of the AWCI
    # final-polish plan - Task 10's finding F3, "white text-boxes on a
    # dark page"): the reference image's top bar is NOT white - it is a
    # dark navy bar with light text, sampled directly from
    # docs/reference/awci_dashboard_reference.png (bar ground ~#001124,
    # title text ~#f7fcfc, subtitle ~#5b7491). Reusing this codebase's
    # own existing dark-navy design tokens (acf.gui.theme_tokens.TOKENS)
    # rather than inventing new one-off hex values, since TOKENS.bg_root/
    # text_primary/text_muted already land within a few RGB points of the
    # sampled reference colors.
    _BG = TOKENS.bg_root
    _BORDER = TOKENS.border
    _TEXT = TOKENS.text_primary
    _TEXT_MUTED = TOKENS.text_muted
    # Real filter-row palette (2026-09-20, Task 8) - the reference image
    # places this row over the dark page background, not inside the top
    # bar, so its pills need the dark-surface treatment rather than the
    # light-bar style this class used before Task 1's dark-navy repaint.
    _FILTER_BG = "#101a2e"
    _FILTER_BORDER = "#25365a"
    _FILTER_TEXT = "#e8edf5"
    _FILTER_TEXT_MUTED = "#8fa0bd"
    _FILTER_HOVER = "#1b2a47"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(64)
        # Root cause of Task 10 finding F3 (white text-boxes on a dark
        # page): a plain QWidget subclass does NOT paint a stylesheet
        # `background-color` on its own - Qt only does that for widgets
        # with WA_StyledBackground set (or ones with a native/QSS-aware
        # style like QFrame). Without it, this bar was visually
        # transparent over whatever sat behind it, while its light-on-dark
        # child labels below still assumed the (never-actually-painted)
        # dark background. Verified no conflicting paintEvent/style logic
        # exists in this widget before adding this.
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {self._BG}; border-bottom: 1px solid {self._BORDER};")

        row = QHBoxLayout(self)
        row.setContentsMargins(20, 8, 20, 8)
        row.setSpacing(16)

        self.logo_mark = AWCILogoMark(size=36)
        row.addWidget(self.logo_mark, alignment=Qt.AlignmentFlag.AlignVCenter)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        title = QLabel("Aviation Weather Complexity Index")
        title.setStyleSheet(f"color: {self._TEXT}; font-size: 15px; font-weight: bold; border: none;")
        subtitle = QLabel("From ACF data  •  For safer skies")
        subtitle.setStyleSheet(f"color: {self._TEXT_MUTED}; font-size: 10px; border: none;")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        row.addLayout(title_col)
        row.addStretch()

        # --- Real filter bar (relocated 2026-09-20, Task 8 of the AWCI
        # dashboard-fixes plan) -------------------------------------------
        # The reference image (docs/reference/awci_dashboard_reference.png)
        # does NOT merge the Area/Date & Time/Forecast/Model selectors into
        # the white top bar - they sit in their OWN row directly below it,
        # over the dark page background. Every control below is therefore
        # still constructed here (this widget owns the real Qt objects
        # `AWCIDashboard._wire_topbar()` connects to - `area_combo`,
        # `prev_time_button`, ... - unchanged), but assembled into
        # `self.filter_bar` instead of being added to this bar's own `row`.
        # `AWCIDashboard._build_ui()` reparents `filter_bar` into its own
        # real filter row, so these selectors are genuinely no longer
        # children of the top bar widget.
        self.filter_bar = QWidget()
        filter_row = QHBoxLayout(self.filter_bar)
        filter_row.setContentsMargins(12, 6, 12, 6)
        filter_row.setSpacing(14)
        self.filter_bar.setObjectName("awciFilterBar")
        # Object-name-scoped so the card background/border applies to the
        # bar itself only - a bare `QWidget { ... }` rule here would cascade
        # a border onto every child pill inside it.
        self.filter_bar.setStyleSheet(
            f"QWidget#awciFilterBar {{ background-color: {self._FILTER_BG}; "
            f"border: 1px solid {self._FILTER_BORDER}; border-radius: 8px; }}"
        )

        # --- Real Area selector (wired to the existing VIEW MODE radios) ---
        self.area_combo = QComboBox()
        self.area_combo.addItems(["Global", "North Africa"])
        self.area_combo.setStyleSheet(self._dark_pill_style())
        self.area_combo.currentTextChanged.connect(self.areaChanged.emit)
        filter_row.addWidget(self._labeled("Area", self.area_combo, dark=True))

        # --- Real Date & Time (wired to the existing real time_slider) ---
        time_group = QWidget()
        time_row = QHBoxLayout(time_group)
        time_row.setContentsMargins(0, 0, 0, 0)
        time_row.setSpacing(2)
        self.prev_time_button = QToolButton()
        self.prev_time_button.setText("‹")
        self.next_time_button = QToolButton()
        self.next_time_button.setText("›")
        self.now_button = QPushButton("Now")
        self.now_button.setStyleSheet(self._dark_pill_style())
        self.time_readout_label = QLabel("--:-- UTC")
        self.time_readout_label.setStyleSheet(
            f"color: {self._FILTER_TEXT}; font-size: 11px; font-weight: bold; border: none; padding: 0 6px;"
        )
        for btn in (self.prev_time_button, self.next_time_button):
            btn.setStyleSheet(
                f"QToolButton {{ border: 1px solid {self._FILTER_BORDER}; border-radius: 4px; padding: 2px 6px; "
                f"color: {self._FILTER_TEXT}; }}"
                f"QToolButton:hover {{ background-color: {self._FILTER_HOVER}; }}"
            )
        time_row.addWidget(self.prev_time_button)
        time_row.addWidget(self.time_readout_label)
        time_row.addWidget(self.next_time_button)
        time_row.addWidget(self.now_button)
        filter_row.addWidget(self._labeled("Date & Time", time_group, dark=True))

        # --- Real Forecast lead-time readout (derived from time_slider) ---
        self.forecast_label = QLabel("+0h")
        self.forecast_label.setStyleSheet(self._dark_pill_style())
        filter_row.addWidget(self._labeled("Forecast", self.forecast_label, dark=True))

        # --- Real current model name (already computed elsewhere) ------
        self.model_label = QLabel("—")
        self.model_label.setStyleSheet(self._dark_pill_style())
        filter_row.addWidget(self._labeled("Model", self.model_label, dark=True), stretch=1)
        filter_row.addStretch()

        # --- Real system status -----------------------------------------
        status_col = QVBoxLayout()
        status_col.setSpacing(0)
        status_row = QHBoxLayout()
        status_row.setSpacing(4)
        self.status_dot = QLabel("●")
        self.status_label = QLabel("DEMO MODE")
        self.status_label.setStyleSheet(f"color: {self._TEXT}; font-size: 10px; font-weight: bold; border: none;")
        status_row.addWidget(self.status_dot)
        status_row.addWidget(self.status_label)
        status_col.addLayout(status_row)
        self.last_update_label = QLabel("Last Update: —")
        self.last_update_label.setStyleSheet(f"color: {self._TEXT_MUTED}; font-size: 9px; border: none;")
        status_col.addWidget(self.last_update_label)
        row.addLayout(status_col)

        self.bell_button = self._icon_button("🔔")
        self.hpc_button = self._icon_button("🔌")
        self.settings_button = self._icon_button("⚙️")
        row.addWidget(self.bell_button)
        row.addWidget(self.hpc_button)
        row.addWidget(self.settings_button)

        # Honest placeholder - see module docstring: ACF has no real
        # user-account system, so no name/role is fabricated here.
        self.user_button = self._icon_button("👤")
        self.user_button.setToolTip("No real user-account system exists in ACF yet - purely decorative.")
        self.user_button.setEnabled(False)
        row.addWidget(self.user_button)

    def _labeled(self, label_text: str, control: QWidget, *, dark: bool = False) -> QWidget:
        wrapper = QWidget()
        col = QVBoxLayout(wrapper)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(2)
        label = QLabel(label_text)
        muted = self._FILTER_TEXT_MUTED if dark else self._TEXT_MUTED
        label.setStyleSheet(f"color: {muted}; font-size: 9px; border: none;")
        col.addWidget(label)
        col.addWidget(control)
        return wrapper

    def _dark_pill_style(self) -> str:
        """Real pill geometry for the filter row's dark page surface -
        see `filter_bar`'s own construction comment. Was previously
        paired with a light-bar `_pill_style()` counterpart; removed
        2026-09-21 (Task 1, AWCI final-polish plan) once this bar's own
        dark-navy repaint made the light variant dead code - it had no
        remaining call site and would have painted an illegible white
        pill with light text had anything still used it."""
        return (
            f"border: 1px solid {self._FILTER_BORDER}; border-radius: 5px; padding: 3px 8px; "
            f"color: {self._FILTER_TEXT}; font-size: 11px; background-color: #16233c;"
        )

    def _icon_button(self, glyph: str) -> QToolButton:
        button = QToolButton()
        button.setText(glyph)
        # Hover recolored alongside the bar's dark-navy palette (Task 1,
        # 2026-09-21) - the old #f0f2f5 light hover was a leftover from
        # this bar's previous white-background styling and would have
        # painted a bright square on the new dark bar.
        button.setStyleSheet(
            f"QToolButton {{ border: none; border-radius: 6px; padding: 6px; font-size: 14px; }}"
            f"QToolButton:hover {{ background-color: {self._FILTER_HOVER}; }}"
        )
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def set_status(self, *, is_real: bool, label: str) -> None:
        """Real status readout - `is_real` drives the dot color
        (green=Real Physics/Real Archive, amber=demo), `label` is the
        real current mode text."""
        color = "#22c55e" if is_real else "#f59e0b"
        self.status_dot.setStyleSheet(f"color: {color}; font-size: 10px; border: none;")
        self.status_label.setText(label)
