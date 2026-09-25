"""
Build the embedded AWCI Web basemap (web/awci/public/basemap/*.geojson) from Natural Earth 1:50m.

Downloads land, coastline and land boundary lines (public domain, github.com/nvkelso/natural-earth-vector),
clips them to the union of every configured domain plus a 10 degree margin, rounds coordinates to 3
decimals (about 100 m, far below the 0.25 degree model grid) and writes compact GeoJSON, so the
browser never needs an external tile server.

    .venv/bin/python tools/awci/make_basemap.py [--margin 10]
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from shapely.geometry import box, mapping, shape

from acf.awci.ops.domains import DEFAULT_DOMAINS_PATH, load_domains

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "web" / "awci" / "public" / "basemap"
SOURCE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/{}.geojson"
LAYERS = {"land": "ne_50m_land", "coastline": "ne_50m_coastline", "borders": "ne_50m_admin_0_boundary_lines_land"}


def _round(coords: Any) -> Any:
    if isinstance(coords, (int, float)):
        return round(float(coords), 3)
    return [_round(c) for c in coords]


def clip(collection: dict[str, Any], bounds: tuple[float, float, float, float]) -> dict[str, Any]:
    window = box(*bounds)
    features = []
    for feature in collection["features"]:
        geometry = shape(feature["geometry"]).intersection(window)
        if geometry.is_empty:
            continue
        geo = mapping(geometry)
        features.append({"type": "Feature", "properties": {},
                         "geometry": {"type": geo["type"], "coordinates": _round(geo["coordinates"])}})
    return {"type": "FeatureCollection", "features": features}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--margin", type=float, default=10.0)
    args = parser.parse_args(argv)
    domains = list(load_domains(DEFAULT_DOMAINS_PATH).values())
    bounds = (max(-180.0, min(d.west for d in domains) - args.margin), max(-90.0, min(d.south for d in domains) - args.margin),
              min(180.0, max(d.east for d in domains) + args.margin), min(90.0, max(d.north for d in domains) + args.margin))
    OUT.mkdir(parents=True, exist_ok=True)
    sizes = {}
    for name, source in LAYERS.items():
        with urllib.request.urlopen(SOURCE.format(source), timeout=120) as response:
            collection = json.load(response)
        text = json.dumps(clip(collection, bounds), separators=(",", ":"))
        (OUT / f"{name}.geojson").write_text(text)
        sizes[name] = len(text)
    (OUT / "NOTICE.md").write_text(
        "# Basemap\n\nNatural Earth 1:50m vector data (public domain, https://www.naturalearthdata.com/),\n"
        f"layers {', '.join(LAYERS.values())}, from github.com/nvkelso/natural-earth-vector,\n"
        f"clipped to lon {bounds[0]}..{bounds[2]}, lat {bounds[1]}..{bounds[3]} and rounded to 3 decimals on "
        f"{datetime.now(UTC).date().isoformat()} by tools/awci/make_basemap.py.\n")
    print({k: f"{v / 1024:.0f} KiB" for k, v in sizes.items()}, "bounds", bounds)


if __name__ == "__main__":
    main()
