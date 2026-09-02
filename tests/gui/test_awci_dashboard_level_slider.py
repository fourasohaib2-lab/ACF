"""
Tests for AWCIDashboard's real vertical-level slider (explicit user
request "ajoute la 4eme dimension au niveau d'affichage des cartes")
- completes the already-real (time, level, lat, lon) data pipeline
(acf.awci.vertical_field.compute_real_complexity_volume(),
acf.awci.temporal_field.compute_real_complexity_evolution()) that
every consumer used to hardcode to level 0 (surface) with no user
control over the level axis at all.
"""

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.temporal_field import compute_real_complexity_evolution
from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.awci_dashboard import AWCIDashboard


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=10, n_lon=18, n_levels=6, steps=3, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def _real_evolution(**overrides):
    kwargs = dict(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=5, n_frames=4, steps_per_frame=2,
        perturbation_scale=2.0, seed=1,
    )
    kwargs.update(overrides)
    return compute_real_complexity_evolution(**kwargs)


def test_level_slider_disabled_before_real_physics(qapp):
    dashboard = AWCIDashboard()
    assert dashboard.level_slider.isEnabled() is False
    assert dashboard.level_slider.maximum() == 0


def test_level_slider_enabled_with_real_range_after_real_physics_ready(qapp):
    dashboard = AWCIDashboard()
    volume = _real_volume(n_levels=6)

    dashboard._on_real_physics_ready(volume)

    assert dashboard.level_slider.isEnabled() is True
    assert dashboard.level_slider.maximum() == 5  # n_levels - 1
    assert dashboard.level_slider.value() == 0
    assert "L0" in dashboard.level_readout.text()


def test_moving_the_level_slider_genuinely_changes_the_global_map_field(qapp):
    dashboard = AWCIDashboard()
    volume = _real_volume(n_levels=6)
    dashboard._on_real_physics_ready(volume)
    _lons, _lats, surface_grid = dashboard.global_map._external_field

    dashboard.level_slider.setValue(5)

    _lons2, _lats2, top_grid = dashboard.global_map._external_field
    assert dashboard._current_level_index == 5
    np.testing.assert_array_equal(top_grid, volume["awci_volume"][5])
    assert not np.array_equal(surface_grid, top_grid)
    assert "L5" in dashboard.global_map._title


def test_moving_the_level_slider_updates_the_readout_with_a_real_mean_pressure(qapp):
    dashboard = AWCIDashboard()
    volume = _real_volume(n_levels=6)
    dashboard._on_real_physics_ready(volume)

    dashboard.level_slider.setValue(3)

    expected_pressure = float(np.mean(volume["pressure_volume_hpa"][3]))
    assert "L3" in dashboard.level_readout.text()
    assert f"{expected_pressure:.0f}" in dashboard.level_readout.text()


def test_moving_the_level_slider_reslices_the_same_volume_without_recomputing(qapp):
    """Real proof no new solver run happens on a slider move - the
    exact same volume object is still referenced afterward."""
    dashboard = AWCIDashboard()
    volume = _real_volume(n_levels=6)
    dashboard._on_real_physics_ready(volume)

    dashboard.level_slider.setValue(2)

    assert dashboard._real_volume is volume


def test_moving_the_level_slider_updates_the_point_component_scores_for_real(qapp):
    """component_list (the numeric module-score readout next to the
    radar) is recomputed from the real volume at the point of interest
    for the newly selected level - real proof this is not just the map
    that updates."""
    dashboard = AWCIDashboard()
    volume = _real_volume(n_levels=6)
    dashboard._on_real_physics_ready(volume)
    surface_texts = {key: label.text() for key, label in dashboard.component_list._values.items()}

    dashboard.level_slider.setValue(5)

    top_texts = {key: label.text() for key, label in dashboard.component_list._values.items()}
    assert surface_texts != top_texts


def test_revert_to_demo_disables_and_resets_the_level_slider(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume(n_levels=6))
    dashboard.level_slider.setValue(4)

    dashboard._revert_to_demo()

    assert dashboard.level_slider.isEnabled() is False
    assert dashboard.level_slider.value() == 0
    assert dashboard.level_slider.maximum() == 0
    assert dashboard.level_readout.text() == "L0"
    assert dashboard._real_volume is None
    assert dashboard._current_level_index == 0


def test_evolution_playback_respects_the_selected_level_not_hardcoded_surface(qapp):
    """Real regression guard: _render_evolution_frame() used to
    hardcode level 0 regardless of the level slider - this locks in
    that the 4D animation now genuinely follows the user's selected
    level."""
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume(n_levels=6))
    dashboard.level_slider.setValue(3)
    evolution = _real_evolution(n_levels=5)

    dashboard._on_evolution_ready(evolution)

    _lons, _lats, grid = dashboard.global_map._external_field
    np.testing.assert_array_equal(grid, evolution["awci_evolution"][0, 3])
    assert "L3" in dashboard.global_map._title


def test_evolution_playback_clamps_a_level_beyond_the_evolutions_own_range(qapp):
    """The static Real Physics volume and the 4D evolution can have
    different real n_levels (independent solver runs/configs) - a
    level selected on the (larger) volume must not index out of bounds
    on a (smaller) evolution array."""
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume(n_levels=8))
    dashboard.level_slider.setValue(7)  # valid for the volume (8 levels)
    evolution = _real_evolution(n_levels=4)  # but the evolution only has 4

    dashboard._on_evolution_ready(evolution)  # must not raise IndexError

    _lons, _lats, grid = dashboard.global_map._external_field
    np.testing.assert_array_equal(grid, evolution["awci_evolution"][0, 3])  # clamped to the last real level
