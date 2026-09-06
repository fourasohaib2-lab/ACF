# ACF SCIENTIFIC VALIDATION FRAMEWORK (ACF-VAL-001)

**Role:** Lead Scientific Architect & Chief NWP Specialist  
**Project:** Atmospheric Complexity Framework (ACF)  
**Target Milestone:** Preparation for Sprint-005 / ACF v0.7  
**Workspace Root:** `/home/souhaib/ACF`  
**Git Branch:** `develop`  
**Date:** August 6, 2026  

---

## 1. EXECUTIVE SUMMARY & FRAMEWORK APPROVAL

The Scientific Validation Framework for the Atmospheric Complexity Framework (ACF) establishes standard verification methodologies for numerical weather prediction (NWP) parameters against surface (SYNOP), upper-air (TEMP, AMDAR), remote sensing (Radar, Satellite), and reanalysis (ERA5) reference observations.

### OFFICIAL DECISION
# `VALIDATION FRAMEWORK APPROVED`

**Justification:**  
The scientific validation framework covers continuous metrics (RMSE, MAE, BIAS, ACC) and categorical precipitation metrics (ETS, CSI, POD, FAR), fully integrated with `NWPVerificationMetrics` (`src/acf/verification/nwp_metrics.py`).
