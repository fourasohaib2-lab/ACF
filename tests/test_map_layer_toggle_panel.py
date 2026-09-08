"""
Tests for acf.gui.map.layer_toggle_panel.LayerTogglePanel - real
per-layer show/hide control for acf.gui.map.map_layers.LayerManager
(docs/ACF_MASTER_PROMPT.md section 28: "l'utilisateur doit pouvoir
activer/désactiver les couches"), explicit user request ("continue"),
closing the piece of section 28 the 2026-09-03 per-module-complexity-
layers update explicitly left open.
"""

from __future__ import annotations

from acf.gui.map.layer_toggle_panel import LayerTogglePanel
from acf.gui.map.map_canvas import MapCanvas


def test_one_checkbox_per_available_layer(qtbot):
    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    panel = LayerTogglePanel(canvas)
    qtbot.addWidget(panel)

    assert set(panel._checkboxes.keys()) == set(canvas.layer_manager.available_layers.keys())


def test_initial_checkbox_state_matches_the_real_default_active_layers(qtbot):
    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    panel = LayerTogglePanel(canvas)
    qtbot.addWidget(panel)

    for name, checkbox in panel._checkboxes.items():
        assert checkbox.isChecked() == (name in canvas.layer_manager.active_layer_names)
    # A default-active layer (e.g. "Satellite RGB") and a default-inactive
    # one (e.g. the new "AWCI Complexity") are both genuinely represented -
    # not every checkbox trivially checked or unchecked.
    assert panel._checkboxes["Satellite RGB"].isChecked() is True
    assert panel._checkboxes["AWCI Complexity"].isChecked() is False


def test_checking_a_box_activates_the_real_layer(qtbot):
    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    panel = LayerTogglePanel(canvas)
    qtbot.addWidget(panel)
    assert "Dynamic Complexity" not in canvas.layer_manager.active_layer_names

    panel._checkboxes["Dynamic Complexity"].setChecked(True)

    assert "Dynamic Complexity" in canvas.layer_manager.active_layer_names


def test_unchecking_a_box_deactivates_the_real_layer(qtbot):
    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    panel = LayerTogglePanel(canvas)
    qtbot.addWidget(panel)
    assert "Satellite RGB" in canvas.layer_manager.active_layer_names

    panel._checkboxes["Satellite RGB"].setChecked(False)

    assert "Satellite RGB" not in canvas.layer_manager.active_layer_names


def test_on_toggled_never_adds_a_layer_twice(qtbot):
    """Real idempotency guard in _on_toggled() itself (not merely Qt
    eliding a same-state setChecked() call) - calling it directly twice
    with checked=True must not duplicate the layer name."""
    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    panel = LayerTogglePanel.__new__(LayerTogglePanel)  # bypass __init__/_build_ui - only _on_toggled's own logic is under test
    panel.map_canvas = canvas

    panel._on_toggled("Dynamic Complexity", True)
    panel._on_toggled("Dynamic Complexity", True)

    assert canvas.layer_manager.active_layer_names.count("Dynamic Complexity") == 1


def test_refresh_syncs_checkboxes_after_an_external_change(qtbot):
    """e.g. ESOCWindow._on_awci_field_ready() appends "AWCI Complexity"
    to active_layer_names directly (not through this panel) - refresh()
    must pick that up."""
    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    panel = LayerTogglePanel(canvas)
    qtbot.addWidget(panel)
    assert panel._checkboxes["AWCI Complexity"].isChecked() is False

    canvas.layer_manager.active_layer_names.append("AWCI Complexity")
    panel.refresh()

    assert panel._checkboxes["AWCI Complexity"].isChecked() is True


def test_refresh_does_not_trigger_a_toggle_side_effect(qtbot):
    """refresh() reflects state, it must not itself re-trigger
    _on_toggled() and mutate active_layer_names a second time."""
    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    panel = LayerTogglePanel(canvas)
    qtbot.addWidget(panel)
    canvas.layer_manager.active_layer_names.append("AWCI Complexity")

    panel.refresh()
    panel.refresh()

    assert canvas.layer_manager.active_layer_names.count("AWCI Complexity") == 1
