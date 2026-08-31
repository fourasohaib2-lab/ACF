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

## 3. Governance and Standards
For detailed governance manuals, ADRs, and maturity matrices, consult [`docs/ACF_ARCHITECTURE_GOVERNANCE.md`](docs/ACF_ARCHITECTURE_GOVERNANCE.md).
