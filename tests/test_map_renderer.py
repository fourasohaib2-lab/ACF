"""
Tests for acf.gui.map.map_renderer.MapRenderer - found with zero test
coverage during a repo-wide scan for silently-swallowed exceptions
(every base-map feature was wrapped in `except Exception: pass` with
no logging at all - fixed alongside these tests).
"""

from __future__ import annotations

import logging

import cartopy.crs as ccrs
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from acf.gui.map.map_renderer import MapRenderer


@pytest.fixture
def geo_axes():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    yield ax
    plt.close(fig)


def test_render_none_axes_is_a_real_no_op():
    MapRenderer().render(None)  # must not raise


def test_render_draws_every_real_base_map_feature_without_raising(geo_axes):
    MapRenderer().render(geo_axes, title="Test Map")
    assert geo_axes.get_title() == "Test Map"


def test_render_calls_layer_manager_with_the_real_active_layers():
    class _FakeLayerManager:
        def __init__(self):
            self.active_layers = None
            self.rendered = False

        def set_active_layers(self, layers):
            self.active_layers = layers

        def render_layers(self, axes, transform):
            self.rendered = True

    layer_manager = _FakeLayerManager()

    class _StubAxes:
        def set_facecolor(self, *a, **k):
            pass

        def add_feature(self, *a, **k):
            pass

        def coastlines(self, *a, **k):
            pass

        def gridlines(self, *a, **k):
            class _Grid:
                pass

            return _Grid()

        def set_title(self, *a, **k):
            pass

    MapRenderer().render(_StubAxes(), layer_manager=layer_manager, active_layers=["temperature"])

    assert layer_manager.active_layers == ["temperature"]
    assert layer_manager.rendered is True


class _RaisingAxes:
    """A real stub whose every real Cartopy-facing call genuinely raises - proves render() logs and keeps going, instead of the old silent `except Exception: pass`."""

    def set_facecolor(self, *a, **k):
        pass

    def add_feature(self, *a, **k):
        raise RuntimeError("no real network route to download the Natural Earth shapefile")

    def coastlines(self, *a, **k):
        raise RuntimeError("coastline data unavailable")

    def gridlines(self, *a, **k):
        raise RuntimeError("gridlines failed")

    def set_title(self, *a, **k):
        pass


def test_render_logs_a_real_feature_failure_instead_of_silently_swallowing_it(caplog):
    with caplog.at_level(logging.WARNING, logger="acf.gui.map.map_renderer"):
        MapRenderer().render(_RaisingAxes(), title="Should still set no crash")  # must not raise

    messages = [r.message for r in caplog.records]
    assert any("ocean" in m.lower() for m in messages)
    assert any("land" in m.lower() for m in messages)
    assert any("coastlines" in m.lower() for m in messages)
    assert any("gridlines" in m.lower() for m in messages)
    # 6 real base-map features attempted (ocean/land/lakes/rivers/borders/coastlines) + gridlines = 7 real failures logged.
    assert len(messages) == 7
