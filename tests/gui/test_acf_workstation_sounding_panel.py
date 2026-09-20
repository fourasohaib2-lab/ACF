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


# -------------------------------------------- show_model_comparison (§19)


def _fake_profile(base_temp_k: float) -> dict:
    import numpy as np

    return {
        "lat": 36.7,
        "lon": 3.0,
        "pressure_profile_hpa": np.array([1000.0, 850.0, 700.0, 500.0]),
        "temperature_profile": np.array([base_temp_k, base_temp_k - 10, base_temp_k - 20, base_temp_k - 35]),
        "wind_speed_profile": np.array([2.0, 5.0, 8.0, 12.0]),
    }


def test_show_model_comparison_sets_a_real_point_from_the_last_profile(qapp):
    widget = ACFVerticalSoundingWidget()
    profiles = {"AROME": _fake_profile(290.0), "ALADIN": _fake_profile(288.0)}

    widget.show_model_comparison(profiles)

    assert widget.status() == {"has_point": True, "point": (36.7, 3.0)}


def test_show_model_comparison_draws_one_line_per_real_model(qapp):
    widget = ACFVerticalSoundingWidget()
    profiles = {"AROME": _fake_profile(290.0), "ALADIN": _fake_profile(288.0), "ARPEGE": _fake_profile(292.0)}

    widget.show_model_comparison(profiles)

    legend = widget.axis.get_legend()
    assert legend is not None
    labels = [text.get_text() for text in legend.get_texts()]
    assert set(labels) == {"AROME", "ALADIN", "ARPEGE"}
    assert len(widget.axis.lines) == 3


def test_show_model_comparison_title_names_the_real_point(qapp):
    widget = ACFVerticalSoundingWidget()
    widget.show_model_comparison({"AROME": _fake_profile(290.0), "ALADIN": _fake_profile(288.0)})

    title = widget.axis.get_title(loc="left")
    assert "Model Comparison" in title
    assert "36.70" in title
    assert "3.00" in title
