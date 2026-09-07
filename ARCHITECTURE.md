# ACF System Architecture

## 1. Overview
The Atmospheric Complexity Framework (ACF) is built upon a layered, decoupled micro-modular architecture designed for extreme scientific rigor, real-time performance, and seamless high-performance computing (HPC) orchestration.

## 2. Core Architectural Pillars

```
+-------------------------------------------------------------------------+
|                  ESOC & UI Layer (acf.gui, acf.visualization)           |
+-------------------------------------------------------------------------+
|                  Digital Twin & AEOS Platform Layer                     |
|            (acf.aeos, acf.digital_twin, acf.intelligence)               |
+-------------------------------------------------------------------------+
|              Domain Science & Earth System Intelligence                 |
| (acf.science, acf.hydrology, acf.ocean, acf.aviation, acf.space_weather)|
+-------------------------------------------------------------------------+
|              NWP Model Runners & HPC Workflows Engine                   |
|          (acf.models, acf.surfex, acf.hpc_workflow, acf.hpc_connector)  |
+-------------------------------------------------------------------------+
|              Data Ingestion, Standard Catalogs & Post-Processing       |
|            (acf.data, acf.catalogs, acf.analysis, acf.verification)     |
+-------------------------------------------------------------------------+
|                        ACF Core Foundation                              |
|                          (acf.core, acf.model4d)                        |
+-------------------------------------------------------------------------+
```

### Pillar 1: Scientific Computing & Core Physics (`acf.core`, `acf.model4d`, `acf.science`)
- Rigorous SI units, coordinate transformations (Cartesian, Spherical, Pressure, Hybrid Sigma-Pressure).
- Full thermodynamic formulations (Bolton 1980, Clausius-Clapeyron, Virtual Potential Temperature).
- 4D field tensor abstractions, finite-difference spatial operators (advection, divergence, vorticity, laplacian).

### Pillar 2: Universal Ingestion & Parameter Catalogs (`acf.data`, `acf.catalogs`)
- Multi-format ingestion adapter hierarchy (NetCDF4, GRIB1/2, HDF5, GeoTIFF, BUFR, epygram FA/LFI).
- CF-compliant standard name registries, ECMWF GRIB tables, and WMO parameter mapping.

### Pillar 3: Model Runners & HPC Orchestration (`acf.models`, `acf.surfex`, `acf.hpc_workflow`, `acf.hpc_connector`)
- Complete lifecycle management for operational numerical models: AROME, ALADIN, ARPEGE, and SURFEX.
- Multi-cluster Slurm/PBS job management, environment discovery, stage automation, and async telemetry.

### Pillar 4: Earth Digital Twin & AEOS Platform (`acf.aeos`, `acf.digital_twin`, `acf.intelligence`)
- Event-driven micro-kernel architecture with event bus, task scheduler, and health monitoring.
- Multi-sphere earth system coupling: atmosphere-hydrology-ocean-cryosphere feedback loops.
- Explainable AI causal reasoning and autonomous meteorological decision support.

### Pillar 5: Earth System Operations Center (`acf.gui`, `acf.visualization`)
- Hardware-accelerated 2D/3D map canvas powered by PySide6 and Cartopy/Matplotlib.
- Volumetric isosurfaces, cross-sections, particle streamline animations, and real-time alerts dashboard.

## 3. Maturity & Scope Tiers

The 5 pillars above describe *where* a module sits logically. They do not
say whether it is actually finished. As of 2026-09-06 the codebase carries
~133k lines across 62 `src/acf/` submodules of very uneven maturity (from
`gui` at ~30k lines to two-file skeletons). To make "finished" a verifiable
claim rather than a declared one, every submodule is assigned exactly one
tier:

- **Tier F — Foundation.** Physical/mathematical bedrock. Must be
  fully audited, zero undisclosed stubs, tests green, before anything else
  is called done.
- **Tier C — Core.** The operational spine: ingestion, model execution,
  HPC, the desktop GUI. Required for a v1.0 release.
- **Tier E — Extended.** Real, in-scope domain/product features, audited
  to the same honesty bar, but not release-blocking individually.
- **Tier X — Experimental / out of v1.0 scope.** Kept in the repository
  (never deleted without an explicit request — see `AGENTS.md`), but
  explicitly *not* covered by the v1.0 "done" claim. Revisit post-v1.0.

