"""
AIRMET Decoder
==============

A real, best-effort AIRMET (Airmen's Meteorological Information) parser
per ICAO Annex 3 Appendix 6, Table A6-2, following the exact same
structure and conservative-scope discipline as sigmet_decoder.py (see
that module's own docstring for the full rationale - the same
reasoning applies here unchanged).

Added 2026-09-12 during the ICAO/WMO compliance audit: AIRMET is one of
the two products explicitly named by the user's own request ("Critères
SIGMET/AIRMET") and had NO decoder anywhere in this codebase before
this - confirmed via grep. AIRMET shares SIGMET's overall header/
movement/flight-level grammar but covers moderate-severity phenomena
for low-level/VFR flight (below FL100, or FL150 in mountainous areas)
rather than SIGMET's severe phenomena - a genuinely distinct product,
not a duplicate.

This replicates sigmet_decoder.py's conservative approach: parse the
fields that ARE reliably, structurally present (FIR, sequence number,
validity times, issuing center, phenomenon keyword, flight-level range,
movement), leave the free-text location/extent description verbatim
rather than guessing a structural decode of it.

Format (ICAO Annex 3 Appendix 6, Table A6-2 - abbreviated):
    <FIR> AIRMET <seq> VALID <DDHHmm>/<DDHHmm> <ISSUING_CENTER>-
    <FIR> <FIR name> FIR[/UIR] <phenomenon> <OBS|FCST> [AT <DDHHmm>Z]
        <location text> [<FL range>] [MOV <DIR> <speed>KT|STNR] [<intensity change>]=

WARNING: does NOT parse the geographic location/extent description
(free-text, highly variable between issuing centers/regions) - see
sigmet_decoder.py's own identical warning. Phenomenon detection is
keyword-based against the standard ICAO AIRMET phenomenon code list,
not a full grammar.

Reference:
    ICAO Annex 3 to the Convention on International Civil Aviation —
    Meteorological Service for International Air Navigation, Appendix 6,
    Table A6-2 (AIRMET phenomena).
"""

import re
from dataclasses import dataclass

_HEADER_RE = re.compile(
    r"^(?P<fir>[A-Z]{4})\s+AIRMET\s+(?P<seq>\d+)\s+VALID\s+"
    r"(?P<fday>\d{2})(?P<fhour>\d{2})(?P<fmin>\d{2})/(?P<uday>\d{2})(?P<uhour>\d{2})(?P<umin>\d{2})\s+"
    r"(?P<center>[A-Z]{4})-"
)

# Standard ICAO Annex 3 Table A6-2 AIRMET phenomenon codes, longest/
# most-specific first (same ordering discipline as sigmet_decoder.py's
# own list, for the same reason: "MOD TURB" must match before a bare
# "TURB" substring inside a longer phrase would).
_PHENOMENON_KEYWORDS: tuple[str, ...] = (
    "MOD TURB",
    "MOD ICE",
    "MOD MTW",
    "ISOL CB",
    "OCNL CB",
    "SFC WIND",
    "SFC VIS",
    "BKN CLD",
    "OVC CLD",
    "MT OBSC",
)

_FL_RANGE_RE = re.compile(r"\bSFC/FL(?P<top>\d{3})\b")
_FL_BETWEEN_RE = re.compile(r"\bFL(?P<bottom>\d{3})/FL(?P<top>\d{3})\b")
_TOP_FL_RE = re.compile(r"\bTOP\s+FL(?P<top>\d{3})\b")
_ABV_FL_RE = re.compile(r"\bABV\s+FL(?P<level>\d{3})\b")
_MOV_RE = re.compile(r"\bMOV\s+(?P<dir>N|NE|E|SE|S|SW|W|NW)\s+(?P<speed>\d{1,3})\s*KT\b")
_STNR_RE = re.compile(r"\bSTNR\b")
_OBS_AT_RE = re.compile(r"\bOBS\s+AT\s+(?P<hh>\d{2})(?P<mm>\d{2})Z\b")
_FCST_AT_RE = re.compile(r"\bFCST\s+AT\s+(?P<hh>\d{2})(?P<mm>\d{2})Z\b")


