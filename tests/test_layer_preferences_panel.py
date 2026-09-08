"""
Tests for "Settings / Layer Preferences" (LayerPreferencesPanel,
acf.gui.esoc.panel_manager) and its real read-back in LayerTogglePanel
(acf.gui.map.layer_toggle_panel) - a real settings-persistence backend,
previously entirely absent from this codebase (confirmed via search,
see WorkspaceModesPanel's own docstring), closing one of "Settings"'s
2 previously-unmapped System Explorer leaves ("ultra scan" gap pass
over reports/ACF_MASTER_AUDIT_v2.md's Phases 1-49).

Every test constructs its own QSettings backed by an INI file under
pytest's own tmp_path - never the real ~/.config/ACF/ESOC.conf a real
user's desktop session would use (see
layer_toggle_panel.make_layer_preferences_settings's own docstring).
"""

from __future__ import annotations

from PySide6.QtCore import QSettings

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import LayerPreferencesPanel
from acf.gui.map.layer_toggle_panel import LAYER_PREFERENCES_KEY, LayerTogglePanel, load_default_active_layer_names
from acf.gui.map.map_canvas import MapCanvas
from acf.gui.map.map_layers import LayerManager


def _isolated_settings(tmp_path, name="settings.ini"):
    return QSettings(str(tmp_path / name), QSettings.Format.IniFormat)


def test_nothing_saved_reports_none(tmp_path):
    settings = _isolated_settings(tmp_path)
    assert load_default_active_layer_names(settings) is None


def test_panel_defaults_to_layermanagers_own_built_in_default(tmp_path, qtbot):
    settings = _isolated_settings(tmp_path)
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    panel = LayerPreferencesPanel(registry, dispatcher, settings=settings)
    qtbot.addWidget(panel)

    reference = LayerManager()
    for name, checkbox in panel._checkboxes.items():
        assert checkbox.isChecked() == (name in reference.active_layer_names)
    assert "Showing LayerManager's built-in default" in panel.status_label.text()


def test_one_checkbox_per_real_available_layer(tmp_path, qtbot):
    settings = _isolated_settings(tmp_path)
    panel = LayerPreferencesPanel(ModuleRegistry(), CommandDispatcher(), settings=settings)
    qtbot.addWidget(panel)

    assert set(panel._checkboxes.keys()) == set(LayerManager().available_layers.keys())


def test_save_as_default_persists_the_real_current_selection(tmp_path, qtbot):
    settings = _isolated_settings(tmp_path)
    panel = LayerPreferencesPanel(ModuleRegistry(), CommandDispatcher(), settings=settings)
    qtbot.addWidget(panel)

    panel._checkboxes["Satellite RGB"].setChecked(False)
    panel._checkboxes["AWCI Complexity"].setChecked(True)
    panel._save()

    saved = load_default_active_layer_names(settings)
    assert saved is not None
    assert "Satellite RGB" not in saved
    assert "AWCI Complexity" in saved
    assert "Saved as default" in panel.status_label.text()


def test_restore_built_in_default_clears_the_saved_preference(tmp_path, qtbot):
    settings = _isolated_settings(tmp_path)
    settings.setValue(LAYER_PREFERENCES_KEY, ["AWCI Complexity"])  # a real, previously-saved preference
    panel = LayerPreferencesPanel(ModuleRegistry(), CommandDispatcher(), settings=settings)
    qtbot.addWidget(panel)
    assert panel._checkboxes["AWCI Complexity"].isChecked() is True

    panel._restore()

    assert load_default_active_layer_names(settings) is None
    reference = LayerManager()
    for name, checkbox in panel._checkboxes.items():
        assert checkbox.isChecked() == (name in reference.active_layer_names)
    assert "Reverted to LayerManager's built-in default" in panel.status_label.text()


def test_layer_toggle_panel_applies_a_real_saved_default_at_startup(tmp_path, qtbot):
    """The real point of this whole feature: what LayerPreferencesPanel
    saves is genuinely read back by the live map's own LayerTogglePanel,
    not a write-only setting nobody ever reads."""
    settings = _isolated_settings(tmp_path)
    settings.setValue(LAYER_PREFERENCES_KEY, ["MSLP", "AWCI Complexity"])

    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    panel = LayerTogglePanel(canvas, settings=settings)
    qtbot.addWidget(panel)

    assert set(canvas.layer_manager.active_layer_names) == {"MSLP", "AWCI Complexity"}
    assert panel._checkboxes["MSLP"].isChecked() is True
    assert panel._checkboxes["Satellite RGB"].isChecked() is False  # was in the built-in default, not the saved one


def test_layer_toggle_panel_ignores_a_stale_saved_layer_name(tmp_path, qtbot):
    """A name that WAS saved but no longer exists as a real layer (e.g.
    removed by a later code change) must never raise - just be dropped."""
    settings = _isolated_settings(tmp_path)
    settings.setValue(LAYER_PREFERENCES_KEY, ["MSLP", "Some Layer That No Longer Exists"])

    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    panel = LayerTogglePanel(canvas, settings=settings)
    qtbot.addWidget(panel)

    assert canvas.layer_manager.active_layer_names == ["MSLP"]


def test_layer_toggle_panel_keeps_built_in_default_when_nothing_saved(tmp_path, qtbot):
    settings = _isolated_settings(tmp_path)
    canvas = MapCanvas()
    qtbot.addWidget(canvas)
    reference = LayerManager()

    panel = LayerTogglePanel(canvas, settings=settings)
    qtbot.addWidget(panel)

    assert canvas.layer_manager.active_layer_names == reference.active_layer_names
