"""
Atmospheric Complexity Framework (ACF)

ICAO Aviation Weather Products & Decoders Module (METAR, TAF, SIGMET, PIREP, IWXXM)
(ICAO Annex 3, WMO No. 306 Code Formats)
"""

from dataclasses import dataclass
from typing import Any

from acf.aviation.icao.metar_decoder import METARDecoder
from acf.aviation.icao.taf_decoder import TAFDecoder


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

    raw_text: str
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
        """
        Décode un bulletin de prévision d'aérodrome TAF.

        Délègue à TAFDecoder (aviation/icao/taf_decoder.py) pour
        l'analyse réelle du message, puis adapte le résultat au
        dataclass TAFData historique de ce module.

        NOTE (correction) : l'implémentation précédente ignorait tout
        le contenu du TAF au-delà du code ICAO et retournait toujours
        les mêmes horaires et la même période de prévision codés en
        dur ("020600Z"/"031200Z", "TEMPO 0212/0216 SHRA 26022G35KT"),
        quel que soit le message passé en entrée — un stub non
        fonctionnel identique à celui du décodeur METAR corrigé plus
        tôt dans cette session. Voir taf_decoder.py et
        tests/test_taf_decoder.py pour la preuve (via des TAF
        différents de celui du test existant) que le décodage des
        groupes de changement (FM/BECMG/TEMPO/PROB30/PROB40) est
        désormais réel.
        """
        report = TAFDecoder.decode(raw_taf)

        issue_time = (
            f"{report.issue_day:02d}{report.issue_hour:02d}{report.issue_minute:02d}Z"
            if report.issue_day is not None
            else ""
        )
        valid_from = (
            f"{report.valid_from_day:02d}{report.valid_from_hour:02d}" if report.valid_from_day is not None else ""
        )
        valid_until = (
            f"{report.valid_until_day:02d}{report.valid_until_hour:02d}"
            if report.valid_until_day is not None
            else ""
        )

        forecast_periods = [
            {
                "change_type": p.change_type,
                "probability": p.probability,
                "from_day": p.from_day,
                "from_hour": p.from_hour,
                "from_minute": p.from_minute,
                "until_day": p.until_day,
                "until_hour": p.until_hour,
                "wind_direction_deg": p.wind_direction_deg,
                "wind_variable": p.wind_variable,
                "wind_speed_kt": p.wind_speed_kt,
                "wind_gust_kt": p.wind_gust_kt,
                "visibility_m": p.visibility_m,
                "cavok": p.cavok,
                "present_weather": p.present_weather,
                "cloud_layers": p.cloud_layers,
                "vertical_visibility_ft": p.vertical_visibility_ft,
            }
            for p in report.periods
        ]

        return TAFData(
            raw_text=report.raw_text,
            icao_code=report.icao_code,
            issue_time_utc=issue_time,
            valid_from_utc=valid_from,
            valid_until_utc=valid_until,
            forecast_periods=forecast_periods,
        )

    @staticmethod
    def decode_sigmet(raw_sigmet: str) -> SIGMETData:
        """
        Décode un message d'avertissement de vol SIGMET.

        NOTE (correction — operationally dangerous, same class as the
        METAR decoder bug fixed earlier this session): this used to
        unconditionally return the exact same fabricated SIGMET
        (fixed FIR "LFFF", fixed phenomenon "EMBD TS", fixed "SEV"
        severity, fixed FL100/FL380, fixed validity/movement)
        regardless of the actual SIGMET text passed in - a SIGMET
        warning severe turbulence over a totally different FIR would
        decode identically to one warning embedded thunderstorms over
        Paris. A real SIGMET decoder needs to parse the FIR
        identifier, phenomenon code, severity, flight-level range,
        validity window, and movement/intensity-change group per
        ICAO Annex 3 - not yet implemented here, for the same reason
        given in decode_taf()'s NOTE. Not fabricated: only raw_text is
        returned as real; every other field is honestly empty instead
        of invented.
        """
        return SIGMETData(
            raw_text=raw_sigmet,
            sigmet_id="",
            fir_code="",
            phenomenon="",
            severity="",
            flight_levels="",
            valid_from="",
            valid_until="",
            movement_dir_speed="",
        )
