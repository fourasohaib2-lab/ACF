# ACF LTS VALIDATION POLICY (ACF-LTS-001)

## 1. CONTINUOUS VALIDATION & TESTING SCHEDULE

- **Nightly Regression Gate**: Automated execution of `.venv/bin/python -m compileall src` and `PYTHONPATH=src pytest tests/` (Target: 100.0% pass rate).
- **Weekly Scientific Benchmark**: Verification of T2M, U10M, MSLP, and Z500 RMSE/ACC metrics against ERA5 reanalysis.
- **Dependency Audit**: Monthly security and compatibility scanning for 48 core Python libraries.
