# ACF — ATMOSPHERIC COMPLEXITY FRAMEWORK
## MASTER UNIFIED ARCHITECTURE

**Statut :** architecture cible (target), fournie par l'utilisateur le 2 septembre 2026.
**Portée :** architecture unique intégrale — cible ACF v1.0 Production.

> Ce document décrit la chaîne de traitement de référence à 30 niveaux vers
> laquelle ACF doit tendre. Il ne décrit **pas** l'état actuel du code — voir
> `docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md` pour la correspondance avec la
> structure `src/acf/` réelle au 2 septembre 2026.

---

## 1. Architecture unique

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                         ACF v1.0 PRODUCTION                                  │
│                  ATMOSPHERIC COMPLEXITY FRAMEWORK                            │
└──────────────────────────────────────────────────────────────────────────────┘

                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                         0. INPUT ECOSYSTEM                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  NWP MODELS                                                                  │
│  ├── ARPEGE                                                                  │
│  ├── AROME                                                                   │
│  ├── ALADIN                                                                  │
│  ├── WRF                                                                      │
│  ├── ICON                                                                     │
│  ├── IFS                                                                      │
│  └── OpenIFS                                                                  │
│                                                                              │
│  OBSERVATIONS                                                                │
│  ├── stations                                                                 │
│  ├── radiosondes                                                              │
│  ├── aircraft                                                                  │
│  ├── buoys                                                                     │
│  └── surface observations                                                     │
│                                                                              │
│  REMOTE SENSING                                                              │
│  ├── radar                                                                    │
│  └── satellite                                                                 │
│                                                                              │
│  ENVIRONMENT                                                                  │
│  ├── land                                                                      │
│  ├── soil                                                                      │
│  ├── ocean                                                                     │
│  ├── aerosols                                                                  │
│  ├── dust                                                                      │
│  └── fire                                                                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                    1. INGESTION & SOURCE ADAPTER LAYER                       │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Format adapters                                                              │
│  ├── GRIB / GRIB2                                                             │
│  ├── NetCDF                                                                   │
│  ├── HDF5                                                                     │
│  ├── BUFR                                                                     │
│  ├── CSV / JSON                                                               │
│  └── Zarr                                                                     │
│                                                                              │
│  Model adapters                                                               │
│  ├── ARPEGE                                                                   │
│  ├── AROME                                                                    │
│  ├── ALADIN                                                                   │
│  ├── WRF                                                                      │
│  ├── ICON                                                                     │
│  ├── IFS / OpenIFS                                                            │
│  └── Generic Adapter                                                          │
│                                                                              │
│  Observation adapters                                                         │
│  ├── radar                                                                    │
│  ├── satellite                                                                 │
│  ├── station                                                                   │
│  └── radiosonde                                                               │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                  2. DISCOVERY / INSPECTION / METADATA                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Dataset discovery                                                            │
│  Model identification                                                        │
│  Variable discovery                                                          │
│  Grid detection                                                               │
│  Coordinate detection                                                         │
│  Time detection                                                               │
│  Vertical-coordinate detection                                                │
│  Metadata extraction                                                          │
│  Run identification                                                           │
│  Forecast-cycle identification                                               │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                    3. NORMALIZATION & INTEROPERABILITY                       │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Variable naming                                                              │
│  Unit normalization                                                           │
│  Coordinate normalization                                                     │
│  Time normalization                                                           │
│  Vertical normalization                                                       │
│  Grid normalization                                                           │
│  Projection normalization                                                     │
│  Metadata normalization                                                       │
│                                                                              │
│                         COMMON ACF DATA MODEL                                 │
│                                                                              │
│  Dataset                                                                      │
│  Variable                                                                     │
│  Grid                                                                         │
│  TimeAxis                                                                     │
│  VerticalAxis                                                                 │
│  Domain                                                                       │
│  Run                                                                          │
│  AtmosphericState                                                             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                         4. QUALITY CONTROL                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Schema QC                                                                    │
│  Metadata QC                                                                  │
│  Range QC                                                                     │
│  Unit QC                                                                      │
│  Spatial QC                                                                   │
│  Temporal QC                                                                  │
│  Vertical QC                                                                  │
│  Completeness QC                                                              │
│  Physical consistency QC                                                      │
│                                                                              │
│                     PASS ───── WARNING ───── FAIL                            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                          5. PHYSICS GUARD                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  DIMENSIONAL VALIDATION                                                       │
│  UNIT VALIDATION                                                              │
│  RANGE VALIDATION                                                             │
│  VARIABLE DEPENDENCY VALIDATION                                               │
│  PHYSICAL CONSISTENCY                                                         │
│  CONSTANT VALIDATION                                                          │
│  FORMULA INPUT VALIDATION                                                     │
│                                                                              │
│  Central constants                                                            │
│  ├── Rd                                                                       │
│  ├── Rv                                                                       │
│  ├── Cp                                                                       │
│  ├── Cv                                                                       │
│  ├── g                                                                        │
│  ├── Lv                                                                       │
│  ├── Ls                                                                       │
│  ├── epsilon                                                                   │
│  ├── sigma                                                                     │
│  ├── Earth parameters                                                         │
│  └── planetary parameters                                                      │
│                                                                              │
│                    PHYSICS SAFE / PHYSICS FAIL                               │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                      6. GRID / SPATIAL / VERTICAL ENGINE                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Horizontal grids                                                             │
│  ├── regular                                                                  │
│  ├── projected                                                                │
│  ├── curvilinear                                                              │
│  └── unstructured                                                             │
│                                                                              │
│  Regridding                                                                   │
│  ├── nearest                                                                   │
│  ├── bilinear                                                                  │
│  ├── bicubic                                                                   │
│  └── conservative                                                              │
│                                                                              │
│  Vertical coordinates                                                         │
│  ├── pressure                                                                 │
│  ├── height                                                                    │
│  ├── model level                                                               │
│  ├── hybrid                                                                    │
│  └── sigma                                                                     │
│                                                                              │
│  Vertical operations                                                          │
│  ├── interpolation                                                             │
│  ├── gradients                                                                 │
│  ├── integration                                                               │
│  ├── averaging                                                                 │
│  ├── maxima/minima                                                             │
│  └── layer operations                                                          │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                       7. ACF ATMOSPHERIC STATE                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         ATMOSPHERIC STATE                                    │
│                                                                              │
│  ├── Thermodynamics                                                           │
│  ├── Moisture                                                                 │
│  ├── Pressure                                                                  │
│  ├── Temperature                                                               │
│  ├── Wind                                                                      │
│  ├── Geopotential                                                              │
│  ├── Clouds                                                                    │
│  ├── Precipitation                                                             │
│  ├── Radiation                                                                 │
│  ├── Turbulence                                                                │
│  ├── Boundary layer                                                            │
│  ├── Surface                                                                   │
│  ├── Soil                                                                      │
│  ├── Ocean                                                                     │
│  └── Aerosols                                                                  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                         8. 4D ATMOSPHERIC CUBE                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                              X × Y × Z × T                                   │
│                                                                              │
│             Longitude × Latitude × Vertical × Time                           │
│                                                                              │
│  ├── 2D slices                                                               │
│  ├── vertical slices                                                         │
│  ├── temporal slices                                                         │
│  ├── cross sections                                                           │
│  ├── trajectories                                                              │
│  ├── volumes                                                                   │
│  ├── animation                                                                 │
│  └── 4D interpolation                                                         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                         9. PHYSICS ENGINE                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  THERMODYNAMICS                                                              │
│  ├── potential temperature                                                    │
│  ├── virtual temperature                                                      │
│  ├── equivalent potential temperature                                        │
│  ├── dew point                                                                │
│  ├── wet bulb                                                                 │
│  ├── saturation                                                               │
│  └── phase transitions                                                        │
│                                                                              │
│  MOISTURE                                                                    │
│  ├── specific humidity                                                        │
│  ├── mixing ratio                                                             │
│  ├── relative humidity                                                       │
│  └── vapor pressure                                                           │
│                                                                              │
│  DYNAMICS                                                                     │
│  ├── vorticity                                                                │
│  ├── divergence                                                               │
│  ├── deformation                                                              │
│  ├── shear                                                                     │
│  └── vertical motion                                                          │
│                                                                              │
│  STABILITY                                                                    │
│  ├── CAPE                                                                     │
│  ├── CIN                                                                      │
│  ├── LCL                                                                      │
│  ├── LFC                                                                      │
│  ├── EL                                                                       │
│  └── stability indices                                                        │
│                                                                              │
│  BOUNDARY LAYER                                                               │
│  TURBULENCE                                                                   │
│  CLOUD PHYSICS                                                                │
│  RADIATION                                                                    │
│  PRECIPITATION                                                                │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                         10. DIAGNOSTIC ENGINE                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Thermodynamic diagnostics                                                    │
│  Dynamic diagnostics                                                          │
│  Kinematic diagnostics                                                        │
│  Moisture diagnostics                                                         │
│  Stability diagnostics                                                        │
│  Convection diagnostics                                                       │
│  Wind diagnostics                                                             │
│  Precipitation diagnostics                                                    │
│  Cloud diagnostics                                                            │
│  Boundary-layer diagnostics                                                   │
│  Severe-weather diagnostics                                                   │
│  Vertical diagnostics                                                         │
│                                                                              │
│  Chaque diagnostic possède :                                                  │
│  ├── définition                                                               │
│  ├── unités                                                                    │
│  ├── dépendances                                                               │
│  ├── référence scientifique                                                   │
│  ├── tests                                                                     │
│  └── provenance                                                                │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                  ┌─────────────────┼──────────────────┐
                  │                 │                  │
                  ▼                 ▼                  ▼

┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────────┐
│ 11. OBSERVATION      │ │ 12. ENSEMBLE ENGINE  │ │ 13. MODEL COMPARISON     │
│ / ASSIMILATION       │ │                      │ │                          │
├──────────────────────┤ ├──────────────────────┤ ├──────────────────────────┤
│ stations             │ │ members              │ │ ARPEGE                   │
│ radiosondes          │ │ mean                 │ │ AROME                    │
│ aircraft             │ │ median               │ │ ALADIN                   │
│ radar                │ │ spread               │ │ WRF                      │
│ satellite            │ │ variance             │ │ ICON                     │
│ observations         │ │ percentiles          │ │ OpenIFS                  │
│ analysis             │ │ probability          │ │                          │
│ innovations          │ │ clustering           │ │ variable comparison      │
│ bias                 │ │ distributions        │ │ spatial comparison       │
└──────────────────────┘ └──────────────────────┘ │ temporal comparison      │
                  │                 │             │ vertical comparison      │
                  └─────────────────┼─────────────┴──────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                         14. CONSENSUS ENGINE                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Model agreement                                                              │
│  Model disagreement                                                           │
│  Model spread                                                                 │
│  Model weighting                                                              │
│  Bias-aware weighting                                                         │
│  Consensus field                                                              │
│  Consensus probability                                                        │
│  Confidence                                                                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                        15. UNCERTAINTY ENGINE                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Forecast uncertainty                                                         │
│  Model uncertainty                                                            │
│  Ensemble uncertainty                                                         │
│  Observation uncertainty                                                      │
│  Initial-condition uncertainty                                                │
│  Diagnostic uncertainty                                                       │
│                                                                              │
│  OUTPUT                                                                       │
│  ├── probability                                                              │
│  ├── spread                                                                    │
│  ├── confidence                                                               │
│  ├── uncertainty field                                                        │
│  └── confidence profile                                                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                          16. EVENT ENGINE                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Threshold detection                                                         │
│  Multi-variable detection                                                     │
│  Spatial detection                                                            │
│  Temporal detection                                                           │
│  Pattern detection                                                            │
│  Event tracking                                                               │
│                                                                              │
│  EVENTS                                                                       │
│  ├── convection                                                               │
│  ├── severe storms                                                            │
│  ├── heavy precipitation                                                      │
│  ├── flash-flood potential                                                    │
│  ├── strong wind                                                              │
│  ├── hail                                                                     │
│  ├── snow                                                                     │
│  ├── freezing rain                                                            │
│  ├── fog                                                                      │
│  ├── heat                                                                     │
│  ├── cold                                                                     │
│  ├── dust                                                                     │
│  └── aviation hazards                                                        │
│                                                                              │
│  Event Object                                                                 │
│  ├── location                                                                 │
│  ├── time                                                                      │
│  ├── duration                                                                  │
│  ├── vertical extent                                                          │
│  ├── severity                                                                 │
│  ├── probability                                                              │
│  ├── confidence                                                               │
│  └── supporting models                                                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                       17. COMPLEXITY ENGINE                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Instability                                                                 │
│  Moisture                                                                    │
│  Shear                                                                       │
│  Forcing                                                                     │
│  Vertical structure                                                          │
│  Spatial gradients                                                           │
│  Temporal evolution                                                          │
│  Model disagreement                                                          │
│  Observation support                                                         │
│                                                                              │
│                         ↓                                                    │
│                                                                              │
│                    ATMOSPHERIC COMPLEXITY                                    │
│                                                                              │
│  ├── complexity index                                                        │
│  ├── dominant processes                                                       │
│  ├── forecast difficulty                                                     │
│  └── confidence                                                              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                     18. ATMOSPHERIC INTELLIGENCE                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Feature extraction                                                          │
│  Pattern recognition                                                         │
│  Regime detection                                                            │
│  Anomaly detection                                                           │
│  Event correlation                                                           │
│  Evolution analysis                                                          │
│  Risk classification                                                         │
│  Explainability                                                              │
│                                                                              │
│  IMPORTANT:                                                                  │
│  L'intelligence exploite les produits scientifiques validés.                 │
│  Elle ne remplace pas le Physics Engine.                                    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼

┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────────┐
│ 19. ENVIRONMENT      │ │ 20. SPECIALIZED      │ │ 21. DIGITAL TWIN        │
│                      │ │ WEATHER SERVICES      │ │                          │
├──────────────────────┤ ├──────────────────────┤ ├──────────────────────────┤
│ LAND                 │ │ AVIATION             │ │ Current state            │
│ ├── soil             │ │ ├── icing            │ │ Analysis                 │
│ ├── vegetation       │ │ ├── turbulence       │ │ Forecast                 │
│ └── surface          │ │ ├── wind shear       │ │ Scenarios                │
│                      │ │ ├── ceiling          │ │ What-if                  │
│ OCEAN                │ │ └── visibility       │ │ Sensitivity              │
│ ├── SST              │ │                      │ │ Evolution                │
│ ├── currents         │ │ FIRE WEATHER         │ │                          │
│ └── waves            │ │ ├── fire indices     │ │                          │
│                      │ │ ├── fuel conditions   │ │                          │
│ AEROSOLS / DUST      │ │ └── smoke transport  │ │                          │
│ ├── concentration    │ │                      │ │                          │
│ ├── transport        │ │ CLIMATE              │ │                          │
│ └── visibility       │ │ ├── climatology      │ │                          │
│                      │ │ ├── anomalies        │ │                          │
│ SATELLITE / RADAR    │ │ └── extremes         │ │                          │
└──────────────────────┘ └──────────────────────┘ └──────────────────────────┘
                  │                 │                 │
                  └─────────────────┼─────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                         22. PRODUCT ENGINE                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  HORIZONTAL                                                                   │
