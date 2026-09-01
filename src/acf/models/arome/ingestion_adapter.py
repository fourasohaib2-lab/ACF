"""
Atmospheric Complexity Framework (ACF)

AROME NWP Model Ingestion Adapter (EPyGrAM Integration)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from acf.data.readers.epygram_reader import EPyGrAMReader
from acf.models.base_model import BaseWeatherModel


class AROMEIngestionAdapter(BaseWeatherModel):
    """
    Ingestion adapter for Météo-France AROME 1.3km convective-scale FA/LFA datasets.
    """

    name = "AROME"
    supported_extensions = (".fa", ".lfa", ".grib2")

    def __init__(self, filepath: str | Path | None = None) -> None:
        self.filepath: Path | None = Path(filepath) if filepath else None
        self.reader = EPyGrAMReader()

    def detect(self, dataset: Any) -> bool:
        """
        Detect if the dataset belongs to AROME NWP model.

        NOTE (correction): ARPEGE, AROME and ALADIN all share the same
        FA/LFA file format (see each adapter's supported_extensions) -
        a bare ".fa"/".lfa" extension does not distinguish between
        them at all. This used to also match on that extension alone,
        so any of the three adapters registered together would all
        return True for the same ambiguous filename (e.g.
        "run_20260801.fa" with no model name in it), making
        ModelDetector's result depend on arbitrary registry iteration
        order rather than the file's actual model. Only the
        model-name substring is a genuinely distinguishing signal here.
        """
        path_str = str(dataset).lower() if dataset else ""
        return "arome" in path_str

    def variables(self) -> list[str]:
        """Return standard AROME model variable keys."""
        return [
            "S090TEMPERATURE",
            "S090WIND.U.PHYS",
            "S090WIND.V.PHYS",
            "S090HUMI_RELAT",
            "S090GRAUPEL",
            "SURFPRESSION",
            "SURFTEMPERATURE",
            "SURFPREC.EAU.CON",
        ]

    def levels(self) -> list[int]:
        """Return vertical level numbers (90 hybrid levels)."""
        return list(range(1, 91))

    def projection(self) -> str:
        """Return AROME grid projection description."""
        return "Lambert-93 / Conformal Projection (1.3km resolution)"

    def read_arome_file(self, filepath: str | Path) -> dict[str, Any]:
        """Ingest AROME operational output using EPyGrAM backend."""
        path = Path(filepath)
        with self.reader.open(path) as r:
            fields = r.list_fields()
            meta = r.metadata()
            geom = r.geometry()
            vlevels = r.vertical_levels()

            meta["model"] = "AROME"
            meta["resolution_km"] = 1.3
            geom["projection"] = "Lambert-93"
            geom["resolution_x_meters"] = 1300.0

            return {
                "model": "AROME",
                "filepath": str(path),
                "format": meta.get("format", "FA"),
                "fields_count": len(fields),
                "fields": fields,
                "metadata": meta,
                "geometry": geom,
                "vertical_levels_count": len(vlevels),
            }
