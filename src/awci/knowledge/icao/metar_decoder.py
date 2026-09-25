"""
METAR Decoder
=============

A real, token-based METAR/SPECI parser per ICAO Annex 3 / WMO No. 306
(commonly referenced by its older designation, WMO Doc 782, "Manual on
Codes").

This replaces ICAOMetDecoder.decode_metar() in aviation/icao/products.py,
which was a NON-FUNCTIONAL STUB: it ignored the METAR content entirely
and returned the same hard-coded METARData every time regardless of
input (verified: the one pre-existing test for it happened to pass
only because its test METAR string was crafted to coincidentally match
the hard-coded fake values — a test that passes for the wrong reason).
See tests/test_metar_decoder.py for coverage with METAR strings that
would NOT match the old stub's fake output, proving this is real
parsing.

WARNING (kept from the original plan, still true): this decoder covers
the commonly-used METAR groups (wind incl. VRB/gusts/variable
direction, visibility incl. statute miles and CAVOK, present weather,
cloud layers incl. CB/TCU and vertical visibility, temperature/
dewpoint, altimeter in both hPa and inHg, NOSIG/BECMG/TEMPO trend
detection) but does NOT implement the complete WMO Doc 782 grammar
(e.g. RVR trend arrows, full remarks-section parsing, runway state
groups, volcanic ash/wind shear remarks). Verify against the current
ICAO Annex 3 / WMO No. 306 text before any operational use.

Reference:
    ICAO Annex 3 to the Convention on International Civil Aviation —
    Meteorological Service for International Air Navigation.
    WMO No. 306, Manual on Codes, Vol. I.1 (FM 15-XV METAR, FM 51-XV TAF).
"""

import re
from dataclasses import dataclass, field
from typing import Any

from acf.physics_guard.variable_quality import VariableQualityStatus, assess_variable_quality

INHG_TO_HPA = 33.8639  # 1 inHg = 1013.25/29.9212 hPa, standard atmosphere conversion.

_WIND_RE = re.compile(r"^(?P<dir>\d{3}|VRB)(?P<speed>\d{2,3})(G(?P<gust>\d{2,3}))?(?P<unit>KT|MPS)$")
_WIND_VAR_RE = re.compile(r"^(?P<from>\d{3})V(?P<to>\d{3})$")
_VIS_M_RE = re.compile(r"^(?P<vis>\d{4})$")
_VIS_SM_RE = re.compile(r"^(?P<whole>\d+)?(?:(?P<num>\d)/(?P<den>\d))?SM$")
_RVR_RE = re.compile(
    r"^R(?P<runway>\d{2}[LRC]?)/(?P<mod>[MP])?(?P<value>\d{4})(V(?P<mod2>[MP])?(?P<value2>\d{4}))?(?P<unit>FT)?$"
)
_CLOUD_RE = re.compile(r"^(?P<cover>FEW|SCT|BKN|OVC)(?P<height>\d{3})(?P<type>CB|TCU)?$")
_VV_RE = re.compile(r"^VV(?P<height>\d{3}|///)$")
_TEMP_RE = re.compile(r"^(?P<tsign>M)?(?P<temp>\d{2})/(?P<dsign>M)?(?P<dew>\d{2})?$")
_QNH_RE = re.compile(r"^Q(?P<value>\d{4})$")
_ALT_RE = re.compile(r"^A(?P<value>\d{4})$")
_WX_RE = re.compile(
    r"^(?P<intensity>[-+]|VC)?"
    r"(?P<descriptor>MI|PR|BC|DR|BL|SH|TS|FZ)?"
    r"(?P<phenomena>(?:DZ|RA|SN|SG|IC|PL|GR|GS|UP|FG|BR|SA|DU|HZ|FU|VA|PY|PO|SQ|FC|SS|DS)+)$"
)


@dataclass
class METARReport:
    """Fully decoded METAR/SPECI report."""

    raw_text: str
    icao_code: str
    day: int | None
    hour: int | None
    minute: int | None
    is_auto: bool
    wind_direction_deg: int | None  # None if VRB
    wind_variable_direction: bool
    wind_speed_kt: float | None
    wind_gust_kt: float | None
    wind_variable_from_deg: int | None
    wind_variable_to_deg: int | None
    visibility_m: float | None
    cavok: bool
    rvr: list[dict[str, Any]] = field(default_factory=list)
    present_weather: list[str] = field(default_factory=list)
    cloud_layers: list[dict[str, Any]] = field(default_factory=list)
    vertical_visibility_ft: int | None = None
    temperature_c: float | None = None
    dewpoint_c: float | None = None
    qnh_hpa: float | None = None
    trend: str | None = None  # "NOSIG", "BECMG", "TEMPO", or None if absent


