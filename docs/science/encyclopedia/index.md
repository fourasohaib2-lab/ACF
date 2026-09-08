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

# ACF Computational Scientific Encyclopedia Index

## 1. Overview
The **ACF Computational Scientific Encyclopedia Engine** is an integrated knowledge base and numerical execution system for atmospheric physics, thermodynamics, cloud microphysics, convection, dynamics, radiative transfer, atmospheric chemistry, ocean-atmosphere coupling, cryosphere, NWP numerical models, satellite remote sensing, radar meteorology, aeronautics, and applied mathematics.

---

## 2. Key Domains & Formulations

### 2.1 Atmospheric Physics
- **Ideal Gas Law**: $p = \rho R_d T$
- **Hydrostatic Equilibrium**: $\frac{\partial p}{\partial z} = -\rho g$
- **Hypsometric Equation**: $z_2 - z_1 = \frac{R_d \bar{T}_v}{g} \ln\left(\frac{p_1}{p_2}\right)$
- **Boussinesq Approximation**: $\frac{D\mathbf{u}}{Dt} = -\frac{1}{\rho_0}\nabla p^\prime + B\mathbf{k} + \nu \nabla^2\mathbf{u}$

### 2.2 Numerical Weather Prediction (NWP) Models
- **ECMWF IFS**: TCo1279 octahedrally reduced spectral grid, 137 vertical levels up to 0.01 hPa.
- **AROME (Météo-France)**: Non-hydrostatic Euler equations at 1.3 km resolution, ICE3 microphysics.
- **ICON (DWD)**: Triangular icosahedral grid, non-hydrostatic global & regional formulation.

### 2.3 Knowledge Graph Engine
The `KnowledgeGraphEngine` maps causal relationships across phenomena:
$$\text{CAPE} \longrightarrow \text{Convective Instability} \longrightarrow \text{Updraft} \longrightarrow \text{Cumulonimbus} \longrightarrow \text{Lightning / Hail / Heavy Rain}$$

---

## 3. Usage Examples

```python
from acf.science.encyclopedia import EncyclopediaRegistry, KnowledgeGraphEngine

# 1. Lookup entry by key
entry = EncyclopediaRegistry.get("ideal_gas_law")
print("Equation:", entry.latex_equation)

# 2. Perform computation
p = EncyclopediaRegistry.calculate("ideal_gas_law", density=1.225, temperature=288.15)
print("Pressure (Pa):", p)

# 3. Traversal in Knowledge Graph
graph = KnowledgeGraphEngine()
path = graph.find_path("cape", "lightning")
print("Causal Chain:", " -> ".join(path))
```

---

## 4. References
- WMO-No. 8: Guide to Meteorological Instruments and Methods of Observation.
- ECMWF IFS Model Documentation.
- NOAA NCEP Technical Reports.
- ICAO Doc 7488/3: Manual of the ICAO Standard Atmosphere.
- Holton, J. R., & Hakim, G. J. (2012). An Introduction to Dynamic Meteorology.
