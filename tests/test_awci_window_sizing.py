"""
Real responsive-sizing regression test for AWCIDashboardWindow.

AWCIDashboard's own real, stacked maps/charts (global map, cross-
section, regional map, regional trend, ...) give it a genuine measured
minimum size of ~1489x1064 - larger than plenty of real screens
(1366x768/1280x800/1024x768 laptops). `fit_window_to_screen`'s own
resize()/margin clamp cannot fix this on its own: Qt floors a
QMainWindow's actual minimum size to its central widget's, no matter
what size was requested. Wrapped in a QScrollArea - the same pattern,
and the same real AWCIDashboard widget class, `PanelManager.
AWCIDashboardPanel` already uses to embed this identical dashboard
inside ESOC's own dock (see that class's own docstring) - the window's
own minimum drops to just the scroll area's frame, and the window can
always be shrunk to whatever the operator's screen allows.
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
