"""
Atmospheric Complexity Framework (ACF)

4D Atmospheric Volume Data Representation Module (Phase 2)
(AtmosphericVolume representing Atmosphere(x, y, z, t) fields)
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class AtmosphericVolume:
    """
    Représentation 4D d'un champ volumétrique d'atmosphère terrestre Atmosphere(x,y,z,t).

    NOTE (correction): units used to default to "K" (Kelvin)
    regardless of variable_name - correct for the one case this
    class's own test happens to use ("temperature_4d"), but wrong for
    any other variable (humidity, pressure, wind speed, ...) not
    explicitly overriding it. Changed to an honest empty default,
    matching the convention used elsewhere in this codebase (e.g.
    visualization.layer.Layer) for a field with no single
    variable-independent correct value.
    """

    variable_name: str
    grid_dimensions: tuple = (360, 180, 50, 24)  # (lon, lat, levels, time)
    vertical_coordinate_type: str = "Pressure Level (hPa)"
    units: str = ""
    time_step_hours: int = 1
    has_microphysics: bool = True
    has_chemistry: bool = True
    data_shape: tuple = (360, 180, 50, 24)

    def get_volume_metadata(self) -> dict[str, Any]:
        """
        Retourne la synthèse des métadonnées du volume atmosphérique 4D.

        NOTE (correction): "status": "VOLUME_4D_LOADED" used to be
        unconditional - but this class holds no actual data array field
        at all (only dimension/unit/coordinate-type metadata), so
        nothing is ever genuinely "loaded" in the sense the status
        implies.
        """
        return {
            "variable_name": self.variable_name,
            "grid_dimensions": self.grid_dimensions,
            "vertical_coordinate": self.vertical_coordinate_type,
            "units": self.units,
            "total_grid_cells": self.grid_dimensions[0] * self.grid_dimensions[1] * self.grid_dimensions[2],
            "status": "METADATA_ONLY_NO_DATA_ARRAY_LOADED",
        }
