"""Off-GUI-thread fetch workers for ACF's real, no-auth-required observation
connectors (ARGO floats, METAR/TAF stations, NEXRAD radar, PIREP reports).

Extracted from the former acf.gui.esoc.panel_manager (ESOC dashboard,
removed) so acf.gui.dashboard.acf_workstation - the ACF Scientific
Workstation's real Earth Monitoring "Observations" dialog - keeps a
real, working off-thread fetch path with zero duplicated logic.
"""

from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Signal

_logger = logging.getLogger("acf.gui.workers.observation_fetch_workers")


class _ArgoFetchSignals(QObject):
    """QRunnable itself cannot be a QObject (no signals) - same
    companion-object pattern as acf.gui.map.mtg_basemap._MTGFetchSignals."""

    finished = Signal(object)  # ArgoFetchResult


class _ArgoFetchWorker(QRunnable):
    """Runs ArgoFloatsConnector.fetch_recent_profiles() off the GUI
    thread - a synchronous network call there would freeze the panel."""

    def __init__(self, connector: Any) -> None:
        super().__init__()
        self._connector = connector
        self.signals = _ArgoFetchSignals()

    def run(self) -> None:
        try:
            result = self._connector.fetch_recent_profiles()
            self.signals.finished.emit(result)
        except Exception:  # pragma: no cover - defensive, mirrors _MTGFetchWorker
            _logger.exception("Argo profile fetch failed in background worker")


class _METARFetchSignals(QObject):
    """QRunnable itself cannot be a QObject (no signals) - same
    companion-object pattern as acf.gui.map.mtg_basemap._MTGFetchSignals."""

    finished = Signal(int, int)  # (stations_reporting, stations_total)


class _METARFetchWorker(QRunnable):
    """Polls acf.aviation.icao.live_source.fetch_raw_report("metar", ...)
    for every real station in REAL_STATIONS, off the GUI thread - 4
    sequential real HTTP calls there would freeze the panel."""

    def __init__(self) -> None:
        super().__init__()
        self.signals = _METARFetchSignals()

    def run(self) -> None:
        from acf.aviation.icao.live_source import REAL_STATIONS, LiveReportUnavailable, fetch_raw_report

        reporting = 0
        try:
            for icao_code in REAL_STATIONS:
                try:
                    fetch_raw_report("metar", icao_code)
                    reporting += 1
                except LiveReportUnavailable:
                    pass  # this one station has no current report - not a fetch-wide failure
            self.signals.finished.emit(reporting, len(REAL_STATIONS))
        except Exception:  # pragma: no cover - defensive, mirrors _ArgoFetchWorker
            _logger.exception("METAR station poll failed in background worker")


class _NexradFetchSignals(QObject):
    """QRunnable itself cannot be a QObject (no signals) - same
    companion-object pattern as acf.gui.map.mtg_basemap._MTGFetchSignals."""

    finished = Signal(object)  # NexradFetchResult


class _NexradFetchWorker(QRunnable):
    """Runs NEXRADRadarConnector.fetch_station_status() off the GUI
    thread - several sequential real HTTP calls there would freeze the
    panel."""

    def __init__(self, connector: Any) -> None:
        super().__init__()
        self._connector = connector
        self.signals = _NexradFetchSignals()

    def run(self) -> None:
        try:
            result = self._connector.fetch_station_status()
            self.signals.finished.emit(result)
        except Exception:  # pragma: no cover - defensive, mirrors _ArgoFetchWorker
            _logger.exception("NEXRAD station poll failed in background worker")


class _PIREPFetchSignals(QObject):
    """QRunnable itself cannot be a QObject (no signals) - same
    companion-object pattern as acf.gui.map.mtg_basemap._MTGFetchSignals."""

    finished = Signal(object)  # PIREPFetchResult


class _PIREPFetchWorker(QRunnable):
    """Runs PIREPConnector.fetch_recent_reports() off the GUI thread -
    a synchronous network call there would freeze the panel."""

    def __init__(self, connector: Any) -> None:
        super().__init__()
        self._connector = connector
        self.signals = _PIREPFetchSignals()

    def run(self) -> None:
        try:
            result = self._connector.fetch_recent_reports()
            self.signals.finished.emit(result)
        except Exception:  # pragma: no cover - defensive, mirrors _ArgoFetchWorker
            _logger.exception("PIREP fetch failed in background worker")
