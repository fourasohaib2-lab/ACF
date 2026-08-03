# ATMOSPHERIC COMPLEXITY FRAMEWORK (ACF)
## EARTH SYSTEM OPERATIONS CENTER (ESOC)
### OFFICIAL OPERATIONAL TOOLBAR ENGINEERING SPECIFICATION — ACF-UI-004

---

## EXECUTIVE SUMMARY

The **Earth System Operations Center (ESOC) Official Operational Toolbar** defines the persistent, bottom-anchored command bar for the **Atmospheric Complexity Framework (ACF)** and **Atmospheric Weather Center Interface (AWCI)**.

Positioned permanently at the base of the application viewport (height 36px–44px), the toolbar acts as an operational command bar, giving meteorologists, climate scientists, oceanographers, hydrologists, AI researchers, and emergency coordinators instant 1-click access to the most vital scientific tools, visualization diagnostics, AI copilots, and HPC controls.

---

## 1. DESIGN PHILOSOPHY & OPERATIONAL PRINCIPLES

1. **Maximum Operational Productivity**: Minimizes mouse travel distance by placing high-frequency scientific tools within a fixed bottom bar.
2. **Context-Aware Dynamic Adaptation**: The central section of the toolbar dynamically presents domain-specific tool groups based on the active module (e.g. Weather, Climate, Ocean, Air Quality).
3. **1-Click Execution**: Critical operations (Run Forecast, Compare Models, Launch AI Diagnostics, Issue Warning) trigger instantly with zero multi-level menu navigation.
4. **State Machine-Driven Availability**: Buttons reflect real-time service readiness (e.g., *Run Forecast* disables gracefully if data ingestion is pending).
5. **Zero Performance Footprint**: Event-driven UI updates guarantee 60 FPS rendering on 3D Earth System canvases without UI redraw lag.

---

## 2. TOOLBAR POSITION, MODES & RESPONSIVE BEHAVIOR

- **Anchor Position**: Fixed persistent bottom bar at the base of AWCI main window.
- **Display Modes**:
  - `Fixed Mode` (Default): Locked at 40px height; reserves lower canvas border.
  - `Auto-Hide Mode`: Minimizes to a 4px accent line; expands on hover or `Ctrl + Shift + T`.
  - `Compact Mode`: Hides text labels, displaying vector icons with tooltips.
  - `Expanded Mode`: Displays icons, title text, and keyboard shortcut badges.
  - `Floating Mode`: Detaches into an independent floating tool palette for multi-monitor video walls.

---

## 3. FUNCTIONAL TOOL GROUPS (11 CORE ZONES)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HOME │ OBS │ FORECAST │ MODELS │ EARTH SYSTEM │ ANALYSIS │ AI │ HAZARDS │ REPORTS │ HPC │ SETTINGS │ QUICK PINNED ACTIONS │ SEARCH │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### GROUP 1 — HOME & WORKSPACE MANAGEMENT
- **Dashboard**: Main operational KPI view.
- **Mission Control**: Active campaign monitor.
- **Workspace Selector**: Quick workspace preset switcher.
- **Favorites & Pinned Views**: Access to pinned custom views.

### GROUP 2 — OBSERVATIONS & REMOTE SENSING
- **Satellite**: GOES, Meteosat MTG, Sentinel RGB & IR channels.
- **Radar Composite**: NEXRAD / PANTHERE reflectivity & Doppler velocity.
- **Lightning Network**: GLM / WWLLN flash density mapping.
- **In-Situ Surface & Upper-Air**: SYNOP, Radiosondes (TEMP), AMDAR Aircraft.
- **Ocean & Hydrology Sensors**: ARGO floats, LISFLOOD discharge gauges.

### GROUP 3 — FORECAST OPERATIONS
- **Nowcasting**: 0-6h extrapolation and AI Nowcasting (GraphCast-NWC).
- **Short & Medium Range**: 24h to 10-day deterministic & ensemble runs.
- **Extended & Seasonal**: Sub-seasonal to seasonal (S2S) forecasts.
- **Forecast Comparison & Spread**: Multi-model ensemble dispersion plots.

### GROUP 4 — NUMERICAL & AI MODELS
- **Deterministic NWP**: IFS, AROME, ICON, GFS, WRF, MPAS.
- **AI Surrogate Models**: GraphCast, AIFS, NeuralGCM, Pangu, FourCastNet.
- **Ensemble Matrix**: 50-member IFS EPS + GenCast stochastic ensemble.

