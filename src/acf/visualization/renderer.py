"""
ACF Scientific Renderer Engine

Transformation des données météo en couches graphiques.
"""


from acf.visualization.layer import Layer
from acf.visualization.colormap import ColorMapManager



class ScientificRenderer:
    """
    Moteur principal de rendu scientifique ACF.
    """

    def __init__(self):

        self.colormaps = ColorMapManager()

        self.layers = []


    ##################################################


    def create_layer(
        self,
        dataset,
        variable,
        name=None
    ):

        if name is None:
            name = variable


        layer = Layer(
            name=name,
            variable=variable
        )


        self.layers.append(layer)


        return layer



    ##################################################


    def get_colormap(
        self,
        variable
    ):

        variable = variable.lower()


        if "temp" in variable:

            return self.colormaps.get(
                "temperature"
            )


        if "wind" in variable:

            return self.colormaps.get(
                "wind"
            )


        if "pressure" in variable:

            return self.colormaps.get(
                "pressure"
            )


        if "humidity" in variable:

            return self.colormaps.get(
                "humidity"
            )


        return "viridis"



    ##################################################


    def render_info(
        self,
        layer
    ):

        return {

            "layer": layer.name,

            "variable": layer.variable,

            "colormap":
                self.get_colormap(
                    layer.variable
                ),

        }



    ##################################################


    def status(self):

        return {

            "layers":
                len(self.layers),

            "engine":
                "ACF Scientific Renderer"

        }