│  ├── maps                                                                     │
│  ├── contours                                                                 │
│  ├── vectors                                                                  │
│  ├── wind barbs                                                               │
│  ├── precipitation                                                            │
│  ├── probability                                                              │
│  └── risk                                                                     │
│                                                                              │
│  VERTICAL                                                                     │
│  ├── profiles                                                                 │
│  ├── soundings                                                                │
│  ├── Skew-T                                                                   │
│  ├── cross sections                                                           │
│  └── vertical composites                                                      │
│                                                                              │
│  TEMPORAL                                                                     │
│  ├── time series                                                              │
│  ├── Hovmöller                                                                │
│  └── event evolution                                                          │
│                                                                              │
│  3D                                                                           │
│  ├── volumes                                                                  │
│  ├── isosurfaces                                                              │
│  ├── particles                                                                │
│  ├── clouds                                                                    │
│  └── wind structures                                                          │
│                                                                              │
│  4D                                                                           │
│  └── 3D + time                                                                │
│                                                                              │
│  MULTI-MODEL                                                                  │
│  ├── model comparison                                                          │
│  ├── ensemble                                                                  │
│  ├── consensus                                                                 │
│  └── uncertainty                                                               │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                      23. VISUALIZATION ENGINE                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                                 2D                                           │
│                                  │                                           │
│                    ┌─────────────┴─────────────┐                             │
│                    │                           │                             │
│                   MAP                     DIAGNOSTICS                        │
│                                                                              │
│                                 3D                                           │
│                                  │                                           │
│              ┌───────────────────┼────────────────────┐                      │
│              │                   │                    │                      │
│            TERRAIN            VOLUME              VECTORS                    │
│              │                   │                    │                      │
│              └───────────────────┼────────────────────┘                      │
│                                  │                                           │
│                                 4D                                           │
│                                  │                                           │
│                        TIME + 3D EVOLUTION                                   │
│                                                                              │
│  Vertical controls                                                           │
│  ├── surface                                                                   │
│  ├── 2 m                                                                       │
│  ├── 10 m                                                                      │
│  ├── pressure levels                                                           │
│  ├── model levels                                                              │
│  ├── height levels                                                             │
│  └── custom layers                                                             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                         24. DASHBOARD                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ MODEL │ RUN │ TIME │ LEVEL │ VARIABLE │ PRODUCT │ DOMAIN             │  │
│  ├────────────────────────────────────────────────────────────────────────┤  │
│  │                                                                        │  │
│  │                           2D / 3D / 4D                                  │  │
│  │                                                                        │  │
│  ├───────────────────────────┬────────────────────────────────────────────┤  │
│  │ Diagnostics               │ Consensus / Uncertainty                    │  │
│  ├───────────────────────────┴────────────────────────────────────────────┤  │
│  │ Vertical Profile / Cross Section / Time Series                         │  │
│  ├────────────────────────────────────────────────────────────────────────┤  │
│  │ Events │ Alerts │ Risk │ Explanation │ Model Comparison                │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼

┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────────┐
│ 25. API / DELIVERY   │ │ 26. REAL-TIME        │ │ 27. HPC / COMPUTE        │
├──────────────────────┤ ├──────────────────────┤ ├──────────────────────────┤
│ REST API             │ │ scheduler            │ │ SLURM                    │
│ WebSocket            │ │ data arrival         │ │ distributed jobs         │
│ product API          │ │ streaming            │ │ parallel processing      │
│ event API            │ │ triggers             │ │ Dask-compatible          │
│ dataset API          │ │ automatic pipeline    │ │ memory-aware             │
│ metadata API         │ │ monitoring            │ │ batch processing         │
│                      │ │                      │ │ interactive processing   │
│ alerts               │ │                      │ │                          │
│ reports              │ │                      │ │                          │
└──────────────────────┘ └──────────────────────┘ └──────────────────────────┘
                  │                 │                 │
                  └─────────────────┼─────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                    28. PROVENANCE / OBSERVABILITY                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  DATA PROVENANCE                                                             │
│  ├── source                                                                    │
│  ├── model                                                                     │
│  ├── run                                                                       │
│  ├── variable                                                                  │
│  ├── units                                                                     │
│  ├── transformations                                                           │
│  ├── regridding                                                                │
│  ├── diagnostics                                                               │
│  └── software/configuration                                                    │
│                                                                              │
│  OBSERVABILITY                                                                │
│  ├── logs                                                                      │
│  ├── metrics                                                                   │
│  ├── performance                                                               │
│  ├── memory                                                                    │
│  ├── CPU                                                                       │
│  ├── I/O                                                                       │
│  ├── health                                                                    │
│  └── pipeline status                                                           │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

