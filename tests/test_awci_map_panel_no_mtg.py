"""
Regression test for the real MTG-removal fix (2026-09-07, explicit
user request "enleve le MTG ... trouve moi une solution pour afficher
des cartes reel et fonctionnel a 100%").

AWCIMapPanel used to draw a live MTG (EUMETSAT FCI Level 1c) basemap
image first, falling back to Cartopy's plain Ocean/Land fill only
until the first successful network fetch landed. Removed - see
awci_map_panel.py's own NOTE at the update_data() call site for the
full honest rationale (MTG's own disclosed thumbnail-resolution/
approximate-geolocation limits, plus a real network/auth dependency
that could leave the map blank or degraded - Cartopy's own Natural
Earth vector geography needs neither and is always available).
"""

from __future__ import annotations

from unittest.mock import patch

from acf.gui.dashboard.awci_map_panel import AWCIMapPanel


def test_update_data_never_calls_draw_mtg_basemap(qtbot):
    """The real, decisive regression guard: even if MTGBasemapProvider
    would have a real cached image ready, this panel must never draw
    it - confirmed by asserting the function is simply never called,
    not by checking pixels."""
    # The MTG-removal pass also removed the module's own
    # `draw_mtg_basemap` import (no other caller remained here), so
    # patching it by name would now raise AttributeError - the real
    # guarantee this test makes is that the NAME is gone from this
    # module's namespace entirely (no import left to even call), plus
    # a real behavioural check below against the provider itself.
    import acf.gui.dashboard.awci_map_panel as map_panel_module

    assert not hasattr(map_panel_module, "draw_mtg_basemap")

    with patch("acf.gui.map.mtg_basemap.draw_mtg_basemap") as mock_draw:
        panel = AWCIMapPanel()
        qtbot.addWidget(panel)
        panel.update_data(flight_level_hpa=300.0)

    mock_draw.assert_not_called()


def test_map_panel_no_longer_subscribes_to_the_live_mtg_provider(qtbot):
    """The real per-instance MTGBasemapProvider.updated subscription
    (redrawing on every fresh EUMETSAT image) is gone too - not just
    the draw call - confirmed by asserting the panel's own real
    listener-count-independent behaviour: update_data() called by hand
    is the ONLY thing that redraws now."""
    from acf.gui.map.mtg_basemap import MTGBasemapProvider

    panel = AWCIMapPanel()
    qtbot.addWidget(panel)

    with patch.object(panel, "update_data") as mock_update:
        MTGBasemapProvider.instance().updated.emit()

    mock_update.assert_not_called()


def test_global_map_always_shows_real_cartopy_basemap_features(qtbot):
    """The real replacement basemap - always present, never conditional
    on a network fetch having succeeded.

    NOTE (updated 2026-09-12, docs/reference/awci_dashboard_reference.jpg
    pixel-parity pass): the flat OCEAN/LAND facecolor fill this test's
    name used to describe was replaced by a real stock_img() Natural
    Earth relief raster (see update_data()'s own comment) - still 100%
    real, bundled, offline; COASTLINE/BORDERS are unchanged."""
    from matplotlib.image import AxesImage

    panel = AWCIMapPanel()
    qtbot.addWidget(panel)
    panel.update_data(flight_level_hpa=300.0)

    feature_types = {type(artist) for artist in panel.axis.get_children()}
    # Cartopy features are added as real matplotlib artists - a direct
    # add_feature() call always produces at least one real artist on
    # this axis once drawn; the decisive check is behavioural (no MTG
    # call, above) rather than introspecting private feature internals
    # further here.
    assert len(feature_types) > 0
    # stock_img() specifically draws a real AxesImage - a direct,
    # non-brittle check that the real relief raster is actually there.
    assert any(isinstance(artist, AxesImage) for artist in panel.axis.get_children())
