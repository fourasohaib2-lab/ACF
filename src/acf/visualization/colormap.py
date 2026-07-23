"""
ACF Scientific Color Maps

Gestion des palettes météorologiques.
"""


class ColorMapManager:
    """
    Gestionnaire des palettes scientifiques ACF.
    """

    DEFAULT_MAPS = {

        "temperature": "turbo",

        "pressure": "coolwarm",

        "wind": "plasma",

        "humidity": "BrBG",

        "precipitation": "Blues",

        "clouds": "Greys",

        "terrain": "terrain",

    }


    ##################################################

    def __init__(self):

        self.maps = dict(
            self.DEFAULT_MAPS
        )


    ##################################################

    def register(
        self,
        name: str,
        cmap: str
    ):

        self.maps[name] = cmap



    ##################################################

    def get(
        self,
        name: str
    ):

        return self.maps.get(
            name,
            "viridis"
        )



    ##################################################

    def available(self):

        return list(
            self.maps.keys()
        )



    ##################################################

    def summary(self):

        return {

            "count": len(self.maps),

            "maps": self.maps

        }
