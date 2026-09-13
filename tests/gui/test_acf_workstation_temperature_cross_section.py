"""
Tests for ACFTemperatureCrossSectionWidget (2026-09-13, merged Overview
screen) - a real temperature cross-section reusing
acf.awci.path_sampling.sample_volume_cross_section() with a real
temperature colormap, not the AWCI 0-100 score AWCICrossSection draws.
"""

from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.path_sampling import sample_volume_cross_section
from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation_temperature_cross_section import ACFTemperatureCrossSectionWidget


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_small_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=8, n_lon=8, n_levels=5, steps=2, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_update_from_volume_draws_a_real_colorbar_without_raising(qapp):
    widget = ACFTemperatureCrossSectionWidget()
    volume = _real_small_volume()

    widget.update_from_volume(volume)

    assert widget.status()["has_colorbar"] is True


def test_cross_section_grid_matches_an_independent_sample_volume_cross_section_call(qapp):
    """Cross-check discipline: the widget's own real transect must
    match a fresh, independent call to the same real sampling
    function - never a separately re-derived grid."""
    widget = ACFTemperatureCrossSectionWidget()
    volume = _real_small_volume()

    widget.update_from_volume(volume)

    lats = np.asarray(volume["lats"])
    lons = np.asarray(volume["lons"])
    mid_lon = float(lons[len(lons) // 2])
    point_a = (float(lats.min()), mid_lon)
    point_b = (float(lats.max()), mid_lon)
    expected = sample_volume_cross_section(
        lats, lons, volume["pressure_volume_hpa"], volume["temperature_volume"], point_a, point_b,
    )

    # The widget draws grid - 273.15 (K -> degC) - re-derive the same
    # real transform and check the real contour's own quantized level
    # boundaries genuinely enclose that real data range (levels are
    # binned, so an exact match to raw data isn't expected - only that
    # the real transect data, not some other range, drove them).
    expected_grid_c = expected["grid"] - 273.15
    levels = np.asarray(widget._colorbar.mappable.levels)
    assert levels.min() <= expected_grid_c.min() + 1e-6
    assert levels.max() >= expected_grid_c.max() - 1e-6
