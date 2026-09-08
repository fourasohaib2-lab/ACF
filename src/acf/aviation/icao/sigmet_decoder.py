"""
SIGMET Decoder
==============

A real, best-effort SIGMET (Significant Meteorological Information) parser
per ICAO Annex 3 Appendix 6, Table A6-1A, following the same overall pattern
as metar_decoder.py / taf_decoder.py, with one deliberate difference: SIGMET
free text (location description, movement, intensity change) is genuinely
less rigidly standardized across issuing centers than METAR/TAF's tightly
defined TAC grammar, so this parser is explicitly scoped to the fields that
ARE reliably, structurally present (FIR, sequence number, validity times,
issuing center, phenomenon keyword, flight-level range, movement) via
targeted regex/keyword extraction, rather than a strict positional grammar
for the entire message. Fields this parser cannot confidently extract are
left None rather than guessed - the same "don't fabricate an unverifiable
extraction" discipline used throughout this session, applied to parsing
rather than only to formula coefficients.

This replaces ICAOMetDecoder.decode_sigmet() in aviation/icao/products.py,
which used to unconditionally return the exact same fabricated SIGMET
(fixed FIR/phenomenon/severity/levels) regardless of the actual SIGMET text
- fixed earlier this session by removing the fabrication (every field but
raw_text returned honestly empty), with a real parser deferred as too risky
to rush at the time. This is that real parser, scoped conservatively.

Format (ICAO Annex 3 Appendix 6, Table A6-1A - abbreviated):
    <FIR> SIGMET <seq> VALID <DDHHmm>/<DDHHmm> <ISSUING_CENTER>-
    <FIR> <FIR name> FIR[/UIR] <phenomenon> <OBS|FCST> [AT <DDHHmm>Z]
        <location text> [<FL range>] [MOV <DIR> <speed>KT|STNR] [<intensity change>]=

WARNING: does NOT parse the geographic location/extent description (e.g.
"N OF N50", "WI FIR", polygon coordinate lists) - this is genuinely
free-text and highly variable between issuing centers/regions; it is
preserved verbatim in `location_text` rather than structurally decoded.
Phenomenon detection is keyword-based against the standard ICAO phenomenon
code list, not a full grammar - an unusual or non-standard phrasing may not
be recognized (phenomenon stays None rather than a guessed/wrong value).

Reference:
    ICAO Annex 3 to the Convention on International Civil Aviation —
    Meteorological Service for International Air Navigation, Appendix 6.
"""

import re
from dataclasses import dataclass

_HEADER_RE = re.compile(
    r"^(?P<fir>[A-Z]{4})\s+SIGMET\s+(?P<seq>\d+)\s+VALID\s+"
    r"(?P<fday>\d{2})(?P<fhour>\d{2})(?P<fmin>\d{2})/(?P<uday>\d{2})(?P<uhour>\d{2})(?P<umin>\d{2})\s+"
    r"(?P<center>[A-Z]{4})-"
)

# Standard ICAO Annex 3 phenomenon codes, longest/most-specific first so e.g.
# "SEV TURB" is matched before a bare "TURB" would otherwise be found first.
_PHENOMENON_KEYWORDS: tuple[str, ...] = (
    "SEV TURB",
    "SEV ICE (FZRA)",
    "SEV ICE",
    "SEV MTW",
    "HVY DS",
    "HVY SS",
    "OBSC TS",
    "EMBD TS",
    "FRQ TS",
    "SQL TS",
    "TSGR",
    "GR",
    "TS",
    "TURB",
    "ICE",
    "MTW",
    "VA CLD",
    "VA",
    "TC",
    "RDOACT CLD",
)

_INTENSITY_QUALIFIERS: tuple[str, ...] = ("OBSC", "EMBD", "FRQ", "SQL", "ISOL", "OCNL")
_SEVERITY_KEYWORDS: tuple[str, ...] = ("SEV", "MOD")

_FL_RANGE_RE = re.compile(r"\bSFC/FL(?P<top>\d{3})\b")
_FL_BETWEEN_RE = re.compile(r"\bFL(?P<bottom>\d{3})/FL(?P<top>\d{3})\b")
_TOP_FL_RE = re.compile(r"\bTOP\s+FL(?P<top>\d{3})\b")
_ABV_FL_RE = re.compile(r"\bABV\s+FL(?P<level>\d{3})\b")
_MOV_RE = re.compile(r"\bMOV\s+(?P<dir>N|NE|E|SE|S|SW|W|NW)\s+(?P<speed>\d{1,3})\s*KT\b")
_STNR_RE = re.compile(r"\bSTNR\b")
_OBS_AT_RE = re.compile(r"\bOBS\s+AT\s+(?P<hh>\d{2})(?P<mm>\d{2})Z\b")
_FCST_AT_RE = re.compile(r"\bFCST\s+AT\s+(?P<hh>\d{2})(?P<mm>\d{2})Z\b")


@dataclass
class SIGMETReport:
    """Fully decoded SIGMET report (reliably-structured fields only - see module WARNING)."""

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
    phenomenon: str | None = None
    intensity_qualifier: str | None = None  # "OBSC", "EMBD", "FRQ", "SQL", "ISOL", "OCNL", or None
    severity: str | None = None  # "SEV", "MOD", or None
    is_observed: bool | None = None  # True=OBS, False=FCST, None=neither keyword found
    observed_or_forecast_hour: int | None = None
    observed_or_forecast_minute: int | None = None
    flight_level_bottom: int | None = None  # None if SFC or not specified
    flight_level_top: int | None = None
    movement_dir: str | None = None
    movement_speed_kt: float | None = None
    is_stationary: bool = False
    location_text: str = ""  # verbatim remainder - genuinely free-text, not structurally parsed


class SIGMETDecoder:
    """Best-effort, conservative SIGMET decoder (see module docstring for scope)."""

    @staticmethod
    def decode(raw_sigmet: str) -> SIGMETReport:
        """
        Parse a raw SIGMET text into a SIGMETReport.

        Unlike METARDecoder/TAFDecoder, this does not raise on a body it
        cannot fully interpret: SIGMET free text is genuinely too variable
        to treat a parse gap as an input error. It DOES raise if the
        message doesn't even have the standard header line (FIR, SIGMET
        keyword, sequence number, validity, issuing center) - without
        that, nothing here can be trusted at all.
        """
        text = " ".join(raw_sigmet.strip().split())  # normalize internal whitespace/newlines to single spaces
        if not text:
            raise ValueError("empty SIGMET text.")

        header_match = _HEADER_RE.match(text)
        if not header_match:
            raise ValueError(
                f"no valid SIGMET header found (expected '<FIR> SIGMET <seq> VALID "
                f"<DDHHmm>/<DDHHmm> <CENTER>-') in: {raw_sigmet!r}"
            )

        report = SIGMETReport(
            raw_text=raw_sigmet,
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

        for qualifier in _INTENSITY_QUALIFIERS:
            if re.search(rf"\b{qualifier}\b", body):
                report.intensity_qualifier = qualifier
                break

        for severity in _SEVERITY_KEYWORDS:
            if re.search(rf"\b{severity}\b", body):
                report.severity = severity
                break

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
