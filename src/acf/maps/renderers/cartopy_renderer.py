"""
Cartopy Renderer
================

Renderer cartographique principal de l'Atmospheric Complexity Framework.
"""

import cartopy.crs as ccrs
import cartopy.feature as cfeature


class CartopyRenderer:
    """Renderer basé sur Cartopy."""

    def __init__(self, canvas):
        self.canvas = canvas

    # ==========================================================
    # Carte complète
    # ==========================================================

    def draw_world(self):
        """Dessine une carte du monde complète."""

        self.canvas.figure.clear()

        ax = self.canvas.figure.add_subplot(
            111,
            projection=ccrs.PlateCarree(),
        )

        ax.set_global()

        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS)

        ax.gridlines(draw_labels=True)

        ax.set_title("Atmospheric Complexity Framework")

        self.canvas.axes = ax

        self.canvas.draw()

    # ==========================================================
    # Couches individuelles
    # ==========================================================

    def draw_coastlines(self):
        """Dessine les côtes."""

        self.canvas.axes.coastlines()

        self.canvas.draw()

    def draw_borders(self):
        """Dessine les frontières."""

        self.canvas.axes.add_feature(cfeature.BORDERS)

        self.canvas.draw()

    def draw_land(self):
        """Dessine les terres."""

        self.canvas.axes.add_feature(cfeature.LAND)

        self.canvas.draw()

    def draw_ocean(self):
        """Dessine les océans."""

        self.canvas.axes.add_feature(cfeature.OCEAN)

        self.canvas.draw()

    def draw_gridlines(self):
        """Dessine la grille."""

        self.canvas.axes.gridlines(draw_labels=True)

        self.canvas.draw()

    # ==========================================================
    # Gestion du canvas
    # ==========================================================

    def clear(self):
        """Réinitialise la carte."""

        self.canvas.figure.clear()

        self.canvas.axes = self.canvas.figure.add_subplot(
            111,
            projection=ccrs.PlateCarree(),
        )

        self.canvas.draw()

    def refresh(self):
        """Rafraîchit l'affichage."""

        self.canvas.draw()

    # ==========================================================
    # Informations
    # ==========================================================

    def projection(self):
        """Retourne la projection actuelle."""

        return self.canvas.axes.projection

    def __repr__(self):
        return "CartopyRenderer()"
