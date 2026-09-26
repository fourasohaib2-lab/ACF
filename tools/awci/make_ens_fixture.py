"""
Regenerate the AWCI ENS test fixture: real ECMWF IFS ENS messages (enfo, perturbed members) the pipeline
needs, for a few members and steps, cropped with eccodes, with a matching .index that keeps "number".
Data: © ECMWF, CC-BY-4.0.

    .venv/bin/python tools/awci/make_ens_fixture.py   # run 2026-09-26 00Z, members 1-4, steps 0,6, 35-37N / 2-4E
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from make_ops_fixture import BOX, crop  # noqa: E402

from acf.awci.ops.source_ecmwf import UrllibFetcher, ens_step_urls, parse_index, select_entries  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "tests" / "data" / "awci_ens"
RUN = datetime(2026, 9, 26, 0, tzinfo=UTC)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="regenerate a cropped real IFS ENS fixture")
    parser.add_argument("--run", default=f"{RUN:%Y%m%d%H}")
    parser.add_argument("--members", default="1,2,3,4")
    parser.add_argument("--steps", default="0,6")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    run = datetime.strptime(args.run, "%Y%m%d%H").replace(tzinfo=UTC)
    args.out.mkdir(parents=True, exist_ok=True)
    fetcher = UrllibFetcher()
    for step in (int(s) for s in args.steps.split(",")):
        grib_url, index_url = ens_step_urls(run, step)
        entries = parse_index(fetcher.get_text(index_url))
        chosen = [e for m in (int(x) for x in args.members.split(",")) for e in select_entries(entries, member=m)]
        with ThreadPoolExecutor(12) as pool:  # downloads in parallel; eccodes is not thread-safe: crop sequentially
            raw = list(pool.map(lambda e: fetcher.get_range(grib_url, e.offset, e.length), chosen))
        blobs = [crop(message, BOX) for message in raw]
        offset, lines = 0, []
        for entry, blob in zip(chosen, blobs):
            line = {"param": entry.param, "levtype": entry.levtype, "number": str(entry.number), "type": "pf",
                    "_offset": offset, "_length": len(blob)}
            if entry.level is not None:
                line["levelist"] = str(entry.level)
            lines.append(json.dumps(line))
            offset += len(blob)
        stem = Path(grib_url).name.removesuffix(".grib2")
        (args.out / f"{stem}.grib2").write_bytes(b"".join(blobs))
        (args.out / f"{stem}.index").write_text("\n".join(lines) + "\n")
        print(f"step {step}: {len(chosen)} messages, {offset} bytes")


if __name__ == "__main__":
    main()
