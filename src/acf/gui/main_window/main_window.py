"""Atmospheric Complexity Framework (ACF) Main Window.

Professional ACF Main Window (Backward-compatible ESOC subclass wrapper).
"""

from typing import Optional, Any
from acf.gui.esoc.esoc_window import ESOCWindow
from acf.gui.layer_panel.layer_panel import LayerPanel
from acf.gui.map.map_canvas import MapCanvas
from acf.gui.main_window.property_panel import PropertyPanel


class MainWindow(ESOCWindow):
    """Legacy MainWindow subclass wrapping ESOCWindow for complete backward compatibility."""

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Atmospheric Complexity Framework — Unified ESOC")

        # Backward compatibility widget attributes
        self.layer_panel = LayerPanel()
        self.map_canvas = MapCanvas()
        self.property_panel = PropertyPanel()

        try:
            self.map_canvas.draw_world()
        except Exception:
            pass
