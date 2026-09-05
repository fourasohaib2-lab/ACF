"""
AWCI Messages Panel
====================

Real, live METAR/TAF/SIGMET aviation weather messages - explicit user
request: "le but est de brancher acf et awci avec des vrais station
pour nous rendre des vrai reponse instantanément" (connect ACF/AWCI to
real stations for real, instant responses). Fetches real, current text
from the public NOAA Aviation Weather Center API
(acf.aviation.icao.live_source) and decodes it with this project's own
real METAR/TAF/SIGMET decoders - both existed before this module, but
neither was ever wired into anything the app actually shows.

SPECI/SPECIAL are not a separate code path here: they are the exact
same real ICAO TAC grammar as a routine METAR (a station issues a
SPECI instead of a METAR only when a significant change occurred -
whichever one the real feed currently holds is displayed as-is,
METARDecoder.decode() already recognizes both keywords). Nothing here
distinguishes or fabricates that distinction.
"""

from __future__ import annotations

import logging

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QTabWidget, QTextEdit, QVBoxLayout, QWidget

from acf.aviation.icao.live_source import REAL_STATIONS, LiveReport, LiveStationBundle, fetch_active_sigmets, fetch_and_decode_station
from acf.aviation.icao.metar_decoder import METARReport, metar_report_quality
from acf.aviation.icao.sigmet_decoder import SIGMETReport
from acf.aviation.icao.taf_decoder import TAFForecastPeriod, TAFReport
from acf.gui.theme_tokens import TOKENS, dashboard_stylesheet, label_style
from acf.gui_screen_utils import fit_dialog_to_screen

logger = logging.getLogger("acf.gui.dashboard.awci_messages_panel")


def _format_metar_quality(report: METARReport) -> str:
    """
    Real per-variable quality line (docs/ACF_MASTER_PROMPT.md section
    32) for this real, live, decoded METAR - closes the quality-
    flagging half of "brancher acf et awci avec des vrais station" for
    the values this panel already displays. VALID entries are folded
    into a single count rather than listed individually (a station
    with 4 real values, all VALID, doesn't need 4 separate lines) - any
    non-VALID status is shown in full, since that is the real,
    actionable signal this line exists to surface.
    """
    quality = metar_report_quality(report)
    if not quality:
        return "Quality (§32): no assessable variables in this report."

    n_valid = sum(1 for s in quality.values() if s.status == "VALID")
    problems = [f"{s.variable}={s.status}" for s in quality.values() if s.status != "VALID"]

    if not problems:
        return f"Quality (§32): {n_valid}/{len(quality)} variable(s) VALID."
    return f"Quality (§32): {n_valid}/{len(quality)} VALID — ⚠ " + ", ".join(problems)


def _format_metar_summary(report: METARReport) -> str:
    lines = [f"Station: {report.icao_code}"]
    if report.day is not None:
        lines.append(f"Time: day {report.day:02d} {report.hour:02d}:{report.minute:02d}Z" + (" (AUTO)" if report.is_auto else ""))
    if report.wind_variable_direction:
        wind = "Variable direction"
    elif report.wind_direction_deg is not None:
        wind = f"{report.wind_direction_deg:03d}°"
    else:
        wind = "Calm/unknown"
    if report.wind_speed_kt is not None:
        wind += f" at {report.wind_speed_kt:.0f} kt"
    if report.wind_gust_kt:
        wind += f", gusting {report.wind_gust_kt:.0f} kt"
    lines.append(f"Wind: {wind}")
    if report.cavok:
        lines.append("Visibility: CAVOK (ceiling and visibility OK)")
    elif report.visibility_m is not None:
        lines.append(f"Visibility: {report.visibility_m:.0f} m")
    if report.cloud_layers:
        clouds = ", ".join(
            f"{c.get('coverage')} {c.get('base_ft')}ft" + (f" {c['type']}" if c.get("type") else "") for c in report.cloud_layers
        )
        lines.append(f"Clouds: {clouds}")
    if report.vertical_visibility_ft is not None:
        lines.append(f"Vertical visibility: {report.vertical_visibility_ft}ft")
    if report.temperature_c is not None:
        dew = f" / dewpoint {report.dewpoint_c:.0f}°C" if report.dewpoint_c is not None else ""
        lines.append(f"Temperature: {report.temperature_c:.0f}°C{dew}")
    if report.qnh_hpa is not None:
        lines.append(f"QNH: {report.qnh_hpa:.0f} hPa")
    if report.present_weather:
        lines.append(f"Weather: {', '.join(report.present_weather)}")
    if report.trend:
        lines.append(f"Trend: {report.trend}")
    return "\n".join(lines)