┌──────────────────────────────────────────────────────────────────────────────┐
│                     29. VERIFICATION & CERTIFICATION                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  UNIT TESTS                                                                   │
│  SCIENTIFIC TESTS                                                             │
│  NUMERICAL TESTS                                                              │
│  REFERENCE TESTS                                                              │
│  REGRESSION TESTS                                                             │
│  MODEL ADAPTER TESTS                                                          │
│  INTEGRATION TESTS                                                            │
│  END-TO-END TESTS                                                             │
│  PERFORMANCE TESTS                                                            │
│  VISUALIZATION TESTS                                                          │
│  HPC TESTS                                                                    │
│  RECOVERY TESTS                                                               │
│                                                                              │
│                         CERTIFICATION                                        │
│                                                                              │
│                 DRAFT → VALIDATED → CERTIFIED → PUBLISHED                    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼

                         ┌─────────────────────┐
                         │    ACF PRODUCTION   │
                         │                     │
                         │  CERTIFIED OUTPUT   │
                         └─────────────────────┘
```

## 2. Les 30 niveaux font une seule chaîne

```text
INPUT → INGESTION → INSPECTION → NORMALIZATION → QC → PHYSICS GUARD →
GRID/VERTICAL → ATMOSPHERIC STATE → 4D STATE → PHYSICS → DIAGNOSTICS →
OBSERVATIONS → MULTI-MODEL → ENSEMBLE → CONSENSUS → UNCERTAINTY →
EVENTS → COMPLEXITY → INTELLIGENCE → SPECIALIZED SERVICES → PRODUCTS →
VISUALIZATION → DASHBOARD → API/REAL-TIME/HPC → PROVENANCE →
VERIFICATION → CERTIFICATION → PRODUCTION
```

## 3. Structure du code cible

```text
src/acf/
├── core/            ├── diagnostics/     ├── radar/           ├── api/
├── data/            ├── observations/    ├── satellite/       ├── realtime/
├── ingestion/       ├── assimilation/    ├── land/            ├── workflow/
├── models/          ├── ensemble/        ├── ocean/           ├── storage/
├── normalization/   ├── comparison/      ├── aerosols/        ├── monitoring/
├── qc/              ├── consensus/       ├── fire_weather/    └── verification/
├── physics/         ├── uncertainty/     ├── aviation/
├── grid/            ├── events/          ├── climate/
├── vertical/        ├── complexity/      ├── simulation/
├── state/           ├── intelligence/    ├── products/
├── model4d/                              ├── visualization/
                                           └── dashboard/
```

## 4. Objet central unique — ACF Atmospheric State

```text
                         ACF ATMOSPHERIC STATE
                                  │
                    ┌─────────────┼─────────────┐
                  SPACE         VERTICAL       TIME
                    └─────────────┼─────────────┘
                               X Y Z T
                    ┌─────────────┼─────────────┐
                VARIABLES      MODELS       OBSERVATIONS
                    └─────────────┼─────────────┘
                           SCIENTIFIC STATE
```

## 5. Règle architecturale absolue

Un nouveau module ACF doit toujours répondre à :

1. Où entre-t-il dans la chaîne ?
2. Quelle donnée reçoit-il ?
3. Quel contrat utilise-t-il ?
4. Quelle transformation effectue-t-il ?
5. Quelle validation lui est appliquée ?
6. Quel produit produit-il ?
7. Quelle provenance conserve-t-il ?
8. Quels tests certifient son résultat ?

Si ces huit réponses ne sont pas définies, le module n'est pas prêt à entrer dans ACF.

## 6. Définition finale d'ACF

```text
              ┌──────────────────────────────┐
              │            ACF                │
              │ Atmospheric Complexity        │
              │ Framework                     │
              │                                │
              │ DATA + PHYSICS + MULTI-MODEL   │
              │ + OBSERVATIONS + DIAGNOSTICS   │
              │ + UNCERTAINTY + EVENTS         │
              │ + COMPLEXITY + INTELLIGENCE    │
              │ + 4D + PRODUCTS                │
              │ + VISUALIZATION + DASHBOARD    │
              │ + HPC + REAL-TIME              │
              │ + CERTIFICATION                │
              └──────────────────────────────┘
```

C'est cette architecture unique qui doit servir de référence pour tout le
développement ACF v1.0.
