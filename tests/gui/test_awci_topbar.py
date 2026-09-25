"""
Tests for acf.gui.dashboard.awci_topbar.AWCITopBar - the real light
top bar added 2026-09-12 (docs/reference/awci_dashboard_reference.png,
explicit user request "je veux que le dashboard soit exactement comme
celui dans la photo... 100%... tous les boutons fonctionnelles").
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_topbar import AWCITopBar


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_area_combo_has_the_2_real_options(qapp):
    topbar = AWCITopBar()
    items = [topbar.area_combo.itemText(i) for i in range(topbar.area_combo.count())]
    assert items == ["Global", "North Africa"]


def test_area_changed_emits_the_real_selected_text(qapp):
    topbar = AWCITopBar()
    seen = []
    topbar.areaChanged.connect(seen.append)
    topbar.area_combo.setCurrentText("North Africa")
    assert seen == ["North Africa"]


def test_set_status_updates_the_real_label_and_dot_color(qapp):
    topbar = AWCITopBar()
    topbar.set_status(is_real=True, label="REAL PHYSICS")
    assert topbar.status_label.text() == "REAL PHYSICS"
    assert "#22c55e" in topbar.status_dot.styleSheet()

    topbar.set_status(is_real=False, label="DEMO MODE")
    assert topbar.status_label.text() == "DEMO MODE"
    assert "#f59e0b" in topbar.status_dot.styleSheet()


def test_user_button_is_a_real_honest_disabled_placeholder(qapp):
    """No real user-account system exists in ACF yet - see module
    docstring - so this must be genuinely disabled, not a fabricated
    working control."""
    topbar = AWCITopBar()
    assert topbar.user_button.isEnabled() is False
    assert topbar.user_button.toolTip() != ""


def test_real_control_buttons_are_all_enabled(qapp):
    topbar = AWCITopBar()
    for button in (topbar.bell_button, topbar.hpc_button, topbar.settings_button, topbar.now_button):
        assert button.isEnabled() is True


# --------------------------------------------------------- _ElidingLabel
# Master Prompt V3 §32 ("1366x768/1280x800" responsive verification,
# added 2026-09-20) - real regression guard: the title label alone
# used to force this whole bar (and therefore the whole dashboard) 298px
# wider than necessary on a narrow real screen.


def test_eliding_label_keeps_full_text_when_wide_enough(qapp, qtbot):
    from acf.gui.dashboard.awci_topbar import _ElidingLabel

    label = _ElidingLabel("Aviation Weather Complexity Index")
    qtbot.addWidget(label)
    label.resize(400, 20)
    label.show()
    qtbot.waitExposed(label)

    assert label.text() == "Aviation Weather Complexity Index"


def test_eliding_label_elides_when_genuinely_too_narrow(qapp, qtbot):
    from acf.gui.dashboard.awci_topbar import _ElidingLabel

    label = _ElidingLabel("Aviation Weather Complexity Index")
    qtbot.addWidget(label)
    label.resize(60, 20)
    label.show()
    qtbot.waitExposed(label)

    assert label.text() != "Aviation Weather Complexity Index"
    assert label.text().endswith("…")


def test_eliding_label_has_a_real_minimum_width_of_1(qapp):
    """The whole point: this must be far smaller than the real
    un-elided text width (~299px for the topbar's own title), so a
    parent QHBoxLayout can genuinely shrink this column on a narrow
    real screen instead of being forced wider by it."""
    from acf.gui.dashboard.awci_topbar import _ElidingLabel

    label = _ElidingLabel("Aviation Weather Complexity Index")
    assert label.minimumWidth() == 1


def test_eliding_label_tooltip_always_shows_the_real_full_text(qapp, qtbot):
    from acf.gui.dashboard.awci_topbar import _ElidingLabel

    label = _ElidingLabel("Aviation Weather Complexity Index")
    qtbot.addWidget(label)
    label.resize(60, 20)
    label.show()
    qtbot.waitExposed(label)

    assert label.toolTip() == "Aviation Weather Complexity Index"


def test_eliding_label_settext_updates_the_real_full_text(qapp, qtbot):
    from acf.gui.dashboard.awci_topbar import _ElidingLabel

    label = _ElidingLabel("short")
    qtbot.addWidget(label)
    label.resize(400, 20)
    label.show()
    qtbot.waitExposed(label)

    label.setText("Aviation Weather Complexity Index")

    assert label.text() == "Aviation Weather Complexity Index"
    assert label.toolTip() == "Aviation Weather Complexity Index"


def test_topbar_title_and_status_labels_are_real_eliding_labels(qapp):
    """Real regression guard - confirms the actual topbar wiring, not
    just the standalone _ElidingLabel class."""
    from acf.gui.dashboard.awci_topbar import _ElidingLabel

    topbar = AWCITopBar()
    assert isinstance(topbar.model_label, _ElidingLabel)
    assert isinstance(topbar.last_update_label, _ElidingLabel)


# ------------------------------------------------- route-selector width
# (acf.gui.dashboard.awci_dashboard.AWCIDashboard) - same §32 pass; the
# route combo boxes' own default AdjustToContentsOnFirstShow policy was
# the other largest real contributor to the dashboard's minimum width.


def test_route_selector_combos_are_bounded_not_sized_to_the_longest_real_name(qapp):
    from acf.gui.dashboard.awci_dashboard import AWCIDashboard

    dashboard = AWCIDashboard()
    for combo in (dashboard.route_from_selector, dashboard.route_to_selector):
        assert combo.minimumContentsLength() == 14
        # Still every real airport - the bound is cosmetic (elided
        # display), never a reduction in real selectable options.
        assert combo.count() >= 5
