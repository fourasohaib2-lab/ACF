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

## ✅ Verified Status (updated 2 September 2026 — see `ROADMAP.md` for the full history)

The `src/acf` tree (1,345 Python files) compiles cleanly (`python -m compileall src`, 0 errors). Running the full test suite in this repo's own dev environment gives **2895 passed / 0 failed**, stable across repeated runs; `ruff check` and `mypy src` are both clean. The August-2026 audit's original numbers (1,922 passed / 12 failed / 45 uncollectable) are superseded — the 12 failures and the import-order issue behind the 45 uncollectable files were fixed, and the "Physics Guard" sweep documented in `docs/ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md` since then removed fabricated data across dozens of modules, built a real FastAPI/WebSocket dashboard, real CI/CD forecast automation, a real trained FNO surrogate, and a fully real Complexity Engine (2D/3D/4D fields + dashboard — `docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md`). `pyproject.toml`'s dependencies are now split into a lean core (`numpy`, `scipy`, `PyYAML`) plus optional extras (`gui`, `geospatial`, `formats`, `science`, `hpc`, `web`, `ai`) — verified with a real fresh-venv install, not assumed (see `ROADMAP.md`). This is a solid, verifiable, reproducible pass rate — but it is still **not** the "100% of 2,100+ tests, fully certified v1.0" state that some documents under `docs/` (release certificates, LTS reports) claim without stating the environment or dependency set those numbers assumed. Treat any completion claim in `docs/`'s older certificate/report files as aspirational until it links to a reproducible run — `ROADMAP.md`'s "Near-Term Priorities" tracks reconciling those documents.

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

Complete technical documentation, architecture decision records (ADRs), and sprint specifications are available in the [`docs/`](docs/) directory:
- **[Complete Technical Documentation](docs/ACF_V1_0_COMPLETE_TECHNICAL_DOCUMENTATION.pdf)**
- **[Architecture Governance](docs/ACF_ARCHITECTURE_GOVERNANCE.md)**
- **[Scientific Reference Guide](docs/ACF_SCIENTIFIC_REFERENCE.md)**
- **[Operational Manual](docs/ACF_OPERATIONAL_MANUAL.md)**

Note: several documents in `docs/` (release certificates, "CERTIFIED" reports) were generated automatically and assert completion without a reproducible test run backing them. See the "Verified Status" section above for numbers that were actually re-run and checked.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
