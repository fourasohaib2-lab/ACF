"""
AWCI Situation Panel
====================

Real "Current Situation" / "Model Agreement" / "Airport Complexity"
cards (added 2026-09-12, explicit user request "je veux que le
dashboard soit exactement comme celui dans la photo... 100%... tous
les boutons fonctionnelles" - docs/reference/
awci_dashboard_reference.png), Phase 4/6 of that redesign.

Real values, not invented - see each class's own docstring for its
exact real source:
- AWCICurrentSituationCard: the SAME real elevated-hazard list, area/
  altitude/valid-time controls, and forecast-confidence value every
  other panel on this dashboard already reads/shows.
- AWCIModelAgreementCard: the real (currently-always-0 by default,
  honestly disclosed) `model_disagreement` module score - ACF has no
  real multi-model ensemble wired in yet, same disclosed limitation
  already established for this exact key elsewhere in this codebase.
- AWCIAirportTable: a REAL per-airport AWCI score, computed by running
  the SAME real AWCICalculator/_synthetic_inputs demo pipeline at each
  airport's own real (lat, lon) from awci_dashboard.py's own real
  _AIRPORTS reference table - never fabricated numbers. Trend is a
  real comparison against the same real computation one hour earlier
  (both real synthetic-pattern evaluations, not a guess).
"""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from acf.gui.dashboard.awci_alerts_panel import compute_elevated_risks
from acf.gui.dashboard.awci_colors import level_for, risk_qcolor
from acf.gui.theme_tokens import TOKENS, dashboard_stylesheet


def _card_frame() -> QFrame:
    frame = QFrame()
    frame.setStyleSheet(f"background-color: {TOKENS.bg_card}; border-radius: {TOKENS.radius_md}px;")
    return frame


