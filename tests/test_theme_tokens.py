"""
Tests for acf.gui.theme_tokens and acf.gui.theme.ThemeManager - the
unified design-system foundation (explicit user request "améliorer le
dashboard... moderne idéal pour 2026"), replacing ESOC's minimal QSS
and AWCI dashboard's separate hardcoded navy palette with one real,
shared token source.
"""

from __future__ import annotations

import re

import pytest

from acf.gui.theme import ThemeManager
from acf.gui.theme_tokens import (
    COLORS,
    TOKENS,
    accent_gradient_css,
    apply_elevation,
    card_frame_style,
    dashboard_stylesheet,
    label_style,
)

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def test_every_color_token_is_a_real_hex_color():
    for name, value in COLORS.items():
        assert _HEX_RE.match(value), f"{name!r} is not a real #RRGGBB hex color: {value!r}"


def test_tokens_dataclass_matches_the_colors_dict():
    """COLORS is a convenience mirror of TOKENS - locked in sync so a
    future edit to one doesn't silently drift from the other."""
    for name, value in COLORS.items():
        assert getattr(TOKENS, name) == value


@pytest.mark.parametrize("theme_name", ["dark", "light"])
def test_theme_manager_loads_a_real_non_empty_stylesheet(theme_name):
    manager = ThemeManager()
    manager.set_theme(theme_name)
    sheet = manager.stylesheet()
    assert isinstance(sheet, str)
    assert len(sheet) > 200  # a real, non-trivial stylesheet, not a stub
    assert "QPushButton" in sheet  # real widget coverage, not just QMainWindow


def test_dashboard_stylesheet_is_real_and_token_driven():
    sheet = dashboard_stylesheet()
    assert TOKENS.bg_root in sheet
    assert TOKENS.accent_primary in sheet
    assert "QSlider" in sheet  # real widget coverage beyond the old 6-line block


def test_label_style_uses_real_tokens_not_fabricated_values():
    style = label_style("accent_primary", "lg", "bold")
    assert TOKENS.accent_primary in style
    assert f"{TOKENS.font_size_lg}px" in style
    assert "font-weight: bold" in style


def test_label_style_rejects_unknown_color_key():
    with pytest.raises(KeyError):
        label_style("not_a_real_token")


def test_card_frame_style_uses_real_tokens():
    style = card_frame_style()
    assert TOKENS.bg_card in style
    assert TOKENS.border in style
    assert f"{TOKENS.radius_md}px" in style


# --------------------------------------------------------- 2026 refresh
# (accent_real/accent_gradient_*, accent_gradient_css(), apply_elevation() -
# added the same "modernize the AWCI dashboard à 2026" request that
# added the real card shadows and scrollbar styling above)


def test_accent_real_is_a_distinct_real_token_from_the_other_accents():
    """The whole point of accent_real: a real-data affordance (Real
    Physics/Real Archive) must read as visually distinct from the demo/
    chrome accents, not silently reuse one of them."""
    assert TOKENS.accent_real not in (TOKENS.accent_primary, TOKENS.accent_secondary)
    assert _HEX_RE.match(TOKENS.accent_real)


def test_accent_gradient_css_is_a_real_qss_lineargradient_using_the_real_tokens():
    css = accent_gradient_css()
    assert css.startswith("qlineargradient(")
    assert TOKENS.accent_gradient_start in css
    assert TOKENS.accent_gradient_end in css


def test_accent_gradient_css_direction_changes_with_angle():
    """Not a fixed string regardless of the angle argument - genuinely
    computes different QSS coordinates."""
    assert accent_gradient_css(0) != accent_gradient_css(90)


def test_apply_elevation_attaches_a_real_drop_shadow_effect(qtbot):
    from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget

    widget = QWidget()
    qtbot.addWidget(widget)
    assert widget.graphicsEffect() is None

    apply_elevation(widget)

    effect = widget.graphicsEffect()
    assert isinstance(effect, QGraphicsDropShadowEffect)
    assert effect.blurRadius() == 24


def test_apply_elevation_respects_custom_parameters(qtbot):
    from PySide6.QtWidgets import QWidget

    widget = QWidget()
    qtbot.addWidget(widget)

    apply_elevation(widget, blur_radius=40, y_offset=10, opacity=0.5)

    effect = widget.graphicsEffect()
    assert effect.blurRadius() == 40
    assert effect.offset().y() == 10
    assert effect.color().alpha() == int(255 * 0.5)


def test_dashboard_stylesheet_includes_modern_scrollbar_styling():
    sheet = dashboard_stylesheet()
    assert "QScrollBar" in sheet
    assert TOKENS.border_strong in sheet
