# ATMOSPHERIC COMPLEXITY FRAMEWORK (ACF)
## EARTH SYSTEM OPERATIONS CENTER (ESOC)
### OFFICIAL NAVIGATION SYSTEM ENGINEERING SPECIFICATION — ACF-UI-003

---

## EXECUTIVE SUMMARY

The **Earth System Operations Center (ESOC) Official Navigation System** defines the hierarchical, multi-perspective navigation framework for the **Atmospheric Complexity Framework (ACF)**.

Designed to manage hundreds of scientific modules across meteorology, climatology, oceanography, hydrology, cryosphere, space weather, atmospheric chemistry, artificial intelligence, and HPC digital twin operations, the navigation system guarantees **instant access in <= 2 clicks** while preserving visual elegance, low cognitive load, and infinite scalability.

---

## 1. DESIGN PHILOSOPHY & ERGONOMIC PRINCIPLES

1. **Fast Access & Minimal Clicks**: Every operational tool or physical variable module is accessible within 2 clicks from the main workspace.
2. **Scientific Domain Organization**: Modules are grouped strictly according to Earth System domains (Atmosphere, Hydrosphere, Cryosphere, Lithosphere, Heliosphere, Anthroposphere, and HPC/AI Compute).
3. **Workspace-Aware Perspective Switching**: Switching workspaces dynamically filters visible navigation trees, docks, layer panels, and tool palettes.
4. **Zero-Lag Virtualized Rendering**: Designed for instant rendering of 500+ submodules using virtualized model-view architecture.
5. **Infinite Scalability**: New satellite constellations, NWP models, or AI surrogates integrate seamlessly into existing taxonomy without UI redesign.

---

## 2. NAVIGATION PANEL STATES & MODES

The navigation system is implemented as a collapsible, high-density left sidebar with 5 interactive display modes:

1. **Expanded Mode (260px)**: Full category labels, badge counters, submodule counts, and expand/collapse chevrons.
2. **Collapsed / Icons-Only Mode (64px)**: Minimalist icon strip with hover tooltips displaying submodules and live badge counters.
3. **Auto-Hide / Floating Drawer Mode**: Slides out on mouse proximity or keyboard shortcut (`Ctrl + B`), auto-collapses on canvas focus.
4. **Pinned Mode**: Locked in place; resizes central 3D Earth canvas dynamically.
5. **Split Dual-Panel Mode**: Used on Ultra-Wide or Multi-Monitor setups to pin Level 1 (Categories) and Level 2 (Submodules) side-by-side.

---

## 3. HIERARCHICAL TREE ARCHITECTURE (LEVELS 1, 2, AND 3)

The navigation hierarchy follows a strict 3-tier structure:

### LEVEL 1 — MAIN CATEGORIES (PRIMARY TREE)
- 📊 **Dashboard**: System overview, mission status, real-time KPI ribbon.
- 🌐 **Earth System**: Planetary state vector, 4D Digital Twin coupling, mass/energy budgets.
- 🌤️ **Weather (Atmosphere)**: Synoptic, mesoscale, convective, boundary layer, dynamics.
- 🌡️ **Climate**: CMIP6 projections, ERA5 reanalyses, climate indices, paleoclimate.
- 🌊 **Ocean**: Sea surface temperature, salinity, currents, wave spectra, sea level.
- 💧 **Hydrology**: River discharge, flood inundation, soil moisture, groundwater, reservoirs.
- 🧊 **Cryosphere**: Sea ice extent, ice sheet thickness, snow water equivalent (SWE), glaciers.
- 🌿 **Land Surface & Biosphere**: LAI, NDVI, land cover, soil temperature, carbon sinks.
- 🌫️ **Air Quality & Chemistry**: PM2.5, PM10, O3, NO2, SO2, volcanic ash, dust transport.
- 🔄 **Carbon Cycle & Greenhouse Gases**: CO2/CH4 fluxes, DACCS, ocean carbon uptake.
- ⚡ **Space Weather & Heliophysics**: Solar wind, Kp/Dst indices, ionospheric TEC, aurora.
- 🌋 **Natural & Cosmic Hazards**: Tropical cyclones, floods, tsunamis, earthquakes, asteroids.
- 🔮 **Forecast Models (NWP)**: IFS, AROME, ICON, GFS, WRF, MPAS deterministic & ensemble runs.
- 🤖 **Artificial Intelligence**: GraphCast, AIFS, NeuralGCM, Pangu, FourCastNet, PINN surrogates.
- 🛰️ **Observations & Remote Sensing**: WIGOS SYNOP, Satellites (GOES/MTG/Sentinel), Radar composites.
- 📊 **Forecast Verification**: RMSE, Anomaly Correlation Coefficient (ACC), Reliability Diagrams.
- 📑 **Reports & Briefings**: Executive summary generator, ICAO aviation briefings, civil protection bulletins.
- 🖥️ **HPC & Infrastructure**: Slurm cluster status, MPI topology, GPU vRAM, node telemetry.
- ⚙️ **Settings & Administration**: System preferences, plugin manager, security, licenses.

