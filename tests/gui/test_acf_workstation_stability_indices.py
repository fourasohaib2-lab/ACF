"""
Tests for acf.gui.dashboard.acf_workstation_stability_indices.
ACFStabilityIndicesWidget - the real, compact display widget (Phase
39, 2026-09-05).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation_stability_indices import (
    ACFStabilityIndicesWidget,
    compute_real_stability_indices_at_point,
)


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_starts_with_no_real_data(qapp):
    widget = ACFStabilityIndicesWidget()
    assert widget.status() == {"has_data": False}


def test_set_indices_renders_the_real_values(qapp):
    widget = ACFStabilityIndicesWidget()
    volume = compute_real_complexity_volume(model="ALADIN", n_lat=10, n_lon=18, n_levels=8, steps=3, perturbation_scale=2.0, seed=1)
    indices = compute_real_stability_indices_at_point(volume, lat=10.0, lon=20.0)

    widget.set_indices(indices)

    assert widget.status() == {"has_data": True}
    assert f"{indices['cape_j_kg']:.1f}" in widget._labels["CAPE"].text()


def test_set_indices_shows_n_a_for_a_real_none_value(qapp):
    widget = ACFStabilityIndicesWidget()

    widget.set_indices({"cape_j_kg": 0.0, "cin_j_kg": 0.0, "bulk_wind_shear_ms": 5.0, "static_stability_n_s1": None})

    assert widget._labels["Static Stability (N)"].text() == "n/a"
