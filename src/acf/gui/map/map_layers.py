"""Extensible Scientific Map Layer Manager for ACF MapCanvas with NWP & Data Ingestion Engine Support."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

import cartopy.crs as ccrs
import numpy as np

from acf.data.dataset import Dataset
from acf.gui.dashboard.awci_colors import AWCI_CMAP

logger = logging.getLogger("acf.gui.map.map_layers")


class BaseMapLayer(ABC):
    """Abstract base class for all scientific map layer overlays."""

    def __init__(self, name: str, zorder: int = 10, visible: bool = True) -> None:
        self.name = name
        self.zorder = zorder
        self.visible = visible
        self.custom_data: dict[str, Any] | None = None

    def set_data(self, lons: np.ndarray, lats: np.ndarray, values: np.ndarray) -> None:
        """Set real field data arrays."""
        self.custom_data = {"lons": lons, "lats": lats, "values": values}

    @abstractmethod
    def render(self, axes: Any, transform: ccrs.CRS) -> None:
        """Render scientific layer overlay on Matplotlib Cartopy GeoAxes."""


class SatelliteLayer(BaseMapLayer):
    """Satellite RGB/IR cloud & water vapor radiance overlay layer."""

    def __init__(self) -> None:
        super().__init__("Satellite RGB", zorder=12)

    def render(self, axes: Any, transform: ccrs.CRS) -> None:
        if self.custom_data is not None:
            lon_grid = self.custom_data["lons"]
            lat_grid = self.custom_data["lats"]
            data = self.custom_data["values"]
        else:
            lons = np.linspace(-180, 180, 100)
            lats = np.linspace(-90, 90, 50)
            lon_grid, lat_grid = np.meshgrid(lons, lats)
            data = np.sin(np.radians(lon_grid * 3)) * np.cos(np.radians(lat_grid * 2))
            data = np.where(data > 0.3, data, np.nan)

        axes.contourf(
            lon_grid,
            lat_grid,
            data,
            levels=8,
            cmap="Blues_r",
            alpha=0.45,
            zorder=self.zorder,
            transform=transform,
        )


class RadarLayer(BaseMapLayer):
    """Doppler Radar reflectivity mosaic overlay layer."""

    def __init__(self) -> None:
        super().__init__("Radar Mosaic", zorder=14)

    def render(self, axes: Any, transform: ccrs.CRS) -> None:
        if self.custom_data is not None:
            lon_grid = self.custom_data["lons"]
            lat_grid = self.custom_data["lats"]
            dbz = self.custom_data["values"]
        else:
            lons = np.linspace(-30, 40, 60)
            lats = np.linspace(25, 65, 40)
            lon_grid, lat_grid = np.meshgrid(lons, lats)
            dbz = 45 * np.exp(-((lon_grid - 5) ** 2 / 50 + (lat_grid - 36) ** 2 / 30)) + 35 * np.exp(
                -((lon_grid - 15) ** 2 / 40 + (lat_grid - 48) ** 2 / 20)
            )
            dbz = np.where(dbz > 15, dbz, np.nan)

        axes.contourf(
            lon_grid,
            lat_grid,
            dbz,
            levels=10,
            cmap="jet",
            alpha=0.6,
            zorder=self.zorder,
            transform=transform,
        )


class TemperatureLayer(BaseMapLayer):
    """2m Surface Air Temperature field overlay layer (WRF / ARPEGE / ICON / GRIB / NetCDF)."""

    def __init__(self) -> None:
        super().__init__("2m Temp", zorder=8)

    def render(self, axes: Any, transform: ccrs.CRS) -> None:
        if self.custom_data is not None:
            lon_grid = self.custom_data["lons"]
            lat_grid = self.custom_data["lats"]
            temp = self.custom_data["values"]
        else:
            lons = np.linspace(-180, 180, 90)
            lats = np.linspace(-90, 90, 45)
            lon_grid, lat_grid = np.meshgrid(lons, lats)
            temp = 30 * np.cos(np.radians(lat_grid)) - 10 + 5 * np.sin(np.radians(lon_grid * 2))

        cs = axes.contour(
            lon_grid,
            lat_grid,
            temp,
            levels=12,
            cmap="plasma",
            linewidths=0.7,
            alpha=0.7,
            zorder=self.zorder,
            transform=transform,
        )
        axes.clabel(cs, inline=True, fontsize=7, fmt="%1.0f°C")


class WindLayer(BaseMapLayer):
    """10m Wind Speed & Vector field overlay layer."""

    def __init__(self) -> None:
        super().__init__("Wind Vectors", zorder=15)

    def render(self, axes: Any, transform: ccrs.CRS) -> None:
        if self.custom_data is not None:
            lon_grid = self.custom_data["lons"]
            lat_grid = self.custom_data["lats"]
            u = self.custom_data.get("u", self.custom_data["values"])
            v = self.custom_data.get("v", self.custom_data["values"])
        else:
            lons = np.linspace(-180, 180, 24)
            lats = np.linspace(-80, 80, 12)
            lon_grid, lat_grid = np.meshgrid(lons, lats)
            u = 15 * np.sin(np.radians(lat_grid * 3)) + 10
            v = 5 * np.cos(np.radians(lon_grid * 2))

        axes.quiver(
            lon_grid,
            lat_grid,
            u,
            v,
            color="#FFD54F",
            scale=350,
            width=0.003,
            alpha=0.75,
            zorder=self.zorder,
            transform=transform,
        )


class PressureLayer(BaseMapLayer):
    """Mean Sea Level Pressure (MSLP) isobar overlay layer."""

    def __init__(self) -> None:
        super().__init__("MSLP", zorder=9)

    def render(self, axes: Any, transform: ccrs.CRS) -> None:
        if self.custom_data is not None:
            lon_grid = self.custom_data["lons"]
            lat_grid = self.custom_data["lats"]
            mslp = self.custom_data["values"]
        else:
            lons = np.linspace(-180, 180, 80)
            lats = np.linspace(-90, 90, 40)
            lon_grid, lat_grid = np.meshgrid(lons, lats)
            mslp = 1013.25 + 20 * np.cos(np.radians(lat_grid * 2)) * np.sin(np.radians(lon_grid))

        cs = axes.contour(
            lon_grid,
            lat_grid,
            mslp,
            levels=10,
            colors="#81D4FA",
            linewidths=0.8,
            linestyles="solid",
            alpha=0.8,
            zorder=self.zorder,
            transform=transform,
        )
        axes.clabel(cs, inline=True, fontsize=7, fmt="%1.0f")


class CloudLayer(BaseMapLayer):
    """Cloud Cover & Precipitable Water shading overlay layer."""

    def __init__(self) -> None:
        super().__init__("Cloud Cover & Precipitable Water", zorder=11)

    def render(self, axes: Any, transform: ccrs.CRS) -> None:
        if self.custom_data is not None:
            lon_grid = self.custom_data["lons"]
            lat_grid = self.custom_data["lats"]
            clouds = self.custom_data["values"]
        else:
            lons = np.linspace(-180, 180, 70)
            lats = np.linspace(-90, 90, 35)
            lon_grid, lat_grid = np.meshgrid(lons, lats)
            clouds = np.abs(np.sin(np.radians(lon_grid * 4)) * np.cos(np.radians(lat_grid * 3)))
            clouds = np.where(clouds > 0.4, clouds, np.nan)

        axes.contourf(
            lon_grid,
            lat_grid,
            clouds,
            levels=5,
            cmap="Greys",
            alpha=0.35,
            zorder=self.zorder,
            transform=transform,
        )


class AWCILayer(BaseMapLayer):
    """Real AWCI complexity heatmap overlay - explicit user request
    "ajoute la 4eme dimension au niveau d'affichage des cartes",
    closing a real gap found while planning this work: ESOC's central
    map (this canvas) had never shown any real AWCI/CAPE/CIN data at
    all, unlike the separate AWCI dashboard's own maps.

    Unlike every other layer in this file, there is deliberately NO
    synthetic fallback pattern here - render() draws nothing until
    set_data() has been fed a real
    acf.awci.spatial_field.compute_real_complexity_field() result (see
    acf.gui.map.map_canvas.MapCanvas.set_awci_field()). A fabricated
    AWCI heatmap from a made-up pattern would be exactly the kind of
    invented number this project's audits exist to remove - the other
    6 layers' synthetic defaults exist because they are illustrative
    demo overlays by design (their own docstrings say so); this one is
    not.
    """

    def __init__(self) -> None:
        super().__init__("AWCI Complexity", zorder=16)

    def render(self, axes: Any, transform: ccrs.CRS) -> None:
        if self.custom_data is None:
            return
        lon_grid = self.custom_data["lons"]
        lat_grid = self.custom_data["lats"]
        values = self.custom_data["values"]
        axes.contourf(
            lon_grid,
            lat_grid,
            values,
            levels=20,
            cmap=AWCI_CMAP,
            vmin=0,
            vmax=100,
            alpha=0.7,
            zorder=self.zorder,
            transform=transform,
        )


class LayerManager:
    """Manages active scientific layers and orchestrates rendering with real NWP data binding."""

    def __init__(self) -> None:
        self.available_layers: dict[str, BaseMapLayer] = {
            "Satellite RGB": SatelliteLayer(),
            "Radar Mosaic": RadarLayer(),
            "2m Temp": TemperatureLayer(),
            "Wind Vectors": WindLayer(),
            "MSLP": PressureLayer(),
            "Cloud Cover & Precipitable Water": CloudLayer(),
            "AWCI Complexity": AWCILayer(),
        }
        self.active_layer_names: list[str] = [
            "Satellite RGB",
            "Radar Mosaic",
            "2m Temp",
            "Wind Vectors",
            "MSLP",
            # AWCI Complexity is intentionally NOT in this default list -
            # unlike the layers above (all real, but a synthetic demo
            # pattern until real data is bound), it draws nothing at all
            # until MapCanvas.set_awci_field() feeds it a real field, so
            # there is no synthetic "always-on-by-default" state for it
            # to silently occupy.
        ]
        self.current_dataset: Dataset | None = None

    def bind_dataset(self, dataset: Dataset) -> None:
        """Connect canonical Dataset (GRIB/NetCDF/FA/WRF/ARPEGE/ICON) to map layers."""
        self.current_dataset = dataset
        # Ingest field variables into active layer instances if present
        if hasattr(dataset, "variables"):
            for var_name, var_data in dataset.variables.items():
                if "temp" in var_name.lower() or "t2m" in var_name.lower():
                    layer = self.available_layers.get("2m Temp")
                    if layer and isinstance(var_data, np.ndarray) and var_data.ndim == 2:
                        lons = np.linspace(-180, 180, var_data.shape[1])
                        lats = np.linspace(-90, 90, var_data.shape[0])
                        lon_g, lat_g = np.meshgrid(lons, lats)
                        layer.set_data(lon_g, lat_g, var_data)

    def set_active_layers(self, layer_names: list[str]) -> None:
        """Update list of active layers."""
        self.active_layer_names = list(layer_names)

    def get_active_layers(self) -> list[str]:
        """Return active layer names."""
        return list(self.active_layer_names)

    def render_layers(self, axes: Any, transform: ccrs.CRS | None = None) -> None:
        """Render all active scientific overlays onto the provided GeoAxes."""
        if transform is None:
            transform = ccrs.PlateCarree()

        for name in self.active_layer_names:
            layer = self.available_layers.get(name)
            if not layer:
                for key, l_obj in self.available_layers.items():
                    if key.lower() in name.lower() or name.lower() in key.lower():
                        layer = l_obj
                        break
            if layer and layer.visible:
                try:
                    layer.render(axes, transform=transform)
                except Exception:
                    # NOTE (correction): used to silently swallow ANY
                    # exception from a layer's render() (bare except
                    # Exception: pass, no logging) - a genuinely broken
                    # layer (bad data shape, a real matplotlib/cartopy
                    # error) would just silently vanish from the map
                    # with zero indication anything went wrong, the same
                    # "stop silently swallowing failures" bug class
                    # already fixed elsewhere in this codebase (see
                    # importers/factory.py, science/encyclopedia.py).
                    logger.exception("Failed to render map layer %r", name)
