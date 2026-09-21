# AWCI Reference Architecture

**Status: reference/target architecture, adopted 2026-09-21 at explicit user
request, superseding every AWCI architecture discussion before it.**

This document is a faithful transcription of the architecture the user
provided as `awci.odt`. It describes AWCI as a **separate aviation
product/project**, built above the ACF scientific core, with its own
independent aviation core, aviation data, hazard/risk engines, complexity
computation, and decision/visualization layers — not as a subpackage buried
inside ACF's own layer 3.

This is a **target/blueprint** for a top-level `src/awci/` package, distinct
from the current `src/acf/awci/` subpackage the codebase actually has today
— see
[`acf_awci_architecture_gap_analysis.md`](acf_awci_architecture_gap_analysis.md)
for how the existing code maps onto it, and what a real migration would
involve.

This is the **first, historical** AWCI architecture. It must not be
confused with the separate, later decision to remove AWCI from the ACF
dashboard — that decision stands: AWCI exists as a separate aviation
project/application, while ACF remains the general scientific framework.

## 1. AWCI Core (`src/awci/core/`)

The software nucleus coordinating the whole platform.

```
src/awci/core/
├── __init__.py
├── application.py
├── configuration.py
├── context.py
├── exceptions.py
├── logging.py
├── lifecycle.py
├── registry.py
├── events.py
├── dependencies.py
├── version.py
├── constants.py
└── types.py
```

Responsibilities: configuration, lifecycle, events, dependency injection,
plugin registry, AWCI context, common types, error handling, logging. It
does **not** itself compute turbulence or icing.

## 2. Aviation Knowledge Base (`src/awci/knowledge/`)

The aviation domain knowledge.

```
src/awci/knowledge/
├── __init__.py
├── aviation/
│   ├── airports.py
│   ├── aircraft.py
│   ├── flight_levels.py
│   ├── airspaces.py
│   ├── runways.py
│   └── procedures.py
├── meteorology/
│   ├── terminology.py
│   ├── phenomena.py
│   ├── clouds.py
│   ├── fronts.py
│   └── air_masses.py
├── regulations/
│   ├── categories.py
│   ├── thresholds.py
│   └── standards.py
├── hazards/
│   ├── turbulence.py
│   ├── icing.py
│   ├── wind_shear.py
│   ├── convection.py
│   ├── visibility.py
│   ├── ceiling.py
│   ├── volcanic_ash.py
│   └── precipitation.py
└── knowledge_graph/
    ├── entities.py
    ├── relations.py
    ├── graph.py
    └── ontology.py
```

Must know about: METAR, SPECI, TAF, SIGMET, AIRMET, NOTAM, weather
phenomena, cloud types, flight levels, airports, runways, airspaces,
aviation hazards.

## 3. Data Hub (`src/awci/data/`)

The entry point for all data.

```
src/awci/data/
├── __init__.py
├── hub.py
├── dataset.py
├── field.py
├── metadata.py
├── provenance.py
├── quality_control.py
├── validation.py
├── normalization.py
├── synchronization.py
├── cache.py
└── catalog.py
```

Connectors:

```
src/awci/data/connectors/
├── acf.py
├── grib.py
├── fa.py
├── lfa.py
├── netcdf.py
├── metar.py
├── speci.py
├── taf.py
├── sigmet.py
├── airmet.py
├── radar.py
├── satellite.py
├── lightning.py
├── pirep.py
└── notam.py
```

Chain: `Sources → Connectors → Validation → QC → Normalization → Canonical AWCI Data`.

## 4. Aviation Observation Hub (`src/awci/observations/`)

Specialized in aviation observations.

```
src/awci/observations/
├── __init__.py
├── hub.py
├── stations.py
├── metar.py
├── speci.py
├── pirep.py
├── radar.py
├── satellite.py
├── lightning.py
├── surface.py
├── upper_air.py
└── aircraft_observations.py
```

