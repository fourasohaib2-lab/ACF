"""
Satellite Remote Sensing Ingestion Module (GOES, Meteosat, Himawari, Sentinel, MODIS, VIIRS)
"""

from typing import Any


class SatelliteIngestor:
    """Gestionnaire d'ingestion des radiances et produits satellitaires observés."""

    SUPPORTED_CONSTELLATIONS = [
        "NOAA GOES",
        "EUMETSAT Meteosat MTG",
        "JMA Himawari",
        "ESA Sentinel",
        "NASA MODIS/VIIRS",
    ]

    @classmethod
    def ingest_satellite_stream(cls, constellation: str = "NOAA GOES") -> dict[str, Any]:
        """
        NOTE (correction): constellation is genuinely echoed, but this
        used to also unconditionally claim 4 fixed "variables_ingested"
        and "STREAM_INGESTED_SUCCESS" with 0 real satellite data
        connection (no ground-station link, no L1/L2 product feed).
        Not fabricated.
        """
        return {
            "constellation": constellation,
            "variables_ingested": [],
            "ingestion_frequency": None,
            "status": "NOT_INGESTED_NO_SATELLITE_DATA_CONNECTION",
            "is_real_data": False,
        }
