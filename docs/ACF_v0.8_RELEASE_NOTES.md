# ACF v0.8 RELEASE NOTES

**Release Version:** v0.8.0  
**Release Date:** August 6, 2026  

---

## 🚀 Key Highlights & New Capabilities

1. **Data Assimilation Engine (`DataAssimilationEngine`)**:
   - Integrated observation processing pipeline supporting Doppler radial wind, radar reflectivity, satellite radiances, and brightness temperatures.
2. **Multi-Method Assimilation Solvers**:
   - Unified analysis increment $x_a = x_b + K (y - H(x_b))$ solver supporting 3D-Var, 4D-Var, and Ensemble Kalman Filter (EnKF) assimilation cycles.
3. **Automated Observation Quality Control (QC)**:
   - Range checks, spatial consistency checks, and observation operator $H$ evaluations.