@dataclass
class AIRMETReport:
    """Fully decoded AIRMET report (reliably-structured fields only - see module WARNING)."""

    raw_text: str
    fir_code: str | None = None
    sequence_number: str | None = None
    valid_from_day: int | None = None
    valid_from_hour: int | None = None
    valid_from_minute: int | None = None
    valid_until_day: int | None = None
    valid_until_hour: int | None = None
    valid_until_minute: int | None = None
    issuing_center: str | None = None
    phenomenon: str | None = None  # e.g. "MOD TURB", "SFC WIND", or None if not recognized
    is_observed: bool | None = None  # True=OBS, False=FCST, None=neither keyword found
    observed_or_forecast_hour: int | None = None
    observed_or_forecast_minute: int | None = None
    flight_level_bottom: int | None = None  # None if SFC or not specified
    flight_level_top: int | None = None
    movement_dir: str | None = None
    movement_speed_kt: float | None = None
    is_stationary: bool = False
    location_text: str = ""  # verbatim remainder - genuinely free-text, not structurally parsed


class AIRMETDecoder:
    """Best-effort, conservative AIRMET decoder (see module docstring for scope)."""

    @staticmethod
    def decode(raw_airmet: str) -> AIRMETReport:
        """
        Parse a raw AIRMET text into an AIRMETReport.

        Same non-strict-on-body-but-strict-on-header contract as
        SIGMETDecoder.decode() - see that method's own docstring.
        """
        text = " ".join(raw_airmet.strip().split())  # normalize internal whitespace/newlines to single spaces
        if not text:
            raise ValueError("empty AIRMET text.")

        header_match = _HEADER_RE.match(text)
        if not header_match:
            raise ValueError(
                f"no valid AIRMET header found (expected '<FIR> AIRMET <seq> VALID "
                f"<DDHHmm>/<DDHHmm> <CENTER>-') in: {raw_airmet!r}"
            )

        report = AIRMETReport(
            raw_text=raw_airmet,
            fir_code=header_match.group("fir"),
            sequence_number=header_match.group("seq"),
            valid_from_day=int(header_match.group("fday")),
            valid_from_hour=int(header_match.group("fhour")),
            valid_from_minute=int(header_match.group("fmin")),
            valid_until_day=int(header_match.group("uday")),
            valid_until_hour=int(header_match.group("uhour")),
            valid_until_minute=int(header_match.group("umin")),
            issuing_center=header_match.group("center"),
        )

        body = text[header_match.end() :].strip()
        if body.endswith("="):
            body = body[:-1].strip()

        for keyword in _PHENOMENON_KEYWORDS:
            if re.search(rf"\b{re.escape(keyword)}\b", body):
                report.phenomenon = keyword
                break

        obs_match = _OBS_AT_RE.search(body)
        fcst_match = _FCST_AT_RE.search(body)
        if obs_match:
            report.is_observed = True
            report.observed_or_forecast_hour = int(obs_match.group("hh"))
            report.observed_or_forecast_minute = int(obs_match.group("mm"))
        elif fcst_match:
            report.is_observed = False
            report.observed_or_forecast_hour = int(fcst_match.group("hh"))
            report.observed_or_forecast_minute = int(fcst_match.group("mm"))
        elif re.search(r"\bOBS\b", body):
            report.is_observed = True
        elif re.search(r"\bFCST\b", body):
            report.is_observed = False

        m = _FL_BETWEEN_RE.search(body)
        if m:
            report.flight_level_bottom = int(m.group("bottom"))
            report.flight_level_top = int(m.group("top"))
        else:
            m = _FL_RANGE_RE.search(body)
            if m:
                report.flight_level_bottom = 0  # SFC
                report.flight_level_top = int(m.group("top"))
            else:
                m = _TOP_FL_RE.search(body)
                if m:
                    report.flight_level_top = int(m.group("top"))
                else:
                    m = _ABV_FL_RE.search(body)
                    if m:
                        report.flight_level_bottom = int(m.group("level"))

        if _STNR_RE.search(body):
            report.is_stationary = True
        else:
            m = _MOV_RE.search(body)
            if m:
                report.movement_dir = m.group("dir")
                report.movement_speed_kt = float(m.group("speed"))

        report.location_text = body
        return report
