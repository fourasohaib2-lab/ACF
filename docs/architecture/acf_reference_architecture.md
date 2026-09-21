# ACF Reference Architecture

**Status: reference/target architecture, adopted 2026-09-21 at explicit user
request, superseding every ACF architecture discussion before it.**

This document is a faithful transcription (French source preserved where the
original used French terms, translated where it aids clarity) of the
architecture the user provided as the two files `acf.odt`. It supersedes any
other ACF architecture description in this repository's history. It is a
**target/blueprint**, not a description of the current `src/acf/` tree — see
[`acf_awci_architecture_gap_analysis.md`](acf_awci_architecture_gap_analysis.md)
for how the existing code maps onto it.

ESOC is explicitly and permanently excluded from this architecture (see
§"ESOC removal" below) — this is consistent with, and predates in intent,
the actual removal of `src/acf/gui/esoc/` from this codebase on 2026-09-21
(see `docs/STATUS.md`).

## 1. Full historical tree (L0 → L4)

```
ACF/
│
├── src/
│   └── acf/
│       │
│       ├── LAYER 0 — FOUNDATION
│       │   ├── core/
│       │   └── utils/
│       │
│       ├── LAYER 1 — SCIENTIFIC FORMULATIONS & STANDARDS
│       │   ├── science/
│       │   ├── parameters/
│       │   ├── standards/
│       │   └── catalog/
│       │
│       ├── LAYER 2 — DATA & SPATIO-TEMPORAL CORE
│       │   ├── data/
│       │   ├── io/
│       │   ├── model4d/
│       │   └── workspace/
│       │
│       ├── LAYER 3 — DOMAIN & HIGH-LEVEL ENGINES
│       │   ├── maps/
│       │   ├── visualization/
│       │   ├── models/
│       │   ├── ai/
│       │   └── awci/            # historical only — see "AWCI separation" below
│       │
│       └── LAYER 4 — PRESENTATION & APPLICATIONS
│           ├── gui/
│           ├── dashboard/
│           ├── api/
│           ├── alerts/
│           └── reports/
│
├── tests/
├── docs/
├── resources/
├── scripts/
├── examples/
├── tools/
├── assets/
└── configs/
```

## 2. LAYER 0 — Foundation (`src/acf/core/`, `src/acf/utils/`)

```
core/
├── __init__.py
├── application.py
├── configuration.py
├── context.py
├── exceptions.py
├── logging.py
├── lifecycle.py
├── registry.py
├── events.py
├── plugins.py
├── dependencies.py
├── environment.py
└── version.py

utils/
├── __init__.py
├── filesystem.py
├── paths.py
├── datetime.py
├── units.py
├── validation.py
├── serialization.py
├── hashing.py
├── caching.py
├── profiling.py
├── concurrency.py
├── numerical.py
└── decorators.py
```

Role: knows nothing about AROME, radar, or the GUI. Provides the primitives
every other layer depends on.

## 3. LAYER 1 — Scientific formulations & standards

`src/acf/science/`, `src/acf/parameters/`, `src/acf/standards/`, `src/acf/catalog/`.

```
science/
├── __init__.py
├── constants/
├── thermodynamics/
├── dynamics/
├── stability/
├── convection/
├── radiation/
├── microphysics/
├── turbulence/
├── boundary_layer/
├── clouds/
├── precipitation/
├── atmospheric_composition/
├── ocean/
├── hydrology/
├── cryosphere/
├── land_surface/
├── carbon_cycle/
├── climate/
└── diagnostics/
```

Initial atmospheric priority:

