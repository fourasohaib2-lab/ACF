"""ACF Map Canvas Subsystem.

Provides scientific QWidget map canvas, Cartopy projections, base map renderers, and layer managers.

NOTE (found, NOT changed — RÈGLE D'OR / single source of truth): this
package re-exports MapCanvas/LayerManager/MapProjection/MapRenderer from
the flat map_canvas.py/map_layers.py/map_projection.py/map_renderer.py
files - and these ARE the live ones (map_canvas.MapCanvas is genuinely
used by acf.gui.esoc.view_manager.ViewManager, ESOC's real central map).

Sitting alongside them, entirely unimported by anything in src/ (verified
by grep across the whole tree), is a second, more elaborately factored
map architecture spread across 5 subpackages: layers/ (LayerManager,
BaseLayer, Raster/Vector/Satellite/Radar/AWCI layer classes),
renderers/ (RendererManager-orchestrated BaseRenderer, Cartopy/Raster/
Vector/World/AWCI renderers), navigation/ (Pan/Zoom/Wheel/Mouse
controllers, CoordinateTracker), projections/ (ProjectionManager), and
rendering/ (RendererManager). Unlike this session's other X.py-vs-X/-
package findings (data/engine.py, model4d/operators.py,
model4d/interpolation.py, maps/canvas.py - all literal name collisions
where Python's own import resolution silently picks one), there is no
naming collision here forcing this outcome - both this flat system and
the subpackage system are independently importable. Nothing ever chose
to use the subpackage one: it is a complete, self-consistent, QObject-
based (signals for layerAdded/layerChanged/rendererAdded/etc.) alternate
design - not fabricated, not broken by a spot-check of its manager
classes - that was simply never wired into a real widget. Making it live
would mean building new integration glue (a host widget actually
connecting layers to renderers to navigation to real Qt mouse/wheel
events), not just giving an existing complete unit a window - a
different scope of work than this session's dashboard/menu-bar
wiring passes. Not deleted per project convention - flagged so nobody
mistakes it for a live alternative to the map_canvas.py system above.
"""

from acf.gui.map.map_canvas import MapCanvas
from acf.gui.map.map_layers import BaseMapLayer, LayerManager
from acf.gui.map.map_projection import MapProjection
from acf.gui.map.map_renderer import MapRenderer

__all__ = [
    "BaseMapLayer",
    "LayerManager",
    "MapCanvas",
    "MapProjection",
    "MapRenderer",
]
