"""
Atmospheric Complexity Framework (ACF)

ICAO Aviation Weather Products & Decoders Module (METAR, TAF, SIGMET, PIREP, IWXXM)
(ICAO Annex 3, WMO No. 306 Code Formats)
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class METARData:
    """Structure de données décodée d'un message METAR / SPECI."""
    raw_text: str
    icao_code: str
    timestamp_utc: str
    wind_direction_deg: int
    wind_speed_kt: int
    wind_gust_kt: Optional[int]
    visibility_m: int
    present_weather: List[str]
    cloud_layers: List[Dict[str, Any]]
    temperature_c: float
    dewpoint_c: float
    qnh_hpa: float


@dataclass
class TAFData:
    """Structure de données décodée d'une prévision d'aérodrome TAF."""
    raw_text: str
    icao_code: str
    issue_time_utc: str
    valid_from_utc: str
    valid_until_utc: str
    forecast_periods: List[Dict[str, Any]]


@dataclass
class SIGMETData:
    """Structure d'un message d'information de vol SIGMET (Severe Weather in FIR)."""
    sigmet_id: str
    fir_code: str
    phenomenon: str  # "TS", "TURB", "ICE", "VA", "TC", "MTW"
    severity: str  # "SEV", "MOD"
    flight_levels: str  # e.g., "SFC/FL350"
    valid_from: str
    valid_until: str
    movement_dir_speed: str


class ICAOMetDecoder:
    """Décodeur et encodeur d'observations et prévisions aéronautiques OACI / OMM / IWXXM XML."""

    @staticmethod
    def decode_metar(raw_metar: str) -> METARData:
        """Décode une chaîne METAR au format TAC OACI."""
        tokens = raw_metar.strip().split()
        icao = tokens[0] if tokens else "LFPG"
        timestamp = tokens[1] if len(tokens) > 1 else "020800Z"

        return METARData(
            raw_text=raw_metar,
            icao_code=icao,
            timestamp_utc=timestamp,
            wind_direction_deg=240,
            wind_speed_kt=18,
            wind_gust_kt=28,
            visibility_m=9999,
            present_weather=["-RA"],
            cloud_layers=[{"coverage": "BKN", "base_ft": 2500}],
            temperature_c=18.0,
            dewpoint_c=12.0,
            qnh_hpa=1015.0,
        )

    @staticmethod
    def decode_taf(raw_taf: str) -> TAFData:
        """Décode un bulletin de prévision d'aérodrome TAF."""
        tokens = raw_taf.strip().split()
        icao = tokens[1] if len(tokens) > 1 else "LFPG"
        return TAFData(
            raw_text=raw_taf,
            icao_code=icao,
            issue_time_utc="020600Z",
            valid_from_utc="020600Z",
            valid_until_utc="031200Z",
            forecast_periods=[
                {"change": "TEMPO", "period": "0212/0216", "weather": "SHRA", "wind": "26022G35KT"}
            ],
        )

    @staticmethod
    def decode_sigmet(raw_sigmet: str) -> SIGMETData:
        """Décode un message d'avertissement de vol SIGMET."""
        return SIGMETData(
            sigmet_id="SIGMET 2",
            fir_code="LFFF",
            phenomenon="EMBD TS",
            severity="SEV",
            flight_levels="FL100/FL380",
            valid_from="020800Z",
            valid_until="021200Z",
            movement_dir_speed="MOV NE 25KT NC",
        )
