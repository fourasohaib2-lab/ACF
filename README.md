# Atmospheric Complexity Framework (ACF)

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status: Active Development](https://img.shields.io/badge/Status-active--development-yellow.svg)]()

The **Atmospheric Complexity Framework (ACF)** is an Earth System and Meteorological Computing Platform in active development, targeting operational numerical weather prediction (NWP), atmospheric physics modeling, multi-sensor data assimilation, and digital twin simulation. See `docs/ACF_Vision_1.0.md` for the full target vision and the project's own maturity roadmap for what is built versus planned.

---

## 🌟 Key Capabilities

- **Earth System Core Engines**: High-precision thermodynamics, dynamics, turbulence closures, radiation budgets, cloud microphysics, and chemistry coupling.
- **NWP Model Support**: Native interfaces and automated workflow engines for AROME, ALADIN, ARPEGE, and SURFEX modeling systems.
- **Universal Data Ingestion**: Formats supported include GRIB1/GRIB2 (via eccodes/cfgrib), NetCDF4, HDF5, GeoTIFF/Raster, Shapefile, BUFR, and FA/LFI (epygram).
- **Meteorological Knowledge Base**: Comprehensive physical encyclopedia, WMO cloud taxonomy, instability indices (CAPE, CIN, Lifted Index, K-Index, SWEAT), and severe weather diagnostic engines.
- **Atmospheric Weather Complexity Index (AWCI)**: Multi-factor composite complexity diagnostic calculating dynamic, thermodynamic, convective, microphysical, topographic, and temporal complexity scores.
- **Earth System Operations Center (ESOC) GUI**: High-performance Qt/PySide6 visualization platform with interactive 2D/3D map rendering, cross-sections, streamlines, and real-time HPC monitoring.
- **HPC Cluster Integration**: Slurm and PBS/Torque workload management, remote execution over SSH/SFTP, environment management, and job lifecycle monitoring.

---

## ✅ Verified Status (updated 6 September 2026 — see [`docs/STATUS.md`](docs/STATUS.md) for the live, authoritative tracking)

The `src/acf` tree compiles cleanly and the full test suite gives **4578 passed / 0 failed**, stable across repeated runs (re-confirmed the same day after the changes below, not a stale number carried forward). Since the 2 September status previously recorded here, the project went through a systematic, module-by-module honesty audit rather than another self-issued completion report: [`ARCHITECTURE.md`](ARCHITECTURE.md) §3 now classifies every `src/acf/` submodule into a maturity tier (Foundation/Core/Extended/Experimental), and [`docs/STATUS.md`](docs/STATUS.md) tracks, per module, whether it has (1) a dated audit commit, (2) green tests, (3) no known docstring surclaim, and (4) declared dependencies — the only four criteria that make "done" a checkable claim instead of a declared one. All 58 modules in the Foundation+Core+Extended scope, plus every named Experimental-tier module, have been through this audit as of this date. Real findings from that audit include several fabricated "certified"/"production-ready"/"integrated" status claims removed from live code (not just from `docs/`'s prose - see `docs/STATUS.md` for specifics), a real user-reported bug (launching the app opened several independent, uncoordinated windows) traced to both a missing single-instance guard and orphaned demo scripts at the repo root, and a second real bug found afterward by an end-to-end toolbar smoke-test (not a code read): 3 of the 9 real per-module AWCI fields the app computes were being silently discarded before ever reaching the map. All fixed and covered by new tests the same day.

`docs/` still contains ~185 historical sprint/release/"CERTIFIED" documents from before this discipline was in place - archived under [`docs/archive/`](docs/archive/README.md) rather than deleted, explicitly not to be read as current status. Treat any completion claim outside `ARCHITECTURE.md`/`docs/STATUS.md` as historical unless it links to a reproducible run.

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/fourasohaib2-lab/ACF.git
cd ACF

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the package in editable mode.
# `pip install -e .` alone installs only the lean core (numpy, scipy,
# PyYAML) - enough for the science/model4d/earth_physics/
# data_assimilation layers, but not the GUI, maps, HPC connectivity,
# web dashboard or FNO surrogate this README describes above. For the
# full feature set, install the extras (see pyproject.toml's
# [project.optional-dependencies] for what each one covers):
pip install -e ".[all]"

# Or pick only what you need, e.g. GUI + geospatial:
#   pip install -e ".[gui,geospatial]"
```

### Running Tests

```bash
pytest
```

### Static Analysis & Linting

```bash
ruff check .
mypy src
```

### Launching the ESOC GUI

```bash
acf-gui
```

---

## 📂 Architecture Overview

The tree below is illustrative, not the complete/authoritative module
list - see [`ARCHITECTURE.md`](ARCHITECTURE.md) §3 for every `src/acf/`
submodule classified by maturity tier (e.g. `awci/`, the project's
flagship complexity-index calculator, isn't shown below but is
extensively covered there and in [`docs/STATUS.md`](docs/STATUS.md)).

```
src/acf/
├── aeos/             # Atmospheric & Earth Operating System kernel and services
├── ai/               # Physics-informed AI, neural forecast, ensemble uncertainty
├── analysis/         # Meteorological post-processing and diagnostic analysis
├── aviation/         # ICAO routing, hazards, SIGMET/AIRMET, aerodrome tools
├── catalogs/         # Parameter dictionaries, CF standards, ECMWF/WMO tables
├── climate/          # Earth system projections, reanalysis, climate indices
├── connectors/       # High-throughput data connectors and protocol adapters
├── core/             # Fundamental parameter, unit, and coordinate system abstractions
├── data/             # Universal reader, format adapters, and preprocessing pipelines
├── digital_twin/     # Earth system coupling, knowledge graph, and scenarios
├── gui/              # ESOC UI, map canvas, GIS rendering, and dashboard widgets
├── hpc_connector/    # Slurm/PBS workload scheduling and remote task execution
├── hpc_workflow/     # Forecast cycle pipelines and model runner orchestration
├── hydrology/        # Drought, runoff, flood routing, and soil moisture coupling
├── intelligence/     # Causal reasoning, anomaly detection, decision support
├── master/           # Module manifest, system registry, and maturity manager
├── model4d/          # 4D atmospheric physics operators, advection, and volume grids
├── models/           # NWP forecast configurations and runner interfaces
├── ocean/            # Waves, oceanography, cyclones, and marine coupling
├── science/          # Physics encyclopedia, thermodynamic equations, cloud physics
├── space_weather/    # Solar wind, magnetosphere, ionosphere, and GNSS alerts
├── surfex/           # Surface-atmosphere exchange and physiography integration
├── verification/     # NWP verification metrics (RMSE, ETS, POD, FAR, ROC)
└── visualization/    # 3D volume explorer, particle streamlines, and shaders
```

---

## 📚 Documentation

Start here, the two living, currently-maintained sources of truth:
- **[Architecture & Maturity Tiers](ARCHITECTURE.md)** — the 5-pillar logical architecture plus the Foundation/Core/Extended/Experimental tiering that defines what "done" means.
- **[Live Status Tracking](docs/STATUS.md)** — per-module audit checklist, updated as work happens, not after the fact.

Governance manuals, ADRs, and technical specifications live in [`docs/`](docs/):
- **[Complete Technical Documentation](docs/ACF_V1_0_COMPLETE_TECHNICAL_DOCUMENTATION.pdf)**
- **[Architecture Governance](docs/ACF_ARCHITECTURE_GOVERNANCE.md)**
- **[Scientific Reference Guide](docs/ACF_SCIENTIFIC_REFERENCE.md)**
- **[Operational Manual](docs/ACF_OPERATIONAL_MANUAL.md)**

`docs/archive/` holds ~185 historical sprint/release/"CERTIFIED" documents that were generated automatically and asserted completion without a reproducible test run backing them - kept for history, explicitly superseded by the two living sources above, not deleted. See [`docs/archive/README.md`](docs/archive/README.md) for why.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
