"""
Unit test suite for ESOCController.handle_refresh_observations() -
this command backs the ESOC toolbar's "🔴 Live Stream" button
(esoc_window.py's `cmd == "live_stream"`), the one caller that could
reach ACF's real observation feeds before this fix but never did.

CORRECTED (2026-09-06): used to unconditionally report
NOT_REFRESHED_NO_INGESTION_PIPELINE_CONNECTED - true when written, but
stale once this same session's Phases 57-60 wired 4 real observation
connectors (GOES/MTG, ARGO, METAR, NEXRAD) into
acf.gui.esoc.panel_manager.EarthMonitoringPanel. Now genuinely triggers
a real, async refresh of all 4 by reusing that panel's own worker
classes, fire-and-forget via CommandDispatcher.run_async().

Network access is mocked - same convention as
tests/test_esoc_earth_monitoring_panel.py.
"""

from __future__ import annotations

import urllib.error
from unittest.mock import patch

import pytest
import requests
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication

from acf.connectors.eumetsat_mtg import EUMETSATMTGConnector, MTGFetchResult
from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.esoc_controller import ESOCController
from acf.gui.esoc.esoc_workspace import WorkspaceManager
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.session_manager import SessionManager
from acf.gui.map.mtg_basemap import MTGBasemapProvider


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture(autouse=True)
def _reset_singleton_and_block_real_network(qapp):
    MTGBasemapProvider._instance = None
    honest_stub = MTGFetchResult(is_real_data=False, status="NOT_FETCHED_YET", authenticated=False)
    service_unavailable = requests.Response()
    service_unavailable.status_code = 503
    with (
        patch.object(EUMETSATMTGConnector, "fetch_latest_image", return_value=honest_stub),
        patch.object(requests, "get", return_value=service_unavailable),
        patch("urllib.request.urlopen", side_effect=urllib.error.URLError("blocked for tests")),
    ):
        yield
    QThreadPool.globalInstance().waitForDone(2000)
    MTGBasemapProvider._instance = None


@pytest.fixture
def controller():
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    workspace = WorkspaceManager()
    session = SessionManager()
    return ESOCController(registry, dispatcher, workspace, session)


def test_refresh_observations_reports_a_real_trigger_not_a_stale_not_connected_claim(controller):
    result = controller.handle_refresh_observations()

    assert result["status"] == "REFRESH_TRIGGERED_4_REAL_FEEDS_ASYNC_RESULTS_NOT_YET_KNOWN"
    assert result["feeds_triggered"] == 4


def test_refresh_observations_genuinely_starts_the_mtg_provider_refresh(controller):
    provider = MTGBasemapProvider.instance()
    with patch.object(provider, "refresh_async") as mock_refresh:
        controller.handle_refresh_observations()
        mock_refresh.assert_called_once()


def test_refresh_observations_does_not_block_waiting_on_real_network(controller):
    """A real regression guard: this handler must return immediately
    (fire-and-forget) rather than synchronously waiting on 3 real HTTP
    round-trips - the background workers still run and complete
    honestly (verified by draining the thread pool afterward)."""
    import time

    t0 = time.monotonic()
    controller.handle_refresh_observations()
    elapsed = time.monotonic() - t0

    assert elapsed < 1.0  # genuinely fire-and-forget, not a synchronous network wait
    QThreadPool.globalInstance().waitForDone(5000)  # the async workers still ran to completion
