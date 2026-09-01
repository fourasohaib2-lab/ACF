"""
TAF Decoder
===========

A real, token-based TAF (Terminal Aerodrome Forecast) parser per ICAO
Annex 3 / WMO No. 306 (FM 51-XV TAF), following the same pattern and
verification discipline as metar_decoder.py.

This replaces ICAOMetDecoder.decode_taf() in aviation/icao/products.py,
which used to unconditionally return the same hard-coded, fabricated
forecast periods regardless of the actual TAF text (fixed earlier this
session by removing the fabrication and returning honestly-empty fields
instead - a real parser was deferred at that point as too risky to rush).
This is that real parser.

Grammar covered (WMO FM 51-XV / ICAO Annex 3):
    TAF [AMD|COR] CCCC DDHHmmZ DDHH/DDHH
    <base forecast: wind visibility weather clouds [CAVOK]>
    [FMDDHHmm <wind visibility weather clouds [CAVOK]>]*
    [BECMG DDHH/DDHH <wind visibility weather clouds [CAVOK]>]*
    [TEMPO DDHH/DDHH <wind visibility weather clouds [CAVOK]>]*
    [PROB30|PROB40 [TEMPO] DDHH/DDHH <wind visibility weather clouds>]*
    [RMK ...]

Each change-group's wind/visibility/weather/cloud sub-fields reuse the
exact same, already-verified regex groups as METARDecoder (same TAC
syntax for these groups in both product types) - imported directly
rather than duplicated, per the project's single-source-of-truth rule.

WARNING (same spirit as metar_decoder.py's own warning): this covers the
commonly-used TAF groups and change-group types (FM/BECMG/TEMPO/PROB30/
PROB40, including combined PROB+TEMPO) but does NOT implement the full
WMO Doc 782 grammar (e.g. TX/TN temperature groups, wind shear WS
groups, full remarks-section parsing beyond truncating at "RMK", NSW/NSC
edge cases beyond the basic no-significant-weather/cloud markers already
handled). Verify against the current ICAO Annex 3 / WMO No. 306 text
before any operational use.

Reference:
    ICAO Annex 3 to the Convention on International Civil Aviation —
    Meteorological Service for International Air Navigation.
    WMO No. 306, Manual on Codes, Vol. I.1 (FM 51-XV TAF).
"""

import re
from dataclasses import dataclass, field
from typing import Any

from acf.aviation.icao.metar_decoder import (
    _CLOUD_RE,
    _VIS_M_RE,
    _VV_RE,
    _WIND_RE,
    _WX_RE,
)

_HEADER_TIME_RE = re.compile(r"^(?P<day>\d{2})(?P<hour>\d{2})(?P<minute>\d{2})Z$")
_VALIDITY_RE = re.compile(r"^(?P<fday>\d{2})(?P<fhour>\d{2})/(?P<uday>\d{2})(?P<uhour>\d{2})$")
_FM_RE = re.compile(r"^FM(?P<day>\d{2})(?P<hour>\d{2})(?P<minute>\d{2})$")
_PERIOD_RE = re.compile(r"^(?P<fday>\d{2})(?P<fhour>\d{2})/(?P<uday>\d{2})(?P<uhour>\d{2})$")

_CHANGE_KEYWORDS = ("BECMG", "TEMPO", "PROB30", "PROB40")


@dataclass
class TAFForecastPeriod:
    """One forecast period within a TAF: the base forecast or one change group."""

    change_type: str  # "BASE", "FM", "BECMG", "TEMPO", "PROB30", "PROB40"
    probability: int | None = None  # 30 or 40, only set for PROB groups (incl. PROB+TEMPO)
    from_day: int | None = None
    from_hour: int | None = None
    from_minute: int | None = None  # only meaningful for "FM" groups (minute-precision)
    until_day: int | None = None
    until_hour: int | None = None
    wind_direction_deg: int | None = None  # None if VRB or absent
    wind_variable: bool = False
    wind_speed_kt: float | None = None
    wind_gust_kt: float | None = None
    visibility_m: float | None = None
    cavok: bool = False
    present_weather: list[str] = field(default_factory=list)
    cloud_layers: list[dict[str, Any]] = field(default_factory=list)
    vertical_visibility_ft: int | None = None