```
observations/metar/
├── parser.py
├── decoder.py
├── validator.py
├── interpreter.py
└── observation.py

observations/pirep/
├── parser.py
├── decoder.py
├── turbulence.py
├── icing.py
└── observation.py
```

## 5. Aviation Forecast Engine (`src/awci/forecast/`)

```
src/awci/forecast/
├── __init__.py
├── engine.py
├── forecast.py
├── nowcasting.py
├── short_range.py
├── medium_range.py
├── ensemble.py
├── uncertainty.py
├── interpolation.py
└── verification.py
```

Consumes: ACF, AROME, ALADIN, ARPEGE, WRF, observations, radar, satellite.
Produces fields usable by AWCI.

## 6. Vertical Profile Engine (`src/awci/vertical/`)

A particularly important layer.

```
src/awci/vertical/
├── __init__.py
├── profile.py
├── sounding.py
├── thermodynamics.py
├── stability.py
├── wind_profile.py
├── shear.py
├── cloud_layers.py
├── icing_profile.py
├── turbulence_profile.py
└── flight_levels.py
```

Vertical structure: `Surface → Boundary Layer → Troposphere → Tropopause → Stratosphere`.

Variables: Temperature, Dew Point, RH, Wind, Wind Shear, Stability, Clouds,
Icing, Turbulence, Flight Levels.

Diagrams:

```
src/awci/vertical/diagrams/
├── skew_t.py
├── tephigram.py
├── emagram.py
├── stuve.py
├── hodograph.py
└── wind_profile.py
```

## 7. Aviation Hazard Engine (`src/awci/hazards/`)

The meteorological aviation hazard engine.

```
src/awci/hazards/
├── __init__.py
├── engine.py
├── hazard.py
├── severity.py
├── probability.py
├── spatial.py
├── temporal.py
├── vertical.py
└── aggregation.py
```

One module per hazard:

```
hazards/
├── turbulence/
├── icing/
├── wind_shear/
├── convection/
├── thunderstorm/
├── visibility/
├── ceiling/
├── precipitation/
├── strong_wind/
├── crosswind/
├── microburst/
├── mountain_wave/
├── volcanic_ash/
├── dust/
├── fog/
├── lightning/
└── snowfall/
```

Every hazard module must be able to produce: `hazard, severity, probability,
altitude, location, time, confidence, source`.

## 8. Aviation Complexity Engine (`src/awci/complexity/`)

This is where AWCI itself is actually computed.

```
src/awci/complexity/
├── __init__.py
├── engine.py
├── factors.py
├── weights.py
├── normalization.py
├── aggregation.py
├── scoring.py
├── thresholds.py
├── uncertainty.py
├── confidence.py
└── classification.py
```

Factors: Instability, Humidity, Wind, Wind shear, Convection, Turbulence,
Icing, Visibility, Ceiling, Precipitation, Model disagreement, Forecast
uncertainty, Spatial variability, Temporal variability.

Pipeline: `Factors → Normalization → Weighting → Aggregation → Complexity → AWCI`.

**Core principle: the AWCI score must be computed from traceable scientific
factors, never an arbitrary score.**

## 9. Model Comparison (`src/awci/comparison/`)

Measures disagreement between models.

```
src/awci/comparison/
├── __init__.py
├── engine.py
├── pairwise.py
├── spatial.py
├── temporal.py
├── vertical.py
├── metrics.py
├── bias.py
└── disagreement.py
```

```
AROME
  │
ALADIN ──→ comparison
  │
ARPEGE
  │
WRF
```

Output: `agreement, disagreement, spread, bias, uncertainty, confidence`.

## 10. Consensus Engine (`src/awci/consensus/`)

Above comparison:

```
src/awci/consensus/
├── __init__.py
├── engine.py
├── model_consensus.py
├── ensemble_consensus.py
├── observation_consensus.py
├── confidence.py
└── uncertainty.py
```

Answers: *Do the models agree? Do observations confirm the models? What is
the confidence level?*

## 11. Flight Planning Engine (`src/awci/flight/`)

