"""
Tests for acf.gui.dashboard.awci_hazard_row.AWCIHazardRow - the real
"AWCI GLOBAL" gauge + 6 hazard cards row added 2026-09-12 (docs/
reference/awci_dashboard_reference.png, Phase 2/6 of that redesign).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_hazard_row import AWCIHazardRow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _module_scores(**overrides):
    base = {
        "dynamic": 72.0,
        "convective": 91.0,
        "microphysical": 52.0,
        "visibility": 28.0,
        "ceiling": 46.0,
    }
    base.update(overrides)
    return base


def test_gauge_shows_the_real_overall_awci_score(qapp):
    row = AWCIHazardRow()
    row.update_data(_module_scores(), overall_awci=72.0)
    assert row.gauge._score == 72.0


def test_cards_show_the_real_module_scores_without_a_second_scaling(qapp):
    """Real regression guard: module_scores arrives already on the
    real 0-100 scale (AWCICalculator.calculate_module_scores() itself
    does round(v * 100, 1)) - a second *100 here would show 9100
    instead of 91."""
    row = AWCIHazardRow()
    row.update_data(_module_scores(), overall_awci=72.0)
    assert row._cards["Turbulence"].value_label.text() == "72"
    assert row._cards["Convection"].value_label.text() == "91"
    assert row._cards["Icing"].value_label.text() == "52"
    assert row._cards["Visibility"].value_label.text() == "28"
    assert row._cards["Ceiling"].value_label.text() == "46"


def test_wind_shear_is_an_honest_dash_never_a_duplicated_number(qapp):
    """No standalone real wind-shear module score exists - see module
    docstring - so this card must always show the real, disclosed gap
    (—), never Turbulence's own dynamic-module number relabeled."""
    row = AWCIHazardRow()
    row.update_data(_module_scores(), overall_awci=72.0)
    assert row._cards["Wind Shear"].value_label.text() == "—"
    assert row._cards["Wind Shear"].toolTip() != ""


def test_severity_labels_match_the_real_shared_awci_scale(qapp):
    """Uses the SAME real level_for() scale as the map legend/gauge -
    not a separately invented one."""
    from acf.gui.dashboard.awci_colors import level_for

    row = AWCIHazardRow()
    row.update_data(_module_scores(), overall_awci=72.0)
    assert row._cards["Convection"].severity_label.text() == level_for(91.0)
    assert row._cards["Icing"].severity_label.text() == level_for(52.0)


def test_missing_module_score_keys_default_honestly_to_zero(qapp):
    row = AWCIHazardRow()
    row.update_data({}, overall_awci=0.0)
    assert row._cards["Turbulence"].value_label.text() == "0"
    assert row._cards["Wind Shear"].value_label.text() == "—"
