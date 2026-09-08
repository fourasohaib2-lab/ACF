"""
Atmospheric Complexity Framework (ACF)

Vector Layer
============

Scientific vector layer.
"""

from .base_layer import BaseLayer


class VectorLayer(BaseLayer):
    """
    Wind / Current / Streamlines layer.
    """

    def __init__(
        self,
        name="Vector",
        data=None,
    ):

        super().__init__(name)

        self.data = data

        self.style = {
            "color": "white",
            "scale": 50,
            "width": 0.002,
            "alpha": 1.0,
        }

    ##################################################

    def render(
        self,
        renderer,
        axes,
    ):
        """
        Render the vector layer.
        """

        if not self.visible:
            return

        if renderer is None:
            return

        if self.data is None:
            return

        renderer.render(
            axes,
            self.data,
            **self.style,
        )

    ##################################################

    def status(self):

        status = super().status()

        status.update(
            {
                "type": "vector",
                "has_data": self.data is not None,
            }
        )

        return status