class METARDecoder:
    """Token-based METAR/SPECI decoder."""

    @staticmethod
    def decode(raw_metar: str) -> METARReport:
        """
        Parse a raw METAR/SPECI text into a METARReport.

        Parameters
        ----------
        raw_metar : str
            Raw METAR text in ICAO TAC format.

        Returns
        -------
        METARReport

        Raises
        ------
        ValueError
            If the report has no station identifier token, or if the
            wind group fails to parse (both required for any
            minimally-useful decode).
        """
        text = raw_metar.strip()
        tokens = text.split()
        if not tokens:
            raise ValueError("empty METAR text.")

        # Skip optional leading METAR/SPECI/COR keyword.
        idx = 0
        while idx < len(tokens) and tokens[idx] in ("METAR", "SPECI", "COR"):
            idx += 1

        if idx >= len(tokens) or not re.match(r"^[A-Z]{4}$", tokens[idx]):
            raise ValueError(f"no valid 4-letter ICAO station identifier found in: {raw_metar!r}")
        icao_code = tokens[idx]
        idx += 1

        day = hour = minute = None
        if idx < len(tokens) and re.match(r"^\d{6}Z$", tokens[idx]):
            t = tokens[idx]
            day, hour, minute = int(t[0:2]), int(t[2:4]), int(t[4:6])
            idx += 1

        is_auto = False
        if idx < len(tokens) and tokens[idx] == "AUTO":
            is_auto = True
            idx += 1

        wind_dir = wind_speed = wind_gust = None
        wind_var_from = wind_var_to = None
        wind_variable = False
        if idx < len(tokens):
            m = _WIND_RE.match(tokens[idx])
            if m:
                wind_variable = m.group("dir") == "VRB"
                wind_dir = None if wind_variable else int(m.group("dir"))
                speed = float(m.group("speed"))
                # MPS -> KT conversion (1 m/s = 1.94384 kt).
                wind_speed = speed * 1.94384 if m.group("unit") == "MPS" else speed
                if m.group("gust"):
                    gust = float(m.group("gust"))
                    wind_gust = gust * 1.94384 if m.group("unit") == "MPS" else gust
                idx += 1
            else:
                raise ValueError(f"expected a wind group at position {idx} in: {raw_metar!r}")

        if idx < len(tokens):
            m = _WIND_VAR_RE.match(tokens[idx])
            if m:
                wind_var_from, wind_var_to = int(m.group("from")), int(m.group("to"))
                idx += 1

        cavok = False
        visibility_m: float | None = None
        if idx < len(tokens) and tokens[idx] == "CAVOK":
            cavok = True
            visibility_m = 10000.0
            idx += 1
        elif idx < len(tokens):
            m = _VIS_M_RE.match(tokens[idx])
            if m:
                # NOTE (correction): "9999" is a defined WMO/ICAO sentinel
                # meaning "visibility >= 10 km", not a literal measurement
                # of 9999 m - the same convention already established and
                # tested in science/observations/wmo_code_tables.py's
                # decode_metar_visibility() elsewhere in ACF. This decoder
                # used to report it as a literal 9999.0 m, one meter short
                # of the actual documented meaning; the existing test
                # even asserted directly on that wrong value.
                raw_vis = m.group("vis")
                visibility_m = 10000.0 if raw_vis == "9999" else float(raw_vis)
                idx += 1
            else:
                m = _VIS_SM_RE.match(tokens[idx])
                sm_value = None
                if m and (m.group("whole") or m.group("num")):
                    sm_value = float(m.group("whole") or 0)
                    if m.group("num"):
                        sm_value += float(m.group("num")) / float(m.group("den"))
                    idx += 1
                else:
                    m2 = re.match(r"^(\d+)/(\d+)SM$", tokens[idx + 1]) if idx + 1 < len(tokens) else None
                    if m2 is not None and tokens[idx].isdigit():
                        # Split form "1 1/2SM".
                        whole = float(tokens[idx])
                        sm_value = whole + float(m2.group(1)) / float(m2.group(2))
                        idx += 2
                if sm_value is not None:
                    visibility_m = sm_value * 1609.344  # statute miles -> meters

        rvr = []
        while idx < len(tokens):
            m = _RVR_RE.match(tokens[idx])
            if not m:
                break
            rvr.append(
                {
                    "runway": m.group("runway"),
                    "value_m": float(m.group("value")),
                    "modifier": m.group("mod"),
                }
            )
            idx += 1

        present_weather = []
        while idx < len(tokens):
            m = _WX_RE.match(tokens[idx])
            if not m or not m.group("phenomena"):
                break
            present_weather.append(tokens[idx])
            idx += 1

        cloud_layers = []
        vertical_visibility_ft = None
        while idx < len(tokens):
            if tokens[idx] in ("SKC", "CLR", "NSC", "NCD"):
                idx += 1
                continue
            m = _CLOUD_RE.match(tokens[idx])
            if m:
                cloud_layers.append(
                    {
                        "coverage": m.group("cover"),
                        "base_ft": int(m.group("height")) * 100,
                        "type": m.group("type"),
                    }
                )
                idx += 1
                continue
            m = _VV_RE.match(tokens[idx])
            if m and m.group("height") != "///":
                vertical_visibility_ft = int(m.group("height")) * 100
                idx += 1
                continue
            break

        temperature_c = dewpoint_c = None
        if idx < len(tokens):
            m = _TEMP_RE.match(tokens[idx])
            if m and m.group("temp"):
                temperature_c = -float(m.group("temp")) if m.group("tsign") else float(m.group("temp"))
                if m.group("dew"):
                    dewpoint_c = -float(m.group("dew")) if m.group("dsign") else float(m.group("dew"))
                idx += 1

        qnh_hpa = None
        if idx < len(tokens):
            m = _QNH_RE.match(tokens[idx])
            if m:
                qnh_hpa = float(m.group("value"))
                idx += 1
            else:
                m = _ALT_RE.match(tokens[idx])
                if m:
                    qnh_hpa = (float(m.group("value")) / 100.0) * INHG_TO_HPA
                    idx += 1

        trend = None
        remaining = tokens[idx:]
        if "NOSIG" in remaining:
            trend = "NOSIG"
        elif "BECMG" in remaining:
            trend = "BECMG"
        elif "TEMPO" in remaining:
            trend = "TEMPO"

        return METARReport(
            raw_text=raw_metar,
            icao_code=icao_code,
            day=day,
            hour=hour,
            minute=minute,
            is_auto=is_auto,
            wind_direction_deg=wind_dir,
            wind_variable_direction=wind_variable,
            wind_speed_kt=wind_speed,
            wind_gust_kt=wind_gust,
            wind_variable_from_deg=wind_var_from,
            wind_variable_to_deg=wind_var_to,
            visibility_m=visibility_m,
            cavok=cavok,
            rvr=rvr,
            present_weather=present_weather,
            cloud_layers=cloud_layers,
            vertical_visibility_ft=vertical_visibility_ft,
            temperature_c=temperature_c,
            dewpoint_c=dewpoint_c,
            qnh_hpa=qnh_hpa,
            trend=trend,
        )


