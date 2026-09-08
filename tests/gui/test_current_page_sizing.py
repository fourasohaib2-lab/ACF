"""
Tests for acf.gui.widgets.current_page_sizing.

Real bug this closes (see that module's own docstring for the full
writeup, and the measured numbers from the live codebase it was
verified against): `QStackedWidget`/`QTabWidget` both default to
sizing themselves off the LARGEST of every page they hold, not the one
actually showing, so a container - and anything whose own minimum size
Qt floors to it (a QMainWindow via its dock widgets, in
`ESOCLayout.bottom_tabs`'s real case) - can never shrink below its
single biggest page, however small the page currently selected is.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QWidget

from acf.gui.widgets.current_page_sizing import CurrentPageStackedWidget, CurrentPageTabWidget


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _page(width: int, height: int) -> QWidget:
    page = QWidget()
    page.setMinimumSize(width, height)
    return page


# ------------------------------------------------------------- CurrentPageStackedWidget


def test_stacked_widget_min_size_follows_small_current_page_not_the_largest(qapp):
    stack = CurrentPageStackedWidget()
    small = _page(100, 80)
    big = _page(600, 500)
    stack.addWidget(small)
    stack.addWidget(big)

    # NOTE: comparing against the *explicit* setMinimumSize(), not
    # small.minimumSizeHint() - a bare QWidget's own minimumSizeHint()
    # ignores an explicit setMinimumSize() entirely (it stays an invalid
    # QSize(-1, -1) with no layout of its own); CurrentPageStackedWidget
    # is meant to report the size the page will *actually* enforce
    # inside a layout, i.e. `_effective_min_size()`'s combination of the
    # two - see that helper's own docstring.
    stack.setCurrentWidget(small)
    assert stack.minimumSizeHint() == QSize(100, 80)
    assert stack.minimumSizeHint() != QSize(600, 500)


def test_stacked_widget_min_size_grows_back_for_the_actually_large_page(qapp):
    stack = CurrentPageStackedWidget()
    small = _page(100, 80)
    big = _page(600, 500)
    stack.addWidget(small)
    stack.addWidget(big)

    stack.setCurrentWidget(big)
    assert stack.minimumSizeHint() == QSize(600, 500)


def test_stacked_widget_size_hint_also_follows_current_page(qapp):
    stack = CurrentPageStackedWidget()
    small = _page(100, 80)
    big = _page(600, 500)
    stack.addWidget(small)
    stack.addWidget(big)

    stack.setCurrentWidget(small)
    assert stack.sizeHint() == small.sizeHint()


def test_stacked_widget_falls_back_to_default_when_empty(qapp):
    stack = CurrentPageStackedWidget()
    # No pages added - must not raise, and must behave like a plain
    # QStackedWidget (super()'s own hint) rather than crash on
    # `currentWidget()` being None.
    assert stack.currentWidget() is None
    stack.minimumSizeHint()
    stack.sizeHint()


# ------------------------------------------------------------- CurrentPageTabWidget


def test_tab_widget_min_size_follows_small_current_tab_not_the_largest(qapp):
    tabs = CurrentPageTabWidget()
    small = _page(100, 80)
    big = _page(600, 500)
    tabs.addTab(small, "Small")
    tabs.addTab(big, "Big")

    tabs.setCurrentIndex(0)
    small_min = tabs.minimumSizeHint()
    tabs.setCurrentIndex(1)
    big_min = tabs.minimumSizeHint()

    assert small_min.width() < big_min.width()
    assert small_min.height() < big_min.height()


def test_tab_widget_min_size_shrinks_back_after_returning_to_a_small_tab(qapp):
    tabs = CurrentPageTabWidget()
    small = _page(100, 80)
    big = _page(600, 500)
    tabs.addTab(small, "Small")
    tabs.addTab(big, "Big")

    tabs.setCurrentIndex(1)
    big_min = tabs.minimumSizeHint()
    tabs.setCurrentIndex(0)
    small_min_again = tabs.minimumSizeHint()

    assert small_min_again.width() < big_min.width()
    assert small_min_again.height() < big_min.height()


def test_tab_widget_min_size_accounts_for_the_tab_bar_chrome(qapp):
    """Even a tiny page's reported minimum must not claim less width
    than the tab bar itself needs to show its own tabs/scroll buttons."""
    tabs = CurrentPageTabWidget()
    tiny = _page(1, 1)
    tabs.addTab(tiny, "One")
    tabs.addTab(_page(1, 1), "Two")
    tabs.setCurrentIndex(0)

    min_size = tabs.minimumSizeHint()
    assert min_size.width() >= tabs.tabBar().minimumSizeHint().width()
    assert min_size.height() > tiny.minimumSizeHint().height()  # tab bar adds real height


def test_tab_widget_falls_back_to_default_when_empty(qapp):
    tabs = CurrentPageTabWidget()
    assert tabs.currentWidget() is None
    tabs.minimumSizeHint()
    tabs.sizeHint()


def test_tab_widget_many_tabs_does_not_force_full_tab_bar_width(qapp):
    """Regression guard for the exact bug found in ESOCLayout.bottom_tabs
    (44 real tabs): the fix must use the tab bar's own *minimum* size
    hint (which QTabWidget's scroll buttons can satisfy) as the width
    floor, never its full (preferred) sizeHint() - the width needed to
    lay out every tab label with no scrolling at all, which for many
    tabs is far larger than any reasonable minimum."""
    tabs = CurrentPageTabWidget()
    for i in range(30):
        tabs.addTab(_page(80, 60), f"A Reasonably Long Tab Label {i}")
    tabs.setCurrentIndex(0)

    min_size = tabs.minimumSizeHint()
    full_bar_width = tabs.tabBar().sizeHint().width()
    assert min_size.width() < full_bar_width