@dataclass
class TAFReport:
    """Fully decoded TAF report."""

    raw_text: str
    icao_code: str
    is_amended: bool
    is_corrected: bool
    issue_day: int | None
    issue_hour: int | None
    issue_minute: int | None
    valid_from_day: int | None
    valid_from_hour: int | None
    valid_until_day: int | None
    valid_until_hour: int | None
    periods: list[TAFForecastPeriod] = field(default_factory=list)


def _parse_wind_visibility_weather_clouds(tokens: list[str], start: int, end: int, period: TAFForecastPeriod) -> None:
    """Consumes wind/CAVOK/visibility/weather/cloud groups from tokens[start:end] into `period`."""
    idx = start
    if idx < end:
        m = _WIND_RE.match(tokens[idx])
        if m:
            period.wind_variable = m.group("dir") == "VRB"
            period.wind_direction_deg = None if period.wind_variable else int(m.group("dir"))
            speed = float(m.group("speed"))
            period.wind_speed_kt = speed * 1.94384 if m.group("unit") == "MPS" else speed
            if m.group("gust"):
                gust = float(m.group("gust"))
                period.wind_gust_kt = gust * 1.94384 if m.group("unit") == "MPS" else gust
            idx += 1

    if idx < end and tokens[idx] == "CAVOK":
        period.cavok = True
        period.visibility_m = 10000.0
        idx += 1
    elif idx < end:
        m = _VIS_M_RE.match(tokens[idx])
        if m:
            # NOTE (correction): same fix as aviation/icao/metar_decoder.py -
            # "9999" is the WMO/ICAO sentinel for "visibility >= 10 km",
            # not a literal 9999 m measurement.
            raw_vis = m.group("vis")
            period.visibility_m = 10000.0 if raw_vis == "9999" else float(raw_vis)
            idx += 1

    while idx < end:
        m = _WX_RE.match(tokens[idx])
        if not m or not m.group("phenomena") or tokens[idx] in ("NSW",):
            break
        period.present_weather.append(tokens[idx])
        idx += 1
    if idx < end and tokens[idx] == "NSW":
        idx += 1  # "no significant weather" (used in change groups) - explicitly absent, not a group to record

    while idx < end:
        if tokens[idx] in ("SKC", "CLR", "NSC", "NCD"):
            idx += 1
            continue
        m = _CLOUD_RE.match(tokens[idx])
        if m:
            period.cloud_layers.append(
                {"coverage": m.group("cover"), "base_ft": int(m.group("height")) * 100, "type": m.group("type")}
            )
            idx += 1
            continue
        m = _VV_RE.match(tokens[idx])
        if m and m.group("height") != "///":
            period.vertical_visibility_ft = int(m.group("height")) * 100
            idx += 1
            continue
        break


