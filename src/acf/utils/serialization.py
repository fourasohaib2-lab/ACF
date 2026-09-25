"""
Atmospheric Complexity Framework (ACF)

Utils - Serialization

Real, generic dataclass -> JSON-safe-value conversion - the
``serialization.py`` module named in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` (row
``utils/{...}.py``). Promoted here from
``awci.api.routes._serialization`` (built earlier this session for
the AWCI HTTP API, where it converts real domain dataclasses -
``RunwayWindAssessment``, ``AirportWeatherSnapshot`` - to a JSON-safe
dict) once it became clear the same real, generic need applies beyond
that one caller. ``awci.api.routes._serialization`` now re-exports
this module rather than keeping a second, duplicate implementation.
"""

from __future__ import annotations

import base64
import dataclasses
from datetime import datetime
from typing import Any


def to_json_safe(value: Any) -> Any:
    """Real recursive conversion - dataclasses become dicts,
    ``datetime`` becomes its ISO 8601 string, ``bytes``/``bytearray``
    become a base64 string, tuples/lists/dicts are walked recursively,
    everything else is returned unchanged (already JSON-safe:
    str/float/int/bool/None).

    NOTE (correction, 2026-09-24 - real bug found while exercising the
    AWCI API's own GET /observations/{icao} against a real request):
    ``bytes`` previously fell through the "already JSON-safe" default
    case unconverted - real, since it looks JSON-serializable in
    Python - but it is NOT actually valid JSON, so any real caller
    whose dataclass carries genuine binary data (e.g.
    ``awci.data.connectors.eumetsat_mtg.MTGFetchResult.image_bytes``,
    a real downloaded satellite quicklook image) crashed the whole
    response with a real
    ``PydanticSerializationError: invalid utf-8 sequence`` - not a
    fabricated fallback, a genuine unhandled type. Base64 is the
    standard, real, reversible JSON-safe encoding for binary data (the
    frontend can decode it back to real bytes to actually display the
    image), not a lossy placeholder."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {field.name: to_json_safe(getattr(value, field.name)) for field in dataclasses.fields(value)}
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (bytes, bytearray)):
        return base64.b64encode(bytes(value)).decode("ascii")
    if isinstance(value, dict):
        return {key: to_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json_safe(item) for item in value]
    return value