```
science/thermodynamics/
├── __init__.py
├── potential_temperature.py
├── virtual_temperature.py
├── equivalent_potential_temperature.py
├── mixing_ratio.py
├── specific_humidity.py
├── vapor_pressure.py
├── saturation_vapor_pressure.py
├── relative_humidity.py
└── air_density.py

science/stability/
├── __init__.py
├── lapse_rate.py
├── static_stability.py
├── brunt_vaisala.py
├── lifted_index.py
├── showalter_index.py
└── stability_diagnostics.py

science/convection/
├── __init__.py
├── cape.py
├── cin.py
├── lcl.py
├── lfc.py
├── equilibrium_level.py
├── parcel.py
└── convection_diagnostics.py
```

### `parameters/`

A real, structured scientific catalog, not a flat `parameters.py` — the
historical inventory reached **152 parametrization modules**.

```
parameters/
├── __init__.py
├── atmosphere/
├── ocean/
├── land/
├── cryosphere/
├── radiation/
├── microphysics/
├── turbulence/
├── convection/
├── chemistry/
└── parameterizations/
```

### `standards/`

```
standards/
├── __init__.py
├── units.py
├── dimensions.py
├── coordinates.py
├── metadata.py
├── naming.py
├── conventions.py
├── cf_conventions.py
└── validation.py
```

Purpose: `FA / GRIB / NetCDF / LFA / observations → standards → coherent ACF representation`.

### `catalog/`

```
catalog/
├── __init__.py
├── variables.py
├── fields.py
├── models.py
├── datasets.py
├── levels.py
├── coordinates.py
├── products.py
└── registry.py
```

Lets ACF know what it is manipulating: `T, P, U, V, RH, q, θ, θv, θe, CAPE, CIN, ...`.

## 4. LAYER 2 — Data & spatio-temporal core

`src/acf/data/`, `src/acf/io/`, `src/acf/model4d/`, `src/acf/workspace/`.

```
data/
├── __init__.py
├── dataset.py
├── field.py
├── variable.py
├── observation.py
├── metadata.py
├── quality_control.py
├── validation.py
├── transformations.py
├── resampling.py
├── interpolation.py
└── provenance.py
```

```
io/
├── __init__.py
├── readers/
│   ├── __init__.py
│   ├── fa_reader.py
│   ├── lfa_reader.py
│   ├── grib_reader.py
│   ├── netcdf_reader.py
│   └── observation_reader.py
├── writers/
│   ├── __init__.py
│   ├── grib_writer.py
│   ├── netcdf_writer.py
│   └── export_writer.py
├── adapters/
│   ├── __init__.py
│   ├── epygram_adapter.py
│   ├── eccodes_adapter.py
│   └── xarray_adapter.py
└── formats/
    ├── __init__.py
    ├── fa.py
    ├── lfa.py
    ├── grib.py
    └── netcdf.py
```

```
model4d/
├── __init__.py
├── grid4d.py
├── field4d.py
├── coordinate4d.py
├── time_axis.py
├── vertical_axis.py
├── horizontal_grid.py
├── interpolation.py
├── derivatives.py
├── differential_operators.py
├── gradients.py
├── divergence.py
├── vorticity.py
├── laplacian.py
├── advection.py
└── operators/
```

The two files identified earliest in the original design: `model4d/grid4d.py`
and `model4d/field4d.py`.

```
workspace/
├── __init__.py
├── project.py
├── serializer.py
├── workspace_manager.py
├── session.py
├── state.py
├── recent_projects.py
├── project_registry.py
└── explorer.py
```

Project format: `project.acf`, with `data/ maps/ models/ reports/ scripts/
exports/ logs/ cache/ plugins/` inside a project directory.

## 5. LAYER 3 — Domain & high-level engines

