"""
Atmospheric Complexity Framework (ACF)

World Renderer
==============

Professional base map renderer.
"""

import cartopy.feature as cfeature


class WorldRenderer:
    """
    Draws the professional world background.
    """

    def __init__(self):

        self.initialized = True

    ##################################################

    def render(self, axes):
        """
        Render the world base map.
        """

        if axes is None:
            return

        ##################################################
        # Background
        ##################################################

        axes.set_facecolor("#0d1b2a")

        ##################################################
        # Ocean
        ##################################################

        axes.add_feature(
            cfeature.OCEAN,
            facecolor="#143d59",
            zorder=0,
        )

        ##################################################
        # Land
        ##################################################

        axes.add_feature(
            cfeature.LAND,
            facecolor="#3b7a57",
            edgecolor="none",
            zorder=1,
        )

        ##################################################
        # Coastlines
        ##################################################

        axes.coastlines(
            resolution="110m",
            linewidth=0.8,
            color="white",
            zorder=5,
        )

        ##################################################
        # Borders
        ##################################################

        axes.add_feature(
            cfeature.BORDERS,
            linewidth=0.4,
            edgecolor="gray",
            zorder=4,
        )

        ##################################################
        # Lakes
        ##################################################

        axes.add_feature(
            cfeature.LAKES,
            facecolor="#1f6aa5",
            edgecolor="none",
            zorder=2,
        )

        ##################################################
        # Rivers
        ##################################################

        axes.add_feature(
            cfeature.RIVERS,
            linewidth=0.2,
            edgecolor="#6fb3d2",
            zorder=3,
        )

        ##################################################
        # Grid
        ##################################################

        grid = axes.gridlines(
            draw_labels=True,
            linewidth=0.3,
            color="gray",
            alpha=0.5,
            linestyle="--",
        )

        grid.top_labels = False
        grid.right_labels = False

    ##################################################

    def status(self):

        return {
            "initialized": self.initialized,
        }
