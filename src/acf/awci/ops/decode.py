"""
GRIB2 message bytes -> cropped NumPy arrays per domain (eccodes, no cfgrib).

Grid geometry is read from each message (Ni, Nj, first-point lat/lon, increments,
jScansPositively), longitudes are wrapped to [-180, 180) and latitudes returned
ascending. Missing values (bitmap) become NaN.
"""

from __future__ import annotations

from dataclasses import dataclass

import eccodes
import numpy as np

from acf.awci.ops.domains import Domain
from acf.awci.ops.source_ecmwf import PL_LEVELS, PL_PARAMS, SFC_PARAMS


@dataclass
class StepFields:
    lats: np.ndarray
    lons: np.ndarray
    levels_hpa: np.ndarray
    pl: dict[str, np.ndarray]
    sfc: dict[str, np.ndarray]


def _read(message: bytes) -> tuple[str, int | None, np.ndarray, np.ndarray, np.ndarray]:
    handle = eccodes.codes_new_from_message(message)
    try:
        get = lambda key: eccodes.codes_get(handle, key)  # noqa: E731
        ni, nj = get("Ni"), get("Nj")
        di, dj = get("iDirectionIncrementInDegrees"), get("jDirectionIncrementInDegrees")
        lat0, lon0 = get("latitudeOfFirstGridPointInDegrees"), get("longitudeOfFirstGridPointInDegrees")
        lats = lat0 + (dj if get("jScansPositively") else -dj) * np.arange(nj)
        lons = (lon0 + di * np.arange(ni) + 180.0) % 360.0 - 180.0
        values = eccodes.codes_get_values(handle).astype(float).reshape(nj, ni)
        if get("bitmapPresent"):
            values[values == get("missingValue")] = np.nan
        level = int(get("level")) if get("typeOfLevel") == "isobaricInhPa" else None
        return str(get("shortName")), level, lats, lons, values
    finally:
        eccodes.codes_release(handle)


def decode_messages(messages: list[bytes], domains: list[Domain]) -> dict[str, StepFields]:
    decoded: dict[tuple[str, int | None], np.ndarray] = {}
    lats = lons = None
    for message in messages:
        name, level, m_lats, m_lons, values = _read(message)
        lat_order = np.argsort(m_lats)
        lon_order = np.argsort(m_lons)
        if lats is None:
            lats, lons = m_lats[lat_order], m_lons[lon_order]
        decoded[(name, level)] = values[np.ix_(lat_order, lon_order)]
    wanted = [(p, lev) for p in PL_PARAMS for lev in PL_LEVELS] + [(p, None) for p in SFC_PARAMS]
    missing = [key for key in wanted if key not in decoded]
    if missing or lats is None or lons is None:
        raise ValueError(f"missing GRIB messages: {missing}")
    out: dict[str, StepFields] = {}
    for domain in domains:
        iy, ix = domain.crop_indices(lats, lons)
        sub = lambda arr: arr[np.ix_(iy, ix)]  # noqa: E731
        out[domain.name] = StepFields(
            lats=lats[iy],
            lons=lons[ix],
            levels_hpa=np.asarray(PL_LEVELS, dtype=float),
            pl={p: np.stack([sub(decoded[(p, lev)]) for lev in PL_LEVELS]) for p in PL_PARAMS},
            sfc={p: sub(decoded[(p, None)]) for p in SFC_PARAMS},
        )
    return out
