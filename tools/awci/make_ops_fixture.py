"""
Regenerate an AWCI ops test fixture: download the real ECMWF IFS Open Data messages
AWCI Web needs (run 2026-09-25 00Z by default, steps 0 and 3), crop them with eccodes
and write a matching .index. Data: © ECMWF, CC-BY-4.0.
Usage:
    .venv/bin/python tools/awci/make_ops_fixture.py                       # dry: 35-37N / 2-4E
    .venv/bin/python tools/awci/make_ops_fixture.py --box 15 17 -20 -18 --out tests/data/awci_ops_wet
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import eccodes
import numpy as np

from acf.awci.ops.source_ecmwf import UrllibFetcher, parse_index, select_entries, step_urls

OUT = Path(__file__).resolve().parents[2] / "tests" / "data" / "awci_ops"
RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)
BOX = (35.0, 37.0, 2.0, 4.0)  # south, north, west, east


def crop(message: bytes, box: tuple[float, float, float, float] = BOX) -> bytes:
    handle = eccodes.codes_new_from_message(message)
    try:
        ni, nj = eccodes.codes_get(handle, "Ni"), eccodes.codes_get(handle, "Nj")
        values = eccodes.codes_get_values(handle).reshape(nj, ni)
        lats = 90.0 - 0.25 * np.arange(nj)
        lons = -180.0 + 0.25 * np.arange(ni)
        iy = np.where((lats >= box[0]) & (lats <= box[1]))[0]
        ix = np.where((lons >= box[2]) & (lons <= box[3]))[0]
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


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="regenerate a cropped real-IFS fixture")
    parser.add_argument("--run", default=f"{RUN:%Y%m%d%H}")
    parser.add_argument("--box", nargs=4, type=float, default=BOX, metavar=("S", "N", "W", "E"))
    parser.add_argument("--steps", default="0,3")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    run = datetime.strptime(args.run, "%Y%m%d%H").replace(tzinfo=UTC)
    out = args.out
    box = (args.box[0], args.box[1], args.box[2], args.box[3])
    out.mkdir(parents=True, exist_ok=True)
    fetcher = UrllibFetcher()
    for step in (int(s) for s in args.steps.split(",")):
        grib_url, index_url = step_urls(run, step)
        entries = select_entries(parse_index(fetcher.get_text(index_url)))
        stem = Path(grib_url).name.removesuffix(".grib2")
        offset, blobs, index_lines = 0, [], []
        for entry in entries:
            blob = crop(fetcher.get_range(grib_url, entry.offset, entry.length), box)
            line = {"param": entry.param, "levtype": entry.levtype, "_offset": offset, "_length": len(blob)}
            if entry.level is not None:
                line["levelist"] = str(entry.level)
            index_lines.append(json.dumps(line))
            blobs.append(blob)
            offset += len(blob)
        (out / f"{stem}.grib2").write_bytes(b"".join(blobs))
        (out / f"{stem}.index").write_text("\n".join(index_lines) + "\n")
        print(f"step {step}: {len(entries)} messages, {offset} bytes")


if __name__ == "__main__":
    main()