def _format_taf_period(period: TAFForecastPeriod) -> str:
    header = period.change_type
    if period.probability:
        header += f" (PROB{period.probability})"
    parts = [header]
    if period.wind_speed_kt is not None:
        wind = "Variable" if period.wind_variable else (f"{period.wind_direction_deg:03d}°" if period.wind_direction_deg is not None else "?")
        wind += f" {period.wind_speed_kt:.0f}kt"
        if period.wind_gust_kt:
            wind += f" gust {period.wind_gust_kt:.0f}kt"
        parts.append(wind)
    if period.cavok:
        parts.append("CAVOK")
    elif period.visibility_m is not None:
        parts.append(f"vis {period.visibility_m:.0f}m")
    if period.cloud_layers:
        parts.append(", ".join(f"{c.get('coverage')} {c.get('base_ft')}ft" for c in period.cloud_layers))
    if period.present_weather:
        parts.append(", ".join(period.present_weather))
    return "  " + " - ".join(parts)


def _format_taf_summary(report: TAFReport) -> str:
    lines = [f"Station: {report.icao_code}"]
    if report.is_amended:
        lines.append("(Amended - AMD)")
    if report.is_corrected:
        lines.append("(Corrected - COR)")
    if report.valid_from_day is not None:
        lines.append(
            f"Valid: day {report.valid_from_day:02d} {report.valid_from_hour:02d}Z "
            f"through day {report.valid_until_day:02d} {report.valid_until_hour:02d}Z"
        )
    lines.append(f"{len(report.periods)} real forecast period(s):")
    for period in report.periods:
        lines.append(_format_taf_period(period))
    return "\n".join(lines)


def _format_sigmet_summary(report: SIGMETReport) -> str:
    lines = []
    if report.fir_code:
        fir_line = f"FIR: {report.fir_code}"
        if report.sequence_number:
            fir_line += f"  Seq: {report.sequence_number}"
        lines.append(fir_line)
    if report.phenomenon:
        sev = f"{report.severity} " if report.severity else ""
        lines.append(f"Phenomenon: {sev}{report.phenomenon}")
    if report.flight_level_bottom is not None or report.flight_level_top is not None:
        lines.append(f"Flight levels: FL{report.flight_level_bottom or 0}-FL{report.flight_level_top or '?'}")
    if report.is_stationary:
        lines.append("Movement: stationary")
    elif report.movement_dir:
        lines.append(f"Movement: {report.movement_dir} at {report.movement_speed_kt or '?'}kt")
    if report.location_text:
        lines.append(f"Location: {report.location_text}")
    return "\n".join(lines) if lines else "(no structurally-parsed fields)"


class _MessagesWorkerSignals(QObject):
    """QRunnable itself cannot be a QObject - same companion-object
    pattern as _RealFieldWorkerSignals (awci_dashboard.py) /
    _AWCIFieldWorkerSignals (esoc_window.py), reused not duplicated."""

    finished = Signal(dict, list)  # {icao: LiveStationBundle}, [LiveReport] (sigmets)
    failed = Signal(str)


class _MessagesWorker(QRunnable):
    """Fetches every real station's METAR/TAF plus active SIGMETs off
    the GUI thread."""

    def __init__(self) -> None:
        super().__init__()
        self.signals = _MessagesWorkerSignals()

    def run(self) -> None:
        try:
            bundles = {icao: fetch_and_decode_station(icao) for icao in REAL_STATIONS}
            sigmets = fetch_active_sigmets()
        except Exception as exc:  # noqa: BLE001 - must not crash the worker thread
            logger.exception("AWCI Messages: live fetch failed")
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(bundles, sigmets)


