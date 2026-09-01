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
    cccc: str  # Centre collecteur/origine GTS (e.g., "LFPW" Météo-France Paris-Toulouse)
    yygggg: str  # Jour et heure UTC (e.g., "301500")
    wigos_station_id: str | None
    topic_wis2: str


class WMOWISEngine:
    """Moteur d'ingestion et de décodage des métadonnées WMO WIS 2.0 et GTS."""

    @staticmethod
    def parse_gts_header(header_line: str) -> WISBulletinHeader:
        """
        Décode une ligne d'en-tête standard GTS/WIS WMO.

        NOTE (correction): wigos_station_id used to be synthesized as
        f"0-20000-0-{cccc}" for every header, formatted exactly like a
        real WIGOS identifier and asserted on as such by this file's
        test. This was wrong on two levels: (1) the WIGOS "20000"
        issuer namespace is specifically reserved for legacy 5-digit
        numeric WMO station numbers, not 4-letter GTS codes, so
        "0-20000-0-LFPW" is not a validly-formed WIGOS ID; (2) more
        fundamentally, cccc is the bulletin's *collecting/relay*
        center (e.g. "LFPW" = Météo-France's GTS relay) - a single GTS
        bulletin from one collecting center routinely carries
        observations from many different stations, none of which is
        "LFPW" itself, so no per-station identifier can be derived
        from the header line alone (the actual reporting station's ID
        is embedded further down in the bulletin body, which this
        function does not parse). Fix: wigos_station_id is now
        honestly None here; cccc (the real, correctly-decoded field)
        is unchanged.
        """
        parts = header_line.strip().split()
        t12 = parts[0] if len(parts) > 0 else "SAFR31"
        cccc = parts[1] if len(parts) > 1 else "LFPW"
        yygg = parts[2] if len(parts) > 2 else "301500"

        topic = f"origin/a/wis2/{cccc.lower()}/data/core/weather/surface/observation"

        return WISBulletinHeader(
            t1_t2_a1_a2_ii=t12,
            cccc=cccc,
            yygggg=yygg,
            wigos_station_id=None,
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
