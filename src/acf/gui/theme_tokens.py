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


@dataclass(frozen=True)
class _Tokens:
    """Design tokens for the dark theme (ACF's only theme today with a
    fully modern treatment - `light.qss` gets the same shape mirrored
    to a light ground, see resources/themes/light.qss)."""

    # Surfaces (darkest to lightest)
    bg_root: str = "#0b1220"
    bg_surface: str = "#121a2b"
    bg_surface_alt: str = "#182238"
    bg_card: str = "#16213e"
    border: str = "#263450"
    border_strong: str = "#34445f"

    # Text
    text_primary: str = "#e8edf5"
    text_secondary: str = "#9fb0c9"
    text_muted: str = "#6b7a94"

    # Accents
    accent_primary: str = "#4fc3f7"
    accent_primary_hover: str = "#7ad4ff"
    accent_secondary: str = "#7c4dff"
    success: str = "#4caf82"
    warning: str = "#ffb74d"
    danger: str = "#ff5f6d"

    # Geometry
    radius_sm: int = 4
    radius_md: int = 8
    radius_lg: int = 14
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
    "success": TOKENS.success,
    "warning": TOKENS.warning,
    "danger": TOKENS.danger,
}


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


def dashboard_stylesheet() -> str:
    """Full Qt stylesheet for a top-level dashboard widget (used by
    AWCIDashboard._apply_theme()) - real, token-driven replacement for
    the previous 6-line hardcoded `QWidget { background-color: #0d1b2a; ... }`
    block. Modernized with real QSS-achievable depth: rounded corners
    and hover/pressed states on buttons and sliders, consistent borders
    instead of none, all from the same tokens ESOC's own QSS files use."""
    t = TOKENS
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
        }}
    """


def card_frame_style() -> str:
    """QFrame background for AWCI panel cards (map/radar/chart containers) -
    replaces ad hoc per-panel `border: none;`/no-background frames with
    a real card look (rounded corners, subtle border) shared everywhere."""
    t = TOKENS
    return f"QFrame {{ background-color: {t.bg_card}; border: 1px solid {t.border}; border-radius: {t.radius_md}px; }}"
