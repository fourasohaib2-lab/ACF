# ACF V1.0 PREPARATION RECOMMENDATIONS (ACF-ARCH-001)

## 1. MANDATORY RECOMMENDATIONS BEFORE v1.0

1. **Maintain Zero-Regression Policy**: Run `.venv/bin/python -m compileall src` and `pytest tests/` prior to every release tag.
2. **Module Maturity Manifest Verification**: Ensure all new components register a valid `module.yaml` manifest.
3. **Preserve API Contracts**: Maintain strict backward compatibility for `BaseWeatherModel`, `UniversalModelRunner`, `HPCMonitor`, and `UniversalReader`.