Turns weather into usable flight information.

```
src/awci/flight/
├── __init__.py
├── planning.py
├── route.py
├── waypoint.py
├── corridor.py
├── altitude.py
├── flight_levels.py
├── departure.py
├── arrival.py
├── alternate.py
├── fuel_weather.py
└── route_weather.py
```

Covers: Route, Altitude, Departure, Cruise, Arrival, Alternate, Weather
along route, Hazards along route.

## 12. Airport Operations (`src/awci/airport/`)

```
src/awci/airport/
├── __init__.py
├── airport.py
├── runway.py
├── terminal.py
├── operations.py
├── weather.py
├── visibility.py
├── ceiling.py
├── crosswind.py
├── runway_condition.py
├── departure.py
├── arrival.py
└── disruption.py
```

Chain: `Weather → Airport → Runway → Operation`.

## 13. Decision Support (`src/awci/decision/`)

Gathers information into an operational view. Does not replace the decision
maker.

```
src/awci/decision/
├── __init__.py
├── engine.py
├── context.py
├── situation.py
├── risk_matrix.py
├── confidence.py
├── alternatives.py
├── scenario.py
└── recommendation.py
```

Provides: Situation, Risks, Hazards, Confidence, Uncertainty, Alternatives,
Evidence.

## 14. Aviation AI Assistant (`src/awci/ai/`)

AI comes after the data and the scientific computations.

```
src/awci/ai/
├── __init__.py
├── assistant.py
├── agents/
├── rag/
├── knowledge/
├── reasoning/
├── anomaly_detection/
├── explanation/
├── summarization/
└── orchestration/
```

```
ai/agents/
├── weather_agent.py
├── hazard_agent.py
├── aviation_agent.py
├── analysis_agent.py
├── report_agent.py
└── decision_agent.py

ai/rag/
├── retriever.py
├── embeddings.py
├── vector_store.py
├── documents.py
└── citations.py
```

## 15. Maps & Visualization (`src/awci/visualization/`)

```
src/awci/visualization/
├── __init__.py
├── maps/
├── charts/
├── profiles/
├── cross_sections/
├── time_series/
├── flight_paths/
├── hazards/
├── complexity/
├── radar/
├── satellite/
└── 3d/
```

```
visualization/maps/
├── base_map.py
├── projection.py
├── layers.py
├── contours.py
├── vectors.py
├── raster.py
├── airports.py
├── flight_routes.py
└── hazard_overlay.py

visualization/complexity/
├── awci_map.py
├── factor_map.py
├── uncertainty_map.py
└── model_disagreement_map.py
```

## 16. Dashboard (`src/awci/dashboard/`)

The aviation dashboard is an application layer above everything else.

```
src/awci/dashboard/
├── __init__.py
├── application.py
├── layout.py
├── state.py
├── data_provider.py
├── map_view.py
├── timeline.py
├── flight_view.py
├── airport_view.py
├── hazard_view.py
├── complexity_view.py
├── model_view.py
├── profile_view.py
└── components/
```

General layout:

```
┌───────────────────────────────────────────┐
│  AWCI / FLIGHT / AIRPORT / MODEL / TIME    │
├───────────────────────┬───────────────────┤
│                        │                   │
│         MAP            │      HAZARDS      │
│                        │    COMPLEXITY     │
│                        │    CONFIDENCE     │
├───────────────────────┴───────────────────┤
│      VERTICAL PROFILE / TIME SERIES        │
├───────────────────────────────────────────┤
│ FORECAST │ MODELS │ OBS │ ROUTE │ REPORT   │
└───────────────────────────────────────────┘
```

## 17. Reports (`src/awci/reports/`)

```
src/awci/reports/
├── __init__.py
├── generator.py
├── aviation_report.py
├── flight_report.py
├── airport_report.py
├── hazard_report.py
├── complexity_report.py
├── model_report.py
├── verification_report.py
└── templates/
```

