"""
Tests for the ACF Scientific Workstation's left navigation sidebar
(`acf.gui.dashboard.acf_workstation_sidebar.WorkstationSidebar`) -
the static Home/Data/Science/Analysis/Reports/Infrastructure/Settings
tree of `acf_workstation_reference.jpg`'s own left column.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_sidebar import WorkstationSidebar

_SECTIONS = [
    "Home", "Data", "Science", "Analysis", "Reports", "Infrastructure", "Settings",
]


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_sidebar_lists_every_reference_section(qapp, qtbot):
    sidebar = WorkstationSidebar()
    qtbot.addWidget(sidebar)
    for section in _SECTIONS:
        assert sidebar.findChild(object, section) is not None or section in sidebar.section_names()


def test_sidebar_emits_section_selected(qapp, qtbot):
    sidebar = WorkstationSidebar()
    qtbot.addWidget(sidebar)
    with qtbot.waitSignal(sidebar.sectionSelected, timeout=1000) as blocker:
        sidebar.select_section("Science")
    assert blocker.args == ["Science"]


def test_sidebar_ignores_an_unknown_section(qapp, qtbot):
    """A name that is not one of the real reference sections must not
    change the selection and must not emit - never a fabricated
    section."""
    sidebar = WorkstationSidebar()
    qtbot.addWidget(sidebar)
    sidebar.select_section("Science")
    emitted: list[str] = []
    sidebar.sectionSelected.connect(emitted.append)

    sidebar.select_section("Not A Real Section")

    assert emitted == []
    assert sidebar.current_section() == "Science"
