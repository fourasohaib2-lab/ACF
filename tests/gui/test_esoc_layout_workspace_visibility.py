"""
Regression tests for ESOCLayout.apply_workspace_profile()'s real panel-
visibility gap, found during a full ESOC rescan (2026-09-11):

apply_workspace_profile() used to read profile["primary_panel"] (drives
tab FOCUS, real) but never profile["visible_panels"] at all, despite
every one of WorkspaceManager's 10 mode profiles defining one specifically
to describe which bottom-dock tabs should be shown for that mode - so all
44 tabs stayed visible regardless of workspace mode; only focus worked.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.esoc_layout import ESOCLayout
from acf.gui.esoc.esoc_workspace import WorkspaceManager, WorkspaceMode
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import PanelManager


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def layout(qapp):
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    panel_manager = PanelManager(registry, dispatcher)
    window = QMainWindow()
    return ESOCLayout(window, panel_manager, registry=registry)


def _visible_tab_keys(layout: ESOCLayout) -> set[str]:
    panel_keys = layout.panel_manager.list_panel_names()
    return {
        panel_keys[i]
        for i in range(layout.bottom_tabs.count())
        if layout.bottom_tabs.isTabVisible(i)
    }


def test_all_tabs_start_visible(layout):
    assert all(layout.bottom_tabs.isTabVisible(i) for i in range(layout.bottom_tabs.count()))


def test_applying_a_workspace_profile_genuinely_hides_non_listed_tabs(layout):
    profile = WorkspaceManager(WorkspaceMode.RESEARCH).get_current_profile()
    assert "hpc" in profile["visible_panels"]
    assert "climate" not in profile["visible_panels"]  # real, not this mode's own profile

    layout.apply_workspace_profile(profile)

    visible = _visible_tab_keys(layout)
    assert "hpc" in visible
    assert "climate" not in visible


def test_applying_a_workspace_profile_shows_exactly_its_own_visible_panels(layout):
    profile = WorkspaceManager(WorkspaceMode.CLIMATE).get_current_profile()

    layout.apply_workspace_profile(profile)

    visible = _visible_tab_keys(layout)
    # "system" (climate profile has none, but confirm the mapping is real
    # elsewhere) - here just confirm exact real match to this profile's own list.
    assert visible == set(profile["visible_panels"])


def test_the_system_visible_panels_name_maps_to_the_real_system_console_panel(layout):
    """"system" is the one visible_panels name with no identically-named
    panel_manager key - same "System Config" -> "system_console" mapping
    _CATEGORY_LABEL_TO_PANEL_NAME already uses for sidebar routing."""
    profile = WorkspaceManager(WorkspaceMode.RESEARCH).get_current_profile()
    assert "system" in profile["visible_panels"]

    layout.apply_workspace_profile(profile)

    visible = _visible_tab_keys(layout)
    assert "system_console" in visible


def test_switching_between_two_profiles_re_applies_visibility_each_time(layout):
    research = WorkspaceManager(WorkspaceMode.RESEARCH).get_current_profile()
    climate = WorkspaceManager(WorkspaceMode.CLIMATE).get_current_profile()

    layout.apply_workspace_profile(research)
    assert "hpc" in _visible_tab_keys(layout)

    layout.apply_workspace_profile(climate)
    visible = _visible_tab_keys(layout)
    assert "hpc" not in visible
    assert "climate" in visible


def test_apply_workspace_profile_still_focuses_the_primary_panel_tab(layout):
    """The pre-existing, already-working half of this method must keep working."""
    profile = WorkspaceManager(WorkspaceMode.CLIMATE).get_current_profile()

    layout.apply_workspace_profile(profile)

    current_key = layout.panel_manager.list_panel_names()[layout.bottom_tabs.currentIndex()]
    assert current_key == "climate"
