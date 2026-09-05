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

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QCheckBox, QDockWidget, QScrollArea, QVBoxLayout, QWidget

from acf.gui.map.map_canvas import MapCanvas

#: Real settings-persistence backend for "Settings / Layer Preferences"
#: (docs/ACF_MASTER_PROMPT.md's System Explorer - previously unmapped,
#: confirmed via search to have no real backend anywhere in this
#: codebase; see `panel_manager.LayerPreferencesPanel`'s own docstring).
#: Shared with that panel so both write/read the exact same real key -
#: not two independent, silently-diverging copies of the same setting.
LAYER_PREFERENCES_ORG = "ACF"
LAYER_PREFERENCES_APP = "ESOC"
LAYER_PREFERENCES_KEY = "layers/default_active_names"


def make_layer_preferences_settings() -> QSettings:
    """The one real place `QSettings(LAYER_PREFERENCES_ORG,
    LAYER_PREFERENCES_APP)` gets constructed for production use - tests
    inject their own tmp_path-backed QSettings instead (see
    `load_default_active_layer_names`/`LayerTogglePanel`/
    `LayerPreferencesPanel`'s own `settings` parameter) so the test
    suite never reads or writes this real user's actual
    ~/.config/ACF/ESOC.conf."""
    return QSettings(LAYER_PREFERENCES_ORG, LAYER_PREFERENCES_APP)


def load_default_active_layer_names(settings: QSettings | None = None) -> list[str] | None:
    """Read the operator's saved default active-layer set, or None if
    "Settings / Layer Preferences" -> Save as Default was never used."""
    settings = settings if settings is not None else make_layer_preferences_settings()
    value = settings.value(LAYER_PREFERENCES_KEY)
    if value is None:
        return None
    if isinstance(value, str):
        # A single-element list can round-trip as a bare str depending on
        # the platform's real QSettings backend (e.g. a 1-item INI value) -
        # always hand callers a list regardless.
        return [value]
    return list(value)


class LayerTogglePanel(QDockWidget):
    """
    Real checkbox per `map_canvas.layer_manager.available_layers` entry
    - checking one adds its name to `active_layer_names` and redraws;
    unchecking removes it. `refresh()` re-syncs checkbox state with
    `active_layer_names` after anything else changes it programmatically
    (e.g. ESOCWindow._on_awci_field_ready() auto-activating "AWCI
    Complexity").

    NOTE (correction - closes a real, previously-disclosed gap): on
    construction, if the operator has ever used "Settings / Layer
    Preferences" -> Save as Default (`LayerPreferencesPanel`,
    `panel_manager.py`), that saved set is applied to the real,
    live `map_canvas.layer_manager` here - the same object this panel's
    own checkboxes control - rather than only ever being written and
    never read back. Silently falls back to `LayerManager`'s own
    built-in default (unchanged behaviour) when nothing has been saved
    yet, or when a name that WAS saved no longer exists as a real layer
    (e.g. after a later code change removed one) - never raises for a
    stale saved name.
    """

    def __init__(
        self, map_canvas: MapCanvas, parent: QWidget | None = None, settings: QSettings | None = None
    ) -> None:
        super().__init__("Map Layers", parent)
        self.map_canvas = map_canvas
        self._checkboxes: dict[str, QCheckBox] = {}
        self._apply_saved_default_layers(settings)
        self._build_ui()
        self.refresh()

    def _apply_saved_default_layers(self, settings: QSettings | None) -> None:
        """Apply a real saved "Layer Preferences" default, if one exists."""
        saved = load_default_active_layer_names(settings)
        if saved is None:
            return  # nothing ever saved - keep LayerManager's own built-in default.
        valid = [name for name in saved if name in self.map_canvas.layer_manager.available_layers]
        self.map_canvas.layer_manager.set_active_layers(valid)

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