def metar_report_quality(report: METARReport) -> dict[str, VariableQualityStatus]:
    """
    Real per-variable quality status (docs/ACF_MASTER_PROMPT.md section
    32) for one decoded, real, live METAR/SPECI report - explicit user
    request: "le but est de brancher acf et awci avec des vrais station
    pour nous rendre des vrai reponse instantanément" (this closes the
    quality-flagging half of that loop for real live station data, not
    just decoding it).

    Bridges METARReport's own real native units (Celsius, hPa, knots)
    to acf.physics_guard.variable_quality.assess_variable_quality()'s
    CF-standard_name-keyed real range/consistency checks via that
    function's own `units` parameter (real MetPy/pint conversion, not
    reimplemented here).

    Only fields the report actually reports (not None) are assessed -
    a METAR that omits temperature, say, is not claimed to be MISSING
    a variable this function never confirmed the station was expected
    to report (see assess_variable_quality()'s own `expected_variables`
    default - unused here for the same reason).

    Returns
    -------
    dict[str, VariableQualityStatus]
        Keyed by CF standard_name ("air_temperature",
        "dewpoint_temperature", "air_pressure", "wind_speed") - NOT by
        METARReport's own field names.
    """
    data: dict[str, float] = {}
    units: dict[str, str] = {}

    if report.temperature_c is not None:
        data["air_temperature"] = report.temperature_c
        units["air_temperature"] = "degC"
    if report.dewpoint_c is not None:
        data["dewpoint_temperature"] = report.dewpoint_c
        units["dewpoint_temperature"] = "degC"
    if report.qnh_hpa is not None:
        data["air_pressure"] = report.qnh_hpa
        units["air_pressure"] = "hPa"
    if report.wind_speed_kt is not None:
        data["wind_speed"] = report.wind_speed_kt
        units["wind_speed"] = "kt"

    return assess_variable_quality(data, units=units)
