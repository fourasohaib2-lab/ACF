"""
Tests for acf.gui.esoc.panel_manager.EarthMonitoringPanel - upgrading
the "GOES/MTG Satellites" row from a fixed "EXAMPLE"/"1.2 min"
placeholder to the real, live acf.gui.map.mtg_basemap.MTGBasemapProvider
status already feeding every real ACF map view, and honestly relabeling
the other 5 rows (no real connector exists for them anywhere in ACF)
"NOT_CONNECTED" instead of leaving them as an equally fake "EXAMPLE"
(2026-09-06, Phase 57).

Network access is mocked - same convention as tests/test_mtg_basemap.py.
"""

from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pytest
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
    with patch.object(EUMETSATMTGConnector, "fetch_latest_image", return_value=honest_stub):
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


def test_the_5_unconnected_networks_are_honestly_labeled_not_connected(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = EarthMonitoringPanel(registry, dispatcher)

    for row in range(1, 6):
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
