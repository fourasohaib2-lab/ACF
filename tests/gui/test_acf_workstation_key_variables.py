from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_key_variables import KeyVariablesPanel


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def _fake_volume(n_levels=3, n_lat=4, n_lon=4):
    rng = np.random.default_rng(0)
    return {
        "model": "AROME",
        "temperature_volume": 290.0 + rng.normal(size=(n_levels, n_lat, n_lon)),
        "wind_speed_volume": np.abs(rng.normal(10.0, 2.0, size=(n_levels, n_lat, n_lon))),
        "specific_humidity_volume": np.abs(rng.normal(0.008, 0.002, size=(n_levels, n_lat, n_lon))),
        "pressure_volume_hpa": np.linspace(1000, 700, n_levels)[:, None, None] * np.ones((n_levels, n_lat, n_lon)),
        "u_volume": rng.normal(size=(n_levels, n_lat, n_lon)),
        "v_volume": rng.normal(size=(n_levels, n_lat, n_lon)),
        "lats": np.linspace(35.0, 45.0, n_lat),
        "lons": np.linspace(-5.0, 15.0, n_lon),
    }


def test_key_variables_panel_shows_real_values(qapp, qtbot):
    panel = KeyVariablesPanel()
    qtbot.addWidget(panel)
    panel.update_from_volume(_fake_volume(), level_index=0)

    assert panel.temperature_value.text() != ""
    assert "K" in panel.temperature_value.text() or "°C" in panel.temperature_value.text()
    assert panel.wind_speed_value.text() != ""
    # CAPE/CIN/LCL come from compute_real_convection_indices_field - may be
    # NaN-only on this tiny synthetic grid, but must render SOMETHING, not crash.
    assert panel.cape_value.text() != ""
    assert panel.lcl_value.text() != ""


def test_key_variables_panel_before_any_volume_is_honest(qapp, qtbot):
    panel = KeyVariablesPanel()
    qtbot.addWidget(panel)
    assert "NOT_" in panel.temperature_value.text()
