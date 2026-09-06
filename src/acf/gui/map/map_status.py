"""
Atmospheric Complexity Framework (ACF)

Map Status
==========

NOTE (Physics Guard, 2026-09-06 Tier C sweep): despite "for MapCanvas"
below, `class MapCanvas(EventMixin, QWidget)` in map_canvas.py does
NOT mix this class in - verified by reading that class's own base
list. Real code, not fabricated, just never wired in - see
map_rendering.py's own NOTE (same finding, fuller context) and this
package's __init__.py for the broader disconnected-reserve pattern.

Status and diagnostic mixin - NOT currently used by MapCanvas.
"""


class StatusMixin:
    ##################################################
    # Camera
    ##################################################

    def camera_status(self):

        return {
            "center": self.camera.center(),
            "zoom": self.camera.zoom_level,
            "extent": self.camera.extent,
        }

    ##################################################
    # Scene
    ##################################################

    def scene_status(self):

        return {
            "layers": len(self.scene.layers),
            "initialized": self.scene.initialized,
        }

    ##################################################
    # Projection
    ##################################################

    def projection_status(self):

        if hasattr(self, "projection_manager"):
            return self.projection_manager.status()

        return {}

    ##################################################
    # Renderers
    ##################################################

    def renderer_status(self):

        if hasattr(self, "renderer_manager"):
            return self.renderer_manager.status()

        return {}

    ##################################################
    # Canvas
    ##################################################

    def canvas_status(self):

        return {
            "figure": self.figure is not None,
            "axes": self.axes is not None,
            "canvas": self.canvas is not None,
            "base_map": getattr(
                self,
                "_base_map_rendered",
                False,
            ),
        }

    ##################################################
    # Global
    ##################################################

    def status(self):

        return {
            "camera": self.camera_status(),
            "scene": self.scene_status(),
            "projection": self.projection_status(),
            "renderers": self.renderer_status(),
            "canvas": self.canvas_status(),
        }
