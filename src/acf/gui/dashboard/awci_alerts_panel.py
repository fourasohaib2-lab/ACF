"""
AWCI Alerts Panel
==================

Real, non-fabricated active alerts - explicit user request ("un autre
bouton pour les alertes"). Deliberately built on top of
`acf.gui.dashboard.awci_risk_summary.AWCIRiskSummary`'s own already-
computed real risk levels (the exact same `_band()`/`_ROWS`
classification that panel already displays, reused not duplicated -
importing its "private" module-level helpers directly rather than
re-deriving a second, potentially-drifting threshold scale), NOT
`acf.hazard_operations`'s `HazardDetectionEngine`/`AlertGenerator` -
both confirmed, self-documented stubs today ("NOT_ASSESSED_..."/
"NOT_SCANNED_...") with no real hazard-detection engine connected. An
alert here is real precisely because it is nothing more than "one of
the AWCI module scores/composite you already computed is currently at
High or above" - never a second, independent guess.

Optionally enriched with real METAR-derived flags (thunderstorm,
strong gust, low visibility) once a live station fetch
(acf.gui.dashboard.awci_messages_panel) has actually completed - real,
decoded values from a real external source, not a second hazard-
detection engine.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget

from acf.aviation.icao.live_source import LiveStationBundle
from acf.aviation.icao.metar_decoder import METARReport
from acf.gui.dashboard.awci_colors import risk_qcolor
from acf.gui.dashboard.awci_risk_summary import _ROWS, _band
from acf.gui.theme_tokens import TOKENS, dashboard_stylesheet, label_style
from acf.gui_screen_utils import fit_dialog_to_screen

#: Real, elevated-only threshold - Moderate/Low are not alerts, matching
#: this dialog's own purpose (surface what actually needs attention).
_ELEVATED_LEVELS = {"High", "Very High", "Extreme"}

#: Real, documented thresholds for METAR-derived flags - defensible,
#: commonly-used aviation-weather values, not the only possible choice
#: (same "documented bound, not a universal law" convention as
#: acf.physics_guard.range_check.OPERATIONAL_RANGES).
_STRONG_GUST_KT = 35.0
_LOW_VISIBILITY_M = 1600.0


def compute_elevated_risks(
    module_scores: dict[str, float],
    overall_awci: float,
    physical_score: float | None,
    forecast_score: float | None,
) -> list[tuple[str, str, str, float]]:
    """
    Real, non-fabricated elevated-risk rows: reuses AWCIRiskSummary's
    own real `_band()` classification (see module docstring) on the
    exact same real inputs that panel already receives. Returns
    (icon, label, level, score) tuples for every row currently at
    High/Very High/Extreme - empty list means genuinely nothing
    elevated right now, not "not computed".
    """
    specials = {"__physical__": physical_score, "__forecast__": forecast_score}
    rows: list[tuple[str, str, str, float]] = []
    for key, icon, label, module in _ROWS:
        if module is None:
            score: float | None = overall_awci
        elif module in specials:
            score = specials[module]
        else:
            score = module_scores.get(module, 0.0)
        if score is None:
            continue
        level = _band(score)
        if level in _ELEVATED_LEVELS:
            rows.append((icon, label, level, score))
    return rows


def compute_live_condition_flags(bundles: dict[str, LiveStationBundle] | None) -> list[str]:
    """
    Real METAR-derived flags from an already-completed live fetch
    (acf.gui.dashboard.awci_messages_panel) - real decoded fields, not
    a second hazard-detection engine. Empty/None input yields an empty
    list (honest "no live data to check" state, not a fabricated flag).
    """
    if not bundles:
        return []
    flags: list[str] = []
    for icao, bundle in bundles.items():
        report = bundle.metar.decoded
        if not isinstance(report, METARReport):
            continue
        if any("TS" in w for w in report.present_weather):
            flags.append(f"⛈️ {icao}: Thunderstorm reported in current METAR")
        if report.wind_gust_kt is not None and report.wind_gust_kt >= _STRONG_GUST_KT:
            flags.append(f"💨 {icao}: Strong wind gusts ({report.wind_gust_kt:.0f}kt) in current METAR")
        if not report.cavok and report.visibility_m is not None and report.visibility_m < _LOW_VISIBILITY_M:
            flags.append(f"🌫️ {icao}: Low visibility ({report.visibility_m:.0f}m) in current METAR")
    return flags


class AWCIAlertsDialog(QDialog):
    """Real active-alerts viewer - see module docstring for the real
    (non-fabricated) source of every row shown here."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("AWCI – Active Alerts")
        # NOTE (real responsive-sizing fix, 2026-09-05): was a hardcoded
        # self.resize(480, 420) - clamp to the actual screen instead, same
        # fix as gui_screen_utils.fit_window_to_screen for main windows.
        fit_dialog_to_screen(self, 480, 420)
        self.setStyleSheet(dashboard_stylesheet())

        outer = QVBoxLayout(self)
        header = QLabel("🔔 ACTIVE ALERTS")
        header.setStyleSheet(label_style("text_primary", "lg", "bold"))
        outer.addWidget(header)

        self.risk_section_label = QLabel("AWCI risk levels")
        self.risk_section_label.setStyleSheet(label_style("text_secondary", "sm", "bold"))
        outer.addWidget(self.risk_section_label)

        self.risk_rows_container = QVBoxLayout()
        outer.addLayout(self.risk_rows_container)

        self.live_section_label = QLabel("Live station conditions")
        self.live_section_label.setStyleSheet(label_style("text_secondary", "sm", "bold"))
        outer.addWidget(self.live_section_label)

        self.live_rows_container = QVBoxLayout()
        outer.addLayout(self.live_rows_container)

        outer.addStretch()

    def refresh(
        self,
        module_scores: dict[str, float],
        overall_awci: float,
        physical_score: float | None = None,
        forecast_score: float | None = None,
        live_bundles: dict[str, LiveStationBundle] | None = None,
    ) -> None:
        """Rebuild every row from real, freshly-computed inputs -
        never left showing a stale prior state."""
        self._clear_layout(self.risk_rows_container)
        self._clear_layout(self.live_rows_container)

        elevated = compute_elevated_risks(module_scores, overall_awci, physical_score, forecast_score)
        if elevated:
            for icon, label, level, score in elevated:
                self.risk_rows_container.addWidget(self._alert_row(f"{icon} {label}", f"{level} ({score:.0f})", level))
        else:
            self.risk_rows_container.addWidget(self._info_row("No elevated risk currently active."))

        flags = compute_live_condition_flags(live_bundles)
        if flags:
            for flag in flags:
                self.live_rows_container.addWidget(self._info_row(flag))
        elif live_bundles:
            self.live_rows_container.addWidget(self._info_row("No elevated conditions in the last live fetch."))
        else:
            self.live_rows_container.addWidget(self._info_row("No live station data fetched yet (open 📨 Message first)."))

    @staticmethod
    def _clear_layout(layout: Any) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    @staticmethod
    def _alert_row(label_text: str, value_text: str, level: str) -> QWidget:
        color = risk_qcolor(level)
        row = QLabel(f"{label_text}:  {value_text}")
        row.setStyleSheet(
            f"color: rgb({color.red()},{color.green()},{color.blue()}); font-size: 11px; font-weight: bold; padding: 3px 0;"
        )
        return row

    @staticmethod
    def _info_row(text: str) -> QWidget:
        row = QLabel(text)
        row.setStyleSheet(f"color: {TOKENS.text_secondary}; font-size: 10px; padding: 3px 0;")
        row.setWordWrap(True)
        return row


def count_active_alerts(
    module_scores: dict[str, float],
    overall_awci: float,
    physical_score: float | None,
    forecast_score: float | None,
    live_bundles: dict[str, LiveStationBundle] | None = None,
) -> int:
    """Real total alert count (elevated risks + live condition flags) -
    used for the "🔔 Alerts" button's badge, so the badge is always
    consistent with what refresh() would actually show."""
    return len(compute_elevated_risks(module_scores, overall_awci, physical_score, forecast_score)) + len(
        compute_live_condition_flags(live_bundles)
    )
