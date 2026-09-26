"""
Storage of IFS ENS results (spec SP5): data/awci/{domain}/ens/{run}/{cube.nc, manifest.json}.

Counts and valid-member numbers are exact integers (uint8); probabilities are derived on read (count / n).
Written to `<run>.tmp` then renamed, as the deterministic cubes (acf.awci.ops.store.CubeWriter).
"""

from __future__ import annotations

import json
import os
import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import netCDF4
import numpy as np
import xarray as xr

from acf.awci.ops.domains import Domain
from acf.awci.ops.ensemble import ENS_LEVEL_PRODUCTS, ENS_STATISTICS, ENS_SURFACE_PRODUCTS
from acf.awci.ops.isa import flight_level
from acf.awci.ops.store import _check_run_id, _git_sha, _open, data_root, run_id

MODEL = "ECMWF IFS ENS 0.25° Open Data (50 perturbed members)"
ATTRIBUTION = "© ECMWF, CC-BY-4.0 — IFS ENS"


def ens_dir(root: Path, domain: str) -> Path:
    return Path(root) / domain / "ens"


class EnsWriter:
    def __init__(self, root: Path, domain: Domain, run: datetime, lats: np.ndarray, lons: np.ndarray,
                 levels_hpa: np.ndarray, steps: list[int]) -> None:
        self.final_dir = ens_dir(root, domain.name) / run_id(run)
        self.tmp_dir = self.final_dir.with_name(self.final_dir.name + ".tmp")
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        self.tmp_dir.mkdir(parents=True)
        self.domain, self.run, self.steps = domain, run, steps
        self.levels_hpa = np.asarray(levels_hpa, dtype=float)
        nc = netCDF4.Dataset(self.tmp_dir / "cube.nc", "w", format="NETCDF4")
        for name, size in (("step", len(steps)), ("level", len(levels_hpa)), ("lat", len(lats)), ("lon", len(lons))):
            nc.createDimension(name, size)
        for name, values in (("step", steps), ("level", levels_hpa), ("lat", lats), ("lon", lons)):
            nc.createVariable(name, "f8", (name,))[:] = np.asarray(values, dtype=float)
        level_dims: tuple[str, ...] = ("step", "level", "lat", "lon")
        surface_dims: tuple[str, ...] = ("step", "lat", "lon")
        for names, dims in ((ENS_LEVEL_PRODUCTS, level_dims), (ENS_SURFACE_PRODUCTS, surface_dims)):
            for product in names:
                for suffix in ("count", "n"):
                    # no _FillValue: 0 is a real count, not missing data; zeros written up front so that a step
                    # never written reads back as n = 0 (no probability), never as a fill value
                    var = nc.createVariable(f"{product}_{suffix}", "u1", dims, zlib=True, complevel=4, fill_value=False)
                    var[:] = np.zeros(var.shape, np.uint8)
        for name in ENS_STATISTICS:
            nc.createVariable(name, "f4", level_dims, zlib=True, complevel=4, fill_value=np.float32(np.nan))
        self.nc = nc

    def write_step(self, step_index: int, result: dict[str, Any]) -> None:
        for product in (*ENS_LEVEL_PRODUCTS, *ENS_SURFACE_PRODUCTS):
            for suffix in ("count", "n"):
                self.nc[f"{product}_{suffix}"][step_index] = result[f"{product}_{suffix}"]
        for name in ENS_STATISTICS:
            self.nc[name][step_index] = result[name]

    def finalize(self, missing_steps: list[int], extra: dict[str, Any]) -> dict[str, Any]:
        self.nc.close()
        products = {p: {"dims": "level"} for p in ENS_LEVEL_PRODUCTS} | {p: {"dims": "surface"} for p in ENS_SURFACE_PRODUCTS}
        manifest = {
            "run": run_id(self.run), "run_time": self.run.isoformat(), "domain": self.domain.name,
            "ingested_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "status": "partial" if missing_steps else "complete", "steps": self.steps, "missing_steps": missing_steps,
            "valid_times": [(self.run + timedelta(hours=s)).isoformat() for s in self.steps],
            "levels_hpa": self.levels_hpa.tolist(), "flight_levels": [flight_level(p) for p in self.levels_hpa],
            "products": products, "statistics": list(ENS_STATISTICS), "model": MODEL, "license": "CC-BY-4.0",
            "attribution": ATTRIBUTION, "acf_git_sha": _git_sha(), **extra,
        }
        (self.tmp_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
        old_dir = self.final_dir.with_name(self.final_dir.name + ".old")
        shutil.rmtree(old_dir, ignore_errors=True)
        if self.final_dir.exists():
            os.replace(self.final_dir, old_dir)
        os.replace(self.tmp_dir, self.final_dir)
        shutil.rmtree(old_dir, ignore_errors=True)
        return manifest

    def abort(self) -> None:
        if self.nc.isopen():
            self.nc.close()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)


def apply_ens_retention(root: Path, domain: str, keep: int | None) -> list[str]:
    """Keep the `keep` most recent ENS runs; None keeps them all (age-based retention instead)."""
    if keep is None:
        return []
    folder = ens_dir(root, domain)
    runs = sorted(p.name for p in folder.iterdir() if p.is_dir() and p.name.isdigit()) if folder.exists() else []
    removed = runs[:-keep] if keep > 0 else runs
    for name in removed:
        shutil.rmtree(folder / name, ignore_errors=True)
    return removed


class EnsStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else data_root()

    def runs(self, domain: str) -> list[dict[str, Any]]:
        folder = ens_dir(self.root, domain)
        if not folder.exists():
            return []
        manifests = [json.loads((d / "manifest.json").read_text()) for d in folder.iterdir()
                     if d.is_dir() and d.name.isdigit() and (d / "manifest.json").exists()]
        return sorted(manifests, key=lambda m: m["run"], reverse=True)

    def manifest(self, domain: str, run: str) -> dict[str, Any]:
        path = ens_dir(self.root, domain) / _check_run_id(run) / "manifest.json"
        if not path.exists():
            raise FileNotFoundError(f"no ENS run {run!r} for domain {domain!r}")
        return dict(json.loads(path.read_text()))

    def dataset(self, domain: str, run: str) -> xr.Dataset:
        path = ens_dir(self.root, domain) / _check_run_id(run) / "cube.nc"
        if not path.exists():
            raise FileNotFoundError(f"no ENS cube for {domain!r}/{run!r}")
        return _open(str(path), path.stat().st_mtime)  # serialised first opening (see acf.awci.ops.store._open)
