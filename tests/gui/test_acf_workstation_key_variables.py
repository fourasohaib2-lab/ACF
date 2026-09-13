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
    # CAPE/CIN/LCL/Shear come from compute_real_convection_indices_field - may be
    # NaN-only on this tiny synthetic grid, but must render SOMETHING, not crash.
    assert panel.cape_value.text() != ""
    assert panel.lcl_value.text() != ""
    assert panel.shear_value.text() != ""

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
    lcl_expected_m = indices["lcl_m"][sub_ci, sub_cj]
    if np.isnan(lcl_expected_m):
        assert panel.lcl_value.text() == "NOT_COMPUTED"
    else:
        # Real display conversion (matches acf_workstation_reference.jpg's
        # own "LCL" row, shown in hPa): the standard barometric/hypsometric
        # formula, using the same-cell real surface pressure.
        surface_pressure_hpa = float(volume["pressure_volume_hpa"][0, ci, cj])
        lcl_expected_hpa = surface_pressure_hpa * (1.0 - lcl_expected_m / 44330.0) ** 5.255
        assert panel.lcl_value.text() == f"{lcl_expected_hpa:.0f} hPa"

    shear_expected_ms = indices["bulk_shear_m_s"][sub_ci, sub_cj]
    if np.isnan(shear_expected_ms):
        assert panel.shear_value.text() == "NOT_COMPUTED"
    else:
        # Real unit conversion (matches the reference image's own "kt"
        # units for wind/shear rows): 1 m/s = 1.9438445 kt.
        shear_expected_kt = shear_expected_ms * 1.9438445
        assert panel.shear_value.text() == f"{shear_expected_kt:.0f} kt"


def test_key_variables_panel_before_any_volume_is_honest(qapp, qtbot):
    panel = KeyVariablesPanel()
    qtbot.addWidget(panel)
    assert "NOT_" in panel.temperature_value.text()
    assert "NOT_" in panel.shear_value.text()
