"""
Atmospheric Complexity Framework (ACF)

MAPS - Basemap Test Suite

This file was previously empty. The corresponding source module
(src/acf/maps/basemap.py) contains only a module docstring - no
classes, functions, or constants - so there is genuinely nothing to
test yet; this is a placeholder module, not a fabricated one. Kept as
a documented smoke test rather than a silent empty file.
"""

import acf.maps.basemap as basemap


def test_basemap_module_is_a_documented_placeholder():
    assert basemap.__doc__ is not None
    assert "Basemap" in basemap.__doc__
