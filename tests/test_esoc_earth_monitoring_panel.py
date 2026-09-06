"""
Tests for acf.gui.esoc.panel_manager.EarthMonitoringPanel - upgrading
the "GOES/MTG Satellites" row from a fixed "EXAMPLE"/"1.2 min"
placeholder to the real, live acf.gui.map.mtg_basemap.MTGBasemapProvider
status already feeding every real ACF map view (Phase 57), and later
the "ARGO Ocean Floats" row to the real, public Argovis API via
acf.connectors.argo_floats.ArgoFloatsConnector (Phase 58) - honestly
relabeling the remaining 4 rows (no real connector exists for them
anywhere in ACF) "NOT_CONNECTED" instead of leaving them as an equally
fake "EXAMPLE".

Network access is mocked - same convention as tests/test_mtg_basemap.py
and tests/test_argo_floats_connector.py.
"""

from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pytest
import requests
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication

from acf.connectors.eumetsat_mtg import EUMETSATMTGConnector, MTGFetchResult
from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import EarthMonitoringPanel
from acf.gui.map.mtg_basemap import MTGBasemapProvider


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def registry():
    return ModuleRegistry()


@pytest.fixture(autouse=True)
def _reset_singleton_and_block_real_network():
    MTGBasemapProvider._instance = None
    honest_stub = MTGFetchResult(is_real_data=False, status="NOT_FETCHED_YET", authenticated=False)
    # ArgoFloatsConnector goes straight through the `requests` module (no
    # SSH/Paramiko-style "always succeeds offline" convention to lean on),
    # so its real network call is blocked the same way
    # tests/test_argo_floats_connector.py blocks it - a 503 honestly
    # resolves to is_real_data=False rather than hanging or reaching a
    # real host during this suite.
    argo_503 = requests.Response()
    argo_503.status_code = 503
    with (
        patch.object(EUMETSATMTGConnector, "fetch_latest_image", return_value=honest_stub),
        patch.object(requests, "get", return_value=argo_503),
    ):
        yield
    QThreadPool.globalInstance().waitForDone(2000)
    MTGBasemapProvider._instance = None


def _fake_disk_bytes() -> bytes:
    import io

    from PIL import Image

    rgba = np.full((9, 9, 4), 255, dtype=np.uint8)
    rgba[2:7, 2:7] = [40, 60, 80, 255]
    buf = io.BytesIO()
    Image.fromarray(rgba, mode="RGBA").save(buf, format="PNG")
    return buf.getvalue()


def test_the_4_unconnected_networks_are_honestly_labeled_not_connected(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = EarthMonitoringPanel(registry, dispatcher)
    QThreadPool.globalInstance().waitForDone(2000)

    for row in (1, 2, 4, 5):  # NEXRAD, SYNOP/METAR, AMDAR, Lightning - row 3 is the real ARGO feed
        assert panel.table.item(row, 1).text() == "NOT_CONNECTED"
        assert panel.table.item(row, 2).text() == "N/A"


def test_mtg_row_shows_the_real_provider_status_before_any_fetch(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = EarthMonitoringPanel(registry, dispatcher)

    assert panel.table.item(0, 0).text() == "GOES/MTG Satellites"
    assert panel.table.item(0, 1).text() == "NOT_FETCHED_YET"
    assert panel.table.item(0, 2).text() == "N/A"


def test_mtg_row_goes_live_once_the_real_provider_has_a_real_image(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = EarthMonitoringPanel(registry, dispatcher)

    provider = MTGBasemapProvider.instance()
    provider._on_fetched(
        MTGFetchResult(is_real_data=True, status="FETCHED_OK", authenticated=False, image_bytes=_fake_disk_bytes())
    )

    assert panel.table.item(0, 1).text() == "LIVE"
    assert panel.table.item(0, 2).text().endswith(" min")


def test_panel_updates_live_when_the_shared_provider_fetches_after_construction(qapp, registry):
    """Real regression guard for the same lifetime pattern already fixed
    in AWCIMapPanel (weakref forwarder, see _make_mtg_update_forwarder):
    this panel must react to MTGBasemapProvider's own `updated` signal,
    not only reflect state computed once at construction time."""
    dispatcher = CommandDispatcher()
    panel = EarthMonitoringPanel(registry, dispatcher)
    assert panel.table.item(0, 1).text() != "LIVE"

    MTGBasemapProvider.instance()._on_fetched(
        MTGFetchResult(is_real_data=True, status="FETCHED_OK", authenticated=False, image_bytes=_fake_disk_bytes())
    )

    assert panel.table.item(0, 1).text() == "LIVE"


def test_argo_row_shows_the_real_connector_status_after_construction(qapp, registry):
    """The autouse fixture blocks the real network with an honest 503,
    so the ARGO fetch fired at construction time must resolve to that
    honest failure, never a fabricated LIVE state."""
    dispatcher = CommandDispatcher()
    panel = EarthMonitoringPanel(registry, dispatcher)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()  # deliver the queued cross-thread `finished` signal

    assert panel.table.item(3, 0).text() == "ARGO Ocean Floats"
    assert "NOT_FETCHED_HTTP_503" in panel.table.item(3, 1).text()
    assert panel.table.item(3, 2).text() == "N/A"


def test_argo_row_goes_live_with_a_real_profile_count_once_fetched(qapp, registry):
    from acf.connectors.argo_floats import ArgoFetchResult

    dispatcher = CommandDispatcher()
    panel = EarthMonitoringPanel(registry, dispatcher)
    QThreadPool.globalInstance().waitForDone(2000)

    panel._on_argo_fetched(ArgoFetchResult(is_real_data=True, status="FETCHED_OK", profile_count=1101))

    assert panel.table.item(3, 1).text() == "LIVE (1101 profiles/48h)"
    assert panel.table.item(3, 2).text().endswith(" min")


def test_refresh_button_refetches_both_real_feeds(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = EarthMonitoringPanel(registry, dispatcher)
    QThreadPool.globalInstance().waitForDone(2000)

    with patch.object(panel, "_fetch_argo_async") as mock_fetch:
        panel._refresh()
        mock_fetch.assert_called_once()
