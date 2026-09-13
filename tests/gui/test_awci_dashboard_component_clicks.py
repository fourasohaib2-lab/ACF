"""
Tests for AWCIDashboard's clickable per-module detail dialog (explicit
user request "rend les bouton des différents complexité utilisable pour
rendre tout le details de la situation").

2026-09-13 refonte: clicks used to be dispatched via the old sidebar
component list's own real Signal (._ComponentRow.clicked). That column
has no place in the reference photo and was retired (see
awci_dashboard.py's own NOTE in _build_ui()) - the same real
AWCIComponentDetailDialog is now opened via AWCIHazardRow's own
clickable cards instead (_on_hazard_card_clicked()), which only cover
the 5 real hazard-row modules that have a distinct AWCICalculator
module of their own (dynamic/convective/microphysical/visibility/
ceiling - see HAZARD_CARDS' own docstring on "Wind Shear"). Clicks
below are dispatched via the card's own real Signal
(._HazardCard.clicked, wired through AWCIHazardRow.cardClicked) - the
exact mechanism mousePressEvent() triggers - not by calling the dialog
directly.
"""

import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.awci_dashboard import AWCIDashboard


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=8, n_lon=12, n_levels=6, steps=2, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


#: Hazard-card label -> the real module it drill-downs into (see
#: HAZARD_CARDS in awci_hazard_row.py) - only the 5 real clickable
#: cards (Wind Shear has no distinct module and is not clickable).
_CLICKABLE_CARDS = {
    "Turbulence": "dynamic",
    "Convection": "convective",
    "Icing": "microphysical",
    "Visibility": "visibility",
    "Ceiling": "ceiling",
}


def _press(card):
    event = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(5, 5), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    card.mousePressEvent(event)


def test_clicking_a_card_opens_the_detail_dialog_with_real_demo_data(qapp):
    dashboard = AWCIDashboard()
    assert dashboard._component_detail_window is None

    _press(dashboard.hazard_row._cards["Turbulence"])

    assert dashboard._component_detail_window is not None
    assert "REAL" in dashboard._component_detail_window.badge_label.text()
    assert "wind_speed" in dashboard._component_detail_window.inputs_label.text()


def test_clicking_reuses_the_same_dialog_instance(qapp):
    dashboard = AWCIDashboard()
    _press(dashboard.hazard_row._cards["Turbulence"])
    first = dashboard._component_detail_window
    _press(dashboard.hazard_row._cards["Icing"])
    assert dashboard._component_detail_window is first


def test_clicking_the_convection_card_in_real_physics_mode_shows_honest_default(qapp):
    """Real regression guard for the pipeline gap this dialog exists to
    disclose: convective is pinned at AWCICalculator's own default in
    Real Physics mode today (no real cape/cin per-point source wired
    into compute_real_complexity_volume())."""
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())

    _press(dashboard.hazard_row._cards["Convection"])

    assert "DEFAULT" in dashboard._component_detail_window.badge_label.text()


def test_clicking_the_turbulence_card_in_real_physics_mode_shows_real(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())

    _press(dashboard.hazard_row._cards["Turbulence"])

    assert "REAL" in dashboard._component_detail_window.badge_label.text()
    assert "Real Physics solver" in dashboard._component_detail_window.badge_label.text()


def test_every_clickable_card_is_independently_clickable(qapp):
    dashboard = AWCIDashboard()
    for label in _CLICKABLE_CARDS:
        _press(dashboard.hazard_row._cards[label])
        assert dashboard._component_detail_window.windowTitle() != ""  # a real title was set for this module


def test_the_wind_shear_card_is_not_clickable(qapp):
    """Wind Shear has no distinct real AWCICalculator module of its own
    (see HAZARD_CARDS' own docstring) - never a fabricated drill-down."""
    dashboard = AWCIDashboard()
    _press(dashboard.hazard_row._cards["Wind Shear"])
    assert dashboard._component_detail_window is None


# ------------------------------- real drill-down chain (§26/§53, added 2026-09-03)


def test_clicking_a_card_shows_a_real_drill_down_trace_in_demo_mode(qapp):
    """build_awci_result()/AWCIResult.trace_chain() (§26/§53/§81) existed
    since an earlier closure this session but were never wired into any
    GUI - real regression guard that this dialog now shows the real
    trace text, not the "not available" placeholder."""
    dashboard = AWCIDashboard()
    assert dashboard._last_awci_result is not None  # refresh() in __init__ already built one

    _press(dashboard.hazard_row._cards["Turbulence"])

    trace_text = dashboard._component_detail_window.trace_label.text()
    assert "not available - no real AWCIResult" not in trace_text
    assert "Score: AWCI =" in trace_text
    assert "Diagnostics (module scores):" in trace_text


def test_drill_down_trace_reflects_the_same_real_raw_variables_as_the_inputs_section(qapp):
    dashboard = AWCIDashboard()

    _press(dashboard.hazard_row._cards["Turbulence"])

    dialog = dashboard._component_detail_window
    assert "wind_speed" in dialog.inputs_label.text()
    assert "Variables:" in dialog.trace_label.text()
    assert "wind_speed" in dialog.trace_label.text()


def test_drill_down_trace_includes_the_real_vertical_level_in_real_physics_mode(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())

    _press(dashboard.hazard_row._cards["Turbulence"])

    trace_text = dashboard._component_detail_window.trace_label.text()
    assert "Niveau vertical:" in trace_text
    assert "not available" not in trace_text.split("Niveau vertical:")[1]
