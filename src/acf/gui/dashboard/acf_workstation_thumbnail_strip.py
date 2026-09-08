"""
ACF Scientific Workstation — variable thumbnail strip
==========================================================

Real, lightweight small-multiple preview row (Phase 37, 2026-09-05),
matching the reference mockup's own bottom "DYNAMICS LAB" thumbnail
strip (`docs/reference/acf_scientific_workstation_reference.jpg`,
Wind Speed / Shear / Divergence / Convergence thumbnails below the
main map).

Real data, deliberately lightweight rendering
--------------------------------------------------
Each thumbnail is a real, small `pcolormesh` of an already-computed
real field (no cartopy projection, no legend, no interactivity beyond
a click) - a genuine preview, not the full interactive
`AWCIMapPanel` this Workstation's own main map already is. Clicking a
thumbnail emits `variableSelected` with that variable's own real name
so the caller can switch its own main map to it - this widget never
decides what "selecting" a variable does, it only reports the real
click.
"""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from acf.gui.theme_tokens import COLORS, TOKENS, label_style


class _Thumbnail(QWidget):
    """One real, clickable small-multiple preview."""

    clicked = Signal()

    def __init__(self, name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.name = name
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        self.figure = plt.figure(figsize=(1.3, 0.95), facecolor=TOKENS.bg_root)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setFixedSize(96, 70)
        layout.addWidget(self.canvas)
        self.axis = self.figure.add_subplot(1, 1, 1)
        self.axis.set_xticks([])
        self.axis.set_yticks([])

        self.label_widget = QLabel(name)
        self.label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_widget.setWordWrap(True)
        self.label_widget.setStyleSheet(label_style("text_muted", "xs"))
        layout.addWidget(self.label_widget)

        self._has_field = False
        self._draw_empty()

    def _draw_empty(self) -> None:
        self.axis.clear()
        self.axis.set_facecolor(TOKENS.bg_card)
        self.axis.set_xticks([])
        self.axis.set_yticks([])
        self.canvas.draw_idle()

    def set_field(self, field: np.ndarray, cmap: str, vmin: float | None, vmax: float | None) -> None:
        self.axis.clear()
        self.axis.set_xticks([])
        self.axis.set_yticks([])
        self.axis.pcolormesh(field, cmap=cmap, vmin=vmin, vmax=vmax, shading="auto")
        self.figure.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)
        self.canvas.draw_idle()
        self._has_field = True

    def mousePressEvent(self, event: Any) -> None:  # noqa: N802 - Qt override signature
        self.clicked.emit()
        super().mousePressEvent(event)


class ACFVariableThumbnailStrip(QWidget):
    """Real row of `_Thumbnail`s, one per real variable name - see
    module docstring."""

    variableSelected = Signal(str)

    def __init__(self, variable_names: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._thumbnails: dict[str, _Thumbnail] = {}
        for name in variable_names:
            thumb = _Thumbnail(name)
            thumb.clicked.connect(lambda _checked=False, n=name: self.variableSelected.emit(n))
            layout.addWidget(thumb)
            self._thumbnails[name] = thumb
        layout.addStretch()

    def set_field(self, name: str, field: np.ndarray, cmap: str, vmin: float | None, vmax: float | None) -> None:
        if name not in self._thumbnails:
            raise ValueError(f"Unknown real thumbnail variable {name!r} - expected one of {list(self._thumbnails)}")
        self._thumbnails[name].set_field(field, cmap, vmin, vmax)

    def set_label(self, name: str, text: str) -> None:
        """Real, post-construction label override (added Phase 41,
        2026-09-05) - for a real value only known after the thumbnail
        was built (e.g. a real forecast-hour timestamp), never at
        `__init__` time. `name` still identifies the real thumbnail
        (`set_field`'s own key) - only its DISPLAYED text changes."""
        if name not in self._thumbnails:
            raise ValueError(f"Unknown real thumbnail variable {name!r} - expected one of {list(self._thumbnails)}")
        self._thumbnails[name].label_widget.setText(text)

    def set_selected(self, name: str | None) -> None:
        """Real, at-most-one visual highlight (added Phase 41,
        2026-09-05) - e.g. the Global Timeline's own currently-scrubbed
        frame. `None` clears every highlight."""
        for thumb_name, thumb in self._thumbnails.items():
            thumb.setStyleSheet(f"background-color: {COLORS['bg_surface_alt']};" if thumb_name == name else "")

    def status(self) -> dict[str, Any]:
        return {
            "variables": list(self._thumbnails.keys()),
            "rendered": [name for name, thumb in self._thumbnails.items() if thumb._has_field],
        }
