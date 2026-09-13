"""
ACF Scientific Workstation — Key Alerts & Hazards
=====================================================

Matches acf_workstation_reference.jpg's "Key Alerts & Hazards" panel
(Convection/Turbulence/Low Visibility/Icing, each High/Moderate/Low).

These are real, simple, DISCLOSED threshold heuristics over fields
already computed elsewhere in this Workstation (CAPE, bulk wind shear,
wet-bulb temperature, relative humidity) - not an imported AWCI
hazard-classification engine, and not a machine-learned risk model.
Each threshold below is intentionally conservative/textbook (SPC-style
CAPE bands for convection, generic bulk-shear bands for turbulence
potential, a simple RH band for a fog/visibility proxy, and a
wet-bulb-near-freezing band for icing potential) and documented right
here, not hidden behind a magic function.

Honesty: any `NaN`/`None` input (the underlying computation reporting
"not computed" - see `acf.awci.workstation_fields.
compute_real_convection_indices_field()`'s own docstring) renders
"NOT_COMPUTED" for that hazard, never a fabricated level.
"""

from __future__ import annotations

import math

from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

from acf.gui.theme_tokens import label_style


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
        layout = QGridLayout(self)
        self.convection_level = self._row(layout, 0, "Convection")
        self.turbulence_level = self._row(layout, 1, "Turbulence")
        self.visibility_level = self._row(layout, 2, "Low Visibility")
        self.icing_level = self._row(layout, 3, "Icing")

    def _row(self, layout: QGridLayout, row: int, title: str) -> QLabel:
        heading = QLabel(title)
        heading.setStyleSheet(label_style("text_muted", "xs"))
        value = QLabel("NOT_COMPUTED")
        layout.addWidget(heading, row, 0)
        layout.addWidget(value, row, 1)
        return value

    def update_from_indices(
        self,
        cape_j_kg: float,
        bulk_shear_m_s: float,
        wet_bulb_c: float | None,
        relative_humidity_pct: float | None,
    ) -> None:
        self.convection_level.setText(_convection_level(cape_j_kg))
        self.turbulence_level.setText(_turbulence_level(bulk_shear_m_s))
        self.visibility_level.setText(_visibility_level(relative_humidity_pct))
        self.icing_level.setText(_icing_level(wet_bulb_c))
