"""
Atmospheric Complexity Framework (ACF)

ARPEGE NWP Model Ingestion Adapter (EPyGrAM Integration)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from acf.data.readers.epygram_reader import EPyGrAMReader
from acf.models.base_model import BaseWeatherModel


class ARPEGEIngestionAdapter(BaseWeatherModel):
    """
    Ingestion adapter for Météo-France ARPEGE global spectral model FA datasets.
    """

    name = "ARPEGE"
    supported_extensions = (".fa", ".lfa", ".grib2")

    def __init__(self, filepath: str | Path | None = None) -> None:
        self.filepath: Path | None = Path(filepath) if filepath else None
        self.reader = EPyGrAMReader()

    def detect(self, dataset: Any) -> bool:
        """Detect if the dataset belongs to ARPEGE NWP model."""
        path_str = str(dataset).lower() if dataset else ""
        return "arpege" in path_str or path_str.endswith(".fa")

    def variables(self) -> list[str]:
        """Return standard ARPEGE model variable keys."""
        return [
            "S105TEMPERATURE",
            "S105WIND.U.PHYS",
            "S105WIND.V.PHYS",
            "S105HUMI_RELAT",
            "SURFPRESSION",
            "SURFTEMPERATURE",
        ]

    def levels(self) -> list[int]:
        """Return vertical level numbers (105 hybrid levels)."""
        return list(range(1, 106))

    def projection(self) -> str:
        """Return ARPEGE grid projection description."""
        return "Stretched Rotated Spherical Harmonics / Gaussian Grid"

    def read_arpege_file(self, filepath: str | Path) -> dict[str, Any]:
        """Ingest ARPEGE operational output using EPyGrAM backend."""
        path = Path(filepath)
        with self.reader.open(path) as r:
            fields = r.list_fields()
            meta = r.metadata()
            geom = r.geometry()
            vlevels = r.vertical_levels()

            meta["model"] = "ARPEGE"
            meta["grid_type"] = "Stretched Gaussian"

            return {
                "model": "ARPEGE",
                "filepath": str(path),
                "format": meta.get("format", "FA"),
                "fields_count": len(fields),
                "fields": fields,
                "metadata": meta,
                "geometry": geom,
                "vertical_levels_count": len(vlevels),
            }