### LEVEL 2 — SCIENTIFIC SUBMODULES (SECONDARY BRANCHES)
*Example: Category "Weather"*
- **Surface Analysis**: SYNOP maps, surface pressure QFF, 10m wind vector field.
- **Upper Air & Jet Streams**: 500 hPa geopotential height, 300 hPa jet streak divergence.
- **Thermodynamics & Stability**: Soundings (Skew-T/Emagram), CAPE, CIN, Lifted Index.
- **Convection & Severe Storms**: Helicity (SREH), STP index, hail detection (MESH).
- **Cyclogenesis**: Upper-level PV anomaly tracking, baroclinic instability diagnostics.

### LEVEL 3 — OPERATIONAL SCIENTIFIC TOOLS (ACTION TERMINALS)
*Example: Submodule "Convection"*
- 🗺️ **Interactive Layer Canvas**: 2D/3D visual layer toggle.
- 📈 **Vertical Profile Sounding Viewer**: Skew-T parcel trajectory simulation.
- 📊 **Ensemble Dispersion Plot**: Multi-model CAPE spread boxplots.
- 🤖 **AI Convective Hazard Reasoning**: Automatic XAI explanation of convective triggers.
- 📑 **Export & Alert Generator**: Issue Severe Thunderstorm Warning bulletin.

---

## 4. WORKSPACE SYSTEM & PRESET SWITCHER

The navigation system supports **Dynamic Workspaces**. Selecting a workspace automatically reconfigures navigation trees, default layers, and tool palettes:

1. 🚨 **Operational Weather Forecast Workspace**: Focuses on Radar, Satellite, CAPE, Jet Streams, and Warnings.
2. 🔬 **Climate Research & Projections Workspace**: Focuses on CMIP6 SSP scenarios, ERA5 trends, and Carbon Cycle.
3. 🚢 **Marine Navigation & Oceanography Workspace**: Focuses on Wave Height Hs, Ocean Currents, SST, and Sea State.
4. 🌊 **Hydrology & Flood Early Warning Workspace**: Focuses on LISFLOOD discharge, river networks, and rainfall QPE.
5. ✈️ **Aviation Meteorology & Flight Safety Workspace**: Focuses on CAT Turbulence (EDR), SLW Icing, METAR/TAF.
6. 😷 **Air Quality & Atmospheric Chemistry Workspace**: Focuses on PM2.5, O3 dispersion, and volcanic ash VAAC.
7. ☀️ **Space Weather & Satellite Operations Workspace**: Focuses on Solar Flares, Kp index, and Ionospheric TEC.
8. 🏛️ **Civil Protection & Emergency Operations Workspace**: Focuses on Multi-hazard cascade graphs and evacuation alerts.

---

## 5. FAVORITES, RECENT MODULES & QUICK ACCESS

- **⭐ Favorites Bar (Pinned Header)**: Allows operators to drag-and-drop or star frequently used modules (e.g. `⭐ Live Radar`, `⭐ GraphCast vs IFS`, `⭐ CAPE Sounding`).
- **🕒 Recent Modules List**: Maintains an automated history of the last 10 visited tools.
- **⚡ Quick Access Action Buttons**: Dedicated 1-click launch buttons for `Live Satellite`, `Active Alerts`, `AI Assistant`, and `Digital Twin Replay`.

---

## 6. UNIVERSAL NAVIGATION SEARCH & CONTEXT MENUS

- **Intelligent Search Engine (`Ctrl + Shift + F`)**: Real-time fuzzy matching across module titles, physical variables (`temperature`, `vorticity`), WMO codes, NetCDF keys, and Python functions.
- **Rich Context Menu (Right-Click on any item)**:
  - `Open in Main Workspace`
  - `Open in New Window / Floating Dock`
  - `Add to Pinned Favorites`
  - `Copy Physical Equation / Reference`
  - `Inspect Source Module Code & Documentation`

---

## 7. NOTIFICATION INTEGRATION & BADGES

Navigation nodes dynamically render color-coded badge counters indicating live events:
- 🔴 **Weather (3 Alerts)**: 3 Active Warnings in current domain.
- 🟣 **AI (2 Recommendations)**: 2 AI forecast discrepancy alerts.
- 🟡 **HPC (1 Warning)**: Node 4 Memory Pressure.
- 🟢 **Reports (Complete)**: Executive Briefing compiled successfully.

---

## 8. ACCESSIBILITY, RESPONSIVENESS & PERFORMANCE GUIDELINES

1. **Lazy Loading Architecture**: Tree nodes load submodules on demand; zero initial memory overhead for 500+ items.
2. **Keyboard Navigation Shortcuts**: Full navigation support using Arrow keys, `Tab`, `Enter`, `Esc`, and Alt-mnemonics.
3. **High-DPI & Multi-Monitor Sync**: State changes on the master navigation sidebar instantly synchronize across attached monitor walls.

---

## 9. QT / PYSIDE6 ARCHITECTURE RECOMMENDATIONS

- **Implementation Base**: `QFrame` wrapper with a virtualized `QTreeView` backing a custom `QAbstractItemModel`.
- **Styling**: Modern QSS stylesheet with CSS variables for dynamic palette switching (Dark/OLED/High-Contrast).
- **Thread Safety**: Badge updates and search index operations execute on a background `QThread`.

---

## 10. SPECIFICATION SUMMARY

The **ACF-UI-003 ESOC Official Navigation System Specification** guarantees a highly scalable, scientifically structured, zero-lag navigation architecture capable of driving the entire **Atmospheric Complexity Framework v1.0 Production Release**.
