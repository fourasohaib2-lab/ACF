from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.workstation_fields import CONVECTION_GRID_STRIDE
from acf.gui.dashboard.acf_workstation_key_variables import KeyVariablesPanel
from acf.science.moisture import Moisture


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
    volume = _fake_volume()
    panel.update_from_volume(volume, level_index=0)

    assert panel.temperature_value.text() != ""
    assert "K" in panel.temperature_value.text() or "°C" in panel.temperature_value.text()
    assert panel.wind_speed_value.text() != ""
    # CAPE/CIN/LCL come from compute_real_convection_indices_field - may be
    # NaN-only on this tiny synthetic grid, but must render SOMETHING, not crash.
    assert panel.cape_value.text() != ""
    assert panel.lcl_value.text() != ""

    # Relative humidity must be the real Moisture conversion at the
    # SAME full-resolution center grid cell (ci, cj) the temperature
    # readout uses - not a fabricated q/0.02 formula.
    lats = volume["lats"]
    lons = volume["lons"]
    ci, cj = len(lats) // 2, len(lons) // 2
    temp_k = float(volume["temperature_volume"][0, ci, cj])
    q_kg_kg = float(volume["specific_humidity_volume"][0, ci, cj])
    pressure_hpa = float(volume["pressure_volume_hpa"][0, ci, cj])
    expected_rh_pct = min(
        100.0,
        100.0 * Moisture.relative_humidity_from_temperature(q_kg_kg, pressure_hpa, temp_k),
    )
    assert panel.humidity_value.text() == f"{expected_rh_pct:.0f} %"


def test_key_variables_panel_reads_the_same_grid_cell_for_convection_indices(qapp, qtbot):
    """CAPE/CIN/LCL must come from the strided sub-grid cell nearest to
    the SAME full-resolution (ci, cj) center point used for
    Temperature/Wind Speed/Relative Humidity - not an independently
    halved sub-grid shape."""
    from acf.awci.workstation_fields import compute_real_convection_indices_field

    panel = KeyVariablesPanel()
    qtbot.addWidget(panel)
    volume = _fake_volume()
    panel.update_from_volume(volume, level_index=0)

    lats = volume["lats"]
    lons = volume["lons"]
    ci, cj = len(lats) // 2, len(lons) // 2
    sub_ci, sub_cj = ci // CONVECTION_GRID_STRIDE, cj // CONVECTION_GRID_STRIDE

    indices = compute_real_convection_indices_field(
        volume["temperature_volume"],
        volume["specific_humidity_volume"],
        volume["pressure_volume_hpa"],
        volume["u_volume"],
        volume["v_volume"],
        lats,
        lons,
    )
    lcl_expected = indices["lcl_m"][sub_ci, sub_cj]
    if np.isnan(lcl_expected):
        assert panel.lcl_value.text() == "NOT_COMPUTED"
    else:
        assert panel.lcl_value.text() == f"{lcl_expected:.0f} m"


def test_key_variables_panel_before_any_volume_is_honest(qapp, qtbot):
    panel = KeyVariablesPanel()
    qtbot.addWidget(panel)
    assert "NOT_" in panel.temperature_value.text()
