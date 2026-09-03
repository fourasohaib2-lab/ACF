"""
Map Layer Toggle Panel
========================

Real per-layer show/hide control for
`acf.gui.map.map_layers.LayerManager` - the `LayerManager` that
`acf.gui.map.map_canvas.MapCanvas` (ESOC's own central map) actually
uses. docs/ACF_MASTER_PROMPT.md section 28: "L'utilisateur doit pouvoir
activer/désactiver les couches" - explicit user request ("continue"),
closing the piece of section 28 the 2026-09-03 per-module-complexity-
layers update explicitly left open: real per-module data/layers/API
existed (`MapCanvas.set_module_complexity_field(..., activate=True)`),
but no interactive control for a user to actually pick one.

Found while building this, not reused: a DIFFERENT, entirely orphaned
layer-management pair already exists -
`acf.gui.map.layers.layer_manager.LayerManager` (a real, Qt-signal-based
`QObject` with `add_layer()`/`remove_layer()`/`layers()`/
`visible_layers()`) plus `acf.gui.docks.layer_panel.LayerPanel` /
`acf.gui.layer_panel.layer_panel` (real `QTreeWidget`-based checkbox
UIs for it) - `LayerPanel`'s own docstring already discloses it is
"currently unused/unwired anywhere else in the codebase". That pair
targets a genuinely different, incompatible interface (Qt signals,
`layer.id`/`layer.visible`, add/remove/move semantics) from the simple
`available_layers: dict[str, BaseMapLayer]` +
`active_layer_names: list[str]` `map_layers.LayerManager` the live map
actually uses - adapting either side to the other would be close to a
rewrite, not real reuse, so this panel is built directly against the
real, connected `LayerManager` instead. Not consolidated/deleted here
(docs/ACF_MASTER_PROMPT.md section 71: never mass-delete) - flagged as
a real, disclosed architectural finding in reports/ACF_MASTER_AUDIT_v2.md.
"""

from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QDockWidget, QScrollArea, QVBoxLayout, QWidget

from acf.gui.map.map_canvas import MapCanvas


class LayerTogglePanel(QDockWidget):
    """
    Real checkbox per `map_canvas.layer_manager.available_layers` entry
    - checking one adds its name to `active_layer_names` and redraws;
    unchecking removes it. `refresh()` re-syncs checkbox state with
    `active_layer_names` after anything else changes it programmatically
    (e.g. ESOCWindow._on_awci_field_ready() auto-activating "AWCI
    Complexity").
    """

    def __init__(self, map_canvas: MapCanvas, parent: QWidget | None = None) -> None:
        super().__init__("Map Layers", parent)
        self.map_canvas = map_canvas
        self._checkboxes: dict[str, QCheckBox] = {}
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        for name in self.map_canvas.layer_manager.available_layers:
            checkbox = QCheckBox(name)
            checkbox.toggled.connect(lambda checked, layer_name=name: self._on_toggled(layer_name, checked))
            layout.addWidget(checkbox)
            self._checkboxes[name] = checkbox
        layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        self.setWidget(scroll)

    def _on_toggled(self, layer_name: str, checked: bool) -> None:
        active = self.map_canvas.layer_manager.active_layer_names
        if checked and layer_name not in active:
            active.append(layer_name)
        elif not checked and layer_name in active:
            active.remove(layer_name)
        self.map_canvas.redraw()

    def refresh(self) -> None:
        """Re-sync every checkbox's checked state with the real, current
        `active_layer_names` - does not itself trigger a redraw or emit
        `toggled` (signals blocked), since it reflects state that
        already changed, rather than requesting a change."""
        active = set(self.map_canvas.layer_manager.active_layer_names)
        for name, checkbox in self._checkboxes.items():
            was_blocked = checkbox.blockSignals(True)
            checkbox.setChecked(name in active)
            checkbox.blockSignals(was_blocked)
