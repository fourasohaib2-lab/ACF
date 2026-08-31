"""
Atmospheric Complexity Framework (ACF)

Layer Metadata & LayerDefinition Struct Module
(LayerDefinition struct containing 14 attributes for 500+ Earth System layers)
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
    time: str = "LIVE"
    vertical_level: str = "Surface"
    quality_indicator: str = "HIGH_PRECISION"
    uncertainty: float = 0.0
    confidence_pct: float = 100.0
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
