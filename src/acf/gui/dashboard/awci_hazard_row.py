"""
AWCI Hazard Row
===============

Real "AWCI GLOBAL" gauge + 6 hazard mini-cards (added 2026-09-12,
explicit user request "je veux que le dashboard soit exactement comme
celui dans la photo... 100%... tous les boutons fonctionnelles" -
docs/reference/awci_dashboard_reference.png), Phase 2/6 of that
redesign.

Real values, not invented: every card's number is `100 *
module_scores[key]` for the SAME real `AWCICalculator.
calculate_module_scores()` dict `AWCIRiskSummary`/`_ComponentValueList`
already display elsewhere in this dashboard - see `update_data()`'s
own docstring for the exact key mapping and, honestly, which hazard
has NO distinct real module score of its own yet (Wind Shear - see
below) rather than a fabricated/duplicated one.
"""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from acf.gui.dashboard.awci_colors import level_for, risk_qcolor
from acf.gui.dashboard.awci_gauge import AWCIGauge
from acf.gui.theme_tokens import TOKENS

#: (module_scores key or None, icon, label) - see update_data()'s own
#: docstring for why "Wind Shear" has no key (None): AWCICalculator has
#: no standalone real wind-shear module score distinct from "dynamic"
#: (already used for Turbulence) - showing the same real number twice
#: under two different hazard names would misrepresent it as two
#: independent real measurements.
HAZARD_CARDS: tuple[tuple[str | None, str, str], ...] = (
    ("dynamic", "🌪️", "Turbulence"),
    ("convective", "⛈️", "Convection"),
    ("microphysical", "❄️", "Icing"),
    (None, "💨", "Wind Shear"),
    ("visibility", "👁️", "Visibility"),
    ("ceiling", "☁️", "Ceiling"),
)


class _HazardCard(QFrame):
    """One real hazard mini-card - icon/label, a real 0-100 value, and
    its real AWCI-scale severity name (acf.gui.dashboard.awci_colors.
    level_for() - the SAME real 6-tier scale the map legend/gauge/risk
    badges already use, not a separately invented one)."""

    def __init__(self, icon: str, label: str, tooltip: str = "") -> None:
        super().__init__()
        self.setStyleSheet(f"background-color: {TOKENS.bg_card}; border-radius: {TOKENS.radius_md}px;")
        if tooltip:
            self.setToolTip(tooltip)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        header = QLabel(f"{icon}  {label}")
        header.setStyleSheet(f"color: {TOKENS.text_secondary}; font-size: 10px; font-weight: bold; border: none;")
        layout.addWidget(header)

        self.value_label = QLabel("—")
        self.value_label.setStyleSheet(f"color: {TOKENS.text_primary}; font-size: 20px; font-weight: bold; border: none;")
        layout.addWidget(self.value_label)

        self.severity_label = QLabel("")
        self.severity_label.setStyleSheet(f"color: {TOKENS.text_muted}; font-size: 10px; font-weight: bold; border: none;")
        layout.addWidget(self.severity_label)

    def set_value(self, score_0_100: float | None) -> None:
        if score_0_100 is None:
            self.value_label.setText("—")
            self.severity_label.setText("")
            self.severity_label.setStyleSheet(f"color: {TOKENS.text_muted}; font-size: 10px; font-weight: bold; border: none;")
            return
        level = level_for(score_0_100)
        color = risk_qcolor(level)
        self.value_label.setText(f"{score_0_100:.0f}")
        self.severity_label.setText(level)
        self.severity_label.setStyleSheet(
            f"color: rgb({color.red()},{color.green()},{color.blue()}); font-size: 10px; font-weight: bold; border: none;"
        )


class AWCIHazardRow(QWidget):
    """Real "AWCI GLOBAL" gauge + 6 hazard mini-cards row - see module
    docstring. `update_data()` is the single real entry point, fed the
    SAME `module_scores`/`overall_awci` every other real panel in this
    dashboard already receives."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        gauge_card = QFrame()
        gauge_card.setStyleSheet(f"background-color: {TOKENS.bg_card}; border-radius: {TOKENS.radius_md}px;")
        gauge_layout = QVBoxLayout(gauge_card)
        gauge_layout.setContentsMargins(10, 8, 10, 4)
        gauge_title = QLabel("AWCI GLOBAL")
        gauge_title.setStyleSheet(f"color: {TOKENS.text_secondary}; font-size: 10px; font-weight: bold; border: none;")
        gauge_layout.addWidget(gauge_title)
        self.gauge = AWCIGauge()
        gauge_layout.addWidget(self.gauge)
        layout.addWidget(gauge_card)

        self._cards: dict[str, _HazardCard] = {}
        for key, icon, label in HAZARD_CARDS:
            tooltip = (
                ""
                if key is not None
                else (
                    "No standalone real wind-shear module score exists yet, distinct from "
                    "Turbulence's real dynamic-module value - shown honestly as — rather "
                    "than a duplicated/fabricated number."
                )
            )
            card = _HazardCard(icon, label, tooltip)
            self._cards[label] = card
            layout.addWidget(card, stretch=1)

    def update_data(self, module_scores: dict[str, float], overall_awci: float) -> None:
        """`module_scores` is the SAME real dict `AWCICalculator.
        calculate()` already returns and `AWCIRiskSummary`/
        `_ComponentValueList` already display - already on the real
        0-100 scale (`AWCICalculator.calculate_module_scores()` itself
        rounds each raw 0-1 fraction to `round(v * 100, 1)` before this
        dict ever reaches here), so no second scaling is applied."""
        self.gauge.set_score(overall_awci, animate=False)
        for key, _icon, label in HAZARD_CARDS:
            score = None if key is None else float(module_scores.get(key, 0.0))
            self._cards[label].set_value(score)
