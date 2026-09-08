"""
Surface In-situ Station Ingestion Module (METAR, SYNOP, AWS, TEMP Radiosondes)
"""

from typing import Any


class SurfaceStationIngestor:
    """Gestionnaire d'ingestion des stations météo sol et radiosondages."""

    @classmethod
    def ingest_synop_reports(cls) -> dict[str, Any]:
        """
        NOTE (correction): this used to unconditionally claim a fixed
        "4500" reports_count and "REPORTS_INGESTED" status with 0 real
        GTS/WIS connection (no network request, no file feed) - same
        pattern already fixed in this same directory's sibling
        satellite_ingestor.py (SatelliteIngestor.ingest_satellite_stream).
        Not fabricated.
        """
        return {
            "reports_count": None,
            "report_types": ["METAR", "SYNOP", "AWS"],
            "parameters": ["Temperature", "Pressure", "Humidity", "Wind Vector", "Precipitation"],
            "status": "NOT_INGESTED_NO_STATION_DATA_CONNECTION",
            "is_real_data": False,
        }
