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
        """
        Detect if the dataset belongs to ARPEGE NWP model.

        NOTE (correction): ARPEGE, AROME and ALADIN all share the same
        FA/LFA file format (see each adapter's supported_extensions) -
        a bare ".fa"/".lfa" extension does not distinguish between
        them at all. This used to also match on ".fa" alone, so any
        of the three adapters registered together would all return
        True for the same ambiguous filename (e.g. "run_20260801.fa"
        with no model name in it), making ModelDetector's result
        depend on arbitrary registry iteration order rather than the
        file's actual model. Only the model-name substring is a
        genuinely distinguishing signal here.
        """
        path_str = str(dataset).lower() if dataset else ""
        return "arpege" in path_str

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

    def read(self, filepath: str | Path) -> dict[str, Any]:
        """Model Adapter Protocol entry point (see base_model.py) - delegates to read_arpege_file(), same real logic, added so a caller doesn't need model-specific branching to read any adapter's file."""
        return self.read_arpege_file(filepath)

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
