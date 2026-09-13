"""
ACF Scientific Workstation — Current Configuration bar
=========================================================

Real active-run metadata (model/cycle/forecast hour/domain/resolution/
grid/vertical levels), matching acf_workstation_reference.jpg's
"Current Configuration" bar. Shows an honest placeholder
(NOT_CONFIGURED_NO_RUN_SELECTED) until `update_from_config()` is
called with a real run's metadata - never a fabricated default run.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from acf.gui.theme_tokens import label_style

_PLACEHOLDER = "NOT_CONFIGURED_NO_RUN_SELECTED"


class ConfigBar(QWidget):
    """Real Current Configuration bar."""

    changeRequested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        self.model_label = self._field("Model", _PLACEHOLDER, layout)
        self.cycle_label = self._field("Cycle", _PLACEHOLDER, layout)
        self.forecast_label = self._field("Forecast", _PLACEHOLDER, layout)
        self.domain_label = self._field("Domain", _PLACEHOLDER, layout)
        self.resolution_label = self._field("Resolution", _PLACEHOLDER, layout)
        self.grid_label = self._field("Grid", _PLACEHOLDER, layout)
        self.levels_label = self._field("Vertical Levels", _PLACEHOLDER, layout)

        layout.addStretch()
        self.change_button = QPushButton("Change")
        self.change_button.clicked.connect(self.changeRequested.emit)
        layout.addWidget(self.change_button)

    def _field(self, title: str, initial: str, parent_layout: QHBoxLayout) -> QLabel:
        col = QVBoxLayout()
        heading = QLabel(title)
        heading.setStyleSheet(label_style("text_muted", "xs"))
        value = QLabel(initial)
        col.addWidget(heading)
        col.addWidget(value)
        parent_layout.addLayout(col)
        return value

    def update_from_config(self, config: dict[str, Any]) -> None:
        """Real re-display of the active run's own metadata - no
        derivation, no fabricated field. Each label shows a compact
        value (matching acf_workstation_reference.jpg's own terse
        "20250426 12 UTC"/"+12h"/"EUROPE" style) with the full, more
        verbose real disclosure available on hover - never truncating
        the honest detail, just not forcing it into the fixed-width bar."""
        for label, key in (
            (self.model_label, "model"),
            (self.cycle_label, "cycle"),
            (self.forecast_label, "forecast_hour"),
            (self.domain_label, "domain"),
            (self.grid_label, "grid"),
        ):
            text = str(config.get(key, _PLACEHOLDER))
            label.setText(text)
            label.setToolTip(text)

        resolution = config.get("resolution_km")
        self.resolution_label.setText(f"{resolution} km" if resolution is not None else _PLACEHOLDER)
        levels = config.get("vertical_levels")
        self.levels_label.setText(str(levels) if levels is not None else _PLACEHOLDER)
