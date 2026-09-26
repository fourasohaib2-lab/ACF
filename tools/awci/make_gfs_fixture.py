"""
Regenerate the AWCI GFS test fixture: download the real NOAA GFS 0.25° messages AWCI needs (run 2026-09-25 00Z,
steps 0, 3 and 6 by default), crop them with eccodes to the test box and write a matching wgrib2-style .idx.
Data: NOAA/NCEP GFS, public domain.

    .venv/bin/python tools/awci/make_gfs_fixture.py            # 35-37N / 2-4E -> tests/data/awci_gfs
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

import eccodes
import numpy as np

from acf.awci.ops.source_ecmwf import UrllibFetcher
from acf.awci.ops.source_gfs import gfs_step_urls, parse_gfs_index, select_gfs_entries

OUT = Path(__file__).resolve().parents[2] / "tests" / "data" / "awci_gfs"
RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)
BOX = (35.0, 37.0, 2.0, 4.0)  # south, north, west, east (degrees east, as on the GFS 0-360 grid)


def crop(message: bytes, box: tuple[float, float, float, float] = BOX) -> bytes:
    """Crop one GFS message (north-to-south rows, longitudes 0-359.75) to the box, keeping its encoding."""
    handle = eccodes.codes_new_from_message(message)
    try:
        get = lambda key: eccodes.codes_get(handle, key)  # noqa: E731
        ni, nj = get("Ni"), get("Nj")
        values = eccodes.codes_get_values(handle).reshape(nj, ni)
        lats = get("latitudeOfFirstGridPointInDegrees") - get("jDirectionIncrementInDegrees") * np.arange(nj)
        lons = get("longitudeOfFirstGridPointInDegrees") + get("iDirectionIncrementInDegrees") * np.arange(ni)
        iy = np.where((lats >= box[0] - 1e-6) & (lats <= box[1] + 1e-6))[0]
        ix = np.where((lons >= box[2] - 1e-6) & (lons <= box[3] + 1e-6))[0]
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
        return bytes(data)
    finally:
        eccodes.codes_release(handle)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="regenerate the cropped real-GFS fixture")
    parser.add_argument("--run", default=f"{RUN:%Y%m%d%H}")
    parser.add_argument("--steps", default="0,3,6")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    run = datetime.strptime(args.run, "%Y%m%d%H").replace(tzinfo=UTC)
    args.out.mkdir(parents=True, exist_ok=True)
    fetcher = UrllibFetcher()
    for step in (int(s) for s in args.steps.split(",")):
        grib_url, index_url = gfs_step_urls(run, step)
        chosen = select_gfs_entries(parse_gfs_index(fetcher.get_text(index_url)), step)
        offset, blobs, lines = 0, [], []
        for n, entry in enumerate(chosen.values(), start=1):
            blob = crop(fetcher.get_range(grib_url, entry.offset, entry.length or 0))
            lines.append(f"{n}:{offset}:d={run:%Y%m%d%H}:{entry.var}:{entry.level}:{entry.time}:")
            blobs.append(blob)
            offset += len(blob)
        lines.append(f"{len(chosen) + 1}:{offset}:d={run:%Y%m%d%H}:END:fixture end:{step} hour fcst:")  # closes the last length
        name = Path(grib_url).name
        (args.out / name).write_bytes(b"".join(blobs))
        (args.out / f"{name}.idx").write_text("\n".join(lines) + "\n")
        print(f"step {step}: {len(chosen)} messages, {offset} bytes")


if __name__ == "__main__":
    main()