| Tier | `src/acf/` submodules |
|---|---|
| **F** | `core`, `science`, `physics_guard`, `parameters`, `standards`, `validation`, `normalization`, `time`, `utils`, `earth_physics`, `io` |
| **C** | `data`, `catalog`, `catalogs`, `importers`, `geospatial`, `models`, `surfex`, `hpc_connector`, `hpc_workflow`, `simulation_engine`, `gui`, `visualization`, `maps`, `awci`, `jobs`, `storage` |
| **E** | `aviation`, `hydrology`, `ocean`, `geology`, `space_weather`, `climate`, `ai`, `ai_expert`, `intelligence`, `digital_twin`, `aeos`, `knowledge_platform`, `dashboard`, `web`, `api`, `monitoring`, `alerts`, `hazard_operations`, `release`, `verification`, `data_assimilation`, `forecast`, `events`, `connectors`, `master`, `workspace`, `reports`, `search`, `testing`, `plugins`, `animation` |
| **X** | `model4d`, `geoengineering`, `planetary`, `fire_weather`, `certification` |

Reclassification made unilaterally during the Tier F sweep (2026-09-06),
recorded here rather than asked about, per this project's standing
instruction to keep going without waiting for a check-in except on
destructive actions: **`model4d` moved from Tier F to Tier X.** Its own
module docstring (`src/acf/model4d/__init__.py`) already documents why,
verified by repeated `grep -rl "from acf.model4d"` sweeps across every
other `src/acf/` package: zero real callers anywhere. It is real,
tested, honestly-audited code — as of 2026-09-07, all 20
`physics/*_engine.py` files, the orchestrator, every
`operators/`/`interpolation/` file, AND all 131 remaining
non-`_engine.py` `physics/` files have been individually read (not a
sample — full coverage; see `docs/STATUS.md`) — kept in the repository
per `AGENTS.md`, but a module
nothing in the shipped product imports cannot honestly gate a v1.0
release the way `science`/`core`/`physics_guard` (which real code
throughout the codebase actually calls) do. Pillar 1 above still lists
it (`acf.core`, `acf.model4d`, `acf.science`) as a logical-architecture
statement, not a v1.0-readiness one — the two axes intentionally
disagree here, and that disagreement is the point of having both.

Known cleanup items surfaced by this tiering (tracked in `docs/STATUS.md`,
not resolved by this edit alone):
- ~~`catalog/` and `catalogs/` appear to duplicate the same
  responsibility~~ — investigated during the Tier C sweep (2026-09-06):
  not a duplication. `catalog/` (singular) is the real, load-bearing
  implementation (verified by grep to be what `acf.gui`/`acf.data`/
  `acf.importers` actually import); `catalogs/` (plural) is a small
  CF/ECMWF-specific extension whose own `catalog_manager.py` explicitly
  forwards to `catalog/`'s manager rather than reimplementing it. Both
  packages' docstrings now state this relationship explicitly. No
  consolidation needed — this item is closed.
- ~~`certification/` (the module, distinct from the archived `docs/`
  certificates) generates completion claims — it must itself be audited~~
  — audited during the Tier E sweep (2026-09-06): genuinely excellent.
  `CertificationEngine` composes only already-verified real components
  (`Dataset.validate()`/`PhysicsGuard`/`ModelSkillDatabase`/
  `Event.transition_to()` — the Data Contract, Physics Guard,
  Verification pipeline, and Event Engine, each independently audited
  elsewhere in this sweep), invents no new pass/fail logic of its own,
  and its own docstring explicitly distinguishes itself from the
  earlier, honestly-disclosed-as-unimplemented
  `ScientificCertificationEngine`. 16 tests passing. This item is closed.
- ~~`src/acf/resources/` is an empty directory~~ — corrected during the
  Tier E sweep (2026-09-06): not empty, this tiering's own earlier
  file-count only checked for `.py` files. It holds real reference data
  (`standards/cf/cf_standard_names.json`, `standards/ecmwf/parameters.
  json`). This item is closed.

A module counts as **done** only when all four hold, independent of any
document: (1) a `git log -- src/acf/<module>` entry tagged `audit(<module>)`
exists, (2) its tests are green, (3) no docstring claims a capability the
code doesn't have, (4) every import it uses is declared in `pyproject.toml`.
Live tracking: [`docs/STATUS.md`](docs/STATUS.md).

## 4. Governance and Standards
For detailed governance manuals, ADRs, and maturity matrices, consult [`docs/ACF_ARCHITECTURE_GOVERNANCE.md`](docs/ACF_ARCHITECTURE_GOVERNANCE.md). Historical sprint/release/certification documents that predate this tiering have been moved to [`docs/archive/`](docs/archive/README.md) — see that file for why.
