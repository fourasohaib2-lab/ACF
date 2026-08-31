"""
Atmospheric Complexity Framework (ACF)

ALADIN NWP Model Ingestion Adapter (EPyGrAM Integration)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from acf.data.readers.epygram_reader import EPyGrAMReader
from acf.models.base_model import BaseWeatherModel


class ALADINIngestionAdapter(BaseWeatherModel):
    """
    Ingestion adapter for ALADIN 7.5km regional NWP model FA datasets.
    """

    name = "ALADIN"
    supported_extensions = (".fa", ".lfa", ".grib2")

    def __init__(self, filepath: str | Path | None = None) -> None:
        self.filepath: Path | None = Path(filepath) if filepath else None
        self.reader = EPyGrAMReader()

    def detect(self, dataset: Any) -> bool:
        """Detect if the dataset belongs to ALADIN NWP model."""
        path_str = str(dataset).lower() if dataset else ""
        return "aladin" in path_str or path_str.endswith(".fa")

    def variables(self) -> list[str]:
        """Return standard ALADIN model variable keys."""
        return [
            "S070TEMPERATURE",
            "S070WIND.U.PHYS",
            "S070WIND.V.PHYS",
            "S070HUMI_RELAT",
            "SURFPRESSION",
            "SURFTEMPERATURE",
            "SURFPREC.EAU.CON",
            "SURFPREC.EAU.GEC",
        ]

    def levels(self) -> list[int]:
        """Return vertical level numbers (70 hybrid levels)."""
        return list(range(1, 71))

    def projection(self) -> str:
        """Return ALADIN grid projection description."""
        return "Lambert Conformal / ALADIN Domain (7.5km resolution)"

    def read_aladin_file(self, filepath: str | Path) -> dict[str, Any]:
        """Ingest ALADIN operational output using EPyGrAM backend."""
        path = Path(filepath)
        with self.reader.open(path) as r:
            fields = r.list_fields()
            meta = r.metadata()
            geom = r.geometry()
            vlevels = r.vertical_levels()

            meta["model"] = "ALADIN"
            meta["resolution_km"] = 7.5
            geom["projection"] = "Lambert Conformal"
            geom["resolution_x_meters"] = 7500.0

            return {
                "model": "ALADIN",
                "filepath": str(path),
                "format": meta.get("format", "FA"),
                "fields_count": len(fields),
                "fields": fields,
                "metadata": meta,
                "geometry": geom,
                "vertical_levels_count": len(vlevels),
            }
