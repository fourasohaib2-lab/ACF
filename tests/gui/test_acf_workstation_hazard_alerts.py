from __future__ import annotations

import math

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_hazard_alerts import HazardAlertsPanel


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize(
    ("cape", "shear", "wet_bulb", "rh", "expected_convection", "expected_turbulence", "expected_visibility", "expected_icing"),
    [
        (2500.0, 25.0, 5.0, 60.0, "High", "High", "Low", "Low"),
        (400.0, 8.0, -1.0, 55.0, "Moderate", "Low", "Low", "High"),
        (100.0, 2.0, 10.0, 96.0, "Low", "Low", "High", "Low"),
    ],
)
def test_hazard_thresholds_are_real_and_documented(
    qapp, qtbot, cape, shear, wet_bulb, rh, expected_convection, expected_turbulence, expected_visibility, expected_icing
):
    panel = HazardAlertsPanel()
    qtbot.addWidget(panel)
    panel.update_from_indices(
        cape_j_kg=cape, bulk_shear_m_s=shear, wet_bulb_c=wet_bulb, relative_humidity_pct=rh
    )
    assert panel.convection_level.text() == expected_convection
    assert panel.turbulence_level.text() == expected_turbulence
    assert panel.visibility_level.text() == expected_visibility
    assert panel.icing_level.text() == expected_icing


def test_hazard_alerts_honest_when_inputs_missing(qapp, qtbot):
    panel = HazardAlertsPanel()
    qtbot.addWidget(panel)
    panel.update_from_indices(
        cape_j_kg=math.nan, bulk_shear_m_s=math.nan, wet_bulb_c=None, relative_humidity_pct=None
    )
    assert panel.convection_level.text() == "NOT_COMPUTED"
    assert panel.turbulence_level.text() == "NOT_COMPUTED"
    assert panel.visibility_level.text() == "NOT_COMPUTED"
    assert panel.icing_level.text() == "NOT_COMPUTED"
