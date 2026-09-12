"""
Real responsive-sizing regression test for AWCIDashboardWindow.

AWCIDashboard's own real, stacked maps/charts (global map, cross-
section, regional map, regional trend, ...) give it a genuine measured
minimum size of ~1489x1064 - larger than plenty of real screens
(1366x768/1280x800/1024x768 laptops). `fit_window_to_screen`'s own
resize()/margin clamp cannot fix this on its own: Qt floors a
QMainWindow's actual minimum size to its central widget's, no matter
what size was requested. Wrapped in a QScrollArea - the window's own
minimum drops to just the scroll area's frame, and the window can
always be shrunk to whatever the operator's screen allows.

(ESOC used to also embed this identical AWCIDashboard widget a second
time, redundantly, as a tab in its own bottom dock, wrapped the same
way - that embedding was removed 2026-09-12; this standalone window,
opened via ESOC's own "AWCI" toolbar button, is now the one real way
to reach it.)
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QScrollArea

from acf.gui.dashboard.awci_window import AWCIDashboardWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_awci_dashboard_window_central_widget_is_a_scroll_area(qapp):
    window = AWCIDashboardWindow()
    assert isinstance(window.centralWidget(), QScrollArea)
    assert window.centralWidget().widget() is window.awci_dashboard


def test_awci_dashboard_window_minimum_size_is_no_longer_floored_by_the_dashboards_own_layout(qapp):
    window = AWCIDashboardWindow()
    window.show()
    # AWCIDashboard's own real minimumSizeHint (measured ~1489x1064,
    # from its stacked maps/charts) must no longer be the window's own
    # enforced floor now that it sits behind a resizable scroll area.
    assert window.minimumSizeHint().width() < 500
    assert window.minimumSizeHint().height() < 500


def test_awci_dashboard_window_can_be_shrunk_below_the_dashboards_own_natural_size(qapp):
    window = AWCIDashboardWindow()
    window.show()

    window.resize(700, 500)
    qapp.processEvents()
    assert window.width() == 700
    assert window.height() == 500


def test_awci_dashboard_still_renders_at_full_size_when_the_screen_allows_it(qapp):
    """The scroll wrap must not silently shrink the dashboard when
    there's plenty of room - setWidgetResizable(True) is what keeps
    this the same visual result as before on any normal-sized screen."""
    window = AWCIDashboardWindow()
    window.show()
    window.resize(1600, 1100)
    qapp.processEvents()

    dashboard_size = window.awci_dashboard.size()
    assert dashboard_size.width() > 1400
    assert dashboard_size.height() > 900


def test_awci_dashboard_window_is_wide_enough_for_its_own_real_header(qapp):
    """
    NOTE (correction, 2026-09-07 - real bug, found from a real
    screenshot while modernizing this dashboard's visual design, not a
    code read): AWCIDashboardWindow used to call fit_window_to_screen(
    self, 1500, 950) BEFORE self.awci_dashboard existed, so the fixed
    1500 guess had no way to know the header row's own real natural
    width (title + the 6 header buttons + the RESEARCH STAGE badge) -
    confirmed by direct measurement to need ~1533px, 33px more than the
    guess. The badge's right edge was genuinely clipped in a real
    screenshot on a screen plenty large enough for either width - this
    was never actually a screen-size problem (an earlier pass in this
    same session initially misdiagnosed it as one, comparing against
    the wrong QScreen). Fixed by sizing the window from the dashboard's
    own real, current sizeHint() instead of a second guessed constant -
    self-correcting if a future change grows or shrinks the header.

    The window must end up as wide as the dashboard's own real natural
    width, UNLESS the available screen itself is too small for that -
    in which case fit_window_to_screen's own existing clamp (margin=
    0.92 of the screen's available width) is still the correct,
    expected behaviour (the QScrollArea then takes over, per this
    file's own first test above), not a regression this fix should
    override. The offscreen platform this whole suite runs under
    reports an 800x800 virtual screen - smaller than the real header's
    ~1533px natural width - which is exactly the scenario this
    distinction matters for; a real, wide desktop screen exercises the
    "wide enough" branch instead.
    """
    window = AWCIDashboardWindow()
    window.show()
    qapp.processEvents()

    natural_width = window.awci_dashboard.sizeHint().width()
    available_width = window.screen().availableGeometry().width()
    expected_width = min(natural_width, int(available_width * 0.92))

    assert window.width() == expected_width
    if available_width * 0.92 >= natural_width:
        assert window.width() >= natural_width  # the real bug's own scenario: not narrower than the header needs