Every report must preserve: data sources, model, time, location,
calculation, factors, hazards, confidence, uncertainty, provenance.

## 18. API (`src/awci/api/`)

```
src/awci/api/
├── __init__.py
├── app.py
├── routes/
│   ├── flights.py
│   ├── airports.py
│   ├── observations.py
│   ├── forecasts.py
│   ├── hazards.py
│   ├── complexity.py
│   ├── models.py
│   ├── profiles.py
│   ├── maps.py
│   ├── reports.py
│   └── ai.py
├── schemas/
├── services/
└── middleware/
```

## 19. Alerts (`src/awci/alerts/`)

```
src/awci/alerts/
├── __init__.py
├── engine.py
├── rules.py
├── thresholds.py
├── severity.py
├── notifications.py
├── hazard_alerts.py
├── airport_alerts.py
├── route_alerts.py
└── complexity_alerts.py
```

## 20. Plugins (`src/awci/plugins/`)

AWCI must be extensible.

```
src/awci/plugins/
├── __init__.py
├── manager.py
├── registry.py
├── interface.py
├── loader.py
└── hooks.py
```

Allows adding, without rewriting the core: a new data source, a new model,
a new hazard, a new visualization, a new aviation product, a new AI agent.

## 21. Workspace / Projects (`src/awci/workspace/`)

```
src/awci/workspace/
├── __init__.py
├── project.py
├── session.py
├── state.py
├── workspace.py
├── serializer.py
└── manager.py
```

An AWCI project keeps: `data/ forecasts/ flights/ airports/ hazards/ maps/
reports/ analysis/ exports/ logs/`.

## 22. Provenance & Audit (`src/awci/provenance/`)

Particularly important for a scientific system.

```
src/awci/provenance/
├── __init__.py
├── lineage.py
├── source.py
├── calculation.py
├── version.py
├── audit.py
└── reproducibility.py
```

For every result, must be traceable: `AWCI → Which model? → Which data? →
Which time? → Which variables? → Which formula? → Which factors? → Which
code version?`.

## 23. Tests

The test architecture must mirror the layers:

```
tests/
├── unit/
│   ├── core/
│   ├── knowledge/
│   ├── data/
│   ├── observations/
│   ├── forecast/
│   ├── hazards/
│   ├── complexity/
│   ├── comparison/
│   ├── consensus/
│   ├── flight/
│   ├── airport/
│   ├── ai/
│   └── visualization/
├── integration/
├── scientific/
├── aviation/
├── api/
├── dashboard/
└── end_to_end/
```

## 24. The complete chain

```
┌─────────────────┐
│       ACF        │
│ Scientific Core   │
└────────┬─────────┘
         ▼
┌─────────────────┐
│    AWCI DATA     │
└────────┬─────────┘
         │
┌────────┼──────────────────┐
▼                  ▼                  ▼
Observations       Models             Aviation
METAR/SPECI        AROME/ALADIN       Airports
PIREP              ARPEGE/WRF         Routes
Radar              Ensembles          Flight data
Satellite
│                  │                  │
└──────────────────┼──────────────────┘
                    ▼
           ┌─────────────────┐
           │ FORECAST ENGINE  │
           └────────┬─────────┘
                    ▼
           ┌─────────────────┐
           │ VERTICAL ENGINE  │
           └────────┬─────────┘
                    ▼
           ┌─────────────────┐
           │  HAZARD ENGINE   │
           └────────┬─────────┘
                    │
┌───────────────────┼────────────────────┐
▼                   ▼                    ▼
Turbulence          Icing                Convection
Wind shear          Visibility           Ceiling
Microburst          Fog                  Volcanic ash
│                   │                    │
└───────────────────┼────────────────────┘
                    ▼
           ┌──────────────────┐
           │ MODEL COMPARISON  │
           └────────┬──────────┘
                    ▼
           ┌─────────────────┐
           │    CONSENSUS     │
           └────────┬─────────┘
                    ▼
           ┌─────────────────┐
           │   COMPLEXITY     │
           │     ENGINE       │
           └────────┬─────────┘
                    ▼
           ┌─────────────────┐
           │       AWCI       │
           │   Complexity     │
           │   Confidence     │
           │   Uncertainty    │
           └────────┬─────────┘
                    │
┌───────────────────┼────────────────────┐
▼                   ▼                    ▼
Flight Planning     Airport Ops          Decision Support
│                   │                    │
└───────────────────┼────────────────────┘
                    ▼
              AI ASSISTANT
                    │
┌───────────────────┼────────────────────┐
▼                   ▼                    ▼
Maps                Dashboard            Reports
│                   │                    │
└───────────────────┼────────────────────┘
                    ▼
                   API
```

