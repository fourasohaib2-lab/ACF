"""Scientific QWidget-based MapCanvas using Cartopy and Matplotlib Qt Backend (ACF Map Canvas).

NOTE (found while auditing docs/architecture/duplicate_components.md's
"Canvas carte" row, NOT changed — RÈGLE D'OR / single source of truth):
this is the real `MapCanvas` embedded in ESOC's live window
(`acf.gui.esoc.view_manager.ViewManager` and
`acf.gui.main_window.main_window.MainWindow` both import it directly).
`acf.maps.canvas.map_canvas.MapCanvas` is a second, genuinely-both-live
implementation - it IS a `FigureCanvasQTAgg` (a matplotlib canvas you
call `.draw()`/`.figure` on directly), where this class instead
composes one as a child widget - with its own real consumers
(`acf.maps`'s own public API, `acf.visualization`'s lazy re-export
table). See that module's own NOTE for the full comparison and why
this pass does not unilaterally merge them.
"""

from typing import Any

import matplotlib
from PySide6.QtWidgets import QVBoxLayout, QWidget

matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from acf.data.dataset import Dataset
from acf.gui.map.map_layers import LayerManager
from acf.gui.map.map_projection import MapProjection
from acf.gui.map.map_renderer import MapRenderer


class _LabelProxy:
    """Proxy object maintaining backward compatibility with self.map_canvas.label.setText()."""

    def __init__(self, parent_canvas: "MapCanvas") -> None:
        self._canvas = parent_canvas

    def setText(self, text: str) -> None:
        self._canvas.set_title(text)


class MapCanvas(QWidget):
    """QWidget embedding a Matplotlib Cartopy GeoAxes figure for scientific Earth visualization."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # 1. State & Managers
        self.projection_manager = MapProjection("2D Mercator Map")
        self.renderer = MapRenderer()
        self.layer_manager = LayerManager()

        self.title_text: str = "GLOBAL EARTH INTERACTIVE MAP"

        # Compatibility proxy for ViewManager.map_canvas.label.setText()
        self.label = _LabelProxy(self)

        # 2. Matplotlib Figure & High DPI Setup
        self.figure = plt.figure(figsize=(12, 8), dpi=100, facecolor="#0b1220")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #0b1220;")

        self.axes: Any | None = None

        # 3. Layout Setup
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        # 4. Initial Render
        self.rebuild_axes()
        self.draw_map()

    def rebuild_axes(self) -> None:
        """Re-create subplot axes with current Cartopy CRS projection."""
        self.figure.clear()

        # Add subplot with active Cartopy projection
        current_crs = self.projection_manager.current_crs
        self.axes = self.figure.add_subplot(111, projection=current_crs)
        self.axes.set_facecolor("#0b1220")

    def draw_map(self) -> None:
        """Render base map and active scientific layers on GeoAxes."""
        if self.axes is None:
            return

        self.axes.clear()

        # Draw oceans, continents, coastlines, borders, lat/lon grid, and layers
        self.renderer.render(
            axes=self.axes,
            projection=self.projection_manager.current_crs,
            layer_manager=self.layer_manager,
            title=self.title_text,
        )

        if self.canvas is not None:
            try:
                self.canvas.draw_idle()
            except RuntimeError:
                pass

    def draw_world(self) -> None:
        """Draw professional world base map and scientific layers (ACF-MAP-004 API)."""
        self.draw_map()

    def set_projection(self, name: str) -> None:
        """Update map projection and re-render."""
        self.projection_manager.set_projection(name)
        self.rebuild_axes()
        self.draw_map()

    def set_title(self, title: str) -> None:
        """Update map title and trigger redraw."""
        self.title_text = title
        if self.axes is not None:
            self.axes.set_title(title, fontsize=10, color="#7ad4ff", weight="bold", pad=6)
            if self.canvas is not None:
                try:
                    self.canvas.draw_idle()
                except RuntimeError:
                    pass

    def set_active_layers(self, layers: list[str]) -> None:
        """Update active scientific layer catalog and re-render overlays."""
        self.layer_manager.set_active_layers(layers)
        self.draw_map()

    def load_dataset(self, dataset: Dataset) -> None:
        """Connect canonical NWP Dataset (WRF/ARPEGE/ICON/GRIB/NetCDF) to map layers (ACF-MAP-005)."""
        self.layer_manager.bind_dataset(dataset)
        self.draw_map()

    def refresh(self) -> None:
        """Refresh canvas drawing."""
        if self.canvas is not None:
            try:
                self.canvas.draw_idle()
            except RuntimeError:
                pass

    def clear(self) -> None:
        """Clear map axes."""
        if self.axes is not None:
            self.axes.clear()
            self.refresh()

    def resizeEvent(self, event: Any) -> None:
        """Handle widget resize event gracefully."""
        super().resizeEvent(event)
        self.refresh()

    def closeEvent(self, event: Any) -> None:
        """Clean up Matplotlib resources upon widget closure."""
        if self.figure is not None:
            plt.close(self.figure)
        super().closeEvent(event)
