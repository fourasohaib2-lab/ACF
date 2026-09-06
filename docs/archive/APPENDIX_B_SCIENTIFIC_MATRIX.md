<!-- ACF_RECONCILIATION_BANNER_2026-09-02 -->
> **⚠️ Historical / unverified document.** This file was auto-generated as part
> of an earlier documentation sprint, and its completion, certification, or
> "100%"-style claims were not independently reproduced. For the actual,
> reproducible test/status numbers, see [`ROADMAP.md`](../ROADMAP.md) and
> [`README.md`](../README.md)'s "Verified Status" section; for what has
> genuinely been audited and fixed since, see
> [`ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md`](ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md).
> Treat any specific number, percentage, or "CERTIFIED"/"COMPLETE" claim below
> as aspirational unless it also appears in one of those documents.
>
> _Banner added 2026-09-02 per `ROADMAP.md`'s "reconcile ~150 certificate/
> sprint-report documents" near-term priority — original content preserved
> unchanged below._

---

# APPENDIX B — SCIENTIFIC COVERAGE MATRIX (ACF-MISSION-001A)

| Scientific Discipline | Coverage % | Status | Implemented Components | Recommended Target Version | Priority |
| :--- | :---: | :---: | :--- | :---: | :---: |
| **Atmospheric Dynamics** | 95% | Production | Primitive equations, hydrostatic/non-hydrostatic solvers | v1.0 | High |
| **Thermodynamics & Microphysics** | 95% | Production | Moisture balance, ICE3/ICE4 schemes, cloud fraction | v1.0 | High |
| **Radiation & Convection** | 90% | Production | Shortwave/longwave solvers, explicit convection | v1.0 | High |
| **Land Surface Physics (SURFEX)** | 90% | Production | ISBA 3-layer soil model, snowpack energy balance | v1.0 | High |
| **Hydrology & Runoff** | 85% | Stable | River basin routing, infiltration, evapotranspiration | v1.0 | Medium |
| **Oceanography & Waves** | 85% | Stable | Wave height, wind-sea spectrum, SST coupling | v1.0 | Medium |
| **Space Weather & Ionosphere** | 80% | Stable | Kp/Dst indices, solar wind velocity, geomagnetic alerts | v1.0 | Medium |
| **Data Assimilation (DA)** | 80% | Stable | 3D-Var, 4D-Var, EnKF, Hybrid EnVar solvers | v1.0 | High |
| **Physics-Informed AI (PINNs/FNO)** | 85% | Production | Fourier Neural Operators, neural forecast engines | v1.0 | High |
