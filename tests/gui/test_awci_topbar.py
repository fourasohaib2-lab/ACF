"""
Tests for acf.gui.dashboard.awci_topbar.AWCITopBar - the real light
top bar added 2026-09-12 (docs/reference/awci_dashboard_reference.png,
explicit user request "je veux que le dashboard soit exactement comme
celui dans la photo... 100%... tous les boutons fonctionnelles").
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_topbar import AWCILogoMark, AWCITopBar
from acf.gui.theme_tokens import TOKENS


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


def test_topbar_paints_a_real_background_not_just_a_stylesheet_string(qapp):
    """Task 1 (2026-09-21) root-cause fix for Task 10 finding F3: a plain
    QWidget subclass never actually paints a stylesheet `background-color`
    unless WA_StyledBackground is set - without it the bar was visually
    transparent while its child labels assumed a dark background behind
    them (the "white text-boxes on a dark page" bug)."""
    topbar = AWCITopBar()
    assert topbar.testAttribute(Qt.WidgetAttribute.WA_StyledBackground) is True


def test_topbar_uses_the_real_dark_navy_theme_tokens_not_the_old_light_palette(qapp):
    """The reference image's top bar is dark navy with light text, not
    white - see docs/reference/awci_dashboard_reference.png. This also
    confirms the codebase's shared TOKENS are reused rather than a new
    one-off hex palette being invented."""
    assert AWCITopBar._BG == TOKENS.bg_root
    assert AWCITopBar._BORDER == TOKENS.border
    assert AWCITopBar._TEXT == TOKENS.text_primary
    assert AWCITopBar._TEXT_MUTED == TOKENS.text_muted
    # Sanity: these must actually be dark/light, not the old
    # white-bar/dark-text values (#ffffff / #2a3142).
    assert AWCITopBar._BG != "#ffffff"
    assert AWCITopBar._TEXT != "#2a3142"


def test_topbar_has_a_real_visible_logo_mark_before_the_title(qapp):
    topbar = AWCITopBar()
    assert isinstance(topbar.logo_mark, AWCILogoMark)
    assert topbar.logo_mark.isVisibleTo(topbar)
    assert topbar.logo_mark.width() > 0
    assert topbar.logo_mark.height() > 0


def test_logo_mark_paints_without_error_and_reports_a_sane_fixed_size(qapp):
    """Renders the real paintEvent (not a mock) to a pixmap to make sure
    the QPainter drawing code path actually runs end-to-end."""
    from PySide6.QtGui import QPixmap

    logo = AWCILogoMark(size=36)
    assert logo.size().width() == 36
    assert logo.size().height() == 36
    pixmap = QPixmap(logo.size())
    logo.render(pixmap)
    assert not pixmap.toImage().isNull()
