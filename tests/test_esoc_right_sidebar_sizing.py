"""
Real responsive-sizing regression test for ESOCRightSidebar's 7
Inspector tabs (Properties/Diagnostics/Metadata/Simulation/Logs/
Performance/AI Analysis & Plots).

Same class of bug as ESOCLayout.bottom_tabs and ACFWorkstation.stack
(see acf.gui.widgets.current_page_sizing's own module docstring): a
plain QTabWidget floors ITS OWN minimum size at the single largest of
its pages - here "AI Analysis & Plots" - even while a smaller tab like
"Properties" is the one actually selected. Smaller in magnitude than
the other two cases (~20px width / ~120px height, not hundreds), but
the same real effect, so fixed the same way (CurrentPageTabWidget) for
consistency.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.esoc.esoc_sidebar import ESOCRightSidebar
from acf.gui.widgets.current_page_sizing import CurrentPageTabWidget


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_right_sidebar_uses_the_current_page_sizing_tab_widget(qapp):
    sidebar = ESOCRightSidebar()
    assert isinstance(sidebar.tabs, CurrentPageTabWidget)


def test_right_sidebar_min_size_follows_the_smaller_selected_tab(qapp):
    sidebar = ESOCRightSidebar()
    sidebar.show()

    properties_index = next(i for i in range(sidebar.tabs.count()) if sidebar.tabs.tabText(i) == "Properties")
    ai_index = next(i for i in range(sidebar.tabs.count()) if "AI Analysis" in sidebar.tabs.tabText(i))

    sidebar.tabs.setCurrentIndex(ai_index)
    ai_min = sidebar.tabs.minimumSizeHint()

    sidebar.tabs.setCurrentIndex(properties_index)
    properties_min = sidebar.tabs.minimumSizeHint()

    assert properties_min.height() < ai_min.height()