`src/acf/maps/`, `src/acf/visualization/`, `src/acf/models/`, `src/acf/ai/`.
(`awci/` was historically listed here — see the "AWCI separation" section:
it is no longer part of ACF's own layer 3.)

```
maps/
├── __init__.py
├── projection.py
├── map_engine.py
├── layers.py
├── layer_manager.py
├── geographic.py
├── contours.py
├── vectors.py
├── raster.py
└── overlays.py
```

```
visualization/
├── __init__.py
├── scientific/
├── plots/
├── profiles/
├── cross_sections/
├── time_series/
├── diagrams/
├── 2d/
├── 3d/
├── 4d/
└── animation/
```

```
visualization/scientific/
├── thermodynamic_diagrams.py
├── skewt.py
├── hodograph.py
├── sounding.py
├── wind_profiles.py
└── stability_plots.py
```

```
models/
├── __init__.py
├── base.py
├── arome/
├── aladin/
├── arpege/
├── wrf/
├── ensemble/
├── comparison/
├── verification/
└── consensus/
```

```
models/arome/
├── __init__.py
├── adapter.py
├── metadata.py
├── variables.py
└── configuration.py
```

(Same pattern for `models/aladin/`, `models/arpege/`, `models/wrf/`.)

AI is a layer **above** the scientific engine, never a replacement for it:

```
ai/
├── __init__.py
├── agents/
├── inference/
├── models/
├── rag/
├── knowledge/
├── xai/
├── anomaly_detection/
├── event_detection/
├── forecasting/
├── embeddings/
└── orchestration/

ai/agents/
├── scientific_agent.py
├── analysis_agent.py
├── diagnostic_agent.py
├── report_agent.py
└── orchestration_agent.py
```

## 6. LAYER 4 — Presentation & applications

`src/acf/gui/`, `src/acf/dashboard/`, `src/acf/api/`, `src/acf/alerts/`,
`src/acf/reports/`.

```
gui/
├── __init__.py
├── main_window.py
├── application.py
├── menu.py
├── toolbar.py
├── status_bar.py
├── dialogs/
├── widgets/
├── panels/
├── views/
├── models/
└── controllers/
```

Historical central file: `gui/main_window.py`.

```
gui/dialogs/
├── new_project_dialog.py
├── open_project_dialog.py
└── project_properties_dialog.py
```

```
dashboard/
├── __init__.py
├── application.py
├── layout.py
├── state.py
├── data_provider.py
├── map_view.py
├── timeline.py
├── scientific_panel.py
├── charts.py
├── kpis.py
├── layer_manager.py
└── components/
```

Historical UI layout:

```
HEADER
  ↓
GLOBAL EARTH MAP + SCIENTIFIC ANALYSIS PANEL
  ↓
REGIONAL MAP + OPERATIONAL GRAPHS + RISK MATRIX + DECISION SUPPORT + HPC STATUS
  ↓
TIMELINE
  ↓
OPERATIONAL TOOLBAR
```

```
api/
├── __init__.py
├── app.py
├── routes/
│   ├── data.py
│   ├── models.py
│   ├── diagnostics.py
│   ├── maps.py
│   ├── visualization.py
│   ├── ai.py
│   ├── reports.py
│   └── system.py
├── schemas/
├── services/
└── middleware/
```

```
alerts/
├── __init__.py
├── engine.py
├── rules.py
├── thresholds.py
├── events.py
├── notification.py
└── severity.py
```

```
reports/
├── __init__.py
├── generator.py
├── scientific_report.py
├── model_report.py
├── diagnostic_report.py
├── export.py
└── templates/
```

## 7. Project root, outside `src/acf/`

```
ACF/
├── src/
├── tests/
├── docs/
├── resources/
├── scripts/
├── examples/
├── tools/
├── assets/
├── configs/
├── pyproject.toml
├── README.md
├── LICENSE
└── ...
```

```
tests/
├── unit/
├── integration/
├── scientific/
├── data/
├── io/
├── model4d/
├── models/
├── ai/
├── gui/
├── dashboard/
├── api/
└── end_to_end/
```

Philosophy: tests mirror the scientific equations and transformations
themselves, not just the interfaces.

```
docs/
├── architecture/
├── science/
├── data/
├── models/
├── ai/
├── gui/
├── api/
├── operations/
├── user/
└── latex/
```

Also planned: `scripts/generate_docs.py`, `docs/latex/main.tex`, generating
`docs/latex/ACF_V1_0_COMPLETE_TECHNICAL_DOCUMENTATION.pdf`.

```
tools/
├── acfctl/
├── validation/
├── diagnostics/
├── conversion/
├── profiling/
└── development/
```

`acfctl` was meant to become the operational control point:
`acfctl start | stop | status | report ...`.

```
configs/
├── acf.yaml
├── logging.yaml
├── models.yaml
├── data.yaml
├── science.yaml
├── ai.yaml
├── gui.yaml
├── hpc.yaml
└── environments/
```

```
resources/
├── schemas/
├── dictionaries/
├── catalogs/
├── templates/
├── colormaps/
├── icons/
└── scientific/
```

```
examples/
├── data/
├── notebooks/
├── scientific/
├── model_comparison/
├── visualization/
└── workflows/
```

```
assets/
├── icons/
├── images/
├── fonts/
├── themes/
└── branding/
```

## 8. The consolidated view

```
ACF
│
┌─────────────────┴─────────────────┐
FOUNDATION                     APPLICATION
│                                     │
┌────┴────┐                 ┌─────────┼─────────┐
core   utils                GUI   Dashboard    API
  │                                   │
  └──────────────┐   ┌────────────────┘
                  │   │
        SCIENTIFIC FORMULATIONS
                  │
  ┌───────────────┼───────────────┐
science      parameters       standards
  │               │                │
  └───────────────┼────────────────┘
                  │
            DATA & 4D CORE
                  │
  ┌───────────────┼────────────────┐
data           io          model4d      workspace
  │               │                │
  └───────────────┼────────────────┘
                  │
          HIGH-LEVEL ENGINES
                  │
  ┌────────────────┼──────────────────┐
maps        visualization         models
                                        │
                              ┌─────────┼─────────┐
                           AROME     ALADIN    ARPEGE   WRF
                                        │
                                        ▼
                                       AI
                                        │
                          ┌─────────────┼─────────────┐
                        RAG           XAI          Agents
                                        │
                                        ▼
                          ANALYSIS / DIAGNOSTICS
                                        │
                                        ▼
                            REPORTS / ALERTS
                                        │
                                        ▼
                            GUI / API / ESOC (removed, see below)
                                        │
                                        ▼
                              HPC / SLURM / Runtime
```

Two distinct readings of the same architecture:

**Logical architecture:**
`Foundation → Science → Data → 4D → Models/Maps/Visualization → AI → Applications`

**Operational architecture:**
`Data sources → Ingestion → QC/Validation → Scientific computation → Diagnostics → Analysis → Visualization → GUI/Dashboard/API/Reports → HPC/ESOC`

This original architecture is the historical baseline to work from — not the
current state of the repository, which has since evolved: some layers were
added, others are currently incomplete or missing (see the gap analysis).

## 9. ESOC removal

ESOC — the operational environment/interface once planned to host ACF
(GUI integration, monitoring, VNC, some HPC controls) — is **not** a
necessary scientific component of ACF and is fully removed from the
reference architecture. Distinguish:

- **ACF** = the autonomous scientific software.
- **The operating environment** ACF can optionally be launched inside —
  ESOC was one candidate for this, no longer used.

```
ACF (no ESOC)
│
┌───────────┴───────────┐
SCIENTIFIC CORE                 APPLICATION LAYER
│                                     │
┌───────┼────────┐         ┌──────┼───────┐
Science  Data   4D          GUI  Dashboard  API
│         │      │                │
└───────┼────────┘         └──────┼───────┘
        │                          │
        └───────────┬──────────────┘
                     │
              ACF SERVICES
                     │
        ┌────────────┼────────────┐
       AI          Reports      Alerts
                     │
              HPC / SLURM LAYER
                     │
        ┌────────────┼────────────┐
      CPU         Storage        Jobs
```

What disappears: ESOC itself, its runtime, its GUI integration, its
ESOC-specific services/launcher, are no longer considered foundational ACF
components.

What remains — ACF runs directly with:

```
ACF
├── Scientific Core
├── Data / IO
├── Model 4D
├── Models
├── Visualization
├── AI
├── Reports
├── Alerts
├── GUI
├── Dashboard
├── API
└── HPC / SLURM
```

HPC becomes plain execution infrastructure, not a dependency on ESOC.

### The cleaner 5-level restatement

- **L0 — Foundation**: Core / Utils / Configuration.
- **L1 — Science**: Thermodynamics, Dynamics, Stability, Convection,
  Microphysics, Radiation, etc.
- **L2 — Data**: FA/LFA/GRIB/NetCDF, Observations, QC, Normalization,
  Model 4D, Storage, Provenance.
- **L3 — Intelligence**: Diagnostics, Model comparison, Consensus,
  Uncertainty, AI/RAG, Anomaly detection.
- **L4 — Application**: GUI, Dashboard, API, Visualization, Reports, Alerts.
- **Infrastructure (separate)**: HPC, SLURM, SSH, Storage, Containers,
  Monitoring.

```
ACF
│
┌──────────┼──────────┐
Desktop      Web       CLI
│             │         │
└──────────┼──────────┘
            │
       ACF Engine
            │
      HPC / SLURM
```

ESOC becomes, at most, one possible external environment among others — not
a part of ACF.

### Final restated tree (ESOC-free)

```
ACF
│
┌─────────────────┼─────────────────┐
FOUNDATION      SCIENTIFIC        DATA
│                 CORE               │
│                   │                │
core          thermodynamics    ingestion
utils         dynamics          FA / LFA
config        stability         GRIB
              convection        NetCDF
              microphysics      observations
              radiation         QC
              turbulence        provenance
                                     │
                              MODEL 4D CORE
                                     │
                    ┌────────────────┼────────────────┐
                  AROME            ALADIN            ARPEGE
                    │                │                 │
                    └────────────────┼─────────────────┘
                                     │
                              ACF ENGINES
                                     │
                    ┌────────────────┼─────────────────┐
              Diagnostics       Comparison          Consensus
                    │                │                 │
                    ├───────── Uncertainty ────────────┤
                    │
                    └───────── AI / RAG
                                     │
                              VISUALIZATION
                                     │
                    ┌────────────────┼─────────────────┐
                  GUI            Dashboard             API
                    │                │                 │
                    └────────────────┼─────────────────┘
                                     │
                            Reports / Alerts
                                     │
                                     ▼
                              HPC / SLURM
```

### The new fundamental split

```
ACF SOFTWARE
├── Scientific Core
├── Data & IO
├── Model 4D
├── Model Adapters
├── Diagnostics
├── Comparison / Consensus
├── AI / RAG
├── Visualization
├── GUI
├── Dashboard
├── API
├── Reports
└── Alerts

INFRASTRUCTURE
├── HPC
├── SLURM
├── SSH
├── Storage
└── Compute
```

ESOC no longer appears anywhere. This is not only a diagram change: future
ACF files, imports, tests, configuration, and modules must not introduce an
ESOC dependency again.

## 10. AWCI separation

AWCI was part of the historical ACF architecture (Layer 3, `awci/`). The
user later explicitly decided to take AWCI out of the ACF dashboard/core.
This reference architecture therefore does **not** put AWCI back into ACF's
core without an explicit decision to do so. AWCI has its own full reference
architecture: see
[`awci_reference_architecture.md`](awci_reference_architecture.md).

The relationship between the two projects:

```
ACF                                    AWCI
│                                       │
Atmospheric Science + Generic Data  →  Aviation Hazards Operations → Complexity → AWCI
```

ACF remains the general scientific framework; AWCI (and future sibling
indices such as a maritime "MWCI") are separate aviation/domain-specific
products built on top of it.