class AWCIMessagesDialog(QDialog):
    """Real, live METAR/TAF/SIGMET viewer - one tab per real station
    plus a shared SIGMET tab."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("AWCI – Live Aviation Weather Messages")
        # NOTE (real responsive-sizing fix, 2026-09-05): was a hardcoded
        # self.resize(720, 560) - the largest of this codebase's secondary
        # dialogs, and so the most likely to open off-screen on a small
        # display. Clamp to the actual screen instead, same fix as
        # gui_screen_utils.fit_window_to_screen for main windows.
        fit_dialog_to_screen(self, 720, 560)
        self.setStyleSheet(dashboard_stylesheet())

        outer = QVBoxLayout(self)
        header_row = QHBoxLayout()
        header = QLabel("📨 LIVE MESSAGES — METAR / TAF / SPECI / SIGMET")
        header.setStyleSheet(label_style("text_primary", "lg", "bold"))
        header_row.addWidget(header)
        header_row.addStretch()
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self.refresh)
        header_row.addWidget(self.refresh_button)
        outer.addLayout(header_row)

        self.status_label = QLabel("Not yet fetched.")
        self.status_label.setStyleSheet(label_style("text_muted", "sm"))
        outer.addWidget(self.status_label)

        # Real last-fetched bundles - read by AWCIAlertsDialog (via
        # AWCIDashboard._open_alerts()) for its "Live station
        # conditions" section, so a live fetch made here is genuinely
        # shared rather than the two dialogs staying independent.
        self.last_bundles: dict[str, LiveStationBundle] | None = None

        self.tabs = QTabWidget()
        outer.addWidget(self.tabs, stretch=1)

        self.station_text_edits: dict[str, QTextEdit] = {}
        for icao in REAL_STATIONS:
            edit = QTextEdit()
            edit.setReadOnly(True)
            edit.setStyleSheet(f"font-family: monospace; background-color: {TOKENS.bg_card}; color: {TOKENS.text_primary};")
            edit.setPlainText("Not yet fetched.")
            self.tabs.addTab(edit, icao)
            self.station_text_edits[icao] = edit

        self.sigmet_text_edit = QTextEdit()
        self.sigmet_text_edit.setReadOnly(True)
        self.sigmet_text_edit.setStyleSheet(f"font-family: monospace; background-color: {TOKENS.bg_card}; color: {TOKENS.text_primary};")
        self.sigmet_text_edit.setPlainText("Not yet fetched.")
        self.tabs.addTab(self.sigmet_text_edit, "SIGMET")

        self.refresh()

    def refresh(self) -> None:
        self.refresh_button.setEnabled(False)
        self.status_label.setText("⏳ Fetching live METAR/TAF/SIGMET (aviationweather.gov)…")
        worker = _MessagesWorker()
        worker.signals.finished.connect(self._on_fetch_ready)
        worker.signals.failed.connect(self._on_fetch_failed)
        QThreadPool.globalInstance().start(worker)

    def _on_fetch_ready(self, bundles: dict[str, LiveStationBundle], sigmets: list[LiveReport]) -> None:
        self.refresh_button.setEnabled(True)
        self.last_bundles = bundles
        n_ok = sum(1 for b in bundles.values() if b.metar.raw_text is not None)
        self.status_label.setText(f"✅ Live data fetched for {n_ok}/{len(bundles)} station(s).")

        for icao, bundle in bundles.items():
            lines = [f"=== METAR/SPECI — {icao} ==="]
            if bundle.metar.raw_text:
                lines.append(bundle.metar.raw_text)
                lines.append("")
                if isinstance(bundle.metar.decoded, METARReport):
                    lines.append(_format_metar_summary(bundle.metar.decoded))
                    lines.append("")
                    lines.append(_format_metar_quality(bundle.metar.decoded))
                elif bundle.metar.error:
                    lines.append(f"⚠ {bundle.metar.error}")
            else:
                lines.append(f"⚠ Live data unavailable: {bundle.metar.error}")

            lines.append("")
            lines.append(f"=== TAF — {icao} ===")
            if bundle.taf.raw_text:
                lines.append(bundle.taf.raw_text)
                lines.append("")
                if isinstance(bundle.taf.decoded, TAFReport):
                    lines.append(_format_taf_summary(bundle.taf.decoded))
                elif bundle.taf.error:
                    lines.append(f"⚠ {bundle.taf.error}")
            else:
                lines.append(f"⚠ Live data unavailable: {bundle.taf.error}")

            self.station_text_edits[icao].setPlainText("\n".join(lines))

        if sigmets:
            sigmet_lines = []
            for report in sigmets:
                sigmet_lines.append(report.raw_text or "")
                if isinstance(report.decoded, SIGMETReport):
                    sigmet_lines.append(_format_sigmet_summary(report.decoded))
                elif report.error:
                    sigmet_lines.append(f"⚠ {report.error}")
                sigmet_lines.append("-" * 40)
            self.sigmet_text_edit.setPlainText("\n".join(sigmet_lines))
        else:
            self.sigmet_text_edit.setPlainText("No active SIGMETs fetched (or live data unavailable).")

    def _on_fetch_failed(self, message: str) -> None:
        self.refresh_button.setEnabled(True)
        self.status_label.setText(f"⚠ Live fetch failed: {message}")
        logger.error("AWCI Messages: live fetch failed: %s", message)
