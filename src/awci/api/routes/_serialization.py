"""
Atmospheric Complexity Framework (ACF)

AWCI API - Shared Serialization Helper

Real, generic dataclass→JSON-safe-dict conversion shared by every
route module in this package - the same private-helper convention
``acf.web.routers._solver_guard`` already established for its own
FastAPI routers. Every AWCI domain object this API returns
(``RunwayWindAssessment``, ``AirportWeatherSnapshot``,
``RouteWeatherBriefing``, ``AviationReport``, ...) is already a real,
frozen dataclass - this module never invents new response shapes, it
only makes the real ones JSON-serializable (``dataclasses.asdict()``
does not handle ``datetime``, so this adds that one real conversion).
"""

from __future__ import annotations

import dataclasses
from datetime import datetime
from typing import Any


def to_json_safe(value: Any) -> Any:
    """Real recursive conversion - dataclasses become dicts,
    ``datetime`` becomes its ISO 8601 string, tuples/lists/dicts are
    walked recursively, everything else is returned unchanged (already
    JSON-safe: str/float/int/bool/None)."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {field.name: to_json_safe(getattr(value, field.name)) for field in dataclasses.fields(value)}
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: to_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json_safe(item) for item in value]
    return value
