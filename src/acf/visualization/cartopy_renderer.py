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
    """



    def __init__(self):

        self.figure = None

        self.axis = None



    ##################################################


    def create_map(self):

        """
        Création d'une carte mondiale.
        """

        self.figure = plt.figure(
            figsize=(10,6)
        )


        self.axis = plt.axes(
            projection=ccrs.PlateCarree()
        )


        self.axis.set_global()



        # Terre

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


        self.axis.gridlines(
            draw_labels=True
        )


        return self.figure, self.axis



    ##################################################


    def clear(self):

        self.figure = None

        self.axis = None



    ##################################################


    def status(self):

        return {

            "figure": self.figure is not None,

            "axis": self.axis is not None,

            "engine": "Cartopy"

        }
