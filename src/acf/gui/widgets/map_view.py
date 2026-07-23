"""
ACF Scientific Map View

Widget cartographique principal.
"""


from PySide6.QtWidgets import QWidget, QVBoxLayout


from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg
)


from acf.visualization.cartopy_renderer import (
    CartopyRenderer
)



class MapView(QWidget):
    """
    Carte scientifique interactive ACF.
    """

    def __init__(self):

        super().__init__()


        self.renderer = CartopyRenderer()

        self.canvas = None


        self.build()



    ##################################################


    def build(self):

        layout = QVBoxLayout(
            self
        )


        layout.setContentsMargins(
            0,0,0,0
        )


        figure, axis = (
            self.renderer.create_map()
        )


        self.canvas = FigureCanvasQTAgg(
            figure
        )


        layout.addWidget(
            self.canvas
        )



    ##################################################


    def clear(self):

        self.renderer.clear()



    ##################################################


    def refresh(self):

        if self.canvas:

            self.canvas.draw()



    ##################################################


    def status(self):

        return {

            "widget": "MapView",

            "renderer":
                self.renderer.status()

        }
