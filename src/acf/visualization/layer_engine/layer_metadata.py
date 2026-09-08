"""
Atmospheric Complexity Framework (ACF)

Layer Metadata & LayerDefinition Struct Module
(LayerDefinition struct containing 14 attributes for Earth System layers)

NOTE (correction — operationally dangerous): time/quality_indicator/
confidence_pct/uncertainty used to default to "LIVE"/"HIGH_PRECISION"/
100.0/0.0 - the best possible claim on every axis (perfectly live,
perfectly precise, perfectly confident, zero uncertainty) - for ANY
LayerDefinition not explicitly overriding them. None of the 7 entries
in layer_registry.py's LAYER_REGISTRY_DB override these fields, so
every one of them (temperature, vorticity, CAPE, SST, river discharge,
an AI forecast field) silently claimed to be live, fully precise,
100%-confident data with zero real data pipeline ever connected to any
of them (this class - see its own docstring - is a canonical
*specification* of layer types, not a live measurement). Fixed to
honest "not yet connected" defaults.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LayerDefinition:
    """Spécification canonique d'une couche scientifique d'observation ou de modèle dans ACF."""

    layer_id: str
    name: str
    domain: str
    cf_standard_name: str = ""
    grib2_code: str = ""
    netcdf_variable: str = ""
    unit: str = ""
    source: str = ""
    resolution: str = ""
    dimension: str = ""
    projection: str = "EPSG:4326"
    time: str = "NOT_LIVE_STATIC_CATALOG_ENTRY"
    vertical_level: str = "Surface"
    quality_indicator: str = "NOT_ASSESSED"
    uncertainty: float | None = None
    confidence_pct: float | None = None
    color_palette: str = "Viridis"
    opacity: float = 1.0
    visible: bool = True
    locked: bool = False
    dependencies: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convertit la définition de couche en dictionnaire sérialisable."""
        return {
            "layer_id": self.layer_id,
            "name": self.name,
            "domain": self.domain,
            "cf_standard_name": self.cf_standard_name,
            "grib2_code": self.grib2_code,
            "netcdf_variable": self.netcdf_variable,
            "unit": self.unit,
            "source": self.source,
            "resolution": self.resolution,
            "dimension": self.dimension,
            "projection": self.projection,
            "time": self.time,
            "vertical_level": self.vertical_level,
            "quality_indicator": self.quality_indicator,
            "uncertainty": self.uncertainty,
            "confidence_pct": self.confidence_pct,
            "color_palette": self.color_palette,
            "opacity": self.opacity,
            "visible": self.visible,
            "locked": self.locked,
            "dependencies": self.dependencies,
        }
