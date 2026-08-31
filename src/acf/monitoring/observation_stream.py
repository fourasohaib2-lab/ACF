"""
Atmospheric Complexity Framework (ACF)

Global Observation Stream Engine Module (Phase 3)
(ObservationStreamEngine driving real-time ingestion from satellites, radars, WIGOS stations, ARGO buoys)
"""

from typing import Any

LIVE_SATELLITE_CONSTELLATIONS = [
    "GOES-16/17/18",
    "Meteosat MTG-I1",
    "Himawari-9",
    "Sentinel-1/2/3/6",
    "Suomi NPP / JPSS VIIRS",
    "Terra/Aqua MODIS",
    "EarthCARE",
    "SWOT",
    "SMAP/SMOS",
]

LIVE_RADAR_PRODUCTS = [
    "Reflectivity ZH",
    "Doppler Velocity VR",
    "Differential Reflectivity ZDR",
    "Correlation Coefficient RHOHV",
    "Dual-Pol QPE",
    "MESH Hail Index",
]


class ObservationStreamEngine:
    """
    Moteur de streaming et d'ingestion en temps réel des observations d'observation de la Terre.
    """

    @classmethod
    def get_stream_telemetry(cls) -> dict[str, Any]:
        """
        Retourne l'état des flux de streaming d'observation.

        NOTE (correction): LIVE_SATELLITE_CONSTELLATIONS and
        LIVE_RADAR_PRODUCTS are genuine static reference catalogs (the
        real set of platforms/products ACF is designed to support),
        but this used to also claim fabricated specific live
        throughput numbers ("4500 stations/sec", "3900 ARGO buoys",
        "1200 AMDAR reports/min") and "REALTIME_STREAMING_NOMINAL" -
        no real ingestion pipeline is connected here (0 parameters).
        Not fabricated.
        """
        return {
            "supported_satellites": LIVE_SATELLITE_CONSTELLATIONS,
            "supported_radar_products": LIVE_RADAR_PRODUCTS,
            "surface_stations_ingested_per_sec": None,
            "argo_buoys_active": None,
            "amdar_aircraft_reports_per_min": None,
            "stream_ingestion_status": "NOT_STREAMING_NO_INGESTION_PIPELINE_CONNECTED",
            "is_real_data": False,
        }
