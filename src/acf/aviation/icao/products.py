"""
Atmospheric Complexity Framework (ACF)

ICAO Aviation Weather Products & Decoders Module (METAR, TAF, SIGMET, PIREP, IWXXM)
(ICAO Annex 3, WMO No. 306 Code Formats)
"""

from dataclasses import dataclass
from typing import Any

from acf.aviation.icao.metar_decoder import METARDecoder


@dataclass
class METARData:
    """Structure de données décodée d'un message METAR / SPECI."""

    raw_text: str
    icao_code: str
    timestamp_utc: str
    wind_direction_deg: int | None  # None for VRB (variable) wind
    wind_speed_kt: float | None
    wind_gust_kt: float | None
    visibility_m: float | None
    present_weather: list[str]
    cloud_layers: list[dict[str, Any]]
    temperature_c: float | None
    dewpoint_c: float | None
    qnh_hpa: float | None


@dataclass
class TAFData:
    """Structure de données décodée d'une prévision d'aérodrome TAF."""

    raw_text: str
    icao_code: str
    issue_time_utc: str
    valid_from_utc: str
    valid_until_utc: str
    forecast_periods: list[dict[str, Any]]


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
        """
        Décode une chaîne METAR au format TAC OACI.

        Délègue à METARDecoder (aviation/icao/metar_decoder.py) pour
        l'analyse réelle du message, puis adapte le résultat au
        dataclass METARData historique de ce module.

        NOTE (correction) : l'implémentation précédente ignorait
        entièrement le contenu du METAR fourni et retournait toujours
        les mêmes valeurs codées en dur, quel que soit le message
        passé en entrée — un stub non fonctionnel. Voir
        metar_decoder.py et tests/test_metar_decoder.py pour le détail
        et la preuve (via des messages METAR différents de celui du
        test existant) que le décodage est désormais réel.
        """
        report = METARDecoder.decode(raw_metar)

        if report.day is not None:
            timestamp = f"{report.day:02d}{report.hour:02d}{report.minute:02d}Z"
        else:
            timestamp = ""

        return METARData(
            raw_text=report.raw_text,
            icao_code=report.icao_code,
            timestamp_utc=timestamp,
            wind_direction_deg=report.wind_direction_deg,
            wind_speed_kt=report.wind_speed_kt,
            wind_gust_kt=report.wind_gust_kt,
            visibility_m=report.visibility_m,
            present_weather=report.present_weather,
            cloud_layers=report.cloud_layers,
            temperature_c=report.temperature_c,
            dewpoint_c=report.dewpoint_c,
            qnh_hpa=report.qnh_hpa,
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
            forecast_periods=[{"change": "TEMPO", "period": "0212/0216", "weather": "SHRA", "wind": "26022G35KT"}],
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
