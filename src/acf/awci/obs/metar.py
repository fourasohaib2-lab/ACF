"""
METAR / SPECI decoder for AWCI verification (code form FM 15, WMO-No. 306 Vol. I.1; ICAO Annex 3, App. 3).

Only the observation body is decoded (up to a trend group NOSIG/BECMG/TEMPO or RMK): station, time,
AUTO/NIL, prevailing visibility, CAVOK, present weather, cloud groups, vertical visibility. The AWC JSON
carries neither the CB/TCU cloud type nor present weather, hence this decoder.

Derived quantities:
- ceiling: base of the lowest BKN or OVC layer, or the vertical visibility (ft above the aerodrome).
  CAVOK, NSC, NCD, SKC and CLR state that no significant cloud lies below 5000 ft (or the highest
  minimum sector altitude): no ceiling *below 5000 ft*, nothing said above it. An unknown cover or
  base ("///") below the lowest known ceiling makes the ceiling unknown. Layers are only required below
  5000 ft (or the highest minimum sector altitude) plus CB/TCU (Annex 3, App. 3, 4.5.4.3), so reported
  layers without BKN/OVC also rule out a ceiling below 5000 ft only.
- convective: CB or TCU in a cloud group, or TS (incl. VCTS) in present weather. A manual report, or an
  AUTO report with CAVOK, states their absence; an AUTO report with an untyped layer ("///") or NCD may
  not detect CB, so absence is then unknown (None).
- flight category (FAA, display only): LIFR ceiling < 500 ft or visibility < 1 SM; IFR 500 to < 1000 ft
  or 1 to < 3 SM; MVFR 1000 to 3000 ft or 3 to 5 SM; VFR above both (FAA Aeronautical Information Manual,
  and the AWC flight-category definition).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from fractions import Fraction

METRES_PER_SM = 1609.344  # international statute mile (exact)
NO_CLOUD_LIMIT_FT = 5000  # CAVOK/NSC/NCD/SKC/CLR: no significant cloud below 5000 ft (ICAO Annex 3, 4.5.4.1)

CEILING_VALUE = "value"
CEILING_NONE = "none"  # layers reported, none BKN/OVC
CEILING_NONE_BELOW_5000 = "none_below_5000"
CEILING_UNKNOWN = "unknown"

_STATION = re.compile(r"^[A-Z][A-Z0-9]{3}$")
_TIME = re.compile(r"^(\d{2})(\d{2})(\d{2})Z$")
_WIND = re.compile(r"^(\d{3}|VRB|///)(\d{2,3}|//)(G\d{2,3})?(KT|MPS|KMH)$")
_WIND_VAR = re.compile(r"^\d{3}V\d{3}$")
_VIS_M = re.compile(r"^(\d{4})(NDV|N|NE|E|SE|S|SW|W|NW)?$")
_VIS_SM = re.compile(r"^(M|P)?(\d+/\d+|\d+)SM$")
_WHOLE = re.compile(r"^\d$")
_RVR = re.compile(r"^R\d{2}[LCR]?/")
_WX = re.compile(r"^(\+|-|VC)?(MI|PR|BC|DR|BL|SH|TS|FZ)?((DZ|RA|SN|SG|PL|GR|GS|UP|IC|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS)*)$")
_CLOUD = re.compile(r"^(FEW|SCT|BKN|OVC|///)(\d{3}|///)(CB|TCU|///)?$")
_VV = re.compile(r"^VV(\d{3}|///)$")
_TEMP = re.compile(r"^(M?\d{2}|//)/(M?\d{2}|//)?$")
_STOP = {"RMK", "NOSIG", "BECMG", "TEMPO"}
_NO_SIG = {"NSC", "NCD", "SKC", "CLR"}


class MetarError(ValueError):
    """The text is not a decodable METAR/SPECI."""


@dataclass(frozen=True)
class Layer:
    cover: str  # FEW, SCT, BKN, OVC, or "///" (not observable)
    base_ft: int | None  # above aerodrome level; None when "///"
    cloud_type: str | None  # CB, TCU, "///" (not observable) or None


@dataclass(frozen=True)
class MetarReport:
    raw: str
    kind: str
    station: str
    day: int
    hour: int
    minute: int
    auto: bool
    nil: bool
    cavok: bool
    no_sig_cloud: str | None  # NSC, NCD, SKC or CLR
    visibility_m: float | None
    weather: tuple[str, ...]
    layers: tuple[Layer, ...]
    vertical_visibility_ft: int | None
    vertical_visibility_unknown: bool
    ceiling_status: str
    ceiling_ft: int | None
    convective: bool | None
    flight_category: str | None


def _visibility_sm(token: str, whole: int = 0) -> float:
    match = _VIS_SM.match(token)
    assert match
    value = whole + float(Fraction(match.group(2)))
    return value * METRES_PER_SM


def _ceiling(layers: list[Layer], vv_ft: int | None, vv_unknown: bool, no_cloud: bool,
             any_cloud_group: bool) -> tuple[str, int | None]:
    candidates: list[tuple[int, bool]] = []  # (base, is_ceiling_known)
    lowest_unknown = None
    for layer in layers:
        if layer.cover in ("BKN", "OVC") and layer.base_ft is not None:
            candidates.append((layer.base_ft, True))
        elif layer.cover in ("BKN", "OVC") or layer.cover == "///":
            # unknown base of a ceiling layer, or unknown cover: could be a ceiling at this base or lower
            base = layer.base_ft if layer.base_ft is not None else -1
            lowest_unknown = base if lowest_unknown is None else min(lowest_unknown, base)
    if vv_ft is not None:
        candidates.append((vv_ft, True))
    if vv_unknown:
        lowest_unknown = -1
    known = min((c[0] for c in candidates), default=None)
    if lowest_unknown is not None and (known is None or lowest_unknown < known):
        return CEILING_UNKNOWN, None
    if known is not None:
        return CEILING_VALUE, known
    if no_cloud:
        return CEILING_NONE_BELOW_5000, None
    return (CEILING_NONE, None) if any_cloud_group else (CEILING_UNKNOWN, None)


def _convective(layers: list[Layer], weather: list[str], auto: bool, cavok: bool, ncd: bool) -> bool | None:
    if any(layer.cloud_type in ("CB", "TCU") for layer in layers) or any("TS" in w for w in weather):
        return True
    if cavok or not auto:
        return False
    if ncd or any(layer.cloud_type == "///" for layer in layers):
        return None
    return False


def _category(ceiling_status: str, ceiling_ft: int | None, visibility_m: float | None) -> str | None:
    ranks = []
    if ceiling_status == CEILING_VALUE and ceiling_ft is not None:
        ranks.append(0 if ceiling_ft < 500 else 1 if ceiling_ft < 1000 else 2 if ceiling_ft <= 3000 else 3)
    elif ceiling_status in (CEILING_NONE, CEILING_NONE_BELOW_5000):
        ranks.append(3)
    if visibility_m is not None:
        sm = visibility_m / METRES_PER_SM
        ranks.append(0 if sm < 1 else 1 if sm < 3 else 2 if sm <= 5 else 3)
    return ("LIFR", "IFR", "MVFR", "VFR")[min(ranks)] if ranks else None


def parse_metar(raw: str) -> MetarReport:
    """Decode the observation part of one METAR/SPECI text (see module docstring)."""
    tokens = raw.replace("=", " ").split()
    kind = "METAR"
    if tokens and tokens[0] in ("METAR", "SPECI"):
        kind = tokens.pop(0)
    if tokens and tokens[0] == "COR":
        tokens.pop(0)
    if len(tokens) < 2 or not _STATION.match(tokens[0]) or not _TIME.match(tokens[1]):
        raise MetarError(f"not a METAR/SPECI: {raw[:40]!r}")
    station = tokens[0]
    day, hour, minute = (int(g) for g in _TIME.match(tokens[1]).groups())  # type: ignore[union-attr]
    body: list[str] = []
    for tok in tokens[2:]:
        if tok in _STOP:
            break
        body.append(tok)

    auto = nil = cavok = False
    no_sig: str | None = None
    visibility: float | None = None
    weather: list[str] = []
    layers: list[Layer] = []
    vv_ft: int | None = None
    vv_unknown = False
    any_cloud_group = False
    after_temperature = False
    i = 0
    while i < len(body):
        tok = body[i]
        nxt = body[i + 1] if i + 1 < len(body) else ""
        if tok == "NIL":
            nil = True
        elif tok in ("AUTO", "COR"):
            auto = auto or tok == "AUTO"
        elif after_temperature:
            pass  # QNH, recent weather, wind shear, sea state: not needed here
        elif _WIND.match(tok) or _WIND_VAR.match(tok):
            pass
        elif tok == "CAVOK":
            cavok, visibility = True, 10000.0
        elif _VIS_M.match(tok) and visibility is None:
            visibility = float(int(tok[:4]))
            visibility = 10000.0 if visibility == 9999 else visibility
        elif _WHOLE.match(tok) and _VIS_SM.match(nxt) and "/" in nxt and visibility is None:
            visibility = _visibility_sm(nxt, int(tok))
            i += 1
        elif _VIS_SM.match(tok) and visibility is None:
            visibility = _visibility_sm(tok)
        elif _RVR.match(tok) or tok in ("////", "//"):
            pass
        elif tok in _NO_SIG:
            no_sig, any_cloud_group = tok, True
        elif match := _CLOUD.match(tok):
            cover, base, ctype = match.groups()
            layers.append(Layer(cover, None if base == "///" else int(base) * 100, ctype))
            any_cloud_group = True
        elif match := _VV.match(tok):
            any_cloud_group = True
            if match.group(1) == "///":
                vv_unknown = True
            else:
                vv_ft = int(match.group(1)) * 100
        elif tok == "//////":
            layers.append(Layer("///", None, "///"))
            any_cloud_group = True
        elif _TEMP.match(tok):
            after_temperature = True
        elif _WX.match(tok) and len(tok) >= 2:
            weather.append(tok)
        i += 1

    if nil:
        return MetarReport(raw, kind, station, day, hour, minute, auto, True, False, None, None, (), (), None,
                           False, CEILING_UNKNOWN, None, None, None)
    no_cloud = cavok or no_sig is not None
    status, ceiling_ft = _ceiling(layers, vv_ft, vv_unknown, no_cloud, any_cloud_group or cavok)
    convective = _convective(layers, weather, auto, cavok, no_sig == "NCD")
    return MetarReport(raw, kind, station, day, hour, minute, auto, False, cavok, no_sig, visibility,
                       tuple(weather), tuple(layers), vv_ft, vv_unknown, status, ceiling_ft, convective,
                       _category(status, ceiling_ft, visibility))


def ceiling_below(report: MetarReport, threshold_ft: float) -> bool | None:
    """Observed event "ceiling below threshold": True/False, or None when the report cannot tell."""
    if report.ceiling_status == CEILING_VALUE and report.ceiling_ft is not None:
        return report.ceiling_ft < threshold_ft
    if report.ceiling_status in (CEILING_NONE, CEILING_NONE_BELOW_5000):
        return False if threshold_ft <= NO_CLOUD_LIMIT_FT else None
    return None
