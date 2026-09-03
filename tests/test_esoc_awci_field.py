"""
Tests for ESOCWindow's "🌪️ AWCI Field" toolbar action (explicit user
request "ajoute la 4eme dimension au niveau d'affichage des cartes")
- real acf.awci.spatial_field.compute_real_complexity_field() overlaid
on ESOC's own central map, previously showing no real AWCI data at all.

Uses qtbot.waitUntil() to wait for the real QThreadPool worker to
finish, rather than calling the worker's run() synchronously - this is
deliberate: an earlier version of this wiring connected the worker's
finished signal to a bare lambda instead of a bound method, which
PySide6 silently never invoked at all (no receiver QObject to
determine safe cross-thread queuing for). A test that called run()
directly, or that connected its own lambda the same way, would not
have caught this - only driving it through the real
QThreadPool.globalInstance().start() + Qt event loop path does.
"""

from __future__ import annotations

from acf.gui.esoc.esoc_toolbar import ESOCToolbar
from acf.gui.esoc.esoc_window import ESOCWindow


def test_toolbar_has_the_real_awci_field_action(qtbot):
    # ESOCToolbar builds its QActions from an internal list, not exposed
    # as data - the real, black-box-observable check is that the action
    # exists on the constructed toolbar with the right label.
    toolbar = ESOCToolbar()
    qtbot.addWidget(toolbar)
    action_labels = [act.text() for act in toolbar.actions()]
    assert "🌪️ AWCI Field" in action_labels


def test_show_awci_field_on_map_genuinely_populates_the_real_layer(qtbot):
    win = ESOCWindow()
    qtbot.addWidget(win)
    map_canvas = win.layout_manager.view_manager.map_canvas
    assert "AWCI Complexity" not in map_canvas.layer_manager.active_layer_names

    win._show_awci_field_on_map()

    qtbot.waitUntil(
        lambda: "AWCI Complexity" in map_canvas.layer_manager.active_layer_names,
        timeout=60000,
    )

    layer = map_canvas.layer_manager.available_layers["AWCI Complexity"]
    assert layer.custom_data is not None
    assert "REAL AWCI" in map_canvas.title_text
    assert "Real AWCI field displayed" in win.status_bar.currentMessage()


def test_show_awci_field_on_map_also_populates_real_module_layers(qtbot):
    """docs/ACF_MASTER_PROMPT.md sections 28-29 - the same real
    compute_real_complexity_field() call that populates the combined
    AWCI layer also carries module_fields/forecast_field for free;
    _on_awci_field_ready() must feed them into the real per-module map
    layers (populated but not yet shown - see MapCanvas.
    set_module_complexity_field()'s own `activate` parameter for why)."""
    from acf.gui.map.map_layers import MODULE_COMPLEXITY_LAYERS

    win = ESOCWindow()
    qtbot.addWidget(win)
    map_canvas = win.layout_manager.view_manager.map_canvas

    win._show_awci_field_on_map()

    qtbot.waitUntil(
        lambda: "AWCI Complexity" in map_canvas.layer_manager.active_layer_names,
        timeout=60000,
    )

    for layer_name in MODULE_COMPLEXITY_LAYERS:
        layer = map_canvas.layer_manager.available_layers[layer_name]
        assert layer.custom_data is not None
        # Data is real and ready, but not auto-shown alongside the
        # combined AWCI layer (would stack 7 overlapping heatmaps).
        assert layer_name not in map_canvas.layer_manager.active_layer_names
    uncertainty_layer = map_canvas.layer_manager.available_layers["Uncertainty"]
    assert uncertainty_layer.custom_data is not None
    assert "Uncertainty" not in map_canvas.layer_manager.active_layer_names


def test_toolbar_action_dispatch_reaches_the_real_handler(qtbot):
    """End-to-end from the actual dispatch path (_handle_toolbar_action),
    not by calling _show_awci_field_on_map() directly - proves the
    toolbar's command string ("show_awci_field_on_map") is genuinely
    wired to the same handler the action list above declares."""
    win = ESOCWindow()
    qtbot.addWidget(win)
    map_canvas = win.layout_manager.view_manager.map_canvas

    win._handle_toolbar_action("show_awci_field_on_map")

    qtbot.waitUntil(
        lambda: "AWCI Complexity" in map_canvas.layer_manager.active_layer_names,
        timeout=60000,
    )
    assert map_canvas.layer_manager.available_layers["AWCI Complexity"].custom_data is not None