## 25. ACF ↔ AWCI relationship

```
ACF
│
┌─────────┴─────────┐
Atmospheric Science   Generic Data
│                     │
└─────────┬───────────┘
          ▼
        AWCI
          │
┌─────────┼─────────┐
Aviation   Hazards   Operations
│         │          │
└─────────┼──────────┘
          ▼
      Complexity
          │
          ▼
        AWCI
```

**Important distinction, restated**: this is the **first, historical** AWCI
architecture. It must not be confused with the later, separate decision to
remove AWCI from the ACF dashboard. AWCI can exist as a separate
aviation project/application, while ACF remains the general scientific
framework — consistent with the direction already taken in this codebase
(ESOC removed 2026-09-21; ACF's own default entry point is now the AWCI-free
`ACFWorkstationWindow`, with AWCI reachable as its own standalone
application via `acf-awci`).

## 26. The original AWCI architecture, as first defined (2026-09-21, restated by the user)

The user restated the very first AWCI architecture discussion, from before
even this document, to make sure it is not lost sight of during the ongoing
migration. Transcribed faithfully below, verbatim in structure. **It is
fully consistent with §1-25 above** - every block named here has a direct,
already-documented counterpart in this document's own §1-22 per-layer
breakdown (cross-referenced below); nothing here contradicts what is
already written. This section exists to (a) preserve the original framing
in the user's own words and diagram shapes, and (b) make the ACF/AWCI
separation principle - the reason this whole `src/awci/` migration
(`acf_awci_architecture_gap_analysis.md` §2) exists at all - impossible to
lose sight of.

**The original tree:**

```
                              AWCI
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   DATA HUB              KNOWLEDGE BASE          CORE ENGINE
        │                      │                      │
        │                Aviation Knowledge      Formulas
        │                Aviation KG            Units
        │                Rules                  Validation
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                         INPUT ADAPTERS
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
         ACF                  GRIB/FA           Observations
          │                    │                    │
       NetCDF                 LFA               METAR/TAF
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                  CANONICAL METEOROLOGICAL DATA
                               │
                               ▼
                    AVIATION FORECAST ENGINE
                               │
                               ▼
                     AVIATION HAZARD ENGINE
                               │
          ┌────────────┬──────┼──────┬─────────────┐
          │            │      │      │             │
      Turbulence    Icing  Convection Wind      Visibility
          │            │      │      │             │
          ├────────────┼──────┼──────┼─────────────┤
          │
      Ceiling / Precipitation / Shear /
      Microburst / Mountain Wave / ...
                               │
                               ▼
                    FLIGHT PLANNING ENGINE
                               │
                               ▼
                     AIRPORT OPERATIONS
                               │
                               ▼
                    AVIATION DECISION SUPPORT
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
            AWCI COMPLEXITY              FORECAST
                 │                           │
                 ▼                           ▼
             AWCI SCORE              Verification /
                 │                   Confidence
                 │                   Consensus
                 └─────────────┬─────────────┘
                               │
                               ▼
                    AVIATION AI ASSISTANT
                               │
              ┌────────────────┼────────────────┐
              │                │                │
             MAPS          DASHBOARD         REPORTS
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
                              API
                               │
                            Plugins
```

**The 13-14 original top-level blocks, and their §1-22 counterpart in this
document:**