### GROUP 5 — EARTH SYSTEM SPHERES
- **Atmosphere & Dynamics**: Wind, Pressure, Vorticity, Jet Streams.
- **Climate & CMIP6**: SSP scenarios, ERA5 trends, carbon budget.
- **Ocean & Waves**: Wave Height Hs, Ocean Currents, SST anomalies.
- **Hydrology & Cryosphere**: River discharge, Sea ice concentration.
- **Space Weather & Geology**: Solar flares, Kp index, USGS Seismicity.

### GROUP 6 — ANALYSIS & DIAGNOSTICS
- **Thermodynamics**: Skew-T Sounding, Emagram 761, Hodographs.
- **Cross Sections & Vertical Cuts**: 2D/3D atmospheric vertical slices.
- **Time Series & Heatmaps**: Hovmöller diagrams, Hovmöller longitude-time plots.
- **Verification Metrics**: RMSE, Anomaly Correlation (ACC), Taylor diagrams.

### GROUP 7 — ARTIFICIAL INTELLIGENCE & XAI
- **AI Copilot**: Autonomous AI Meteorologist assistant.
- **Forecast Explanation**: XAI physical evidence & reference generator.
- **Pattern Recognition**: Automated front & cyclogenesis detection.
- **Natural Language Query**: Text search interface (`Ctrl + K`).

### GROUP 8 — NATURAL & COSMIC HAZARDS
- **Severe Storms & Hail**: MESH hail size, STP tornado parameter.
- **Tropical Cyclones**: IBTrACS track & rapid intensification alert.
- **Floods & Surges**: 100-year flood inundation, storm surge.
- **Wildfires & Air Quality**: Dust transport, PM2.5, Volcanic ash.

### GROUP 9 — REPORTS & BRIEFINGS
- **Executive Summary**: One-click daily briefing compiler.
- **Aviation Briefing**: ICAO SIGWX / METAR / TAF package.
- **Export & Share**: PDF, PowerPoint, GeoTIFF, NetCDF export.

### GROUP 10 — HPC & INFRASTRUCTURE
- **HPC Telemetry**: Real-time CPU, RAM, GPU vRAM, Network gauges.
- **Slurm & Cluster Queue**: Active MPI jobs and node health.

### GROUP 11 — GLOBAL SETTINGS
- **System Preferences**: Theme, units (SI/Imperial/KT), language, plugins.

---

## 4. CONTEXTUAL TOOLBAR ADAPTATION LOGIC

The central section of the toolbar automatically morphs based on the active module:
- **Active Module: Weather** → Displays `[Satellite | Radar | Lightning | Skew-T Sounding | CAPE | Hodograph]`.
- **Active Module: Climate** → Displays `[CMIP6 SSPs | ERA5 Reanalysis | Anomalies | Carbon Fluxes | Trend Plot]`.
- **Active Module: Ocean** → Displays `[Wave Height Hs | Currents | SST Anomaly | Marine Warning | Salinity]`.
- **Active Module: Hydrology** → Displays `[River Discharge Q | Soil Moisture | Flood Risk | Spillway Control]`.
- **Active Module: Aviation** → Displays `[CAT Turbulence EDR | Icing Index | METAR Decoder | QNH | Flight Level]`.

---

## 5. CUSTOMIZATION, PROFILES & QUICK ACTIONS

- **Custom Quick-Action Pins**: Users can star or drag-and-drop any tool to the persistent right section of the toolbar (e.g., `⚡ Run GraphCast`, `⚡ Compare Models`, `⚡ Issue Alert`).
- **Toolbar Profiles**: Pre-configured profiles for *Forecaster*, *Research Scientist*, *HPC Administrator*, and *Civil Protection Commander*.
- **Quick Tool Search (`Ctrl + Space`)**: Popup command palette for instant tool execution.

---

## 6. PYSIDE6 / QT INTEGRATION ARCHITECTURE

- **Base Class**: `ESOCToolbar` derived from `QToolBar` / `QFrame`.
- **Action Management**: Uses a centralized `QActionGroup` registry mapped to `ActionID` strings.
- **State Machine**: Driven by an internal `ToolbarStateMachine` tracking application state (`DATA_LOADING`, `READY`, `COMPUTING`, `ALERT_ACTIVE`).
- **Performance**: Icons rendered as cached `QSvgRenderer` vectors; tooltips powered by lightweight rich-text popups.

---

## 7. SPECIFICATION SUMMARY

The **ACF-UI-004 ESOC Official Operational Toolbar Specification** defines a highly productive, context-aware command bar that unifies tool execution across all 45 engineering domains of **Atmospheric Complexity Framework Version 1.0 Production Release**.
