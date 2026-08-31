"""Map projection manager supporting dynamic Cartopy projections (ACF Map Canvas)."""

from typing import Any

import cartopy.crs as ccrs


class MapProjection:
    """Manages dynamic Cartopy projection instantiation and resolution."""

    # Map standard names & UI view modes to Cartopy CRS factories
    PROJECTION_REGISTRY: dict[str, Any] = {
        # Standard projection names
        "platecarree": ccrs.PlateCarree,
        "equirectangular": ccrs.PlateCarree,
        "mercator": ccrs.Mercator,
        "robinson": ccrs.Robinson,
        "orthographic": ccrs.Orthographic,
        "lambertconformal": ccrs.LambertConformal,
        "northpolarstereo": ccrs.NorthPolarStereo,
        "southpolarstereo": ccrs.SouthPolarStereo,
        # ESOC UI Combo View Mode Mapping
        "2d mercator map": ccrs.Mercator,
        "3d photorealistic sphere": ccrs.Orthographic,
        "global interactive globe": ccrs.Orthographic,
        "orthographic projection": ccrs.Orthographic,
        "lambert conformal conic": ccrs.LambertConformal,
        "polar north stereographic": ccrs.NorthPolarStereo,
        "polar south stereographic": ccrs.SouthPolarStereo,
    }

    def __init__(self, default_name: str = "2D Mercator Map") -> None:
        self.current_name = default_name
        self.current_crs = self.get_projection(default_name)

    @classmethod
    def get_projection(cls, name: str) -> ccrs.CRS:
        """Resolve a string projection name or view mode to a Cartopy CRS instance."""
        key = name.strip().lower()
        crs_cls = cls.PROJECTION_REGISTRY.get(key, ccrs.PlateCarree)
        try:
            return crs_cls()
        except Exception:
            return ccrs.PlateCarree()

    def set_projection(self, name: str) -> ccrs.CRS:
        """Update active projection name and return new CRS instance."""
        self.current_name = name
        self.current_crs = self.get_projection(name)
        return self.current_crs

    @classmethod
    def list_supported_projections(cls) -> list[str]:
        """Return list of supported projection names."""
        return [
            "Mercator",
            "Robinson",
            "Orthographic",
            "Lambert Conformal",
            "Polar North",
            "Polar South",
            "PlateCarree",
        ]
