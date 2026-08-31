# ACF VALIDATION WORKFLOW SPECIFICATION (ACF-VAL-001)

```
NWP Forecast Outputs (FA / GRIB2 / NetCDF)
  │
  ▼
[OBSERVATION MATCHING] (Nearest-neighbor / Bilinear spatial matching to SYNOP/TEMP stations)
  │
  ▼
[QUALITY CONTROL] (Range checks, gross error detection, temporal consistency)
  │
  ▼
[METRIC CALCULATION] (NWPVerificationMetrics continuous & categorical score evaluation)
  │
  ▼
[REPORT GENERATION] (JSON Metadata export & ESOC Verification Panel rendering)
  │
  ▼
[SCIENTIFIC ACCEPTANCE] (Threshold verification against WMO / ECMWF standards)
```
