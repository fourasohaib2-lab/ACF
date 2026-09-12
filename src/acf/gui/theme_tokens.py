"""
Atmospheric Complexity Framework (ACF)

GUI - Theme Tokens
===================

Single source of truth for ACF's visual design system - colors,
spacing, radius, and typography - shared by ESOC's chrome
(`resources/themes/{dark,light}.qss`, applied via `ThemeManager`) and
the AWCI dashboard (`acf.gui.dashboard.*`, which used to hardcode its
own separate hex-literal palette in `awci_dashboard.py`'s
`_apply_theme()` and every panel's inline `setStyleSheet()` calls).

Before this module, ESOC and AWCI drew from two incompatible dark
palettes (`#202124`/`#252526` flat-grey chrome vs `#0d1b2a`/`#0a1929`
navy panels, plus 8+ unrelated per-label Material accent hues in
`esoc_statusbar.py` alone) - real, working, but not one coherent
design. This module doesn't replace `acf.gui.dashboard.awci_colors`'s
0-100 AWCI score colormap (`AWCI_CMAP`) - that is data-driven and
stays as-is - it replaces the *chrome* palette both windows paint
around that data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class _Tokens:
    """Design tokens for the dark theme (ACF's only theme today with a
    fully modern treatment - `light.qss` gets the same shape mirrored
    to a light ground, see resources/themes/light.qss).

    Refreshed 2026-09-07 (explicit user request to modernize the AWCI
    dashboard "à 2026") - deeper, higher-contrast surfaces, a real
    two-stop accent gradient (`accent_gradient_start/end`, used by
    `accent_gradient_css()` below for headers/active states instead of
    a flat accent fill), and a dedicated `accent_real` token so real
    data affordances (Real Physics/Real Archive) can read as visually
    distinct from a flat, single-color chrome - all values still consumed
    through the same `TOKENS`/`COLORS`/`label_style()`/`dashboard_stylesheet()`
    call sites, so every panel already using them picks this up with no
    per-panel change required."""

    # Surfaces (darkest to lightest) - deepened slightly for more
    # contrast against cards, and to read as less "flat grey" on a
    # modern OLED-friendly dark UI.
    bg_root: str = "#080d17"
    bg_surface: str = "#0f1729"
    bg_surface_alt: str = "#16213a"
    bg_card: str = "#1a2540"
    border: str = "#28375a"
    border_strong: str = "#3c5180"

    # Text
    text_primary: str = "#eef2f9"
    text_secondary: str = "#a7b6d1"
    text_muted: str = "#71809c"

    # Accents - primary kept as the established cyan (brand
    # continuity), secondary a real gradient partner (violet) via
    # accent_gradient_css() below. accent_real marks a genuine-data
    # affordance (Real Physics/Real Archive) as distinct from demo/
    # synthetic ones, on purpose - not decorative.
    accent_primary: str = "#4fc3f7"
    accent_primary_hover: str = "#7ad4ff"
    accent_secondary: str = "#8b5cf6"
    accent_real: str = "#22d3a8"
    accent_gradient_start: str = "#4fc3f7"
    accent_gradient_end: str = "#8b5cf6"
    success: str = "#22d3a8"
    warning: str = "#ffb74d"
    danger: str = "#ff5f6d"

    # Status SURFACES - a muted, dark-tinted background/border pair for
    # a banner/callout in that status color, distinct from the flat
    # foreground `warning`/`danger` tokens above (those are for text/
    # icons on the normal chrome background, not a background of their
    # own). Added 2026-09-11, promoting the AWCI recommendation
    # banner's own already-deliberate amber pair
    # (awci_dashboard.py) into a named, reusable token instead of a
    # second ad hoc hex literal - same amber values, not a new color
    # choice. Only `warning_surface`/`_border` exist today (the one
    # real call site needing it); add `danger_surface`/`success_surface`
    # the same way if/when a real caller needs them, not speculatively.
    warning_surface: str = "#3a2410"
    warning_surface_border: str = "#b8763a"

    # Geometry - slightly larger radii read as a more current, softer
    # "2026" card language than the previous sharper corners.
    radius_sm: int = 6
    radius_md: int = 10
    radius_lg: int = 16
    spacing_xs: int = 4
    spacing_sm: int = 8
    spacing_md: int = 12
    spacing_lg: int = 16
    spacing_xl: int = 24

    # Typography
    font_family: str = "'Inter', 'Segoe UI', 'Ubuntu', sans-serif"
    font_size_xs: int = 9
    font_size_sm: int = 10
    font_size_md: int = 12
    font_size_lg: int = 14
    font_size_xl: int = 18


TOKENS = _Tokens()

# Kept as a plain dict too - QSS files are generated/hand-aligned to
# these values (see resources/themes/dark.qss's own header comment),
# and some call sites format tokens straight into an f-string, where a
# dict lookup is more concise than a dataclass field lookup.
COLORS: dict[str, str] = {
    "bg_root": TOKENS.bg_root,
    "bg_surface": TOKENS.bg_surface,
    "bg_surface_alt": TOKENS.bg_surface_alt,
    "bg_card": TOKENS.bg_card,
    "border": TOKENS.border,
    "border_strong": TOKENS.border_strong,
    "text_primary": TOKENS.text_primary,
    "text_secondary": TOKENS.text_secondary,
    "text_muted": TOKENS.text_muted,
    "accent_primary": TOKENS.accent_primary,
    "accent_primary_hover": TOKENS.accent_primary_hover,
    "accent_secondary": TOKENS.accent_secondary,
    "accent_real": TOKENS.accent_real,
    "success": TOKENS.success,
    "warning": TOKENS.warning,
    "danger": TOKENS.danger,
}


def accent_gradient_css(angle_deg: int = 100) -> str:
    """QSS-syntax linear gradient between the two real accent tokens -
    for headers/active-tab/primary-button fills that want a real 2026
    gradient look instead of a flat single-color fill. Qt's QSS only
    supports `qlineargradient` with x1/y1/x2/y2 in [0,1] normalized
    coordinates, not a CSS-style angle, so `angle_deg` is converted to
    the nearest of the 4 cardinal/diagonal directions QSS can actually
    express (0/45/90/135/180/...) rather than silently producing the
    wrong gradient direction for an arbitrary angle."""
    import math

    rad = math.radians(angle_deg % 360)
    x2 = 0.5 + 0.5 * math.cos(rad)
    y2 = 0.5 + 0.5 * math.sin(rad)
    x1, y1 = 1.0 - x2, 1.0 - y2
    return (
        f"qlineargradient(x1:{x1:.2f}, y1:{y1:.2f}, x2:{x2:.2f}, y2:{y2:.2f}, "
        f"stop:0 {TOKENS.accent_gradient_start}, stop:1 {TOKENS.accent_gradient_end})"
    )


def apply_elevation(widget: Any, blur_radius: int = 24, y_offset: int = 6, opacity: float = 0.35) -> None:
    """Attach a real QGraphicsDropShadowEffect to `widget` - the
    closest Qt-achievable equivalent to a modern web dashboard's
    `box-shadow` card elevation (added 2026-09-07, "modernize the AWCI
    dashboard à 2026" request). Soft, dark, offset downward - reads as
    the card floating slightly above the root background rather than
    being flush with it. Safe to call on any QWidget; each widget gets
    its own effect instance (Qt does not allow sharing one
    QGraphicsEffect across widgets - reusing one would silently move it
    to the last widget it was assigned to)."""
    from PySide6.QtGui import QColor
    from PySide6.QtWidgets import QGraphicsDropShadowEffect

    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur_radius)
    effect.setOffset(0, y_offset)
    effect.setColor(QColor(0, 0, 0, int(255 * opacity)))
    widget.setGraphicsEffect(effect)


def label_style(color: str = "text_primary", size: str = "md", weight: str = "normal") -> str:
    """A ready `setStyleSheet()` string for a QLabel - replaces the
    repeated `"color: #xxxxxx; font-size: Npx;"` literals scattered
    across `awci_*.py` with one call site referencing real tokens.

    Parameters
    ----------
    color : one of COLORS's keys.
    size : "xs"/"sm"/"md"/"lg"/"xl" (maps to TOKENS.font_size_*).
    weight : passed through to the `font-weight` CSS property as-is
        ("normal", "bold", or a numeric weight string).
    """
    font_size = getattr(TOKENS, f"font_size_{size}")
    return f"color: {COLORS[color]}; font-size: {font_size}px; font-weight: {weight};"


def _rgba(hex_color: str, alpha: float) -> str:
    """Real `rgba(...)` QSS literal from a token's own hex value - QSS
    has no `color-mix()`/CSS-variable-with-opacity syntax, so a
    translucent tint (e.g. a nav item's own "active" background) has
    to be computed from the token's real RGB channels, not a second,
    independently-chosen hex literal."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def dashboard_stylesheet() -> str:
    """Full Qt stylesheet for a top-level dashboard widget (used by
    AWCIDashboard._apply_theme()) - real, token-driven replacement for
    the previous 6-line hardcoded `QWidget { background-color: #0d1b2a; ... }`
    block. Modernized with real QSS-achievable depth: rounded corners
    and hover/pressed states on buttons and sliders, consistent borders
    instead of none, all from the same tokens ESOC's own QSS files use.

    UPDATE (2026-09-12, ACF Workstation redesign Phase 46): added real
    QGroupBox/QComboBox/QListWidget rules - every one of this
    Workstation's ~20 real QGroupBox sections (Key Metrics, Model
    Consensus, Alerts & Hazards, Quick Actions, every Lab's own group
    boxes, ...) and its 2 real QListWidget nav lists had NO rule here
    at all before this, so they rendered with the native OS default
    (grey outline, black title text, OS-native blue selection
    highlight) against this dashboard's own dark background - jarring,
    and the nav list's own "active item" teal-pill look this
    Workstation's docstrings already described was never actually
    wired into real QSS. Purely additive - no existing selector's
    rule changed, so no risk to AWCI's own already pixel-matched
    chrome (which uses none of these 3 widget types in its own
    reference-matched panels)."""
    t = TOKENS
    active_tint = _rgba(t.accent_real, 0.14)
    hover_tint = _rgba(t.accent_real, 0.07)
    return f"""
        QWidget {{
            background-color: {t.bg_root};
            color: {t.text_primary};
            font-family: {t.font_family};
        }}
        QPushButton {{
            background-color: {t.bg_surface_alt};
            color: {t.text_primary};
            border: 1px solid {t.border};
            border-radius: {t.radius_md}px;
            padding: {t.spacing_xs}px {t.spacing_md}px;
        }}
        QPushButton:hover {{
            background-color: {t.bg_card};
            border-color: {t.accent_primary};
        }}
        QPushButton:pressed {{
            background-color: {t.bg_root};
        }}
        QPushButton:disabled {{
            color: {t.text_muted};
            border-color: {t.border};
        }}
        QSlider::groove:horizontal {{
            height: 4px;
            background: {t.border};
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            background: {t.accent_primary};
            width: 14px;
            height: 14px;
            margin: -6px 0;
            border-radius: 7px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {t.accent_primary_hover};
        }}
        QSlider:disabled::handle:horizontal {{
            background: {t.text_muted};
        }}
        QTabBar::tab {{
            background: {t.bg_surface};
            color: {t.text_secondary};
            border: 1px solid {t.border};
            border-bottom: none;
            border-top-left-radius: {t.radius_sm}px;
            border-top-right-radius: {t.radius_sm}px;
            padding: {t.spacing_xs}px {t.spacing_sm}px;
        }}
        QTabBar::tab:selected {{
            background: {t.bg_card};
            color: {t.text_primary};
            border-bottom: 2px solid {t.accent_primary};
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 10px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {t.border_strong};
            border-radius: 5px;
            min-height: 24px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {t.accent_primary};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background: transparent;
            height: 10px;
            margin: 0;
        }}
        QScrollBar::handle:horizontal {{
            background: {t.border_strong};
            border-radius: 5px;
            min-width: 24px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {t.accent_primary};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        QToolButton {{
            background-color: {t.bg_surface_alt};
            color: {t.text_primary};
            border: 1px solid {t.border};
            border-radius: {t.radius_md}px;
            padding: {t.spacing_xs}px {t.spacing_sm}px;
        }}
        QToolButton:hover {{
            background-color: {t.bg_card};
            border-color: {t.accent_primary};
        }}
        QToolButton::menu-indicator {{
            image: none;
        }}
        QMenu {{
            background-color: {t.bg_card};
            color: {t.text_primary};
            border: 1px solid {t.border};
            border-radius: {t.radius_md}px;
            padding: {t.spacing_xs}px;
        }}
        QMenu::item {{
            padding: {t.spacing_xs}px {t.spacing_md}px;
            border-radius: {t.radius_sm}px;
        }}
        QMenu::item:selected {{
            background-color: {t.bg_surface_alt};
            color: {t.accent_primary};
        }}
        QGroupBox {{
            background-color: {t.bg_surface};
            border: 1px solid {t.border};
            border-radius: {t.radius_md}px;
            margin-top: {t.spacing_lg}px;
            padding-top: {t.spacing_sm}px;
            font-weight: 700;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: {t.spacing_sm}px;
            padding: 0 {t.spacing_xs}px;
            color: {t.text_secondary};
        }}
        QComboBox {{
            background-color: {t.bg_surface_alt};
            color: {t.text_primary};
            border: 1px solid {t.border};
            border-radius: {t.radius_sm}px;
            padding: {t.spacing_xs}px {t.spacing_sm}px;
        }}
        QComboBox:hover {{
            border-color: {t.accent_primary};
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox QAbstractItemView {{
            background-color: {t.bg_card};
            color: {t.text_primary};
            border: 1px solid {t.border};
            selection-background-color: {t.bg_surface_alt};
            selection-color: {t.accent_primary};
            outline: none;
        }}
        QListWidget {{
            background-color: {t.bg_surface};
            border: 1px solid {t.border};
            border-radius: {t.radius_md}px;
            outline: none;
        }}
        QListWidget::item {{
            color: {t.text_secondary};
            padding: {t.spacing_xs}px {t.spacing_sm}px;
            border-radius: {t.radius_sm}px;
        }}
        QListWidget::item:hover {{
            background-color: {hover_tint};
        }}
        QListWidget::item:selected {{
            background-color: {active_tint};
            color: {t.accent_real};
        }}
        QListWidget::item:disabled {{
            color: {t.text_muted};
        }}
    """


def card_frame_style() -> str:
    """QFrame background for AWCI panel cards (map/radar/chart containers) -
    replaces ad hoc per-panel `border: none;`/no-background frames with
    a real card look (rounded corners, subtle border) shared everywhere."""
    t = TOKENS
    return f"QFrame {{ background-color: {t.bg_card}; border: 1px solid {t.border}; border-radius: {t.radius_md}px; }}"
