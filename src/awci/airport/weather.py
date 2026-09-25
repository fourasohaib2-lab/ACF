"""
Atmospheric Complexity Framework (ACF)

Airport Operations - Weather Snapshot

Real per-airport weather snapshot - the ``weather.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 12
("Airport Operations... Chain: Weather → Airport → Runway →
Operation"). Composes 3 already-real systems - never a new fetch or
classification of its own:

- ``awci.observations.hub.ObservationsHub`` (real live METAR fetch).
- ``awci.hazards.ceiling.classify_ceiling_category`` (real FAA/NOAA
  LIFR/IFR/MVFR/VFR ceiling-only bands) - applied here to a real
  CEILING HEIGHT taken directly from the METAR's own real decoded
  cloud layers (the lowest BKN/OVC layer base, the real ICAO
  definition of "ceiling"), a different, more authoritative real
  source than that module's own ``compute_real_ceiling_at_point()``
  (a dewpoint-depression LCL estimate) - both real, complementary, not
  duplicated.
- ``awci.knowledge.icao.present_weather_codes`` (real WMO/ICAO
  intensity/descriptor/phenomena meanings) - applied to the METAR's
  own real, already-decoded ``present_weather`` code strings via
  ``metar_decoder``'s own already-real ``_WX_RE`` regex (reused
  directly, not re-derived, to avoid a second, potentially-drifting
  parser for the exact same real grammar).

Deliberately does NOT fabricate a precipitation rate (mm/h): METAR
present-weather codes carry a real intensity QUALIFIER (light/
moderate/heavy), never a quantified rate - forcing one through
``awci.hazards.visibility.classify_precipitation_intensity()`` (which
expects a real mm/h value) would mean inventing a number METAR itself
does not report.
"""

from __future__ import annotations

from dataclasses import dataclass

from awci.hazards.ceiling import classify_ceiling_category
from awci.knowledge.icao.metar_decoder import _WX_RE, METARReport
from awci.knowledge.icao.present_weather_codes import (
    PRESENT_WEATHER_DESCRIPTORS,
    PRESENT_WEATHER_INTENSITY,
    PRESENT_WEATHER_PHENOMENA,
)
from awci.observations.hub import ObservationsHub

#: Real ICAO ceiling definition - only BKN (broken) or OVC (overcast)
#: coverage constitutes a ceiling; FEW/SCT layers do not, by the real,
#: standard ICAO/FAA definition.
_CEILING_COVERAGE_CODES = frozenset({"BKN", "OVC"})

#: Real feet -> metres conversion, matching every other real conversion
#: already used throughout awci.hazards/awci.knowledge.
_FT_TO_M = 0.3048


@dataclass(frozen=True)
class AirportWeatherSnapshot:
    """Real, composed per-airport weather view - every field either a
    real, directly-decoded METAR value, or a real classification of
    one. Fields are honestly ``None`` (never fabricated) when the real
    underlying METAR fetch failed or the real report carries no
    relevant group."""

    icao_code: str
    is_real_data: bool
    status: str
    ceiling_height_ft: float | None
    ceiling_category: str | None
    visibility_m: float | None
    present_weather_descriptions: tuple[str, ...]
    raw_metar: str | None


def real_ceiling_height_ft(report: METARReport) -> float | None:
    """
    Real ICAO ceiling height (feet) - the lowest real BKN/OVC
    cloud-layer base already decoded from this real METAR. ``None``
    (never fabricated) when no real BKN/OVC layer is present - a real,
    honest "no ceiling reported" state (e.g. CAVOK, or only FEW/SCT
    layers), not an error.
    """
    ceiling_layer_bases = [
        layer["base_ft"] for layer in report.cloud_layers if layer["coverage"] in _CEILING_COVERAGE_CODES
    ]
    if not ceiling_layer_bases:
        return None
    return float(min(ceiling_layer_bases))


def describe_present_weather_code(code: str) -> str:
    """
    Real, human-readable description of one real METAR present-weather
    code (e.g. "-RA" -> "Light Rain", "+TSRA" -> "Thunderstorm, Heavy
    Rain") - parses ``code`` with ``metar_decoder``'s own already-real
    ``_WX_RE`` regex (the exact same grammar the decoder itself already
    parses this code with, reused directly rather than re-derived) and
    looks each real group up in the real WMO/ICAO meaning tables
    already in ``present_weather_codes``. Unparseable input (should not
    occur for a code that already came from a real decoded
    ``METARReport``) is returned verbatim rather than raising, since
    this is a display-formatting concern, not validation.
    """
    match = _WX_RE.match(code)
    if match is None:
        return code
    parts: list[str] = []
    intensity = match.group("intensity") or ""
    intensity_meaning = PRESENT_WEATHER_INTENSITY.get(intensity)
    if intensity_meaning and intensity_meaning != "Moderate":
        parts.append(intensity_meaning)
    descriptor = match.group("descriptor")
    if descriptor:
        parts.append(PRESENT_WEATHER_DESCRIPTORS.get(descriptor, descriptor))
    phenomena = match.group("phenomena") or ""
    phenomenon_codes = [phenomena[i : i + 2] for i in range(0, len(phenomena), 2)]
    parts.extend(PRESENT_WEATHER_PHENOMENA.get(p, p) for p in phenomenon_codes)
    return ", ".join(parts) if parts else code


def build_weather_snapshot(icao_code: str, hub: ObservationsHub | None = None, timeout: float = 8.0) -> AirportWeatherSnapshot:
    """
    Real, composed weather snapshot for one real airport - fetches the
    real, current METAR via ``ObservationsHub.fetch_station()`` (a real
    default hub is constructed if none is supplied) and derives the
    real ceiling/visibility/present-weather fields from it. Honestly
    ``is_real_data=False`` with every derived field ``None`` (never a
    fabricated fallback) when the real fetch or decode failed.
    """
    hub = hub or ObservationsHub()
    bundle = hub.fetch_station(icao_code, timeout=timeout)
    report = bundle.metar.decoded
    if not isinstance(report, METARReport):
        return AirportWeatherSnapshot(
            icao_code=icao_code,
            is_real_data=False,
            status=bundle.metar.error or "NOT_DECODED",
            ceiling_height_ft=None,
            ceiling_category=None,
            visibility_m=None,
            present_weather_descriptions=(),
            raw_metar=bundle.metar.raw_text,
        )
    ceiling_ft = real_ceiling_height_ft(report)
    ceiling_category = classify_ceiling_category(ceiling_ft * _FT_TO_M) if ceiling_ft is not None else None
    return AirportWeatherSnapshot(
        icao_code=icao_code,
        is_real_data=True,
        status="OK",
        ceiling_height_ft=ceiling_ft,
        ceiling_category=ceiling_category,
        visibility_m=report.visibility_m,
        present_weather_descriptions=tuple(describe_present_weather_code(code) for code in report.present_weather),
        raw_metar=report.raw_text,
    )
