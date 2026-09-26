"""
Radiosonde verification route of AWCI Web (spec SP7 §5): `/soundings/verification?domain&run&model`.

Soundings are read from the observation store filled by `acf-awci-obs --soundings`; no request ever reaches the
University of Wyoming from here. Scores: acf.awci.ops.verify_sounding.
"""

from __future__ import annotations

import json
from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Request

from acf.awci.obs.store import ObsStore, parse_time
from acf.awci.ops.domains import Domain
from acf.awci.ops.store import CubeStore
from acf.awci.ops.verify_sounding import column_pairs, verify_soundings
from acf.web.awci_models import data_root, model_store

router = APIRouter()
RunId = Annotated[str, Query(pattern=r"^\d{10}$")]


@lru_cache(maxsize=16)
def _report(cube_root: str, obs_root: str, domain: Domain, run: str, cube_mtime: float, obs_mtime: float) -> str:
    cubes, store = CubeStore(Path(cube_root)), ObsStore(obs_root, domain.name)
    manifest = cubes.manifest(domain.name, run)
    times = [parse_time(t) for t in manifest["valid_times"]]
    soundings = store.soundings(times[0] - timedelta(minutes=1), times[-1] + timedelta(minutes=1))
    pairs, excluded = column_pairs(cubes.dataset(domain.name, run), manifest, soundings, domain)
    report = verify_soundings(pairs, excluded, manifest["levels_hpa"])
    report.update({"domain": domain.name, "run": run, "valid_from": manifest["valid_times"][0],
                   "valid_to": manifest["valid_times"][-1], "model_id": manifest.get("model_id", "ifs"),
                   "model": manifest.get("model", "ECMWF IFS 0.25°"),
                   "stations_known": len(store.sounding_stations())})
    return json.dumps(report)


@router.get("/soundings/verification")
def sounding_verification(request: Request, domain: str, run: RunId) -> dict[str, Any]:
    """Scores of the run's column (T, RH, wind, vertical shear, icing inputs) against radiosondes."""
    d = request.app.state.awci_domains.get(domain)
    if d is None:
        raise HTTPException(404, f"unknown domain {domain!r}")
    cubes = model_store(request)
    cube = cubes.root / d.name / run / "cube.nc"
    if not cube.exists():
        raise HTTPException(404, f"no run {run!r} for domain {domain!r}")
    store = ObsStore(data_root(request), d.name)
    report: dict[str, Any] = json.loads(_report(str(cubes.root), str(data_root(request)), d, run,
                                                cube.stat().st_mtime, store.mtime()))
    return report
