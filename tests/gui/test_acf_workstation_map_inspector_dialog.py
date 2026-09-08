"""
Tests for acf.gui.dashboard.acf_workstation_map_inspector.
ACFMapInspectorDialog - the real, non-modal display widget (Phase 36,
2026-09-05).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation_map_inspector import ACFMapInspectorDialog, compute_real_map_inspector_snapshot


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_starts_with_a_real_honest_placeholder(qapp):
    dialog = ACFMapInspectorDialog()
    assert "Click a map" in dialog.text_label.text()


def test_is_non_modal(qapp):
    dialog = ACFMapInspectorDialog()
    assert dialog.isModal() is False


def test_set_snapshot_renders_the_real_point_data(qapp):
    dialog = ACFMapInspectorDialog()
    volume = compute_real_complexity_volume(model="ALADIN", n_lat=10, n_lon=18, n_levels=5, steps=3, perturbation_scale=2.0, seed=1)
    snapshot = compute_real_map_inspector_snapshot(volume, lat=10.0, lon=20.0, level_index=0)

    dialog.set_snapshot(snapshot)

    assert f"{snapshot['lat']:.2f}" in dialog.text_label.text()
    assert snapshot["model"] in dialog.text_label.text()
