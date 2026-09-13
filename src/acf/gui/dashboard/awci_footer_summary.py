"""
AWCI Footer Summary
====================

Real "Recent Alerts" / "Latest Updates" / "Quick Actions" footer row
(added 2026-09-13, docs/reference/awci_dashboard_reference.png, Phase
6/6 of the AWCI redesign, explicit user request "je veux que tout le
dashboard soit exactement comme la photo à 100%") - replaces the old
5-icon feature-button footer (acf.gui.dashboard.awci_footer.AWCIFooter).
That module's own 5 real features (Synthetic View/Decision Support/
Multi-Scale/Adaptive to Mission/Research Stage) are not lost: each
already dispatched to an existing real dashboard method
(_revert_to_demo/_open_alerts/_cycle_view_mode/_open_vertical_profile/
_open_execution_report) that stays reachable exactly as before - via
the sidebar nav and/or the topbar's ⚙ Settings menu - this file just
retires the specific 5-icon strip, not any feature behind it.

Real data, no fabricated per-alert timestamps
-----------------------------------------------
AWCIRecentAlertsCard reuses the EXACT SAME real elevated-risk rows
already shown in awci_situation_panel.AWCICurrentSituationCard's own
"Main Hazards" list (acf.gui.dashboard.awci_alerts_panel.
compute_elevated_risks() - the same real classification the "🔔
Alerts" dialog itself uses) - never a second/independent hazard list.
Each row shows the real current Affected Area/Valid Time (the SAME
real values Current Situation already displays) rather than inventing
a distinct fabricated timestamp per row - this dashboard has no real
per-alert event log to draw individual past timestamps from.

AWCILatestUpdatesCard shows real dashboard state-change lines the
caller (AWCIDashboard) provides - see that class's own call site for
what real event each line actually reflects (always a real wall-clock
timestamp already tracked elsewhere in this dashboard, never invented).

AWCIQuickActionsCard is 4 real buttons wired by the caller to already-
real dashboard features (generate report / focus route analysis / save
scenario / export data) - never a fabricated action.
"""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from acf.gui.dashboard.awci_alerts_panel import compute_elevated_risks
from acf.gui.dashboard.awci_colors import risk_qcolor
from acf.gui.theme_tokens import TOKENS


def _card_style() -> str:
    return f"background-color: {TOKENS.bg_card}; border-radius: {TOKENS.radius_md}px;"


