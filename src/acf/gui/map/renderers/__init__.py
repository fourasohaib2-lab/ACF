"""ACF Map Renderers.

NOTE (found, NOT changed — RÈGLE D'OR / single source of truth): every
class exported here (including this CartopyRenderer - a third, distinct
class from both acf.maps.renderers.cartopy_renderer.CartopyRenderer and
its acf.visualization.cartopy_renderer compatibility shim) is unused by
anything in src/ - see acf/gui/map/__init__.py's own NOTE for the full
explanation (this is part of a complete, correct, but never-integrated
alternate map architecture superseded in practice by the flat
map_canvas.py/map_layers.py/map_projection.py/map_renderer.py files that
ESOC actually uses).
"""

from .awci_renderer import AWCIRenderer
from .base_renderer import BaseRenderer
from .cartopy_renderer import CartopyRenderer
from .raster_renderer import RasterRenderer
from .vector_renderer import VectorRenderer

__all__ = [
    "AWCIRenderer",
    "BaseRenderer",
    "CartopyRenderer",
    "RasterRenderer",
    "VectorRenderer",
]
