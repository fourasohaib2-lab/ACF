"""
Regenerate tests/data/awci_ops: download the real ECMWF IFS Open Data messages
AWCI Web needs for run 2026-09-25 00Z, steps 0 and 3, crop them to 35-37N / 2-4E
with eccodes, and write a matching .index. Data: © ECMWF, CC-BY-4.0.
Usage: .venv/bin/python tools/awci/make_ops_fixture.py
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import eccodes
import numpy as np

from acf.awci.ops.source_ecmwf import UrllibFetcher, parse_index, select_entries, step_urls

OUT = Path(__file__).resolve().parents[2] / "tests" / "data" / "awci_ops"
RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)
BOX = (35.0, 37.0, 2.0, 4.0)  # south, north, west, east


def crop(message: bytes) -> bytes:
    handle = eccodes.codes_new_from_message(message)
    try:
        ni, nj = eccodes.codes_get(handle, "Ni"), eccodes.codes_get(handle, "Nj")
        values = eccodes.codes_get_values(handle).reshape(nj, ni)
        lats = 90.0 - 0.25 * np.arange(nj)
        lons = -180.0 + 0.25 * np.arange(ni)
        iy = np.where((lats >= BOX[0]) & (lats <= BOX[1]))[0]
        ix = np.where((lons >= BOX[2]) & (lons <= BOX[3]))[0]
        clone = eccodes.codes_clone(handle)
        for key, value in (("Ni", len(ix)), ("Nj", len(iy)),
                           ("latitudeOfFirstGridPointInDegrees", float(lats[iy[0]])),
                           ("latitudeOfLastGridPointInDegrees", float(lats[iy[-1]])),
                           ("longitudeOfFirstGridPointInDegrees", float(lons[ix[0]])),
                           ("longitudeOfLastGridPointInDegrees", float(lons[ix[-1]]))):
            eccodes.codes_set(clone, key, value)
        eccodes.codes_set_values(clone, values[np.ix_(iy, ix)].ravel())
        data = eccodes.codes_get_message(clone)
        eccodes.codes_release(clone)
        return data
    finally:
        eccodes.codes_release(handle)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fetcher = UrllibFetcher()
    for step in (0, 3):
        grib_url, index_url = step_urls(RUN, step)
        entries = select_entries(parse_index(fetcher.get_text(index_url)))
        stem = Path(grib_url).name.removesuffix(".grib2")
        offset, blobs, index_lines = 0, [], []
        for entry in entries:
            blob = crop(fetcher.get_range(grib_url, entry.offset, entry.length))
            line = {"param": entry.param, "levtype": entry.levtype, "_offset": offset, "_length": len(blob)}
            if entry.level is not None:
                line["levelist"] = str(entry.level)
            index_lines.append(json.dumps(line))
            blobs.append(blob)
            offset += len(blob)
        (OUT / f"{stem}.grib2").write_bytes(b"".join(blobs))
        (OUT / f"{stem}.index").write_text("\n".join(index_lines) + "\n")
        print(f"step {step}: {len(entries)} messages, {offset} bytes")


if __name__ == "__main__":
    main()