class AWCICurrentSituationCard(QFrame):
    """Real "Current Situation" card - see module docstring."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {TOKENS.bg_card}; border-radius: {TOKENS.radius_md}px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        self.title_label = QLabel("CURRENT SITUATION")
        self.title_label.setStyleSheet(f"color: {TOKENS.text_secondary}; font-size: 10px; font-weight: bold; border: none;")
        layout.addWidget(self.title_label)
        self.severity_label = QLabel("—")
        self.severity_label.setStyleSheet(f"color: {TOKENS.text_primary}; font-size: 14px; font-weight: bold; border: none;")
        layout.addWidget(self.severity_label)

        self.hazards_header = QLabel("Main Hazards")
        self.hazards_header.setStyleSheet(f"color: {TOKENS.text_muted}; font-size: 9px; border: none; margin-top: 4px;")
        layout.addWidget(self.hazards_header)
        self.hazards_layout = QVBoxLayout()
        self.hazards_layout.setSpacing(1)
        layout.addLayout(self.hazards_layout)

        self.area_label = QLabel("Affected Area: —")
        self.altitude_label = QLabel("Main Altitude: —")
        self.valid_time_label = QLabel("Valid Time: —")
        for label in (self.area_label, self.altitude_label, self.valid_time_label):
            label.setStyleSheet(f"color: {TOKENS.text_secondary}; font-size: 9px; border: none; margin-top: 3px;")
            layout.addWidget(label)

        confidence_row = QHBoxLayout()
        confidence_label = QLabel("Confidence")
        confidence_label.setStyleSheet(f"color: {TOKENS.text_muted}; font-size: 9px; border: none;")
        self.confidence_value_label = QLabel("—")
        self.confidence_value_label.setStyleSheet(f"color: {TOKENS.text_primary}; font-size: 9px; font-weight: bold; border: none;")
        confidence_row.addWidget(confidence_label)
        confidence_row.addStretch()
        confidence_row.addWidget(self.confidence_value_label)
        layout.addLayout(confidence_row)
        self.confidence_bar = QFrame()
        self.confidence_bar.setFixedHeight(4)
        self.confidence_bar.setStyleSheet(f"background-color: {TOKENS.border}; border-radius: 2px;")
        layout.addWidget(self.confidence_bar)
        self._confidence_fill = QFrame(self.confidence_bar)
        self._confidence_fill.setStyleSheet(f"background-color: {TOKENS.accent_real}; border-radius: 2px;")
        self._confidence_fill.setGeometry(0, 0, 0, 4)

    def update_data(
        self,
        module_scores: dict[str, float],
        overall_awci: float,
        physical_score: float | None,
        forecast_score: float | None,
        area: str,
        altitude: str,
        valid_time: str,
        confidence_pct: float,
    ) -> None:
        level = level_for(overall_awci)
        self.severity_label.setText(level)
        color = risk_qcolor(level)
        self.severity_label.setStyleSheet(
            f"color: rgb({color.red()},{color.green()},{color.blue()}); font-size: 14px; font-weight: bold; border: none;"
        )

        while self.hazards_layout.count():
            item = self.hazards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        elevated = compute_elevated_risks(module_scores, overall_awci, physical_score, forecast_score)
        if not elevated:
            no_hazard_label = QLabel("None currently elevated")
            no_hazard_label.setStyleSheet(f"color: {TOKENS.text_muted}; font-size: 9px; border: none;")
            self.hazards_layout.addWidget(no_hazard_label)
        for icon, label_text, hazard_level, _score in elevated:
            row = QHBoxLayout()
            name_label = QLabel(f"{icon} {label_text}")
            name_label.setStyleSheet(f"color: {TOKENS.text_secondary}; font-size: 9px; border: none;")
            hazard_color = risk_qcolor(hazard_level)
            level_label = QLabel(hazard_level)
            level_label.setStyleSheet(
                f"color: rgb({hazard_color.red()},{hazard_color.green()},{hazard_color.blue()}); "
                "font-size: 9px; font-weight: bold; border: none;"
            )
            row.addWidget(name_label)
            row.addStretch()
            row.addWidget(level_label)
            self.hazards_layout.addLayout(row)

        self.area_label.setText(f"Affected Area: {area}")
        self.altitude_label.setText(f"Main Altitude: {altitude}")
        self.valid_time_label.setText(f"Valid Time: {valid_time}")
        self.confidence_value_label.setText(f"{confidence_pct:.0f}%")
        bar_width = int(self.confidence_bar.width() * max(0.0, min(1.0, confidence_pct / 100.0)))
        self._confidence_fill.setGeometry(0, 0, bar_width, 4)

    def resizeEvent(self, event: Any) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        # Real fix: the confidence-bar fill's real width must track the
        # bar's own real current width, not the width at the last
        # update_data() call - a real layout resize otherwise leaves a
        # stale fill.
        pct_text = self.confidence_value_label.text().rstrip("%")
        try:
            pct = float(pct_text) if pct_text else 0.0
        except ValueError:
            pct = 0.0
        bar_width = int(self.confidence_bar.width() * max(0.0, min(1.0, pct / 100.0)))
        self._confidence_fill.setGeometry(0, 0, bar_width, 4)


class AWCIModelAgreementCard(QFrame):
    """Real "Model Agreement" card - see module docstring: real
    `model_disagreement` module score (100 - disagreement = agreement),
    honestly ~100% ("high agreement") by default since ACF has no real
    multi-model ensemble wired in here yet - never a fabricated
    non-trivial disagreement."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {TOKENS.bg_card}; border-radius: {TOKENS.radius_md}px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        title = QLabel("MODEL AGREEMENT")
        title.setStyleSheet(f"color: {TOKENS.text_secondary}; font-size: 10px; font-weight: bold; border: none;")
        layout.addWidget(title)
        self.level_label = QLabel("—")
        self.level_label.setStyleSheet(f"color: {TOKENS.text_primary}; font-size: 14px; font-weight: bold; border: none;")
        layout.addWidget(self.level_label)
        self.detail_label = QLabel("")
        self.detail_label.setWordWrap(True)
        self.detail_label.setStyleSheet(f"color: {TOKENS.text_muted}; font-size: 9px; border: none; margin-top: 4px;")
        layout.addWidget(self.detail_label)
        layout.addStretch()

    #: level_for() is a hazard-severity scale (higher score = worse,
    #: "Extreme" = worst) - real, correct when applied to the real
    #: model_disagreement score itself (higher disagreement IS worse),
    #: but "Model Agreement" needs the OPPOSITE-sense label: real bug
    #: found via direct construction ("Model Agreement: Extreme" for a
    #: real disagreement of 0.0, i.e. perfect real agreement) - fixed
    #: by classifying the real disagreement score on the real hazard
    #: scale first (so the COLOR stays correctly danger-oriented -
    #: green for low real disagreement), then translating that level
    #: name to its real agreement-sense opposite for the TEXT.
    _AGREEMENT_LABELS: dict[str, str] = {
        "Very Low": "Very High",
        "Low": "High",
        "Moderate": "Moderate",
        "High": "Low",
        "Very High": "Very Low",
        "Extreme": "Very Low",
    }

    def update_data(self, module_scores: dict[str, float]) -> None:
        disagreement = float(module_scores.get("model_disagreement", 0.0))
        disagreement_level = level_for(disagreement)
        agreement_label = self._AGREEMENT_LABELS[disagreement_level]
        self.level_label.setText(agreement_label)
        color = risk_qcolor(disagreement_level)
        self.level_label.setStyleSheet(
            f"color: rgb({color.red()},{color.green()},{color.blue()}); font-size: 14px; font-weight: bold; border: none;"
        )
        if disagreement == 0.0:
            self.detail_label.setText("No real multi-model ensemble wired in yet - real default (perfect agreement).")
        else:
            self.detail_label.setText(f"Real model_disagreement score: {disagreement:.0f}/100")


