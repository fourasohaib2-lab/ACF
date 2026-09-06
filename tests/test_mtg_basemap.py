"""
Tests for acf.gui.map.mtg_basemap - the live MTG basemap plumbing shared
by every real map view (explicit user request "je veux que toutes les
maps affiché soient des maps du mtg"). Network access is mocked
(patching EUMETSATMTGConnector.fetch_latest_image, same idea as
test_eumetsat_mtg_connector.py) - this project's own test suite must
not depend on live EUMETSAT access.
"""

from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pytest
from PySide6.QtCore import QThreadPool

from acf.connectors.eumetsat_mtg import EUMETSATMTGConnector, MTGFetchResult
from acf.gui.map import mtg_basemap as mtg_basemap_module
from acf.gui.map.mtg_basemap import (
    MTGBasemapProvider,
    draw_mtg_basemap,
    geostationary_crs,
)


@pytest.fixture(autouse=True)
def _reset_singleton_and_block_real_network():
    """MTGBasemapProvider is a real process-wide singleton by design
    (one shared fetch/cache for every map view) that fetches
    immediately on first construction - reset it around each test so
    tests don't leak state into each other, and patch the connector so
    that automatic first fetch can never make a real HTTP call (tests
    below drive MTGBasemapProvider._on_fetched() directly with crafted
    results instead - deterministic, and this suite must not depend on
    live EUMETSAT access).

    Also waits for QThreadPool to drain before tearing the singleton
    down: without this, a still-running background fetch worker from
    this test can outlive it and try to notify a receiver the next
    test has already reset - _MTGFetchWorker.run() itself already
    survives that (broad except around the whole body - see its own
    NOTE), but Qt Concurrent still prints its own noisy, harmless
    "caught an exception thrown from a worker thread" warning when that
    happens, purely a test-teardown-speed artifact never seen in the
    real app (which does not recreate this singleton every few
    milliseconds).
    """
    MTGBasemapProvider._instance = None
    honest_stub = MTGFetchResult(is_real_data=False, status="NOT_FETCHED_YET", authenticated=False)
    with patch.object(EUMETSATMTGConnector, "fetch_latest_image", return_value=honest_stub):
        yield
    QThreadPool.globalInstance().waitForDone(2000)
    MTGBasemapProvider._instance = None


def _fake_disk_image(size: int = 41) -> np.ndarray:
    """A small synthetic 'full disk' RGBA image: a solid mid-gray disk
    inscribed in an otherwise pure-white square canvas - same real
    convention EUMETSAT's own quicklooks use (confirmed by sampling a
    live one while building this feature), just tiny for a fast test."""
    rgba = np.full((size, size, 4), 255, dtype=np.uint8)
    radius = size / 2.0
    yy, xx = np.mgrid[0:size, 0:size]
    inside = (yy - (size - 1) / 2.0) ** 2 + (xx - (size - 1) / 2.0) ** 2 <= radius**2
    rgba[inside] = [40, 60, 80, 255]
    return rgba


def test_reproject_masks_the_off_earth_padding_transparent():
    geo = geostationary_crs()
    disk = _fake_disk_image()
    out, extent = mtg_basemap_module._reproject_geostationary_to_platecarree(disk, geo)

    assert out.shape[2] == 4
    assert extent[0] < extent[1]  # lon_min < lon_max
    assert extent[2] < extent[3]  # lat_min < lat_max

    # The sub-satellite point (0, 0) must land on real (non-transparent)
    # disk data, not padding.
    lons = np.linspace(extent[0], extent[1], out.shape[1])
    lats = np.linspace(extent[2], extent[3], out.shape[0])
    center_row = int(np.argmin(np.abs(lats - 0.0)))
    center_col = int(np.argmin(np.abs(lons - 0.0)))
    assert out[center_row, center_col, 3] == 255

    # A far corner of the grid (near the edge of the configured view
    # window) must be masked transparent, not filled with the source
    # image's real white padding pixels - the actual bug this function's
    # own docstring documents finding.
    assert out[0, 0, 3] == 0
    assert out[-1, -1, 3] == 0


def test_draw_mtg_basemap_returns_false_with_no_image_fetched_yet():
    class _NoImshowAxes:
        pass  # deliberately no imshow() - must never be called here

    assert draw_mtg_basemap(_NoImshowAxes()) is False


def test_draw_mtg_basemap_draws_and_returns_true_once_a_real_image_is_cached():
    provider = MTGBasemapProvider.instance()
    provider._on_fetched(
        MTGFetchResult(
            is_real_data=True,
            status="FETCHED_OK",
            authenticated=False,
            image_bytes=_encode_png(_fake_disk_image()),
            product_id="TEST_PRODUCT",
        )
    )
    assert provider.is_live is True

    calls = []

    class _RecordingAxes:
        def imshow(self, data, **kwargs):
            calls.append((data, kwargs))

    assert draw_mtg_basemap(_RecordingAxes()) is True
    assert len(calls) == 1
    data, kwargs = calls[0]
    assert data.shape[2] == 4
    assert kwargs["extent"] == provider.current_extent()


def test_draw_mtg_basemap_is_honest_when_the_axes_cannot_draw_it():
    provider = MTGBasemapProvider.instance()
    provider._on_fetched(
        MTGFetchResult(
            is_real_data=True,
            status="FETCHED_OK",
            authenticated=False,
            image_bytes=_encode_png(_fake_disk_image()),
            product_id="TEST_PRODUCT",
        )
    )

    class _RaisingAxes:
        def imshow(self, *a, **k):
            raise RuntimeError("no real imshow support")

    # Must not raise, and must honestly report nothing was drawn - same
    # "one real failure must not blank the whole map" discipline as
    # acf.gui.map.map_renderer.
    assert draw_mtg_basemap(_RaisingAxes()) is False


def test_on_fetched_does_not_overwrite_the_last_good_image_on_a_failed_refetch():
    provider = MTGBasemapProvider.instance()
    good_bytes = _encode_png(_fake_disk_image())
    provider._on_fetched(
        MTGFetchResult(is_real_data=True, status="FETCHED_OK", authenticated=False, image_bytes=good_bytes)
    )
    assert provider.is_live is True
    first_image = provider.current_image_rgba()

    provider._on_fetched(
        MTGFetchResult(is_real_data=False, status="NOT_FETCHED_SEARCH_FAILED: timeout", authenticated=False)
    )

    assert provider.is_live is True
    assert provider.current_image_rgba() is first_image
    assert provider.status == "NOT_FETCHED_SEARCH_FAILED: timeout"


def _encode_png(rgba: np.ndarray) -> bytes:
    import io

    from PIL import Image

    buf = io.BytesIO()
    Image.fromarray(rgba, mode="RGBA").save(buf, format="PNG")
    return buf.getvalue()
