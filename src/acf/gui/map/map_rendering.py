"""
Atmospheric Complexity Framework (ACF)

Map Rendering
=============

Rendering mixin used by MapCanvas.

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
