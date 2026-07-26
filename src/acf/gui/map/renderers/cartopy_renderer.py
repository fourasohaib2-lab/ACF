"""Cartopy Renderer - Base map rendering with Cartopy."""

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from typing import Any, Optional

from .base_renderer import BaseRenderer


class CartopyRenderer(BaseRenderer):
    """Renders base map features using Cartopy."""

    def __init__(self):
        super().__init__(name="CartopyRenderer")
        self.projection = ccrs.PlateCarree()

    def render(self, ax: Any, data: Optional[Any] = None, **kwargs) -> Any:
        """Render base map features."""
        # Coastlines
        if kwargs.get('coastlines', True):
            ax.coastlines(
                resolution=kwargs.get('resolution', '10m'),
                color=kwargs.get('coastline_color', 'black'),
                linewidth=kwargs.get('coastline_width', 0.5)
            )

        # Borders
        if kwargs.get('borders', True):
            ax.add_feature(
                cfeature.BORDERS,
                linestyle=kwargs.get('border_style', ':'),
                edgecolor=kwargs.get('border_color', 'gray'),
                linewidth=kwargs.get('border_width', 0.5),
                alpha=self.opacity
            )

        # Lakes
        if kwargs.get('lakes', True):
            ax.add_feature(
                cfeature.LAKES,
                edgecolor=kwargs.get('lake_edge', 'blue'),
                facecolor=kwargs.get('lake_face', 'lightblue'),
                alpha=self.opacity * 0.5
            )

        # Gridlines
        if kwargs.get('gridlines', True):
            gl = ax.gridlines(
                draw_labels=kwargs.get('grid_labels', True),
                color=kwargs.get('grid_color', 'gray'),
                alpha=kwargs.get('grid_alpha', 0.3),
                linestyle=kwargs.get('grid_style', '--'),
                linewidth=kwargs.get('grid_width', 0.5)
            )
            gl.top_labels = False
            gl.right_labels = False

        # Ocean
        if kwargs.get('ocean', False):
            ax.add_feature(
                cfeature.OCEAN,
                color=kwargs.get('ocean_color', 'lightblue'),
                alpha=self.opacity * 0.3
            )

        # Land
        if kwargs.get('land', False):
            ax.add_feature(
                cfeature.LAND,
                color=kwargs.get('land_color', 'lightgreen'),
                alpha=self.opacity * 0.2
            )

    def clear(self) -> None:
        """Clear rendered features."""
        pass
