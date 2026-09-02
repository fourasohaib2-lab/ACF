<!-- ACF_RECONCILIATION_BANNER_2026-09-02 -->
> **⚠️ Historical / unverified document.** This file reads as a comprehensive
> capability specification but its completion/coverage claims were not
> independently reproduced. For the actual, reproducible test/status
> numbers, see [`../../ROADMAP.md`](../../ROADMAP.md) and
> [`../../README.md`](../../README.md)'s "Verified Status" section; for what
> has genuinely been audited and fixed since, see
> [`../ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md`](../ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md).
> Treat any specific number, percentage, or "CERTIFIED"/"COMPLETE" claim
> below as aspirational unless it also appears in one of those documents.
>
> _Banner added 2026-09-02 per `ROADMAP.md`'s "reconcile ~150 certificate/
> sprint-report documents" near-term priority, extended to `docs/`
> subdirectories during a hygiene cleanup pass — original content preserved
> unchanged below._

---

# ACF Cloud Physics Knowledge Engine Documentation

## 1. Overview
The **Atmospheric Complexity Framework (ACF) Cloud Physics Knowledge Engine** is a comprehensive, multi-scale physical simulation and reasoning engine for cloud processes. It integrates microphysics, thermodynamics, convective dynamics, WMO cloud classification, radiative transfer, aerosol interaction, severe weather indicators, data assimilation, and AI reasoning.

---

## 2. Scientific Equations & Formulations

### 2.1 Cloud Microphysics
- **Water Mass Conservation**:
  $$\frac{\partial (\rho q_x)}{\partial t} + \nabla \cdot (\rho q_x \mathbf{V}) = S_x$$
  where $q_x \in \{q_v, q_c, q_r, q_i, q_s, q_g\}$ represent water vapor, cloud water, rain, cloud ice, snow, and graupel mixing ratios.
- **Kessler Autoconversion**:
  $$P_{auto} = k_{auto} \max(q_c - q_{c,crit}, 0)$$
- **Collision-Coalescence**:
  $$P_{coll} = k_{coll} q_c q_r^{0.875}$$

### 2.2 Cloud Thermodynamics
- **Convective Available Potential Energy (CAPE)**:
  $$\text{CAPE} = \int_{\text{LFC}}^{\text{EL}} g \frac{T_{parcel} - T_{env}}{T_{env}} dz$$
- **Convective Inhibition (CIN)**:
  $$\text{CIN} = -\int_{\text{SFC}}^{\text{LFC}} g \frac{T_{parcel} - T_{env}}{T_{env}} dz$$
- **Lifting Condensation Level (LCL)**:
  $$z_{\text{LCL}} \approx 125 \times (T - T_d)$$

### 2.3 Cloud Convective Dynamics
- **Convective Mass Flux**:
  $$M = \rho w \sigma$$
- **Maximum Updraft Speed**:
  $$w_{max} = \sqrt{2 \cdot \text{CAPE}}$$

### 2.4 Cloud Radiation & Forcing
- **Cloud Optical Depth**:
  $$\tau = \frac{3 \cdot \text{LWP}}{2 \cdot \rho_w \cdot r_{eff}}$$
- **Stefan-Boltzmann Infrared Emission**:
  $$F = \epsilon \sigma T_{top}^4$$
- **Beer-Lambert Extinction**:
  $$I = I_0 e^{-\tau}$$

---

## 3. Package Architecture

```
src/acf/
├── science/
│   └── clouds/
│       ├── base.py            # CloudProcess dataclass
│       ├── registry.py        # CloudScientificRegistry
│       ├── microphysics.py    # CloudMicrophysicsEngine
│       ├── thermodynamics.py  # CloudThermodynamicsEngine
│       ├── dynamics.py        # CloudDynamicsEngine
│       ├── classification.py  # CloudClassificationEngine
│       ├── radiation.py       # CloudRadiationEngine
│       ├── aerosols.py        # CloudAerosolEngine
│       ├── severe_weather.py  # SevereWeatherCloudModule
│       └── assimilation.py    # CloudDataAssimilationEngine
└── ai/
    └── cloud_reasoning.py     # CloudReasoningEngine
```

---

## 4. Usage Examples

```python
from acf.science.clouds import (
    CloudScientificRegistry,
    CloudMicrophysicsEngine,
    CloudThermodynamicsEngine,
    CloudClassificationEngine,
)
from acf.ai.cloud_reasoning import CloudReasoningEngine

# 1. Evaluate a cloud process via Registry
autoconversion_rate = CloudScientificRegistry.calculate("kessler_autoconversion", qc=0.001)

# 2. Convective Sounding Analysis
thermo = CloudThermodynamicsEngine()
analysis = thermo.convective_sounding_analysis(
    z_levels=[0.0, 1000.0, 2000.0, 5000.0, 12000.0],
    p_levels=[1013.0, 900.0, 800.0, 500.0, 200.0],
    t_env=[298.15, 288.15, 278.15, 248.15, 218.15],
    td_env=[288.15, 280.15, 270.15, 230.15, 190.15],
)
print("CAPE:", analysis["CAPE_J_kg"])

# 3. Classify Cloud Genre
classifier = CloudClassificationEngine()
cloud_info = classifier.classify(
    base_altitude_m=1000.0,
    top_altitude_m=12000.0,
    temperature_c=25.0,
    relative_humidity=0.85,
    cape_j_kg=2500.0,
    radar_reflectivity_dbz=55.0,
)
print("Genre:", cloud_info["genre"])  # Cumulonimbus

# 4. AI Explanation
reasoner = CloudReasoningEngine()
explanation = reasoner.explain_cumulonimbus_formation(
    cape_j_kg=2500.0,
    surface_humidity_pct=85.0,
    low_level_convergence_s=3e-5,
    shear_0_6km_m_s=25.0,
)
print("Justification:", explanation["justification"])
```

---

## 5. References
- WMO-No. 8: Guide to Meteorological Instruments and Methods of Observation.
- WMO International Cloud Atlas (2017 Edition).
- ECMWF IFS Documentation - Cloud & Convection Parameterization Schemes.
- Holton, J. R., & Hakim, G. J. (2012). An Introduction to Dynamic Meteorology.
- Pruppacher, H. R., & Klett, J. D. (1997). Microphysics of Clouds and Precipitation.
- Kessler, E. (1969). On the Distribution and Continuity of Water Substance in Atmospheric Circulations.
- Liou, K. N. (2002). An Introduction to Atmospheric Radiation.
