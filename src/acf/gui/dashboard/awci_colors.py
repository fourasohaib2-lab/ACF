"""
AWCI Color Scale
================

Single shared 0-100 color scale used by every AWCI widget (map heatmaps,
cross-section, gauge legend, risk badges) so the dashboard reads
consistently, matching the reference mockup's blue -> green -> yellow ->
orange -> red -> magenta scale.
"""

from matplotlib.colors import LinearSegmentedColormap
from PySide6.QtGui import QColor

# (threshold, level name, RGB 0-1 for matplotlib / 0-255 for Qt)
LEVELS: list[tuple[float, str, tuple[int, int, int]]] = [
    (0, "Very Low", (33, 102, 172)),
    (20, "Low", (67, 160, 208)),
    (35, "Moderate", (120, 198, 121)),
    (50, "High", (255, 224, 60)),
    (65, "Very High", (255, 140, 0)),
    (85, "Extreme", (210, 30, 130)),
]

AWCI_CMAP = LinearSegmentedColormap.from_list(
    "awci_scale",
    # LinearSegmentedColormap.from_list requires the stop list to start at
    # x=0 and end at x=1 - LEVELS' thresholds only go up to 85, so the
    # top band's color is repeated at x=1.0 to close the scale.
    [(t / 100.0, tuple(c / 255.0 for c in rgb)) for t, _, rgb in LEVELS]
    + [(1.0, tuple(c / 255.0 for c in LEVELS[-1][2]))],
    N=256,
)


def level_for(score: float) -> str:
    """Return the AWCI level name (Very Low..Extreme) for a 0-100 score."""
    level = LEVELS[0][1]
    for threshold, name, _ in LEVELS:
        if score >= threshold:
            level = name
    return level


def qcolor_for(score: float) -> QColor:
    """Return the QColor for a 0-100 score (nearest lower band, no interpolation)."""
    color = LEVELS[0][2]
    for threshold, _, rgb in LEVELS:
        if score >= threshold:
            color = rgb
    return QColor(*color)


def risk_qcolor(level: str) -> QColor:
    """Map a textual risk level (Low/Moderate/High/Very High) to a QColor."""
    mapping = {
        "Very Low": QColor(67, 160, 208),
        "Low": QColor(120, 198, 121),
        "Moderate": QColor(255, 224, 60),
        "High": QColor(255, 140, 0),
        "Very High": QColor(210, 30, 130),
        "Extreme": QColor(210, 30, 130),
    }
    return mapping.get(level, QColor(150, 150, 150))
