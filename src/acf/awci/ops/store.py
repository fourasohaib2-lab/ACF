"""
NetCDF4 cube per (domain, run): data/awci/{domain}/{YYYYMMDDHH}/{cube.nc, manifest.json}.
Written into {run}.tmp/ then renamed atomically. Float32, zlib level 4, NaN = missing.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

import netCDF4
import numpy as np
import xarray as xr

from acf.awci.ops.domains import Domain
from acf.awci.ops.engine import Profile
from acf.awci.ops.isa import flight_level
from acf.awci.ops.registry import LEVEL_LAYERS, SURFACE_LAYERS

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[4] / "data" / "awci"
LICENSE = "CC-BY-4.0"
ATTRIBUTION = "© ECMWF, CC-BY-4.0"
MODEL = "ECMWF IFS 0.25° Open Data"


def data_root() -> Path:
    return Path(os.environ.get("ACF_AWCI_DATA_DIR", DEFAULT_DATA_DIR))


def run_id(run: datetime) -> str:
    return f"{run:%Y%m%d%H}"


def _git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              check=True, cwd=Path(__file__).parent).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


class CubeWriter:
    def __init__(self, root: Path, domain: Domain, run: datetime, lats: np.ndarray, lons: np.ndarray,
                 levels_hpa: np.ndarray, steps: list[int], profile: Profile) -> None:
        self.final_dir = Path(root) / domain.name / run_id(run)
        self.tmp_dir = self.final_dir.with_name(self.final_dir.name + ".tmp")
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        self.tmp_dir.mkdir(parents=True)
        self.domain, self.run, self.steps, self.profile = domain, run, steps, profile
        self.levels_hpa = np.asarray(levels_hpa, dtype=float)
        self.nc = netCDF4.Dataset(self.tmp_dir / "cube.nc", "w", format="NETCDF4")
        self.nc.createDimension("step", len(steps))
        self.nc.createDimension("level", len(levels_hpa))
        self.nc.createDimension("lat", len(lats))
        self.nc.createDimension("lon", len(lons))
        for name, dims, values in (("step", ("step",), steps), ("level", ("level",), levels_hpa),
                                   ("lat", ("lat",), lats), ("lon", ("lon",), lons)):
            self.nc.createVariable(name, "f8", dims)[:] = np.asarray(values, dtype=float)
        nan = np.float32(np.nan)
        # Never-written cells (a missing step) read back as the NaN fill value - no explicit init needed.
        for name in LEVEL_LAYERS:
            self.nc.createVariable(name, "f4", ("step", "level", "lat", "lon"),
                                   chunksizes=(1, 1, len(lats), len(lons)), zlib=True, complevel=4,
                                   fill_value=nan)
        for name in SURFACE_LAYERS:
            self.nc.createVariable(name, "f4", ("step", "lat", "lon"), chunksizes=(1, len(lats), len(lons)),
                                   zlib=True, complevel=4, fill_value=nan)
        self.nc.createVariable("elevation", "f4", ("lat", "lon"), zlib=True, complevel=4, fill_value=nan)

    def write_step(self, step_index: int, layers: dict[str, np.ndarray], elevation: np.ndarray) -> None:
        for name in LEVEL_LAYERS:
            self.nc[name][step_index] = layers[name].astype(np.float32)
        for name in SURFACE_LAYERS:
            self.nc[name][step_index] = layers[name].astype(np.float32)
        self.nc["elevation"][:] = np.asarray(elevation, dtype=np.float32)

    def finalize(
        self, status: str, missing_steps: list[int], extra: dict[str, Any], force: bool = False
    ) -> dict[str, Any]:
        """Publish the cube. An existing `complete` run is never replaced by a less complete one unless
        `force`; the swap goes through `<run>.old` so readers never see the run missing."""
        self.nc.close()
        existing = self.final_dir / "manifest.json"
        if not force and status != "complete" and existing.exists():
            previous = json.loads(existing.read_text())
            if previous.get("status") == "complete":
                shutil.rmtree(self.tmp_dir, ignore_errors=True)
                return {**previous, "rejected_rerun_status": status, "rejected_rerun_missing_steps": missing_steps}
        manifest = {
            "run": run_id(self.run), "run_time": self.run.isoformat(), "domain": self.domain.name,
            "status": status, "steps": self.steps, "missing_steps": missing_steps,
            "valid_times": [(self.run + timedelta(hours=s)).isoformat() for s in self.steps],
            "levels_hpa": self.levels_hpa.tolist(),
            "flight_levels": [flight_level(p) for p in self.levels_hpa],
            "level_layers": list(LEVEL_LAYERS), "surface_layers": list(SURFACE_LAYERS),
            "profile": self.profile.name, "profile_version": self.profile.version,
            "model": MODEL, "license": LICENSE, "attribution": ATTRIBUTION, "acf_git_sha": _git_sha(), **extra,
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


def apply_retention(root: Path, domain: str, keep: int) -> list[str]:
    domain_dir = Path(root) / domain
    runs = sorted(p.name for p in domain_dir.iterdir() if p.is_dir() and p.name.isdigit()) if domain_dir.exists() else []
    removed = runs[: max(0, len(runs) - keep)]
    for name in removed:
        shutil.rmtree(domain_dir / name)
    return removed


@lru_cache(maxsize=16)
def _open(path: str, mtime: float) -> xr.Dataset:
    return xr.open_dataset(path, engine="netcdf4", cache=False)


_RUN_ID_RE = re.compile(r"^\d{10}$")


def _check_run_id(run: str) -> str:
    if not _RUN_ID_RE.fullmatch(run):
        raise ValueError(f"invalid run id {run!r} - expected YYYYMMDDHH")
    return run


class CubeStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else data_root()

    def runs(self, domain: str) -> list[dict[str, Any]]:
        domain_dir = self.root / domain
        if not domain_dir.exists():
            return []
        manifests = [json.loads((d / "manifest.json").read_text()) for d in domain_dir.iterdir()
                     if d.is_dir() and d.name.isdigit() and (d / "manifest.json").exists()]
        return sorted(manifests, key=lambda m: m["run"], reverse=True)

    def manifest(self, domain: str, run: str) -> dict[str, Any]:
        path = self.root / domain / _check_run_id(run) / "manifest.json"
        if not path.exists():
            raise FileNotFoundError(f"no run {run!r} for domain {domain!r}")
        return json.loads(path.read_text())

    def dataset(self, domain: str, run: str) -> xr.Dataset:
        path = self.root / domain / _check_run_id(run) / "cube.nc"
        if not path.exists():
            raise FileNotFoundError(f"no cube for {domain!r}/{run!r}")
        return _open(str(path), path.stat().st_mtime)