class AWCIRecentAlertsCard(QFrame):
    """Real "Recent Alerts" footer card - see module docstring."""

    def __init__(self, on_open_all: Callable[[], None] | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(_card_style())
        self._on_open_all = on_open_all
        if on_open_all is not None:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setToolTip("Open the full Alerts dialog.")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        title = QLabel("Recent Alerts")
        title.setStyleSheet(f"color: {TOKENS.text_secondary}; font-size: 10px; font-weight: bold; border: none;")
        layout.addWidget(title)

        self.rows_layout = QVBoxLayout()
        self.rows_layout.setSpacing(4)
        layout.addLayout(self.rows_layout)
        layout.addStretch()

    def update_data(
        self,
        module_scores: dict[str, float],
        overall_awci: float,
        physical_score: float | None,
        forecast_score: float | None,
        *,
        area: str,
        valid_time: str,
    ) -> None:
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        elevated = compute_elevated_risks(module_scores, overall_awci, physical_score, forecast_score)
        if not elevated:
            empty = QLabel("No elevated hazard right now.")
            empty.setStyleSheet(f"color: {TOKENS.text_muted}; font-size: 9px; border: none;")
            self.rows_layout.addWidget(empty)
            return

        for icon, label, level, _score in elevated[:3]:
            row = QHBoxLayout()
            row.setSpacing(6)
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 12px; border: none;")
            row.addWidget(icon_label)

            text_col = QVBoxLayout()
            text_col.setSpacing(0)
            name_label = QLabel(label)
            name_label.setStyleSheet(f"color: {TOKENS.text_primary}; font-size: 9px; font-weight: bold; border: none;")
            text_col.addWidget(name_label)
            context_label = QLabel(f"{area} — {valid_time}")
            context_label.setStyleSheet(f"color: {TOKENS.text_muted}; font-size: 8px; border: none;")
            text_col.addWidget(context_label)
            row.addLayout(text_col, 1)

            color = risk_qcolor(level)
            level_label = QLabel(level)
            level_label.setStyleSheet(
                f"color: rgb({color.red()},{color.green()},{color.blue()}); font-size: 9px; font-weight: bold; border: none;"
            )
            row.addWidget(level_label)

            wrapper = QWidget()
            wrapper.setLayout(row)
            self.rows_layout.addWidget(wrapper)

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt override signature
        if self._on_open_all is not None and event.button() == Qt.MouseButton.LeftButton:
            self._on_open_all()
        super().mousePressEvent(event)


class AWCILatestUpdatesCard(QFrame):
    """Real "Latest Updates" footer card - a small real status log fed
    entirely by the caller (AWCIDashboard); see its own call site for
    the real event/timestamp behind each line."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(_card_style())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        title = QLabel("Latest Updates")
        title.setStyleSheet(f"color: {TOKENS.text_secondary}; font-size: 10px; font-weight: bold; border: none;")
        layout.addWidget(title)

        self.rows_layout = QVBoxLayout()
        self.rows_layout.setSpacing(3)
        layout.addLayout(self.rows_layout)
        layout.addStretch()

    def update_data(self, lines: list[tuple[str, str]]) -> None:
        """`lines` is `[(label, real_timestamp_text), ...]` - the
        caller's own responsibility to only ever pass a real, already-
        tracked timestamp (never a fabricated/guessed one)."""
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for label, timestamp in lines:
            row = QHBoxLayout()
            row.setSpacing(6)
            check = QLabel("✓")
            check.setStyleSheet(f"color: {TOKENS.accent_real}; font-size: 10px; font-weight: bold; border: none;")
            row.addWidget(check)
            text = QLabel(f"{label}  —  {timestamp}")
            text.setStyleSheet(f"color: {TOKENS.text_secondary}; font-size: 9px; border: none;")
            row.addWidget(text, 1)
            wrapper = QWidget()
            wrapper.setLayout(row)
            self.rows_layout.addWidget(wrapper)


class AWCIQuickActionsCard(QFrame):
    """Real "Quick Actions" footer card - 4 real buttons, each wired by
    the caller to an already-real dashboard feature (never a
    fabricated/no-op handler - see module docstring)."""

    def __init__(
        self,
        on_generate_report: Callable[[], None],
        on_route_analysis: Callable[[], None],
        on_save_scenario: Callable[[], None],
        on_export_data: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setStyleSheet(_card_style())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        title = QLabel("Quick Actions")
        title.setStyleSheet(f"color: {TOKENS.text_secondary}; font-size: 10px; font-weight: bold; border: none;")
        layout.addWidget(title)

        grid = QHBoxLayout()
        grid.setSpacing(6)

        specs = [
            ("📄", "Generate Report", on_generate_report),
            ("✈️", "Route Analysis", on_route_analysis),
            ("💾", "Save Scenario", on_save_scenario),
            ("⬇️", "Export Data", on_export_data),
        ]
        self.buttons: dict[str, QPushButton] = {}
        for icon, label, handler in specs:
            button = QPushButton(f"{icon}\n{label}")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(
                f"QPushButton {{ background-color: {TOKENS.bg_surface_alt}; color: {TOKENS.text_secondary}; "
                f"border: 1px solid {TOKENS.border}; border-radius: {TOKENS.radius_sm}px; font-size: 9px; padding: 6px 2px; }}"
                f"QPushButton:hover {{ border-color: {TOKENS.accent_primary}; color: {TOKENS.text_primary}; }}"
            )
            button.clicked.connect(handler)
            grid.addWidget(button)
            self.buttons[label] = button

        layout.addLayout(grid)
        layout.addStretch()
