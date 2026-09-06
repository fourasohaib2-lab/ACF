"""
Atmospheric Complexity Framework (ACF)

Map Rendering
=============

NOTE (Physics Guard, 2026-09-06 Tier C sweep): despite "used by
MapCanvas" below, `class MapCanvas(EventMixin, QWidget)` in
map_canvas.py does NOT mix this class in - verified by reading that
class's own base list. Real, substantial (175 lines), self-consistent
code, not fabricated - just never wired in, same disconnected-reserve
situation as this package's own __init__.py already documents for
layers/renderers/rendering/navigation/projections/. See that
docstring for the fuller pattern; this file and its siblings
map_export.py/map_status.py (same false "for MapCanvas" claim) are an
additional, smaller instance of it.

Rendering mixin - NOT currently used by MapCanvas.

Responsible for drawing every scientific layer.
"""


class RenderingMixin:
    ##################################################
    # Base Map
    ##################################################

    def render_base_map(self):

        if self.axes is None:
            return

        self.base_renderer.render(
            self.axes,
            coastlines=True,
            borders=True,
            gridlines=True,
            ocean=True,
            land=True,
            resolution="10m",
        )

        self._base_map_rendered = True

        self.refresh()

    ##################################################
    # Raster
    ##################################################

    def render_raster(
        self,
        data,
        **kwargs,
    ):

        if not self._base_map_rendered:
            self.render_base_map()

        self.raster_renderer.render(
            self.axes,
            data,
            **kwargs,
        )

        self.refresh()

    ##################################################
    # Vector
    ##################################################

    def render_vector(
        self,
        data,
        **kwargs,
    ):

        if not self._base_map_rendered:
            self.render_base_map()

        self.vector_renderer.render(
            self.axes,
            data,
            **kwargs,
        )

        self.refresh()

    ##################################################
    # AWCI
    ##################################################

    def render_awci(
        self,
        data,
        **kwargs,
    ):

        if not self._base_map_rendered:
            self.render_base_map()

        self.awci_renderer.render(
            self.axes,
            data,
            **kwargs,
        )

        self.refresh()

    ##################################################
    # Generic layer
    ##################################################

    def render_layer(
        self,
        layer,
    ):

        if layer is None:
            return

        if not layer.visible:
            return

        variable = layer.variable.lower()

        if variable in (
            "u",
            "v",
            "wind",
            "vector",
        ):
            self.render_vector(
                layer.dataset,
            )

        else:
            self.render_raster(
                layer.dataset,
            )

    ##################################################
    # Scene
    ##################################################

    def render_scene(self):

        if self.scene is None:
            return

        self.clear()

        self.render_base_map()

        for layer in self.scene.layers:
            self.render_layer(
                layer,
            )

    ##################################################
    # Refresh
    ##################################################

    def refresh(self):

        if self.canvas:
            self.canvas.draw_idle()

        self.mapChanged.emit()

    ##################################################
    # Clear
    ##################################################

    def clear(self):

        if self.axes is None:
            return

        self.axes.clear()

        self._base_map_rendered = False

        if self.canvas:
            self.canvas.draw_idle()
