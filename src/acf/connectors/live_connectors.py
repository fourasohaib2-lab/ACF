"""
Atmospheric Complexity Framework (ACF)

Operational Live Data Connectors Module (MISSION ACF-030)
(ECMWF Open Data/MARS, Copernicus CDS, NOAA NOMADS, DWD ICON, NASA EarthData, EUMETSAT Data Store)
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class DataConnectorInfo:
    """
    Description et statut d'un connecteur d'alimentation opérationnelle en temps réel.

    NOTE (correction): status/last_sync_timestamp used to default to a
    fixed "ONLINE" / "2026-07-30T15:00:00Z" for every one of the 6
    registered connectors below (none override these defaults) - so
    ECMWF/NOAA/DWD/EUMETSAT/NASA/Copernicus all claimed to be online
    and recently synced with 0 real network requests ever made to any
    of them. Not fabricated.
    """

    connector_id: str
    name: str
    provider: str
    endpoint_url: str
    supported_products: list[str]
    auth_required: bool
    status: str = "NOT_CONNECTED_NO_REAL_REQUEST_MADE"  # "ONLINE", "SYNCING", "OFFLINE" once really wired up
    last_sync_timestamp: str | None = None


LIVE_CONNECTORS_REGISTRY: dict[str, DataConnectorInfo] = {
    "ecmwf_opendata": DataConnectorInfo(
        connector_id="ecmwf_opendata",
        name="ECMWF Real-Time Open Data Connector",
        provider="ECMWF",
        endpoint_url="https://data.ecmwf.int/forecasts/",
        supported_products=["IFS 0.25° Global Forecasts", "AIFS AI Forecasts", "Wave Grids"],
        auth_required=False,
    ),
    "copernicus_cds": DataConnectorInfo(
        connector_id="copernicus_cds",
        name="Copernicus Climate Data Store (CDS API)",
        provider="C3S / ECMWF",
        endpoint_url="https://cds.climate.copernicus.eu/api/v2",
        supported_products=["ERA5 Reanalysis", "ERA5-Land", "Seasonal Forecasts C3S"],
        auth_required=True,
    ),
    "noaa_nomads": DataConnectorInfo(
        connector_id="noaa_nomads",
        name="NOAA NOMADS Real-Time GFS/HRRR Connector",
        provider="NOAA / NWS / NCEP",
        endpoint_url="https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl",
        supported_products=["GFS 0.25° Global", "HRRR 3km Severe Weather", "RAP 13km"],
        auth_required=False,
    ),
    "dwd_opendata": DataConnectorInfo(
        connector_id="dwd_opendata",
        name="DWD ICON Open Data Server",
        provider="Deutscher Wetterdienst (DWD)",
        endpoint_url="https://opendata.dwd.de/weather/nwp/icon/",
        supported_products=["ICON Global 13km", "ICON-EU 6.5km", "ICON-D2 2.2km"],
        auth_required=False,
    ),
    "eumetsat_datastore": DataConnectorInfo(
        connector_id="eumetsat_datastore",
        name="EUMETSAT Data Store & EUMETCast Real-Time Stream",
        provider="EUMETSAT",
        endpoint_url="https://api.eumetsat.int/data/browse/1.0.0/",
        supported_products=["MSG SEVIRI", "MTG FCI", "MetOp IASI", "ASCAT Winds"],
        auth_required=True,
    ),
    "nasa_earthdata": DataConnectorInfo(
        connector_id="nasa_earthdata",
        name="NASA EarthData & CMR API Connector",
        provider="NASA GMAO / DAAC",
        endpoint_url="https://cmr.earthdata.nasa.gov/search/",
        supported_products=["MERRA-2 Reanalysis", "MODIS", "VIIRS", "GPM Precipitation"],
        auth_required=True,
    ),
}


class LiveDataConnectorEngine:
    """Moteur de gestion et d'ingestion automatique des flux de données en temps réel."""

    def __init__(self):
        self.connectors = LIVE_CONNECTORS_REGISTRY

    def list_connectors(self) -> list[str]:
        return list(self.connectors.keys())

    def get_connector(self, connector_id: str) -> DataConnectorInfo | None:
        return self.connectors.get(connector_id.lower())

    def fetch_catalog_products(self, connector_id: str) -> list[str]:
        """Parcourt le catalogue des produits disponibles pour un connecteur."""
        conn = self.get_connector(connector_id)
        if conn:
            return conn.supported_products
        return []

    def sync_latest_dataset(self, connector_id: str, product_name: str) -> dict[str, Any]:
        """
        NOTE (correction — operationally dangerous): the docstring
        already said "Simule" (simulates), but the return value never
        disclosed that to a caller - it unconditionally claimed
        "status": "success" with a specific "100 MB" download,
        "checksum_verified": True, and a real-looking UUID dataset id,
        for ANY connector_id/product_name, with 0 real HTTP requests
        ever made to ECMWF/NOAA/DWD/EUMETSAT/NASA/Copernicus. An
        operational forecast pipeline trusting this could believe a
        real dataset had been downloaded and integrity-verified when
        nothing was ever fetched. Not fabricated.
        """
        conn = self.get_connector(connector_id)
        if not conn:
            return {"status": "error", "message": f"Unknown connector: {connector_id}"}

        return {
            "status": "NOT_SYNCED_NO_REAL_CONNECTION_ESTABLISHED",
            "connector": conn.name,
            "product": product_name,
            "downloaded_bytes": None,
            "checksum_verified": False,
            "ingested_dataset_id": None,
            "sync_time": None,
            "is_real_data": False,
        }
