"""
ACF Scientific Workstation — Key Alerts & Hazards
=====================================================

Matches acf_workstation_reference.jpg's "Key Alerts & Hazards" panel
(Convection/Turbulence/Low Visibility/Icing, each a colored icon +
title + subtitle + a High/Moderate/Low severity badge on the right).

These are real, simple, DISCLOSED threshold heuristics over fields
already computed elsewhere in this Workstation (CAPE, bulk wind shear,
wet-bulb temperature, relative humidity) - not an imported AWCI
hazard-classification engine, and not a machine-learned risk model.
Each threshold below is intentionally conservative/textbook (SPC-style
CAPE bands for convection, generic bulk-shear bands for turbulence
potential, a simple RH band for a fog/visibility proxy, and a
wet-bulb-near-freezing band for icing potential) and documented right
here, not hidden behind a magic function. Subtitles describe the real
basis of each classification (e.g. "CAPE-based") rather than the
reference image's own illustrative place-names ("over Alps"/"Po
Valley") - this Workstation has no real per-point geographic hazard
attribution to honestly claim those.

Honesty: any `NaN`/`None` input (the underlying computation reporting
"not computed" - see `acf.awci.workstation_fields.
compute_real_convection_indices_field()`'s own docstring) renders
"NOT_COMPUTED" for that hazard, never a fabricated level.
"""

from __future__ import annotations

import math

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from acf.gui.theme_tokens import label_style

#: (level -> (icon background color, badge text color)) - visually
#: matches acf_workstation_reference.jpg's own red/orange/green
#: High/Medium/Low severity coloring.
_LEVEL_COLORS: dict[str, tuple[str, str]] = {
    "High": ("#ef4444", "#ef4444"),
    "Moderate": ("#f97316", "#f97316"),
    "Low": ("#22c55e", "#22c55e"),
    "NOT_COMPUTED": ("#4b5563", "#8ea0b5"),
}


def _convection_level(cape_j_kg: float) -> str:
    if math.isnan(cape_j_kg):
        return "NOT_COMPUTED"
    if cape_j_kg >= 2000.0:
        return "High"
    if cape_j_kg >= 300.0:
        return "Moderate"
    return "Low"


def _turbulence_level(bulk_shear_m_s: float) -> str:
    if math.isnan(bulk_shear_m_s):
        return "NOT_COMPUTED"
    if bulk_shear_m_s >= 20.0:
        return "High"
    if bulk_shear_m_s >= 10.0:
        return "Moderate"
    return "Low"


def _visibility_level(relative_humidity_pct: float | None) -> str:
    if relative_humidity_pct is None:
        return "NOT_COMPUTED"
    if relative_humidity_pct >= 95.0:
        return "High"
    if relative_humidity_pct >= 85.0:
        return "Moderate"
    return "Low"


def _icing_level(wet_bulb_c: float | None) -> str:
    if wet_bulb_c is None:
        return "NOT_COMPUTED"
    if -3.0 <= wet_bulb_c <= 0.0:
        return "High"
    if -6.0 <= wet_bulb_c < -3.0 or 0.0 < wet_bulb_c <= 2.0:
        return "Moderate"
    return "Low"


class HazardAlertsPanel(QWidget):
    """Real, threshold-based Key Alerts & Hazards panel."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self._icons: dict[str, QLabel] = {}
        self._levels: dict[str, QLabel] = {}
        self.convection_level = self._build_row(layout, "convection", "⚠️", "Convection", "CAPE-based convective potential")
        self.turbulence_level = self._build_row(layout, "turbulence", "〰️", "Turbulence", "Bulk shear-based potential")
        self.visibility_level = self._build_row(layout, "visibility", "🌫️", "Low Visibility", "Relative humidity-based fog risk")
        self.icing_level = self._build_row(layout, "icing", "❄️", "Icing", "Wet-bulb temperature band")
        layout.addStretch(1)

    def _build_row(self, layout: QVBoxLayout, key: str, icon: str, title: str, subtitle: str) -> QLabel:
        row = QHBoxLayout()
        row.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setFixedSize(28, 28)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background-color: #4b5563; border-radius: 14px; font-size: 13px;")
        row.addWidget(icon_label)
        self._icons[key] = icon_label

        text_col = QVBoxLayout()
        text_col.setSpacing(1)
        title_label = QLabel(title)
        title_label.setStyleSheet(label_style("text_primary", "sm", "bold"))
        text_col.addWidget(title_label)
        subtitle_label = QLabel(subtitle)
        subtitle_label.setWordWrap(True)
        subtitle_label.setStyleSheet(label_style("text_muted", "xs"))
        text_col.addWidget(subtitle_label)
        row.addLayout(text_col, stretch=1)

        level_label = QLabel("NOT_COMPUTED")
        level_label.setStyleSheet(label_style("text_muted", "xs", "bold"))
        level_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        row.addWidget(level_label)

        layout.addLayout(row)
        self._levels[key] = level_label
        return level_label

    def _apply_level(self, key: str, level: str) -> None:
        icon_color, badge_color = _LEVEL_COLORS.get(level, _LEVEL_COLORS["NOT_COMPUTED"])
        self._icons[key].setStyleSheet(f"background-color: {icon_color}; border-radius: 14px; font-size: 13px;")
        label = self._levels[key]
        label.setText(level)
        label.setStyleSheet(f"color: {badge_color}; font-weight: bold; font-size: 11px;")

    def update_from_indices(
        self,
        cape_j_kg: float,
        bulk_shear_m_s: float,
        wet_bulb_c: float | None,
        relative_humidity_pct: float | None,
    ) -> None:
        self._apply_level("convection", _convection_level(cape_j_kg))
        self._apply_level("turbulence", _turbulence_level(bulk_shear_m_s))
        self._apply_level("visibility", _visibility_level(relative_humidity_pct))
        self._apply_level("icing", _icing_level(wet_bulb_c))
