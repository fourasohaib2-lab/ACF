"""Configured AWCI Web domains (config/awci/domains.json). Antimeridian-crossing boxes are not supported in V1."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

DEFAULT_DOMAINS_PATH = Path(__file__).resolve().parents[4] / "config" / "awci" / "domains.json"


@dataclass(frozen=True)
class Domain:
    name: str
    label: str
    south: float
    north: float
    west: float
    east: float
    default: bool = False

    def crop_indices(self, lats: np.ndarray, lons: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        lats, lons = np.asarray(lats), np.asarray(lons)
        iy = np.where((lats >= self.south - 1e-9) & (lats <= self.north + 1e-9))[0]
        ix = np.where((lons >= self.west - 1e-9) & (lons <= self.east + 1e-9))[0]
        return iy, ix

    def contains(self, lat: float, lon: float) -> bool:
        return self.south <= lat <= self.north and self.west <= lon <= self.east


def load_domains(path: Path | str = DEFAULT_DOMAINS_PATH) -> dict[str, Domain]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    domains: dict[str, Domain] = {}
    for raw in payload["domains"]:
        domain = Domain(
            name=str(raw["name"]), label=str(raw["label"]),
            south=float(raw["south"]), north=float(raw["north"]),
            west=float(raw["west"]), east=float(raw["east"]), default=bool(raw.get("default", False)),
        )
        if not (-90.0 <= domain.south < domain.north <= 90.0):
            raise ValueError(f"domain {domain.name!r}: need -90 <= south < north <= 90")
        if not (-180.0 <= domain.west < domain.east < 180.0):
            raise ValueError(f"domain {domain.name!r}: need -180 <= west < east < 180 (no antimeridian crossing)")
        if domain.name in domains:
            raise ValueError(f"duplicate domain name {domain.name!r}")
        domains[domain.name] = domain
    if sum(d.default for d in domains.values()) != 1:
        raise ValueError("exactly one domain must have default: true")
    return domains
