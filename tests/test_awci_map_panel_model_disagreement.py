"""
Tests for AWCIMapPanel's "Model Disagreement" LAYERS checkbox (Master
Prompt V3 §9/§32, added 2026-09-20) - see
modelDisagreementLayerRequested/set_model_disagreement_grid's own
docstrings in awci_map_panel.py for the real design: unlike every
other extra layer, this one's real grid is genuinely expensive to
compute (N real CoupledEarthSolver runs), so it is never built inline
during update_data() - only via an explicit real request signal the
embedding dashboard answers asynchronously.
"""

from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_map_panel import AWCIMapPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_checking_model_disagreement_with_no_grid_yet_emits_the_real_request(qtbot):
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    qtbot.addWidget(panel)

    with qtbot.waitSignal(panel.modelDisagreementLayerRequested, timeout=1000):
        panel.extra_layer_checkboxes["Model Disagreement"].setChecked(True)

    # No real grid was ever provided - honestly no contour built yet.
    assert "Model Disagreement" not in panel._extra_layer_contours


def test_checking_model_disagreement_does_not_crash_on_a_real_redraw(qtbot):
    """Real regression guard: before this layer's own generic-key
    guard was added, a real redraw while it was checked (but not yet
    computed) risked a KeyError against awci_layer_grids()'s own dict,
    which never has a "model_disagreement" key."""
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    qtbot.addWidget(panel)
    panel.extra_layer_checkboxes["Model Disagreement"].setChecked(True)

    panel.update_data()  # must not raise


def test_set_model_disagreement_grid_builds_a_real_visible_contour(qtbot):
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    qtbot.addWidget(panel)
    panel.extra_layer_checkboxes["Model Disagreement"].setChecked(True)

    lons = np.linspace(-10, 10, 6)
    lats = np.linspace(30, 40, 5)
    values = np.random.default_rng(0).uniform(0, 2, size=(5, 6))
    panel.set_model_disagreement_grid(lons, lats, values)

    assert "Model Disagreement" in panel._extra_layer_contours
    assert panel._extra_layer_contours["Model Disagreement"].get_visible() is True


def test_setting_the_grid_while_unchecked_caches_it_without_building_a_contour(qtbot):
    """The dashboard's async worker may finish AFTER the user has
    already unchecked the layer - the real result must be cached (not
    discarded) but not shown until re-checked."""
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    qtbot.addWidget(panel)
    # Never checked.

    lons = np.linspace(-10, 10, 6)
    lats = np.linspace(30, 40, 5)
    values = np.zeros((5, 6))
    panel.set_model_disagreement_grid(lons, lats, values)

    assert "Model Disagreement" not in panel._extra_layer_contours
    assert panel._model_disagreement_grid is not None

    panel.extra_layer_checkboxes["Model Disagreement"].setChecked(True)
    assert "Model Disagreement" in panel._extra_layer_contours


def test_checking_again_after_a_real_grid_is_cached_does_not_re_emit_the_request(qtbot):
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    qtbot.addWidget(panel)
    lons = np.linspace(-10, 10, 6)
    lats = np.linspace(30, 40, 5)
    panel.set_model_disagreement_grid(lons, lats, np.zeros((5, 6)))

    emitted = []
    panel.modelDisagreementLayerRequested.connect(lambda: emitted.append(True))
    panel.extra_layer_checkboxes["Model Disagreement"].setChecked(True)
    panel.extra_layer_checkboxes["Model Disagreement"].setChecked(False)
    panel.extra_layer_checkboxes["Model Disagreement"].setChecked(True)

    assert emitted == []


def test_toggling_off_and_on_an_already_built_contour_is_a_real_cheap_show_hide(qtbot):
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    qtbot.addWidget(panel)
    lons = np.linspace(-10, 10, 6)
    lats = np.linspace(30, 40, 5)
    panel.set_model_disagreement_grid(lons, lats, np.zeros((5, 6)))
    panel.extra_layer_checkboxes["Model Disagreement"].setChecked(True)
    contour = panel._extra_layer_contours["Model Disagreement"]

    panel.extra_layer_checkboxes["Model Disagreement"].setChecked(False)
    assert contour.get_visible() is False

    panel.extra_layer_checkboxes["Model Disagreement"].setChecked(True)
    assert contour.get_visible() is True
    # Same real artist reused, not rebuilt.
    assert panel._extra_layer_contours["Model Disagreement"] is contour


def test_model_disagreement_survives_a_real_data_refresh_once_computed(qtbot):
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    qtbot.addWidget(panel)
    lons = np.linspace(-10, 10, 6)
    lats = np.linspace(30, 40, 5)
    panel.set_model_disagreement_grid(lons, lats, np.zeros((5, 6)))
    panel.extra_layer_checkboxes["Model Disagreement"].setChecked(True)
    assert "Model Disagreement" in panel._extra_layer_contours

    panel.update_data()  # e.g. the time slider moving

    assert "Model Disagreement" in panel._extra_layer_contours
    assert panel._extra_layer_contours["Model Disagreement"].get_visible() is True
