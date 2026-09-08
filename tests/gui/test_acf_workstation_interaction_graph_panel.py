"""
Tests for acf.gui.dashboard.acf_workstation_interaction_graph_panel.
ACFInteractionGraphWidget - the real, always-visible per-level
correlation network (Phase 34, 2026-09-05).
"""

from __future__ import annotations

import math

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation_interaction_graph_panel import NODES, ACFInteractionGraphWidget


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


def test_starts_with_no_real_edges(qapp):
    widget = ACFInteractionGraphWidget()
    assert widget.status() == {"has_edges": False, "edges": {}}


def test_update_from_volume_computes_every_real_pair(qapp):
    widget = ACFInteractionGraphWidget()
    volume = _real_volume()

    widget.update_from_volume(volume, level_index=0)

    status = widget.status()
    assert status["has_edges"] is True
    n = len(NODES)
    assert len(status["edges"]) == n * (n - 1) // 2  # every real unordered pair, once


def test_every_real_correlation_is_a_genuine_pearson_r_or_honest_nan(qapp):
    """Real regression guard: every edge value must be a real Pearson r
    in [-1, 1] (or NaN for a genuinely zero-variance field), never a
    fabricated placeholder outside that real range."""
    widget = ACFInteractionGraphWidget()
    volume = _real_volume()

    widget.update_from_volume(volume, level_index=0)

    for pair, r in widget.status()["edges"].items():
        assert pair[0] in NODES and pair[1] in NODES
        assert math.isnan(r) or -1.0 - 1e-9 <= r <= 1.0 + 1e-9


def test_humidity_temperature_correlation_matches_a_direct_real_computation(qapp):
    """Cross-check discipline: re-derive one real edge independently
    (numpy.corrcoef) and confirm the widget's own real value agrees."""
    import numpy as np

    from acf.awci.workstation_fields import compute_real_theta_e_and_rh_fields

    widget = ACFInteractionGraphWidget()
    volume = _real_volume()
    level = 0

    widget.update_from_volume(volume, level_index=level)

    _theta_e, relative_humidity = compute_real_theta_e_and_rh_fields(
        volume["temperature_volume"][level], volume["specific_humidity_volume"][level], volume["pressure_volume_hpa"][level]
    )
    expected_r = float(np.corrcoef(relative_humidity.ravel(), volume["temperature_volume"][level].ravel())[0, 1])

    assert widget.status()["edges"][("Humidity", "Temperature")] == pytest.approx(expected_r, abs=1e-6)