class TAFDecoder:
    """Token-based TAF decoder."""

    @staticmethod
    def decode(raw_taf: str) -> TAFReport:
        """
        Parse a raw TAF text into a TAFReport.

        Raises
        ------
        ValueError
            If no valid 4-letter ICAO station identifier is found, or if
            the issue-time/validity header groups are missing or malformed
            (both required for any minimally-useful decode).
        """
        text = raw_taf.strip()
        if "RMK" in text:
            text = text.split("RMK")[0].strip()
        tokens = text.split()
        if not tokens:
            raise ValueError("empty TAF text.")

        idx = 0
        if idx < len(tokens) and tokens[idx] == "TAF":
            idx += 1

        is_amended = is_corrected = False
        if idx < len(tokens) and tokens[idx] == "AMD":
            is_amended = True
            idx += 1
        elif idx < len(tokens) and tokens[idx] == "COR":
            is_corrected = True
            idx += 1

        if idx >= len(tokens) or not re.match(r"^[A-Z]{4}$", tokens[idx]):
            raise ValueError(f"no valid 4-letter ICAO station identifier found in: {raw_taf!r}")
        icao_code = tokens[idx]
        idx += 1

        if idx >= len(tokens):
            raise ValueError(f"TAF header truncated (no issue time) in: {raw_taf!r}")
        m = _HEADER_TIME_RE.match(tokens[idx])
        if not m:
            raise ValueError(f"expected a DDHHmmZ issue time at position {idx} in: {raw_taf!r}")
        issue_day, issue_hour, issue_minute = int(m.group("day")), int(m.group("hour")), int(m.group("minute"))
        idx += 1

        if idx >= len(tokens):
            raise ValueError(f"TAF header truncated (no validity period) in: {raw_taf!r}")
        m = _VALIDITY_RE.match(tokens[idx])
        if not m:
            raise ValueError(f"expected a DDHH/DDHH validity period at position {idx} in: {raw_taf!r}")
        valid_from_day, valid_from_hour = int(m.group("fday")), int(m.group("fhour"))
        valid_until_day, valid_until_hour = int(m.group("uday")), int(m.group("uhour"))
        idx += 1

        periods: list[TAFForecastPeriod] = []

        # Base forecast: every token up to the first change-group keyword.
        base_end = idx
        while base_end < len(tokens) and not _is_change_marker(tokens[base_end]):
            base_end += 1
        base_period = TAFForecastPeriod(change_type="BASE")
        _parse_wind_visibility_weather_clouds(tokens, idx, base_end, base_period)
        periods.append(base_period)
        idx = base_end

        while idx < len(tokens):
            token = tokens[idx]

            m = _FM_RE.match(token)
            if m:
                period = TAFForecastPeriod(
                    change_type="FM",
                    from_day=int(m.group("day")),
                    from_hour=int(m.group("hour")),
                    from_minute=int(m.group("minute")),
                )
                idx += 1
                group_end = idx
                while group_end < len(tokens) and not _is_change_marker(tokens[group_end]):
                    group_end += 1
                _parse_wind_visibility_weather_clouds(tokens, idx, group_end, period)
                periods.append(period)
                idx = group_end
                continue

            if token in ("PROB30", "PROB40"):
                probability = 30 if token == "PROB30" else 40
                idx += 1
                change_type = "PROB30" if probability == 30 else "PROB40"
                if idx < len(tokens) and tokens[idx] == "TEMPO":
                    change_type = "TEMPO"
                    idx += 1
                period = TAFForecastPeriod(change_type=change_type, probability=probability)
                if idx < len(tokens):
                    pm = _PERIOD_RE.match(tokens[idx])
                    if pm:
                        period.from_day, period.from_hour = int(pm.group("fday")), int(pm.group("fhour"))
                        period.until_day, period.until_hour = int(pm.group("uday")), int(pm.group("uhour"))
                        idx += 1
                group_end = idx
                while group_end < len(tokens) and not _is_change_marker(tokens[group_end]):
                    group_end += 1
                _parse_wind_visibility_weather_clouds(tokens, idx, group_end, period)
                periods.append(period)
                idx = group_end
                continue

            if token in ("BECMG", "TEMPO"):
                idx += 1
                period = TAFForecastPeriod(change_type=token)
                if idx < len(tokens):
                    pm = _PERIOD_RE.match(tokens[idx])
                    if pm:
                        period.from_day, period.from_hour = int(pm.group("fday")), int(pm.group("fhour"))
                        period.until_day, period.until_hour = int(pm.group("uday")), int(pm.group("uhour"))
                        idx += 1
                group_end = idx
                while group_end < len(tokens) and not _is_change_marker(tokens[group_end]):
                    group_end += 1
                _parse_wind_visibility_weather_clouds(tokens, idx, group_end, period)
                periods.append(period)
                idx = group_end
                continue

            # Unrecognized token outside any known group (e.g. stray text) - skip defensively rather than looping.
            idx += 1

        return TAFReport(
            raw_text=raw_taf,
            icao_code=icao_code,
            is_amended=is_amended,
            is_corrected=is_corrected,
            issue_day=issue_day,
            issue_hour=issue_hour,
            issue_minute=issue_minute,
            valid_from_day=valid_from_day,
            valid_from_hour=valid_from_hour,
            valid_until_day=valid_until_day,
            valid_until_hour=valid_until_hour,
            periods=periods,
        )


def _is_change_marker(token: str) -> bool:
    return token in _CHANGE_KEYWORDS or bool(_FM_RE.match(token))