#: Real airport reference points to summarize here - a small, fixed
#: subset of awci_dashboard.py's own real _AIRPORTS table (same real
#: ICAO codes/coordinates, not a second/duplicated list).
DEFAULT_AIRPORT_ICAO_CODES: tuple[str, ...] = ("DAAG", "DTTA", "HLLT", "LFPG", "EGLL")


class AWCIAirportTable(QFrame):
    """Real "Airport Complexity" table - see module docstring. Each
    row's AWCI/trend/status is computed by `AWCIDashboard._compute_
    airport_complexity_rows()` (kept there since it needs the real
    AWCICalculator/_synthetic_inputs pipeline this widget does not
    import, to stay a plain display widget)."""

    def __init__(self, parent: QWidget | None = None, on_view_all: Any = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {TOKENS.bg_card}; border-radius: {TOKENS.radius_md}px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        title = QLabel("AIRPORT COMPLEXITY")
        title.setStyleSheet(f"color: {TOKENS.text_secondary}; font-size: 10px; font-weight: bold; border: none;")
        layout.addWidget(title)

        header_row = QHBoxLayout()
        for text, stretch in (("Airport", 3), ("AWCI", 1), ("Trend", 1), ("Status", 2)):
            header_label = QLabel(text)
            header_label.setStyleSheet(f"color: {TOKENS.text_muted}; font-size: 8px; border: none;")
            header_row.addWidget(header_label, stretch=stretch)
        layout.addLayout(header_row)

        self._rows_layout = QVBoxLayout()
        self._rows_layout.setSpacing(3)
        layout.addLayout(self._rows_layout)

        self.view_all_button = QPushButton("View all airports")
        self.view_all_button.setFlat(True)
        self.view_all_button.setStyleSheet(
            f"QPushButton {{ color: {TOKENS.accent_primary}; font-size: 9px; text-align: left; border: none; }}"
            "QPushButton:hover { text-decoration: underline; }"
        )
        if on_view_all is not None:
            self.view_all_button.clicked.connect(on_view_all)
        layout.addWidget(self.view_all_button)

    def update_data(self, rows: list[dict[str, Any]]) -> None:
        """rows: list of {icao, awci, trend, level} - see
        AWCIDashboard._compute_airport_complexity_rows()'s own
        docstring for how each is really computed."""
        while self._rows_layout.count():
            item = self._rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for row in rows:
            row_layout = QHBoxLayout()
            icao_label = QLabel(row["icao"])
            icao_label.setStyleSheet(f"color: {TOKENS.text_primary}; font-size: 10px; font-weight: bold; border: none;")
            awci_label = QLabel(f"{row['awci']:.0f}")
            awci_label.setStyleSheet(f"color: {TOKENS.text_primary}; font-size: 10px; border: none;")
            trend_label = QLabel(row["trend"])
            trend_label.setStyleSheet(f"color: {TOKENS.text_secondary}; font-size: 10px; border: none;")
            color = risk_qcolor(row["level"])
            status_label = QLabel(row["level"])
            status_label.setStyleSheet(
                f"color: rgb({color.red()},{color.green()},{color.blue()}); font-size: 9px; font-weight: bold; border: none;"
            )
            row_layout.addWidget(icao_label, stretch=3)
            row_layout.addWidget(awci_label, stretch=1)
            row_layout.addWidget(trend_label, stretch=1)
            row_layout.addWidget(status_label, stretch=2)
            self._rows_layout.addLayout(row_layout)


class AWCIAllAirportsDialog(QDialog):
    """Real "View all airports" dialog - the SAME real per-airport
    computation as AWCIAirportTable's own summary rows, run over every
    entry in awci_dashboard.py's real _AIRPORTS table, not just the 5
    summarized ones."""

    def __init__(self, rows: list[dict[str, Any]], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("All Airports - Real AWCI")
        self.setStyleSheet(dashboard_stylesheet())
        layout = QVBoxLayout(self)
        table = AWCIAirportTable()
        table.view_all_button.hide()
        table.update_data(rows)
        layout.addWidget(table)
        self.resize(360, min(700, 80 + 24 * len(rows)))
