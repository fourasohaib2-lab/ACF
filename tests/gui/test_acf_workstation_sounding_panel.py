"""
Tests for acf.gui.dashboard.acf_workstation_sounding_panel.
ACFVerticalSoundingWidget - the real, always-visible per-point vertical
profile panel (Phase 33, 2026-09-05).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation_sounding_panel import ACFVerticalSoundingWidget


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=10, n_lon=18, n_levels=5, steps=3, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_starts_with_no_real_point(qapp):
    widget = ACFVerticalSoundingWidget()
    assert widget.status() == {"has_point": False, "point": None}


def test_update_from_volume_and_point_sets_a_real_point(qapp):
    widget = ACFVerticalSoundingWidget()
    volume = _real_volume()
    lat, lon = float(volume["lats"][1]), float(volume["lons"][2])

    widget.update_from_volume_and_point(volume, lat, lon)

    status = widget.status()
    assert status["has_point"] is True
    # Real nearest-neighbour lookup must land on one of the volume's own real coordinates.
    assert status["point"][0] in list(volume["lats"])
    assert status["point"][1] in list(volume["lons"])


def test_update_accepts_a_real_level_index_without_raising(qapp):
    widget = ACFVerticalSoundingWidget()
    volume = _real_volume()

    widget.update_from_volume_and_point(volume, lat=10.0, lon=20.0, level_index=2)

    assert widget.status()["has_point"] is True
