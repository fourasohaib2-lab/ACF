"""
Atmospheric Complexity Framework (ACF)

WMO Information System (WIS 2.0 / GTS / OSCAR / WIGOS) Metadata & Bulletin Engine
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class WISBulletinHeader:
    """En-tête de bulletin synoptique/aéronautique WMO GTS / WIS 2.0 (MQTT/HTTP API)."""

    t1_t2_a1_a2_ii: str  # e.g., "SAFR31" (METAR France), "SMFR01" (SYNOP)
    cccc: str  # Origine OMM (e.g., "LFPW" Météo-France Paris)
    yygggg: str  # Jour et heure UTC (e.g., "301500")
    wigos_station_id: str
    topic_wis2: str


class WMOWISEngine:
    """Moteur d'ingestion et de décodage des métadonnées WMO WIS 2.0 et GTS."""

    @staticmethod
    def parse_gts_header(header_line: str) -> WISBulletinHeader:
        """Décode une ligne d'en-tête standard GTS/WIS WMO."""
        parts = header_line.strip().split()
        t12 = parts[0] if len(parts) > 0 else "SAFR31"
        cccc = parts[1] if len(parts) > 1 else "LFPW"
        yygg = parts[2] if len(parts) > 2 else "301500"

        wigos_id = f"0-20000-0-{cccc}"
        topic = f"origin/a/wis2/{cccc.lower()}/data/core/weather/surface/observation"

        return WISBulletinHeader(
            t1_t2_a1_a2_ii=t12,
            cccc=cccc,
            yygggg=yygg,
            wigos_station_id=wigos_id,
            topic_wis2=topic,
        )

    @classmethod
    def get_station_oscar_metadata(cls, wigos_id: str) -> dict[str, Any]:
        """
        Récupère les métadonnées officielles WMO OSCAR/Surface pour une station.

        NOTE (correction): wigos_id was genuinely accepted as a
        parameter but completely ignored - this used to return the
        identical "PARIS-MONTSOURIS" station (fixed lat/lon/elevation)
        as "operating_status": "Operational" for ANY wigos_id passed
        in, including ones for stations nowhere near Paris. No real WMO
        OSCAR/Surface API is connected. Not fabricated.
        """
        return {
            "wigos_id": wigos_id,
            "station_name": None,
            "country": None,
            "latitude": None,
            "longitude": None,
            "elevation_m": None,
            "barometer_elevation_m": None,
            "operating_status": "NOT_AVAILABLE_NO_OSCAR_API_CONNECTED",
            "gcos_network": None,
            "is_real_data": False,
        }
