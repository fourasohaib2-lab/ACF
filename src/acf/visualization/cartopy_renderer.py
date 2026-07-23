"""
ACF Cartopy Renderer

Moteur cartographique scientifique.
"""

import matplotlib.pyplot as plt

import cartopy.crs as ccrs
import cartopy.feature as cfeature



class CartopyRenderer:
    """
    Renderer basé sur Cartopy.

    Responsable de :
    - création de cartes
    - affichage des couches météo
    - rendu scientifique
    """


    def __init__(self):

        self.figure = None
        self.axis = None
        self.layers = []



    ##################################################
    # Création carte
    ##################################################

    def create_map(self):
        """
        Création d'une carte mondiale.
        """

        self.figure = plt.figure(
            figsize=(10, 6)
        )


        self.axis = plt.axes(
            projection=ccrs.PlateCarree()
        )


        self.axis.set_global()


        # Fond terrestre

        self.axis.add_feature(
            cfeature.LAND
        )


        # Océans

        self.axis.add_feature(
            cfeature.OCEAN
        )


        # Frontières

        self.axis.add_feature(
            cfeature.BORDERS
        )


        # Côtes

        self.axis.add_feature(
            cfeature.COASTLINE
        )


        # Grille

        self.axis.gridlines(
            draw_labels=True
        )


        return (
            self.figure,
            self.axis
        )



    ##################################################
    # Ajout champ scientifique
    ##################################################

    def add_field(
        self,
        longitude,
        latitude,
        data,
        colormap="viridis",
        levels=20,
    ):
        """
        Ajoute un champ météo.

        Exemple :
        température
        pression
        humidité
        """

        if self.axis is None:

            raise RuntimeError(
                "Map not initialized"
            )


        layer = self.axis.contourf(
            longitude,
            latitude,
            data,
            levels=levels,
            cmap=colormap,
            transform=ccrs.PlateCarree()
        )


        self.layers.append(
            layer
        )


        return layer



    ##################################################
    # Nettoyage
    ##################################################

    def clear(self):

        self.figure = None
        self.axis = None
        self.layers = []



    ##################################################
    # Rafraîchir
    ##################################################

    def refresh(self):

        if self.figure:

            self.figure.canvas.draw()



    ##################################################
    # Information
    ##################################################

    def status(self):

        return {

            "figure":
                self.figure is not None,

            "axis":
                self.axis is not None,

            "layers":
                len(self.layers),

            "engine":
                "Cartopy"

        }
