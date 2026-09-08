"""
Tests for acf.gui.dashboard.awci_volume_3d.AWCIVolume3DView - the real
3D half of "ajoute la 4eme dimension au niveau d'affichage des cartes"
(the user, asked whether 4D should mean a 2D time/level control or a
real 3D view, answered "Fait les deux car j'hésite" - do both).
"""

from __future__ import annotations

import numpy as np

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.awci_volume_3d import AWCIVolume3DView


def test_starts_empty_with_no_fabricated_placeholder_surface(qtbot):
    view = AWCIVolume3DView()
    qtbot.addWidget(view)
    assert view.status()["has_data"] is False


def test_set_volume_with_a_real_solver_result_populates_it(qtbot):
    view = AWCIVolume3DView()
    qtbot.addWidget(view)
    volume = compute_real_complexity_volume(model="ALADIN", n_lat=8, n_lon=12, n_levels=6, steps=2)

    view.set_volume(volume["lons"], volume["lats"], volume["awci_volume"], volume["pressure_volume_hpa"], label="REAL PHYSICS")

    assert view.status()["has_data"] is True
    assert "REAL PHYSICS" in view._title


def test_clear_volume_returns_to_the_empty_state(qtbot):
    view = AWCIVolume3DView()
    qtbot.addWidget(view)
    volume = compute_real_complexity_volume(model="ALADIN", n_lat=8, n_lon=12, n_levels=6, steps=2)
    view.set_volume(volume["lons"], volume["lats"], volume["awci_volume"], volume["pressure_volume_hpa"])

    view.clear_volume()

    assert view.status()["has_data"] is False


def test_subsamples_levels_when_the_real_volume_exceeds_max_levels(qtbot):
    """A real, disclosed display choice - not silently dropping real
    data, just not drawing every one of many real levels at once."""
    view = AWCIVolume3DView()
    qtbot.addWidget(view)
    volume = compute_real_complexity_volume(model="ALADIN", n_lat=6, n_lon=8, n_levels=20, steps=2)

    view.set_volume(
        volume["lons"], volume["lats"], volume["awci_volume"], volume["pressure_volume_hpa"], max_levels=5
    )

    zticks = view.axis.get_zticks()
    assert len(zticks) <= 5
    # The first and last real levels are always included, not just an arbitrary subset.
    assert 0 in zticks
    assert 19 in zticks


def test_zaxis_labels_show_a_real_domain_mean_pressure_per_level(qtbot):
    view = AWCIVolume3DView()
    qtbot.addWidget(view)
    volume = compute_real_complexity_volume(model="ALADIN", n_lat=8, n_lon=12, n_levels=4, steps=2)

    view.set_volume(volume["lons"], volume["lats"], volume["awci_volume"], volume["pressure_volume_hpa"])

    labels = [t.get_text() for t in view.axis.get_zticklabels()]
    expected_surface_pressure = float(np.mean(volume["pressure_volume_hpa"][0]))
    assert any(f"{expected_surface_pressure:.0f}hPa" in label for label in labels)
