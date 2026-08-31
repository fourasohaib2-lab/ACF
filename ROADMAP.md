# ACF Roadmap

## Current State (verified August 2026)
- Core scientific foundation (thermodynamics, mathematics, model4d, encyclopedia) is implemented and compiles cleanly across all 1,300 `src/acf` Python files.
- Independently re-run test suite: **1,922 passed / 12 failed / 45 files uncollectable** (uncollectable files need optional dependencies — cartopy, PySide6, xarray, paramiko — not the result of broken logic). See README.md "Verified Status" for detail.
- NWP workflow engines for AROME, ALADIN, ARPEGE, and SURFEX exist as adapters/ingestion code; full operational orchestration (multi-cluster failover, live assimilation feeds) is not yet in place.
- ESOC GUI and AWCI dashboard exist and run; broader real-time HPC/data-assimilation/satellite/radar integration described in `docs/ACF_Vision_1.0.md` is still largely aspirational — see the project's own module-maturity classification (LEVEL 0 absent → LEVEL 4 operationally integrated) before treating any module as "done."

Earlier versions of this roadmap and several `docs/` release certificates stated "Version 1.0.0-LTS (Current)" with "100% passing coverage across 2,100+ tests" and "GESOP v1.0 CERTIFIED." Those claims did not specify an environment or link to a reproducible run, and could not be reproduced as stated during the August 2026 audit. This file has been corrected to reflect only verified, reproducible results; treat any other completion claim in this repository as aspirational until it is backed by a run someone can repeat.

## Near-Term Priorities
- Declare `paramiko` in `requirements.txt` (used directly by `hpc_connector/ssh_connector.py` but previously undeclared) — done.
- Guard optional-dependency imports (`GRIBReader`, `NetCDFReader`) in `acf.importers/__init__.py` so a missing `xarray`/`cfgrib` install doesn't break unrelated imports — done.
- Split `pyproject.toml` dependencies into a lean "core" set (numpy/scipy/pandas/etc., needed for the science/model4d/diagnostics layers) and clearly-marked optional extras (GUI: PySide6; geospatial: cartopy/pyproj/shapely/rasterio; formats: cfgrib/eccodes/netCDF4/xarray; HPC: paramiko) so contributors can install only what a given task needs.
- Reconcile the ~150 auto-generated "certificate"/"sprint report" documents under `docs/` with the actual verified state, or clearly relabel them as historical/aspirational artifacts rather than current status.

## Longer-Term (per ACF_Vision_1.0.md)
- Real-time satellite/radar assimilation, GPU-accelerated solvers, multi-cluster HPC orchestration, and full digital-twin synchronization remain future milestones, not current capabilities.