1. Core → §1 AWCI Core (`awci/core/`)
2. Aviation Knowledge Base → §2 Aviation Knowledge Base (`awci/knowledge/`)
3. Flight Planning Engine → §11 Flight Planning Engine (`awci/flight/`)
4. Airport Operations → §12 Airport Operations (`awci/airport/`)
5. Aviation Observation Hub → §4 Aviation Observation Hub (`awci/observations/`)
6. Aviation Forecast Engine → §5 Aviation Forecast Engine (`awci/forecast/`)
7. Aviation Hazard Engine → §7 Aviation Hazard Engine (`awci/hazards/`)
8. Aviation AI Assistant → §14 Aviation AI Assistant (`awci/ai/`)
9. Aviation Decision Support → §13 Decision Support (`awci/decision/`)
10. Maps & Visualization → §15 Maps & Visualization (`awci/visualization/`)
11. Data Hub → §3 Data Hub (`awci/data/`)
12. Reports → §17 Reports (`awci/reports/`)
13. API → §18 API (`awci/api/`)
14. Plugins → §20 Plugins (`awci/plugins/`)

(§6 Vertical Profile Engine, §8 Aviation Complexity Engine, §9 Model
Comparison, §10 Consensus Engine, §16 Dashboard, §19 Alerts, §21 Workspace,
and §22 Provenance & Audit were elaborated later, as this document's own
more detailed per-layer breakdown of blocks 6/9's implicit content - not
new blocks contradicting the original 13-14.)

**The Vertical Profile Engine** was always meant as an important native
component (elaborated in full in §6 above):

```
Surface
   ↓
Boundary Layer
   ↓
Troposphere
   ↓
Tropopause
   ↓
Stratosphere
```

Profiles: Temperature, Dew Point, RH, Wind, Wind Shear, Stability, Clouds,
Icing, Turbulence, Flight Levels.

Visualizations: Skew-T, Tephigram, Emagram, Stüve, Vertical Cross Sections.

**The compact scientific chain**, as it was formulated afterward:

```
ACF
 │
 ▼
AWCI
 │
 ├── Aviation Hazards
 │
 ├── Aviation Complexity
 │
 ├── Forecast
 │
 ├── Verification
 │
 ├── Confidence
 │
 └── Consensus
 │
 ▼
AWCI SCORE
 │
 ▼
Aviation UI / UX
```

**The fundamental separation - the reason this entire migration exists**:

```
ACF                              AWCI
Atmosphere                       ACF Data
   ↓                                ↓
Physics                          Aviation Hazards
   ↓                                ↓
Complexity                       Aviation Complexity
                                     ↓
                                  Operational Aviation Information
```

**AWCI was, from the start, meant as a specialized aviation application
built on top of ACF - never a replacement for the ACF framework.** ACF
supplies the general atmospheric science (physics, complexity
computation); AWCI consumes ACF as its scientific foundation and adds the
aviation-specific layer on top (hazards → complexity → operational
information). This is exactly the direction the `src/awci/` migration
(`acf_awci_architecture_gap_analysis.md` §2a-§2k) has followed throughout:
every migrated `awci.*` module that needs general atmospheric physics
imports it from `acf.science.*` directly (never duplicated or
reimplemented inside `awci/`); AWCI's own real, aviation-specific code
(hazard computation, complexity scoring, the dashboard) is what physically
moved into `src/awci/`. The one place this principle is not yet fully
realized is the **reverse** direction, disclosed in
`acf_awci_architecture_gap_analysis.md` §2k: ACF's own dashboard
(`acf_workstation_*.py`, `acf_general_dashboard.py`) still reuses several
AWCI dashboard widgets (`AWCIMapPanel` most commonly) as generic
components. That is a real, disclosed, not-yet-resolved decoupling
question - AWCI should ultimately be something ACF's own dashboard does
not need to depend on at all, matching this section's own restated
principle - not something to unilaterally rewrite without confirming the
replacement widget's scope first.
